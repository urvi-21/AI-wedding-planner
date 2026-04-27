#budget_allocate
def allocate_budget(budget: int, priority: str):
    allocation = {
        "venue": 0.4,
        "catering": 0.3,
        "decor": 0.15,
        "misc": 0.15
    }

    if priority.lower() == "decor":
        allocation["decor"] += 0.1
        allocation["venue"] -= 0.05
        allocation["misc"] -= 0.05

    elif priority.lower() == "food":
        allocation["catering"] += 0.1
        allocation["decor"] -= 0.05
        allocation["misc"] -= 0.05

    result = {k: int(v * budget) for k, v in allocation.items()}
    return result

#timeline_create
def generate_timeline():
    return [
        "3 months before: Book venue",
        "2 months before: Finalize vendors",
        "1 month before: Send invitations",
        "2 weeks before: Confirm bookings",
        "1 week before: Final checks",
        "Wedding day: Execute plan"
    ]

from utils import call_llm

def generate_vendors(city: str, budget: int):
    prompt = f"""
    You are a professional wedding planner.

    Suggest 3 realistic wedding vendors in {city} within a total wedding budget of ₹{budget}.

    Return STRICT structured format:

    1. Name:
       Type:
       Price Range:
       Reason:

    2. Name:
       Type:
       Price Range:
       Reason:

    3. Name:
       Type:
       Price Range:
       Reason:
    """

    return call_llm(prompt)

def refine_plan(current_plan: str, feedback: str):
    prompt = f"""
    You are a wedding planning assistant.

    Improve the following wedding plan based on user feedback.

    CURRENT PLAN:
    {current_plan}

    USER FEEDBACK:
    {feedback}

    Return improved structured plan.
    """

    return call_llm(prompt)

