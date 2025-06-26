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
from langchain.tools import tool

# Local imports
from agents.mindflow import MindFlowAgent
from agents.taskflow import TaskFlowAgent
from agents.calendarflow import CalendarFlowAgent
from agents.infoflow import InfoFlowAgent
from tools.db_tool import DBTool
from tools.google_api_tool import GoogleAPITool
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
db_tool = DBTool()
google_tool = GoogleAPITool()
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

        # Register Google API tools
        # These tools will require credentials passed from the state or context
        @tool
        async def get_calendar_events_tool(user_id: str, max_results: int = 10):
            # In a real app, you would retrieve credentials for user_id
            # For this example, we'll assume credentials are part of a mock or passed securely.
            # For now, this is a placeholder.
            # You would fetch credentials based on user_id, e.g., from a database linked to OAuth tokens.
            # As per instruction, MindFlow handles proactive orchestration, so we pass current_user_credentials from state.
            # This requires credentials to be stored in FlowMindState.context
            if "google_credentials" not in FlowMindState.context or not FlowMindState.context["google_credentials"]:
                raise ValueError("Google credentials not found in state context.")
            credentials = FlowMindState.context["google_credentials"]
            return await google_tool.get_calendar_events(credentials, max_results)

        @tool
        async def create_calendar_event_tool(user_id: str, summary: str, description: Optional[str], start_time: datetime, end_time: datetime):
            if "google_credentials" not in FlowMindState.context or not FlowMindState.context["google_credentials"]:
                raise ValueError("Google credentials not found in state context.")
            credentials = FlowMindState.context["google_credentials"]
            return await google_tool.create_calendar_event(credentials, summary, description, start_time, end_time)
        
        @tool
        async def get_tasks_tool(user_id: str, tasklist_id: str = "@default", max_results: int = 10):
            if "google_credentials" not in FlowMindState.context or not FlowMindState.context["google_credentials"]:
                raise ValueError("Google credentials not found in state context.")
            credentials = FlowMindState.context["google_credentials"]
            return await google_tool.get_tasks(credentials, tasklist_id, max_results)

        @tool
        async def create_task_tool(user_id: str, title: str, tasklist_id: str = "@default"):
            if "google_credentials" not in FlowMindState.context or not FlowMindState.context["google_credentials"]:
                raise ValueError("Google credentials not found in state context.")
            credentials = FlowMindState.context["google_credentials"]
            return await google_tool.create_task(credentials, title, tasklist_id)

        workflow.add_tool(get_calendar_events_tool)
        workflow.add_tool(create_calendar_event_tool)
        workflow.add_tool(get_tasks_tool)
        workflow.add_tool(create_task_tool)
        
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
    
    async def run(self, user_input: str, user_id: str, google_credentials: Optional[Any] = None) -> Dict[str, Any]:
        """Execute the multi-agent workflow"""
        initial_state = FlowMindState(
            messages=[UserMessage(content=user_input, user_id=user_id)],
            user_id=user_id,
            current_agent="mindflow",
            context={}
        )
        if google_credentials:
            initial_state.context["google_credentials"] = google_credentials
        
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
    google_credentials: Optional[Any] = None

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
        result = await flowmind_graph.run(request.message, request.user_id, request.google_credentials)
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
    return {"status": "ok", "message": "FlowMind AI backend is running!"}

@app.get("/google-auth-url")
async def google_auth_url():
    auth_url, state = google_tool.get_google_auth_url()
    return {"authorization_url": auth_url, "state": state}

@app.get("/google-oauth-callback")
async def google_oauth_callback(code: str, state: str):
    try:
        credentials = google_tool.exchange_code_for_token(f"code={code}&state={state}")
        # In a real application, you would store these credentials securely,
        # linked to the user_id, possibly in your database.
        # For now, we'll return them, but they won't persist across requests
        # without a proper session or database integration.
        return {"message": "Authentication successful", "credentials": credentials.to_json()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Authentication failed: {str(e)}")

@app.get("/user/{user_id}/tasks")
async def get_user_tasks(user_id: str):
    try:
        tasks = await db_tool.list_tasks(user_id)
        return {"tasks": tasks}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch tasks: {str(e)}")

@app.get("/user/{user_id}/events")
async def get_user_events(user_id: str):
    try:
        events = await db_tool.list_events(user_id)
        return {"events": events}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch events: {str(e)}")

@app.on_event("startup")
async def startup_event():
    await db_tool.connect()
    print("Database connected.")

@app.on_event("shutdown")
async def shutdown_event():
    await db_tool.disconnect()
    print("Database disconnected.")

# Proactive suggestion loop (placeholder for MindFlow's proactivity)
async def proactive_suggestion_loop():
    # This loop would run in the background, orchestrated by MindFlow
    # It would periodically check for user context, deadlines, etc.
    # and generate proactive suggestions/actions.
    while True:
        await asyncio.sleep(3600)  # Check every hour
        # Example: mindflow_agent.check_for_proactive_actions()

# Run the proactive loop in background
@app.on_event("startup")
async def start_proactive_loop():
    asyncio.create_task(proactive_suggestion_loop())

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )