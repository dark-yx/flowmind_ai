"""
FlowMind AI - TaskFlow Agent (LangGraph Node)
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import re

from models.state import FlowMindState, AgentResponse, Task
from tools.db_tool import DatabaseTool
from tools.llm_router import LLMRouter

class TaskFlowAgent:
    """
    TaskFlow - Agent responsible for task management operations (CRUD, prioritization, completion)
    """
    
    def __init__(self, db_tool: DatabaseTool, llm_router: LLMRouter):
        self.db_tool = db_tool
        self.llm_router = llm_router
        self.agent_name = "TaskFlow"
    
    async def process(self, state: FlowMindState) -> AgentResponse:
        """Main processing method for TaskFlow agent"""
        user_input = state.messages[-1].content if state.messages else ""
        user_id = state.user_id
        
        # Parse task-related commands
        action = await self._parse_task_action(user_input)
        
        if action["type"] == "create":
            response = await self._create_task(user_id, action["data"])
        elif action["type"] == "complete":
            response = await self._complete_task(user_id, action["data"])
        elif action["type"] == "delete":
            response = await self._delete_task(user_id, action["data"])
        elif action["type"] == "list":
            response = await self._list_tasks(user_id, action["data"])
        elif action["type"] == "update":
            response = await self._update_task(user_id, action["data"])
        elif action["type"] == "prioritize":
            response = await self._prioritize_tasks(user_id)
        else:
            response = await self._handle_general_task_query(user_input, user_id)
        
        return AgentResponse(
            content=response,
            agent=self.agent_name,
            context={"action": action["type"], "user_id": user_id}
        )
    
    async def _parse_task_action(self, user_input: str) -> Dict[str, Any]:
        """Parse user input to determine task action"""
        input_lower = user_input.lower()
        
        # Create task patterns
        create_patterns = [
            r"add task (.+?)(?:\s+(?:for|due|by)\s+(.+))?$",
            r"create task (.+?)(?:\s+(?:for|due|by)\s+(.+))?$",
            r"new task (.+?)(?:\s+(?:for|due|by)\s+(.+))?$",
            r"task: (.+?)(?:\s+(?:for|due|by)\s+(.+))?$"
        ]
        
        for pattern in create_patterns:
            match = re.search(pattern, input_lower)
            if match:
                title = match.group(1).strip()
                due_date_str = match.group(2).strip() if match.group(2) else None
                return {
                    "type": "create",
                    "data": {"title": title, "due_date_str": due_date_str}
                }
        
        # Complete task patterns
        complete_patterns = [
            r"complete (?:task )?(.+)",
            r"done (?:with )?(.+)",
            r"finished (.+)",
            r"mark (.+) (?:as )?(?:complete|done)"
        ]
        
        for pattern in complete_patterns:
            match = re.search(pattern, input_lower)
            if match:
                task_identifier = match.group(1).strip()
                return {
                    "type": "complete",
                    "data": {"task_identifier": task_identifier}
                }
        
        # Delete task patterns
        delete_patterns = [
            r"delete (?:task )?(.+)",
            r"remove (?:task )?(.+)",
            r"cancel (?:task )?(.+)"
        ]
        
        for pattern in delete_patterns:
            match = re.search(pattern, input_lower)
            if match:
                task_identifier = match.group(1).strip()
                return {
                    "type": "delete",
                    "data": {"task_identifier": task_identifier}
                }
        
        # List tasks patterns
        if any(phrase in input_lower for phrase in [
            "show tasks", "list tasks", "my tasks", "what tasks", "tasks list"
        ]):
            status_filter = None
            if "pending" in input_lower or "todo" in input_lower:
                status_filter = "pending"
            elif "completed" in input_lower or "done" in input_lower:
                status_filter = "completed"
            
            return {
                "type": "list",
                "data": {"status": status_filter}
            }
        
        # Update task patterns
        update_patterns = [
            r"update (?:task )?(.+?) (?:to|with) (.+)",
            r"change (?:task )?(.+?) (?:to|with) (.+)",
            r"modify (?:task )?(.+?) (?:to|with) (.+)"
        ]
        
        for pattern in update_patterns:
            match = re.search(pattern, input_lower)
            if match:
                task_identifier = match.group(1).strip()
                new_value = match.group(2).strip()
                return {
                    "type": "update",
                    "data": {"task_identifier": task_identifier, "new_value": new_value}
                }
        
        # Prioritize tasks
        if any(phrase in input_lower for phrase in [
            "prioritize", "priority", "organize tasks", "sort tasks"
        ]):
            return {"type": "prioritize", "data": {}}
        
        # Default to general query
        return {"type": "general", "data": {"query": user_input}}
    
    async def _create_task(self, user_id: str, data: Dict[str, Any]) -> str:
        """Create a new task"""
        try:
            title = data["title"]
            due_date_str = data.get("due_date_str")
            
            # Parse due date if provided
            due_date = None
            if due_date_str:
                due_date = await self._parse_due_date(due_date_str)
            
            # Use LLM to analyze task priority and estimate time
            task_analysis = await self.llm_router.analyze_task_priority(
                title, "", due_date_str or ""
            )
            
            # Create task object
            task = Task(
                title=title,
                due_date=due_date,
                priority=task_analysis.get("priority", "medium"),
                user_id=user_id
            )
            
            # Save to database
            task_id = await self.db_tool.create_task(task)
            
            # Format response
            priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(task.priority, "⚪")
            response = f"✅ **Task Created Successfully!**\n\n"
            response += f"{priority_emoji} **{title}**\n"
            response += f"Priority: {task.priority.title()}\n"
            
            if due_date:
                response += f"Due: {due_date.strftime('%Y-%m-%d %H:%M')}\n"
            
            if task_analysis.get("estimated_hours"):
                response += f"Estimated time: {task_analysis['estimated_hours']} hours\n"
            
            if task_analysis.get("reasoning"):
                response += f"\n💡 *{task_analysis['reasoning']}*"
            
            return response
            
        except Exception as e:
            return f"❌ Sorry, I couldn't create the task. Error: {str(e)}"
    
    async def _complete_task(self, user_id: str, data: Dict[str, Any]) -> str:
        """Mark a task as complete"""
        try:
            task_identifier = data["task_identifier"]
            
            # Find the task
            tasks = await self.db_tool.get_user_tasks(user_id, status="pending")
            matching_task = None
            
            for task in tasks:
                if (task_identifier.lower() in task["title"].lower() or 
                    task["id"] == task_identifier):
                    matching_task = task
                    break
            
            if not matching_task:
                return f"❌ I couldn't find a pending task matching '{task_identifier}'. Please check the task name."
            
            # Update task status
            success = await self.db_tool.update_task_status(matching_task["id"], "completed")
            
            if success:
                return f"🎉 **Great job!** '{matching_task['title']}' has been marked as complete!\n\nKeep up the excellent work! 💪"
            else:
                return f"❌ I had trouble updating the task status. Please try again."
                
        except Exception as e:
            return f"❌ Sorry, I couldn't complete the task. Error: {str(e)}"
    
    async def _delete_task(self, user_id: str, data: Dict[str, Any]) -> str:
        """Delete a task"""
        try:
            task_identifier = data["task_identifier"]
            
            # Find the task
            tasks = await self.db_tool.get_user_tasks(user_id)
            matching_task = None
            
            for task in tasks:
                if (task_identifier.lower() in task["title"].lower() or 
                    task["id"] == task_identifier):
                    matching_task = task
                    break
            
            if not matching_task:
                return f"❌ I couldn't find a task matching '{task_identifier}'. Please check the task name."
            
            # Delete task
            success = await self.db_tool.delete_task(matching_task["id"])
            
            if success:
                return f"🗑️ **Task Deleted:** '{matching_task['title']}' has been removed from your list."
            else:
                return f"❌ I had trouble deleting the task. Please try again."
                
        except Exception as e:
            return f"❌ Sorry, I couldn't delete the task. Error: {str(e)}"
    
    async def _list_tasks(self, user_id: str, data: Dict[str, Any]) -> str:
        """List user's tasks"""
        try:
            status_filter = data.get("status")
            tasks = await self.db_tool.get_user_tasks(user_id, status=status_filter)
            
            if not tasks:
                if status_filter:
                    return f"📝 You have no {status_filter} tasks. Great job staying organized!"
                else:
                    return "📝 You have no tasks yet. Ready to add some goals to achieve?"
            
            # Group tasks by status
            pending_tasks = [t for t in tasks if t["status"] == "pending"]
            completed_tasks = [t for t in tasks if t["status"] == "completed"]
            
            response = "📝 **Your Tasks:**\n\n"
            
            if pending_tasks and (not status_filter or status_filter == "pending"):
                response += "**📋 Pending Tasks:**\n"
                for task in pending_tasks[:10]:  # Limit to 10
                    priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(task["priority"], "⚪")
                    due_info = ""
                    if task["due_date"]:
                        due_date = task["due_date"]
                        if isinstance(due_date, str):
                            due_date = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
                        days_until = (due_date.date() - datetime.now().date()).days
                        if days_until < 0:
                            due_info = " ⚠️ (Overdue)"
                        elif days_until == 0:
                            due_info = " 📅 (Due today)"
                        elif days_until <= 3:
                            due_info = f" 📅 (Due in {days_until} days)"
                    
                    response += f"{priority_emoji} {task['title']}{due_info}\n"
                response += "\n"
            
            if completed_tasks and (not status_filter or status_filter == "completed"):
                response += f"**✅ Completed Tasks ({len(completed_tasks)}):**\n"
                for task in completed_tasks[:5]:  # Show last 5 completed
                    response += f"✅ {task['title']}\n"
            
            if len(tasks) > 15:
                response += f"\n*Showing recent tasks. You have {len(tasks)} total tasks.*"
            
            return response
            
        except Exception as e:
            return f"❌ Sorry, I couldn't retrieve your tasks. Error: {str(e)}"
    
    async def _update_task(self, user_id: str, data: Dict[str, Any]) -> str:
        """Update a task"""
        try:
            task_identifier = data["task_identifier"]
            new_value = data["new_value"]
            
            # Find the task
            tasks = await self.db_tool.get_user_tasks(user_id)
            matching_task = None
            
            for task in tasks:
                if (task_identifier.lower() in task["title"].lower() or 
                    task["id"] == task_identifier):
                    matching_task = task
                    break
            
            if not matching_task:
                return f"❌ I couldn't find a task matching '{task_identifier}'. Please check the task name."
            
            # For now, we'll implement basic priority updates
            # In a full implementation, this would handle various update types
            if new_value.lower() in ["high", "medium", "low"]:
                # This would require a new database method
                return f"📝 Task priority update noted. Full update functionality coming soon!"
            else:
                return f"📝 Task update noted: '{matching_task['title']}' → '{new_value}'. Full update functionality coming soon!"
                
        except Exception as e:
            return f"❌ Sorry, I couldn't update the task. Error: {str(e)}"
    
    async def _prioritize_tasks(self, user_id: str) -> str:
        """Help prioritize user's tasks"""
        try:
            tasks = await self.db_tool.get_user_tasks(user_id, status="pending")
            
            if not tasks:
                return "📝 You have no pending tasks to prioritize. Great job staying on top of things!"
            
            # Analyze tasks for priority suggestions
            high_priority = [t for t in tasks if t["priority"] == "high"]
            medium_priority = [t for t in tasks if t["priority"] == "medium"]
            low_priority = [t for t in tasks if t["priority"] == "low"]
            
            response = "🎯 **Task Prioritization Analysis:**\n\n"
            
            if high_priority:
                response += f"**🔴 High Priority ({len(high_priority)} tasks):**\n"
                response += "Focus on these first!\n"
                for task in high_priority[:3]:
                    response += f"• {task['title']}\n"
                response += "\n"
            
            if medium_priority:
                response += f"**🟡 Medium Priority ({len(medium_priority)} tasks):**\n"
                response += "Schedule these after high-priority items.\n"
                for task in medium_priority[:3]:
                    response += f"• {task['title']}\n"
                response += "\n"
            
            if low_priority:
                response += f"**🟢 Low Priority ({len(low_priority)} tasks):**\n"
                response += "Handle these when you have extra time.\n"
            
            # Add AI-powered prioritization suggestions
            if len(tasks) > 5:
                response += "\n💡 **Suggestion:** Consider breaking down large tasks into smaller, manageable chunks for better progress tracking."
            
            return response
            
        except Exception as e:
            return f"❌ Sorry, I couldn't analyze your task priorities. Error: {str(e)}"
    
    async def _handle_general_task_query(self, user_input: str, user_id: str) -> str:
        """Handle general task-related queries"""
        try:
            # Get user's task context
            tasks = await self.db_tool.get_user_tasks(user_id)
            
            # Use LLM to provide contextual response
            context_prompt = f"""
            User query: {user_input}
            
            User has {len(tasks)} total tasks:
            - {len([t for t in tasks if t['status'] == 'pending'])} pending
            - {len([t for t in tasks if t['status'] == 'completed'])} completed
            
            Recent tasks: {', '.join([t['title'] for t in tasks[:5]])}
            
            Provide a helpful response about task management.
            """
            
            response = await self.llm_router.generate_response([
                {"role": "user", "content": context_prompt}
            ])
            
            return f"📝 **TaskFlow:** {response}"
            
        except Exception as e:
            return f"📝 I'm here to help with your tasks! You can ask me to add, complete, delete, or list your tasks. Error: {str(e)}"
    
    async def _parse_due_date(self, due_date_str: str) -> Optional[datetime]:
        """Parse due date string into datetime object"""
        try:
            due_date_str = due_date_str.lower().strip()
            now = datetime.now()
            
            # Handle relative dates
            if due_date_str in ["today", "now"]:
                return now.replace(hour=23, minute=59, second=59)
            elif due_date_str == "tomorrow":
                return (now + timedelta(days=1)).replace(hour=23, minute=59, second=59)
            elif "next week" in due_date_str:
                return (now + timedelta(weeks=1)).replace(hour=23, minute=59, second=59)
            elif due_date_str.endswith("days"):
                # Extract number of days
                days_match = re.search(r"(\d+)\s*days?", due_date_str)
                if days_match:
                    days = int(days_match.group(1))
                    return (now + timedelta(days=days)).replace(hour=23, minute=59, second=59)
            
            # Try to parse specific date formats
            date_formats = [
                "%Y-%m-%d",
                "%m/%d/%Y",
                "%d/%m/%Y",
                "%Y-%m-%d %H:%M",
                "%m/%d/%Y %H:%M"
            ]
            
            for fmt in date_formats:
                try:
                    return datetime.strptime(due_date_str, fmt)
                except ValueError:
                    continue
            
            return None
            
        except Exception:
            return None