# Task 05: TaskFlow LangGraph Node (Prompt)

## Objective
Implement TaskFlow as a LangGraph node/agent, using the database tool for CRUD operations on tasks.

## Deliverables
- TaskFlow node implemented in Python (agents/taskflow.py)
- Uses db_tool for task management
- Node registered in the LangGraph graph
- Changes committed to version control

## Steps
1. Create `agents/taskflow.py` with a class or function for the TaskFlow node:
   ```python
   # agents/taskflow.py
   from tools.db_tool import create_task, complete_task, delete_task, list_tasks

   def taskflow_node(input, context):
       # Parse input and call the appropriate db_tool function
       if "add task" in input:
           # ...parse and call create_task(...)
           return "Task added."
       elif "complete" in input:
           # ...parse and call complete_task(...)
           return "Task completed."
       # ...etc.
   ```
2. In your main LangGraph setup, register the node:
   ```python
   from agents.taskflow import taskflow_node
   graph.add_node('TaskFlow', taskflow_node)
   ```
3. Ensure the node can access the db_tool and is callable from the graph.
4. Test TaskFlow node independently and as part of the graph.
5. Add and commit the changes:
   ```bash
   git add .
   git commit -m "Implement TaskFlow as LangGraph node with db_tool integration"
   ```

**At the end of this step, run:**
```bash
git push
```
to update the repository. 