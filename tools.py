import json
import math
import os

# ----------------------------
# LOAD VENDOR DATABASE
# ----------------------------
DATA_PATH = os.path.join("data", "vendors.json")

def load_vendors():
    if not os.path.exists(DATA_PATH):
        return []
    with open(DATA_PATH, "r") as f:
        return json.load(f)


# ----------------------------
# BUDGET ALLOCATION
# ----------------------------
def allocate_budget(budget: int, priority: str):
    allocation = {
        "venue": 0.4,
        "catering": 0.3,
        "decor": 0.15,
        "misc": 0.15
    }

    priority = priority.lower()

    if priority == "decor":
        allocation["decor"] += 0.1
        allocation["venue"] -= 0.05
        allocation["misc"] -= 0.05

    elif priority == "food":
        allocation["catering"] += 0.1
        allocation["decor"] -= 0.05
        allocation["misc"] -= 0.05

    # prevent negatives
    for k in allocation:
        allocation[k] = max(allocation[k], 0)

    # normalize
    total = sum(allocation.values())
    allocation = {k: v / total for k, v in allocation.items()}

    return {k: int(v * budget) for k, v in allocation.items()}


# ----------------------------
# TIMELINE
# ----------------------------
def generate_timeline():
    return [
        "3 months before: Book venue",
        "2 months before: Finalize vendors",
        "1 month before: Send invitations",
        "2 weeks before: Confirm bookings",
        "1 week before: Final checks",
        "Wedding day: Execute plan"
    ]


# ----------------------------
# SCORING FUNCTION
# ----------------------------
def score_vendor(v, usable_budget):
    rating = float(v.get("rating", 0))
    reviews = float(v.get("reviews", 0))
    min_price = float(v.get("price_min", 0))
    max_price = float(v.get("price_max", 0))

    mid_price = (min_price + max_price) / 2 if max_price else min_price or 1

    # price fit
    price_fit = 1 - abs(usable_budget - mid_price) / mid_price
    price_fit = max(0, min(1, price_fit))

    return (
        rating * 0.5 +
        math.log(reviews + 1) * 0.3 +
        price_fit * 0.2
    )


# ----------------------------
# FILTER + RANK VENDORS
# ----------------------------
def get_top_vendors(city, category, total_budget):
    vendors = load_vendors()

    city = city.lower()
    category = category.lower()

    # budget split
    if category == "venue":
        usable_budget = total_budget * 0.4
    elif category == "catering":
        usable_budget = total_budget * 0.3
    elif category == "decor":
        usable_budget = total_budget * 0.15
    else:
        usable_budget = total_budget

    # filter
    filtered = [
        v for v in vendors
        if v.get("city", "").lower() == city
        and v.get("category", "").lower() == category
    ]

    if not filtered:
        return []

    # sort by score
    ranked = sorted(
        filtered,
        key=lambda v: score_vendor(v, usable_budget),
        reverse=True
    )

    # top 3
    top = ranked[:3]

    # format
    result = []
    for v in top:
        min_p = v.get("price_min", 0)
        max_p = v.get("price_max", 0)

        result.append({
            "name": v.get("name"),
            "rating": v.get("rating"),
            "price_range": f"₹{round(min_p/100000)}L - ₹{round(max_p/100000)}L"
        })

    return result


# ----------------------------
# MAIN VENDOR ENGINE
# ----------------------------
def generate_vendors(city: str, budget: int):
    return {
        "venue": get_top_vendors(city, "venue", budget),
        "catering": get_top_vendors(city, "catering", budget),
        "decor": get_top_vendors(city, "decor", budget),
    }


# ----------------------------
# PLAN REFINEMENT (LLM stays)
# ----------------------------
from utils import call_llm

def refine_plan(current_plan: str, feedback: str):
    prompt = f"""
You are a professional wedding planner.

Modify the plan based on feedback.

STRICT RULES:
- Keep same city
- Keep structure:
    💰 Budget
    🏢 Vendors
    📅 Timeline
- Only improve based on feedback
- Do NOT remove sections

CURRENT PLAN:
{current_plan}

USER FEEDBACK:
{feedback}

Return updated structured plan.
"""
    return call_llm(prompt).strip()