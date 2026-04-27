import re
from typing import Optional, List

from langchain.tools import Tool
from langchain.agents import create_react_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate
from langchain.llms.base import LLM

from tools import allocate_budget, generate_vendors, generate_timeline
from utils import call_llm


# -------------------------------
# Wrapper functions (TOOLS)
# -------------------------------

def extract_budget(text):
    match = re.search(r'\d+', text)
    return int(match.group()) if match else 1000000


def extract_city(text):
    cities = ["mumbai", "delhi", "jaipur", "raipur", "goa", "bangalore", "pune"]
    text_lower = text.lower()
    for c in cities:
        if c in text_lower:
            return c.capitalize()
    return "Mumbai"


def extract_priority(text):
    text = text.lower()
    if "decor" in text:
        return "decor"
    elif "food" in text:
        return "food"
    return "balanced"


# -------------------------------
# Tools
# -------------------------------

def budget_tool(input_text: str):
    budget = extract_budget(input_text)
    priority = extract_priority(input_text)
    return str(allocate_budget(budget, priority))


def vendor_tool(input_text: str):
    city = extract_city(input_text)
    budget = extract_budget(input_text)
    return generate_vendors(city, budget)


def timeline_tool(input_text: str):
    return "\n".join(generate_timeline())


tools = [
    Tool(
        name="Budget Planner",
        func=budget_tool,
        description="Allocates wedding budget. Input: user request text"
    ),
    Tool(
        name="Vendor Finder",
        func=vendor_tool,
        description="Finds vendors based on city and budget"
    ),
    Tool(
        name="Timeline Generator",
        func=timeline_tool,
        description="Generates wedding timeline"
    ),
]


# -------------------------------
# Custom LLM
# -------------------------------

class CustomLLM(LLM):
    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        return call_llm(prompt)

    @property
    def _llm_type(self) -> str:
        return "custom_llm"


llm = CustomLLM()


# -------------------------------
# Prompt (VERY IMPORTANT)
# -------------------------------

from langchain_core.prompts import PromptTemplate

prompt = PromptTemplate.from_template("""
You are an AI Wedding Planner.

You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: think about what to do
Action: one of [{tool_names}]
Action Input: input to the action
Observation: result of the action
... (repeat Thought/Action/Observation as needed)

Thought: I now have the final answer
Final Answer:

💰 Budget:
<budget output>

🏢 Vendors:
<vendors output>

📅 Timeline:
<timeline output>

Begin!

Question: {input}
{agent_scratchpad}
""")


# -------------------------------
# Agent
# -------------------------------

agent = create_react_agent(
    llm=llm,
    tools=tools,
    prompt=prompt
)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=False,
    handle_parsing_errors=True,
    max_iterations=4
)