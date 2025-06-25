# Task 03: Implement Google OAuth and Google API Tool for LangGraph

## Objective
Set up Google OAuth login and expose Google Calendar/Tasks API as a tool for LangGraph agents.

## Deliverables
- Google OAuth login enabled
- Google API tool implemented in Python (tools/google_api_tool.py)
- Tool registered in LangGraph and accessible to agents
- Auth flow tested and committed

## Steps
1. Set up Google OAuth credentials and configure them in your environment variables or config file.
2. Create a Python module `tools/google_api_tool.py` with functions to:
   - Authenticate users
   - Fetch/create calendar events
   - Fetch/create tasks
   Example:
   ```python
   # tools/google_api_tool.py
   from google.oauth2.credentials import Credentials
   from googleapiclient.discovery import build

   def get_calendar_events(user_token, ...):
       creds = Credentials(token=user_token)
       service = build('calendar', 'v3', credentials=creds)
       # ... fetch events ...
       return events
   # Similar for tasks
   ```
3. In your LangGraph setup (main.py), register the Google API tool so agents can call it:
   ```python
   from tools.google_api_tool import get_calendar_events
   # ...
   graph.add_tool('google_calendar', get_calendar_events)
   # Agents can now use this tool by name
   ```
4. In agent definitions, call the tool as needed (e.g., MindFlow or CalendarFlow node).
5. Test the integration by running the graph and making agent calls to Google APIs.
6. Add and commit the changes:
   ```bash
   git add .
   git commit -m "Add Google OAuth and Google API tool for LangGraph agents"
   ```

**At the end of this step, run:**
```bash
git push
```
to update the repository. 