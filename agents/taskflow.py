from typing import Dict, Any, List
from tools.db_tool import DatabaseTool
from models.state import FlowMindState, AgentResponse
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from langchain_core.tools import tool

class TaskFlowAgent:
    def __init__(self, db_tool: DatabaseTool, llm_router):
        self.db_tool = db_tool
        self.llm_router = llm_router # Assuming llm_router will provide a suitable LLM
        self.agent_name = "TaskFlow"

    async def process(self, state: FlowMindState) -> FlowMindState:
        user_message = state.messages[-1].content
        user_id = state.user_id

        # Define tools for the agent
        @tool
        async def create_task(title: str, description: str = None, due_date: str = None, priority: str = "medium") -> str:
            """Creates a new task with the given title, description, due date, and priority. Due date should be in YYYY-MM-DD format."""
            try:
                # Convert due_date string to datetime object if provided
                due_date_dt = datetime.strptime(due_date, "%Y-%m-%d") if due_date else None
                task = await self.db_tool.create_task(title, description, due_date_dt, priority, user_id)
                return f"Task \'{task.title}\' created with ID {task.id}."
            except Exception as e:
                return f"Error creating task: {e}"

        @tool
        async def get_all_tasks() -> List[Dict[str, Any]]:
            """Retrieves all tasks for the current user."""
            try:
                tasks = await self.db_tool.get_all_tasks(user_id)
                return [t.dict() for t in tasks] if tasks else []
            except Exception as e:
                return f"Error retrieving tasks: {e}"

        @tool
        async def update_task_status(task_id: str, status: str) -> str:
            """Updates the status of a task given its ID. Valid statuses are \'pending\', \'completed\', \'cancelled\'."""
            try:
                task = await self.db_tool.update_task(task_id, status=status)
                return f"Task \'{task.title}\' (ID: {task.id}) status updated to {task.status}."
            except Exception as e:
                return f"Error updating task status: {e}"
        
        @tool
        async def delete_task(task_id: str) -> str:
            """Deletes a task given its ID."""
            try:
                task = await self.db_tool.delete_task(task_id)
                return f"Task \'{task.title}\' (ID: {task.id}) deleted."
            except Exception as e:
                return f"Error deleting task: {e}"

        # Select the appropriate LLM based on configuration (from llm_router)
        llm = self.llm_router.get_llm(user_id) # Assuming get_llm returns a configured LLM instance

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "You are a helpful AI assistant specializing in task management. Use the provided tools to manage tasks for the user. Respond concisely."),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        # Bind tools to the LLM
        llm_with_tools = llm.bind_tools(tools=[create_task, get_all_tasks, update_task_status, delete_task])

        chain = {"messages": RunnablePassthrough()} | prompt | llm_with_tools

        # Prepare messages for the chain, including the current user message
        # In a real scenario, you would convert FlowMindState messages to LangChain messages if needed.
        # For now, assuming direct compatibility for simplicity or a prior conversion.
        messages_for_chain = [msg.to_langchain_message() for msg in state.messages] # Assuming FlowMindState messages have a to_langchain_message method

        # Invoke the chain
        ai_response = await chain.ainvoke(messages_for_chain)

        # The response from the chain might be a tool invocation or a direct message
        if ai_response.tool_calls:
            tool_output = []
            for tool_call in ai_response.tool_calls:
                # This is a simplified execution. In a real scenario, you'd route based on tool_call.name
                # and pass tool_call.args correctly.
                # For now, let's assume direct mapping based on the tool definition.
                if tool_call.name == "create_task":
                    output = await create_task(**tool_call.args)
                elif tool_call.name == "get_all_tasks":
                    output = await get_all_tasks()
                elif tool_call.name == "update_task_status":
                    output = await update_task_status(**tool_call.args)
                elif tool_call.name == "delete_task":
                    output = await delete_task(**tool_call.args)
                else:
                    output = f"Unknown tool: {tool_call.name}"
                tool_output.append(output)
            # Append the tool's output as an AI message or a specific tool output message
            state.messages.append(AgentResponse(content="\n".join(tool_output), sender=self.agent_name, type="tool_output"))
        else:
            state.messages.append(AgentResponse(content=ai_response.content, sender=self.agent_name))

        state.current_agent = self.agent_name
        return state 