import streamlit as st
import sqlite3
import streamlit.components.v1 as components   
from database.auth_db import register_user, login_user
from modules.study import study_module
from modules.result import analyze_results
from modules.helpdesk import (
    ask_helpdesk,
    add_notice,
    add_timetable,
    add_announcement,
    get_data,
    add_student_question,
    get_all_questions,
    reply_to_question
)

from utils.ai_helper import generate_image, ask_from_data


import pandas as pd
import PyPDF2
import pdfplumber
from datetime import datetime

st.set_page_config(page_title="AI College Assistant", layout="wide")

# ============================================================
# 🔐 LOGIN SYSTEM (BLACK + ORANGE + FIXED DUPLICATE IDS)
# ============================================================

import streamlit as st
import sqlite3

# ============================================================
# DATABASE
# ============================================================

conn = sqlite3.connect("college_assistant.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT UNIQUE,
    password TEXT
)
""")

conn.commit()

# ============================================================
# REGISTER FUNCTION
# ============================================================

def register_user(name, email, password):
    try:
        cursor.execute("""
            INSERT INTO users (name, email, password)
            VALUES (?, ?, ?)
        """, (name, email, password))
        conn.commit()
        return True
    except:
        return False

# ============================================================
# LOGIN FUNCTION
# ============================================================

def login_user(email, password):
    cursor.execute("""
        SELECT * FROM users
        WHERE email=? AND password=?
    """, (email, password))
    return cursor.fetchone()

# ============================================================
# SESSION STATE
# ============================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_name" not in st.session_state:
    st.session_state.user_name = ""

# ============================================================
# LOGIN PAGE
# ============================================================

if not st.session_state.logged_in:

    st.markdown("""
    <style>

    /* ================= BACKGROUND ================= */
    .stApp {
        background: #000000;
        color: white;
    }

    /* ================= HIDE SIDEBAR ================= */
    section[data-testid="stSidebar"] {
        display: none;
    }

    /* ================= TITLE ================= */
    .main-title {
        text-align: center;
        font-size: 46px;
        font-weight: 800;
        color: #ff7a00;
        margin-top: 45px;
    }

    .sub-title {
        text-align: center;
        color: #ff7a00;
        opacity: 0.75;
        font-size: 16px;
        margin-bottom: 30px;
    }

    /* ================= LOGIN CARD ================= */
    div[data-testid="stVerticalBlock"] > div:has(.stTabs) {
        background: #0a0a0a;
        padding: 35px;
        border-radius: 20px;
        border: 1px solid #ff7a00;
        box-shadow: 0 0 25px rgba(255,122,0,0.25);
    }

    /* ================= INPUT STYLE ================= */
    .stTextInput input {
        background: #000000;
        color: white;
        border-radius: 10px;
        border: 1px solid #ff7a00;
        height: 48px;
        padding-left: 42px;
    }

    .stTextInput input:focus {
        border: 1px solid #ff7a00;
        box-shadow: 0 0 12px rgba(255,122,0,0.4);
    }

    /* ================= BUTTON ================= */
    .stButton > button {
        width: 100%;
        height: 48px;
        border-radius: 10px;
        background: #ff7a00;
        color: #000000;
        font-weight: 700;
        border: none;
    }

    .stButton > button:hover {
        background: #ff8c1a;
        box-shadow: 0 0 15px rgba(255,122,0,0.35);
        transform: translateY(-2px);
    }

    /* ================= TABS ================= */
    .stTabs [data-baseweb="tab"] {
        font-size: 16px;
        font-weight: 600;
        color: #ff7a00;
        opacity: 0.7;
    }

    .stTabs [aria-selected="true"] {
        color: #ff7a00 !important;
        opacity: 1;
    }

    /* ================= STREAMLIT INPUT ICON FIX ================= */

    /* Targets Streamlit input container icons */
    [data-testid="stTextInput"] svg {
        fill: #ffffff !important;
        stroke: #ffffff !important;
    }

    /* Hover effect (optional orange theme) */
    [data-testid="stTextInput"] svg:hover {
        fill: #ff7a00 !important;
        stroke: #ff7a00 !important;
    }

    /* Password eye icon button */
    [data-testid="stTextInput"] button {
        color: #ffffff !important;
    }

    [data-testid="stTextInput"] button svg {
        fill: #ffffff !important;
        stroke: #ffffff !important;
    }

    </style>
    """, unsafe_allow_html=True)

    # ================= TITLE =================
    st.markdown("<div class='main-title'>AI College Assistant</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-title'>Smart AI powered learning platform</div>", unsafe_allow_html=True)

    # ================= CENTER =================
    left, center, right = st.columns([1.5, 1, 1.5])

    with center:

        tab1, tab2 = st.tabs(["Login", "Signup"])

        # ================= LOGIN =================
        with tab1:

            st.markdown("### Login")

            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")

            if st.button("Login"):
                if not email or not password:
                    st.warning("Please fill all fields")
                else:
                    user = login_user(email, password)

                    if user:
                        st.session_state.logged_in = True
                        st.session_state.user_name = user[1]
                        st.success("Login successful")
                        st.rerun()
                    else:
                        st.error("Invalid credentials")

        # ================= SIGNUP =================
        with tab2:

            st.markdown("### Create new account")

            name = st.text_input("Full Name", key="signup_name")
            new_email = st.text_input("Email", key="signup_email")
            new_password = st.text_input("Password", type="password", key="signup_password")

            if st.button("Create Account"):
                if not name or not new_email or not new_password:
                    st.warning("Please fill all fields")
                else:
                    success = register_user(name, new_email, new_password)

                    if success:
                        st.success("Account created successfully")
                    else:
                        st.error("Email already exists")

    st.stop()

# ============================================================
# AFTER LOGIN
# ============================================================

# st.sidebar.success(
#     f"Welcome {st.session_state.user_name}"
# )

# if st.sidebar.button("🚪 Logout"):

#     st.session_state.logged_in = False

#     st.session_state.user_name = ""

#     st.rerun()



# ============================================================
# IMPORT
# ============================================================

from streamlit_option_menu import option_menu

# ============================================================
# PREMIUM UI
# ============================================================

st.markdown("""
<style>

