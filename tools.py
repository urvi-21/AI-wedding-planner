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

    # Ensure values are valid (no negatives)
    for k in allocation:
        allocation[k] = max(allocation[k], 0)

    # Normalize (ensure total = 1.0)
    total = sum(allocation.values())
    allocation = {k: v / total for k, v in allocation.items()}

    result = {k: int(v * budget) for k, v in allocation.items()}
    return result


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
# LLM CALL
# ----------------------------
from utils import call_llm


# ----------------------------
# VENDOR GENERATION
# ----------------------------
def generate_vendors(city: str, budget: int):
    prompt = f"""
You are an expert Indian wedding planner.

Suggest EXACTLY 3 realistic wedding vendors in {city}.

STRICT RULES:
- Must include:
    1 Venue
    1 Catering
    1 Decor
- Use realistic Indian business-style names
- Stay within budget ₹{budget}
- DO NOT mention any other city
- DO NOT add extra vendors
- DO NOT write paragraphs

FORMAT EXACTLY:

VENUE:
Name:
Type:
Price Range:
Reason:

CATERING:
Name:
Type:
Price Range:
Reason:

DECOR:
Name:
Type:
Price Range:
Reason:
"""

    return call_llm(prompt).strip()


# ----------------------------
# PLAN REFINEMENT
# ----------------------------
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