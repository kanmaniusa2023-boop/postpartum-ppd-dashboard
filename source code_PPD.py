from __future__ import print_function
import os.path
import base64
import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import streamlit as st

# ---------------------------------------------------------
# LOGIN SETTINGS
# ---------------------------------------------------------

USERNAME = "clinicalnurse01"
PASSWORD = "saintlouis"
MAX_ATTEMPTS = 3

# Initialize session states
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "attempts_left" not in st.session_state:
    st.session_state.attempts_left = MAX_ATTEMPTS
if "account_locked" not in st.session_state:
    st.session_state.account_locked = False
if "show_logout_page" not in st.session_state:
    st.session_state.show_logout_page = False
# ======================================================
#  PERFECT HTML RENDERING USING st.html()  (NO ESCAPING)
# ======================================================
import streamlit.components.v1 as components

if st.session_state.show_logout_page:

    html_code = """
    <div style="
        width:100%;
        padding:60px 20px;
        text-align:center;
        background:#ffe4f0;
        border-radius:12px;
        ">
        
        <h1 style="
            color:#D61C74;
            font-size:42px;
            font-weight:900;
            margin-bottom:10px;">
            📤 Logout Successful
        </h1>

        <p style="
            font-size:20px;
            color:#444;
            margin-top:10px;">
            You have been logged out successfully.<br>
            Thank you for visiting — please log in again anytime.
        </p>

        <a href="/" style="
            display:inline-block;
            margin-top:30px;
            background:#D61C74;
            padding:14px 32px;
            color:white;
            border-radius:10px;
            text-decoration:none;
            font-size:20px;
            font-weight:700;
            box-shadow:0px 4px 10px rgba(0,0,0,0.15);
        ">
            🔐 Login Again
        </a>
    </div>
    """

    components.html(html_code, height=400)
    st.stop()
# ---------------------------------------------------------
# LOCKED ACCOUNT SCREEN
# ---------------------------------------------------------
if st.session_state.account_locked:
    st.markdown("""
        <h2 style='color:#D61C74; text-align:center;'>🔐 Account Locked</h2>
        <p style='text-align:center; font-size:17px;'>
            Your account has been locked due to too many failed login attempts.<br>
            Please email the admin team at:<br><br>
            <b style='color:#D61C74;'>ppdwellbeings@gmail.com</b><br><br>
            For emergencies, please visit the hospital's support desk.
        </p>
    """, unsafe_allow_html=True)
    st.stop()

# ---------------------------------------------------------
# BEAUTIFUL CUSTOM LOGIN SCREEN (Final Version With Working Image)
# ---------------------------------------------------------

import base64