/* =====================================================
   MAIN APP
===================================================== */

.stApp{

    background:
    radial-gradient(circle at top left,
    rgba(255,122,0,0.10),
    transparent 25%),

    radial-gradient(circle at bottom right,
    rgba(0,102,255,0.08),
    transparent 25%),

    linear-gradient(
        135deg,
        #020617,
        #050816,
        #0f172a
    );

    color:white;
}

/* =====================================================
   SIDEBAR
===================================================== */

section[data-testid="stSidebar"]{

    background:
    linear-gradient(
        180deg,
        #030712 0%,
        #0f172a 50%,
        #111827 100%
    );

    border-right:
    1px solid rgba(255,255,255,0.08);

    box-shadow:
    4px 0px 35px rgba(0,0,0,0.55);
}

/* =====================================================
   SIDEBAR PADDING
===================================================== */

section[data-testid="stSidebar"] > div{

    padding-top:15px;

    padding-left:18px;

    padding-right:18px;
}

/* =====================================================
   WELCOME CARD
===================================================== */

.welcome-card{

    background:
    linear-gradient(
        135deg,
        #16a34a,
        #22c55e
    );

    padding:12px;

    border-radius:18px;

    color:white;

    margin-bottom:14px;

    box-shadow:
    0 0 15px rgba(34,197,94,0.25);

    animation: glow 3s infinite alternate;
}

.welcome-title{

    font-size:18px;

    font-weight:700;

    margin-top:2px;

    text-align:center;
}

.welcome-sub{

    margin-top:4px;

    color:#dcfce7;

    font-size:12px;

    text-align:center;
}
/* =====================================================
   GLOW EFFECT
===================================================== */

@keyframes glow {

    from{

        box-shadow:
        0 0 15px rgba(34,197,94,0.25);
    }

    to{

        box-shadow:
        0 0 35px rgba(34,197,94,0.55);
    }
}

/* =====================================================
   SIDEBAR TITLE
===================================================== */

.sidebar-title{

    font-size:42px;

    font-weight:800;

    line-height:1.1;

    margin-top:10px;

    color:white;
}

.sidebar-highlight{

    color:#ffb347;
}

.sidebar-sub{

    color:#9ca3af;

    font-size:16px;

    margin-top:10px;

    margin-bottom:28px;

    line-height:1.6;
}

/* =====================================================
   LOGOUT BUTTON
===================================================== */

.stButton > button{

    width:100%;

    height:60px;

    border:none;

    border-radius:20px;

    background:
    linear-gradient(
        90deg,
        #ff7a00,
        #ff5e00
    );

    color:white;

    font-size:22px;

    font-weight:700;

    transition:0.3s ease;

    box-shadow:
    0 6px 24px rgba(255,122,0,0.35);
}

.stButton > button:hover{

    transform:
    translateY(-4px);

    box-shadow:
    0 8px 35px rgba(255,122,0,0.55);
}

/* =====================================================
   FEATURE CARDS
===================================================== */

.feature{

    background:
    linear-gradient(
        145deg,
        rgba(17,24,39,0.95),
        rgba(30,41,59,0.95)
    );

    padding:28px;

    border-radius:24px;

    text-align:center;

    border:1px solid rgba(255,255,255,0.06);

    transition:0.35s ease;

    backdrop-filter: blur(10px);

    margin-bottom:15px;
}

.feature:hover{

    transform:
    translateY(-8px);

    border:
    1px solid rgba(255,122,0,0.55);

    box-shadow:
    0 0 28px rgba(255,122,0,0.28);
}

/* =====================================================
   RESULT BOX
===================================================== */

.result{

    background:
    rgba(15,23,42,0.92);

    padding:25px;

    border-left:
    6px solid #ff7a00;

    border-radius:18px;

    margin-top:18px;

    box-shadow:
    0 0 18px rgba(255,122,0,0.15);
}

</style>
""", unsafe_allow_html=True)

# ============================================================
# PREMIUM SIDEBAR
# ============================================================

# ========================================================
# WELCOME CARD
# ========================================================

with st.sidebar:

    st.markdown(
        f"""
<div class='welcome-card'>

<div style='font-size:32px; text-align:center;'>

</div>

<div class='welcome-title'>
Welcome
</div>

<div style='
font-size:22px;
font-weight:800;
margin-top:8px;
text-align:center;
'>
{st.session_state.user_name}
</div>

<div class='welcome-sub'>
Glad to see you back 
</div>

