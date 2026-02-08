from cmdbox.app.features.cli import cmdbox_embed_embedding
from google.adk.memory import BaseMemoryService
from google.adk.memory.base_memory_service import SearchMemoryResponse
from google.adk.memory.memory_entry import MemoryEntry
from google.genai import types
from datetime import datetime
from typing import List, Dict, Any, Optional
import asyncpg
import json
import logging


class PostgresqlMemoryService(BaseMemoryService):
    """
    PostgreSQLベースドメモリサービス
    """
    def __init__(self, db_url:str, embed_name:str, embed_model:Any,
                 memory_fetch_offset:int=0, memory_fetch_count:int=10, memory_fetch_summary:bool=False,
                 logger:Optional[logging.Logger]=None, pool_min_size:int=2, pool_max_size:int=3):
        """
        コンストラクタ
        
        Args:
            db_url: PostgreSQLデータベース接続URL
                   - postgresql://user:pass@host:port/dbname
            embed_name: 埋め込みモデル名
            embed_model: 埋め込みモデル
            memory_fetch_offset: メモリ取得開始位置
            memory_fetch_count: メモリ取得件数
            memory_fetch_summary: メモリ取得内容の要約有無
            logger: オプションのロガーインスタンス
            pool_min_size: コネクションプールの最小サイズ
            pool_max_size: コネクションプールの最大サイズ
        """
        self.db_url = db_url
        self.embed_name = embed_name
        self.embed_model = embed_model
        self.memory_fetch_offset = memory_fetch_offset
        self.memory_fetch_count = memory_fetch_count
        self.memory_fetch_summary = memory_fetch_summary
        self.logger = logger or logging.getLogger(__name__)
        self.pool_min_size = pool_min_size
        self.pool_max_size = pool_max_size
        self._done_init_db = False
        self._pool = None

    async def _get_pool(self):
        """
        コネクションプールを取得または作成する
        """
        if self._pool is None:
            self._pool = await asyncpg.create_pool(
                self.db_url,
                min_size=self.pool_min_size,
                max_size=self.pool_max_size,
                command_timeout=60
            )
            self.logger.info(f"Connection pool created with min_size={self.pool_min_size}, max_size={self.pool_max_size}")
        return self._pool

    async def close_pool(self):
        """
        コネクションプールをクローズする
        """
        if self._pool is not None:
            await self._pool.close()
            self._pool = None
            self.logger.info("Connection pool closed")

    async def __aenter__(self):
        """
        非同期コンテキストマネージャーのサポート
        """
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        非同期コンテキストマネージャーの終了処理
        """
        await self.close_pool()

    async def _init_db(self):
        try:
            if self._done_init_db:
                return
            pool = await self._get_pool()
            conn = await pool.acquire()
            try:
                # Enable pgvector extension
                await conn.execute('CREATE EXTENSION IF NOT EXISTS vector')
                await conn.execute('''
                    CREATE TABLE IF NOT EXISTS memory_entries (
                        id TEXT PRIMARY KEY,
                        app_name TEXT NOT NULL,
                        user_id TEXT NOT NULL,
                        session_id TEXT,
                        embed_name TEXT,
                        content TEXT NOT NULL,
                        custom_metadata TEXT,
                        author TEXT,
                        embedding vector(256),
                        timestamp TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create indexes
                await conn.execute('''
                    CREATE INDEX IF NOT EXISTS idx_app_user 
                    ON memory_entries(app_name, user_id)
                ''')
                await conn.execute('''
                    CREATE INDEX IF NOT EXISTS idx_session 
                    ON memory_entries(session_id)
                ''')
                
                # Create index on vector column
                await conn.execute('''
                    CREATE INDEX IF NOT EXISTS idx_embedding 
                    ON memory_entries USING ivfflat (embedding vector_cosine_ops)
                    WITH (lists = 100)
                ''')
                self.logger.info(f"PostgreSQL database initialized at {self.db_url}")
                self._done_init_db = True
            finally:
                await pool.release(conn)
        except Exception as e:
            self.logger.error(f"Error initializing PostgreSQL database: {e}", exc_info=True)
            raise
    
    async def add_session_to_memory(self, session: 'Session'):
        """
        Add session to memory.
        
        Args:
            session: Session object to add to memory
        """
        try:
            await self._add_session_to_memory_postgresql(session)
        except Exception as e:
            self.logger.error(f"Error adding session to memory: {e}", exc_info=True)
            raise

    async def _add_session_to_memory_postgresql(self, session: 'Session'):
        final_event = session.events[-1] if session.events else None
        if final_event is None:
            self.logger.warning(f"Session {session.id} has no events to add to memory")
            return
        final_msg = final_event.content.parts[0].text if final_event.content.parts else ''
        if not final_msg:
            self.logger.warning(f"Session {session.id} final event has no content to add to memory")
            return
        st, _, final_vec = cmdbox_embed_embedding.EmbedEmbedding._embedding(self.embed_model, [final_msg])
        if st != cmdbox_embed_embedding.EmbedEmbedding.RESP_SUCCESS:
            self.logger.warning(f"Failed to generate embedding for session {session.id}")
            return

        try:
            pool = await self._get_pool()
            conn = await pool.acquire()
            
            try:
                # Insert into memory_entries
                await conn.execute('''
                    INSERT INTO memory_entries 
                    (id, app_name, user_id, session_id, embed_name, content, custom_metadata, author, embedding, timestamp)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                ''',
                    final_event.id,
                    session.app_name,
                    session.user_id,
                    session.id,
                    self.embed_name,
                    final_msg,
                    json.dumps({}),
                    'system',
                    final_vec[0],
                    datetime.utcnow().isoformat()
                )
                
                self.logger.info(f"Session {session.id} added to PostgreSQL memory")
            finally:
                await pool.release(conn)
        except Exception as e:
            self.logger.error(f"PostgreSQL error: {e}", exc_info=True)
            raise
    
    async def search_memory(self, *, app_name: str, user_id: str, query: str) -> SearchMemoryResponse:
        """
        Search memory entries.
        
        Args:
            app_name: Application name
            user_id: User ID
            query: Search query
            
        Returns:
            SearchMemoryResponse containing matching memory entries
        """
        try:
            return await self._search_memory_postgresql(app_name, user_id, query)
        except Exception as e:
            self.logger.error(f"Error searching memory: {e}", exc_info=True)
            return SearchMemoryResponse(memories=[])
    
    async def _search_memory_postgresql(self, app_name: str, user_id: str, query: str) -> SearchMemoryResponse:
        await self._init_db()

        if query is not None and query.strip() != '':
            st, _, final_vec = cmdbox_embed_embedding.EmbedEmbedding._embedding(self.embed_model, [query])
            if st != cmdbox_embed_embedding.EmbedEmbedding.RESP_SUCCESS:
                self.logger.warning(f"Failed to generate embedding for search query")
                return SearchMemoryResponse(memories=[])
        else:
            final_vec = None
        
        results = []
        
        try:
            pool = await self._get_pool()
            conn = await pool.acquire()
            
            try:
                sql = '''
                    SELECT m.id, m.app_name, m.user_id, m.session_id, m.embed_name, m.content,
                    m.custom_metadata, m.author, m.timestamp, t.all_cnt
                '''
                if final_vec is not None:
                    sql += ', (m.embedding <=> $1::vector) AS distance '
                else:
                    sql += ', $1 AS distance '
                sql += '''
                    FROM memory_entries m, (SELECT count(*) AS all_cnt FROM memory_entries WHERE app_name = $2) AS t
                    WHERE m.app_name = $2 AND m.user_id = $3
                '''
                if final_vec is not None:
                    sql += 'ORDER BY distance ASC '
                else:
                    sql += 'ORDER BY m.created_at DESC '
                sql += 'LIMIT $4 OFFSET $5'
                
                param = []
                if final_vec is not None:
                    param += [final_vec[0], app_name, user_id, self.memory_fetch_count, self.memory_fetch_offset]
                else:
                    param = ['0', app_name, user_id, self.memory_fetch_count, self.memory_fetch_offset]
                
                rows = await conn.fetch(sql, *param)
                
                for row in rows:
                    try:
                        entry_id = row[0]
                        session_id = row[3]
                        embed_name = row[4]
                        content = row[5]
                        metadata = row[6]
                        author = row[7]
                        timestamp = row[8]
                        all_cnt = row[9]
                        distance = row[10]
                        
                        # Create MemoryEntry object
                        content_obj = types.Content(
                            role='user',
                            parts=[types.Part(text=content)]
                        )
                        metadata = json.loads(metadata) if metadata else {}
                        metadata['session_id'] = session_id
                        metadata['embed_name'] = embed_name
                        metadata['distance'] = float(distance) if distance is not None else 0.0
                        metadata['all_cnt'] = all_cnt
                        entry = MemoryEntry(
                            id=entry_id,
                            content=content_obj,
                            custom_metadata=metadata,
                            author=author,
                            timestamp=timestamp,
                        )
                        results.append(entry)
                    except Exception as e:
                        self.logger.warning(f"Error parsing memory entry: {e}")
                
            finally:
                await pool.release(conn)
        except Exception as e:
            self.logger.error(f"PostgreSQL error: {e}", exc_info=True)
        
        return SearchMemoryResponse(memories=results)
