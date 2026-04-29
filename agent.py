import re
import json
from typing import Optional, List

from langchain.tools import Tool
from langchain.agents import create_react_agent, AgentExecutor
from langchain_core.prompts import PromptTemplate
from langchain.llms.base import LLM

from tools import allocate_budget, generate_vendors, generate_timeline
from utils import call_llm


# -------------------------------
# INPUT EXTRACTION (STRONGER)
# -------------------------------

def extract_budget(text):
    match = re.search(r'(\d+)\s*(lakh|lac|l)?', text.lower())
    if match:
        num = int(match.group(1))
        if match.group(2):
            return num * 100000
        return num
    return 500000


def extract_city(text):
    cities = ["mumbai", "delhi", "jaipur", "raipur", "goa", "bangalore", "pune"]
    text_lower = text.lower()
    for c in cities:
        if c in text_lower:
            return c.capitalize()
    return "Delhi"


def extract_priority(text):
    text = text.lower()
    if "decor" in text:
        return "decor"
    elif "food" in text or "catering" in text:
        return "food"
    return "balanced"


# -------------------------------
# TOOLS (STRICT OUTPUT)
# -------------------------------

def budget_tool(input_text: str):
    budget = extract_budget(input_text)
    priority = extract_priority(input_text)

    result = allocate_budget(budget, priority)

    return json.dumps({
        "total_budget": budget,
        "allocation": result
    })


def vendor_tool(input_text: str):
    city = extract_city(input_text)
    budget = extract_budget(input_text)

    vendors = generate_vendors(city, budget)

    return json.dumps({
        "city": city,
        "vendors": vendors
    })


def timeline_tool(input_text: str):
    timeline = generate_timeline()

    return json.dumps({
        "timeline": timeline
    })


tools = [
    Tool(
        name="BudgetPlanner",
        func=budget_tool,
        description="Returns budget allocation in JSON"
    ),
    Tool(
        name="VendorFinder",
        func=vendor_tool,
        description="Returns top vendors (venue, catering, decor)"
    ),
    Tool(
        name="TimelineGenerator",
        func=timeline_tool,
        description="Returns wedding timeline"
    ),
]


# -------------------------------
# CUSTOM LLM (Groq wrapper)
# -------------------------------

class CustomLLM(LLM):
    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        return call_llm(prompt)

    @property
    def _llm_type(self) -> str:
        return "custom_llm"


llm = CustomLLM()


# -------------------------------
# STRONG PROMPT (CRITICAL)
# -------------------------------

prompt = PromptTemplate.from_template("""
You are an AI Wedding Operations Agent.

STRICT RULES:
- You MUST use ALL tools:
    1. BudgetPlanner
    2. VendorFinder
    3. TimelineGenerator
- DO NOT skip tools
- DO NOT hallucinate vendors
- DO NOT create your own data
- Always rely on tool outputs

WORKFLOW:
1. Extract user intent
2. Call BudgetPlanner
3. Call VendorFinder
4. Call TimelineGenerator
5. Combine results

OUTPUT FORMAT (STRICT JSON):

{{
  "budget": <budget_output>,
  "vendors": <vendor_output>,
  "timeline": <timeline_output>
}}

TOOLS:
{tools}

FORMAT:

Question: {input}
{agent_scratchpad}
""")


# -------------------------------
# AGENT
# -------------------------------

agent = create_react_agent(
    llm=llm,
    tools=tools,
    prompt=prompt
)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,   # turn ON for debugging
    handle_parsing_errors=True,
    max_iterations=5
)