</div>
""",
        unsafe_allow_html=True
    )
    # ========================================================
    # LOGOUT
    # ========================================================

    if st.button("Logout", key="sidebar_logout"):

        st.session_state.logged_in = False
        st.session_state.user_name = ""

        st.rerun()

    # ========================================================
    # TITLE
    # ========================================================

    st.markdown(
        """
        <div class="sidebar-title">
             AI College <br>
            <span class="sidebar-highlight">
            Assistant 
            </span>
        </div>

        <div class="sidebar-sub">
            Smart AI Powered Learning Platform
        </div>
        """,
        unsafe_allow_html=True
    )

    # ========================================================
    # PREMIUM MODULE MENU
    # ========================================================

    module = option_menu(

        menu_title="SELECT MODULE",

        options=[
            "Study Assistant",
            "Result Analysis",
            "Data Analysis",
            "College Helpdesk"
        ],

        icons=[
            "book",
            "bar-chart",
            "graph-up",
            "headset"
        ],

        default_index=0,

        styles={

            "container": {

                "padding": "10px",

                "background-color":
                "rgba(255,255,255,0.03)",

                "border-radius": "28px",

                "border":
                "1px solid rgba(255,255,255,0.08)"
            },

            "menu-title": {

                "color": "#d1d5db",

                "font-size": "18px",

                "font-weight": "700",

                "padding-bottom": "15px",

                "margin-left": "8px"
            },

            "icon": {

                "color": "#a855f7",

                "font-size": "25px"
            },

            "nav-link": {

                "font-size": "22px",

                "font-weight": "500",

                "text-align": "left",

                "margin": "12px",

                "padding": "20px",

                "border-radius": "22px",

                "background-color": "#111827",

                "color": "white",

                "--hover-color":
                "rgba(124,58,237,0.18)"
            },

            "nav-link-selected": {

                "background":
                "linear-gradient(90deg,#6d28d9,#2563eb)",

                "color": "white",

                "box-shadow":
                "0 0 28px rgba(124,58,237,0.55)"
            },
        }
    )

# ============================================================
# 📘 STUDY ASSISTANT
# ============================================================

if module == "Study Assistant":

    st.title("📚 AI Study Assistant")

    col1, col2 = st.columns([3,1])

    with col1:
        topic = st.text_input(" Enter Topic")

    with col2:
        uploaded_file = st.file_uploader("📂 Upload", label_visibility="collapsed")

    content = ""

    if uploaded_file:
        if uploaded_file.type == "text/plain":
            content = uploaded_file.read().decode("utf-8")
        else:
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            for page in pdf_reader.pages:
                text = page.extract_text()
                if text:
                    content += text

    final_input = content if content else topic

    def process(task):
        if not final_input:
            st.warning("Enter topic or upload file")
            return

        with st.spinner("Generating..."):
            result = study_module(final_input, task)

        st.markdown(f"<div class='result'>{result}</div>", unsafe_allow_html=True)

    st.markdown("##  Features")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown('<div class="feature"><h3> Summary</h3></div>', unsafe_allow_html=True)
        if st.button("Generate Summary"): process("Summary")

        st.markdown('<div class="feature"><h3> Concept</h3></div>', unsafe_allow_html=True)
        if st.button("Explain Concept"): process("Concept")

    with col2:
        st.markdown('<div class="feature"><h3> Questions</h3></div>', unsafe_allow_html=True)
        if st.button("Generate Questions"): process("Questions")

        st.markdown('<div class="feature"><h3> Revision</h3></div>', unsafe_allow_html=True)
        if st.button("Revision Points"): process("Revision")

    with col3:
        st.markdown('<div class="feature"><h3> Definitions</h3></div>', unsafe_allow_html=True)
        if st.button("Definitions"): process("Definitions")

        st.markdown('<div class="feature"><h3> Examples</h3></div>', unsafe_allow_html=True)
        if st.button("Examples"): process("Examples")

    st.markdown("##  Image Generation")
    img_topic = st.text_input("Enter topic for image")

    if st.button("Generate Image"):
        if img_topic:
            img = generate_image(img_topic)
            st.image(img)

# ============================================================
# 📊 RESULT ANALYSIS
# ============================================================

elif module == "Result Analysis":

    st.title("📊 Result Analysis")

    uploaded_file = st.file_uploader(
        "Upload File (CSV, Excel, PDF, TXT)",
        type=["csv", "xlsx", "pdf", "txt"]
    )

    df = None
    raw_text = ""

    if uploaded_file:
        file_type = uploaded_file.name.split(".")[-1]

        if file_type == "csv":
            df = pd.read_csv(uploaded_file)

        elif file_type == "xlsx":
            df = pd.read_excel(uploaded_file)

        elif file_type == "txt":
            raw_text = uploaded_file.read().decode("utf-8")

        elif file_type == "pdf":
            try:
                with pdfplumber.open(uploaded_file) as pdf:
                    tables = []
                    for page in pdf.pages:
                        table = page.extract_table()
                        if table:
                            tables.extend(table)

                if tables:
                    df = pd.DataFrame(tables[1:], columns=tables[0])
                    df.dropna(how="all", inplace=True)
                    df.columns = df.columns.str.strip()
                    df = df.applymap(lambda x: str(x).strip() if pd.notnull(x) else x)
                    st.success("✅ Table extracted from PDF")
                else:
                    for page in pdf.pages:
                        raw_text += page.extract_text() or ""
            except Exception as e:
                st.error(f"PDF Error: {e}")

    if df is not None:

        df = analyze_results(df)

        st.markdown("## 📊 Result Table")
        st.dataframe(df)

    # ================= Q&A =================
    if df is not None or raw_text:

        st.markdown("##  Ask Questions from Data")

        question = st.text_input("Ask anything")

        if st.button("Get Answer"):

            if not question:
                st.warning("Enter question")
            else:
                q = question.lower()

                if df is not None and any("sgpa" in c.lower() for c in df.columns):

                    sgpa_col = [c for c in df.columns if "sgpa" in c.lower()][0]
                    df[sgpa_col] = pd.to_numeric(df[sgpa_col], errors="coerce")

                    if "top" in q:
                        top10 = df.sort_values(by=sgpa_col, ascending=False).head(10)
                        st.dataframe(top10[["Name", sgpa_col]])

                    elif "topper" in q:
                        topper = df.loc[df[sgpa_col].idxmax()]
                        st.markdown(f"<div class='result'>{topper['Name']} - {topper[sgpa_col]}</div>", unsafe_allow_html=True)

                else:
                    data_text = df.to_string(index=False) if df is not None else raw_text
                    answer = ask_from_data(data_text, question)
                    st.markdown(f"<div class='result'>{answer}</div>", unsafe_allow_html=True)

# ============================================================
# 📈 DATA ANALYSIS (FULLY UPDATED SMART MODULE)
# ============================================================

elif module == "Data Analysis":

    st.title("📈 College Data Analysis Dashboard")

    uploaded_file = st.file_uploader(
        "Upload Dataset (CSV, Excel, PDF)",
        type=["csv", "xlsx", "pdf"]
    )

    df = None
    raw_text = ""

    # ============================================================
    # 📂 FILE HANDLING
    # ============================================================

    if uploaded_file:

        file_type = uploaded_file.name.split(".")[-1]

        # ---------------- CSV ----------------
        if file_type == "csv":
            df = pd.read_csv(uploaded_file)

        # ---------------- EXCEL ----------------
        elif file_type == "xlsx":
            df = pd.read_excel(uploaded_file)

        # ---------------- PDF ----------------
        elif file_type == "pdf":

            try:
                with pdfplumber.open(uploaded_file) as pdf:

                    tables = []

                    for page in pdf.pages:

                        table = page.extract_table()

                        if table:
                            tables.extend(table)

                if tables:

                    df = pd.DataFrame(
                        tables[1:],
                        columns=tables[0]
                    )

                    df.dropna(how="all", inplace=True)

                    df.columns = df.columns.str.strip()

                    df = df.applymap(
                        lambda x: str(x).strip()
                        if pd.notnull(x)
                        else x
                    )

                    st.success("✅ Table extracted from PDF")

                else:

                    with pdfplumber.open(uploaded_file) as pdf:

                        for page in pdf.pages:

                            text = page.extract_text()

                            if text:
                                raw_text += text

                    st.text_area("PDF Content", raw_text)

            except Exception as e:
                st.error(f"❌ PDF Error: {e}")

    # ============================================================
    # 📊 DATA ANALYSIS
    # ============================================================

    if df is not None:

        st.markdown("## 👀 Dataset Preview")

        st.dataframe(df.head())

        # ============================================================
        # 🔄 CONVERT NUMERIC COLUMNS
        # ============================================================

        for col in df.columns:

            try:
                df[col] = pd.to_numeric(df[col])
            except:
                pass

        # ============================================================
        # 📌 OVERVIEW
        # ============================================================

        st.markdown("## 📌 Dataset Overview")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("📄 Total Rows", df.shape[0])

        with col2:
            st.metric("📊 Total Columns", df.shape[1])

        with col3:
            numeric_cols = df.select_dtypes(include="number").columns
            st.metric("🔢 Numeric Columns", len(numeric_cols))

        # ============================================================
        # 📈 STATISTICS
        # ============================================================

        st.markdown("## 📈 Statistics")

        try:
            st.dataframe(df.describe())

        except:
            st.warning("⚠️ No numeric data available")

        # ============================================================
        # 📊 VISUALIZATION
        # ============================================================

        st.markdown("## 📊 Data Visualization")

        chart_type = st.selectbox(
            "Select Chart Type",
            ["Line Chart", "Bar Chart", "Pie Chart"]
        )

        selected_column = st.selectbox(
            "Select Column",
            df.columns
        )

        # ============================================================
        # 📈 LINE CHART
        # ============================================================

        if chart_type == "Line Chart":

            if df[selected_column].dtype != "object":

                st.line_chart(df[selected_column])

            else:
                st.warning("⚠️ Line chart needs numeric data")

        # ============================================================
        # 📊 BAR CHART
        # ============================================================

        elif chart_type == "Bar Chart":

            if df[selected_column].dtype == "object":

                value_counts = df[selected_column].value_counts()

                st.bar_chart(value_counts)

            else:

                st.bar_chart(df[selected_column])

        # ============================================================
        # 🥧 PIE CHART
        # ============================================================

        elif chart_type == "Pie Chart":

            if df[selected_column].dtype == "object":

                value_counts = df[selected_column].value_counts()

                st.write(value_counts)

                fig = value_counts.plot.pie(
                    autopct="%1.1f%%",
                    figsize=(6, 6)
                ).figure

                st.pyplot(fig)

            else:
                st.warning("⚠️ Pie chart works best with categorical data")

        # ============================================================
        # 📥 DOWNLOAD
        # ============================================================

        st.markdown("## 📥 Download Dataset")

        csv = df.to_csv(index=False).encode("utf-8")

        st.download_button(
            "Download Clean Data",
            csv,
            "clean_data.csv",
            "text/csv"
        )

    # ============================================================
    # 💬 ASK QUESTIONS FROM DATA
    # ============================================================

    if df is not None or raw_text:

        st.markdown("##  Ask Questions from Data")

        question = st.text_input(
            "Ask anything about your dataset"
        )

        if st.button("Get Answer"):

            if not question:

                st.warning("⚠️ Enter a question")

            else:

                q = question.lower()

                # ====================================================
                # 👨‍🎓 TOTAL STUDENTS
                # ====================================================

                if df is not None:

                    if "total" in q and "student" in q:

                        st.markdown(
                            f"""
                            <div class='result'>
                            👨‍🎓 Total Students: {len(df)}
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                    # ====================================================
                    # 📊 TOTAL COLUMNS
                    # ====================================================

                    elif "column" in q:

                        st.markdown(
                            f"""
                            <div class='result'>
                            📊 Total Columns: {len(df.columns)}
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                    # ====================================================
                    # 🏆 HIGHEST ATTENDANCE
                    # ====================================================

                    elif "highest attendance" in q:

                        if "Attendance" in df.columns:

                            top_row = df.loc[
                                df["Attendance"].astype(float).idxmax()
                            ]

                            st.markdown(
                                f"""
                                <div class='result'>
                                🏆 Highest Attendance<br><br>

                                👨‍🎓 Student: {top_row['Name']}<br>
                                🏫 Department: {top_row['Department']}<br>
                                📈 Attendance: {top_row['Attendance']}%
                                </div>
                                """,
                                unsafe_allow_html=True
                            )

                    # ====================================================
                    # 🥇 TOPPER / HIGHEST SGPA
                    # ====================================================

                    elif "highest sgpa" in q or "topper" in q:

                        if "SGPA" in df.columns:

                            top_row = df.loc[
                                df["SGPA"].astype(float).idxmax()
                            ]

                            st.markdown(
                                f"""
                                <div class='result'>
                                🥇 College Topper<br><br>

                                👨‍🎓 Student: {top_row['Name']}<br>
                                🏫 Department: {top_row['Department']}<br>
                                📊 SGPA: {top_row['SGPA']}
                                </div>
                                """,
                                unsafe_allow_html=True
                            )

                    # ====================================================
                    # 💼 PLACED STUDENTS
                    # ====================================================

                    elif "placed" in q:

                        if "Placement_Status" in df.columns:

                            placed_count = (
                                df["Placement_Status"]
                                .astype(str)
                                .str.lower()
                                .eq("placed")
                                .sum()
                            )

                            st.markdown(
                                f"""
                                <div class='result'>
                                💼 Total Placed Students: {placed_count}
                                </div>
                                """,
                                unsafe_allow_html=True
                            )

                    # ====================================================
                    # 📊 AVERAGE ATTENDANCE
                    # ====================================================

                    elif "average attendance" in q:

                        if "Attendance" in df.columns:

                            avg_attendance = round(
                                df["Attendance"]
                                .astype(float)
                                .mean(),
                                2
                            )

                            st.markdown(
                                f"""
                                <div class='result'>
                                📊 Average Attendance: {avg_attendance}%
                                </div>
                                """,
                                unsafe_allow_html=True
                            )

                    # ====================================================
                    # 📘 AVERAGE SGPA
                    # ====================================================

                    elif "average sgpa" in q:

                        if "SGPA" in df.columns:

                            avg_sgpa = round(
                                df["SGPA"]
                                .astype(float)
                                .mean(),
                                2
                            )

                            st.markdown(
                                f"""
                                <div class='result'>
                                📘 Average SGPA: {avg_sgpa}
                                </div>
                                """,
                                unsafe_allow_html=True
                            )

                    # ====================================================
                    # 📈 HIGHEST VALUE
                    # ====================================================

                    elif "highest" in q or "max" in q:

                        numeric_cols = df.select_dtypes(
                            include="number"
                        ).columns

                        if len(numeric_cols) > 0:

                            col = numeric_cols[0]

                            value = df[col].max()

                            st.markdown(
                                f"""
                                <div class='result'>
                                📈 Highest value in {col}: {value}
                                </div>
                                """,
                                unsafe_allow_html=True
                            )

                    # ====================================================
                    # 📉 LOWEST VALUE
                    # ====================================================

                    elif "lowest" in q or "min" in q:

                        numeric_cols = df.select_dtypes(
                            include="number"
                        ).columns

                        if len(numeric_cols) > 0:

                            col = numeric_cols[0]

                            value = df[col].min()

                            st.markdown(
                                f"""
                                <div class='result'>
                                📉 Lowest value in {col}: {value}
                                </div>
                                """,
                                unsafe_allow_html=True
                            )

                    # ====================================================
                    # 📊 GENERAL AVERAGE
                    # ====================================================

                    elif "average" in q or "mean" in q:

                        numeric_cols = df.select_dtypes(
                            include="number"
                        ).columns

                        if len(numeric_cols) > 0:

                            col = numeric_cols[0]

                            avg = round(
                                df[col].mean(),
                                2
                            )

                            st.markdown(
                                f"""
                                <div class='result'>
                                📊 Average of {col}: {avg}
                                </div>
                                """,
                                unsafe_allow_html=True
                            )

                    # ====================================================
                    # 🤖 AI FALLBACK
                    # ====================================================

                    else:

                        data_text = df.to_string(index=False)

                        with st.spinner(" Thinking..."):

                            answer = ask_from_data(
                                data_text,
                                question
                            )

                        st.markdown(
                            f"""
                            <div class='result'>
                            {answer}
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                # ====================================================
                # 📄 RAW TEXT PDF CASE
                # ====================================================

                else:

                    with st.spinner(" Thinking..."):

                        answer = ask_from_data(
                            raw_text,
                            question
                        )

                    st.markdown(
                        f"""
                        <div class='result'>
                        {answer}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

# ============================================================
# 🎓 COLLEGE HELPDESK
# ============================================================

elif module == "College Helpdesk":
    

    # st.title("🎓 College Helpdesk System")
    st.markdown("""
<div style="
background: linear-gradient(145deg,#0f172a,#1e293b);
transition:0.3s;
transform: translateY(0px);
padding:25px;
border-radius:20px;
margin-bottom:25px;
box-shadow:0 0 25px rgba(124,58,237,0.35);
">

<h1 style="
color:white;
margin:0;
font-size:38px;
">
🎓 Smart College Helpdesk
</h1>

<p style="
color:#dbeafe;
font-size:18px;
margin-top:10px;
">
AI Powered Student Support & College Management System
</p>

</div>
""", unsafe_allow_html=True)

    import os
    from dotenv import load_dotenv
    from datetime import datetime
    import streamlit.components.v1 as components

    load_dotenv()

    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

    # =================================================
    # ✅ SESSION
    # =================================================
    if "is_admin" not in st.session_state:
        st.session_state.is_admin = False

    role = st.selectbox(
        "Select Role",
        ["Student", "Admin"]
    )

    # =================================================
    # 👨‍💼 ADMIN PANEL
    # =================================================
    if role == "Admin":

        st.markdown("## 🔐 Admin Login")

        if not st.session_state.is_admin:

            admin_pass = st.text_input(
                "Enter Admin Password",
                type="password"
            )

            if st.button("Login"):

                if admin_pass == ADMIN_PASSWORD:

                    st.session_state.is_admin = True
                    st.success("✅ Login Successful")
                    st.rerun()

                else:
                    st.error("❌ Wrong Password")

        else:

            st.success("🔓 Admin Access Granted")

            if st.button("Logout"):

                st.session_state.is_admin = False
                st.rerun()

            # =================================================
            # ⏱ SETTINGS
            # =================================================
            time_value = st.number_input(
                "Expiry Time",
                min_value=1,
                value=1
            )

            time_unit = st.selectbox(
                "Time Unit",
                ["Minutes", "Hours", "Days"]
            )

            priority = st.selectbox(
                "Priority",
                ["High", "Medium", "Low"]
            )

            category = st.selectbox(
                "Category",
                ["Exam", "Event", "Holiday", "Placement"]
            )

            pinned = st.checkbox("⭐ Pin this update")

            # =================================================
            # 📢 NOTICE
            # =================================================
            st.markdown("### 📢 Add Notice")

            notice = st.text_area("Notice")

            if st.button("Add Notice"):

                msg = add_notice(
                    notice,
                    time_value,
                    time_unit,
                    priority,
                    category,
                    pinned
                )

                st.success(msg)

            # =================================================
            # 📅 TIMETABLE
            # =================================================
            st.markdown("### 📅 Add Timetable")

            timetable = st.text_area("Timetable")

            if st.button("Add Timetable"):

                msg = add_timetable(
                    timetable,
                    time_value,
                    time_unit,
                    priority,
                    "Timetable",
                    pinned
                )

                st.success(msg)

            # =================================================
            # 📣 ANNOUNCEMENT
            # =================================================
            st.markdown("### 📣 Add Announcement")

            announcement = st.text_area("Announcement")

            if st.button("Add Announcement"):

                msg = add_announcement(
                    announcement,
                    time_value,
                    time_unit,
                    priority,
                    "Announcement",
                    pinned
                )

                st.success(msg)
        # =================================================
        # ADMIN Q&A PANEL (SECURE)
        # =================================================

        if st.session_state.is_admin:

            st.markdown("##  Student Questions (Admin Only)")

            questions = get_all_questions()

            if questions:

                for q in questions:

                    st.write(f"ID: {q['id']}")
                    st.write(f"👤 {q['student_name']}")
                    st.write(f"❓ {q['question']}")

                    if q["reply"]:
                        st.success(f"Already Replied: {q['reply']}")

                    reply = st.text_area(
                        f"Reply for ID {q['id']}",
                        key=f"reply_{q['id']}"
                    )

                    if st.button("Send Reply", key=f"btn_{q['id']}"):

                        if reply.strip() == "":
                            st.warning("Enter reply first")

                        else:
                            result = reply_to_question(q["id"], reply)
                            st.success(result)

                    st.divider()

            else:
                st.info("No student questions found")

        else:

            st.warning(" Admin login required to access Student Questions")

    # =================================================
    #  STUDENT PANEL
    # =================================================
    elif role == "Student":

        st.markdown("##  Student Helpdesk")

        data = get_data()

        # =================================================
        # 🔍 SEARCH + FILTER
        # =================================================
        search = st.text_input(" Search Updates")

        filter_category = st.selectbox(
            "🏷 Filter Category",
            [
                "All",
                "Exam",
                "Event",
                "Holiday",
                "Placement",
                "Timetable",
                "Announcement"
            ]
        )

        # =================================================
        # 🎨 PRIORITY COLORS
        # =================================================
        color_map = {
            "High": "#ff4d4d",
            "Medium": "#ffaa00",
            "Low": "#00ff9c"
        }

        # =================================================
        # 📢 NOTICES
        # =================================================
        st.markdown("#  Notices")

        if data.get("notices"):

            data["notices"] = sorted(
                data["notices"],
                key=lambda x: x.get("pinned", False),
                reverse=True
            )

            filtered_notices = []

            for item in data["notices"]:

                if search and search.lower() not in item.get("text", "").lower():
                    continue

                if filter_category != "All" and item.get("category") != filter_category:
                    continue

                filtered_notices.append(item)

            for i, item in enumerate(filtered_notices[-5:]):

                text = item.get("text", "")
                created = datetime.fromisoformat(item["created_at"])
                expiry = datetime.fromisoformat(item["expiry_time"])

                priority = item.get("priority", "Low")
                category = item.get("category", "General")

                pinned_badge = "⭐ PINNED" if item.get("pinned") else ""

                border_color = color_map.get(priority, "#00ff9c")

                is_new = (
                    datetime.now() - created
                ).total_seconds() < 86400

                new_badge = " NEW" if is_new else ""

                expiry_ts = int(expiry.timestamp() * 1000)

                components.html(f"""
                <div style="
                    background: linear-gradient(145deg,#111,#1a1a1a);
                    padding:25px;
                    border-radius:18px;
                    margin-bottom:20px;
                    border-left:7px solid {border_color};
                    box-shadow:0 0 18px rgba(0,0,0,0.5);
                    color:white;
                    font-family:Arial;
                ">

                    <div style="
                        display:flex;
                        justify-content:space-between;
                        align-items:center;
                    ">

                        <h2 style="
                            color:{border_color};
                            margin:0;
                            font-size:28px;
                        ">
                             Notice {new_badge}
                        </h2>

                        <div style="
                            display:flex;
                            gap:10px;
                        ">

                            <div style="
                                background:{border_color};
                                color:black;
                                padding:8px 16px;
                                border-radius:10px;
                                font-size:16px;
                                font-weight:bold;
                            ">
                                {priority}
                            </div>

                            <div style="
                                background:gold;
                                color:black;
                                padding:8px 16px;
                                border-radius:10px;
                                font-size:16px;
                                font-weight:bold;
                            ">
                                {pinned_badge}
                            </div>

                        </div>

                    </div>

                    <div style="
                        margin-top:20px;
                        font-size:22px;
                        line-height:1.6;
                        color:#f1f1f1;
                    ">
                        {text}
                    </div>

                    <div style="
                        margin-top:25px;
                        display:flex;
                        justify-content:space-between;
                        align-items:center;
                        color:#ccc;
                        font-size:16px;
                    ">

                        <div>
                            🏷 <b>{category}</b>
                        </div>

                        <div>
                            🕒 {created.strftime('%d %b %Y %I:%M %p')}
                        </div>

                    </div>

                    <div style="
                        margin-top:15px;
                        font-size:18px;
                        color:#ffcc66;
                        font-weight:bold;
                    " id="notice{i}">
                        ⏳ Loading...
                    </div>

                </div>

                <script>
                function updateNotice{i}() {{

                    var expiry = {expiry_ts};
                    var now = new Date().getTime();
                    var diff = expiry - now;

                    if (diff <= 0) {{

                        document.getElementById("notice{i}")
                        .innerHTML = "⏳ Expired";

                        return;
                    }}

                    var h = Math.floor(diff / (1000 * 60 * 60));

                    var m = Math.floor(
                        (diff % (1000 * 60 * 60))
                        / (1000 * 60)
                    );

                    var s = Math.floor(
                        (diff % (1000 * 60))
                        / 1000
                    );

                    document.getElementById("notice{i}")
                    .innerHTML =
                    "⏳ " + h + "h " +
                    m + "m " +
                    s + "s left";
                }}

                setInterval(updateNotice{i}, 1000);
                updateNotice{i}();
                </script>
                """, height=340)

        # =================================================
        # 📅 TIMETABLE
        # =================================================
        st.markdown("#  Timetable")

        if data.get("timetable"):

            data["timetable"] = sorted(
                data["timetable"],
                key=lambda x: x.get("pinned", False),
                reverse=True
            )

            for i, item in enumerate(data["timetable"][-5:]):

                text = item.get("text", "")
                created = datetime.fromisoformat(item["created_at"])
                expiry = datetime.fromisoformat(item["expiry_time"])

                priority = item.get("priority", "Medium")
                category = item.get("category", "Timetable")

                pinned_badge = "⭐ PINNED" if item.get("pinned") else ""

                border_color = color_map.get(priority, "#4da6ff")

                expiry_ts = int(expiry.timestamp() * 1000)

                components.html(f"""
<div style="
    background: linear-gradient(145deg,#111,#1a1a1a);
    padding:25px;
    border-radius:18px;
    margin-bottom:20px;
    border-left:7px solid {border_color};
    box-shadow:0 0 18px rgba(0,0,0,0.5);
    color:white;
    font-family:Arial;
">

    <div style="
        display:flex;
        justify-content:space-between;
        align-items:center;
    ">

        <h2 style="
            color:{border_color};
            margin:0;
            font-size:28px;
        ">
             Timetable {new_badge}
        </h2>

        <div style="display:flex; gap:10px;">

            <div style="
                background:{border_color};
                color:black;
                padding:8px 16px;
                border-radius:10px;
                font-size:16px;
                font-weight:bold;
            ">
                {priority}
            </div>

            {"<div style='background:gold;color:black;padding:8px 16px;border-radius:10px;font-weight:bold;'>⭐ PINNED</div>" if item.get("pinned") else ""}

        </div>

    </div>

    <div style="
        margin-top:20px;
        font-size:22px;
        line-height:1.6;
        color:#f1f1f1;
    ">
        {text}
    </div>

    <div style="
        margin-top:25px;
        display:flex;
        justify-content:space-between;
        align-items:center;
        color:#ccc;
        font-size:16px;
    ">

        <div>
            🏷 <b>{category}</b>
        </div>

        <div>
            🕒 {created.strftime('%d %b %Y %I:%M %p')}
        </div>

    </div>

    <div style="
        margin-top:15px;
        font-size:18px;
        color:#ffcc66;
        font-weight:bold;
    " id="time{i}">
        ⏳ Loading...
    </div>

</div>

<script>

function updateTime{i}() {{

    var expiry = {expiry_ts};
    var now = new Date().getTime();
    var diff = expiry - now;

    if (diff <= 0) {{

        document.getElementById("time{i}")
        .innerHTML = "⏳ Expired";

        return;
    }}

    var h = Math.floor(diff / (1000 * 60 * 60));

    var m = Math.floor(
        (diff % (1000 * 60 * 60))
        / (1000 * 60)
    );

    var s = Math.floor(
        (diff % (1000 * 60))
        / 1000
    );

    document.getElementById("time{i}")
    .innerHTML =
    "⏳ " + h + "h " +
    m + "m " +
    s + "s left";
}}

setInterval(updateTime{i}, 1000);
updateTime{i}();

</script>
""", height=350)

        # =================================================
        # 📣 ANNOUNCEMENTS
        # =================================================
        st.markdown("#  Announcements")

        if data.get("announcements"):

            data["announcements"] = sorted(
                data["announcements"],
                key=lambda x: x.get("pinned", False),
                reverse=True
            )

            for i, item in enumerate(data["announcements"][-5:]):

                text = item.get("text", "")
                expiry = datetime.fromisoformat(item["expiry_time"])

                priority = item.get("priority", "Medium")

                pinned_badge = "⭐ PINNED" if item.get("pinned") else ""

                border_color = color_map.get(priority, "#ffcc00")

                expiry_ts = int(expiry.timestamp() * 1000)

                components.html(f"""
                <div style="
                    background: linear-gradient(145deg,#111,#1a1a1a);
                    padding:25px;
                    border-radius:18px;
                    margin-bottom:20px;
                    border-left:7px solid {border_color};
                    box-shadow:0 0 18px rgba(0,0,0,0.5);
                    color:white;
                    font-family:Arial;
                ">

                    <div style="
                        display:flex;
                        justify-content:space-between;
                        align-items:center;
                    ">

                        <h2 style="
                            color:{border_color};
                            margin:0;
                            font-size:28px;
                        ">
                             Announcement {new_badge}
                        </h2>

                    <div style="display:flex; gap:10px;">

                        <div style="
                            background:{border_color};
                            color:black;
                            padding:8px 16px;
                            border-radius:10px;
                             font-size:16px;
                font-weight:bold;
            ">
                {priority}
            </div>

            {"<div style='background:gold;color:black;padding:8px 16px;border-radius:10px;font-weight:bold;'>⭐ PINNED</div>" if item.get("pinned") else ""}

        </div>

    </div>

    <div style="
        margin-top:20px;
        font-size:22px;
        line-height:1.6;
        color:#f1f1f1;
    ">
        {text}
    </div>

    <div style="
        margin-top:25px;
        display:flex;
        justify-content:space-between;
        align-items:center;
        color:#ccc;
        font-size:16px;
    ">

        <div>
            🏷 <b>{category}</b>
        </div>

        <div>
            🕒 {created.strftime('%d %b %Y %I:%M %p')}
        </div>

    </div>

    <div style="
        margin-top:15px;
        font-size:18px;
        color:#ffcc66;
        font-weight:bold;
    " id="ann{i}">
        ⏳ Loading...
    </div>

</div>

<script>

function updateAnn{i}() {{

    var expiry = {expiry_ts};
    var now = new Date().getTime();
    var diff = expiry - now;

    if (diff <= 0) {{

        document.getElementById("ann{i}")
        .innerHTML = "⏳ Expired";

        return;
    }}

    var h = Math.floor(diff / (1000 * 60 * 60));

    var m = Math.floor(
        (diff % (1000 * 60 * 60))
        / (1000 * 60)
    );

    var s = Math.floor(
        (diff % (1000 * 60))
        / 1000
    );

    document.getElementById("ann{i}")
    .innerHTML =
    "⏳ " + h + "h " +
    m + "m " +
    s + "s left";
}}

setInterval(updateAnn{i}, 1000);
updateAnn{i}();

</script>
""", height=350)

        # =================================================
        # 💬 AI HELPDESK
        # =================================================
        st.markdown("##  Ask Helpdesk")

        question = st.text_input(
            "Ask about college updates"
        )

        if st.button("Get Answer"):

            if not question:

                st.warning("Enter question")

            else:

                with st.spinner(
                    " Fetching answer..."
                ):

                    answer = ask_helpdesk(question)

                st.markdown(
                    f"<div class='result'>{answer}</div>",
                    unsafe_allow_html=True
                )
        # =================================================
        # STUDENT Q&A (READ ONLY)
        # =================================================

        st.markdown("---")
        st.subheader(" Student Q&A System")

        with st.expander("➕ Ask Question"):

            name = st.text_input("Your Name", key="q_name")
            question = st.text_area("Your Question", key="q_text")

            if st.button("Submit Question"):

                if name and question:
                    msg = add_student_question(name, question)
                    st.success(msg)
                else:
                    st.warning("Fill all fields")

        with st.expander(" View Answers"):

            questions = get_all_questions()

            if questions:

                for q in questions:

                    st.write(f" {q['student_name']}")
                    st.write(f" {q['question']}")

                    if q.get("reply"):
                        st.success(f" {q['reply']}")
                    else:
                        st.warning("Waiting for admin reply")

                    st.divider()

            else:
                st.info("No questions yet")