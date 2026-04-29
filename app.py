import streamlit as st
import re
import requests
from utils import call_llm
import json

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
if "contacted" not in st.session_state:
    st.session_state.contacted = {}

def allocate_budget(total, priority="balanced"):
    allocation = {
        "venue": 0.4,
        "catering": 0.3,
        "decor": 0.15,
        "misc": 0.15
    }

    if priority == "decor":
        allocation["decor"] += 0.1
        allocation["venue"] -= 0.05
        allocation["misc"] -= 0.05

    elif priority == "food":
        allocation["catering"] += 0.1
        allocation["decor"] -= 0.05
        allocation["misc"] -= 0.05

    total_ratio = sum(allocation.values())

    return {
        k: int((v / total_ratio) * total)
        for k, v in allocation.items()
    }

# ----------------------------
# Custom CSS 🎀 (RESTORED)
# ----------------------------
st.markdown("""
<style>
h1, h2, h3, h4, h5, h6 {
    color: #2c2c2c !important;
}
p, span, div {
    color: #333333 !important;
}
button {
    color: white !important;
}
button[data-baseweb="tab"] {
    color: #333 !important;
}
label {
    color: #444 !important;
}
</style>
""", unsafe_allow_html=True)

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
.stTabs [role="tab"] {
    color: #880E4F !important;
    font-weight: 600;
    font-size: 16px;
}
.stTabs [aria-selected="true"] {
    color: #C2185B !important;
    border-bottom: 3px solid #C2185B !important;
}
.stTabs [role="tab"]:hover {
    color: #AD1457 !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
small, .stMarkdown, .stText {
    color: #333 !important;
}
input::placeholder {
    color: #777 !important;
}
.stSpinner {
    color: #333 !important;
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
user_email = st.text_input("📧 Enter your email for updates")

# ----------------------------
# Helpers
# ----------------------------
def clean_text(text):
    text = re.sub(r'\\boxed\{.*?\}', '', text)
    text = text.replace("\\", "")
    return text

# ----------------------------
# Generate Plan
# ----------------------------
if st.button("✨ Generate Plan"):

    if not user_input.strip():
        st.warning("Enter something first!")
    else:
        with st.spinner("Planning your dream wedding... 💖"):
            try:
                response = requests.post(
                    "https://onyx21.app.n8n.cloud/webhook/wedding_agent",
                    json={"message": user_input, "email": user_email}
                )

                if response.status_code != 200:
                    st.error("API Error")
                    st.write(response.text)
                    st.session_state.contacted = {}
                    st.stop()

                try:
                    try:
                        data = response.json()
                    except:
                        try:
                            data = json.loads(response.text)
                        except:
                            data = {"budget": 500000, "vendors": {}, "timeline": []}
                    city = data.get("city", "Unknown")
                except:
                    st.error("Invalid JSON response")
                    st.write(response.text)
                    st.stop()

                budget = data.get("budget", {})
                priority = data.get("priority", "balanced")
                budget = allocate_budget(budget, priority)

                vendors = data.get("vendors") or {}
                timeline = data.get("timeline") or [
                    "3 months before: Book venue",
                    "2 months before: Finalize vendors",
                    "1 month before: Send invitations",
                    "2 weeks before: Confirm bookings",
                    "1 week before: Final checks",
                    "Wedding day: Execute plan"
                ]

                st.subheader("💰 Budget")
                for k, v in budget.items():
                    st.write(f"{k.capitalize()}: ₹{v}")

                if isinstance(budget, dict) and "ERROR" in budget:
                    st.error("Failed to generate budget. Using fallback.")
                    st.write("₹500000")
                elif isinstance(budget, dict):
                    for k, v in budget.items():
                        st.write(f"{k.capitalize()}: ₹{v}")
                else:
                    st.write(f"₹{budget}")

                st.subheader("🏢 Vendors")

                for category, items in vendors.items():
                    st.markdown(f"### {category.capitalize()}")

                    for v in items:
                        vendor_name = v.get("name")

                        st.markdown(f"""
                        <div class='card'>
                        <b>{vendor_name}</b><br>
                        ⭐ Rating: {v.get("rating")}<br>
                        💰 Price: {v.get("price_range")}
                        </div>
                        """, unsafe_allow_html=True)

                        if st.session_state.contacted.get(vendor_name):
                            st.success("Contacted ✅")
                            if st.button(f"Contact Again {vendor_name}", key=f"retry_{vendor_name}"):

                                if not user_email:
                                    st.error("Please enter your email first")
                                    st.stop()

                                try:
                                    contact_response = requests.post(
                                        "https://onyx21.app.n8n.cloud/webhook/contact_vendor",
                                        json={
                                            "vendor_name": vendor_name,
                                            "city": city,
                                            "budget": budget,
                                            "user_email": user_email
                                        }
                                    )

                                    if contact_response.status_code == 200:
                                        st.success("Contacted Again ✅")
                                    else:
                                        st.error("Failed to contact vendor")

                                except Exception as e:
                                    st.error(str(e))

                        else:
                            if st.button(f"📞 Contact {vendor_name}", key=vendor_name):

                                if not user_email:
                                    st.error("Please enter your email first")
                                    st.stop()

                                try:
                                    contact_response = requests.post(
                                        "https://onyx21.app.n8n.cloud/webhook/contact_vendor",
                                        json={
                                            "vendor_name": vendor_name,
                                            "city": city,
                                            "budget": budget,
                                            "user_email": user_email
                                        }
                                    )

                                    if contact_response.status_code == 200:
                                        st.session_state.contacted[vendor_name] = True
                                        st.success("Contacted ✅")
                                    else:
                                        st.error("Failed to contact vendor")

                                except Exception as e:
                                    st.error(str(e))

                st.subheader("📅 Timeline")
                for t in timeline:
                    st.write("•", t)

                st.info("📩 You will receive updates on your email after contacting vendors.")

                full_plan = f"""
Budget:
{budget}

Vendors:
{vendors}

Timeline:
{timeline}
"""

                st.session_state.plan = clean_text(full_plan)
                st.session_state.sections = {
                    "budget": budget,
                    "vendors": vendors,
                    "timeline": timeline,
                    "city": city
                }

            except Exception as e:
                st.error(str(e))

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
""")

                st.session_state.plan = clean_text(refined)

            except Exception as e:
                st.error(str(e))

# ----------------------------
# Display Tabs
# ----------------------------
if st.session_state.plan:

    tab1, tab2, tab3, tab4 = st.tabs([
        "💰 Budget",
        "🏢 Vendors",
        "📅 Timeline",
        "📄 Full Plan"
    ])

    with tab1:
        st.markdown(f"<div class='card'>{st.session_state.sections.get('budget', {})}</div>", unsafe_allow_html=True)

    with tab2:
        vendors = st.session_state.sections.get("vendors", {}) or {}

        for category, items in vendors.items():
            st.markdown(f"**{category.capitalize()}**")

            for v in items:
                st.markdown(f"""
<div class='card'>
<b>{v.get("name")}</b><br>
⭐ Rating: {v.get("rating")}<br>
💰 Price: {v.get("price_range")}
</div>
""", unsafe_allow_html=True)

    with tab3:
        timeline_html = "<br>".join(st.session_state.sections.get("timeline", []))
        st.markdown(f"<div class='card'>{timeline_html}</div>", unsafe_allow_html=True)

    with tab4:
        st.markdown(f"<div class='card'>{st.session_state.plan}</div>", unsafe_allow_html=True)