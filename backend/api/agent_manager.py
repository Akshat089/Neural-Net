import logging
import uuid
from typing import Any, Dict, Optional
from langchain_core.messages import HumanMessage
# Import your agents
from blog.agent_blog_workflow import BlogWorkflowAgent
# from content.content_agent import ContentCreationAgent
# from news.news_agent import NewsroomAgent
# from multipurpose.multipurpose_agent import MultipurposeBot


class AgentManager:
    """Manages all AI agents and orchestrates their interactions."""

    def __init__(self):
        self.logger = logging.getLogger("AgentManager")
        self.agents = {}
        self._initialized = False

    async def initialize(self):
        """Compile and prepare all agents"""
        if self._initialized:
            self.logger.info("Agents already initialized.")
            return
        try:
            self.agents = {
                # "multipurpose": MultipurposeBot(),
                # "content": ContentCreationAgent(),
                "blog_workflow": BlogWorkflowAgent(),
                # "newsroom": NewsroomAgent(),
            }

            for name, agent in self.agents.items():
                self.logger.info(f"Compiling graph for '{name}' agent...")
                agent.compile()
                self.logger.info(f"'{name}' agent ready!")

            self._initialized = True
            self.logger.info("All agents initialized successfully!")
        except Exception as e:
            self.logger.error(f"Initialization failed: {str(e)}")
            raise

    def get_agent(self, agent_type: str):
        agent = self.agents.get(agent_type)
        if not agent:
            raise ValueError(f"Unknown agent type: {agent_type}")
        return agent

    async def process_message(
        self,
        message: str,
        agent_type: str = "multipurpose",
        thread_id: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Send message to the specified agent and get response."""
        agent = self.get_agent(agent_type)
        thread_id = thread_id or str(uuid.uuid4())
        self.logger.info(f"[Incoming] ({agent_type}) → {message}")

        input_data = {"messages": [HumanMessage(content=message)], **kwargs}
        result = await agent.ainvoke(input_data, thread_id=thread_id)

        self.logger.info("Agent finished processing.")
        return {"result": result, "thread_id": thread_id, "agent_type": agent_type}


# Global instance (importable anywhere)
agent_manager = AgentManager()
