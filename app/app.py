import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import snowflake.connector
from snowflake.snowpark import Session

try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False


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
#
# NOTE ON BUTTONS: every button (main sidebar actions, history
# items, file rows, use/remove) is now a bordered/outlined
# button with NO filled background. The only visual "color" is
# the teal border + teal text that appears on hover / when a
# button is the primary action. Nothing is filled with color.
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
        border-right: none;
        box-shadow: none;
    }
    [data-testid="stSidebar"] ~ div,
    [data-testid="stAppViewContainer"] > .main,
    div[data-testid="stMainBlockContainer"] {
        border-left: none !important;
        box-shadow: none !important;
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

    /* ---------- Buttons (generic, whole app) ---------- */
    div[data-testid="stButton"] > button {
        border-radius: 10px;
        font-weight: 500;
        background: transparent;
        color: #f5f5f7;
        border: 1px solid #2a2a34;
        transition: all 0.15s ease;
    }
    div[data-testid="stButton"] > button:hover {
        border-color: #2dd4bf;
        color: #2dd4bf;
        background: transparent;
    }

    /* ---------- Sidebar: main nav-style buttons (secondary look) ---------- */
    /* Used for history items, file rows, use/remove actions */
    section[data-testid="stSidebar"] div[data-testid="stButton"] > button {
        background: transparent;
        border: 1px solid transparent;
        text-align: left;
        justify-content: flex-start;
        color: #cfcfd8 !important;
        font-weight: 500;
        text-transform: none;
        letter-spacing: normal;
        padding: 6px 10px;
        font-size: 0.88rem;
        border-radius: 8px;
    }
    section[data-testid="stSidebar"] div[data-testid="stButton"] > button:hover {
        background: transparent;
        border-color: #2dd4bf;
        color: #2dd4bf !important;
    }

    /* ---------- Sidebar: primary action buttons ---------- */
    /* New Chat / Module / Upload / History / Clear Session — all */
    /* share the same outlined style, no fill, teal border only.  */
    section[data-testid="stSidebar"] div[data-testid="stButton"] > button[kind="primary"] {
        background: transparent;
        color: #f5f5f7 !important;
        border: 1.5px solid #2a2a34;
        border-radius: 10px;
        padding: 9px 10px;
        text-align: center;
        justify-content: center;
        font-weight: 700;
        text-transform: none;
        letter-spacing: normal;
    }
    section[data-testid="stSidebar"] div[data-testid="stButton"] > button[kind="primary"]:hover {
        background: transparent;
        color: #2dd4bf !important;
        border-color: #2dd4bf;
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
        border-bottom: none;
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
        background: #d6231c;
        color: #ffffff;
        font-weight: 800;
        letter-spacing: 1px;
        padding: 7px 14px;
        border-radius: 6px;
        font-size: 0.9rem;
    }

    /* ---------- Floating toggle (plain icon, no box, no tooltip) ---------- */
    .st-key-floating_toggle {
        position: fixed !important;
        top: 14px;
        left: 18px;
        z-index: 1000010;
    }
    .st-key-floating_toggle div[data-testid="stButton"] > button {
        width: 30px;
        height: 30px;
        padding: 0;
        border-radius: 6px;
        background: transparent;
        color: #2dd4bf;
        border: none;
        box-shadow: none;
        font-size: 1.15rem;
        font-weight: 700;
    }
    .st-key-floating_toggle div[data-testid="stButton"] > button:hover {
        color: #5eead4;
        background: transparent;
    }
    .st-key-floating_toggle [data-testid="stTooltipHoverTarget"] + div,
    .st-key-floating_toggle div[role="tooltip"],
    div[data-testid="stTooltipContent"] {
        display: none !important;
    }

    /* ---------- Collapsed sidebar icon rail ---------- */
    .dily-icon-rail div[data-testid="stButton"] > button {
        width: 40px;
        height: 40px;
        padding: 0;
        margin: 0 auto 8px auto;
        border-radius: 8px;
        background: transparent;
        border: 1px solid transparent;
        color: #7a7a89;
        font-size: 1.1rem;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .dily-icon-rail div[data-testid="stButton"] > button:hover {
        background: transparent;
        border-color: #2dd4bf;
        color: #2dd4bf;
    }
    .dily-icon-rail div[data-testid="column"] {
        display: flex;
        justify-content: center;
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

    /* ---------- Login page heading ---------- */
    .dily-login-hero {
        text-align: center;
        max-width: 640px;
        margin: 0 auto;
        padding: 20px 0 6px 0;
    }
    .dily-login-hero h1 {
        font-size: 1.8rem;
        font-weight: 700;
        color: #f5f5f7;
        margin-bottom: 10px;
    }
    .dily-login-hero p.sub {
        color: #9a9aa8;
        font-size: 0.92rem;
    }

    /* ---------- Hero (marketing-style banner) ---------- */
    .dily-hero {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 40px;
        max-width: 1000px;
        margin: 0 auto;
        padding: 46px 8px 34px 8px;
        flex-wrap: wrap;
    }
    .dily-hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: #d6231c;
        color: #ffffff;
        border: none;
        border-radius: 5px;
        padding: 6px 14px;
        font-size: 0.8rem;
        font-weight: 800;
        letter-spacing: 0.03em;
        margin-bottom: 16px;
    }
    .dily-hero-copy { max-width: 480px; }
    .dily-hero-copy h1 {
        font-size: 2.1rem;
        font-weight: 700;
        color: #f5f5f7;
        line-height: 1.2;
        margin-bottom: 14px;
        letter-spacing: -0.02em;
    }
    .dily-hero-copy h1 span {
        color: #2dd4bf;
    }
    .dily-hero-copy p.sub {
        color: #9a9aa8;
        font-size: 0.92rem;
        line-height: 1.55;
        margin-bottom: 20px;
    }
    .dily-hero-graphic {
        width: 220px;
        height: 220px;
        border-radius: 50%;
        background: radial-gradient(circle at 35% 30%, #2dd4bf 0%, #0f766e 60%, #0b3a35 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
        position: relative;
    }
    .dily-hero-graphic .bubble {
        width: 90px;
        height: 66px;
        background: #0b0b0f;
        border-radius: 16px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
    }
    .dily-hero-graphic .dot {
        position: absolute;
        width: 26px;
        height: 26px;
        border-radius: 50%;
        background: #14141a;
        border: 1px solid rgba(45,212,191,0.4);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.8rem;
    }
    .dily-hero-graphic .dot1 { top: -6px; right: 24px; }
    .dily-hero-graphic .dot2 { top: 40px; right: -14px; }
    .dily-hero-graphic .dot3 { bottom: 6px; right: 30px; }

    /* ---------- Chat input ---------- */
    div[data-testid="stBottom"],
    div[data-testid="stBottomBlockContainer"],
    .stBottomBlockContainer,
    div[data-testid="stChatInput"] > div,
    section[data-testid="stChatInputContainer"] {
        background: #0b0b0f !important;
    }
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
    div[data-testid="stChatInput"] textarea,
    div[data-testid="stChatInput"] [contenteditable="true"],
    div[data-testid="stChatInput"] input {
        font-size: 0.92rem;
        color: #f5f5f7 !important;
        -webkit-text-fill-color: #f5f5f7 !important;
        background: transparent !important;
        caret-color: #2dd4bf !important;
    }
    div[data-testid="stChatInput"] textarea::placeholder {
        color: #6b6b78 !important;
        -webkit-text-fill-color: #6b6b78 !important;
    }
    div[data-testid="stChatInput"] button[kind="icon"],
    div[data-testid="stChatInput"] button {
        background: transparent !important;
        border: 1.5px solid #2dd4bf !important;
        border-radius: 50% !important;
    }
    div[data-testid="stChatInput"] button svg {
        fill: #2dd4bf !important;
    }
    div[data-testid="stChatInputFileUploaderButton"] button,
    div[data-testid="stChatInput"] button[title*="attach" i] {
        background: transparent !important;
        color: #2dd4bf !important;
        border: none !important;
        box-shadow: none !important;
    }

    /* ---------- Mic / voice input ---------- */
    /* The mic button lives in its own st.columns() cell placed   */
    /* directly beside the chat input (see the CHAT INPUT section */
    /* in the script) so it's genuinely on the same row — no      */
    /* fixed-position CSS math involved.                          */
    .st-key-mic_beside_btn {
        display: flex;
        align-items: flex-end;
        height: 100%;
        padding-bottom: 4px;
    }
    .st-key-mic_beside_btn div[data-testid="stButton"] > button {
        width: 40px;
        height: 40px;
        padding: 0;
        border-radius: 50%;
        background: transparent;
        border: 1.5px solid #2dd4bf;
        color: #2dd4bf;
        font-size: 1.1rem;
        box-shadow: none;
    }
    .st-key-mic_beside_btn div[data-testid="stButton"] > button:hover {
        color: #5eead4;
        border-color: #5eead4;
        background: transparent;
    }

    div[data-testid="stAudioInput"] {
        max-width: 760px;
        margin: 6px auto 0 auto;
        border-radius: 26px !important;
        border: 1px solid #26262f !important;
        background: #16161c !important;
        padding: 4px 10px;
    }
    div[data-testid="stAudioInput"] button {
        background: transparent !important;
        border: 1.5px solid #2dd4bf !important;
        color: #2dd4bf !important;
        border-radius: 50% !important;
    }
    div[data-testid="stAudioInput"] button:hover {
        color: #5eead4 !important;
        border-color: #5eead4 !important;
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
# FILE UPLOAD HELPERS
# ============================================================
# Extracts plain text from an uploaded file so it can be used
# as context for Q&A. Falls back gracefully if an optional
# parsing library (pypdf / python-docx) is not installed.
# ============================================================

def extract_text_from_upload(uploaded_file):

    name = uploaded_file.name
    ext = name.split(".")[-1].lower() if "." in name else ""

    try:

        if ext == "txt":
            return uploaded_file.read().decode("utf-8", errors="ignore")

        elif ext == "csv":
            df = pd.read_csv(uploaded_file)
            return df.to_csv(index=False)

        elif ext in ("xlsx", "xls"):
            df = pd.read_excel(uploaded_file)
            return df.to_csv(index=False)

        elif ext == "pdf":
            try:
                from pypdf import PdfReader
            except ImportError:
                from PyPDF2 import PdfReader
            reader = PdfReader(uploaded_file)
            return "\n".join(
                (page.extract_text() or "") for page in reader.pages
            )

        elif ext == "docx":
            import docx
            document = docx.Document(uploaded_file)
            return "\n".join(p.text for p in document.paragraphs)

        elif ext in ("png", "jpg", "jpeg"):
            return "[Image file uploaded — no text extracted.]"

        else:
            return "[Unsupported file type for text extraction.]"

    except ImportError as e:
        return (
            f"[Could not read '{name}' — missing library ({e}). "
            f"Install pypdf / python-docx to enable this file type.]"
        )

    except Exception as e:
        return f"[Could not read '{name}': {e}]"


def transcribe_audio(audio_file):
    """Transcribe a recorded audio clip to text using Google's free
    Web Speech API (via the SpeechRecognition package). Returns a
    (text, error_message) tuple — exactly one of the two is set."""

    if not SPEECH_RECOGNITION_AVAILABLE:
        return None, (
            "The `SpeechRecognition` package is not installed. "
            "Run `pip install SpeechRecognition` to enable the mic."
        )

    try:
        recognizer = sr.Recognizer()
        audio_file.seek(0)

        with sr.AudioFile(audio_file) as source:
            audio_data = recognizer.record(source)

        text = recognizer.recognize_google(audio_data)
        return text, None

    except sr.UnknownValueError:
        return None, "Couldn't understand the audio — please try again."

    except sr.RequestError as e:
        return None, f"Speech recognition service error: {e}"

    except Exception as e:
        return None, f"Could not transcribe audio: {e}"


def answer_from_file(prompt, file_text):
    """Answer a question using the active uploaded file as context,
    via Snowflake Cortex COMPLETE. Returns (explanation, sql) to
    match the shape used elsewhere in the app."""

    try:

        context = file_text[:12000]

        cortex_prompt = (
            "You are a helpful assistant. Use the document content "
            "below to answer the question. If the answer is not in "
            "the document, say so clearly.\n\n"
            f"DOCUMENT:\n{context}\n\n"
            f"QUESTION: {prompt}"
        )

        sql = "SELECT SNOWFLAKE.CORTEX.COMPLETE(?, ?) AS RESPONSE"

        result = session.sql(sql, params=["llama3-70b", cortex_prompt]).collect()

        if result:
            return result[0]["RESPONSE"], None

        return "I couldn't generate an answer from the file.", None

    except Exception as e:
        return f"Error answering from the uploaded file.\n\n**Error:** {str(e)}", None


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
        <div class="dily-login-hero">
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

                    conn = snowflake.connector.connect(
                        **connection_parameters
                    )

                    conn.close()

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

if "show_module_selector" not in st.session_state:
    st.session_state.show_module_selector = False

if "selected_module" not in st.session_state:
    st.session_state.selected_module = "Supply Chain"

if "show_files_panel" not in st.session_state:
    st.session_state.show_files_panel = False

if "stored_files" not in st.session_state:
    st.session_state.stored_files = {}

if "selected_file" not in st.session_state:
    st.session_state.selected_file = None

if "active_file" not in st.session_state:
    st.session_state.active_file = None

if "show_history_panel" not in st.session_state:
    st.session_state.show_history_panel = False

if "show_mic_input" not in st.session_state:
    st.session_state.show_mic_input = False

if "last_audio_hash" not in st.session_state:
    st.session_state.last_audio_hash = None


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

    active_file = st.session_state.get("active_file")

    if active_file and active_file in st.session_state.stored_files:

        file_text = st.session_state.stored_files[active_file]["text"]

        return answer_from_file(prompt, file_text)

    return call_cortex_analyst(prompt)


# ============================================================
# TOP NAVBAR + FLOATING SIDEBAR TOGGLE
# ============================================================

st.markdown(
    """
    <div class="dily-navbar"></div>
    """,
    unsafe_allow_html=True
)

with st.container(key="floating_toggle"):

    _toggle_label = "«" if st.session_state.sidebar_open else "»"

    if st.button(_toggle_label, key="floating_toggle_btn"):

        st.session_state.sidebar_open = not st.session_state.sidebar_open
        st.rerun()


# ============================================================
# SIDEBAR
# ============================================================
# Order: New Chat, Module, Upload, History, Clear Session.
# Every button below is styled the same way (outlined, no
# fill — see CSS block above).
# ============================================================

if st.session_state.sidebar_open:

    with st.sidebar:

        # ---------------- New Chat ----------------
        if st.button(
            "➕ New Chat",
            use_container_width=True,
            type="primary",
            key="btn_new_chat"
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

        st.write("")

        # ---------------- Module ----------------
        if st.button(
            "🧩 Module",
            use_container_width=True,
            type="primary",
            key="btn_module"
        ):

            st.session_state.show_module_selector = (
                not st.session_state.show_module_selector
            )

        if st.session_state.show_module_selector:

            module_options = [
                "Supply Chain",
                "Finance (coming soon)",
                "HR (coming soon)"
            ]

            st.session_state.selected_module = st.selectbox(
                "Select module",
                module_options,
                index=module_options.index(
                    st.session_state.selected_module
                ),
                key="module_selectbox",
                label_visibility="collapsed"
            )

        st.write("")

        # ---------------- Upload Files ----------------
        if st.button(
            "📁 Upload Files",
            use_container_width=True,
            type="primary",
            key="btn_upload"
        ):

            st.session_state.show_files_panel = (
                not st.session_state.show_files_panel
            )

        if st.session_state.show_files_panel:

            if not st.session_state.stored_files:

                st.caption(
                    "No files uploaded yet. Use the attach icon "
                    "inside the chat box below to add one."
                )

            else:

                for fname in list(st.session_state.stored_files.keys()):

                    is_active = (fname == st.session_state.active_file)
                    row_label = f"{'✅ ' if is_active else '📄 '}{fname}"

                    if st.button(
                        row_label,
                        key=f"file_row_{fname}",
                        use_container_width=True
                    ):

                        st.session_state.selected_file = (
                            None
                            if st.session_state.selected_file == fname
                            else fname
                        )

                    if st.session_state.selected_file == fname:

                        fcol1, fcol2 = st.columns(2)

                        with fcol1:

                            if st.button(
                                "Use",
                                key=f"use_{fname}",
                                use_container_width=True
                            ):

                                st.session_state.active_file = fname
                                st.session_state.selected_file = None
                                st.rerun()

                        with fcol2:

                            if st.button(
                                "Remove",
                                key=f"remove_{fname}",
                                use_container_width=True
                            ):

                                del st.session_state.stored_files[fname]

                                if st.session_state.active_file == fname:
                                    st.session_state.active_file = None

                                st.session_state.selected_file = None
                                st.rerun()

        st.write("")

        # ---------------- History ----------------
        if st.session_state.show_history_panel:

            past_sessions = [
                (s_id, s_data)
                for s_id, s_data in reversed(
                    list(st.session_state.chat_sessions.items())
                )
                if s_id != st.session_state.current_session_id
            ]

            if not past_sessions:

                st.caption("No past conversations yet.")

            for s_id, s_data in past_sessions:

                label = s_data["title"]

                if len(label) > 20:
                    label = label[:18] + "..."

                if st.button(
                    f"🗨️ {label}",
                    key=f"sess_{s_id}",
                    use_container_width=True
                ):

                    st.session_state.current_session_id = s_id
                    st.rerun()

            st.write("")

        if st.button(
            "🕒 History",
            use_container_width=True,
            type="primary",
            key="btn_history"
        ):

            st.session_state.show_history_panel = (
                not st.session_state.show_history_panel
            )

        st.write("")

        # ---------------- Clear All Sessions ----------------
        if st.button(
            "🗑️ Clear All Sessions",
            use_container_width=True,
            type="primary",
            key="btn_clear_sessions"
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

else:

    # Collapsed state: slim icon-only rail.
    st.markdown(
        """
        <style>
        section[data-testid="stSidebar"] {
            width: 64px !important;
            min-width: 64px !important;
        }
        section[data-testid="stSidebar"] > div:first-child {
            padding-top: 70px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    with st.sidebar:

        st.markdown('<div class="dily-icon-rail">', unsafe_allow_html=True)

        rail_icons = [
            ("➕", "rail_new_chat"),
            ("🧩", "rail_module"),
            ("📁", "rail_upload"),
            ("🕒", "rail_history"),
        ]

        for icon, rail_key in rail_icons:

            if st.button(icon, key=rail_key):

                st.session_state.sidebar_open = True
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)


# ============================================================
# HERO SECTION  (only shown when the current chat is empty)
# ============================================================

if len(messages) == 0:

    st.markdown(
        """
        <div class="dily-hero">
            <div class="dily-hero-copy">
                <span class="dily-hero-badge">DILYTICS</span>
                <h1>Chat with your data<br>using <span>Cortex AI</span></h1>
                <p class="sub">
                    Ask questions in plain English and get instant
                    insights across your business data.
                </p>
            </div>
            <div class="dily-hero-graphic">
                <div class="bubble">💬</div>
                <div class="dot dot1">🔍</div>
                <div class="dot dot2">📁</div>
                <div class="dot dot3">📊</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

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
# ACTIVE FILE INDICATOR
# ============================================================

if st.session_state.active_file:

    st.caption(
        f"📄 Currently answering from file: "
        f"**{st.session_state.active_file}**"
    )


# ============================================================
# MIC / VOICE INPUT
# ============================================================
# The mic button sits in a column directly beside the chat
# input, on the same row — this is done with st.columns(), not
# a CSS overlay, because Streamlit's chat_input can't otherwise
# be embedded next to a real, correctly-aligned button. As a
# side effect, chat_input renders inline here rather than
# auto-sticking to the very bottom of the browser window (that
# floating behaviour only applies when chat_input is called at
# the script's top level, not inside a column).
# ============================================================

mic_prompt = None

if st.session_state.show_mic_input:

    audio_value = st.audio_input(
        "Record your question",
        key="mic_audio",
        label_visibility="collapsed"
    )

    if audio_value is not None:

        audio_bytes = audio_value.getvalue()
        audio_hash = hash(audio_bytes)

        if st.session_state.last_audio_hash != audio_hash:

            st.session_state.last_audio_hash = audio_hash

            with st.spinner("Transcribing..."):
                transcribed_text, transcribe_error = transcribe_audio(audio_value)

            if transcribed_text:
                mic_prompt = transcribed_text
                st.success(f'Heard: "{transcribed_text}"')
            elif transcribe_error:
                st.warning(transcribe_error)


# ============================================================
# CHAT INPUT  (+ mic button on the same row)
# ============================================================

col_input, col_mic = st.columns([0.93, 0.07])

with col_input:

    try:

        chat_result = st.chat_input(
            "Ask me anything about your data...",
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

        user_prompt = st.chat_input(
            "Ask me anything about your data..."
        )
        uploaded_chat_files = []

with col_mic:

    with st.container(key="mic_beside_btn"):

        if st.button(
            "🎤",
            key="btn_mic_toggle",
            help="Voice input",
            use_container_width=True
        ):

            st.session_state.show_mic_input = not st.session_state.show_mic_input
            st.rerun()

user_prompt = (
    user_prompt
    or suggestion_click_prompt
    or mic_prompt
)

if uploaded_chat_files:

    for f in uploaded_chat_files:

        if f.name not in st.session_state.stored_files:

            text_content = extract_text_from_upload(f)

            st.session_state.stored_files[f.name] = {
                "text": text_content,
                "type": f.type
            }

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
