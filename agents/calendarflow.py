"""
FlowMind AI - CalendarFlow Agent (LangGraph Node)
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import re

from models.state import FlowMindState, AgentResponse, Event
from tools.db_tool import DatabaseTool
from tools.google_api_tool import GoogleAPITool
from tools.llm_router import LLMRouter

class CalendarFlowAgent:
    """
    CalendarFlow - Agent responsible for calendar and event management
    """
    
    def __init__(self, db_tool: DatabaseTool, google_tool: GoogleAPITool, llm_router: LLMRouter):
        self.db_tool = db_tool
        self.google_tool = google_tool
        self.llm_router = llm_router
        self.agent_name = "CalendarFlow"
    
    async def process(self, state: FlowMindState) -> AgentResponse:
        """Main processing method for CalendarFlow agent"""
        user_input = state.messages[-1].content if state.messages else ""
        user_id = state.user_id
        
        # Parse calendar-related commands
        action = await self._parse_calendar_action(user_input)
        
        if action["type"] == "create_event":
            response = await self._create_event(user_id, action["data"])
        elif action["type"] == "list_events":
            response = await self._list_events(user_id, action["data"])
        elif action["type"] == "check_availability":
            response = await self._check_availability(user_id, action["data"])
        elif action["type"] == "schedule_meeting":
            response = await self._schedule_meeting(user_id, action["data"])
        elif action["type"] == "find_free_time":
            response = await self._find_free_time(user_id, action["data"])
        else:
            response = await self._handle_general_calendar_query(user_input, user_id)
        
        return AgentResponse(
            content=response,
            agent=self.agent_name,
            context={"action": action["type"], "user_id": user_id}
        )
    
    async def _parse_calendar_action(self, user_input: str) -> Dict[str, Any]:
        """Parse user input to determine calendar action"""
        input_lower = user_input.lower()
        
        # Create event patterns
        event_patterns = [
            r"schedule (.+?) (?:at|on|for) (.+?)(?:\s+(?:at|from)\s+(.+))?$",
            r"add event (.+?) (?:at|on|for) (.+?)(?:\s+(?:at|from)\s+(.+))?$",
            r"create meeting (.+?) (?:at|on|for) (.+?)(?:\s+(?:at|from)\s+(.+))?$",
            r"book (.+?) (?:at|on|for) (.+?)(?:\s+(?:at|from)\s+(.+))?$"
        ]
        
        for pattern in event_patterns:
            match = re.search(pattern, input_lower)
            if match:
                title = match.group(1).strip()
                date_str = match.group(2).strip()
                time_str = match.group(3).strip() if match.group(3) else None
                return {
                    "type": "create_event",
                    "data": {"title": title, "date_str": date_str, "time_str": time_str}
                }
        
        # List events patterns
        if any(phrase in input_lower for phrase in [
            "what do i have", "my schedule", "today's events", "tomorrow's events",
            "show calendar", "list events", "what's on my calendar"
        ]):
            time_filter = "today"
            if "tomorrow" in input_lower:
                time_filter = "tomorrow"
            elif "week" in input_lower:
                time_filter = "week"
            elif "month" in input_lower:
                time_filter = "month"
            
            return {
                "type": "list_events",
                "data": {"time_filter": time_filter}
            }
        
        # Check availability patterns
        availability_patterns = [
            r"am i (?:free|available) (?:at|on) (.+)",
            r"do i have (?:time|availability) (?:at|on) (.+)",
            r"check availability (?:for|at|on) (.+)",
            r"free time (?:at|on) (.+)"
        ]
        
        for pattern in availability_patterns:
            match = re.search(pattern, input_lower)
            if match:
                time_str = match.group(1).strip()
                return {
                    "type": "check_availability",
                    "data": {"time_str": time_str}
                }
        
        # Find free time patterns
        if any(phrase in input_lower for phrase in [
            "find free time", "when am i free", "available slots", "free slots"
        ]):
            duration = 60  # Default 1 hour
            duration_match = re.search(r"(\d+)\s*(?:hour|hr|minute|min)", input_lower)
            if duration_match:
                duration = int(duration_match.group(1))
                if "minute" in input_lower or "min" in input_lower:
                    pass  # Already in minutes
                else:
                    duration *= 60  # Convert hours to minutes
            
            return {
                "type": "find_free_time",
                "data": {"duration": duration}
            }
        
        # Schedule meeting patterns
        meeting_patterns = [
            r"schedule (?:a )?meeting (?:with )?(.+?) (?:at|on|for) (.+?)(?:\s+(?:at|from)\s+(.+))?$",
            r"set up (?:a )?meeting (?:with )?(.+?) (?:at|on|for) (.+?)(?:\s+(?:at|from)\s+(.+))?$"
        ]
        
        for pattern in meeting_patterns:
            match = re.search(pattern, input_lower)
            if match:
                attendees = match.group(1).strip()
                date_str = match.group(2).strip()
                time_str = match.group(3).strip() if match.group(3) else None
                return {
                    "type": "schedule_meeting",
                    "data": {"attendees": attendees, "date_str": date_str, "time_str": time_str}
                }
        
        # Default to general query
        return {"type": "general", "data": {"query": user_input}}
    
    async def _create_event(self, user_id: str, data: Dict[str, Any]) -> str:
        """Create a new calendar event"""
        try:
            title = data["title"]
            date_str = data["date_str"]
            time_str = data.get("time_str")
            
            # Parse date and time
            start_time = await self._parse_datetime(date_str, time_str)
            if not start_time:
                return f"❌ I couldn't understand the date/time '{date_str} {time_str or ''}'. Please try a format like 'tomorrow at 2 PM' or '2024-01-15 14:00'."
            
            # Default duration: 1 hour
            end_time = start_time + timedelta(hours=1)
            
            # Create event object
            event = Event(
                title=title,
                start_time=start_time,
                end_time=end_time,
                user_id=user_id
            )
            
            # Try to create in Google Calendar first
            try:
                google_event = await self.google_tool.create_calendar_event(user_id, {
                    "title": title,
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat()
                })
                event.google_event_id = google_event.get("id")
            except Exception as e:
                print(f"Google Calendar creation failed: {e}")
                # Continue with local storage
            
            # Save to local database
            event_id = await self.db_tool.create_event(event)
            
            # Format response
            response = f"📅 **Event Created Successfully!**\n\n"
            response += f"**{title}**\n"
            response += f"📅 {start_time.strftime('%A, %B %d, %Y')}\n"
            response += f"🕐 {start_time.strftime('%I:%M %p')} - {end_time.strftime('%I:%M %p')}\n"
            
            if event.google_event_id:
                response += "\n✅ Added to your Google Calendar"
            else:
                response += "\n📝 Saved locally (Google Calendar sync unavailable)"
            
            return response
            
        except Exception as e:
            return f"❌ Sorry, I couldn't create the event. Error: {str(e)}"
    
    async def _list_events(self, user_id: str, data: Dict[str, Any]) -> str:
        """List user's calendar events"""
        try:
            time_filter = data.get("time_filter", "today")
            
            # Determine date range
            now = datetime.now()
            if time_filter == "today":
                start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
                end_date = now.replace(hour=23, minute=59, second=59, microsecond=999999)
                title = "Today's Schedule"
            elif time_filter == "tomorrow":
                tomorrow = now + timedelta(days=1)
                start_date = tomorrow.replace(hour=0, minute=0, second=0, microsecond=0)
                end_date = tomorrow.replace(hour=23, minute=59, second=59, microsecond=999999)
                title = "Tomorrow's Schedule"
            elif time_filter == "week":
                start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
                end_date = now + timedelta(days=7)
                title = "This Week's Schedule"
            else:  # month
                start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
                end_date = now + timedelta(days=30)
                title = "This Month's Schedule"
            
            # Get events from both Google Calendar and local database
            events = []
            
            try:
                google_events = await self.google_tool.get_calendar_events(
                    user_id, start_date, end_date
                )
                events.extend(google_events)
            except Exception as e:
                print(f"Google Calendar fetch failed: {e}")
            
            # Get local events
            local_events = await self.db_tool.get_user_events(user_id, start_date, end_date)
            events.extend(local_events)
            
            # Remove duplicates and sort
            unique_events = {}
            for event in events:
                key = f"{event.get('title', '')}{event.get('start_time', '')}"
                if key not in unique_events:
                    unique_events[key] = event
            
            events = list(unique_events.values())
            events.sort(key=lambda x: x.get('start_time', datetime.now()))
            
            if not events:
                return f"📅 **{title}:**\n\nNo events scheduled. You have a free day! 🎉"
            
            response = f"📅 **{title}:**\n\n"
            
            current_date = None
            for event in events[:20]:  # Limit to 20 events
                event_start = event.get('start_time')
                if isinstance(event_start, str):
                    event_start = datetime.fromisoformat(event_start.replace('Z', '+00:00'))
                
                # Group by date
                event_date = event_start.date()
                if current_date != event_date:
                    current_date = event_date
                    response += f"\n**{event_date.strftime('%A, %B %d')}:**\n"
                
                # Format time
                time_str = event_start.strftime('%I:%M %p')
                event_end = event.get('end_time')
                if event_end:
                    if isinstance(event_end, str):
                        event_end = datetime.fromisoformat(event_end.replace('Z', '+00:00'))
                    time_str += f" - {event_end.strftime('%I:%M %p')}"
                
                response += f"🕐 {time_str} - {event.get('title', 'Untitled Event')}\n"
                
                if event.get('location'):
                    response += f"   📍 {event['location']}\n"
            
            if len(events) > 20:
                response += f"\n*Showing first 20 events. You have {len(events)} total events.*"
            
            return response
            
        except Exception as e:
            return f"❌ Sorry, I couldn't retrieve your calendar events. Error: {str(e)}"
    
    async def _check_availability(self, user_id: str, data: Dict[str, Any]) -> str:
        """Check availability at a specific time"""
        try:
            time_str = data["time_str"]
            
            # Parse the time
            check_time = await self._parse_datetime(time_str)
            if not check_time:
                return f"❌ I couldn't understand the time '{time_str}'. Please try a format like 'tomorrow at 2 PM' or '2024-01-15 14:00'."
            
            # Check for conflicts
            start_window = check_time - timedelta(minutes=30)
            end_window = check_time + timedelta(minutes=30)
            
            events = await self.db_tool.get_user_events(user_id, start_window, end_window)
            
            try:
                google_events = await self.google_tool.get_calendar_events(
                    user_id, start_window, end_window
                )
                events.extend(google_events)
            except Exception as e:
                print(f"Google Calendar check failed: {e}")
            
            if not events:
                return f"✅ **You're free!**\n\n📅 {check_time.strftime('%A, %B %d, %Y')}\n🕐 {check_time.strftime('%I:%M %p')}\n\nNo conflicts found in your calendar."
            else:
                response = f"❌ **You have conflicts:**\n\n📅 {check_time.strftime('%A, %B %d, %Y')}\n🕐 {check_time.strftime('%I:%M %p')}\n\n"
                response += "**Conflicting events:**\n"
                for event in events[:3]:  # Show up to 3 conflicts
                    event_start = event.get('start_time')
                    if isinstance(event_start, str):
                        event_start = datetime.fromisoformat(event_start.replace('Z', '+00:00'))
                    response += f"• {event.get('title', 'Event')} at {event_start.strftime('%I:%M %p')}\n"
                
                return response
            
        except Exception as e:
            return f"❌ Sorry, I couldn't check your availability. Error: {str(e)}"
    
    async def _find_free_time(self, user_id: str, data: Dict[str, Any]) -> str:
        """Find free time slots"""
        try:
            duration = data.get("duration", 60)  # Default 1 hour in minutes
            
            # Get free time slots
            free_slots = await self.google_tool.get_free_time_slots(user_id, duration)
            
            if not free_slots:
                return f"📅 I couldn't find any free slots of {duration} minutes in the next few days. Your calendar is quite busy!"
            
            response = f"🕐 **Available Time Slots ({duration} minutes):**\n\n"
            
            current_date = None
            for slot in free_slots[:10]:  # Show up to 10 slots
                slot_start = slot.get('start_time')
                if isinstance(slot_start, str):
                    slot_start = datetime.fromisoformat(slot_start.replace('Z', '+00:00'))
                
                # Group by date
                slot_date = slot_start.date()
                if current_date != slot_date:
                    current_date = slot_date
                    response += f"\n**{slot_date.strftime('%A, %B %d')}:**\n"
                
                # Calculate end time
                slot_end = slot_start + timedelta(minutes=duration)
                time_range = f"{slot_start.strftime('%I:%M %p')} - {slot_end.strftime('%I:%M %p')}"
                response += f"✅ {time_range}\n"
            
            response += "\nWould you like me to schedule something in one of these slots?"
            return response
            
        except Exception as e:
            return f"❌ Sorry, I couldn't find free time slots. Error: {str(e)}"
    
    async def _schedule_meeting(self, user_id: str, data: Dict[str, Any]) -> str:
        """Schedule a meeting with attendees"""
        try:
            attendees = data["attendees"]
            date_str = data["date_str"]
            time_str = data.get("time_str")
            
            # Parse date and time
            start_time = await self._parse_datetime(date_str, time_str)
            if not start_time:
                return f"❌ I couldn't understand the date/time '{date_str} {time_str or ''}'. Please try a format like 'tomorrow at 2 PM'."
            
            # Default meeting duration: 1 hour
            end_time = start_time + timedelta(hours=1)
            
            title = f"Meeting with {attendees}"
            
            # Create the meeting
            event = Event(
                title=title,
                start_time=start_time,
                end_time=end_time,
                user_id=user_id
            )
            
            # Try to create in Google Calendar
            try:
                google_event = await self.google_tool.create_calendar_event(user_id, {
                    "title": title,
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "attendees": attendees
                })
                event.google_event_id = google_event.get("id")
            except Exception as e:
                print(f"Google Calendar meeting creation failed: {e}")
            
            # Save locally
            event_id = await self.db_tool.create_event(event)
            
            response = f"🤝 **Meeting Scheduled!**\n\n"
            response += f"**{title}**\n"
            response += f"📅 {start_time.strftime('%A, %B %d, %Y')}\n"
            response += f"🕐 {start_time.strftime('%I:%M %p')} - {end_time.strftime('%I:%M %p')}\n"
            
            if event.google_event_id:
                response += "\n✅ Added to Google Calendar with invitations"
            else:
                response += "\n📝 Saved locally (Google Calendar sync unavailable)"
            
            return response
            
        except Exception as e:
            return f"❌ Sorry, I couldn't schedule the meeting. Error: {str(e)}"
    
    async def _handle_general_calendar_query(self, user_input: str, user_id: str) -> str:
        """Handle general calendar-related queries"""
        try:
            # Get user's calendar context
            today_events = await self.db_tool.get_user_events(
                user_id, 
                datetime.now().replace(hour=0, minute=0, second=0),
                datetime.now().replace(hour=23, minute=59, second=59)
            )
            
            # Use LLM to provide contextual response
            context_prompt = f"""
            User query: {user_input}
            
            User has {len(today_events)} events today.
            Recent events: {', '.join([e.get('title', 'Event') for e in today_events[:3]])}
            
            Provide a helpful response about calendar management.
            """
            
            response = await self.llm_router.generate_response([
                {"role": "user", "content": context_prompt}
            ])
            
            return f"📅 **CalendarFlow:** {response}"
            
        except Exception as e:
            return f"📅 I'm here to help with your calendar! You can ask me to schedule events, check availability, or show your schedule. Error: {str(e)}"
    
    async def _parse_datetime(self, date_str: str, time_str: str = None) -> Optional[datetime]:
        """Parse date and time strings into datetime object"""
        try:
            combined_str = f"{date_str} {time_str or ''}".strip().lower()
            now = datetime.now()
            
            # Handle relative dates
            if "today" in combined_str:
                base_date = now.date()
            elif "tomorrow" in combined_str:
                base_date = (now + timedelta(days=1)).date()
            elif "next week" in combined_str:
                base_date = (now + timedelta(weeks=1)).date()
            else:
                base_date = now.date()
            
            # Handle time parsing
            time_part = None
            if time_str:
                time_patterns = [
                    r"(\d{1,2}):(\d{2})\s*(am|pm)",
                    r"(\d{1,2})\s*(am|pm)",
                    r"(\d{1,2}):(\d{2})",
                    r"(\d{1,2})"
                ]
                
                for pattern in time_patterns:
                    match = re.search(pattern, time_str.lower())
                    if match:
                        hour = int(match.group(1))
                        minute = int(match.group(2)) if len(match.groups()) > 1 and match.group(2) else 0
                        
                        # Handle AM/PM
                        if len(match.groups()) > 2 and match.group(3):
                            if match.group(3) == "pm" and hour != 12:
                                hour += 12
                            elif match.group(3) == "am" and hour == 12:
                                hour = 0
                        
                        time_part = datetime.combine(base_date, datetime.min.time().replace(hour=hour, minute=minute))
                        break
            
            if time_part:
                return time_part
            else:
                # Default to current time or reasonable default
                return datetime.combine(base_date, datetime.min.time().replace(hour=9, minute=0))
            
        except Exception as e:
            print(f"Date parsing error: {e}")
            return None