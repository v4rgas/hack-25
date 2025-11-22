"""
Simple Agent - Basic conversational agent using LangChain v1 API
"""
from typing import Dict, Any, List

from pydantic import BaseModel, Field
from langchain_anthropic import ChatAnthropic
from langchain.agents import create_agent
from langchain.agents.structured_output import ProviderStrategy

from app.prompts import simple_agent


class AnomalyOutput(BaseModel):
    """Structured output for anomaly detection in procurement analysis"""
    anomalies: List[str] = Field(
        description="List of detected anomalies or red flags in the procurement process"
    )


class SimpleAgent:
    """
    A simple conversational agent using LangChain v1's create_agent API.

    This agent provides basic question-answering and task execution without
    structured outputs or complex tool usage.

    Usage:
        agent = SimpleAgent()
        response = agent.run("What is FastAPI?")
        print(response)  # "FastAPI is a modern Python web framework..."
    """

    def __init__(
        self,
        model_name: str = "claude-sonnet-4-5",
        temperature: float = 0.7,
    ):
        """
        Initialize the Simple Agent using LangChain v1 create_agent API.

        Args:
            model_name: Anthropic model to use
            temperature: Temperature for model responses (0.0-1.0)
            system_prompt: Optional custom system prompt. If None, uses default.
        """
        self.model_name = model_name
        self.temperature = temperature

        # Initialize model
        model = ChatAnthropic(
            model_name=model_name,
            temperature=temperature,
        )

        # Create simple agent with structured output for anomaly detection
        self.agent = create_agent(
            model=model,
            tools=[],  # No tools for simple agent
            system_prompt=simple_agent.SYS_PROMPT,
            response_format=ProviderStrategy(AnomalyOutput)
        )

    def run(self, message: str) -> AnomalyOutput:
        """
        Process a user message and return detected anomalies.

        Args:
            message: The user's question or request

        Returns:
            AnomalyOutput: Structured output with list of detected anomalies

        Example:
            >>> agent = SimpleAgent()
            >>> response = agent.run("Analyze tender with single bidder and 3-day publication")
            >>> print(response.anomalies)
            ['Single bidder detected', 'Publication period too short (3 days)']
        """
        result = self.agent.invoke({
            "messages": [{"role": "user", "content": message}]
        })

        # Return the structured response
        return result["structured_response"]

    def _extract_response(self, result: Dict[str, Any]) -> str:
        """
        Extract the text response from the agent's result.

        Args:
            result: The raw result from agent.invoke()

        Returns:
            str: The extracted text response
        """
        # The response is in the "messages" list, get the last AI message
        if "messages" in result:
            messages = result["messages"]
            if messages:
                # Get the last message content
                last_message = messages[-1]
                if hasattr(last_message, "content"):
                    return last_message.content
                elif isinstance(last_message, dict) and "content" in last_message:
                    return last_message["content"]

        # Fallback: try to convert result to string
        return str(result)
