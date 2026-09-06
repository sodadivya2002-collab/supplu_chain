import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import snowflake.connector
from snowflake.snowpark import Session

 
# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Dilytics Supply Chain AI",
    page_icon="📦",
    layout="wide"
)


# ============================================================
# CUSTOM CSS  (dark, commercial "AI assistant" theme)
# ============================================================
# Palette:
#   Background : #0b0b0f / #101014
#   Surface    : #16161c / #1b1b22
#   Border     : #26262f
#   Accent     : #2dd4bf (teal)  /  #f43f5e (pink, secondary accent)
#   Text       : #f5f5f7 primary, #9a9aa8 secondary
# ============================================================

st.markdown(
    """
    <style>

    /* ---------- Global cleanup ---------- */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    html, body, [class*="css"] {
        font-family: "Inter", "Segoe UI", sans-serif;
    }

    .stApp {
        background: radial-gradient(1200px 600px at 50% -10%, #14141c 0%, #0b0b0f 55%, #0b0b0f 100%) !important;
        color: #f5f5f7;
    }

    header[data-testid="stHeader"] {
        background: transparent !important;
        height: 3.75rem !important;
        z-index: 1000001 !important;
    }
    header[data-testid="stHeader"] * {
        visibility: visible !important;
        fill: #f5f5f7 !important;
    }

    .block-container {
        padding-top: 86px !important;
        max-width: 1100px;
    }

    /* ---------- Sidebar ---------- */
    section[data-testid="stSidebar"] {
        background: #0e0e13;
        border-right: 1px solid #22222b;
    }
    section[data-testid="stSidebar"] > div:first-child {
        padding-top: 78px;
    }
    section[data-testid="stSidebar"] h5,
    section[data-testid="stSidebar"] h4,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label {
        color: #9a9aa8 !important;
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }
    section[data-testid="stSidebar"] hr {
        border-color: #22222b;
    }

    .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background-color: rgba(45,212,191,0.10);
        color: #2dd4bf;
        border: 1px solid rgba(45,212,191,0.35);
        border-radius: 20px;
        padding: 3px 10px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: none !important;
    }

    /* ---------- Buttons (generic) ---------- */
    div[data-testid="stButton"] > button {
        border-radius: 10px;
        font-weight: 500;
        background: #1b1b22;
        color: #f5f5f7;
        border: 1px solid #2a2a34;
        transition: all 0.15s ease;
    }
    div[data-testid="stButton"] > button:hover {
        border-color: #2dd4bf;
        color: #2dd4bf;
    }

    section[data-testid="stSidebar"] div[data-testid="stButton"] > button {
        background: transparent;
        border: none;
        text-align: left;
        justify-content: flex-start;
        color: #cfcfd8 !important;
        font-weight: 500;
        text-transform: none;
        letter-spacing: normal;
        padding: 6px 8px;
        font-size: 0.88rem;
    }
    section[data-testid="stSidebar"] div[data-testid="stButton"] > button:hover {
        background: #1b1b22;
        color: #2dd4bf !important;
    }

    section[data-testid="stSidebar"] div[data-testid="stButton"] > button[kind="primary"] {
        background: linear-gradient(135deg, #2dd4bf 0%, #14b8a6 100%);
        color: #06231f !important;
        border-radius: 10px;
        padding: 9px 10px;
        text-align: center;
        justify-content: center;
        font-weight: 700;
        border: none;
    }
    section[data-testid="stSidebar"] div[data-testid="stButton"] > button[kind="primary"]:hover {
        filter: brightness(1.08);
        color: #06231f !important;
    }

    section[data-testid="stSidebar"] div[data-testid="stExpander"] {
        border: none;
        background: transparent;
    }
    section[data-testid="stSidebar"] div[data-testid="stExpander"] summary {
        font-weight: 500;
        color: #cfcfd8 !important;
        text-transform: none;
        padding: 4px 4px;
    }
    section[data-testid="stSidebar"] div[data-testid="stExpander"] summary:hover {
        color: #2dd4bf !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stExpanderDetails"] {
        background: #131318;
        border-radius: 8px;
    }

    /* ---------- Top navbar ---------- */
    .dily-navbar {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        height: 62px;
        background: #0e0e13;
        border-bottom: 1px solid #22222b;
        display: flex;
        align-items: center;
        justify-content: flex-end;
        padding: 0 26px 0 76px;
        z-index: 999999;
    }
    .dily-navbar-left {
        display: flex;
        align-items: center;
        gap: 16px;
    }
    .dily-logo-box {
        background: linear-gradient(135deg, #2dd4bf 0%, #14b8a6 100%);
        color: #06231f;
        font-weight: 800;
        letter-spacing: 1px;
        padding: 7px 14px;
        border-radius: 6px;
        font-size: 0.9rem;
    }

    /* ---------- Floating toggle + account chip (top corners, screenshot style) ---------- */
    .dily-toggle-fixed {
        position: fixed;
        top: 14px;
        left: 18px;
        width: 34px;
        height: 34px;
        border-radius: 9px;
        background: linear-gradient(135deg, #2dd4bf 0%, #14b8a6 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1000010;
        box-shadow: 0 2px 10px rgba(45,212,191,0.25);
    }
    .st-key-floating_toggle {
        position: fixed !important;
        top: 12px;
        left: 16px;
        z-index: 1000010;
    }
    .st-key-floating_toggle div[data-testid="stButton"] > button {
        width: 34px;
        height: 34px;
        padding: 0;
        border-radius: 9px;
        background: linear-gradient(135deg, #2dd4bf 0%, #14b8a6 100%);
        color: #06231f;
        border: none;
        font-size: 1rem;
        font-weight: 800;
        box-shadow: 0 2px 10px rgba(45,212,191,0.25);
    }
    .st-key-floating_toggle div[data-testid="stButton"] > button:hover {
        filter: brightness(1.08);
        color: #06231f;
    }

    .dily-account {
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .dily-avatar {
        width: 30px;
        height: 30px;
        border-radius: 50%;
        background: rgba(45,212,191,0.15);
        color: #2dd4bf;
        border: 1px solid rgba(45,212,191,0.4);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.75rem;
        font-weight: 700;
    }
    .dily-account-name {
        font-size: 0.85rem;
        color: #f5f5f7;
        font-weight: 500;
    }
    .dily-account-chevron {
        color: #7a7a89;
        font-size: 0.7rem;
    }

    /* ---------- Sidebar collapse tabs ---------- */
    [data-testid="stSidebarCollapsedControl"],
    [data-testid="collapsedControl"],
    [data-testid*="CollapsedControl"],
    [data-testid="stSidebarHeader"] button,
    [data-testid="stSidebarCollapseButton"],
    section[data-testid="stSidebar"] [data-testid*="Collapse"],
    section[data-testid="stSidebar"] button[kind="header"],
    header[data-testid="stHeader"] [data-testid*="Button"][aria-label*="sidebar" i],
    header[data-testid="stHeader"] button[aria-label*="sidebar" i] {
        display: none !important;
        visibility: hidden !important;
    }

    /* ---------- Hero ---------- */
    .dily-hero {
        text-align: left;
        max-width: 900px;
        margin: 0 auto;
        padding: 54px 0 6px 0;
    }
    .dily-hero .greet {
        font-size: 1.05rem;
        color: #9a9aa8;
        margin-bottom: 2px;
        font-weight: 500;
    }
    .dily-hero h1 {
        font-size: 2.4rem;
        font-weight: 700;
        color: #f5f5f7;
        margin-bottom: 0;
        letter-spacing: -0.02em;
    }
    .dily-hero p.sub {
        color: #7a7a89;
        font-size: 0.95rem;
        margin-top: 10px;
        margin-bottom: 26px;
    }

    /* ---------- Hero description cards (screenshot style: colored title pill + copy) ---------- */
    .dily-card {
        background: #131318;
        border: 1px solid #22222b;
        border-radius: 14px;
        padding: 14px 16px;
        height: 100%;
    }
    .dily-card-badge {
        display: inline-block;
        font-size: 0.72rem;
        font-weight: 700;
        padding: 3px 10px;
        border-radius: 14px;
        margin-bottom: 8px;
    }
    .dily-card-desc {
        font-size: 0.78rem;
        color: #8f8f9c;
        line-height: 1.4;
    }
    .dily-card-teal .dily-card-badge { background: rgba(45,212,191,0.15); color: #2dd4bf; }
    .dily-card-pink .dily-card-badge { background: rgba(244,63,94,0.15); color: #fb7185; }
    .dily-card-green .dily-card-badge { background: rgba(34,197,94,0.15); color: #4ade80; }
    .dily-card-purple .dily-card-badge { background: rgba(168,85,247,0.15); color: #c084fc; }

    .st-key-hero_pill_0 div[data-testid="stButton"] > button,
    .st-key-hero_pill_1 div[data-testid="stButton"] > button,
    .st-key-hero_pill_2 div[data-testid="stButton"] > button,
    .st-key-hero_pill_3 div[data-testid="stButton"] > button {
        border: none;
        background: transparent;
        color: #6b6b78;
        font-size: 0.72rem;
        font-weight: 500;
        padding: 2px 0;
        width: 100%;
        text-align: left;
    }
    .st-key-hero_pill_0 div[data-testid="stButton"] > button:hover { color: #2dd4bf; }
    .st-key-hero_pill_1 div[data-testid="stButton"] > button:hover { color: #fb7185; }
    .st-key-hero_pill_2 div[data-testid="stButton"] > button:hover { color: #4ade80; }
    .st-key-hero_pill_3 div[data-testid="stButton"] > button:hover { color: #c084fc; }

    /* ---------- Chat input ---------- */
    div[data-testid="stChatInput"] {
        border-radius: 26px !important;
        border: 1px solid #26262f !important;
        background: #16161c !important;
        box-shadow: 0 0 0 1px rgba(45,212,191,0.06), 0 8px 24px rgba(0,0,0,0.35);
        max-width: 760px;
        margin: 6px auto 0 auto;
    }
    div[data-testid="stChatInput"]:focus-within {
        border-color: #2dd4bf !important;
        box-shadow: 0 0 0 3px rgba(45,212,191,0.15);
    }
    div[data-testid="stChatInput"] textarea {
        font-size: 0.92rem;
        color: #f5f5f7 !important;
        background: transparent !important;
    }
    div[data-testid="stChatInput"] textarea::placeholder {
        color: #6b6b78 !important;
    }
    div[data-testid="stChatInput"] button {
        background: linear-gradient(135deg, #2dd4bf 0%, #14b8a6 100%) !important;
        border-radius: 50% !important;
    }
    div[data-testid="stChatInput"] button svg {
        fill: #06231f !important;
    }

    /* ---------- Chat messages ---------- */
    div[data-testid="stChatMessage"] {
        background: #14141a;
        border: 1px solid #22222b;
        border-radius: 14px;
        padding: 4px 6px;
    }

    /* ---------- Text inputs (login page) ---------- */
    div[data-testid="stTextInput"] input {
        background: #16161c !important;
        color: #f5f5f7 !important;
        border: 1px solid #2a2a34 !important;
        border-radius: 10px !important;
    }
    div[data-testid="stTextInput"] label {
        color: #cfcfd8 !important;
    }

    /* ---------- Dataframe / expander ---------- */
    div[data-testid="stExpander"] {
        background: #14141a;
        border: 1px solid #22222b;
        border-radius: 10px;
    }

    /* ---------- Misc text ---------- */
    h1, h2, h3, h4, h5, h6, p, label, .stMarkdown {
        color: #f5f5f7;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SNOWFLAKE CONFIGURATION
# ============================================================

def get_snowflake_config():

    return {
        "account": st.secrets["snowflake"]["account"],
        "role": st.secrets["snowflake"]["role"],
        "warehouse": st.secrets["snowflake"]["warehouse"],
        "database": st.secrets["snowflake"]["database"],
        "schema": st.secrets["snowflake"]["schema"]
    }


# ============================================================
# CORTEX ANALYST
# ============================================================
# All actual Supply Chain questions are handled by the Cortex
# Analyst semantic view instead of keyword matching. This is a
# standalone, top-level function.
# ============================================================

def call_cortex_analyst(prompt):

    try:

        semantic_view = st.secrets["snowflake"].get(
            "semantic_view",
            ""
        )

        if not semantic_view:
            return (
                "Cortex Analyst is not configured yet. Please add "
                "`semantic_view` under `[snowflake]` in your Streamlit "
                "secrets.",
                None
            )

        analyst_token = st.secrets["snowflake"].get(
            "cortex_analyst_token",
            ""
        )

        if not analyst_token:
            return (
                "Cortex Analyst authentication is not configured. "
                "Please add `cortex_analyst_token` under `[snowflake]` "
                "in your Streamlit secrets.",
                None
            )

        account = st.secrets["snowflake"]["account"]
        account = str(account).strip()

        if account.startswith("https://"):
            host = account.rstrip("/")
        elif account.startswith("http://"):
            host = "https://" + account[7:].rstrip("/")
        elif account.endswith(".snowflakecomputing.com"):
            host = "https://" + account
        else:
            host = "https://" + account + ".snowflakecomputing.com"

        url = host + "/api/v2/cortex/analyst/message"

        headers = {
            "Authorization": f"Bearer {analyst_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-Snowflake-Authorization-Token-Type": "PROGRAMMATIC_ACCESS_TOKEN"
        }

        request_body = {
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ],
            "semantic_view": semantic_view,
            "stream": False
        }

        response = requests.post(
            url,
            headers=headers,
            json=request_body,
            timeout=120
        )

        if response.status_code != 200:
            try:
                error_json = response.json()
                error_message = (
                    error_json.get("message")
                    or error_json.get("error")
                    or response.text
                )
            except Exception:
                error_message = response.text

            return (
                "Cortex Analyst could not process the question.\n\n"
                f"**Error:** {error_message}",
                None
            )

        analyst_response = response.json()
        message = analyst_response.get("message", {})
        content = message.get("content", [])

        explanation_parts = []
        sql_query = None
        suggestions = []

        for item in content:

            item_type = item.get("type")

            if item_type == "text":
                text = item.get("text", "").strip()
                if text:
                    explanation_parts.append(text)

            elif item_type == "sql":
                sql_query = item.get("statement", "").strip()

            elif item_type == "suggestions":
                suggestions = item.get("suggestions", []) or []

        if suggestions and not sql_query:
            suggestion_text = "\n".join(
                f"- {item}" for item in suggestions
            )

            explanation_parts.append(
                "I could not generate a query for that question. "
                "Here are some questions I can answer:\n\n"
                + suggestion_text
            )

        explanation = "\n\n".join(explanation_parts).strip()

        if not explanation:
            explanation = "Here is the result from Cortex Analyst."

        return explanation, sql_query

    except requests.exceptions.Timeout:

        return (
            "Cortex Analyst took too long to respond. "
            "Please try the question again.",
            None
        )

    except requests.exceptions.RequestException as e:

        return (
            f"Unable to connect to Cortex Analyst.\n\n**Error:** {str(e)}",
            None
        )

    except Exception as e:

        return (
            f"Cortex Analyst error.\n\n**Error:** {str(e)}",
            None
        )


# ============================================================
# SESSION STATE
# ============================================================

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "username" not in st.session_state:
    st.session_state.username = st.secrets["snowflake"].get(
        "user",
        ""
    )

if "password" not in st.session_state:
    st.session_state.password = ""

if "snowpark_session" not in st.session_state:
    st.session_state.snowpark_session = None


# ============================================================
# LOGIN
# ============================================================

if not st.session_state.authenticated:

    st.markdown(
        """
        <div class="dily-navbar">
            <div class="dily-navbar-left">
                <div class="dily-logo-box">DILYTICS</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.write("")
    st.write("")

    st.markdown(
        """
        <div class="dily-hero">
            <h1>Welcome to Dilytics Supply Chain AI</h1>
            <p class="sub">Please log in to connect to your Snowflake data warehouse.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    login_col = st.columns([1, 1.2, 1])[1]

    with login_col:

        st.session_state.username = st.text_input(
            "Snowflake Username",
            value=st.session_state.username
        )

        st.session_state.password = st.text_input(
            "Password",
            type="password"
        )

        if st.button("Login", use_container_width=True, type="primary"):

            if not st.session_state.username:

                st.error("Please enter your Snowflake username.")
                st.stop()

            if not st.session_state.password:

                st.error("Please enter your Snowflake password.")
                st.stop()

            try:

                with st.spinner("Connecting to Snowflake..."):

                    config = get_snowflake_config()

                    connection_parameters = {
                        "account": config["account"],
                        "user": st.session_state.username,
                        "password": st.session_state.password,
                        "role": config["role"],
                        "warehouse": config["warehouse"],
                        "database": config["database"],
                        "schema": config["schema"]
                    }

                    # Test connection
                    conn = snowflake.connector.connect(
                        **connection_parameters
                    )

                    conn.close()

                    # Create Snowpark session
                    st.session_state.snowpark_session = (
                        Session.builder
                        .configs(connection_parameters)
                        .create()
                    )

                    st.session_state.authenticated = True

                    st.rerun()

            except Exception as e:

                st.error(
                    f"Authentication failed: {str(e)}"
                )

    st.stop()


# ============================================================
# SNOWPARK SESSION
# ============================================================

session = st.session_state.snowpark_session


# ============================================================
# CUSTOM SIDEBAR TOGGLE STATE
# ============================================================

if "sidebar_open" not in st.session_state:
    st.session_state.sidebar_open = True


# ============================================================
# CHAT SESSIONS
# ============================================================

if "chat_sessions" not in st.session_state:

    st.session_state.chat_sessions = {}


if "current_session_id" not in st.session_state:

    session_id = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    st.session_state.current_session_id = session_id

    st.session_state.chat_sessions[session_id] = {
        "title": "New Conversation",
        "messages": []
    }


current_id = st.session_state.current_session_id

messages = (
    st.session_state
    .chat_sessions[current_id]["messages"]
)


# ============================================================
# CHART FUNCTION
# ============================================================

def display_chart_tab(
    df,
    key_prefix=""
):

    if df is None or df.empty:

        st.info(
            "No data available to create a chart."
        )

        return

    if len(df.columns) < 2:

        st.info(
            "At least two columns are required for a chart."
        )

        return

    columns = list(df.columns)

    col1, col2, col3 = st.columns(3)

    x_col = col1.selectbox(
        "Dimension",
        columns,
        key=f"{key_prefix}_x"
    )

    remaining = [
        c for c in columns
        if c != x_col
    ]

    y_col = col2.selectbox(
        "Metric",
        remaining,
        key=f"{key_prefix}_y"
    )

    chart_type = col3.selectbox(
        "Chart Type",
        [
            "Bar Chart",
            "Line Chart",
            "Area Chart",
            "Scatter Plot"
        ],
        key=f"{key_prefix}_type"
    )

    chart_df = df.copy()

    if chart_type == "Bar Chart":

        st.bar_chart(
            chart_df.set_index(x_col)[y_col]
        )

    elif chart_type == "Line Chart":

        st.line_chart(
            chart_df.set_index(x_col)[y_col]
        )

    elif chart_type == "Area Chart":

        st.area_chart(
            chart_df.set_index(x_col)[y_col]
        )

    elif chart_type == "Scatter Plot":

        st.scatter_chart(
            chart_df,
            x=x_col,
            y=y_col
        )


# ============================================================
# QUESTION ROUTER
# ============================================================

GREETING_PHRASES = [
    "hi",
    "hello",
    "hey",
    "good morning",
    "good afternoon",
    "good evening"
]

GREETING_SUGGESTIONS = [
    "What is the total purchase order count?",
    "How many shipments are currently in transit?",
    "Which suppliers are high risk?",
    "What are the top products by ordered value?",
    "What is the supplier on-time delivery percentage?",
]


def generate_sql_from_prompt(prompt):

    p = prompt.lower().strip()

    if p in GREETING_PHRASES:

        return (
            "Hi there! 👋 I'm your **Supply Chain Intelligence "
            "Assistant**. I can help you explore purchase orders, "
            "suppliers, shipments, deliveries, warehouses, and more "
            "— just ask me in plain English.\n\n"
            "Here are a few things you can try:",
            None
        )

    if (
        "what can i ask" in p
        or "what questions" in p
        or "what can you do" in p
        or "examples" in p
        or p == "help"
    ):

        return (
            """
You can ask me questions about **Supply Chain data**.

Try things like:

- What is the total purchase order count?
- What is the total ordered value?
- How many shipments are currently in transit?
- Which suppliers are high risk?
- What is the supplier on-time delivery percentage?
- What are the top products by ordered value?

Ask in plain English — Cortex Analyst will turn it into a query
against the supply chain semantic view.
""",
            None
        )

    return call_cortex_analyst(prompt)


# ============================================================
# TOP NAVBAR + FLOATING SIDEBAR TOGGLE + ACCOUNT CHIP
# ============================================================
# Matches the reference screenshot: a small teal toggle pinned to
# the top-left corner (independent of the navbar), and an
# account chip (avatar + name) pinned to the top-right.
# ============================================================

_display_name_raw = st.session_state.username or "User"
_initials = "".join(
    part[0].upper()
    for part in _display_name_raw.replace(".", " ").replace("@", " ").split()[:2]
) or "U"

st.markdown(
    f"""
    <div class="dily-navbar">
        <div class="dily-account">
            <div class="dily-avatar">{_initials}</div>
            <span class="dily-account-name">{_display_name_raw.split('@')[0]}</span>
            <span class="dily-account-chevron">▾</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

with st.container(key="floating_toggle"):

    _toggle_label = "«" if st.session_state.sidebar_open else "»"

    if st.button(_toggle_label, key="floating_toggle_btn", help="Toggle panel"):

        st.session_state.sidebar_open = not st.session_state.sidebar_open
        st.rerun()


# ============================================================
# SIDEBAR QUICK-LINK CATEGORIES
# ============================================================

QUICK_LINK_CATEGORIES = {
    "📋 Purchase Orders": [
        ("Total PO count", "What is the total purchase order count?"),
        ("Total ordered value", "What is the total ordered value?"),
        ("Open commitment", "What is the total open commitment?"),
        ("PO status breakdown", "What is the purchase order status breakdown?"),
    ],
    "🚚 Shipments": [
        ("Total shipments", "What is the total number of shipments?"),
        ("In transit", "How many shipments are currently in transit?"),
        ("Delayed shipments", "How many shipments are delayed?"),
        ("Top delay reasons", "What are the top delay reasons?"),
    ],
    "📦 Inventory": [
        ("PO value by warehouse", "What is the purchase order value by warehouse?"),
        ("Ordered qty by category", "What is the ordered quantity by product category?"),
    ],
    "🏭 Suppliers": [
        ("On-time delivery %", "What is the supplier on-time delivery percentage?"),
        ("High risk suppliers", "Which suppliers are high risk?"),
        ("Single source suppliers", "Which suppliers are single source?"),
        ("Active contracts", "Which suppliers have active contracts?"),
    ],
    "🏢 Warehouses": [
        ("PO value by warehouse", "What is the purchase order value by warehouse?"),
    ],
    "🚢 Carriers": [
        ("Shipments by carrier", "What is the shipment count by carrier?"),
        ("Freight cost by carrier", "What is freight cost by carrier?"),
    ],
    "🛠️ Products": [
        ("Top products by value", "What are the top products by ordered value?"),
        ("Ordered value by brand", "What is the ordered value by brand?"),
    ],
}


# ============================================================
# SIDEBAR
# ============================================================

sidebar_quick_prompt = None

if st.session_state.sidebar_open:

    with st.sidebar:

        st.markdown(
            '<span class="status-pill">● Semantic Mart Live</span>',
            unsafe_allow_html=True
        )

        st.write("")

        if st.button(
            "➕ New Chat",
            use_container_width=True,
            type="primary"
        ):

            new_id = datetime.now().strftime(
                "%Y%m%d_%H%M%S"
            )

            st.session_state.current_session_id = new_id

            st.session_state.chat_sessions[new_id] = {
                "title": "New Conversation",
                "messages": []
            }

            st.rerun()

        st.markdown("---")

        st.markdown(
            "##### 🕒 Recent Conversations"
        )

        for s_id, s_data in reversed(
            list(
                st.session_state.chat_sessions.items()
            )
        ):

            is_active = (
                s_id ==
                st.session_state.current_session_id
            )

            label = s_data["title"]

            if len(label) > 20:

                label = label[:18] + "..."

            if st.button(
                f"{'👉 ' if is_active else '🗨️ '}{label}",
                key=f"sess_{s_id}",
                use_container_width=True
            ):

                st.session_state.current_session_id = s_id

                st.rerun()

        st.markdown("---")

        st.markdown(
            "##### 🔗 Quick Links"
        )

        for category, items in QUICK_LINK_CATEGORIES.items():

            with st.expander(category, expanded=False):

                for label, q_prompt in items:

                    if st.button(
                        label,
                        key=f"ql_{category}_{label}",
                        use_container_width=True
                    ):

                        sidebar_quick_prompt = q_prompt

        st.markdown("---")

        if st.button(
            "🗑️ Clear All Sessions",
            use_container_width=True
        ):

            st.session_state.chat_sessions = {}

            new_id = datetime.now().strftime(
                "%Y%m%d_%H%M%S"
            )

            st.session_state.current_session_id = new_id

            st.session_state.chat_sessions[new_id] = {
                "title": "New Conversation",
                "messages": []
            }

            st.rerun()

# ============================================================
# HERO SECTION  (only shown when the current chat is empty)
# ============================================================
# Redesigned to match the dark "assistant" style: short greeting,
# large headline, and a row of colored quick-action pills — no
# decorative background artwork.
# ============================================================

hero_quick_prompt = None

# (badge_color_class, badge_label, description, sample_question)
HERO_CARDS = [
    ("teal", "Purchase Orders", "Track PO counts, open commitment, and status breakdowns.", "What is the total purchase order count?"),
    ("pink", "Suppliers", "Spot high-risk, single-source, or under-performing suppliers.", "Which suppliers are high risk?"),
    ("green", "Shipments", "Monitor in-transit shipments, delays, and delay reasons.", "How many shipments are currently in transit?"),
]

if len(messages) == 0:

    display_name = (
        st.session_state.username.split("@")[0].split(".")[0].title()
        if st.session_state.username
        else "there"
    )

    st.markdown(
        f"""
        <div class="dily-hero">
            <div class="greet">Hey! {display_name}</div>
            <h1>What can I help with?</h1>
        </div>
        """,
        unsafe_allow_html=True
    )

    card_cols = st.columns(len(HERO_CARDS))

    for i, (color, label, desc, q_prompt) in enumerate(HERO_CARDS):

        with card_cols[i]:

            st.markdown(
                f"""
                <div class="dily-card dily-card-{color}">
                    <span class="dily-card-badge">{label}</span>
                    <div class="dily-card-desc">{desc}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

            with st.container(key=f"hero_pill_{i}"):

                if st.button(
                    "Ask this →",
                    key=f"hero_pill_btn_{i}",
                    use_container_width=True
                ):

                    hero_quick_prompt = q_prompt

    st.write("")


# ============================================================
# DISPLAY CHAT HISTORY
# ============================================================

suggestion_click_prompt = None

for idx, msg in enumerate(messages):

    with st.chat_message(msg["role"]):

        st.markdown(
            msg["content"]
        )

        if (
            "sql" in msg
            and msg["sql"]
        ):

            with st.expander(
                "Generated SQL",
                expanded=False
            ):

                st.code(
                    msg["sql"],
                    language="sql"
                )

        if (
            "data" in msg
            and msg["data"] is not None
            and not msg["data"].empty
        ):

            tab1, tab2 = st.tabs(
                [
                    "Data 📄",
                    "Chart 📈"
                ]
            )

            with tab1:

                st.dataframe(
                    msg["data"],
                    use_container_width=True
                )

            with tab2:

                display_chart_tab(
                    msg["data"],
                    key_prefix=f"history_{current_id}_{idx}"
                )

        if msg.get("suggestions"):

            st.write("")

            sugg_cols = st.columns(
                len(msg["suggestions"])
            )

            for s_i, (scol, sugg_q) in enumerate(
                zip(sugg_cols, msg["suggestions"])
            ):

                with scol:

                    if st.button(
                        sugg_q,
                        key=f"sugg_{current_id}_{idx}_{s_i}",
                        use_container_width=True
                    ):

                        suggestion_click_prompt = sugg_q


# ============================================================
# CHAT INPUT
# ============================================================
# `accept_file` adds a native attach (paperclip) button inside
# the chat input, matching the reference UI. This needs
# Streamlit 1.40+; on older versions we fall back to a plain
# text-only input so the app doesn't crash.
# ============================================================

try:

    chat_result = st.chat_input(
        "Ask me anything about suppliers, purchase orders, "
        "shipments, deliveries, warehouses, carriers, or "
        "inventory...",
        accept_file="multiple",
        file_type=["pdf", "docx", "xlsx", "csv", "txt", "png", "jpg", "jpeg"]
    )

    if chat_result:
        user_prompt = chat_result.text
        uploaded_chat_files = chat_result.files
    else:
        user_prompt = None
        uploaded_chat_files = []

except TypeError:

    # Older Streamlit without accept_file support.
    user_prompt = st.chat_input(
        "Ask me anything about suppliers, purchase orders, "
        "shipments, deliveries, warehouses, carriers, or "
        "inventory..."
    )
    uploaded_chat_files = []

user_prompt = (
    user_prompt
    or hero_quick_prompt
    or sidebar_quick_prompt
    or suggestion_click_prompt
)

if uploaded_chat_files:
    # File-aware Q&A (reading/understanding the uploaded file's
    # content) is a bigger feature — this just confirms receipt
    # for now so the attach button is visibly functional.
    file_names = ", ".join(f.name for f in uploaded_chat_files)
    user_prompt = (
        f"{user_prompt or ''}\n\n(Attached: {file_names})"
    ).strip()


# ============================================================
# PROCESS QUESTION
# ============================================================

if user_prompt:

    if len(messages) == 0:

        st.session_state.chat_sessions[
            current_id
        ]["title"] = (
            user_prompt[:25]
            + (
                "..."
                if len(user_prompt) > 25
                else ""
            )
        )

    messages.append(
        {
            "role": "user",
            "content": user_prompt
        }
    )

    with st.chat_message("user"):

        st.markdown(
            user_prompt
        )

    with st.chat_message("assistant"):

        explanation, sql_query = (
            generate_sql_from_prompt(
                user_prompt
            )
        )

        is_greeting_prompt = (
            user_prompt.strip().lower()
            in GREETING_PHRASES
        )

        suggestions = (
            GREETING_SUGGESTIONS
            if is_greeting_prompt
            else None
        )

        st.markdown(
            explanation
        )

        df = None

        if sql_query:

            with st.expander(
                "Generated SQL",
                expanded=False
            ):

                st.code(
                    sql_query,
                    language="sql"
                )

            try:

                df = (
                    session
                    .sql(sql_query)
                    .to_pandas()
                )

                if df.empty:

                    st.info(
                        "The query executed successfully, "
                        "but no records were returned."
                    )

                else:

                    tab1, tab2 = st.tabs(
                        [
                            "Data 📄",
                            "Chart 📈"
                        ]
                    )

                    with tab1:

                        st.dataframe(
                            df,
                            use_container_width=True
                        )

                    with tab2:

                        display_chart_tab(
                            df,
                            key_prefix=f"live_{current_id}"
                        )

            except Exception as e:

                st.error(
                    f"SQL Execution Error: {str(e)}"
                )

    messages.append(
        {
            "role": "assistant",
            "content": explanation,
            "sql": sql_query,
            "data": df,
            "suggestions": suggestions
        }
    )

    st.rerun()
