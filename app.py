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
# Custom CSS 🎀 (FINAL FIXED)
# ----------------------------
st.markdown("""
<style>

/* Background */
.stApp {
    background: linear-gradient(135deg, #fff0f5, #ffe4ec);
}

/* MAIN TITLE */
h1 {
    color: #880E4F !important;
    text-align: center;
    font-family: 'Georgia', serif;
    font-size: 42px;
    font-weight: bold;
}

/* SUBTITLE */
.subtitle {
    text-align: center;
    color: #AD1457 !important;
    font-size: 18px;
    margin-bottom: 20px;
}

/* ALL HEADINGS */
h2, h3 {
    color: #880E4F !important;
    font-weight: bold;
}

/* Labels */
label {
    color: #6A1B4D !important;
}

/* Buttons */
.stButton>button {
    background: linear-gradient(90deg, #E75480, #C2185B);
    color: white;
    border-radius: 12px;
    font-size: 16px;
    padding: 10px 24px;
}

/* Cards */
.card {
    background: white;
    padding: 20px;
    border-radius: 12px;
    margin-top: 15px;
    color: black;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.08);
}

/* 🔥 FIX SPINNER TEXT */
.stSpinner > div {
    color: #880E4F !important;
    font-weight: 500;
}

/* 🔥 FIX TAB TEXT COLORS */
button[data-baseweb="tab"] {
    color: #6A1B4D !important;   /* normal tabs */
    font-weight: 600;
}

/* ACTIVE TAB */
button[aria-selected="true"] {
    color: #C2185B !important;
    border-bottom: 3px solid #C2185B !important;
}

/* HOVER EFFECT */
button[data-baseweb="tab"]:hover {
    color: #880E4F !important;
}

/* Extra fallback */
[data-testid="stStatusWidget"] {
    color: #880E4F !important;
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
# CLEAN OUTPUT
# ----------------------------
def clean_text(text):
    text = re.sub(r'\\boxed\{.*?\}', '', text)
    text = text.replace("\\", "")
    return text

# ----------------------------
# GENERATE PLAN
# ----------------------------
if st.button("✨ Generate Plan"):

    if not user_input.strip():
        st.warning("Enter something first!")
    else:
        st.toast("💖 Creating your dream wedding...")

        with st.spinner("Planning in progress..."):
            try:
                budget = allocate_budget(800000, "decor")
                vendors = generate_vendors("Mumbai", 800000)
                timeline = generate_timeline()

                full_plan = f"""
💰 Budget:
{budget}

🏢 Vendors:
{vendors}

📅 Timeline:
{timeline}
"""

                full_plan = clean_text(str(full_plan))

                st.session_state.plan = full_plan
                st.session_state.sections = {
                    "budget": str(budget),
                    "vendors": str(vendors),
                    "timeline": str(timeline)
                }

            except Exception as e:
                st.error(str(e))

# ----------------------------
# DISPLAY PLAN
# ----------------------------
if st.session_state.plan:

    tab1, tab2, tab3, tab4 = st.tabs([
        "💰 Budget",
        "🏢 Vendors",
        "📅 Timeline",
        "📄 Full Plan"
    ])

    with tab1:
        st.markdown(f"<div class='card'>{st.session_state.sections.get('budget','')}</div>", unsafe_allow_html=True)

    with tab2:
        st.markdown(f"<div class='card'>{st.session_state.sections.get('vendors','')}</div>", unsafe_allow_html=True)

    with tab3:
        st.markdown(f"<div class='card'>{st.session_state.sections.get('timeline','')}</div>", unsafe_allow_html=True)

    with tab4:
        st.markdown(f"<div class='card'>{st.session_state.plan}</div>", unsafe_allow_html=True)

# ----------------------------
# 💬 REFINEMENT CHAT
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
        st.toast("✨ Updating your plan...")

        with st.spinner("Refining your plan..."):
            try:
                refined = call_llm(
                    f"""
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

                Keep it clean and concise. Do NOT use symbols like \\boxed.
               """
                )

                st.session_state.plan = clean_text(str(refined))

            except Exception as e:
                st.error(str(e))