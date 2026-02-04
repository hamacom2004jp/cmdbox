from cmdbox.app.features.cli import cmdbox_agent_embedding
from google.adk.memory import BaseMemoryService
from google.adk.memory.base_memory_service import SearchMemoryResponse
from google.adk.memory.memory_entry import MemoryEntry
from google.genai import types
from datetime import datetime
from typing import List, Dict, Any, Optional
import json
import asyncio
import logging


class PostgresqlMemoryService(BaseMemoryService):
    """
    PostgreSQLベースドメモリサービス
    """
    def __init__(self, db_url:str, embed_name:str, embed_model:Any,
                 memory_fetch_offset:int = 0, memory_fetch_count:int = 10, memory_fetch_summary:bool = False,
                 logger:Optional[logging.Logger] = None):
        """
        コンストラクタ
        
        Args:
            db_url: PostgreSQLデータベース接続URL
                   - postgresql+psycopg://user:pass@host:port/dbname
                   - postgresql://user:pass@host:port/dbname
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
        self.memory_fetch_offset = memory_fetch_offset
        self.memory_fetch_count = memory_fetch_count
        self.memory_fetch_summary = memory_fetch_summary
        self.logger = logger or logging.getLogger(__name__)
        self._init_db()

    async def _init_db(self):
        """Initialize PostgreSQL database schema."""
        try:
            import asyncpg
            
            conn = await asyncpg.connect(self._parse_db_url())
            
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
            
            await conn.close()
            self.logger.info(f"PostgreSQL database initialized at {self.db_url}")
        except Exception as e:
            self.logger.error(f"Error initializing PostgreSQL database: {e}", exc_info=True)
            raise
    
    def _parse_db_url(self) -> str:
        """Parse PostgreSQL URL for asyncpg connection."""
        # Convert postgresql+psycopg:// to postgresql://
        if self.db_url.startswith('postgresql+psycopg://'):
            return self.db_url.replace('postgresql+psycopg://', 'postgresql://')
        return self.db_url
    
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
        import asyncpg

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
        
        try:
            async with asyncpg.connect(self._parse_db_url()) as conn:

                await conn.execute('''
                    INSERT INTO memory_entries 
                    (id, app_name, user_id, session_id, embed_name, content, custom_metadata, author, timestamp)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                ''', 
                    final_event.id,
                    session.app_name,
                    session.user_id,
                    session.id,
                    self.embed_name,
                    final_msg,
                    json.dumps({}),
                    'system',
                    datetime.utcnow().isoformat()
                )
            
                self.logger.info(f"Session {session.id} added to PostgreSQL memory")
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
        """Search memory in PostgreSQL."""
        import asyncpg
        
        results = []
        
        try:
            conn = await asyncpg.connect(self._parse_db_url())
            
            search_query = f"%{query}%"
            rows = await conn.fetch('''
                SELECT id, content, custom_metadata, author, timestamp
                FROM memory_entries
                WHERE app_name = $1 AND user_id = $2
                AND (content LIKE $3 OR custom_metadata LIKE $3)
                ORDER BY timestamp DESC
                LIMIT 10
            ''', app_name, user_id, search_query)
            
            for row in rows:
                try:
                    content_dict = json.loads(row['content'])
                    content_obj = types.Content(
                        role=content_dict.get('role', 'user'),
                        parts=[types.Part(text=json.dumps(content_dict))]
                    )
                    
                    entry = MemoryEntry(
                        id=row['id'],
                        content=content_obj,
                        custom_metadata=json.loads(row['custom_metadata']) if row['custom_metadata'] else {},
                        author=row['author'],
                        timestamp=row['timestamp']
                    )
                    results.append(entry)
                except Exception as e:
                    self.logger.warning(f"Error parsing memory entry {row['id']}: {e}")
            
            await conn.close()
        except Exception as e:
            self.logger.error(f"PostgreSQL error: {e}", exc_info=True)
        
        return SearchMemoryResponse(memories=results)
    
    @staticmethod
    def _extract_session_history(session: 'Session') -> List[Dict[str, Any]]:
        """Extract conversation history from session."""
        history = []
        
        if hasattr(session, 'history') and session.history:
            for item in session.history:
                try:
                    if hasattr(item, 'content') and hasattr(item.content, 'parts'):
                        text_parts = [p.text for p in item.content.parts if hasattr(p, 'text') and p.text]
                        if text_parts:
                            history.append({
                                'role': getattr(item.content, 'role', 'unknown'),
                                'text': ' '.join(text_parts)
                            })
                except Exception as e:
                    pass
        
        return history
