from cmdbox.app.features.cli import cmdbox_agent_embedding
from google.adk.memory import BaseMemoryService
from google.adk.memory.base_memory_service import SearchMemoryResponse
from google.adk.memory.memory_entry import MemoryEntry
from google.genai import types
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import json
import sqlite3
import sqlite_vec
import asyncio
import logging


class SqliteMemoryService(BaseMemoryService):
    """
    SQLiteベースドメモリサービス
    """
    
    def __init__(self, db_url:str, embed_name:str, embed_model:Any,
                 memory_fetch_offset:int = 0, memory_fetch_count:int = 10, memory_fetch_summary:bool = False,
                 logger:Optional[logging.Logger] = None):
        """
        コンストラクタ

        Args:
            db_url: SQLiteデータベース接続URL
                    - sqlite:///path/to/db.db
                    - sqlite+aiosqlite:///path/to/db.db
            embed_name: 埋め込みモデル名
            embed_model: 埋め込みモデル
            memory_fetch_offset: メモリ取得開始位置
            memory_fetch_count: メモリ取得件数
            memory_fetch_summary: メモリ取得内容の要約有無
            logger: オプションのロガーインスタンス
        """
        self.db_url = db_url
        self.embed_name = embed_name
        self.embed_model = embed_model
        self.logger = logger or logging.getLogger(__name__)
        self.db_path = self._get_db_path()
        self.memory_fetch_offset = memory_fetch_offset
        self.memory_fetch_count = memory_fetch_count
        self.memory_fetch_summary = memory_fetch_summary
        self._init_db()

    def _get_db_path(self) -> str:
        """Extract database file path from SQLite URL."""
        # Parse sqlite:///path/to/db.db or sqlite+aiosqlite:///path/to/db.db
        if '///' in self.db_url:
            path = self.db_url.split('///', 1)[1]
        else:
            # Fallback for paths that might not match the expected pattern
            path = self.db_url.split('://', 1)[-1] if '://' in self.db_url else self.db_url

        # Windows paths handling
        if path.startswith('/') and len(path) > 2 and path[2] == ':':
            path = path[1:]  # Remove leading slash for Windows paths like /C:/path/to/db.db
        return path
    
    def _init_db(self):
        """Initialize SQLite database schema."""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.enable_load_extension(True)
            sqlite_vec.load(conn)
            conn.enable_load_extension(False)
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS memory_entries (
                    id TEXT PRIMARY KEY,
                    app_name TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    session_id TEXT,
                    embed_name TEXT,
                    content TEXT NOT NULL,
                    custom_metadata TEXT,
                    author TEXT,
                    timestamp TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cursor.execute('''
                CREATE VIRTUAL TABLE IF NOT EXISTS memory_entries_vec USING vec0(
                    id TEXT PRIMARY KEY,
                    embedding float[256]
                )
            ''')
            
            # Create indexes
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_app_user 
                ON memory_entries(app_name, user_id)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_session 
                ON memory_entries(session_id)
            ''')
            
            conn.commit()
            self.logger.info(f"SQLite database initialized at {self.db_path}")
    
    async def add_session_to_memory(self, session: 'Session'):
        """
        Add session to memory.
        
        Args:
            session: Session object to add to memory
        """
        try:
            await self._add_session_to_memory_sqlite(session)
        except Exception as e:
            self.logger.error(f"Error adding session to memory: {e}", exc_info=True)
            raise

    from google.adk.sessions import Session
    async def _add_session_to_memory_sqlite(self, session:Session):

        final_event = session.events[-1] if session.events else None
        if final_event is None:
            self.logger.warning(f"Session {session.id} has no events to add to memory")
            return
        final_msg = final_event.content.parts[0].text if final_event.content.parts else ''
        if not final_msg:
            self.logger.warning(f"Session {session.id} final event has no content to add to memory")
            return
        st, _, final_vec = cmdbox_agent_embedding.AgentEmbedding._embedding(self.embed_model, [final_msg])
        if st != cmdbox_agent_embedding.AgentEmbedding.RESP_SUCCESS:
            self.logger.warning(f"Failed to generate embedding for session {session.id}")
            return

        def run_in_executor():
            with sqlite3.connect(self.db_path) as conn:
                conn.enable_load_extension(True)
                sqlite_vec.load(conn)
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO memory_entries 
                    (id, app_name, user_id, session_id, embed_name, content, custom_metadata, author, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    final_event.id,
                    session.app_name,
                    session.user_id,
                    session.id,
                    self.embed_name,
                    final_msg,
                    json.dumps({}),
                    'system',
                    datetime.utcnow().isoformat()
                ))

                cursor.execute('''
                    INSERT INTO memory_entries_vec (id, embedding)
                    VALUES (?, ?)
                ''', (
                    final_event.id,
                    final_vec[0]
                ))
                conn.enable_load_extension(False)
                conn.commit()
        
        # Run in executor to avoid blocking
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, run_in_executor)
        self.logger.info(f"Session {session.id} added to SQLite memory")
    
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
            return await self._search_memory_sqlite(app_name, user_id, query)
        except Exception as e:
            self.logger.error(f"Error searching memory: {e}", exc_info=True)
            return SearchMemoryResponse(memories=[])
    
    async def _search_memory_sqlite(self, app_name: str, user_id: str, query: str) -> SearchMemoryResponse:

        if query is not None and query.strip() != '':
            st, _, final_vec = cmdbox_agent_embedding.AgentEmbedding._embedding(self.embed_model, [query])
            if st != cmdbox_agent_embedding.AgentEmbedding.RESP_SUCCESS:
                self.logger.warning(f"Failed to generate embedding for search query")
                return SearchMemoryResponse(memories=[])
        else:
            final_vec = None
        def run_in_executor(app_name, user_id, final_vec):
            results = []
            with sqlite3.connect(self.db_path) as conn:
                conn.enable_load_extension(True)
                sqlite_vec.load(conn)
                cursor = conn.cursor()
                sql ='SELECT m.id, m.app_name, m.user_id, m.session_id, m.embed_name, m.content, m.custom_metadata, m.author, m.timestamp '
                if final_vec is not None:
                    sql += ',vec_distance_cosine(v.embedding, ?) AS distance '
                else:
                    sql += ',0 AS distance '
                sql += '''
                    FROM memory_entries m inner join memory_entries_vec v on m.id = v.id
                    WHERE m.app_name = ? AND m.user_id = ?
                '''
                if final_vec is not None:
                    sql += 'ORDER BY distance DESC '
                else:
                    sql += 'ORDER BY m.created_at DESC '
                sql += 'LIMIT ? OFFSET ?'
                param = []
                if final_vec is not None:
                    param.append(final_vec[0])
                param += [app_name, user_id, self.memory_fetch_count, self.memory_fetch_offset]
                cursor.execute(sql, tuple(param))

                rows = cursor.fetchall()
                conn.enable_load_extension(False)
                for row in rows:
                    entry_id, aid, uid, session_id, embed_name, content, metadata, author, timestamp, distance = row
                    try:
                        # Create MemoryEntry object
                        content_obj = types.Content(
                            role='user',
                            parts=[types.Part(text=content)]
                        )
                        metadata = json.loads(metadata) if metadata else {}
                        metadata['session_id'] = session_id
                        metadata['embed_name'] = embed_name
                        metadata['score'] = distance
                        entry = MemoryEntry(
                            id=entry_id,
                            content=content_obj,
                            custom_metadata=metadata,
                            author=author,
                            timestamp=timestamp
                        )
                        results.append(entry)
                    except Exception as e:
                        self.logger.warning(f"Error parsing memory entry {entry_id}: {e}")
                return results
        
        loop = asyncio.get_event_loop()
        memories = await loop.run_in_executor(None, run_in_executor, app_name, user_id, final_vec)
        return SearchMemoryResponse(memories=memories)
