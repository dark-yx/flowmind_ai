# Task 06: CalendarFlow LangGraph Node (Prompt)

## Objective
Implement CalendarFlow as a LangGraph node/agent, using the Google API tool for event and calendar management.

## Deliverables
- CalendarFlow node implemented in Python (agents/calendarflow.py)
- Uses google_api_tool for calendar operations
- Node registered in the LangGraph graph
- Changes committed to version control

## Steps
1. Create `agents/calendarflow.py` with a class or function for the CalendarFlow node:
   ```python
   # agents/calendarflow.py
   from tools.google_api_tool import get_calendar_events, create_calendar_event

   def calendarflow_node(input, context):
       # Parse input and call the appropriate google_api_tool function
       if "schedule event" in input:
           # ...parse and call create_calendar_event(...)
           return "Event scheduled."
       elif "what do I have tomorrow" in input:
           # ...call get_calendar_events(...)
           return "Events listed."
       # ...etc.
   ```
2. In your main LangGraph setup, register the node:
   ```python
   from agents.calendarflow import calendarflow_node
   graph.add_node('CalendarFlow', calendarflow_node)
   ```
3. Ensure the node can access the google_api_tool and is callable from the graph.
4. Test CalendarFlow node independently and as part of the graph.
5. Add and commit the changes:
   ```bash
   git add .
   git commit -m "Implement CalendarFlow as LangGraph node with Google API tool integration"
   ```

**At the end of this step, run:**
```bash
git push
```
to update the repository. 