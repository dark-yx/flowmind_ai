# Task 09: Basic Chat UI Connected to LangGraph (Prompt)

## Objective
Implement a chat UI that communicates with the LangGraph multi-agent backend, routing user messages to the appropriate agent/node and displaying responses.

## Deliverables
- Chat UI (web or Bolt.new) connected to LangGraph backend
- FastAPI (or similar) endpoint to receive and route messages
- End-to-end test of UI-backend-agent flow
- Changes committed to version control

## Steps
1. In your backend (e.g., `main.py`), create an endpoint to receive chat messages and route them to the LangGraph graph:
   ```python
   # main.py
   from fastapi import FastAPI
   from langgraph import Graph
   app = FastAPI()
   graph = Graph(...)

   @app.post("/chat")
   async def chat_endpoint(message: str):
       response = graph.run(message)
       return {"response": response}
   ```
2. In your UI (e.g., Bolt.new or React), create a chat component that sends user input to the `/chat` endpoint and displays the response:
   ```js
   // Example fetch in JS
   fetch('/chat', {
     method: 'POST',
     headers: { 'Content-Type': 'application/json' },
     body: JSON.stringify({ message: userInput })
   })
   .then(res => res.json())
   .then(data => setChatResponse(data.response));
   ```
3. Test the full flow: user sends a message, backend routes it through LangGraph, response is shown in the UI.
4. Add and commit the changes:
   ```bash
   git add .
   git commit -m "Connect chat UI to LangGraph multi-agent backend"
   ```

**At the end of this step, run:**
```bash
git push
```
to update the repository. 