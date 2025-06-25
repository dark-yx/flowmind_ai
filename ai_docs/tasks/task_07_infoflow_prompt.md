# Task 07: InfoFlow LangGraph Node (Prompt)

## Objective
Implement InfoFlow as a LangGraph node/agent, using an LLM tool for information queries and summarization.

## Deliverables
- InfoFlow node implemented in Python (agents/infoflow.py)
- Uses llm_tool for information and summaries
- Node registered in the LangGraph graph
- Changes committed to version control

## Steps
1. Create `agents/infoflow.py` with a class or function for the InfoFlow node:
   ```python
   # agents/infoflow.py
   from tools.llm_tool import summarize, explain

   def infoflow_node(input, context):
       if "summarize" in input:
           # ...parse and call summarize(...)
           return "Summary provided."
       elif "explain" in input:
           # ...parse and call explain(...)
           return "Explanation provided."
       # ...etc.
   ```
2. In your main LangGraph setup, register the node:
   ```python
   from agents.infoflow import infoflow_node
   graph.add_node('InfoFlow', infoflow_node)
   ```
3. Ensure the node can access the llm_tool and is callable from the graph.
4. Test InfoFlow node independently and as part of the graph.
5. Add and commit the changes:
   ```bash
   git add .
   git commit -m "Implement InfoFlow as LangGraph node with LLM tool integration"
   ```

**At the end of this step, run:**
```bash
git push
```
to update the repository. 