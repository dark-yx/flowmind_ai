"""
FlowMind AI - Database Tool for LangGraph Agents
"""
import os
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import asyncpg
from models.state import Task, Event, Note, LLMConfig, ProactiveSuggestion

class DatabaseTool:
    """Database operations tool for FlowMind AI agents"""
    
    def __init__(self):
        self.connection_string = os.getenv(
            "DATABASE_URL", 
            "postgresql://user:password@localhost:5432/flowmind"
        )
        self.pool = None
    
    async def initialize(self):
        """Initialize database connection pool"""
        if not self.pool:
            self.pool = await asyncpg.create_pool(self.connection_string)
            await self._create_tables()
    
    async def _create_tables(self):
        """Create database tables if they don't exist"""
        async with self.pool.acquire() as conn:
            # Users table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    email VARCHAR(255) UNIQUE NOT NULL,
                    name VARCHAR(255),
                    google_token TEXT,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            # Tasks table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    title VARCHAR(255) NOT NULL,
                    description TEXT,
                    due_date TIMESTAMP,
                    priority VARCHAR(20) DEFAULT 'medium',
                    status VARCHAR(20) DEFAULT 'pending',
                    user_id UUID NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            # Events table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    title VARCHAR(255) NOT NULL,
                    description TEXT,
                    start_time TIMESTAMP NOT NULL,
                    end_time TIMESTAMP NOT NULL,
                    location VARCHAR(255),
                    user_id UUID NOT NULL,
                    google_event_id VARCHAR(255),
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            # Notes table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS notes (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    title VARCHAR(255),
                    content TEXT NOT NULL,
                    tags TEXT[],
                    user_id UUID NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            # LLM Config table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS llm_configs (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    provider VARCHAR(50) NOT NULL,
                    model_name VARCHAR(100) NOT NULL,
                    api_key TEXT NOT NULL,
                    endpoint VARCHAR(255),
                    is_active BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            # Proactive Suggestions table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS proactive_suggestions (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    user_id UUID NOT NULL,
                    suggestion_type VARCHAR(50) NOT NULL,
                    title VARCHAR(255) NOT NULL,
                    description TEXT,
                    action_data JSONB DEFAULT '{}',
                    status VARCHAR(20) DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT NOW(),
                    expires_at TIMESTAMP
                )
            """)
    
    # Task operations
    async def create_task(self, task: Task) -> str:
        """Create a new task"""
        await self.initialize()
        async with self.pool.acquire() as conn:
            task_id = await conn.fetchval("""
                INSERT INTO tasks (title, description, due_date, priority, status, user_id)
                VALUES ($1, $2, $3, $4, $5, $6)
                RETURNING id
            """, task.title, task.description, task.due_date, task.priority, task.status, task.user_id)
            return str(task_id)
    
    async def get_user_tasks(self, user_id: str, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get tasks for a user"""
        await self.initialize()
        async with self.pool.acquire() as conn:
            if status:
                rows = await conn.fetch("""
                    SELECT * FROM tasks WHERE user_id = $1 AND status = $2
                    ORDER BY created_at DESC
                """, user_id, status)
            else:
                rows = await conn.fetch("""
                    SELECT * FROM tasks WHERE user_id = $1
                    ORDER BY created_at DESC
                """, user_id)
            
            return [dict(row) for row in rows]
    
    async def update_task_status(self, task_id: str, status: str) -> bool:
        """Update task status"""
        await self.initialize()
        async with self.pool.acquire() as conn:
            result = await conn.execute("""
                UPDATE tasks SET status = $1, updated_at = NOW()
                WHERE id = $2
            """, status, task_id)
            return result == "UPDATE 1"
    
    async def delete_task(self, task_id: str) -> bool:
        """Delete a task"""
        await self.initialize()
        async with self.pool.acquire() as conn:
            result = await conn.execute("DELETE FROM tasks WHERE id = $1", task_id)
            return result == "DELETE 1"
    
    async def get_urgent_tasks(self, user_id: str) -> List[Dict[str, Any]]:
        """Get urgent tasks (high priority or due soon)"""
        await self.initialize()
        tomorrow = datetime.now() + timedelta(days=1)
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT * FROM tasks 
                WHERE user_id = $1 
                AND status = 'pending'
                AND (priority = 'high' OR due_date <= $2)
                ORDER BY due_date ASC, priority DESC
            """, user_id, tomorrow)
            
            return [dict(row) for row in rows]
    
    # Event operations
    async def create_event(self, event: Event) -> str:
        """Create a new event"""
        await self.initialize()
        async with self.pool.acquire() as conn:
            event_id = await conn.fetchval("""
                INSERT INTO events (title, description, start_time, end_time, location, user_id, google_event_id)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                RETURNING id
            """, event.title, event.description, event.start_time, event.end_time, 
                event.location, event.user_id, event.google_event_id)
            return str(event_id)
    
    async def get_user_events(self, user_id: str, start_date: Optional[datetime] = None, 
                             end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Get events for a user"""
        await self.initialize()
        async with self.pool.acquire() as conn:
            if start_date and end_date:
                rows = await conn.fetch("""
                    SELECT * FROM events 
                    WHERE user_id = $1 AND start_time >= $2 AND end_time <= $3
                    ORDER BY start_time ASC
                """, user_id, start_date, end_date)
            else:
                rows = await conn.fetch("""
                    SELECT * FROM events WHERE user_id = $1
                    ORDER BY start_time ASC
                """, user_id)
            
            return [dict(row) for row in rows]
    
    # Note operations
    async def create_note(self, note: Note) -> str:
        """Create a new note"""
        await self.initialize()
        async with self.pool.acquire() as conn:
            note_id = await conn.fetchval("""
                INSERT INTO notes (title, content, tags, user_id)
                VALUES ($1, $2, $3, $4)
                RETURNING id
            """, note.title, note.content, note.tags, note.user_id)
            return str(note_id)
    
    async def get_user_notes(self, user_id: str) -> List[Dict[str, Any]]:
        """Get notes for a user"""
        await self.initialize()
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT * FROM notes WHERE user_id = $1
                ORDER BY created_at DESC
            """, user_id)
            
            return [dict(row) for row in rows]
    
    # LLM Config operations
    async def get_active_llm_config(self) -> Optional[Dict[str, Any]]:
        """Get the active LLM configuration"""
        await self.initialize()
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT * FROM llm_configs WHERE is_active = TRUE LIMIT 1
            """)
            return dict(row) if row else None
    
    async def set_active_llm(self, config_id: str) -> bool:
        """Set an LLM config as active"""
        await self.initialize()
        async with self.pool.acquire() as conn:
            # Deactivate all configs
            await conn.execute("UPDATE llm_configs SET is_active = FALSE")
            # Activate the specified config
            result = await conn.execute("""
                UPDATE llm_configs SET is_active = TRUE WHERE id = $1
            """, config_id)
            return result == "UPDATE 1"
    
    # Proactive suggestions
    async def store_suggestions(self, user_id: str, suggestions: List[Dict[str, Any]]) -> List[str]:
        """Store proactive suggestions"""
        await self.initialize()
        suggestion_ids = []
        async with self.pool.acquire() as conn:
            for suggestion in suggestions:
                suggestion_id = await conn.fetchval("""
                    INSERT INTO proactive_suggestions 
                    (user_id, suggestion_type, title, description, action_data, expires_at)
                    VALUES ($1, $2, $3, $4, $5, $6)
                    RETURNING id
                """, user_id, suggestion.get("type"), suggestion.get("title"),
                    suggestion.get("description"), suggestion.get("action_data", {}),
                    suggestion.get("expires_at"))
                suggestion_ids.append(str(suggestion_id))
        
        return suggestion_ids
    
    async def get_pending_suggestions(self, user_id: str) -> List[Dict[str, Any]]:
        """Get pending suggestions for a user"""
        await self.initialize()
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT * FROM proactive_suggestions 
                WHERE user_id = $1 AND status = 'pending'
                AND (expires_at IS NULL OR expires_at > NOW())
                ORDER BY created_at DESC
            """, user_id)
            
            return [dict(row) for row in rows]
    
    async def update_suggestion_status(self, suggestion_id: str, status: str) -> bool:
        """Update suggestion status"""
        await self.initialize()
        async with self.pool.acquire() as conn:
            result = await conn.execute("""
                UPDATE proactive_suggestions SET status = $1 WHERE id = $2
            """, status, suggestion_id)
            return result == "UPDATE 1"
    
    # User operations
    async def get_active_users(self) -> List[Dict[str, Any]]:
        """Get all active users for proactive scanning"""
        await self.initialize()
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT id, email, name FROM users 
                WHERE created_at > NOW() - INTERVAL '30 days'
            """)
            
            return [dict(row) for row in rows]
    
    async def create_user(self, email: str, name: str, google_token: str = None) -> str:
        """Create a new user"""
        await self.initialize()
        async with self.pool.acquire() as conn:
            user_id = await conn.fetchval("""
                INSERT INTO users (email, name, google_token)
                VALUES ($1, $2, $3)
                RETURNING id
            """, email, name, google_token)
            return str(user_id)
    
    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        await self.initialize()
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("SELECT * FROM users WHERE email = $1", email)
            return dict(row) if row else None