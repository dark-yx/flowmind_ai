"""
FlowMind AI - Main FastAPI Backend with LangGraph Multi-Agent System
"""
import os
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import uvicorn

# LangGraph and LangChain imports
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI

# Local imports
from agents.mindflow import MindFlowAgent
from agents.taskflow import TaskFlowAgent
from agents.calendarflow import CalendarFlowAgent
from agents.infoflow import InfoFlowAgent
from tools import db_tool
from tools import google_api_tool
from tools.llm_router import LLMRouter
from tools.elevenlabs_tool import ElevenLabsTool
from tools.tavus_tool import TavusTool
from models.state import FlowMindState, UserMessage, AgentResponse

# Initialize FastAPI app
app = FastAPI(
    title="FlowMind AI API",
    description="Multi-Agent Productivity Assistant Backend",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Global instances
db_tool = db_tool.DatabaseTool()
google_tool = google_api_tool.GoogleAPITool()
llm_router = LLMRouter()
elevenlabs_tool = ElevenLabsTool()
tavus_tool = TavusTool()

# Initialize agents
mindflow_agent = MindFlowAgent(db_tool, google_tool, llm_router)
taskflow_agent = TaskFlowAgent(db_tool, llm_router)
calendarflow_agent = CalendarFlowAgent(db_tool, google_tool, llm_router)
infoflow_agent = InfoFlowAgent(llm_router)

# LangGraph State Management
class FlowMindGraph:
    def __init__(self):
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph multi-agent workflow"""
        workflow = StateGraph(FlowMindState)
        
        # Add agent nodes
        workflow.add_node("mindflow", self._mindflow_node)
        workflow.add_node("taskflow", self._taskflow_node)
        workflow.add_node("calendarflow", self._calendarflow_node)
        workflow.add_node("infoflow", self._infoflow_node)
        
        # Define routing logic
        workflow.set_entry_point("mindflow")
        
        # MindFlow orchestrates other agents
        workflow.add_conditional_edges(
            "mindflow",
            self._route_from_mindflow,
            {
                "taskflow": "taskflow",
                "calendarflow": "calendarflow", 
                "infoflow": "infoflow",
                "end": END
            }
        )
        
        # All agents can return to MindFlow or end
        for agent in ["taskflow", "calendarflow", "infoflow"]:
            workflow.add_conditional_edges(
                agent,
                self._route_to_end,
                {
                    "mindflow": "mindflow",
                    "end": END
                }
            )
        
        return workflow.compile()
    
    async def _mindflow_node(self, state: FlowMindState) -> FlowMindState:
        """MindFlow orchestrator node"""
        response = await mindflow_agent.process(state)
        state.messages.append(response)
        state.current_agent = "mindflow"
        return state
    
    async def _taskflow_node(self, state: FlowMindState) -> FlowMindState:
        """TaskFlow agent node"""
        response = await taskflow_agent.process(state)
        state.messages.append(response)
        state.current_agent = "taskflow"
        return state
    
    async def _calendarflow_node(self, state: FlowMindState) -> FlowMindState:
        """CalendarFlow agent node"""
        response = await calendarflow_agent.process(state)
        state.messages.append(response)
        state.current_agent = "calendarflow"
        return state
    
    async def _infoflow_node(self, state: FlowMindState) -> FlowMindState:
        """InfoFlow agent node"""
        response = await infoflow_agent.process(state)
        state.messages.append(response)
        state.current_agent = "infoflow"
        return state
    
    def _route_from_mindflow(self, state: FlowMindState) -> str:
        """Route from MindFlow to appropriate agent"""
        last_message = state.messages[-1] if state.messages else None
        if not last_message:
            return "end"
        
        content = last_message.content.lower()
        
        if any(word in content for word in ["task", "todo", "deadline", "priority"]):
            return "taskflow"
        elif any(word in content for word in ["calendar", "event", "meeting", "schedule"]):
            return "calendarflow"
        elif any(word in content for word in ["explain", "summarize", "what is", "how to"]):
            return "infoflow"
        else:
            return "end"
    
    def _route_to_end(self, state: FlowMindState) -> str:
        """Determine if agent should continue or end"""
        # Simple logic: end after agent processes
        return "end"
    
    async def run(self, user_input: str, user_id: str) -> Dict[str, Any]:
        """Execute the multi-agent workflow"""
        initial_state = FlowMindState(
            messages=[UserMessage(content=user_input, user_id=user_id)],
            user_id=user_id,
            current_agent="mindflow",
            context={}
        )
        
        final_state = await self.graph.ainvoke(initial_state)
        
        return {
            "response": final_state.messages[-1].content if final_state.messages else "No response generated",
            "agent": final_state.current_agent,
            "context": final_state.context
        }

# Global graph instance
flowmind_graph = FlowMindGraph()

# Pydantic models for API
class ChatRequest(BaseModel):
    message: str
    user_id: str

class ChatResponse(BaseModel):
    response: str
    agent: str
    context: Dict[str, Any]

class VoiceRequest(BaseModel):
    audio_data: str  # Base64 encoded audio
    user_id: str

class VideoReportRequest(BaseModel):
    user_id: str
    report_type: str = "daily"

# API Endpoints
@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Main chat endpoint for multi-agent interaction"""
    try:
        result = await flowmind_graph.run(request.message, request.user_id)
        return ChatResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")

@app.post("/voice")
async def voice_endpoint(request: VoiceRequest):
    """Voice input processing with ElevenLabs"""
    try:
        # Convert audio to text
        transcription = await elevenlabs_tool.speech_to_text(request.audio_data)
        
        # Process through chat
        result = await flowmind_graph.run(transcription, request.user_id)
        
        # Convert response to speech
        audio_url = await elevenlabs_tool.text_to_speech(result["response"])
        
        return {
            "transcription": transcription,
            "response": result["response"],
            "audio_url": audio_url,
            "agent": result["agent"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Voice processing failed: {str(e)}")

@app.post("/video-report")
async def video_report_endpoint(request: VideoReportRequest):
    """Generate personalized video report with Tavus"""
    try:
        # Generate report content via MindFlow
        report_content = await mindflow_agent.generate_daily_report(request.user_id)
        
        # Create video with Tavus
        video_url = await tavus_tool.generate_video_report(
            report_content, 
            request.user_id
        )
        
        return {
            "video_url": video_url,
            "report_content": report_content,
            "generated_at": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Video report generation failed: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "agents": ["mindflow", "taskflow", "calendarflow", "infoflow"]
    }

@app.get("/user/{user_id}/tasks")
async def get_user_tasks(user_id: str):
    """Get user's tasks"""
    try:
        tasks = await db_tool.get_user_tasks(user_id)
        return {"tasks": tasks}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch tasks: {str(e)}")

@app.get("/user/{user_id}/events")
async def get_user_events(user_id: str):
    """Get user's calendar events"""
    try:
        events = await google_tool.get_calendar_events(user_id)
        return {"events": events}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch events: {str(e)}")

# Background task for proactive suggestions
@app.on_event("startup")
async def startup_event():
    """Initialize background tasks"""
    asyncio.create_task(proactive_suggestion_loop())

async def proactive_suggestion_loop():
    """Background loop for proactive suggestions"""
    while True:
        try:
            # Get all active users
            users = await db_tool.get_active_users()
            
            for user in users:
                # Run proactive analysis
                suggestions = await mindflow_agent.generate_proactive_suggestions(user["id"])
                
                if suggestions:
                    # Store suggestions for UI to display
                    await db_tool.store_suggestions(user["id"], suggestions)
            
            # Wait 30 minutes before next scan
            await asyncio.sleep(1800)
            
        except Exception as e:
            print(f"Proactive suggestion loop error: {e}")
            await asyncio.sleep(300)  # Wait 5 minutes on error

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )