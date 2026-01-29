"""
SQLite-backed Memory Service for Google ADK

This module provides a memory service that persists memory entries to SQLite.
"""

from google.adk.memory import BaseMemoryService
from google.adk.memory.base_memory_service import SearchMemoryResponse
from google.adk.memory.memory_entry import MemoryEntry
from google.genai import types
import json
import sqlite3
import asyncio
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging


class SqliteMemoryService(BaseMemoryService):
    """
    SQLite-backed Memory Service that stores memory entries in a SQLite database.
    """
    
    def __init__(self, db_url: str, logger: Optional[logging.Logger] = None):
        """
        Initialize the SqliteMemoryService.
        
        Args:
            db_url: SQLite database connection URL
                   - sqlite:///path/to/db.db
                   - sqlite+aiosqlite:///path/to/db.db
            logger: Optional logger instance
        """
        self.db_url = db_url
        self.logger = logger or logging.getLogger(__name__)
        self.db_path = self._get_db_path()
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
            cursor = conn.cursor()
            cursor.execute('''
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
    
    async def _add_session_to_memory_sqlite(self, session: 'Session'):
        """Add session to SQLite memory."""
        import uuid
        
        entry_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        
        # Prepare memory entry data
        content_data = {
            'role': 'user',
            'history': self._extract_session_history(session),
            'metadata': {
                'session_id': session.id,
                'user_id': session.user_id,
                'app_name': session.app_name,
            }
        }
        
        def run_in_executor():
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO memory_entries 
                    (id, app_name, user_id, session_id, content, custom_metadata, author, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    entry_id,
                    session.app_name,
                    session.user_id,
                    session.id,
                    json.dumps(content_data, default=str),
                    json.dumps({'source': 'session_save'}),
                    'system',
                    timestamp
                ))
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
        """Search memory in SQLite."""
        results = []
        
        def run_in_executor():
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Search with full-text matching
                search_query = f"%{query}%"
                cursor.execute('''
                    SELECT id, content, custom_metadata, author, timestamp
                    FROM memory_entries
                    WHERE app_name = ? AND user_id = ?
                    AND (content LIKE ? OR custom_metadata LIKE ?)
                    ORDER BY timestamp DESC
                    LIMIT 10
                ''', (app_name, user_id, search_query, search_query))
                
                rows = cursor.fetchall()
                for row in rows:
                    entry_id, content, metadata, author, timestamp = row
                    try:
                        content_dict = json.loads(content)
                        # Create MemoryEntry object
                        content_obj = types.Content(
                            role=content_dict.get('role', 'user'),
                            parts=[types.Part(text=json.dumps(content_dict))]
                        )
                        
                        entry = MemoryEntry(
                            id=entry_id,
                            content=content_obj,
                            custom_metadata=json.loads(metadata) if metadata else {},
                            author=author,
                            timestamp=timestamp
                        )
                        results.append(entry)
                    except Exception as e:
                        self.logger.warning(f"Error parsing memory entry {entry_id}: {e}")
                
                return results
        
        loop = asyncio.get_event_loop()
        memories = await loop.run_in_executor(None, run_in_executor)
        return SearchMemoryResponse(memories=memories)
    
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
