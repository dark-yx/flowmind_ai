"""
FlowMind AI - Dynamic LLM Router Tool
"""
import os
from typing import Dict, Any, List, Optional
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from tools.db_tool import DatabaseTool

class LLMRouter:
    """Dynamic LLM routing tool for FlowMind AI agents"""
    
    def __init__(self):
        self.db_tool = DatabaseTool()
        self.llm_cache = {}
        
        # Default configurations
        self.default_configs = {
            "openai": {
                "provider": "openai",
                "model_name": "gpt-4",
                "api_key": os.getenv("OPENAI_API_KEY"),
                "class": ChatOpenAI
            },
            "anthropic": {
                "provider": "anthropic", 
                "model_name": "claude-3-sonnet-20240229",
                "api_key": os.getenv("ANTHROPIC_API_KEY"),
                "class": ChatAnthropic
            },
            "google": {
                "provider": "google",
                "model_name": "gemini-pro",
                "api_key": os.getenv("GOOGLE_API_KEY"),
                "class": ChatGoogleGenerativeAI
            }
        }
    
    async def get_active_llm(self):
        """Get the currently active LLM instance"""
        # Try to get from database first
        config = await self.db_tool.get_active_llm_config()
        
        if not config:
            # Fall back to default (OpenAI)
            config = self.default_configs["openai"]
            if not config["api_key"]:
                # Try Anthropic as fallback
                config = self.default_configs["anthropic"]
                if not config["api_key"]:
                    # Try Google as final fallback
                    config = self.default_configs["google"]
        
        provider = config.get("provider", "openai")
        model_name = config.get("model_name")
        api_key = config.get("api_key")
        
        if not api_key:
            raise ValueError(f"No API key found for provider: {provider}")
        
        # Cache LLM instances
        cache_key = f"{provider}_{model_name}"
        if cache_key not in self.llm_cache:
            if provider == "openai":
                self.llm_cache[cache_key] = ChatOpenAI(
                    model=model_name,
                    api_key=api_key,
                    temperature=0.7
                )
            elif provider == "anthropic":
                self.llm_cache[cache_key] = ChatAnthropic(
                    model=model_name,
                    api_key=api_key,
                    temperature=0.7
                )
            elif provider == "google":
                self.llm_cache[cache_key] = ChatGoogleGenerativeAI(
                    model=model_name,
                    google_api_key=api_key,
                    temperature=0.7
                )
            else:
                raise ValueError(f"Unsupported LLM provider: {provider}")
        
        return self.llm_cache[cache_key]
    
    async def generate_response(self, messages: List[Dict[str, str]], 
                              system_prompt: Optional[str] = None) -> str:
        """Generate response using the active LLM"""
        try:
            llm = await self.get_active_llm()
            
            # Convert messages to LangChain format
            langchain_messages = []
            
            if system_prompt:
                langchain_messages.append(SystemMessage(content=system_prompt))
            
            for msg in messages:
                if msg.get("role") == "user":
                    langchain_messages.append(HumanMessage(content=msg["content"]))
            
            # Generate response
            response = await llm.ainvoke(langchain_messages)
            return response.content
            
        except Exception as e:
            # Fallback error handling
            return f"I apologize, but I'm experiencing technical difficulties. Error: {str(e)}"
    
    async def summarize_text(self, text: str, max_length: int = 200) -> str:
        """Summarize text using the active LLM"""
        system_prompt = f"""
        You are a helpful assistant that creates concise summaries.
        Summarize the following text in no more than {max_length} characters.
        Focus on the key points and main ideas.
        """
        
        messages = [{"role": "user", "content": text}]
        return await self.generate_response(messages, system_prompt)
    
    async def explain_concept(self, concept: str) -> str:
        """Explain a concept using the active LLM"""
        system_prompt = """
        You are a knowledgeable assistant that explains concepts clearly and concisely.
        Provide a helpful explanation that is easy to understand.
        """
        
        messages = [{"role": "user", "content": f"Please explain: {concept}"}]
        return await self.generate_response(messages, system_prompt)
    
    async def analyze_task_priority(self, task_title: str, task_description: str, 
                                   due_date: str = None) -> Dict[str, Any]:
        """Analyze task priority using LLM"""
        system_prompt = """
        You are a productivity expert. Analyze the given task and provide:
        1. Suggested priority level (low, medium, high)
        2. Estimated time to complete (in hours)
        3. Brief reasoning for the priority level
        
        Respond in JSON format:
        {
            "priority": "medium",
            "estimated_hours": 2,
            "reasoning": "explanation here"
        }
        """
        
        task_info = f"Title: {task_title}\nDescription: {task_description}"
        if due_date:
            task_info += f"\nDue Date: {due_date}"
        
        messages = [{"role": "user", "content": task_info}]
        response = await self.generate_response(messages, system_prompt)
        
        try:
            import json
            return json.loads(response)
        except:
            # Fallback if JSON parsing fails
            return {
                "priority": "medium",
                "estimated_hours": 1,
                "reasoning": "Unable to analyze automatically"
            }
    
    async def generate_proactive_suggestions(self, user_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate proactive suggestions based on user context"""
        system_prompt = """
        You are a proactive productivity assistant. Based on the user's current tasks, 
        calendar events, and context, generate helpful suggestions.
        
        Respond with a JSON array of suggestions:
        [
            {
                "type": "schedule_task",
                "title": "Schedule high-priority task",
                "description": "You have a free slot at 2 PM to work on your urgent project",
                "action_data": {"task_id": "123", "suggested_time": "2024-01-15T14:00:00"}
            }
        ]
        """
        
        context_str = f"""
        Current tasks: {user_context.get('tasks', [])}
        Upcoming events: {user_context.get('events', [])}
        Free time slots: {user_context.get('free_slots', [])}
        """
        
        messages = [{"role": "user", "content": context_str}]
        response = await self.generate_response(messages, system_prompt)
        
        try:
            import json
            return json.loads(response)
        except:
            return []
    
    async def switch_llm_provider(self, provider: str, model_name: str = None) -> bool:
        """Switch to a different LLM provider"""
        if provider not in self.default_configs:
            return False
        
        config = self.default_configs[provider].copy()
        if model_name:
            config["model_name"] = model_name
        
        # Clear cache to force reload
        self.llm_cache.clear()
        
        return True