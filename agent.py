import os
from typing import Optional, List

from langchain.agents import initialize_agent, Tool
from langchain.agents.agent_types import AgentType
from langchain.llms.base import LLM

from tools import allocate_budget, generate_vendors, generate_timeline
from utils import call_llm


# -------------------------------
# Wrapper functions (TOOLS)
# -------------------------------

def budget_tool(input_text):
    import re

    # Extract budget
    budget_match = re.search(r'\d+', input_text)
    budget = int(budget_match.group()) if budget_match else 1000000

    # Detect priority
    if "decor" in input_text.lower():
        priority = "decor"
    elif "food" in input_text.lower():
        priority = "food"
    else:
        priority = "balanced"

    return str(allocate_budget(budget, priority))


def vendor_tool(input_text):
    import re

    # Extract city
    words = input_text.split()
    city = words[-1] if len(words) > 0 else "Mumbai"

    # Extract budget
    budget_match = re.search(r'\d+', input_text)
    budget = int(budget_match.group()) if budget_match else 1000000

    return generate_vendors(city, budget)


def timeline_tool(input_text):
    return str(generate_timeline())


# -------------------------------
# Tool definitions
# -------------------------------

tools = [
    Tool(
        name="Budget Planner",
        func=budget_tool,
        description="Use this FIRST to allocate wedding budget"
    ),
    Tool(
        name="Vendor Finder",
        func=vendor_tool,
        description="Use this AFTER budget to suggest vendors"
    ),
    Tool(
        name="Timeline Generator",
        func=timeline_tool,
        description="Use this LAST to create timeline"
    ),
]


# -------------------------------
# Custom LLM (IMPORTANT FIX)
# -------------------------------

class CustomLLM(LLM):
    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        return call_llm(prompt)

    @property
    def _llm_type(self) -> str:
        return "custom_openrouter"


llm = CustomLLM()


# -------------------------------
# Agent initialization
# -------------------------------

agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=False,
    handle_parsing_errors=True,
    max_iterations=4  
)