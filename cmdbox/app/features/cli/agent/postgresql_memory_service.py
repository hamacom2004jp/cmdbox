"""
PostgreSQL-backed Memory Service for Google ADK

This module provides a memory service that persists memory entries to PostgreSQL.
"""

from google.adk.memory import BaseMemoryService
from google.adk.memory.base_memory_service import SearchMemoryResponse
from google.adk.memory.memory_entry import MemoryEntry
from google.genai import types
import json
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging


class PostgresqlMemoryService(BaseMemoryService):
    """
    PostgreSQL-backed Memory Service that stores memory entries in a PostgreSQL database.
    """
    
    def __init__(self, db_url: str, logger: Optional[logging.Logger] = None):
        """
        Initialize the PostgresqlMemoryService.
        
        Args:
            db_url: PostgreSQL database connection URL
                   - postgresql+psycopg://user:pass@host:port/dbname
                   - postgresql://user:pass@host:port/dbname
            logger: Optional logger instance
        """
        self.db_url = db_url
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
        """Add session to PostgreSQL memory."""
        import uuid
        import asyncpg
        
        entry_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        
        content_data = {
            'role': 'user',
            'history': self._extract_session_history(session),
            'metadata': {
                'session_id': session.id,
                'user_id': session.user_id,
                'app_name': session.app_name,
            }
        }
        
        try:
            conn = await asyncpg.connect(self._parse_db_url())
            
            await conn.execute('''
                INSERT INTO memory_entries 
                (id, app_name, user_id, session_id, content, custom_metadata, author, timestamp)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            ''', 
                entry_id,
                session.app_name,
                session.user_id,
                session.id,
                json.dumps(content_data, default=str),
                json.dumps({'source': 'session_save'}),
                'system',
                timestamp
            )
            
            await conn.close()
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
