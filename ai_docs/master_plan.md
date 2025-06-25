# 📘 High-Level Master Plan for FlowMind AI (with LangGraph)

## 🧠 Plan Role
As a technical architect expert in productivity systems with multi-agent AI and low-code platforms, this plan details the modular roadmap to build FlowMind AI using **LangGraph** as the multi-agent framework. All agents will be implemented as LangGraph nodes, each with explicit tools, and the system will leverage modern multi-agent orchestration.

---

## ⚙️ System Context
- **Multi-agent architecture (LangGraph):** MindFlow (proactive orchestrator), TaskFlow (task management), CalendarFlow (events/calendar), InfoFlow (information/summarization), all as LangGraph nodes.
- **Stack:** LangGraph (Python), Bolt.new (UI), PostgreSQL+Prisma, Google OAuth 2.0, ElevenLabs, Tavus, Supabase, Netlify.
- **Key principle:** Intelligence implemented via LangGraph agents and tools, with minimal custom code for integrations.

---

## 🏗️ Phases and Tasks

### **Phase 1: Foundations and Initial Setup**
**Objective:** Establish the project base, install LangGraph, set up the multi-agent environment, authentication, database, and first deployment.
**Key deliverables:** LangGraph installed, agent/node structure scaffolded, Bolt.new UI, Prisma models, Google OAuth, Netlify pipeline.
**Agents/Modules:** No functional agent yet, only technical base and LangGraph skeleton.

- **task_01_project_init.md**
  - **Purpose:** Initialize the project, install LangGraph, set up the repository, folder structure, and environment for multi-agent development.

- **task_02_db_schema.md**
  - **Purpose:** Define Prisma models for Task, Event, Note, LLMConfig, and ensure LangGraph nodes can access the database as a tool.

- **task_03_google_oauth.md**
  - **Purpose:** Implement Google OAuth login and expose Google APIs as tools for LangGraph agents.

- **task_04_netlify_setup.md**
  - **Purpose:** Set up CI/CD and first deployment on Netlify, including LangGraph dependencies and multi-agent structure.

---

### **Phase 2: Multi-Agent Core and Main Logic (LangGraph)**
**Objective:** Implement TaskFlow, CalendarFlow, InfoFlow agents as LangGraph nodes, and the base of MindFlow orchestrator. Each agent uses explicit tools.
**Key deliverables:** LangGraph graph with agent nodes, CRUD logic as tools, basic chat and task UI connected to the graph.
**Agents/Modules:** TaskFlow, CalendarFlow, InfoFlow, MindFlow (all as LangGraph nodes).

- **task_05_taskflow_prompt.md**
  - **Purpose:** Implement TaskFlow as a LangGraph node, using tools for CRUD operations on tasks.

- **task_06_calendarflow_prompt.md**
  - **Purpose:** Implement CalendarFlow as a LangGraph node, using tools for event management and Google Calendar integration.

- **task_07_infoflow_prompt.md**
  - **Purpose:** Implement InfoFlow as a LangGraph node, using tools for LLM queries and summarization.

- **task_08_mindflow_base.md**
  - **Purpose:** Implement MindFlow as the orchestrator node in LangGraph, coordinating other agents and using tools for proactivity and scheduling.

- **task_09_basic_chat_ui.md**
  - **Purpose:** Implement a chat UI connected to the LangGraph, routing user messages to the appropriate agent/node.

---

### **Phase 3: Advanced Integrations and Proactivity**
**Objective:** Integrate voice, video, advanced proactivity, and dynamic LLM management as tools accessible to LangGraph agents.
**Key deliverables:** ElevenLabs, Tavus, Supabase, llmRouter integrations as tools, proactive UI, all accessible from LangGraph nodes.
**Agents/Modules:** MindFlow (proactive), voice/video integration, user management, all as LangGraph nodes/tools.

- **task_10_llm_router.md**
  - **Purpose:** Implement llmRouter as a tool for dynamic LLM model switching, accessible to LangGraph agents.

- **task_11_elevenlabs_voice.md**
  - **Purpose:** Integrate ElevenLabs as a tool for voice input/output, accessible to LangGraph agents.

- **task_12_tavus_video.md**
  - **Purpose:** Integrate Tavus as a tool for personalized video report generation, accessible to LangGraph agents.

- **task_13_supabase_auth.md**
  - **Purpose:** Set up Supabase for user profiles and external auth, accessible as a tool for LangGraph agents.

- **task_14_mindflow_proactive.md**
  - **Purpose:** Enhance MindFlow for automatic suggestions and smart scheduling, orchestrating other nodes via LangGraph.

---

### **Phase 4: Testing, Optimization, and Final Deployment**
**Objective:** Validate, optimize, and deploy the complete LangGraph-based solution.
**Key deliverables:** Test suite for LangGraph agents/tools, UX/UI adjustments, final deployment, documentation.
**Agents/Modules:** All integrated agents and tools in LangGraph.

- **task_15_tests_suite.md**
  - **Purpose:** Implement unit/integration tests for LangGraph agents and tools.

- **task_16_ux_ui_polish.md**
  - **Purpose:** Improve user experience and final design, ensuring smooth interaction with the LangGraph multi-agent system.

- **task_17_final_deploy.md**
  - **Purpose:** Final deployment on Netlify, environment variables, security review, including LangGraph dependencies.

- **task_18_docs_video.md**
  - **Purpose:** Document the system and record demo video, highlighting the LangGraph multi-agent architecture.

---

## 📦 Task File Summary
All files must be created in `/ai_docs/tasks/` following the pattern `task_XX_slug-name.md` and must reference LangGraph and the multi-agent structure.

---

## 📝 Final Notes
- Each task file must include: objective, deliverables, technical steps, LangGraph node/tool structure, and success criteria.
- The plan covers end-to-end: setup, agents as LangGraph nodes, tools, integrations, proactivity, voice, video, testing, and deployment.
- Modularity and clarity for multidisciplinary teams (devs, AI, UX), with explicit use of LangGraph and tools. 