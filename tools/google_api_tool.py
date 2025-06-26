"""
FlowMind AI - Google API Tool for Calendar and Tasks Integration
"""
import os
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json

# Note: In a real implementation, you would use the actual Google API client
# For this demo, we'll simulate the Google API responses

class GoogleAPITool:
    """Google API integration tool for FlowMind AI agents"""
    
    def __init__(self):
        self.client_id = os.getenv("GOOGLE_CLIENT_ID")
        self.client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
        self.redirect_uri = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/google/callback")
        
        # In a real implementation, this would store actual OAuth tokens
        self.user_tokens = {}
    
    async def authenticate_user(self, user_id: str, auth_code: str) -> Dict[str, Any]:
        """Authenticate user with Google OAuth"""
        try:
            # In a real implementation, this would exchange the auth code for tokens
            # For demo purposes, we'll simulate a successful authentication
            
            mock_token_response = {
                "access_token": f"mock_access_token_{user_id}",
                "refresh_token": f"mock_refresh_token_{user_id}",
                "expires_in": 3600,
                "scope": "https://www.googleapis.com/auth/calendar https://www.googleapis.com/auth/tasks"
            }
            
            # Store tokens (in real implementation, store securely in database)
            self.user_tokens[user_id] = mock_token_response
            
            return {
                "success": True,
                "user_info": {
                    "id": user_id,
                    "email": f"user_{user_id}@example.com",
                    "name": f"User {user_id}"
                }
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_calendar_events(self, user_id: str, start_date: Optional[datetime] = None, 
                                 end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Get calendar events for a user"""
        try:
            # Check if user is authenticated
            if user_id not in self.user_tokens:
                return []
            
            # Set default date range if not provided
            if not start_date:
                start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            if not end_date:
                end_date = start_date + timedelta(days=7)
            
            # In a real implementation, this would make actual Google Calendar API calls
            # For demo purposes, we'll return mock events
            mock_events = [
                {
                    "id": f"event_1_{user_id}",
                    "title": "Team Meeting",
                    "start_time": (start_date + timedelta(hours=9)).isoformat(),
                    "end_time": (start_date + timedelta(hours=10)).isoformat(),
                    "location": "Conference Room A",
                    "description": "Weekly team sync"
                },
                {
                    "id": f"event_2_{user_id}",
                    "title": "Project Review",
                    "start_time": (start_date + timedelta(hours=14)).isoformat(),
                    "end_time": (start_date + timedelta(hours=15, minutes=30)).isoformat(),
                    "location": "Virtual",
                    "description": "Q4 project review meeting"
                },
                {
                    "id": f"event_3_{user_id}",
                    "title": "Client Call",
                    "start_time": (start_date + timedelta(days=1, hours=11)).isoformat(),
                    "end_time": (start_date + timedelta(days=1, hours=12)).isoformat(),
                    "location": "Phone",
                    "description": "Monthly client check-in"
                }
            ]
            
            # Filter events within the date range
            filtered_events = []
            for event in mock_events:
                event_start = datetime.fromisoformat(event["start_time"])
                if start_date <= event_start <= end_date:
                    filtered_events.append(event)
            
            return filtered_events
            
        except Exception as e:
            print(f"Error fetching calendar events: {e}")
            return []
    
    async def create_calendar_event(self, user_id: str, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new calendar event"""
        try:
            # Check if user is authenticated
            if user_id not in self.user_tokens:
                raise Exception("User not authenticated with Google")
            
            # In a real implementation, this would create an actual Google Calendar event
            # For demo purposes, we'll return a mock created event
            
            event_id = f"created_event_{user_id}_{datetime.now().timestamp()}"
            
            created_event = {
                "id": event_id,
                "title": event_data.get("title", "New Event"),
                "start_time": event_data.get("start_time"),
                "end_time": event_data.get("end_time"),
                "location": event_data.get("location"),
                "description": event_data.get("description"),
                "attendees": event_data.get("attendees", []),
                "created": datetime.now().isoformat(),
                "status": "confirmed"
            }
            
            return created_event
            
        except Exception as e:
            raise Exception(f"Failed to create calendar event: {str(e)}")
    
    async def update_calendar_event(self, user_id: str, event_id: str, 
                                   event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing calendar event"""
        try:
            # Check if user is authenticated
            if user_id not in self.user_tokens:
                raise Exception("User not authenticated with Google")
            
            # In a real implementation, this would update the actual Google Calendar event
            # For demo purposes, we'll return a mock updated event
            
            updated_event = {
                "id": event_id,
                "title": event_data.get("title", "Updated Event"),
                "start_time": event_data.get("start_time"),
                "end_time": event_data.get("end_time"),
                "location": event_data.get("location"),
                "description": event_data.get("description"),
                "updated": datetime.now().isoformat(),
                "status": "confirmed"
            }
            
            return updated_event
            
        except Exception as e:
            raise Exception(f"Failed to update calendar event: {str(e)}")
    
    async def delete_calendar_event(self, user_id: str, event_id: str) -> bool:
        """Delete a calendar event"""
        try:
            # Check if user is authenticated
            if user_id not in self.user_tokens:
                raise Exception("User not authenticated with Google")
            
            # In a real implementation, this would delete the actual Google Calendar event
            # For demo purposes, we'll return success
            
            return True
            
        except Exception as e:
            print(f"Failed to delete calendar event: {str(e)}")
            return False
    
    async def get_free_time_slots(self, user_id: str, duration_minutes: int = 60, 
                                 days_ahead: int = 7) -> List[Dict[str, Any]]:
        """Find free time slots in the user's calendar"""
        try:
            # Check if user is authenticated
            if user_id not in self.user_tokens:
                return []
            
            # Get existing events
            start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(days=days_ahead)
            
            events = await self.get_calendar_events(user_id, start_date, end_date)
            
            # Find free slots (simplified algorithm)
            free_slots = []
            current_date = start_date
            
            while current_date < end_date:
                # Check business hours (9 AM to 6 PM)
                work_start = current_date.replace(hour=9, minute=0)
                work_end = current_date.replace(hour=18, minute=0)
                
                # Skip weekends for this demo
                if current_date.weekday() >= 5:
                    current_date += timedelta(days=1)
                    continue
                
                # Find gaps between events
                current_time = work_start
                day_events = []
                
                for event in events:
                    event_start = datetime.fromisoformat(event["start_time"])
                    event_end = datetime.fromisoformat(event["end_time"])
                    
                    if (event_start.date() == current_date.date() and 
                        work_start <= event_start <= work_end):
                        day_events.append((event_start, event_end))
                
                # Sort events by start time
                day_events.sort(key=lambda x: x[0])
                
                # Find free slots between events
                for i, (event_start, event_end) in enumerate(day_events):
                    # Check if there's a gap before this event
                    if (event_start - current_time).total_seconds() >= duration_minutes * 60:
                        free_slots.append({
                            "start_time": current_time.isoformat(),
                            "end_time": event_start.isoformat(),
                            "duration": int((event_start - current_time).total_seconds() / 60)
                        })
                    
                    current_time = max(current_time, event_end)
                
                # Check if there's time after the last event
                if (work_end - current_time).total_seconds() >= duration_minutes * 60:
                    free_slots.append({
                        "start_time": current_time.isoformat(),
                        "end_time": work_end.isoformat(),
                        "duration": int((work_end - current_time).total_seconds() / 60)
                    })
                
                current_date += timedelta(days=1)
            
            # Filter slots that meet the minimum duration requirement
            suitable_slots = [
                slot for slot in free_slots 
                if slot["duration"] >= duration_minutes
            ]
            
            return suitable_slots[:20]  # Return up to 20 slots
            
        except Exception as e:
            print(f"Error finding free time slots: {e}")
            return []
    
    async def get_today_events(self, user_id: str) -> List[Dict[str, Any]]:
        """Get today's events for a user"""
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow = today + timedelta(days=1)
        
        return await self.get_calendar_events(user_id, today, tomorrow)
    
    async def get_tasks(self, user_id: str) -> List[Dict[str, Any]]:
        """Get Google Tasks for a user"""
        try:
            # Check if user is authenticated
            if user_id not in self.user_tokens:
                return []
            
            # In a real implementation, this would fetch actual Google Tasks
            # For demo purposes, we'll return mock tasks
            
            mock_tasks = [
                {
                    "id": f"task_1_{user_id}",
                    "title": "Review quarterly reports",
                    "notes": "Check all department reports for Q4",
                    "status": "needsAction",
                    "due": (datetime.now() + timedelta(days=2)).isoformat()
                },
                {
                    "id": f"task_2_{user_id}",
                    "title": "Prepare presentation",
                    "notes": "Client presentation for next week",
                    "status": "needsAction",
                    "due": (datetime.now() + timedelta(days=5)).isoformat()
                },
                {
                    "id": f"task_3_{user_id}",
                    "title": "Team one-on-ones",
                    "notes": "Schedule individual meetings with team members",
                    "status": "needsAction",
                    "due": (datetime.now() + timedelta(days=7)).isoformat()
                }
            ]
            
            return mock_tasks
            
        except Exception as e:
            print(f"Error fetching Google Tasks: {e}")
            return []
    
    async def create_task(self, user_id: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new Google Task"""
        try:
            # Check if user is authenticated
            if user_id not in self.user_tokens:
                raise Exception("User not authenticated with Google")
            
            # In a real implementation, this would create an actual Google Task
            # For demo purposes, we'll return a mock created task
            
            task_id = f"created_task_{user_id}_{datetime.now().timestamp()}"
            
            created_task = {
                "id": task_id,
                "title": task_data.get("title", "New Task"),
                "notes": task_data.get("notes", ""),
                "status": "needsAction",
                "due": task_data.get("due"),
                "created": datetime.now().isoformat()
            }
            
            return created_task
            
        except Exception as e:
            raise Exception(f"Failed to create Google Task: {str(e)}")
    
    async def is_user_authenticated(self, user_id: str) -> bool:
        """Check if user is authenticated with Google"""
        return user_id in self.user_tokens
    
    async def get_auth_url(self, user_id: str) -> str:
        """Get Google OAuth authorization URL"""
        # In a real implementation, this would generate the actual OAuth URL
        base_url = "https://accounts.google.com/o/oauth2/v2/auth"
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": "https://www.googleapis.com/auth/calendar https://www.googleapis.com/auth/tasks",
            "response_type": "code",
            "access_type": "offline",
            "state": user_id
        }
        
        # Build URL with parameters
        param_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{base_url}?{param_string}"