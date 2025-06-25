# Task 02: Define Database Schema for LangGraph Agents (Prompt)

## Objective
Define the Prisma models for Task, Event, Note, and LLMConfig, and expose database access as a tool for LangGraph agents.

## Deliverables
- Prisma models for Task, Event, Note, LLMConfig
- Database access tool implemented for LangGraph
- Schema and tool committed to version control

## Steps
1. In the project, navigate to the models directory (e.g., `models/` or `server/models/`).
2. Create or edit the following Prisma schema files:
   - `Task.prisma`
   - `Event.prisma`
   - `Note.prisma`
   - `LLMConfig.prisma`
3. Example for `Task.prisma`:
   ```prisma
   model Task {
     id          String   @id @default(uuid())
     title       String
     description String?
     due_date    DateTime?
     priority    String   @default("medium")
     status      String   @default("pending")
     user_id     String
     created_at  DateTime @default(now())
     updated_at  DateTime @updatedAt
   }
   ```
4. Implement a Python module in `tools/` (e.g., `tools/db_tool.py`) that provides CRUD functions for the database and can be registered as a tool in LangGraph.
5. In your LangGraph agent definitions, import and register the database tool so that agents can perform CRUD operations via the tool interface.
6. Run Prisma migration commands to apply the schema.
7. Add and commit the changes:
   ```bash
   git add .
   git commit -m "Add Prisma models and database tool for LangGraph agents"
   ```

**At the end of this step, run:**
```bash
git push
```
to update the repository. 