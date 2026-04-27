import streamlit as st
from agent import agent
from tools import allocate_budget, generate_vendors, generate_timeline
import re
from utils import call_llm

# ----------------------------
# Page Config
# ----------------------------
st.set_page_config(
    page_title="AI Wedding Planner",
    page_icon="💍",
    layout="centered"
)

# ----------------------------
# Session State
# ----------------------------
if "plan" not in st.session_state:
    st.session_state.plan = ""
if "sections" not in st.session_state:
    st.session_state.sections = {}

# ----------------------------
# Custom CSS 🎀
# ----------------------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #fff0f5, #ffe4ec);
}

h1 {
    color: #880E4F !important;
    text-align: center;
    font-family: 'Georgia', serif;
    font-size: 42px;
    font-weight: bold;
}

.subtitle {
    text-align: center;
    color: #AD1457 !important;
    font-size: 18px;
    margin-bottom: 20px;
}

h2, h3 {
    color: #880E4F !important;
    font-weight: bold;
}

label {
    color: #6A1B4D !important;
}

.stButton>button {
    background: linear-gradient(90deg, #E75480, #C2185B);
    color: white;
    border-radius: 12px;
    font-size: 16px;
    padding: 10px 24px;
}

.card {
    background: white;
    padding: 20px;
    border-radius: 12px;
    margin-top: 15px;
    color: black;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.08);
}

/* 🔥 FIX TAB TEXT VISIBILITY */
.stTabs [role="tab"] {
    color: #880E4F !important;
    font-weight: 600;
    font-size: 16px;
}

/* Active tab */
.stTabs [aria-selected="true"] {
    color: #C2185B !important;
    border-bottom: 3px solid #C2185B !important;
}

/* Hover effect */
.stTabs [role="tab"]:hover {
    color: #AD1457 !important;
}
</style>
""", unsafe_allow_html=True)

# ----------------------------
# Header
# ----------------------------
st.markdown("<h1>💍 AI Wedding Planner</h1>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>✨ Plan your dream Indian wedding ✨</div>", unsafe_allow_html=True)

# ----------------------------
# Input
# ----------------------------
user_input = st.text_input(
    "Describe your wedding",
    placeholder="e.g. Wedding in Mumbai under 8L with decor focus"
)

# ----------------------------
# Helpers
# ----------------------------
def clean_text(text):
    text = re.sub(r'\\boxed\{.*?\}', '', text)
    text = text.replace("\\", "")
    return text


def format_vendors(text):
    text = text.replace("VENUE:", "<h3>🏛️ Venue</h3>")
    text = text.replace("CATERING:", "<h3>🍽️ Catering</h3>")
    text = text.replace("DECOR:", "<h3>🎀 Decor</h3>")
    text = text.replace("Name:", "<b>Name:</b>")
    text = text.replace("Price Range:", "<b>Price:</b>")
    text = text.replace("Reason:", "<b>Why:</b>")
    text = text.replace("\n", "<br>")
    return text


def format_budget(budget_dict):
    return "<br>".join([
        f"💸 <b>{k.capitalize()}</b>: ₹{v:,}"
        for k, v in budget_dict.items()
    ])


def parse_user_input(text):
    text = text.lower()

    # budget
    budget_match = re.search(r'\d+', text)
    budget = int(budget_match.group()) if budget_match else 800000

    # city
    cities = ["mumbai", "delhi", "jaipur", "raipur", "goa", "bangalore", "pune"]
    city = "Mumbai"
    for c in cities:
        if c in text:
            city = c.capitalize()

    # preference
    if "decor" in text:
        preference = "decor"
    elif "food" in text:
        preference = "food"
    elif "luxury" in text:
        preference = "luxury"
    else:
        preference = "balanced"

    return city, budget, preference


# ----------------------------
# Generate Plan
# ----------------------------
if st.button("✨ Generate Plan"):

    if not user_input.strip():
        st.warning("Enter something first!")
    else:
        with st.spinner("Planning your dream wedding... 💖"):
            try:
                city, budget_val, preference = parse_user_input(user_input)

                budget = allocate_budget(budget_val, preference)
                vendors = generate_vendors(city, budget_val)
                timeline = generate_timeline()

                full_plan = f"""
💰 Budget:
{format_budget(budget)}

<br><br>

🏢 Vendors:
{format_vendors(vendors)}

<br><br>

📅 Timeline:
{"<br>".join(timeline)}
"""

                full_plan = clean_text(full_plan)

                st.session_state.plan = full_plan
                st.session_state.sections = {
                    "budget": budget,
                    "vendors": vendors,
                    "timeline": timeline
                }

            except Exception as e:
                st.error(str(e))


# ----------------------------
# Display
# ----------------------------
if st.session_state.plan:

    tab1, tab2, tab3, tab4 = st.tabs([
        "💰 Budget",
        "🏢 Vendors",
        "📅 Timeline",
        "📄 Full Plan"
    ])

    with tab1:
        budget_data = st.session_state.sections.get("budget", {})
        st.markdown(
            f"<div class='card'>{format_budget(budget_data)}</div>",
            unsafe_allow_html=True
        )

    with tab2:
        st.markdown("### 🏢 Recommended Vendors")
        vendors_html = format_vendors(st.session_state.sections.get("vendors", ""))
        st.markdown(
            f"<div class='card'>{vendors_html}</div>",
            unsafe_allow_html=True
        )

    with tab3:
        st.markdown("### 📅 Wedding Timeline")
        timeline_html = "<br>".join(st.session_state.sections.get("timeline", []))
        st.markdown(
            f"<div class='card'>{timeline_html}</div>",
            unsafe_allow_html=True
        )

    with tab4:
        st.markdown(
            f"<div class='card'>{st.session_state.plan}</div>",
            unsafe_allow_html=True
        )


# ----------------------------
# Refinement
# ----------------------------
st.divider()
st.subheader("💬 Refine Your Plan")

refine_input = st.text_input(
    "Modify your plan",
    placeholder="e.g. reduce budget, more luxury decor"
)

if st.button("Update Plan"):

    if not st.session_state.plan:
        st.warning("Generate a plan first!")
    else:
        with st.spinner("Refining your plan... ✨"):
            try:
                refined = call_llm(f"""
You are a wedding planner.

Modify the following plan based on user request.

PLAN:
{st.session_state.plan}

USER REQUEST:
{refine_input}

Return updated plan in same format:
1. Budget
2. Vendors
3. Timeline

Keep it clean and structured.
""")

                st.session_state.plan = clean_text(refined)

            except Exception as e:
                st.error(str(e))