"""
Tool for generating structured task plans from user requests
"""
from pydantic import BaseModel, Field
from langchain.tools import tool

from app.agents.plan_agent import PlanAgent


class GetPlanInput(BaseModel):
    """Input schema for the get_plan tool."""
    user_request: str = Field(
        description="The user's request or objective that needs to be broken down into a structured plan"
    )


@tool(args_schema=GetPlanInput)
def get_plan(user_request: str) -> dict:
    """Generate a structured task plan from a user request.

    This tool analyzes user requests and breaks them down into clear, actionable tasks.
    Each task is assigned to the most appropriate specialized agent.

    Use this tool when you need to:
    - Plan complex multi-step projects
    - Break down ambiguous requests into concrete tasks
    - Organize work across multiple specialized domains

    Args:
        user_request: The user's request or objective to plan

    Returns:
        dict: A dictionary containing a list of structured tasks with prompts and assigned agents
    """
    # Initialize the planning agent
    plan_agent = PlanAgent()

    # Generate the plan
    plan_output = plan_agent.run(user_request)

    # Return structured result
    return {
        "tasks": plan_output.tasks,
        "total_tasks": len(plan_output.tasks)
    }
