from typing import Dict, Any, List, Optional
from tools.db_tool import DBTool
from models.state import FlowMindState, AgentResponse, UserMessage
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from langchain_core.tools import tool
from langchain_core.messages import ToolMessage

class TaskFlowAgent:
    def __init__(self, db_tool: DBTool, llm_router):
        self.db_tool = db_tool
        self.llm_router = llm_router
        self.agent_name = "TaskFlow"

    async def process(self, state: FlowMindState) -> FlowMindState:
        user_message_content = state.messages[-1].content
        user_id = state.user_id

        # Select the appropriate LLM based on configuration (from llm_router)
        llm = self.llm_router.get_llm(user_id)

        # Define tools for the agent
        # Note: user_id is implicit from the state, but we'll pass it explicitly to tools for clarity
        # and because LangChain tools often require explicit arguments.

        @tool
        async def create_task(title: str, user_id: str, description: Optional[str] = None, due_date: Optional[str] = None, priority: str = "medium") -> str:
            """Creates a new task with the given title, description, due date (YYYY-MM-DD), and priority. User ID is required."""
            try:
                due_date_dt = datetime.strptime(due_date, "%Y-%m-%d") if due_date else None
                task = await self.db_tool.create_task(title=title, user_id=user_id, description=description, due_date=due_date_dt, priority=priority)
                return f"Task \'{task["title"]}\' created with ID {task["id"]}."
            except Exception as e:
                return f"Error creating task: {e}"

        @tool
        async def list_tasks(user_id: str) -> List[Dict[str, Any]]:
            """Retrieves all tasks for the given user ID."""
            try:
                tasks = await self.db_tool.list_tasks(user_id)
                return tasks
            except Exception as e:
                return f"Error retrieving tasks: {e}"

        @tool
        async def update_task(task_id: str, user_id: str, title: Optional[str] = None, description: Optional[str] = None, due_date: Optional[str] = None, priority: Optional[str] = None, status: Optional[str] = None) -> str:
            """Updates an existing task given its ID. Can update title, description, due date (YYYY-MM-DD), priority, or status. Valid statuses are 'pending', 'completed', 'cancelled'. User ID is required."""
            try:
                data = {}
                if title: data["title"] = title
                if description: data["description"] = description
                if due_date: data["due_date"] = datetime.strptime(due_date, "%Y-%m-%d") if due_date else None
                if priority: data["priority"] = priority
                if status: data["status"] = status

                if not data: # No fields to update
                    return f"No valid fields provided to update for task ID: {task_id}"

                task = await self.db_tool.update_task(task_id, data)
                if task:
                    return f"Task \'{task["title"]}\' (ID: {task["id"]}) updated."
                else:
                    return f"Task with ID {task_id} not found or could not be updated."
            except Exception as e:
                return f"Error updating task: {e}"
        
        @tool
        async def delete_task(task_id: str, user_id: str) -> str:
            """Deletes a task given its ID. User ID is required."""
            try:
                task = await self.db_tool.delete_task(task_id)
                if task:
                    return f"Task \'{task["title"]}\' (ID: {task["id"]}) deleted."
                else:
                    return f"Task with ID {task_id} not found or could not be deleted."
            except Exception as e:
                return f"Error deleting task: {e}"

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "You are a helpful AI assistant specializing in task management. Use the provided tools to manage tasks for the user. Always include the `user_id` when calling a tool. If the user asks to create a task, ensure to ask for a `due_date` in YYYY-MM-DD format if not provided. Respond concisely."),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        # Bind tools to the LLM
        # Ensure the tools are passed as a list of their function objects
        tools = [create_task, list_tasks, update_task, delete_task]
        llm_with_tools = llm.bind_tools(tools=tools)

        # Prepare messages for the chain, including the current user message
        messages_for_chain = [msg.to_langchain_message() for msg in state.messages if isinstance(msg, (UserMessage, AgentResponse))]

        chain = prompt | llm_with_tools

        ai_response = await chain.ainvoke({"messages": messages_for_chain})

        # The response from the chain might be a tool invocation or a direct message
        if ai_response.tool_calls:
            tool_outputs = []
            for tool_call in ai_response.tool_calls:
                # This is a simplified execution. In a real scenario, you'd route based on tool_call.name
                # and pass tool_call.args correctly.
                try:
                    # Pass the user_id from the state to the tool arguments
                    tool_call.args["user_id"] = user_id
                    if tool_call.name == "create_task":
                        output = await create_task(**tool_call.args)
                    elif tool_call.name == "list_tasks":
                        output = await list_tasks(**tool_call.args)
                    elif tool_call.name == "update_task":
                        output = await update_task(**tool_call.args)
                    elif tool_call.name == "delete_task":
                        output = await delete_task(**tool_call.args)
                    else:
                        output = f"Unknown tool: {tool_call.name}"
                    tool_outputs.append(output)
                except Exception as e:
                    tool_outputs.append(f"Error executing tool {tool_call.name}: {e}")

            # Append the tool's output as an AI message or a specific tool output message
            # It's better to append a ToolMessage if it's a tool output
            state.messages.append(ToolMessage(content="\n".join(tool_outputs), tool_call_id=ai_response.tool_calls[0].id)) # Simplified, assumes one tool call

            # Re-invoke the chain with the tool output to get a natural language response
            messages_for_chain.append(ToolMessage(content="\n".join(tool_outputs), tool_call_id=ai_response.tool_calls[0].id))
            final_ai_response = await chain.ainvoke({"messages": messages_for_chain})
            state.messages.append(AgentResponse(content=final_ai_response.content, sender=self.agent_name))

        else:
            state.messages.append(AgentResponse(content=ai_response.content, sender=self.agent_name))

        state.current_agent = self.agent_name
        return state 