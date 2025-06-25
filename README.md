# FlowMind AI

**FlowMind AI** is a proactive personal productivity assistant built on a modern multi-agent architecture using [LangGraph](https://github.com/langchain-ai/langgraph), AI tools, and a low-code philosophy.

---

## 🚀 Vision
FlowMind AI helps users achieve a state of mental "flow" by automating task management, calendar, information, and reminders through intelligent and proactive agents.

---

## 🧠 Multi-Agent Architecture (LangGraph)
- **MindFlow**: Proactive orchestrator, coordinates other agents and intelligent suggestion logic.
- **TaskFlow**: Task management (CRUD, prioritization, completion).
- **CalendarFlow**: Event/calendar management and integration (Google Calendar).
- **InfoFlow**: Summaries, answers, and general queries via LLM.
- **Tools**: Each agent accesses explicit tools (DB, Google API, LLM, ElevenLabs, Tavus, etc.)
- **UI**: Web interface (Bolt.new or React) connected to the multi-agent backend via API (FastAPI).

---

## 🛠️ Tech Stack
- **LangGraph** (Python): Multi-agent orchestration
- **LangChain**: LLM and tool integration
- **FastAPI**: Backend API for UI-agent communication
- **Prisma + PostgreSQL**: Data modeling and persistence
- **Google OAuth 2.0**: Authentication and access to Google Calendar/Tasks
- **ElevenLabs**: Voice input/output
- **Tavus**: Personalized video generation
- **Supabase**: User profiles and external auth
- **Netlify**: CI/CD and deployment
- **Bolt.new**: Low-code UI generation

---

## 📁 Folder Structure
```
FlowMind/
├── agents/           # LangGraph agent nodes (mindflow.py, taskflow.py, etc.)
├── tools/            # Reusable tools (db_tool.py, google_api_tool.py, etc.)
├── ui/               # Web interface (Bolt.new, React, etc.)
├── models/           # Prisma schemas
├── main.py           # Main LangGraph graph and FastAPI endpoints
├── requirements.txt  # Python dependencies
├── ai_docs/          # Technical documentation and master plan
│   ├── master_plan.md
│   ├── FlowMind_AI-Complete_Technical_Proposal.md
│   ├── Technical_Proposal-FlowMind_AI-Your_Proactive_Productivity_Assistant_Powered_by_Bolt.md
│   └── tasks/        # Detailed prompts and tasks
└── README.md         # This file
```

---

## ⚡ Installation & Getting Started
1. **Clone the repository and enter the directory:**
   ```bash
   git clone <repo-url>
   cd FlowMind
   ```
2. **Create and activate a virtual environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Set up environment variables (Google, ElevenLabs, Tavus, Supabase, etc.)**
5. **Run Prisma migrations and prepare the database:**
   ```bash
   # According to your Prisma setup
   ```
6. **Start the backend (FastAPI):**
   ```bash
   uvicorn main:app --reload
   ```
7. **Access the UI** (depending on your stack, Bolt.new or React).

---

## 🚀 Deployment (Backend & Frontend)

### Backend (FastAPI + LangGraph)
- Ensure all environment variables and secrets are set (Google, ElevenLabs, Tavus, Supabase, etc.).
- For production, use a production-ready ASGI server (e.g., Uvicorn or Gunicorn):
  ```bash
  uvicorn main:app --host 0.0.0.0 --port 8000
  # or
  gunicorn -k uvicorn.workers.UvicornWorker main:app
  ```
- Deploy on your preferred platform (Netlify Functions, AWS, GCP, Azure, or a dedicated VM/container).
- Expose the `/chat` and other API endpoints for the frontend.

### Frontend (Bolt.new or React)
- If using **Bolt.new**:
  - Deploy the UI directly from Bolt.new to Netlify or Vercel.
  - Configure the API base URL to point to your deployed backend.
- If using **React**:
  - Build the frontend:
    ```bash
    cd ui
    npm install
    npm run build
    ```
  - Deploy the `build/` directory to Netlify, Vercel, or your preferred static hosting.
  - Set the environment variable (e.g., `REACT_APP_API_URL`) to your backend endpoint.

### Netlify (Recommended for Fullstack)
- Use a `netlify.toml` to configure both frontend and backend (functions or proxy).
- Set all environment variables in the Netlify dashboard.
- Ensure the build command installs Python dependencies and runs migrations if needed.
- Example `netlify.toml` snippet:
  ```toml
  [build]
    command = "pip install -r requirements.txt && npm run build"
    publish = "ui/build"

  [[redirects]]
    from = "/api/*"
    to = "/.netlify/functions/:splat"
    status = 200
  ```

---

## 🤝 How to Contribute
- Read the [master_plan.md](ai_docs/master_plan.md) and the task files in `ai_docs/tasks/`.
- Follow the LangGraph-based agent and tool structure.
- Each new feature should be modular (agent/tool) and documented.
- Make clear pull requests with technical descriptions.

---

## 📚 Technical Documentation
- [Master Plan](ai_docs/master_plan.md)
- [Complete Technical Proposal](ai_docs/FlowMind_AI-Complete_Technical_Proposal.md)
- [Technical Proposal (English)](ai_docs/Technical_Proposal-FlowMind_AI-Your_Proactive_Productivity_Assistant_Powered_by_Bolt.md)
- [Detailed Tasks & Prompts](ai_docs/tasks/)

---

## 📝 Notes
- The project follows a **low-code** philosophy: intelligence is in the prompts, orchestration in LangGraph, and integrations in Python tools.
- For architectural questions, check the diagrams and examples in `ai_docs/`.

---

## 👤 Author
**Jonnathan Peña**

---

**With FlowMind AI, your productivity enters flow!** 