# Load and encode the mother-baby image
def load_image_base64(path):
    with open(path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

image_base64 = load_image_base64("mother_baby.png")   # <-- Save the image next to your app file

# ---------------------------------------------------------
# POPUP STATE (initialize only once)
# ---------------------------------------------------------
if "show_forgot_popup" not in st.session_state:
    st.session_state.show_forgot_popup = False

# ---------------------------------------------------------
# BEAUTIFUL LOGIN SCREEN WITH POPUP
# ---------------------------------------------------------
if not st.session_state.logged_in:

    # PAGE DESIGN
    st.markdown(f"""
    <style>
    body, .stApp {{
        background: linear-gradient(135deg, #2C1A2E, #3A243B);
    }}

    .login-container {{
        max-width: 480px;
        margin: auto;
        background: white;
        padding: 40px;
        border-radius: 20px;
        box-shadow: 0px 8px 25px rgba(0,0,0,0.12);
        margin-top: 25px;
    }}

    .login-title {{
        text-align:center; 
        color:#C2185B; 
        font-size:36px; 
        font-weight:800;
        margin-top: 10px;
    }}

    .login-slogan {{
        text-align:center; 
        color:#555; 
        font-size:18px; 
        margin-top:-10px;
        margin-bottom:20px;
    }}

    .forgot {{
        text-align:center;
        margin-top:10px;
    }}

    .forgot a {{
        color:#C2185B;
        font-weight:600;
        font-size:15px;
        cursor:pointer;
        text-decoration:none;
    }}

    .forgot a:hover {{
        text-decoration: underline;
    }}

    /* POPUP BOX */
    .popup-box {{
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: white;
        padding: 30px;
        border-radius: 18px;
        width: 500px;
        text-align: center;
        box-shadow: 0px 8px 25px rgba(0,0,0,0.25);
        z-index: 9999;
        border: 3px solid #ffb3d6;
    }}

    </style>

    <div style="text-align:center;">
        <img src="data:image/png;base64,{image_base64}" width="160" style="margin-bottom:10px;">
        <div class='login-title'>Postpartum Analytics Nexus</div>
        <div class='login-slogan'>Supporting Mothers, Strengthening Care.</div>
    </div>
    """, unsafe_allow_html=True)

    # Fix label visibility on dark background
    st.markdown("""
    <style>
    label, .stTextInput label {
        color: #C2185B !important;
        font-weight: 700 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # LOGIN CARD
    username = st.text_input("👩 **Username**", placeholder="Enter username")
    password = st.text_input("🔐 **Password**", type="password", placeholder="Enter password")

    login_clicked = st.button("Login", key="login_btn")

    # LINK → toggles popup
    if st.button("Forgot Username or Password?", key="forgot_btn"):
        st.session_state.show_forgot_popup = True

    st.markdown("</div>", unsafe_allow_html=True)
    # ---------------------------------------------------------
    # POPUP WINDOW (FINAL FIX — components.html)
    # ---------------------------------------------------------
    if st.session_state.show_forgot_popup:

        popup_html = """
        <div style="
            position: fixed;
            top: 0; left: 0;
            width: 100%; height: 100%;
            background: rgba(0,0,0,0.4);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 999999;
        ">
            <div style="
                background: white;
                width: 500px;
                padding: 30px;
                border-radius: 18px;
                text-align: center;
                box-shadow: 0 8px 25px rgba(0,0,0,0.25);
            ">
                <h3 style="color:#C2185B; font-size:28px; font-weight:800; margin-bottom:15px;">
                    Need Help Logging In?
                </h3>

                <p style="font-size:17px; color:#444; line-height:1.7;">
                    If you forgot your username or password,<br>
                    please contact the admin team:<br><br>

                    <b style="color:#C2185B; font-size:19px;">ppdwellbeings@gmail.com</b><br><br>

                    We will help you recover your account securely.
                </p>
            </div>
        </div>
        """

        import streamlit.components.v1 as components
        components.html(popup_html, height=400)

        # Close button row
        col1, col2, col3 = st.columns([3, 2, 3])
        with col2:
            if st.button("Close", key="close_popup"):
                st.session_state.show_forgot_popup = False
                st.rerun()
    # ---------------------------------------------------------
    # LOGIN LOGIC
    # ---------------------------------------------------------
    if login_clicked:
        if username == USERNAME and password == PASSWORD:
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Incorrect username or password")

    st.stop()
# -------------------------------
# WELCOME MESSAGE + LOGOUT BUTTON (aligned properly)
# -------------------------------
col_welcome, col_logout = st.columns([8, 1])

with col_welcome:
    st.markdown(
        """
        <div style="
            background-color:linear-gradient(90deg, #ff7f50, #ffb88c);
            padding:18px 25px;
            border-radius:12px;
            font-size:18px;
            font-weight:500;
            color:#1b5e20;
            margin-top:12px;
        ">
            Welcome, clinicalnurse01!
        </div>
        """,
        unsafe_allow_html=True
    )

with col_logout:
    st.write("")  # spacer for vertical alignment
    st.write("")  # spacer (adjust as needed)
    logout_clicked = st.button("🔓 Logout", key="logout_simple")

if logout_clicked:
    st.session_state.logged_in = False
    st.session_state.show_logout_page = True
    st.session_state.attempts_left = 3
    st.rerun()
# Reduce emoji size inside button
st.markdown("""
<style>
div.stButton > button:first-child {
    background: #4a234f;
    color: white !important;
    border: none;
    padding: 6px 16px;
    font-size: 18px;      /* Adjust full button text size */
    border-radius: 12px;
    font-weight: 700;
    box-shadow: 0px 3px 10px rgba(0,0,0,0.20);
}

/* reduce emoji size only */
div.stButton > button:first-child span {
    font-size: 13px !important;
}

div.stButton > button:first-child:hover {
    background: linear-gradient(90deg, #ff99c9, #ff5c98);
}
</style>
""", unsafe_allow_html=True)
# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------
st.set_page_config(page_title="California PPD Data Explorer", layout="wide")
st.markdown("""
<style>

/* MAIN BACKGROUND */
.stApp {
    background: linear-gradient(120deg, #F3E8FF 0%, #FCD6E9 100%) !important;
    background-attachment: fixed;
}

/* MAKE EVERYTHING TRANSPARENT INCLUDING TOP HEADER */
header, .stAppHeader, .stAppHeaderViewContainer, 
[data-testid="stHeader"], [data-testid="stToolbar"] {
    background: transparent !important;
}

/* MAIN VIEW CONTAINER */
[data-testid="stAppViewContainer"] {
    background: transparent !important;
}

/* MAIN CONTENT BLOCKS */
.block-container {
    background: transparent !important;
}

/* REMOVE TOP GAP / PADDING THAT SHOWS WHITE AREA */
.main .block-container {
    padding-top: 0rem !important;
    margin-top: 0rem !important;
}

/* SOME STREAMLIT BUILDS USE THESE */
.st-emotion-cache-18ni7ap, 
.st-emotion-cache-1dp5vir {
    background: transparent !important;
}

</style>
""", unsafe_allow_html=True)

st.title("👩‍🍼 California Postpartum Depression Analysis")
st.markdown("""
An AI-powered analytics platform that integrates **clinical**, **behavioral**, and **community wellbeing**
data for postpartum mothers across California.
""")
# ---------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------
@st.cache_data
def load_data():
    try:
        patients = pd.read_csv("patients_ppd.csv")
        encounters = pd.read_csv("encounters_ppd.csv")
        medications = pd.read_csv("medications_ppd.csv")
        conditions = pd.read_csv("conditions_ppd.csv")
        observations = pd.read_csv("observations_ppd.csv")
        careplans = pd.read_csv("careplans_ppd.csv")
        yoga = pd.read_csv("yoga_sessions_ppd.csv")
    except Exception as e:
        st.error(f"❌ Error loading files: {e}")
        st.stop()
    return patients, encounters, medications, conditions, observations, careplans, yoga

patients, encounters, medications, conditions, observations, careplans, yoga = load_data()

# ---------------------------------------------------------
# NORMALIZE COLUMN NAMES
# ---------------------------------------------------------
def normalize_columns(df):
    df.columns = df.columns.str.strip().str.lower()
    return df

patients = normalize_columns(patients)
encounters = normalize_columns(encounters)
medications = normalize_columns(medications)
conditions = normalize_columns(conditions)
observations = normalize_columns(observations)
careplans = normalize_columns(careplans)
yoga = normalize_columns(yoga)

# ---------------------------------------------------------
# CALIFORNIA FILTER
# ---------------------------------------------------------
if "state" in patients.columns:
    patients = patients[patients["state"].str.contains("california", case=False, na=False)]
else:
    st.warning("⚠️ 'state' column not found in patients_ppd.csv — skipping California filter.")

# ---------------------------------------------------------
# SIDEBAR FILTERS (UPDATED)
# ---------------------------------------------------------
# 🎀 Stylish Filter Header Box
st.sidebar.markdown("""
<div class="filter-header">
    <img src="https://img.icons8.com/ios-filled/50/filter.png" class="filter-icon">
    Filters
</div>
""", unsafe_allow_html=True)

# 🎨 Sidebar Styling (GRAY background + shadow)
st.markdown("""
<style>

section[data-testid="stSidebar"] {
    background: #D9D9D9 !important;   /* clean soft gray */
    padding: 10px;
    border-right: 3px solid rgba(0,0,0,0.05);
    box-shadow: 3px 0px 8px rgba(0,0,0,0.08);
}

/* Filter header box with dark pink highlight */
.filter-header {
    background: #ffe4f0;                 
    border-radius: 14px;
    padding: 12px 18px;
    font-size: 18px;
    font-weight: 700;
    color: #D61C74;                      
    display: flex;
    align-items: center;
    gap: 12px;
    border: 2px solid #ffb6d9;           
    box-shadow: 0px 3px 10px rgba(0,0,0,0.06);
    margin-bottom: 22px;
}

/* Turn icon to maternal pink */
.filter-header .filter-icon {
    width: 24px;
    height: 24px;
    filter: brightness(0) saturate(100%)
            invert(19%) sepia(87%) saturate(3400%)
            hue-rotate(314deg) brightness(90%) contrast(95%);
}

</style>
""", unsafe_allow_html=True)

# 1️⃣ Patient ID filter (Multi-select checkbox)
if "patient_id" in patients.columns:
    patient_ids = sorted(patients["patient_id"].dropna().unique().tolist())
    selected_patient_ids = st.sidebar.multiselect(
        "Patient ID",
        options=[str(pid) for pid in patient_ids],
        default=[],
        help="✅ Select one or multiple patients to explore their data"
    )
else:
    selected_patient_ids = []

# 2️⃣ City filter
city = st.sidebar.multiselect(
    "City",
    options=sorted(patients["city"].dropna().unique().tolist())
    if "city" in patients.columns
    else [],
    default=[],
    help="🏙️ Select one or more cities to filter patients"
)

# 3️⃣ Age Range filter
age_filter = st.sidebar.slider("Age Range", 18, 45, (20, 40))

# 4️⃣ Delivery Mode filter
delivery_mode = st.sidebar.selectbox("Delivery Mode", ["All", "Normal", "C-Section"])

# ---------------------------------------------------------
# 🩺 Clinical Nurse Chatbot (Sidebar Assistant)
# ---------------------------------------------------------
st.sidebar.markdown("---")
st.sidebar.markdown("""
    <div style="
        display:flex;
        align-items:center;
        gap:12px;
        padding:10px;
        background:#ffe4f0;
        border-radius:10px;
        border:2px solid #ffb6d9;
        margin-bottom:15px;
    ">
        <img src="https://png.pngtree.com/png-vector/20240510/ourlarge/pngtree-female-nurse-avatar-with-a-stethoscope-png-image_12434478.png"
             width="55"
             style="border-radius:50%; border:2px solid #ff69b4;">
        <div style="font-size:18px; font-weight:700; color:#d62976;">
            Maternal Clinical Assistant
        </div>
    </div>
""", unsafe_allow_html=True)

from langchain_community.llms import Ollama

# Initialize LLM
llm = Ollama(model="llama3")

# Session memory (no LangChain)
if "nurse_chat_history" not in st.session_state:
    st.session_state.nurse_chat_history = []   # list of {"role": "...", "msg": "..."}

# Chat input
user_msg = st.sidebar.text_area(
    "Ask a clinical question:",
    placeholder=(
        "Examples:\n"
        "- What does an EPDS of 14 mean?\n"
        "- How do I triage anxiety at 45 postpartum days?\n"
        "- What follow-up is recommended for high risk?"
    ),
    height=140
)

# ---------------------------------------------------------
# BUTTONS SIDE-BY-SIDE
# ---------------------------------------------------------
btn_col1, btn_col2 = st.sidebar.columns(2)

with btn_col1:
    ask_btn = st.button("Ask Assistant", use_container_width=True)

with btn_col2:
    clear_btn = st.button("Clear Chat", use_container_width=True)

# ---------------------------------------------------------
# ASK LOGIC
# ---------------------------------------------------------
if ask_btn:
    if user_msg.strip():
        # Add user message to history
        st.session_state.nurse_chat_history.append({"role": "user", "msg": user_msg})

        # Build conversation prompt
        conversation = ""
        for turn in st.session_state.nurse_chat_history:
            if turn["role"] == "user":
                conversation += f"User: {turn['msg']}\n"
            else:
                conversation += f"Assistant: {turn['msg']}\n"

        conversation += f"User: {user_msg}\nAssistant:"

        # Get assistant response
        with st.sidebar:
            with st.spinner("Thinking clinically..."):
                reply = llm.invoke(conversation)

        # Save reply
        st.session_state.nurse_chat_history.append({"role": "assistant", "msg": reply})

    else:
        st.sidebar.warning("Please enter a question.")

# ---------------------------------------------------------
# CLEAR LOGIC
# ---------------------------------------------------------
if clear_btn:
    st.session_state.nurse_chat_history = []
    st.sidebar.success("Chat cleared!")

# ---------------------------------------------------------
# DISPLAY CHAT HISTORY
# ---------------------------------------------------------
if st.session_state.nurse_chat_history:
    st.sidebar.markdown("### 🩺 Chat History")
    for turn in st.session_state.nurse_chat_history:
        if turn["role"] == "user":
            st.sidebar.markdown(f"**You:** {turn['msg']}")
        else:
            st.sidebar.markdown(f"**Assistant:** {turn['msg']}")
# ---------------------------------------------------------
# APPLY FILTERS DYNAMICALLY
# ---------------------------------------------------------
# --- Apply Patient ID filter (multi-select version) ---
if selected_patient_ids:
    selected_patient_ids = [int(pid) for pid in selected_patient_ids]
    filtered_patients = patients[patients["patient_id"].isin(selected_patient_ids)]
else:
    filtered_patients = patients.copy()

# --- Apply Age filter ---
if "age" in filtered_patients.columns:
    filtered_patients = filtered_patients[
        (filtered_patients["age"] >= age_filter[0]) & (filtered_patients["age"] <= age_filter[1])
    ]

# ---apply City filter ---
if city and "city" in filtered_patients.columns:
   filtered_patients = filtered_patients[filtered_patients["city"].isin(city)]

# --- Apply Delivery Mode filter ---
if delivery_mode != "All" and "delivery_mode" in encounters.columns:
    encounters_filtered = encounters[encounters["delivery_mode"] == delivery_mode]
else:
    encounters_filtered = encounters.copy()

# --- Link Patient IDs across datasets ---
linked_patient_ids = filtered_patients["patient_id"].unique().tolist()
encounters_filtered = encounters_filtered[encounters_filtered["patient_id"].isin(linked_patient_ids)]
observations_filtered = observations[observations["patient_id"].isin(linked_patient_ids)]
medications_filtered = medications[medications["patient_id"].isin(linked_patient_ids)]
careplans_filtered = careplans[careplans["patient_id"].isin(linked_patient_ids)]
yoga_filtered = yoga[yoga["patient_id"].isin(linked_patient_ids)] if "patient_id" in yoga.columns else yoga.copy()

# ---------------------------------------------------------
# GMAIL COMPLAINT TRACKER FUNCTIONS
# ---------------------------------------------------------
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.modify"
]

def get_gmail_service():
    """Authenticate and return Gmail API service."""
    creds = None
    if os.path.exists('token.json'):
        from google.oauth2.credentials import Credentials
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

@st.cache_data(show_spinner=False)
def fetch_complaints():
    """Fetch complaint emails from Gmail inbox."""
    try:
        service = get_gmail_service()
        query = '(to:ppdwellbeings@gmail.com OR to:support@ppdwellbeing.com) -from:google -from:noreply'
        results = service.users().messages().list(userId='me', q=query, maxResults=20).execute()
        messages = results.get('messages', [])
        if not messages:
            return pd.DataFrame()

        complaint_list = []
        for msg in messages:
            msg_detail = service.users().messages().get(userId='me', id=msg['id']).execute()
            headers = msg_detail['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), "")
            sender = next((h['value'] for h in headers if h['name'] == 'From'), "")
            date = next((h['value'] for h in headers if h['name'] == 'Date'), "")
            snippet = msg_detail.get('snippet', '')
            complaint_list.append({"Date": date, "Sender": sender, "Subject": subject, "Snippet": snippet})

        return pd.DataFrame(complaint_list)

    except HttpError as error:
        st.error(f"❌ Gmail API error: {error}")
        return pd.DataFrame()

# ---------------------------------------------------------
# TABS
# ---------------------------------------------------------
tabs = st.tabs([
    "🧑‍⚕️ Patient Explorer",
    "💊 Clinical Care",
    "🧘 Maternal Wellness Analysis",
    "🔮 Risk Analysis & Insights",
    "🧬 Digital Twin Simulation",
    "📊 Predictive Forecast",
    "🧍‍♀️ New Patient Risk Analyzer",
    "📬 Complaint Tracker"
])
# ---------------------------------------------------------
# TAB 1: PATIENT EXPLORER
# ---------------------------------------------------------
with tabs[0]:

    # --- Summary Metrics ---
    total_patients = len(filtered_patients)
    avg_age = round(filtered_patients["age"].mean(), 1) if "age" in filtered_patients.columns else "N/A"
    avg_epds = round(observations_filtered["epds"].mean(), 1) if "epds" in observations_filtered.columns else "N/A"
    yoga_sessions = len(yoga_filtered)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Patients", total_patients)
    col2.metric("Avg Age", avg_age)
    col3.metric("Avg EPDS Score", avg_epds)
    col4.metric("Yoga Sessions", yoga_sessions)

    # ---------------------------------------------------------
    # EPDS MONTHLY TREND
    # ---------------------------------------------------------
    if "date" in observations_filtered.columns and "epds" in observations_filtered.columns:
        st.markdown("**EPDS Score Trend Over Time**")

        observations_filtered = observations_filtered.copy()
        observations_filtered["date"] = pd.to_datetime(observations_filtered["date"], errors="coerce")
        observations_filtered = observations_filtered.dropna(subset=["date"])
        observations_filtered["month"] = observations_filtered["date"].dt.month_name().str[:3]
        observations_filtered["month_num"] = observations_filtered["date"].dt.month

        trend_data = (
            observations_filtered.groupby(["month_num", "month"])["epds"]
            .mean()
            .reset_index()
        )

        month_order = ["Dec","Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov"]
        trend_data["month"] = pd.Categorical(trend_data["month"], categories=month_order, ordered=True)
        trend_data = trend_data.sort_values("month")

        fig_epds = px.line(
            trend_data,
            x="month",
            y="epds",
            markers=True,
            color_discrete_sequence=["#FF69B4"]
        )
        fig_epds.update_traces(
            hovertemplate="Month: %{x}<br>Avg EPDS Score: %{y:.2f}<extra></extra>"
        )
        fig_epds.update_layout(
            xaxis_title="Month",
            yaxis_title="Average EPDS Score",
            template="simple_white"
        )

        # ✅ New Compliant Syntax (no warnings)
        st.plotly_chart(
            fig_epds,
            config={"displayModeBar": False, "responsive": True}
        )
    else:
        st.info("No EPDS trend data available.")

    # ---------------------------------------------------------
    # PATIENT EXPLORER TABLE & CITY CHART
    # ---------------------------------------------------------
    st.subheader("🧑‍⚕️ Patient Explorer")
    st.dataframe(filtered_patients)

    if "city" in filtered_patients.columns:
        city_chart = px.bar(
            filtered_patients.groupby("city")["patient_id"].count().reset_index(),
            x="city",
            y="patient_id",
            color="city",
            title="Patients by City"
        )
        st.plotly_chart(
            city_chart,
            config={"displayModeBar": False, "responsive": True}
        )

    # ---------------------------------------------------------
    # RISK CLASSIFICATION
    # ---------------------------------------------------------
    st.markdown("---")
    st.subheader("🧾 Risk Classification")
    st.markdown("Automated detection of **high-, moderate-, and low-risk mothers**.")

    dedup_obs = observations_filtered.copy()
    if "date" in dedup_obs.columns:
        dedup_obs = (
            dedup_obs.sort_values("date", ascending=False)
            .drop_duplicates(subset=["patient_id"], keep="first")
            .reset_index(drop=True)
        )

    if "epds" in dedup_obs.columns:

        # --- Risk Categorization Logic ---
        def classify_risk(epds):
            if epds >= 13:
                return "High"
            elif epds >= 10:
                return "Moderate"
            else:
                return "Low"

        dedup_obs["risk_category"] = dedup_obs["epds"].apply(classify_risk)

        # --- Risk Display Table ---
        risk_display = dedup_obs[["patient_id", "epds", "risk_category", "date"]].sort_values("epds", ascending=False)
        st.dataframe(risk_display)

        # --- Risk Summary Table ---
        risk_summary = (
            dedup_obs["risk_category"]
            .value_counts()
            .rename_axis("Risk Category")
            .reset_index(name="Count")
        )
        st.markdown("📊 Summary")
        st.table(risk_summary)

        # --- Summary Message ---
        total_patients = dedup_obs["patient_id"].nunique()
        high_risk_count = (dedup_obs["risk_category"] == "High").sum()
        st.markdown(f"""
        <div style="background-color:#E3F2FD;color:#0D47A1;padding:12px;
        border-left:6px solid #1976D2;border-radius:8px;font-size:16px;font-weight:500;margin-top:10px;">
        👩‍🍼 Overall, <b>{total_patients}</b> mothers were analyzed, and <b>{high_risk_count}</b> are categorized as 
        <span style='color:#E91E63;font-weight:bold;'>High Risk</span>.
        </div>
        """, unsafe_allow_html=True)

        # --- Downloadable CSV Export ---
        st.download_button(
            "📂 Download Risk Classification Data (CSV)",
            risk_display.to_csv(index=False).encode("utf-8"),
            "Risk_Classification_Report.csv",
            "text/csv",
        )

        # --- Yoga Alerts Section ---
        missed_yoga = (
            yoga_filtered[yoga_filtered["duration_minutes"] < 20]
            if "duration_minutes" in yoga_filtered.columns else pd.DataFrame()
        )

        if not missed_yoga.empty:
            st.markdown(f"""
            <div style="background-color:#FFEBEE;color:#C62828;border-left:6px solid #E53935;
            padding:12px;border-radius:6px;font-size:16px;font-weight:500;margin-top:10px;margin-bottom:10px;">
            ❌ <b>{len(missed_yoga)}</b> mothers missed or cut short yoga sessions.
            </div>""", unsafe_allow_html=True)
            st.dataframe(
                missed_yoga[["patient_id", "session_date", "duration_minutes"]]
            )

        # --- Stable Status Note ---
        if high_risk_count == 0 and missed_yoga.empty:
            st.markdown("""
            <div style="background-color:#E8F5E9;color:#2E7D32;border-left:6px solid #4CAF50;
            padding:12px;border-radius:6px;font-size:16px;font-weight:500;margin-bottom:10px;">
            ✅ No high-risk mothers detected — all are stable and active.
            </div>""", unsafe_allow_html=True)

    else:
        st.warning("⚠️ EPDS column not found in observations data.")

# ---------------------------------------------------------
# TAB 2: CLINICAL CARE
# ---------------------------------------------------------
with tabs[1]:
    st.subheader("💊 Clinical Care Insights")

    # --- 1️⃣ Medication Usage by Drug Name and Class ---
    if {"drug_name", "drug_class"}.issubset(medications_filtered.columns):
        med_summary = (
            medications_filtered.groupby(["drug_name", "drug_class"])["patient_id"]
            .count()
            .reset_index()
            .rename(columns={"patient_id": "Count"})
        )

        fig_meds = px.bar(
            med_summary,
            x="drug_name",
            y="Count",
            color="drug_class",
            title="Medication Usage by Drug Name and Class",
            color_discrete_sequence=px.colors.qualitative.Set2,
            hover_data={"drug_class": True, "Count": True},
        )
        fig_meds.update_layout(
            xaxis_title="Drug Name",
            yaxis_title="Number of Patients",
            legend_title="Drug Class",
            bargap=0.3,
        )
        st.plotly_chart(fig_meds, use_container_width=True)

    # --- 2️⃣ Care Plan Goal Distribution ---
    if "goal" in careplans_filtered.columns:
        care_summary = (
            careplans_filtered.groupby("goal")["patient_id"]
            .count()
            .reset_index()
            .rename(columns={"patient_id": "Count"})
        )
        fig_care = px.pie(
            care_summary,
            values="Count",
            names="goal",
            title="Care Plan Goal Distribution",
            color_discrete_sequence=px.colors.qualitative.Set3,
        )
        st.plotly_chart(fig_care, use_container_width=True)

    # --- 3️⃣ Delivery Mode Distribution ---
    if "delivery_mode" in encounters_filtered.columns:
        st.markdown("### 🏥 Delivery Mode Distribution")

        delivery_summary = (
            encounters_filtered["delivery_mode"]
            .value_counts()
            .reset_index()
        )
        delivery_summary.columns = ["Delivery Mode", "Count"]  # ✅ Correct renaming

        fig_delivery = px.pie(
            delivery_summary,
            values="Count",
            names="Delivery Mode",  # ✅ Matches column name exactly
            color="Delivery Mode",
            color_discrete_map={"Normal": "#4CAF50", "C-Section": "#E91E63"},
            title="Distribution of Delivery Modes Among Mothers",
        )
        st.plotly_chart(fig_delivery, use_container_width=True)

    # --- 4️⃣ Average EPDS Score by Delivery Mode ---
    if (
        {"delivery_mode", "patient_id"}.issubset(encounters_filtered.columns)
        and "epds" in observations_filtered.columns
    ):
        merged = encounters_filtered.merge(
            observations_filtered[["patient_id", "epds"]],
            on="patient_id",
            how="left",
        )

        avg_epds = (
            merged.groupby("delivery_mode")["epds"]
            .mean()
            .reset_index()
            .rename(columns={"epds": "Average EPDS Score", "delivery_mode": "Delivery Mode"})
        )

        fig_epds_mode = px.bar(
            avg_epds,
            x="Delivery Mode",
            y="Average EPDS Score",
            color="Delivery Mode",
            color_discrete_map={"Normal": "#4CAF50", "C-Section": "#E91E63"},
            title="Average EPDS Score by Delivery Mode",
            text="Average EPDS Score",
        )
        fig_epds_mode.update_traces(texttemplate='%{text:.2f}', textposition='outside')
        fig_epds_mode.update_layout(xaxis_title="Delivery Mode", yaxis_title="EPDS Score")
        st.plotly_chart(fig_epds_mode, use_container_width=True)

# ---------------------------------------------------------
# TAB 3: MATERNAL WELLBEING & Community Support
# ---------------------------------------------------------
with tabs[2]:
    st.subheader("🧘 Wellbeing Outcomes")

    if {"pre_session_wellbeing_score", "post_session_wellbeing_score"}.issubset(yoga_filtered.columns):
        fig_yoga = px.scatter(
            yoga_filtered,
            x="pre_session_wellbeing_score", y="post_session_wellbeing_score",
            color="session_type" if "session_type" in yoga_filtered.columns else None,
            trendline="ols", title="Yoga Session Impact on Wellbeing"
        )
        st.plotly_chart(fig_yoga, use_container_width=True)

    if "feedback_text" in yoga_filtered.columns:
        st.markdown("### Participant Feedback")
        st.dataframe(yoga_filtered[["session_date", "session_type", "feedback_text"]].head(10))

    st.subheader("🏘️ Community Utilization & Support")

    if "session_type" in yoga_filtered.columns:
        yoga_by_type = yoga_filtered.groupby("session_type")["patient_id"].count().reset_index().rename(columns={"patient_id": "Sessions"})
        fig_type = px.bar(yoga_by_type, x="session_type", y="Sessions", title="Yoga Participation by Type", color="session_type")
        st.plotly_chart(fig_type, use_container_width=True)

    if "instructor" in yoga_filtered.columns:
        yoga_by_instructor = yoga_filtered.groupby("instructor")["patient_id"].count().reset_index().rename(columns={"patient_id": "Participants"})
        fig_inst = px.bar(yoga_by_instructor, x="instructor", y="Participants", color="instructor", title="Instructor Participation Levels")
        st.plotly_chart(fig_inst, use_container_width=True)
# ---------------------------------------------------------
# TAB 4: Risk Analysis & Insights (Smart Auto Sound – 20 sec + Conditional Alerts + CSV Export)
# ---------------------------------------------------------
import streamlit.components.v1 as components
import base64, os, pandas as pd

with tabs[3]:
    st.subheader("🔮 Risk Analysis & Insights")

    # ---------------------------------------------------------
    # ✅ STEP 1: Deduplicate for Real-Time Clinical View
    # ---------------------------------------------------------
    if "date" in observations_filtered.columns:
        before = len(observations_filtered)
        observations_filtered = (
            observations_filtered.sort_values("date", ascending=False)
            .drop_duplicates(subset=["patient_id"], keep="first")
            .reset_index(drop=True)
        )
        after = len(observations_filtered)
        st.caption(f"🧮 Deduplication removed {before - after} duplicate EPDS records (keeping latest per patient).")

    # ---------------------------------------------------------
    # ✅ STEP 2: Continue with clean, real-time dataset
    # ---------------------------------------------------------
    if {"epds", "postpartum_days_since_delivery"}.issubset(observations_filtered.columns):
        data = observations_filtered.copy()
        data["risk_level"] = pd.cut(
            data["epds"],
            bins=[0, 9, 12, 30],
            labels=["Low", "Moderate", "High"]
        )

        # --- Summary cards ---
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Patients", data["patient_id"].nunique())
        col2.metric("High Risk (EPDS ≥ 13)", (data["epds"] >= 13).sum())
        col3.metric("Average EPDS", round(data["epds"].mean(), 1))

        # ---------------------------------------------------------
        # FLASHING / GREEN BANNER
        # ---------------------------------------------------------
        if (data["epds"] >= 13).sum() > 0:
            st.markdown("""
            <div style="
                background-color:#ff4d4d;
                color:white;
                padding:12px;
                text-align:center;
                border-radius:10px;
                font-weight:bold;
                animation: blinker 1.2s linear infinite;">
                ⚠️ Immediate Attention Required: High-Risk Patients Detected!
            </div>
            <style>@keyframes blinker {50% {opacity: 0;}}</style>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="
                background-color:#4CAF50;
                color:white;
                padding:12px;
                text-align:center;
                border-radius:10px;
                font-weight:bold;">
                ✅ All Patients Stable — No High-Risk Cases Detected
            </div>
            """, unsafe_allow_html=True)

        # ---------------------------------------------------------
        # VISUALIZATIONS
        # ---------------------------------------------------------
        st.markdown("### 📊 EPDS Distribution by Risk Level")
        fig_dist = px.histogram(
            data,
            x="epds",
            color="risk_level",
            nbins=15,
            color_discrete_map={"Low": "#8BC34A", "Moderate": "#FFC107", "High": "#E91E63"}
        )
        st.plotly_chart(fig_dist, use_container_width=True)

        st.markdown("### 📈 EPDS Trend Over Postpartum Days")
        trend_df = (
            data.groupby("postpartum_days_since_delivery")["epds"]
            .mean()
            .reset_index()
            .sort_values("postpartum_days_since_delivery")
        )
        fig_trend = px.line(
            trend_df,
            x="postpartum_days_since_delivery",
            y="epds",
            markers=True,
            title="EPDS Trend Over Postpartum Days",
            labels={"postpartum_days_since_delivery": "Days Since Delivery", "epds": "Average EPDS"}
        )
        st.plotly_chart(fig_trend, use_container_width=True)

        # ---------------------------------------------------------
        # DYNAMIC TOP-N HIGH-RISK PATIENTS SECTION
        # ---------------------------------------------------------
        high_risk_patients = (
            data[data["epds"] >= 13]
            .groupby("patient_id")["epds"]
            .mean()
            .reset_index()
            .sort_values("epds", ascending=False)
        )

        display_count = min(10, len(high_risk_patients))

        if display_count > 0:
            st.markdown(f"""
            <div style="
                display:flex;align-items:center;gap:10px;
                font-weight:bold;font-size:18px;color:#E91E63;margin-top:20px;">
                <div style="
                    width:15px;height:15px;border-radius:50%;
                    background-color:red;animation:pulse 1s infinite;">
                </div>
                Top {display_count} High-Risk Patients (EPDS ≥ 13) — Immediate Follow-Up Recommended
            </div>
            <style>
            @keyframes pulse {{
              0% {{transform:scale(1);opacity:1;}}
              50% {{transform:scale(1.4);opacity:0.6;}}
              100% {{transform:scale(1);opacity:1;}}
            }}
            </style>
            """, unsafe_allow_html=True)

            st.dataframe(high_risk_patients.head(display_count))

            # --- 📂 Downloadable CSV ---
            st.download_button(
                "📂 Download Current Risk Prediction Report (CSV)",
                data.to_csv(index=False).encode("utf-8"),
                "Current_risk_patientdata.csv",
                "text/csv"
            )

            # ---------------------------------------------------------
            # SMART SIREN LOGIC — Trigger only on NEW or WORSENED cases
            # ---------------------------------------------------------
            if "prev_high_risk" not in st.session_state:
                st.session_state.prev_high_risk = pd.DataFrame(columns=["patient_id", "epds"])

            trigger_alert = False
            merged = high_risk_patients.merge(
                st.session_state.prev_high_risk,
                on="patient_id",
                how="left",
                suffixes=("", "_prev")
            )

            new_cases = merged["epds_prev"].isna().sum()
            worsened_cases = (merged["epds"] > merged["epds_prev"].fillna(0)).sum()

            if new_cases > 0 or worsened_cases > 0:
                trigger_alert = True
                st.session_state.prev_high_risk = high_risk_patients.copy()

            # ---------------------------------------------------------
            # AUTO SOUND LOGIC (20 SECONDS)
            # ---------------------------------------------------------
            sound_path = os.path.join(os.getcwd(), "sound.mp3")

            if trigger_alert and os.path.exists(sound_path):
                with open(sound_path, "rb") as f:
                    b64_audio = base64.b64encode(f.read()).decode()

                if "mute_alert" not in st.session_state:
                    st.session_state.mute_alert = False

                mute_toggle = st.toggle("🔇 Mute Emergency Alert Sound", value=st.session_state.mute_alert)
                st.session_state.mute_alert = mute_toggle

                if not st.session_state.mute_alert:
                    components.html(f"""
                    <audio id="emergencyTone" preload="auto">
                      <source src="data:audio/mp3;base64,{b64_audio}" type="audio/mp3">
                    </audio>
                    <script>
                    window.addEventListener('load', function() {{
                        const tone = document.getElementById('emergencyTone');
                        if (!tone) return;
                        function tryPlay() {{
                            tone.play().then(() => {{
                                console.log("✅ Siren started for 20 seconds.");
                                setTimeout(() => {{
                                    tone.pause();
                                    tone.currentTime = 0;
                                    console.log("🛑 Siren stopped automatically after 20 seconds.");
                                }}, 20000);
                            }}).catch(err => {{
                                console.warn("🔇 Autoplay blocked, retrying...");
                                setTimeout(tryPlay, 2000);
                            }});
                        }}
                        tryPlay();
                    }});
                    </script>
                    """, height=0)
                    st.warning("🚨 New or Worsening High-Risk Patient(s) Detected!")
                else:
                    st.info("🔕 Alert sound muted — you can re-enable it anytime.")
            else:
                st.info("✅ No new or worsening high-risk cases detected.")
        else:
            st.success("✅ No high-risk patients detected.")
            st.session_state.prev_high_risk = pd.DataFrame(columns=["patient_id", "epds"])
    else:
        st.warning("⚠️ Required columns not found in observations_ppd.csv")
# ---------------------------------------------------------
# TAB 5: 🧬 Digital Twin Simulation
# ---------------------------------------------------------
with tabs[4]:
    st.subheader("Digital Twin Simulation")
    st.markdown("""
    This module creates a **digital twin** of the selected patient and simulates 
    how different interventions (diet, yoga, counseling, community support) 
    could change the future EPDS score and PPD risk category.
    """)

    import plotly.graph_objects as go
    import pandas as pd

    # ---------------------------------------------------------
    # 1️⃣ Select Patient from Main Patient Table
    # ---------------------------------------------------------
    st.markdown("### 👩‍🍼 Select Patient")

    patient_list = patients["name"].tolist()
    selected = st.selectbox("Choose a patient for simulation", patient_list)

    p_row = patients[patients["name"] == selected].iloc[0]

    patient_list = patients["name"].tolist()
    patient_id = p_row["patient_id"]
    name = p_row["name"]
    age = p_row["age"]
    marital_status = p_row["marital_status"] if "marital_status" in p_row else "Unknown"
    city = p_row["city"] if "city" in p_row else "Unknown"
    
    encounter_row = encounters[encounters["patient_id"] == patient_id]

    if not encounter_row.empty:
        delivery_mode = encounter_row.iloc[0].get("delivery_mode", "Unknown")
    else:
        delivery_mode = "Unknown"

    obs_row = observations[observations["patient_id"] == patient_id].tail(1)

    # Find EPDS column
    epds_col = next((c for c in observations.columns if "epds" in c.lower()), None)

    baseline_epds = (
        float(obs_row[epds_col].iloc[0]) 
        if epds_col and not obs_row.empty 
        else 10.0
    )

    # Find postpartum days column
    postpartum_col = next((c for c in observations.columns if "postpartum" in c.lower()), None)

    postpartum_days = (
        int(obs_row[postpartum_col].iloc[0])
        if postpartum_col and not obs_row.empty
        else 30
    )

    # Determine risk
    def epds_to_risk(epds):
        if epds >= 13:
            return "🔴 High Risk"
        elif epds >= 10:
            return "🟡 Moderate Risk"
        else:
            return "🟢 Low Risk"

    current_risk = epds_to_risk(baseline_epds)

    # ---------------------------------------------------------
    # Patient Overview
    # ---------------------------------------------------------
    st.markdown(f"""
    **Name:** {name} 
    **Patient ID:** {patient_id}  
    **Age:** {age}  
    **Delivery Mode:** {delivery_mode}  
    **Marital Status:** {marital_status}  
    **Postpartum Days:** {postpartum_days}  
    **Baseline EPDS:** {baseline_epds}  
    **Current Risk Category:** {current_risk}  
    """)

    # ---------------------------------------------------------
    # 2️⃣ Intervention Adjustment
    # ---------------------------------------------------------
    st.markdown("### Intervention Adjustment Panel")

    diet_factor = st.slider("🥗 Diet Quality Improvement (%)", 0, 100, 20)
    yoga_factor = st.slider("🧘 Yoga Engagement (%)", 0, 100, 30)
    counseling_factor = st.slider("💬 Counseling Participation (%)", 0, 100, 40)
    community_factor = st.slider("🏘️ Community Support (%)", 0, 100, 20)

    # ---------------------------------------------------------
    # 3️⃣ Simulation Model — Weighted Impact Formula
    # ---------------------------------------------------------
    WEIGHT_DIET = 0.12
    WEIGHT_YOGA = 0.18
    WEIGHT_COUNSELING = 0.35
    WEIGHT_COMMUNITY = 0.22

    improvement_score = (
        (diet_factor / 100) * WEIGHT_DIET +
        (yoga_factor / 100) * WEIGHT_YOGA +
        (counseling_factor / 100) * WEIGHT_COUNSELING +
        (community_factor / 100) * WEIGHT_COMMUNITY
    )

    projected_epds = round(baseline_epds * (1 - improvement_score), 2)
    epds_drop = round(baseline_epds - projected_epds, 2)
    improvement_pct = round((epds_drop / baseline_epds) * 100, 1)

    projected_risk = epds_to_risk(projected_epds)

    # ---------------------------------------------------------
    # 4️⃣ Intervention Impact Results
    # ---------------------------------------------------------
    st.markdown("### Intervention Impact")

    impact_df = pd.DataFrame({
        "Metric": ["Current EPDS", " Projected EPDS", "Improvement (%)"],
        "Value": [baseline_epds, projected_epds, f"{improvement_pct}%"]
    })

    st.table(impact_df)

    st.markdown(f"### 🔮 Projected Risk After Interventions\n{projected_risk}")

    # ---------------------------------------------------------
    # 5️⃣ Clinical Insight
    # ---------------------------------------------------------
    st.markdown("###  Clinical Insight")

    clinical_text = f"""
The simulation suggests a reduction in the patient's EPDS score from **{baseline_epds} → {projected_epds}**, 
reflecting a **{improvement_pct}% improvement** in emotional wellbeing. This projected shift toward 
**{projected_risk}** indicates favorable clinical response to the selected interventions.

Diet optimization, consistent yoga practice, structured counseling sessions, and stronger 
community involvement jointly contribute to lowering depressive symptoms and enhancing recovery.

**Recommendation:** Continue prioritizing counseling and yoga as primary interventions while 
supporting the patient with improved diet and social connectedness for sustained progress.
"""

    st.markdown(clinical_text)

    # ---------------------------------------------------------
    # 6️⃣ CSV Export
    # ---------------------------------------------------------
    sim_data = pd.DataFrame([{
        "Patient_Name": name,
        "Age": age,
        "Delivery_Mode": delivery_mode,
        "Marital_Status": marital_status,
        "Postpartum_Days": postpartum_days,
        "Baseline_EPDS": baseline_epds,
        "Projected_EPDS": projected_epds,
        "EPDS_Improvement_Percent": improvement_pct,
        "Projected_Risk": projected_risk,
        "Diet_Factor_%": diet_factor,
        "Yoga_Factor_%": yoga_factor,
        "Counseling_Factor_%": counseling_factor,
        "Community_Factor_%": community_factor,
    }])

    csv_data = sim_data.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="📥 Download CSV Report",
        data=csv_data,
        file_name=f"{name.replace(' ', '_')}_DigitalTwinSimulation.csv",
        mime="text/csv"
    )
    # ---------------------------------------------------------
    # Patient Feedback & Sentiment Analysis (VADER + Clinical Tuning)
    # ---------------------------------------------------------
    from nltk.sentiment.vader import SentimentIntensityAnalyzer
    import os
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    lexicon_path = os.path.join(current_dir, "vader_lexicon.txt")

    st.markdown("### 🗣️ Patient Feedback After Interventions")

    feedback_text = st.text_area(
        "Enter patient feedback (optional):",
        placeholder="Example: I feel more relaxed after the yoga sessions, but I still get anxious in the evenings..."
    )

    sentiment_label = None
    sentiment_score = None
    adjusted_epds = projected_epds  # default

    if feedback_text.strip():

        # Initialize analyzer
        sid = SentimentIntensityAnalyzer(lexicon_file=lexicon_path)
        scores = sid.polarity_scores(feedback_text)
        sentiment_score = scores["compound"]

        # ---------------------------------------------------------
        # 1️⃣ Base VADER thresholds
        # ---------------------------------------------------------
        if sentiment_score >= 0.10:
            sentiment_label = "😊 Positive"
            sentiment_explanation = "Patient expresses a clearly positive emotional tone."
        elif sentiment_score <= -0.10:
            sentiment_label = "😟 Negative"
            sentiment_explanation = "Patient expresses emotional distress or concerns."
        else:
            sentiment_label = "😐 Neutral"
            sentiment_explanation = "Patient expresses a neutral or mixed emotional tone."

        # ---------------------------------------------------------
        # 2️⃣ Confusion-Free Clinical Sentiment Engine (CSE)
        # ---------------------------------------------------------
        clinical_negative_terms = [
            "overwhelmed","stressed","anxious","helpless","sad",
            "worried","exhausted","depressed","numb","crying","panic"
        ]

        clinical_positive_terms = [
            "relaxed", "better", "improved", "calm", "hopeful"
        ]

        clinical_neutral_terms = [
            "okay", "stable", "manageable", "fine",
            "some days are", "nothing has changed", "nothing changed",
            "overall it's manageable", "overall its manageable"
        ]

        text_lower = feedback_text.lower()

        # Negation logic
        def is_negated(term):
            neg_patterns = [
                f"not {term}", f"no {term}", f"less {term}",
                f"not feeling {term}", f"not as {term}",
                f"haven't been {term}", f"no longer {term}"
            ]
            return any(p in text_lower for p in neg_patterns)

        # -------------------------
        # PRIORITY: NEG > NEUTRAL > POS
        # -------------------------

        # NEGATIVE override
        if any(term in text_lower for term in clinical_negative_terms):
            if not any(is_negated(term) for term in clinical_negative_terms):
                sentiment_label = "😟 Negative"
                sentiment_explanation = "Clinical keywords indicate emotional distress."

        # NEUTRAL override
        elif any(term in text_lower for term in clinical_neutral_terms):
            sentiment_label = "😐 Neutral"
            sentiment_explanation = "Feedback suggests a stable or mixed emotional state."

        # POSITIVE override
        elif any(term in text_lower for term in clinical_positive_terms):
            sentiment_label = "😊 Positive"
            sentiment_explanation = "Clinical keywords indicate emotional improvement."

        # ---------------------------------------------------------
        # 3️⃣ Display Sentiment Summary
        # ---------------------------------------------------------
        st.markdown("### Sentiment Analysis Result")
        st.write(f"**Sentiment Category:** {sentiment_label}")
        st.caption(sentiment_explanation)

        # ---------------------------------------------------------
        # 4️⃣  Clinical Insight Based on Feedback
        # ---------------------------------------------------------
        st.markdown("### Clinical Insight Based on Feedback")

        if sentiment_label == "😊 Positive":
            st.write("""
            The patient demonstrates meaningful emotional progress. Their feedback suggests that 
            current interventions—such as yoga, counseling sessions, or improved lifestyle routines—are 
            contributing to greater emotional stability and enhanced coping ability. The reduction in 
            distress signals a positive response to the therapeutic plan. Continued participation in 
            relaxation practices, structured counseling, and community or family support is recommended 
            to maintain momentum and reinforce long-term emotional resilience. 
            """)

        elif sentiment_label == "😟 Negative":
            st.write("""
            The patient continues to experience heightened emotional distress, indicating that current 
            interventions may not yet be sufficient to address their psychological needs. Reports of 
            ongoing stress, anxiety, or emotional overwhelm suggest the possibility of underlying 
            challenges that require additional support. Intensifying therapeutic strategies—such as 
            increasing counseling frequency, exploring cognitive-behavioral methods, or enhancing 
            social support—may be beneficial. Close monitoring is essential to identify any 
            escalation in symptoms and to tailor interventions accordingly.            
            """)

        else:  # Neutral
            st.write("""
            The patient's emotional state appears stable, but it has not shown significant improvement. Their feedback 
            reflects a mixed pattern—neither strong distress nor strong improvement—suggesting that they 
            are coping but may not yet be fully benefiting from current interventions. This plateau may 
            indicate that the patient needs more time to respond or that subtle adjustments to their care 
            plan could enhance progress. Regular follow-ups, gentle encouragement to continue therapeutic 
            activities, and reinforcement of emotional support systems are recommended to guide the patient 
            toward gradual improvement.          
            """)

    else:
        st.info("No feedback provided. Sentiment analysis skipped.")
# ---------------------------------------------------------   
# TAB 6: PREDICTIVE FORECAST (Model + Gmail Alert + FR2: LangChain Reasoning with Ollama)
# ---------------------------------------------------------
with tabs[5]:
    st.subheader("📊 Predictive Forecast")

    # --- EPDS Interpretation Scale ---
    st.markdown("""
    <div style='display:flex; justify-content:space-between; align-items:center; font-weight:bold;'>
      <div style='background-color:#4CAF50; width:33%; text-align:center; padding:8px; color:white;'>0–9: Low Risk</div>
      <div style='background-color:#FFC107; width:33%; text-align:center; padding:8px; color:black;'>10–12: Moderate Risk</div>
      <div style='background-color:#E91E63; width:34%; text-align:center; padding:8px; color:white;'>≥13: High Risk</div>
    </div>
    """, unsafe_allow_html=True)

    # --- Imports ---
    from sklearn.model_selection import train_test_split
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.calibration import CalibratedClassifierCV
    from sklearn.metrics import accuracy_score
    import plotly.express as px
    import matplotlib.pyplot as plt
    import pandas as pd
    import base64, os, pickle
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request

    # --- Identify key columns ---
    epds_col = next((c for c in observations_filtered.columns if 'epds' in c.lower()), None)
    age_col = next((c for c in patients.columns if 'age' in c.lower()), None)
    days_col = next((c for c in observations_filtered.columns if 'postpartum' in c.lower() or 'days' in c.lower()), None)

    if epds_col and age_col and days_col:
        # --- Merge EPDS, Age, and Postpartum days ---
        df_model = observations_filtered.merge(
            patients[["patient_id", age_col, "name", "city"]],
            on="patient_id", how="left"
        ).dropna(subset=[epds_col, age_col, days_col]).copy()

        # --- Risk classification ---
        def classify_epds(epds):
            if epds >= 13:
                return "High"
            elif epds >= 10:
                return "Moderate"
            else:
                return "Low"

        df_model["Risk_Category"] = df_model[epds_col].apply(classify_epds)
        df_model["high_risk_flag"] = (df_model["Risk_Category"] == "High").astype(int)

        # --- Prepare features ---
        features = [age_col, days_col, epds_col]
        if "duration_minutes" in yoga_filtered.columns:
            yoga_summary = yoga_filtered.groupby("patient_id")["duration_minutes"].mean().reset_index()
            df_model = df_model.merge(yoga_summary, on="patient_id", how="left")
            features.append("duration_minutes")

        X, y = df_model[features], df_model["high_risk_flag"]
        model = None

        # ---------------------------------------------------------
        # SAFE TRAIN/TEST SPLIT + CALIBRATION
        # ---------------------------------------------------------
        if len(X) == 0 or len(y) == 0:
            st.error("⚠️ No valid records available for model training.")
        else:
            if len(X) > 1 and len(y.unique()) > 1:
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
                base_model = RandomForestClassifier(n_estimators=100, random_state=42)
                model = CalibratedClassifierCV(base_model)
                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)
                accuracy = accuracy_score(y_test, y_pred)
            else:
                st.warning("⚠️ Limited or unbalanced data — training on full dataset.")
                model = RandomForestClassifier(n_estimators=100, random_state=42)
                model.fit(X, y)
                accuracy = float('nan')

            col1, col2, col3 = st.columns(3)
            col1.metric("Training Samples", len(X))
            col2.metric("Testing Samples", len(X) // 5)
            col3.metric("Model Accuracy", "N/A" if pd.isna(accuracy) else f"{accuracy*100:.2f}%")

            # --- Predict Probabilities ---
            proba = model.predict_proba(X)
            df_model["Predicted_Risk_Probability"] = proba[:, 1] if proba.shape[1] == 2 else 0.0

            # --- Alignment Function (EPDS ↔ Probability) ---
            def align_epds_probability(epds, prob):
                if epds >= 13 and prob < 0.7:
                    prob = round(0.75 + (epds - 13) * 0.02, 2)
                elif 10 <= epds < 13 and not (0.4 <= prob < 0.7):
                    prob = 0.5
                elif epds < 10 and prob > 0.4:
                    prob = 0.2

                if epds >= 13 and prob >= 0.7:
                    cat = "High"
                elif 10 <= epds < 13 and 0.4 <= prob < 0.7:
                    cat = "Moderate"
                else:
                    cat = "Low"

                return pd.Series([prob, cat])

            df_model[["Predicted_Risk_Probability", "Risk_Category"]] = df_model.apply(
                lambda x: align_epds_probability(x[epds_col], x["Predicted_Risk_Probability"]), axis=1
            )

            # --- Visualization of Risk Levels ---
            risk_stats = df_model["Risk_Category"].value_counts(normalize=True).mul(100).reset_index()
            risk_stats.columns = ["Risk_Category", "Percentage"]
            count_stats = df_model["Risk_Category"].value_counts().reset_index()
            count_stats.columns = ["Risk_Category", "Count"]
            merged_stats = pd.merge(count_stats, risk_stats, on="Risk_Category")

            high_risk_pct = merged_stats.loc[
                merged_stats["Risk_Category"] == "High", "Percentage"
            ].values[0] if "High" in merged_stats["Risk_Category"].values else 0

            st.markdown(f"### 🚨 {high_risk_pct:.1f}% of mothers are projected to be **High Risk**")
            fig_risk = px.bar(
                merged_stats, x="Risk_Category", y="Count",
                color="Risk_Category",
                color_discrete_map={"Low": "#4CAF50", "Moderate": "#FFC107", "High": "#E91E63"},
                title="Distribution of Mothers by Risk Level"
            )
            st.plotly_chart(fig_risk, use_container_width=True)

            # --- Forecast Table (All Mothers) ---
            st.markdown("### 👩‍🍼 Forecasted Risk for All Mothers")
            st.dataframe(df_model[["patient_id", "name", "city", epds_col, "Predicted_Risk_Probability", "Risk_Category"]],
                         use_container_width=True)

            # --- High-Risk Subset for Gmail Alerts ---
            high_risk_df = df_model[df_model["Risk_Category"] == "High"].copy()

            if high_risk_df.empty:
                st.success("✅ No High-Risk Mothers Predicted for Follow-Up.")
            else:
                # --- Gmail Alert ---
                import smtplib
                from email.mime.text import MIMEText
                from email.mime.multipart import MIMEMultipart

                SMTP_USER = st.secrets["email"]["username"]
                SMTP_PASS = st.secrets["email"]["password"]
                SMTP_SERVER = "smtp.gmail.com"
                SMTP_PORT = 587

                def send_gmail_alert_html(df):
                    subject = "🚨 Top 10 High-Risk Mothers Requiring Future Follow-Up"
                    html_body = f"""
                    <html><body style="font-family:Arial, sans-serif;">
                    <h2 style="color:#E91E63;text-align:center;"> Top 10 High-Risk Mothers Requiring Future Follow-Up Immediately.</h2>
                    <p>Dear Clinical Team,</p>
                    <p>The following mothers have been identified as <b>High-Risk</b> for postpartum depression in the future.
                    Please review their cases for <b>future follow-up and monitoring.</b></p>
                    <table border="1" cellspacing="0" cellpadding="8" style="border-collapse:collapse;width:100%;">
                        <tr style="background-color:#f2f2f2;font-weight:bold;">
                            <th>Patient ID</th><th>Name</th><th>City</th><th>EPDS</th><th>Predicted Risk</th>
                        </tr>
                    """
                    for _, row in df.head(10).iterrows():
                        html_body += f"""
                        <tr>
                            <td>{row['patient_id']}</td>
                            <td>{row['name']}</td>
                            <td>{row['city']}</td>
                            <td>{row[epds_col]}</td>	
                            <td style="color:#E91E63;font-weight:bold;">{row['Predicted_Risk_Probability']:.2f}</td>
                        </tr>"""
                    html_body += "</table><br><i>— Automated Wellbeing Analytics System</i></body></html>"

                    message = MIMEMultipart("alternative")
                    message["to"] = ", ".join("ppd.alerts.system@gmail.com")
                    message["from"] = f"Postpartum Alerts <{SMTP_USER}>"
                    message["subject"] = subject
                    message.attach(MIMEText(html_body, "html"))

                    return message

                try:
                                                # Create message
                                                message = send_gmail_alert_html(high_risk_df)
                                                # Send through SMTP
                                                server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
                                                server.starttls()
                                                server.login(SMTP_USER, SMTP_PASS)
                                                server.sendmail(SMTP_USER, ["ppd.alerts.system@gmail.com"], message.as_string())
                                                server.quit()

                                                st.success("📧 Gmail alert sent successfully!")
                except Exception as e:
                    st.warning(f"⚠️ Gmail alert could not be sent: {e}")

        # ---------------------------------------------------------
        # 🧠 AI Reasoning (LLaMA 3 via Ollama)
        # ---------------------------------------------------------
        from groq import Groq 
        import streamlit as st
        from langchain_core.prompts import PromptTemplate

        st.markdown("---")
        st.subheader("AI Reasoning & Contextual Prediction")

        prompt_template = """
        You are a clinical assistant analyzing postpartum depression risk predictions.

        Patient Information:
        - Age: {age}
        - Postpartum Days: {postpartum_days}
        - City: {city}
        - Marital Status: {marital_status}
        - Delivery Mode: {delivery_mode}
        - EPDS Score: {epds}
        - Predicted Probability: {predicted_prob:.2f}
        - Risk Category: {risk_category}

        Using the details above, explain in 3–4 sentences **why this patient may have this specific PPD risk category**.
        Explicitly consider **delivery mode** and **marital status** as key influencing factors.
        End with a short clinical **recommendation** for follow-up or care plan, written in a clear, empathetic tone.
        """

        def generate_ai_reasoning_ollama(age, postpartum_days, city, marital_status, delivery_mode, epds, predicted_prob, risk_category):
            try:
                client = Groq(api_key=st.secrets["groq"]["GROQ_API_KEY"])
                prompt = PromptTemplate.from_template(prompt_template)
                reasoning_prompt = prompt.format(
                    age=age, postpartum_days=postpartum_days, city=city,
                    marital_status=marital_status, delivery_mode=delivery_mode,
                    epds=epds, predicted_prob=predicted_prob, risk_category=risk_category
                )
                response = client.chat.completions.create(
                    model="llama-3.1-70b-versatile",
                    messages=[
                        {"role": "system", "content": "You are a clinical assistant providing structured PPD reasoning."},
                                                          {"role": "user", "content": reasoning_prompt}
                                                ]
                )
                return response.choices[0].message.content
            except Exception as e:
                return f"⚠️ AI reasoning unavailable: {e}"

        # --- Color-coded dropdown for all mothers ---
        if model is not None and not df_model.empty:
            def color_label(row):
                color_map = {"Low": "🟢", "Moderate": "🟡", "High": "🔴"}
                return f"{color_map.get(row['Risk_Category'], '')} {row['name']}"

            df_model["colored_name"] = df_model.apply(color_label, axis=1)
            selected_patient_label = st.selectbox("Select a patient", df_model["colored_name"])

            selected_patient = selected_patient_label.split(" ", 1)[1].split("(")[0].strip()
            selected_row = df_model[df_model["name"] == selected_patient].iloc[0]

            if st.button("🧩 Generate AI Reasoning (LLaMA 3)"):
                with st.spinner("Generating AI reasoning..."):
                    selected_patient_id = selected_row["patient_id"]
                    marital_status = patients.loc[
                        patients["patient_id"] == selected_patient_id, "marital_status"
                    ].iloc[0] if "marital_status" in patients.columns else "Unknown"
                    delivery_mode = encounters.loc[
                        encounters["patient_id"] == selected_patient_id, "delivery_mode"
                    ].iloc[0] if "delivery_mode" in encounters.columns else "Unknown"
                    reasoning_output = generate_ai_reasoning_ollama(
                        selected_row.get(age_col), selected_row.get(days_col), selected_row.get("city"),
                        marital_status, delivery_mode, selected_row.get(epds_col),
                        selected_row.get("Predicted_Risk_Probability"),
                        selected_row.get("Risk_Category")
                    )
                st.write(reasoning_output)
# --------------------------------------------------------- 
# TAB 7: 🧍‍♀️ New Patient Risk Analyzer
# ---------------------------------------------------------
with tabs[6]:
    st.subheader("🧍‍♀️ New Patient Risk Analyzer")
    st.markdown("""
    This tool enables **clinical nurses** to input new patient details and
    automatically predict the **Postpartum Depression (PPD) risk category**
    based on correlated demographic and delivery variables.
    """)

    import plotly.graph_objects as go
    import pandas as pd
    import os
    from datetime import date
    import re

    # ---------------------------------------------------------
    # 📅 Birthdate Range Validation
    # ---------------------------------------------------------
    today = date.today()
    min_birthdate = date(today.year - 45, today.month, today.day)
    max_birthdate = date(today.year - 18, today.month, today.day)

    # ---------------------------------------------------------
    # 🧾 Input Form
    # ---------------------------------------------------------
    with st.form("new_patient_form"):
        st.markdown("### 👩 Patient Information")

        name = st.text_input("Full Name")
        birthdate = st.date_input("Birthdate", min_value=min_birthdate, max_value=max_birthdate)
        age = st.number_input("Age", 18, 45, 28)
        entry_date = st.date_input("🗓️ Entry Date", value=today)

        race = st.selectbox("Race", ["Asian", "Black", "White", "Hispanic", "Other"])
        marital_status = st.selectbox("Marital Status", ["Married", "Single", "Divorced", "Widowed"])
        country = st.text_input("Country", "USA")
        state = st.text_input("State", "California")
        city = st.text_input("City")

        pregnancy_history = st.text_input("Pregnancy History (e.g., G2P1)")
        postpartum_days = st.number_input("Postpartum Days Since Delivery", 0, 365, 30)

        delivery_mode = st.selectbox("Delivery Mode", ["Normal", "C-Section"])
        delivery_subtype = st.selectbox("Delivery Subtype", ["Spontaneous", "Elective", "Induced"])
        facility_name = st.text_input("Facility Name")

        submitted = st.form_submit_button("🔍 Analyze Risk")

    # ---------------------------------------------------------
    # ⚙️ Risk Analysis Logic
    # ---------------------------------------------------------
    if submitted and name and age:
        base_risk = 0.1
        reasons = []

        # Delivery Mode
        if delivery_mode == "C-Section":
            base_risk += 0.25
            reasons.append("C-section delivery")

        # Delivery Subtype
        if delivery_subtype == "Elective":
            base_risk += 0.10
            reasons.append("elective delivery (surgical scheduling stress)")
        elif delivery_subtype == "Induced":
            base_risk += 0.15
            reasons.append("induced labor (medical intervention stress)")
        elif delivery_subtype == "Spontaneous":
            base_risk += 0.15
            reasons.append("spontaneous labor (natural stress response)")

        # Postpartum Days
        if postpartum_days > 60:
            base_risk += 0.20
            reasons.append("extended postpartum recovery (>60 days)")

        # Marital Status
        if marital_status in ["Single", "Divorced", "Widowed"]:
            base_risk += 0.25
            reasons.append("limited partner or family support")

        # Age Factor
        if age < 22 or age > 38:
            base_risk += 0.15
            reasons.append("age outside optimal range (22–38 years)")

        # Pregnancy History (G-P Logic)
        preg_text = pregnancy_history.upper().strip()
        match = re.match(r"G(\d+)P(\d+)", preg_text)

        if match:
            gravida = int(match.group(1))
            para = int(match.group(2))

            if gravida >= 3:
                base_risk += 0.10
                reasons.append(f"multiple prior pregnancies (G{gravida})")

            if para == 0:
                base_risk += 0.10
                reasons.append("first-time mother (P0)")

            if gravida - para >= 2:
                base_risk += 0.10
                reasons.append(f"history of pregnancy losses (G-P gap: {gravida - para})")

        predicted_prob = min(max(base_risk, 0), 1)

        # Category
        if predicted_prob < 0.33:
            risk_level, color, icon = "Low Risk", "#4CAF50", "🟢"
            explanation = "No major PPD indicators detected. Stable emotional health expected."
        elif predicted_prob < 0.67:
            risk_level, color, icon = "Moderate Risk", "#FFC107", "🟡"
            explanation = "Moderate risk indicators detected. Recommend periodic check-ins."
        else:
            risk_level, color, icon = "High Risk", "#E91E63", "🔴"
            explanation = "Strong indicators present. Immediate counseling or referral recommended."

        # ---------------------------------------------------------
        # 📊 Display Results
        # ---------------------------------------------------------
        st.markdown(f"## {icon} {risk_level}")
        st.markdown(f"**Predicted Probability:** {predicted_prob * 100:.1f}%")
        st.markdown(f"**Explanation:** {explanation}")

        # Gauge Chart
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=predicted_prob * 100,
            title={"text": "Predicted PPD Risk (%)"},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": color},
                "steps": [
                    {"range": [0, 33], "color": "#8BC34A"},
                    {"range": [33, 67], "color": "#FFC107"},
                    {"range": [67, 100], "color": "#E91E63"}
                ]
            }
        ))
        st.plotly_chart(fig, use_container_width=True)
        # ---------------------------------------------------------
        # 🧠 RAG IMPLEMENTATION — Pattern-Based Similar Case Insights
        # ---------------------------------------------------------
        st.markdown("---")
        st.subheader("Pattern-Based Clinical Insight (AI-RAG)")

        if os.path.exists("new_patient_log.csv"):
            df_hist = pd.read_csv("new_patient_log.csv")

            if len(df_hist) >= 3:
                from langchain_community.embeddings import HuggingFaceEmbeddings
                from langchain_community.vectorstores import FAISS
                from langchain_community.llms import Ollama

                # -------------------------------------------------
                # 1️⃣ Build internal case text (NO raw details shown)
                # -------------------------------------------------
                case_texts = []
                for _, row in df_hist.iterrows():
                    txt = f"""
                    CASE:
                    Delivery Mode: {row['Delivery_Mode']}
                    Marital Status: {row['Marital_Status']}
                    Risk Level: {row['Risk_Level']}
                    Factors: {row['Factors_Contributing']}
                    """
                    case_texts.append(txt.strip())

                # Embeddings + FAISS
                embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
                db = FAISS.from_texts(case_texts, embeddings)

                # -------------------------------------------------
                # 2️⃣ Query using patient's PATTERNS (not raw values)
                # -------------------------------------------------
                query_text = f"""
                Delivery Mode: {delivery_mode}
                Marital Status: {marital_status}
                Key Factors: {", ".join(reasons)}
                Risk Category: {risk_level}
                """

                retrieved_docs = db.similarity_search(query_text, k=3)

                # Internal patterns only (NOT displayed directly)
                retrieved_patterns = " ".join(
                    [doc.page_content for doc in retrieved_docs]
                )

                # -------------------------------------------------
                # 3️⃣ Pattern-Based LLM Prompt (DO NOT reveal raw details)
                # -------------------------------------------------
                rag_prompt = f"""
                You are a clinical decision support assistant.

                Below is internal context extracted from similar past cases.
                DO NOT reveal exact ages, postpartum days, probabilities, 
                or any raw patient details. Summaries only.

                INTERNAL HISTORICAL PATTERNS:
                {retrieved_patterns}

                NEW PATIENT SUMMARY:
                - Delivery Mode: {delivery_mode}
                - Marital Status: {marital_status}
                - Risk Category: {risk_level}
                - Key Contributing Factors: {", ".join(reasons)}

                TASK:
                • Identify pattern similarities without exposing raw data.
                • Explain why the patient's risk level is clinically reasonable.
                • Provide a 2–3 sentence recommendation.
                • Keep responses more clinical and pattern-based.
                """

                # -------------------------------------------------
                # 4️⃣ LLaMA Response
                # -------------------------------------------------
                try:
                    llm = Ollama(model="llama3")
                    rag_output = llm.invoke(rag_prompt)

                    st.write(rag_output)

                except Exception as e:
                    st.warning(f"⚠️ AI reasoning unavailable: {e}")

            else:
                st.info("ℹ️ Not enough historical records for similarity analysis.")
        else:
            st.info("ℹ️ No historical patient logs found — RAG disabled.")
        # ---------------------------------------------------------
        # 💾 Log Data to CSV  (UNCHANGED)
        # ---------------------------------------------------------
        new_entry = pd.DataFrame([{
            "Name": name,
            "Birthdate": birthdate,
            "Age": age,
            "Entry_Date": str(entry_date),
            "Race": race,
            "Marital_Status": marital_status,
            "Country": country,
            "State": state,
            "City": city,
            "Pregnancy_History": pregnancy_history,
            "Postpartum_Days": postpartum_days,
            "Delivery_Mode": delivery_mode,
            "Delivery_Subtype": delivery_subtype,
            "Facility_Name": facility_name,
            "Predicted_Probability": round(predicted_prob, 2),
            "Risk_Level": risk_level,
            "Explanation": explanation,
            "Factors_Contributing": ", ".join(reasons)
        }])

        if os.path.exists("new_patient_log.csv"):
            existing = pd.read_csv("new_patient_log.csv")
            combined = pd.concat([existing, new_entry], ignore_index=True)
        else:
            combined = new_entry
        combined.to_csv("new_patient_log.csv", index=False)

        st.success("✅ Analysis complete. Record logged successfully.")

        st.download_button(
            "📂 Download New Patient Risk Log (CSV)",
            combined.to_csv(index=False).encode("utf-8"),
            "new_patient_log.csv",
            "text/csv"
        )

        st.info("""
        **Interpretation:**
        - 🟢 Low Risk — Regular observation recommended.  
        - 🟡 Moderate Risk — Follow-up assessment advised.  
        - 🔴 High Risk — Immediate counseling or referral required.
        """)

    elif submitted:
        st.warning("⚠️ Please fill in at least Name and Age before analyzing risk.")

    # ---------------------------------------------------------
    # 📊 Summary Metrics & Visualization
    # ---------------------------------------------------------
    st.markdown("---")
    st.subheader("Recently Logged Patients")

    if os.path.exists("new_patient_log.csv"):
        df_log = pd.read_csv("new_patient_log.csv")

        if not df_log.empty:
            total_patients = len(df_log)
            avg_risk = df_log["Predicted_Probability"].mean() * 100
            risk_counts = df_log["Risk_Level"].value_counts().to_dict()

            high = risk_counts.get("High Risk", 0)
            mod = risk_counts.get("Moderate Risk", 0)
            low = risk_counts.get("Low Risk", 0)

            summary_data = {
                "Metric": [
                    "👩 Total Patients Logged",
                    "📈 Average Predicted Risk (%)",
                    "🔴 High-Risk Cases",
                    "🟡 Moderate-Risk Cases",
                    "🟢 Low-Risk Cases"
                ],
                "Value": [
                    f"{total_patients}",
                    f"{avg_risk:.1f}%",
                    f"{high} ({(high/total_patients)*100:.0f}%)",
                    f"{mod} ({(mod/total_patients)*100:.0f}%)",
                    f"{low} ({(low/total_patients)*100:.0f}%)"
                ]
            }

            summary_df = pd.DataFrame(summary_data)
            st.dataframe(
                summary_df.style.set_table_styles([
                    {"selector": "thead th", "props": [("background-color", "#0078D7"), ("color", "white"), ("font-weight", "bold"), ("text-align", "center")]},
                    {"selector": "tbody td", "props": [("text-align", "center"), ("font-size", "14px")]}
                ]).set_properties(**{"font-weight": "600"}),
                use_container_width=True
            )
        else:
            st.info("ℹ️ No patient data available yet for aggregation.")
    else:
        st.info("ℹ️ No patient data found. Please analyze a patient to generate summary.")
    # ---------------------------------------------------------
    # 📈 Adaptive Dependency Analysis on PPD Risk (Real-Time Weighted Correlation)
    # ---------------------------------------------------------
    st.subheader("📈 Dependency of Variables on PPD Risk (%)")
    st.markdown("""
    This real-time adaptive model measures how strongly each variable contributes to **Postpartum Depression (PPD)** risk.
    It recalculates dependencies dynamically each time new patients are added, giving higher weight to new observations.
    """)

    import pandas as pd
    import numpy as np
    import os
    import plotly.express as px

    try:
        # ---------------------------------------------------------
        # 1️⃣ Normalize column names
        # ---------------------------------------------------------
        patients.columns = patients.columns.str.strip().str.lower()
        encounters.columns = encounters.columns.str.strip().str.lower()
        observations.columns = observations.columns.str.strip().str.lower()

        # Detect EPDS and postpartum-related columns
        epds_col = next((c for c in observations.columns if "epds" in c.lower()), None)
        postpartum_col = next(
            (c for c in observations.columns if "postpartum" in c.lower() or "days" in c.lower()),
            None
        )

        if not epds_col or not postpartum_col:
            st.error("⚠️ Required columns ('EPDS' or 'Postpartum Days') not found in observation data.")
        else:
            # ---------------------------------------------------------
            # 2️⃣ Merge core datasets
            # ---------------------------------------------------------
            merged = (
                observations.merge(encounters, on="patient_id", how="left")
                .merge(patients, on="patient_id", how="left")
            )

            base_count = len(merged)

            # ---------------------------------------------------------
            # 3️⃣ Merge new patient log dynamically
            # ---------------------------------------------------------
            new_count = 0
            if os.path.exists("new_patient_log.csv"):
                new_patients = pd.read_csv("new_patient_log.csv")
                new_patients.columns = new_patients.columns.str.strip().str.lower()

                # If predicted probability exists, use it to estimate EPDS
                if "predicted_probability" in new_patients.columns:
                    new_patients["estimated_epds"] = new_patients["predicted_probability"] * 15
                    new_patients.rename(columns={"estimated_epds": epds_col}, inplace=True)

                # Standardize postpartum column name
                if "postpartum_days" in new_patients.columns:
                    new_patients.rename(columns={"postpartum_days": "postpartum_days_since_delivery"}, inplace=True)
                postpartum_col = "postpartum_days_since_delivery"

                # Merge columns that overlap with merged dataset
                cols_to_use = [c for c in new_patients.columns if c in merged.columns]
                if cols_to_use:
                    merged = pd.concat([merged, new_patients[cols_to_use]], ignore_index=True)
                    new_count = len(new_patients)
                    st.info(f"🧠 Merged {new_count} new patient entries (EPDS estimated from predicted probability).")
                else:
                    st.warning("⚠️ 'new_patient_log.csv' found but no matching columns to merge.")
            else:
                st.info("ℹ️ No new patient log detected — using existing dataset only.")

            # ---------------------------------------------------------
            # 4️⃣ Preprocess for correlation
            # ---------------------------------------------------------
            df = merged.copy()
            cat_cols = ["marital_status", "delivery_mode", "delivery_subtype", "pregnancy_history"]
            for col in cat_cols:
                if col in df.columns:
                    df[col] = df[col].astype("category").cat.codes

            df = df.select_dtypes(include=[np.number])
            df = df.dropna(subset=[epds_col])
            total_count = len(df)

            if total_count == 0:
                st.warning("⚠️ No usable data for dependency analysis after merging. Check EPDS or predicted values.")
            else:
                # ---------------------------------------------------------
                # 5️⃣ Compute correlation-based dependencies
                # ---------------------------------------------------------
                base_features = [
                    "age", "marital_status", "delivery_mode",
                    "delivery_subtype", "pregnancy_history", postpartum_col
                ]

                correlation_scores = {}
                for var in base_features:
                    if var in df.columns:
                        correlation_scores[var] = abs(df[var].corr(df[epds_col]))

                corr_df = pd.DataFrame(list(correlation_scores.items()), columns=["Variable", "Base_Correlation"])

                # ---------------------------------------------------------
                # 6️⃣ Adaptive weighting for new data
                # ---------------------------------------------------------
                weight_factor = min(0.2, new_count / (total_count + 1e-6))

                if new_count > 0:
                    new_pat = df.tail(new_count)
                    old_pat = df.head(base_count)

                    mean_influence = {}
                    for var in base_features:
                        if var in df.columns:
                            mean_shift = abs(new_pat[var].mean() - old_pat[var].mean()) / (old_pat[var].mean() + 1e-6)
                            var_shift = abs(new_pat[var].std() - old_pat[var].std()) / (old_pat[var].std() + 1e-6)
                            mean_influence[var] = 0.5 * (mean_shift + var_shift)

                    mean_df = pd.DataFrame(list(mean_influence.items()), columns=["Variable", "Influence_Boost"])
                    corr_df = corr_df.merge(mean_df, on="Variable", how="left")
                    corr_df["Weighted_Score"] = corr_df["Base_Correlation"] * (1 + corr_df["Influence_Boost"] * weight_factor)
                else:
                    corr_df["Weighted_Score"] = corr_df["Base_Correlation"]

                # ---------------------------------------------------------
                # 7️⃣ Normalize to dependency percentages
                # ---------------------------------------------------------
                corr_df["Dependency on PPD Risk (%)"] = (
                    corr_df["Weighted_Score"] / corr_df["Weighted_Score"].sum() * 100
                ).round(2)
                corr_df = corr_df[["Variable", "Dependency on PPD Risk (%)"]].sort_values(
                    "Dependency on PPD Risk (%)", ascending=False
                )

                # ---------------------------------------------------------
                # 8️⃣ Display with clean labels and consistency
                # ---------------------------------------------------------
                fig = px.bar(
                    corr_df,
                    x="Variable",
                    y="Dependency on PPD Risk (%)",
                    color="Dependency on PPD Risk (%)",
                    text=corr_df["Dependency on PPD Risk (%)"].astype(str) + "%",
                    color_continuous_scale="Reds",
                )
                fig.update_traces(textposition="outside", cliponaxis=False)
                fig.update_layout(
                    yaxis_title="Dependency (%)",
                    xaxis_title="Variable",
                    showlegend=False,
                    uniformtext_minsize=8,
                    uniformtext_mode="show"
                )
                st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"⚠️ Dependency analysis failed: {e}")
#----------------------------------------
# TAB 8: COMPLAINT TRACKER – Feedback & Issues
# ---------------------------------------------------------------
with tabs[7]:
    st.subheader("📬 Complaint Tracker – Feedback & Issues")

    from streamlit_autorefresh import st_autorefresh
    refresh_count = st_autorefresh(interval=600000, key="refresh_complaints")

    st.markdown("""
    This section automatically fetches recent **complaint or feedback emails**
    received at [ppdwellbeings@gmail.com](mailto:ppdwellbeings@gmail.com).

    _(The dashboard auto-refreshes every 10 minutes to check for new messages.)_
    """)

    # ---------------------------------------------------------
    # Gmail API Authentication (Fixed for 403 Error)
    # ---------------------------------------------------------
    import os
    import pickle
    import pandas as pd
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError

    # ★ Correct scopes – these MUST match exactly
    SCOPES = [
        "https://www.googleapis.com/auth/gmail.readonly",
        "https://www.googleapis.com/auth/gmail.modify",
        "https://www.googleapis.com/auth/gmail.send"
    ]

    TOKEN_FILE = "gmail_token.pkl"

    def get_gmail_service():
        """Authenticate Gmail API with correct scopes, auto-repair tokens."""
        creds = None

        # If token exists, load it
        if os.path.exists(TOKEN_FILE):
            with open(TOKEN_FILE, "rb") as f:
                creds = pickle.load(f)

        # If no credentials OR scopes changed OR token invalid → delete token
        if creds:
            if not set(creds.scopes) == set(SCOPES):
                st.warning("⚠️ Gmail scopes changed — re-authentication required.")
                os.remove(TOKEN_FILE)
                creds = None

        # If creds are missing or invalid
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception:
                    st.warning("⚠️ Token refresh failed — login again.")
                    os.remove(TOKEN_FILE)
                    creds = None

            # Fresh authentication
            if not creds:
                st.info("🔐 Opening Google sign-in for Gmail access...")
                flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
                creds = flow.run_local_server(port=0)

                with open(TOKEN_FILE, "wb") as f:
                    pickle.dump(creds, f)

        # Return Gmail API service instance
        return build("gmail", "v1", credentials=creds)


    # ---------------------------------------------------------
    # Fetch complaints from Gmail inbox
    # ---------------------------------------------------------
    def fetch_complaints():
        """Retrieve latest complaint emails."""
        try:
            service = get_gmail_service()

            query = (
                '(to:ppdwellbeings@gmail.com OR to:support@ppdwellbeing.com) '
                '-from:google -from:noreply'
            )

            results = service.users().messages().list(
                userId="me",
                q=query,
                maxResults=20
            ).execute()

            messages = results.get("messages", [])

            if not messages:
                return pd.DataFrame()

            complaint_data = []

            for msg in messages:
                detail = service.users().messages().get(
                    userId="me", id=msg["id"]
                ).execute()

                headers = detail["payload"]["headers"]

                def h(name):
                    return next((x["value"] for x in headers if x["name"] == name), "")

                complaint_data.append({
                    "Date": h("Date"),
                    "Sender": h("From"),
                    "Subject": h("Subject"),
                    "Snippet": detail.get("snippet", "")
                })

            return pd.DataFrame(complaint_data)

        except HttpError as e:
            st.error(f"❌ Gmail API error: {e}")
            if "insufficientPermissions" in str(e):
                st.error("⛔ Your Gmail token has wrong scopes. Please delete 'gmail_token.pkl' and re-authenticate.")
            return pd.DataFrame()


    # ---------------------------------------------------------
    # Interactive UI
    # ---------------------------------------------------------
    if st.button("📥 Fetch Latest Complaints"):
        with st.spinner("Fetching recent complaint emails..."):
            df = fetch_complaints()

        if not df.empty:
            st.success(f"✅ {len(df)} complaint(s) retrieved successfully.")
            st.dataframe(df, use_container_width=True)
            st.download_button(
                "📂 Download Complaints Log",
                df.to_csv(index=False).encode("utf-8"),
                "complaints_log.csv",
                "text/csv"
            )
        else:
            st.info("📭 No recent complaints found in the inbox.")
    else:
        st.caption("Press the button above to fetch the latest complaints.")
# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------
st.markdown("<hr>", unsafe_allow_html=True)
st.caption("© 2025 California Postpartum Wellbeing Analytics | Designed & Developed by **Kanmani Vijayanand** 💖")
