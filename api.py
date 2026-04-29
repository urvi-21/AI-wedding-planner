from fastapi import FastAPI
from pydantic import BaseModel
import re

from tools import allocate_budget, generate_vendors, generate_timeline

app = FastAPI()


class RequestData(BaseModel):
    message: str


def extract_basic_info(text):
    text = text.lower()

    city = "raipur" if "raipur" in text else "mumbai"

    import re
    budget_match = re.search(r'\d+', text)
    budget = int(budget_match.group()) if budget_match else 500000

    if "decor" in text:
        priority = "decor"
    elif "food" in text:
        priority = "food"
    else:
        priority = "balanced"

    return city.capitalize(), budget, priority


@app.post("/plan")
def generate_plan(data: RequestData):
    user_input = data.message.lower()

    # city
    if "mumbai" in user_input:
        city = "Mumbai"
    elif "raipur" in user_input:
        city = "Raipur"
    else:
        city = "Delhi"

    # budget
    match = re.search(r'\d+', user_input)
    budget = int(match.group()) if match else 500000

    # ✅ DEFINE VARIABLES PROPERLY
    budget_data = allocate_budget(budget, "balanced")
    vendors_data = generate_vendors(city, budget)
    timeline_data = generate_timeline()

    # ✅ RETURN CLEAN JSON
    return {
        "budget": budget_data,
        "vendors": vendors_data,
        "timeline": timeline_data
    }