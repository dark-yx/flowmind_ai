# Task 04: Netlify CI/CD Setup and LangGraph Deployment (Prompt)

## Objective
Configure CI/CD pipeline and deploy the project to Netlify, ensuring LangGraph and all Python dependencies are installed and the multi-agent backend is accessible to the UI.

## Deliverables
- Netlify deployment configured for Python/LangGraph
- Environment variables set
- FastAPI (or similar) endpoints exposed for UI-backend communication
- Project live on Netlify

## Steps
1. Ensure your `requirements.txt` includes all Python dependencies (langgraph, fastapi, etc.).
2. In your backend, create an API (e.g., with FastAPI) to expose endpoints for the UI to interact with the LangGraph agents:
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
3. Add a `netlify.toml` or similar config to ensure Netlify deploys the Python backend and serves the UI.
4. Set all required environment variables (API keys, secrets) in the Netlify dashboard.
5. Test the live deployment to ensure the app is accessible and the UI can communicate with the backend.
6. Add and commit any deployment configuration files:
   ```bash
   git add .
   git commit -m "Configure Netlify deployment for LangGraph multi-agent backend"
   ```

**At the end of this step, run:**
```bash
git push
```
to update the repository. 