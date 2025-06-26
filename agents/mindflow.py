"""
FlowMind AI - MindFlow Orchestrator Agent (LangGraph Node)
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import asyncio

from models.state import FlowMindState, AgentResponse
from tools.db_tool import DatabaseTool
from tools.google_api_tool import GoogleAPITool
from tools.llm_router import LLMRouter

class MindFlowAgent:
    """
    MindFlow - The proactive orchestrator agent that coordinates other agents
    and provides intelligent suggestions and workflow automation.
    """
    
    def __init__(self, db_tool: DatabaseTool, google_tool: GoogleAPITool, llm_router: LLMRouter):
        self.db_tool = db_tool
        self.google_tool = google_tool
        self.llm_router = llm_router
        self.agent_name = "MindFlow"
    
    async def process(self, state: FlowMindState) -> AgentResponse:
        """Main processing method for MindFlow agent"""
        user_input = state.messages[-1].content if state.messages else ""
        user_id = state.user_id
        
        # Analyze user input to determine intent
        intent = await self._analyze_intent(user_input)
        
        if intent == "proactive_request":
            response = await self._handle_proactive_request(user_id)
        elif intent == "status_check":
            response = await self._handle_status_check(user_id)
        elif intent == "daily_summary":
            response = await self._generate_daily_summary(user_id)
        elif intent == "workflow_optimization":
            response = await self._suggest_workflow_optimization(user_id)
        else:
            # Default orchestration - route to appropriate agent
            response = await self._orchestrate_request(user_input, user_id)
        
        return AgentResponse(
            content=response,
            agent=self.agent_name,
            context={"intent": intent, "user_id": user_id}
        )
    
    async def _analyze_intent(self, user_input: str) -> str:
        """Analyze user input to determine intent"""
        input_lower = user_input.lower()
        
        if any(phrase in input_lower for phrase in ["what should i do", "suggestions", "proactive", "help me focus"]):
            return "proactive_request"
        elif any(phrase in input_lower for phrase in ["status", "overview", "what's up", "summary"]):
            return "status_check"
        elif any(phrase in input_lower for phrase in ["daily summary", "today's summary", "daily report"]):
            return "daily_summary"
        elif any(phrase in input_lower for phrase in ["optimize", "improve workflow", "better productivity"]):
            return "workflow_optimization"
        else:
            return "orchestration"
    
    async def _handle_proactive_request(self, user_id: str) -> str:
        """Handle proactive assistance requests"""
        try:
            # Get user's current context
            tasks = await self.db_tool.get_user_tasks(user_id, status="pending")
            urgent_tasks = await self.db_tool.get_urgent_tasks(user_id)
            events = await self.google_tool.get_today_events(user_id)
            free_slots = await self.google_tool.get_free_time_slots(user_id)
            
            # Generate proactive suggestions
            suggestions = await self._generate_intelligent_suggestions(
                user_id, tasks, urgent_tasks, events, free_slots
            )
            
            if suggestions:
                # Store suggestions in database
                await self.db_tool.store_suggestions(user_id, suggestions)
                
                # Format response
                response = "🧠 **MindFlow Insights:**\n\n"
                for i, suggestion in enumerate(suggestions[:3], 1):  # Limit to top 3
                    response += f"{i}. **{suggestion['title']}**\n   {suggestion['description']}\n\n"
                
                response += "Would you like me to help you implement any of these suggestions?"
                return response
            else:
                return "🧠 You're doing great! I don't see any immediate optimizations needed. Keep up the good work!"
                
        except Exception as e:
            return f"🧠 I'm having trouble analyzing your current situation. Let me know what specific help you need! Error: {str(e)}"
    
    async def _handle_status_check(self, user_id: str) -> str:
        """Handle status check requests"""
        try:
            tasks = await self.db_tool.get_user_tasks(user_id)
            pending_tasks = [t for t in tasks if t['status'] == 'pending']
            completed_today = [t for t in tasks if t['status'] == 'completed' and 
                             t['updated_at'].date() == datetime.now().date()]
            
            events = await self.google_tool.get_today_events(user_id)
            
            response = "📊 **Your Current Status:**\n\n"
            response += f"• **Pending Tasks:** {len(pending_tasks)}\n"
            response += f"• **Completed Today:** {len(completed_today)}\n"
            response += f"• **Today's Events:** {len(events)}\n\n"
            
            if pending_tasks:
                response += "**Next Priority Tasks:**\n"
                for task in pending_tasks[:3]:
                    priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(task['priority'], "⚪")
                    response += f"{priority_emoji} {task['title']}\n"
            
            return response
            
        except Exception as e:
            return f"📊 I'm having trouble getting your status. Error: {str(e)}"
    
    async def _generate_daily_summary(self, user_id: str) -> str:
        """Generate daily summary"""
        try:
            # Get today's data
            today = datetime.now().date()
            tasks = await self.db_tool.get_user_tasks(user_id)
            events = await self.google_tool.get_today_events(user_id)
            
            completed_tasks = [t for t in tasks if t['status'] == 'completed' and 
                             t['updated_at'].date() == today]
            pending_tasks = [t for t in tasks if t['status'] == 'pending']
            
            # Use LLM to generate intelligent summary
            context = {
                "completed_tasks": len(completed_tasks),
                "pending_tasks": len(pending_tasks),
                "events": len(events),
                "task_details": [t['title'] for t in completed_tasks[:5]],
                "upcoming_tasks": [t['title'] for t in pending_tasks[:5]]
            }
            
            summary_prompt = f"""
            Generate a motivating daily summary for a user based on their productivity data:
            - Completed {len(completed_tasks)} tasks today
            - Has {len(pending_tasks)} pending tasks
            - Had {len(events)} calendar events
            
            Completed tasks: {', '.join([t['title'] for t in completed_tasks[:3]])}
            Upcoming tasks: {', '.join([t['title'] for t in pending_tasks[:3]])}
            
            Make it encouraging and actionable.
            """
            
            ai_summary = await self.llm_router.generate_response([
                {"role": "user", "content": summary_prompt}
            ])
            
            return f"📈 **Daily Summary:**\n\n{ai_summary}"
            
        except Exception as e:
            return f"📈 I'm having trouble generating your daily summary. Error: {str(e)}"
    
    async def _suggest_workflow_optimization(self, user_id: str) -> str:
        """Suggest workflow optimizations"""
        try:
            tasks = await self.db_tool.get_user_tasks(user_id)
            events = await self.google_tool.get_calendar_events(user_id)
            
            # Analyze patterns
            high_priority_tasks = [t for t in tasks if t['priority'] == 'high']
            overdue_tasks = [t for t in tasks if t['due_date'] and 
                           t['due_date'] < datetime.now() and t['status'] == 'pending']
            
            suggestions = []
            
            if len(high_priority_tasks) > 5:
                suggestions.append("Consider breaking down high-priority tasks into smaller, manageable chunks.")
            
            if overdue_tasks:
                suggestions.append(f"You have {len(overdue_tasks)} overdue tasks. Let's reschedule them realistically.")
            
            if len(events) > 8:  # Busy day
                suggestions.append("Your calendar looks packed. Consider blocking focus time for deep work.")
            
            if not suggestions:
                suggestions.append("Your workflow looks well-organized! Keep maintaining this balance.")
            
            response = "⚡ **Workflow Optimization Suggestions:**\n\n"
            for i, suggestion in enumerate(suggestions, 1):
                response += f"{i}. {suggestion}\n"
            
            return response
            
        except Exception as e:
            return f"⚡ I'm having trouble analyzing your workflow. Error: {str(e)}"
    
    async def _orchestrate_request(self, user_input: str, user_id: str) -> str:
        """Orchestrate request to appropriate agent"""
        # This method determines which agent should handle the request
        # In the LangGraph implementation, this logic is handled by the routing functions
        return "🧠 I'm analyzing your request and will route it to the appropriate specialist..."
    
    async def _generate_intelligent_suggestions(self, user_id: str, tasks: List[Dict], 
                                              urgent_tasks: List[Dict], events: List[Dict], 
                                              free_slots: List[Dict]) -> List[Dict[str, Any]]:
        """Generate intelligent proactive suggestions"""
        suggestions = []
        
        try:
            # Suggestion 1: Schedule urgent tasks in free slots
            if urgent_tasks and free_slots:
                for task in urgent_tasks[:2]:  # Top 2 urgent tasks
                    for slot in free_slots[:3]:  # Check first 3 free slots
                        if slot.get('duration', 0) >= 60:  # At least 1 hour
                            suggestions.append({
                                "type": "schedule_task",
                                "title": f"Schedule '{task['title']}'",
                                "description": f"You have a free slot at {slot.get('start_time', 'soon')} - perfect for working on this urgent task!",
                                "action_data": {
                                    "task_id": task['id'],
                                    "suggested_time": slot.get('start_time'),
                                    "duration": min(slot.get('duration', 60), 120)  # Max 2 hours
                                }
                            })
                            break
            
            # Suggestion 2: Break reminder if too many consecutive events
            if len(events) >= 4:
                suggestions.append({
                    "type": "break_reminder",
                    "title": "Take a Break",
                    "description": "You have many events today. Consider scheduling a 15-minute break between meetings.",
                    "action_data": {"break_duration": 15}
                })
            
            # Suggestion 3: Priority review if too many high-priority tasks
            high_priority_count = len([t for t in tasks if t.get('priority') == 'high'])
            if high_priority_count > 5:
                suggestions.append({
                    "type": "priority_review",
                    "title": "Review Task Priorities",
                    "description": f"You have {high_priority_count} high-priority tasks. Consider reviewing and adjusting priorities for better focus.",
                    "action_data": {"high_priority_count": high_priority_count}
                })
            
            # Use LLM for additional context-aware suggestions
            if tasks or events:
                context = {
                    "tasks": [{"title": t["title"], "priority": t.get("priority"), "status": t.get("status")} for t in tasks[:10]],
                    "events": [{"title": e.get("title", "Event"), "start": str(e.get("start_time", ""))} for e in events[:5]],
                    "free_slots": free_slots[:3]
                }
                
                ai_suggestions = await self.llm_router.generate_proactive_suggestions(context)
                suggestions.extend(ai_suggestions[:2])  # Add top 2 AI suggestions
            
        except Exception as e:
            print(f"Error generating suggestions: {e}")
        
        return suggestions[:5]  # Return top 5 suggestions
    
    async def generate_proactive_suggestions(self, user_id: str) -> List[Dict[str, Any]]:
        """Public method for background proactive suggestion generation"""
        try:
            tasks = await self.db_tool.get_user_tasks(user_id, status="pending")
            urgent_tasks = await self.db_tool.get_urgent_tasks(user_id)
            events = await self.google_tool.get_today_events(user_id)
            free_slots = await self.google_tool.get_free_time_slots(user_id)
            
            return await self._generate_intelligent_suggestions(
                user_id, tasks, urgent_tasks, events, free_slots
            )
        except Exception as e:
            print(f"Error in proactive suggestions: {e}")
            return []
    
    async def generate_daily_report(self, user_id: str) -> str:
        """Generate daily report content for video generation"""
        try:
            # Get comprehensive daily data
            tasks = await self.db_tool.get_user_tasks(user_id)
            events = await self.google_tool.get_today_events(user_id)
            suggestions = await self.db_tool.get_pending_suggestions(user_id)
            
            today = datetime.now().date()
            completed_today = [t for t in tasks if t['status'] == 'completed' and 
                             t['updated_at'].date() == today]
            pending_tasks = [t for t in tasks if t['status'] == 'pending']
            
            # Generate comprehensive report using LLM
            report_prompt = f"""
            Create a personalized daily productivity report for a user:
            
            Today's Achievements:
            - Completed {len(completed_today)} tasks
            - Attended {len(events)} events/meetings
            
            Current Status:
            - {len(pending_tasks)} pending tasks
            - {len(suggestions)} active suggestions
            
            Top completed tasks: {', '.join([t['title'] for t in completed_today[:3]])}
            Priority pending tasks: {', '.join([t['title'] for t in pending_tasks[:3] if t.get('priority') == 'high'])}
            
            Make this report encouraging, specific, and actionable for tomorrow.
            Keep it under 200 words for video narration.
            """
            
            report_content = await self.llm_router.generate_response([
                {"role": "user", "content": report_prompt}
            ])
            
            return report_content
            
        except Exception as e:
            return f"Here's your daily summary: You're making progress on your goals. Keep up the great work! (Error: {str(e)})"