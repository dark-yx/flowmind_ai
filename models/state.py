"""
FlowMind AI - State Management Models for LangGraph
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
from pydantic import BaseModel
from langchain_core.messages import BaseMessage

class UserMessage(BaseModel):
    """User input message"""
    content: str
    user_id: str
    timestamp: datetime = datetime.now()
    message_type: str = "user"

class AgentResponse(BaseModel):
    """Agent response message"""
    content: str
    agent: str
    timestamp: datetime = datetime.now()
    message_type: str = "agent"
    context: Dict[str, Any] = {}

class FlowMindState(BaseModel):
    """Global state for FlowMind AI multi-agent system"""
    messages: List[BaseMessage] = []
    user_id: str
    current_agent: str = "mindflow"
    context: Dict[str, Any] = {}
    
    # Agent-specific state
    task_context: Dict[str, Any] = {}
    calendar_context: Dict[str, Any] = {}
    info_context: Dict[str, Any] = {}
    
    # Proactive state
    suggestions: List[Dict[str, Any]] = []
    last_proactive_scan: Optional[datetime] = None
    
    class Config:
        arbitrary_types_allowed = True

class Task(BaseModel):
    """Task model"""
    id: Optional[str] = None
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: str = "medium"  # low, medium, high
    status: str = "pending"  # pending, in_progress, completed, cancelled
    user_id: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

class Event(BaseModel):
    """Calendar event model"""
    id: Optional[str] = None
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    location: Optional[str] = None
    user_id: str
    google_event_id: Optional[str] = None
    created_at: datetime = datetime.now()

class Note(BaseModel):
    """Note model"""
    id: Optional[str] = None
    content: str
    title: Optional[str] = None
    user_id: str
    tags: List[str] = []
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

class LLMConfig(BaseModel):
    """LLM configuration model"""
    id: Optional[str] = None
    provider: str  # openai, anthropic, google
    model_name: str
    api_key: str
    endpoint: Optional[str] = None
    is_active: bool = False
    created_at: datetime = datetime.now()

class ProactiveSuggestion(BaseModel):
    """Proactive suggestion model"""
    id: Optional[str] = None
    user_id: str
    suggestion_type: str  # schedule_task, break_reminder, priority_alert
    title: str
    description: str
    action_data: Dict[str, Any] = {}
    status: str = "pending"  # pending, accepted, dismissed
    created_at: datetime = datetime.now()
    expires_at: Optional[datetime] = None