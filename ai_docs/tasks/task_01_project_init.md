# Task 01: Project Initialization with LangGraph (Prompt)

## Objective
Initialize the FlowMind AI project using LangGraph for multi-agent orchestration. Set up the repository, folder structure, and environment for LangGraph-based development.

## Deliverables
- LangGraph installed and ready
- Project scaffolded for multi-agent development
- Initial commit to version control

## Steps
1. Open your terminal and navigate to your workspace directory.
2. (Recommended) Create a Python virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. Install LangGraph and other dependencies:
   ```bash
   pip install langgraph langchain openai prisma supabase elevenlabs tavus
   ```
4. Scaffold the project structure:
   - `agents/` (for LangGraph agent nodes)
   - `tools/` (for reusable tools)
   - `main.py` (entry point for LangGraph graph)
   - `ui/` (for Bolt.new or web UI integration)
5. Initialize a git repository if not already done:
   ```bash
   git init
   ```
6. Add all files and make the first commit:
   ```bash
   git add .
   git commit -m "Initial project setup with LangGraph multi-agent scaffold"
   ```
7. (Optional) Create a remote repository and push your code.

**At the end of this step, run:**
```bash
git push
```
to update the repository. 