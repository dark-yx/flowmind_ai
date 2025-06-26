"""
FlowMind AI - InfoFlow Agent (LangGraph Node)
"""
from typing import Dict, Any, List, Optional
from datetime import datetime

from models.state import FlowMindState, AgentResponse
from tools.llm_router import LLMRouter

class InfoFlowAgent:
    """
    InfoFlow - Agent responsible for information queries, explanations, and summaries
    """
    
    def __init__(self, llm_router: LLMRouter):
        self.llm_router = llm_router
        self.agent_name = "InfoFlow"
    
    async def process(self, state: FlowMindState) -> AgentResponse:
        """Main processing method for InfoFlow agent"""
        user_input = state.messages[-1].content if state.messages else ""
        user_id = state.user_id
        
        # Analyze the type of information request
        request_type = await self._analyze_request_type(user_input)
        
        if request_type == "explanation":
            response = await self._handle_explanation(user_input)
        elif request_type == "summarization":
            response = await self._handle_summarization(user_input)
        elif request_type == "definition":
            response = await self._handle_definition(user_input)
        elif request_type == "how_to":
            response = await self._handle_how_to(user_input)
        elif request_type == "comparison":
            response = await self._handle_comparison(user_input)
        elif request_type == "analysis":
            response = await self._handle_analysis(user_input)
        else:
            response = await self._handle_general_query(user_input)
        
        return AgentResponse(
            content=response,
            agent=self.agent_name,
            context={"request_type": request_type, "user_id": user_id}
        )
    
    async def _analyze_request_type(self, user_input: str) -> str:
        """Analyze the type of information request"""
        input_lower = user_input.lower()
        
        # Explanation patterns
        if any(phrase in input_lower for phrase in [
            "explain", "what is", "what are", "tell me about", "describe"
        ]):
            return "explanation"
        
        # Summarization patterns
        elif any(phrase in input_lower for phrase in [
            "summarize", "summary of", "sum up", "brief overview", "key points"
        ]):
            return "summarization"
        
        # Definition patterns
        elif any(phrase in input_lower for phrase in [
            "define", "definition of", "meaning of", "what does", "means"
        ]):
            return "definition"
        
        # How-to patterns
        elif any(phrase in input_lower for phrase in [
            "how to", "how do i", "how can i", "steps to", "guide to"
        ]):
            return "how_to"
        
        # Comparison patterns
        elif any(phrase in input_lower for phrase in [
            "compare", "difference between", "vs", "versus", "better than"
        ]):
            return "comparison"
        
        # Analysis patterns
        elif any(phrase in input_lower for phrase in [
            "analyze", "analysis of", "pros and cons", "advantages", "disadvantages"
        ]):
            return "analysis"
        
        else:
            return "general"
    
    async def _handle_explanation(self, user_input: str) -> str:
        """Handle explanation requests"""
        try:
            system_prompt = """
            You are InfoFlow, a knowledgeable assistant specializing in clear, comprehensive explanations.
            Provide detailed but accessible explanations that help users understand complex topics.
            Structure your response with:
            1. A clear, concise definition
            2. Key concepts or components
            3. Real-world examples or applications
            4. Why it matters or its significance
            
            Keep explanations informative but not overwhelming.
            """
            
            response = await self.llm_router.generate_response([
                {"role": "user", "content": user_input}
            ], system_prompt)
            
            return f"💡 **InfoFlow Explanation:**\n\n{response}"
            
        except Exception as e:
            return f"💡 I'd be happy to explain that for you, but I'm experiencing some technical difficulties. Error: {str(e)}"
    
    async def _handle_summarization(self, user_input: str) -> str:
        """Handle summarization requests"""
        try:
            system_prompt = """
            You are InfoFlow, an expert at creating concise, informative summaries.
            When asked to summarize:
            1. Extract the most important points
            2. Organize information logically
            3. Use bullet points or numbered lists when appropriate
            4. Maintain accuracy while being concise
            5. Highlight key takeaways
            
            If the user hasn't provided specific content to summarize, ask for clarification.
            """
            
            response = await self.llm_router.generate_response([
                {"role": "user", "content": user_input}
            ], system_prompt)
            
            return f"📋 **InfoFlow Summary:**\n\n{response}"
            
        except Exception as e:
            return f"📋 I'd be happy to summarize that for you, but I'm experiencing some technical difficulties. Error: {str(e)}"
    
    async def _handle_definition(self, user_input: str) -> str:
        """Handle definition requests"""
        try:
            system_prompt = """
            You are InfoFlow, a precise and helpful assistant for definitions.
            When providing definitions:
            1. Give a clear, accurate definition
            2. Include pronunciation if it's a complex term
            3. Provide context about when/where the term is used
            4. Give 1-2 simple examples
            5. Mention related terms if relevant
            
            Keep definitions clear and accessible.
            """
            
            response = await self.llm_router.generate_response([
                {"role": "user", "content": user_input}
            ], system_prompt)
            
            return f"📖 **InfoFlow Definition:**\n\n{response}"
            
        except Exception as e:
            return f"📖 I'd be happy to define that for you, but I'm experiencing some technical difficulties. Error: {str(e)}"
    
    async def _handle_how_to(self, user_input: str) -> str:
        """Handle how-to requests"""
        try:
            system_prompt = """
            You are InfoFlow, a helpful guide for step-by-step instructions.
            When providing how-to guidance:
            1. Break down the process into clear, numbered steps
            2. Include any prerequisites or materials needed
            3. Provide tips or warnings where appropriate
            4. Suggest alternatives if applicable
            5. End with next steps or related actions
            
            Make instructions practical and easy to follow.
            """
            
            response = await self.llm_router.generate_response([
                {"role": "user", "content": user_input}
            ], system_prompt)
            
            return f"🛠️ **InfoFlow Guide:**\n\n{response}"
            
        except Exception as e:
            return f"🛠️ I'd be happy to guide you through that process, but I'm experiencing some technical difficulties. Error: {str(e)}"
    
    async def _handle_comparison(self, user_input: str) -> str:
        """Handle comparison requests"""
        try:
            system_prompt = """
            You are InfoFlow, an analytical assistant specializing in comparisons.
            When comparing items:
            1. Create a clear structure (table, side-by-side, or categorized)
            2. Compare key attributes or criteria
            3. Highlight main similarities and differences
            4. Provide context about when each option might be better
            5. Give a balanced perspective
            
            Be objective and help users make informed decisions.
            """
            
            response = await self.llm_router.generate_response([
                {"role": "user", "content": user_input}
            ], system_prompt)
            
            return f"⚖️ **InfoFlow Comparison:**\n\n{response}"
            
        except Exception as e:
            return f"⚖️ I'd be happy to compare those options for you, but I'm experiencing some technical difficulties. Error: {str(e)}"
    
    async def _handle_analysis(self, user_input: str) -> str:
        """Handle analysis requests"""
        try:
            system_prompt = """
            You are InfoFlow, an analytical assistant providing thorough analysis.
            When analyzing topics:
            1. Break down the subject into key components
            2. Examine pros and cons objectively
            3. Consider different perspectives or stakeholders
            4. Identify patterns, trends, or implications
            5. Provide actionable insights or recommendations
            
            Be thorough but organized in your analysis.
            """
            
            response = await self.llm_router.generate_response([
                {"role": "user", "content": user_input}
            ], system_prompt)
            
            return f"🔍 **InfoFlow Analysis:**\n\n{response}"
            
        except Exception as e:
            return f"🔍 I'd be happy to analyze that for you, but I'm experiencing some technical difficulties. Error: {str(e)}"
    
    async def _handle_general_query(self, user_input: str) -> str:
        """Handle general information queries"""
        try:
            system_prompt = """
            You are InfoFlow, a knowledgeable and helpful information assistant.
            Provide accurate, helpful information on a wide range of topics.
            
            Guidelines:
            1. Be informative and accurate
            2. Structure your response clearly
            3. Provide context when needed
            4. Suggest follow-up questions if appropriate
            5. Admit if you're unsure about something
            
            Always aim to be helpful and educational.
            """
            
            response = await self.llm_router.generate_response([
                {"role": "user", "content": user_input}
            ], system_prompt)
            
            return f"🧠 **InfoFlow:**\n\n{response}"
            
        except Exception as e:
            return f"🧠 I'm here to help with information and explanations! I can explain concepts, provide definitions, summarize content, give how-to guides, make comparisons, and analyze topics. What would you like to know? Error: {str(e)}"
    
    async def generate_productivity_insights(self, user_context: Dict[str, Any]) -> str:
        """Generate productivity insights based on user data"""
        try:
            system_prompt = """
            You are InfoFlow, providing productivity insights and analysis.
            Based on the user's task and calendar data, provide:
            1. Productivity patterns you notice
            2. Potential areas for improvement
            3. Suggestions for better time management
            4. Insights about work-life balance
            
            Be encouraging and constructive in your analysis.
            """
            
            context_str = f"""
            User productivity data:
            - Total tasks: {user_context.get('total_tasks', 0)}
            - Completed tasks: {user_context.get('completed_tasks', 0)}
            - Pending tasks: {user_context.get('pending_tasks', 0)}
            - Calendar events: {user_context.get('events', 0)}
            - High priority tasks: {user_context.get('high_priority_tasks', 0)}
            
            Recent task titles: {', '.join(user_context.get('recent_tasks', [])[:5])}
            """
            
            response = await self.llm_router.generate_response([
                {"role": "user", "content": context_str}
            ], system_prompt)
            
            return f"📊 **Productivity Insights:**\n\n{response}"
            
        except Exception as e:
            return f"📊 I'd like to provide productivity insights, but I'm experiencing technical difficulties. Error: {str(e)}"
    
    async def explain_productivity_concept(self, concept: str) -> str:
        """Explain productivity-related concepts"""
        try:
            system_prompt = """
            You are InfoFlow, specializing in productivity and time management concepts.
            Explain productivity concepts in a practical, actionable way:
            1. Clear definition
            2. Why it's important for productivity
            3. How to implement or apply it
            4. Common mistakes to avoid
            5. Real-world examples
            
            Make it relevant to personal productivity and task management.
            """
            
            response = await self.llm_router.generate_response([
                {"role": "user", "content": f"Explain the productivity concept: {concept}"}
            ], system_prompt)
            
            return f"⚡ **Productivity Concept:**\n\n{response}"
            
        except Exception as e:
            return f"⚡ I'd be happy to explain that productivity concept, but I'm experiencing technical difficulties. Error: {str(e)}"