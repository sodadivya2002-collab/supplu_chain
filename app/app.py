import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import snowflake.connector
from snowflake.snowpark import Session

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
    /* Enabled state: lit up with a light-white border so it reads
       clearly as clickable, distinct from the disabled state below. */
    section[data-testid="stSidebar"] div[data-testid="stButton"] > button[kind="primary"]:not(:disabled) {
        border-color: rgba(245, 245, 247, 0.55);
        color: #ffffff !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stButton"] > button[kind="primary"]:hover {
        background: transparent;
        color: #2dd4bf !important;
        border-color: #2dd4bf;
    }
    /* Disabled state: dimmed and non-interactive looking. */
    section[data-testid="stSidebar"] div[data-testid="stButton"] > button[kind="primary"]:disabled {
        background: transparent;
        color: #55555f !important;
        border-color: #22222b;
        opacity: 0.55;
        cursor: not-allowed;
    }
    /* Active-mode highlight: Module / Upload Files buttons get a
       teal glow when that mode is the one currently in effect.
       Both buttons stay fully clickable either way — this is a
       highlight, never a disable. */
    .st-key-module_btn_active div[data-testid="stButton"] > button[kind="primary"],
    .st-key-upload_btn_active div[data-testid="stButton"] > button[kind="primary"] {
        border-color: #2dd4bf !important;
        color: #2dd4bf !important;
        box-shadow: 0 0 0 1px rgba(45, 212, 191, 0.25);
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
    .dily-login-hero .dily-logo-box {
        display: inline-block;
        margin-bottom: 18px;
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

# Each module points at a different Cortex Analyst semantic view.
# Add the secret key here whenever a new module goes live, and
# add the matching value under [snowflake] in your Streamlit
# secrets (e.g. semantic_view_supply_chain = "...",
# semantic_view_inventory = "...").
MODULE_SEMANTIC_VIEW_KEYS = {
    "Supply Chain": "semantic_view_supply_chain",
    "Inventory": "semantic_view_inventory",
}


def call_cortex_analyst(prompt, module="Supply Chain"):

    try:

        secret_key = MODULE_SEMANTIC_VIEW_KEYS.get(
            module,
            "semantic_view"
        )

        semantic_view = st.secrets["snowflake"].get(
            secret_key,
            ""
        )

        # Backward compatibility: older deployments only ever set
        # `semantic_view` (no module suffix) for Supply Chain.
        if not semantic_view and module == "Supply Chain":

            semantic_view = st.secrets["snowflake"].get(
                "semantic_view",
                ""
            )

        if not semantic_view:
            return (
                f"Cortex Analyst is not configured yet for the "
                f"**{module}** module. Please add `{secret_key}` "
                f"under `[snowflake]` in your Streamlit secrets.",
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
# Extracts data from an uploaded file. Tabular files (csv/xlsx/xls)
# are parsed into a full pandas DataFrame — nothing is truncated —
# so questions can be answered with real SQL over the WHOLE file
# instead of guesswork over a text snippet. Non-tabular files
# (txt/pdf/docx) fall back to plain extracted text.
# ============================================================

def extract_data_from_upload(uploaded_file):
    """Returns (text, dataframe). `dataframe` is a full pandas
    DataFrame for tabular files (csv/xlsx/xls), or None otherwise.
    `text` is always a string (used as a text preview / fallback
    context for non-tabular files)."""

    name = uploaded_file.name
    ext = name.split(".")[-1].lower() if "." in name else ""

    try:

        if ext == "txt":
            return uploaded_file.read().decode("utf-8", errors="ignore"), None

        elif ext == "csv":
            df = pd.read_csv(uploaded_file)
            return df.to_csv(index=False), df

        elif ext in ("xlsx", "xls"):
            df = pd.read_excel(uploaded_file)
            return df.to_csv(index=False), df

        elif ext == "pdf":
            try:
                from pypdf import PdfReader
            except ImportError:
                from PyPDF2 import PdfReader
            reader = PdfReader(uploaded_file)
            return "\n".join(
                (page.extract_text() or "") for page in reader.pages
            ), None

        elif ext == "docx":
            import docx
            document = docx.Document(uploaded_file)
            return "\n".join(p.text for p in document.paragraphs), None

        elif ext in ("png", "jpg", "jpeg"):
            return "[Image file uploaded — no text extracted.]", None

        else:
            return "[Unsupported file type for text extraction.]", None

    except ImportError as e:
        return (
            f"[Could not read '{name}' — missing library ({e}). "
            f"Install pypdf / python-docx to enable this file type.]",
            None
        )

    except Exception as e:
        return f"[Could not read '{name}': {e}]", None


def _call_groq_json(system_prompt, user_message):
    """Calls the Groq chat completions API and returns the raw
    response text (expected to be a JSON object). Raises on
    network/HTTP errors so callers can report them."""

    groq_api_key = st.secrets.get("groq", {}).get("api_key", "")

    if not groq_api_key:
        raise RuntimeError(
            "File Q&A is not configured yet. Please add `api_key` "
            "under a `[groq]` section in your Streamlit secrets "
            "(get a free key at console.groq.com)."
        )

    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {groq_api_key}",
        "Content-Type": "application/json"
    }

    request_body = {
        "model": "openai/gpt-oss-20b",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        "temperature": 0.1
    }

    response = requests.post(
        url,
        headers=headers,
        json=request_body,
        timeout=60
    )

    if response.status_code != 200:
        try:
            error_json = response.json()
            error_message = (
                error_json.get("error", {}).get("message")
                or response.text
            )
        except Exception:
            error_message = response.text

        raise RuntimeError(error_message)

    result = response.json()

    return (
        result.get("choices", [{}])[0]
        .get("message", {})
        .get("content", "")
        .strip()
    )


def _parse_json_response(raw_text):
    """Best-effort parse of a JSON object out of an LLM response,
    stripping markdown code fences if present."""

    import json

    cleaned = raw_text.strip()

    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:]
        cleaned = cleaned.strip()

    return json.loads(cleaned)


def answer_from_file(prompt, fname):
    """Answer a question about the active uploaded file, via the
    Groq API. Tabular files (csv/xlsx/xls) are queried with real
    SQL over the FULL dataset (loaded into an in-memory SQLite
    table) so KPI-style questions return the same shape as the
    Cortex Analyst path: (explanation, sql, result_dataframe).
    Non-tabular files fall back to a plain text-context answer."""

    file_data = st.session_state.stored_files.get(fname, {})
    df = file_data.get("df")

    # ---------------- Tabular file: text-to-SQL over SQLite ----------------
    if df is not None:

        try:

            import sqlite3

            total_rows = len(df)

            schema_lines = [
                f"- {col} ({str(dtype)})"
                for col, dtype in df.dtypes.items()
            ]
            schema_text = "\n".join(schema_lines)

            sample_csv = df.head(5).to_csv(index=False)

            system_prompt = (
                "You are a data analyst. You have access to a SQLite "
                "table named `uploaded_data` with this schema:\n"
                f"{schema_text}\n\n"
                f"The table has exactly {total_rows} rows in total "
                "(not just the sample below). Here are the first 5 "
                f"rows as a sample of the data format:\n{sample_csv}\n\n"
                "Given the user's question, respond with ONLY a JSON "
                "object (no markdown, no code fences) with exactly "
                "two fields:\n"
                '  "explanation": a short natural-language summary of '
                "what the answer shows.\n"
                '  "sql": a single valid SQLite SELECT query against '
                "`uploaded_data` that answers the question using the "
                "FULL table (never assume only the sample rows exist). "
                "If the question is a greeting or cannot be answered "
                "with a query, set \"sql\" to null and just answer in "
                '"explanation".'
            )

            raw_response = _call_groq_json(system_prompt, prompt)

            try:
                parsed = _parse_json_response(raw_response)
            except Exception:
                # Model didn't return clean JSON — treat the whole
                # response as the explanation with no query.
                return raw_response, None, None

            explanation = parsed.get("explanation", "").strip()
            sql_query = parsed.get("sql")

            if not sql_query:
                return (
                    explanation or "I couldn't generate an answer from the file.",
                    None,
                    None
                )

            conn = sqlite3.connect(":memory:")

            try:
                df.to_sql("uploaded_data", conn, index=False, if_exists="replace")
                result_df = pd.read_sql_query(sql_query, conn)
            finally:
                conn.close()

            return explanation or "Here is the result from your file.", sql_query, result_df

        except RuntimeError as e:
            return f"Error answering from the uploaded file.\n\n**Error:** {str(e)}", None, None

        except Exception as e:
            return (
                "The generated query could not be run against the "
                f"file.\n\n**Error:** {str(e)}",
                None,
                None
            )

    # ---------------- Non-tabular file: plain text context ----------------
    try:

        file_text = file_data.get("text", "")
        context = file_text[:60000]

        system_prompt = (
            "You are a helpful assistant. Use the document content "
            "provided by the user to answer their question. If the "
            "answer is not in the document, say so clearly."
        )

        user_message = (
            f"DOCUMENT:\n{context}\n\n"
            f"QUESTION: {prompt}"
        )

        answer = _call_groq_json(system_prompt, user_message)

        if answer:
            return answer, None, None

        return "I couldn't generate an answer from the file.", None, None

    except RuntimeError as e:
        return f"Error answering from the uploaded file.\n\n**Error:** {str(e)}", None, None

    except Exception as e:
        return f"Error answering from the uploaded file.\n\n**Error:** {str(e)}", None, None


def generate_file_overview(fname):
    """Automatically summarizes a freshly uploaded file. For
    tabular files the numbers are computed directly from the real
    data with pandas (row/column counts, missing values, numeric
    ranges) — not asked of an LLM — so nothing is guessed. Returns
    (explanation, sql, preview_df)."""

    file_data = st.session_state.stored_files.get(fname, {})
    df = file_data.get("df")

    if df is None:
        # Non-tabular file — ask the LLM to summarize the extracted text.
        return answer_from_file(
            "Give me an overview and the key observations about "
            "this document.",
            fname
        )

    total_rows = len(df)
    total_cols = len(df.columns)

    lines = [
        f"**{fname}** — {total_rows:,} rows, {total_cols} columns.",
        "",
        "**Columns:**"
    ]

    for col in df.columns:
        dtype = df[col].dtype
        null_count = int(df[col].isna().sum())
        null_note = f", {null_count} missing" if null_count else ""
        lines.append(f"- `{col}` ({dtype}){null_note}")

    numeric_cols = df.select_dtypes(include="number").columns.tolist()

    if numeric_cols:

        lines.append("")
        lines.append("**Numeric summary:**")

        for col in numeric_cols:
            series = df[col].dropna()
            if series.empty:
                continue
            lines.append(
                f"- `{col}`: min {series.min():,.2f}, "
                f"avg {series.mean():,.2f}, max {series.max():,.2f}"
            )

    categorical_cols = df.select_dtypes(include="object").columns.tolist()

    if categorical_cols:

        lines.append("")
        lines.append("**Categorical columns:**")

        for col in categorical_cols[:5]:
            distinct = df[col].nunique(dropna=True)
            top_value = (
                df[col].value_counts().idxmax()
                if distinct > 0 else "—"
            )
            lines.append(
                f"- `{col}`: {distinct} distinct values, "
                f"most common: \"{top_value}\""
            )

    explanation = "\n".join(lines)
    preview_df = df.head(10)

    return explanation, None, preview_df


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

    st.write("")
    st.write("")

    st.markdown(
        """
        <div class="dily-login-hero">
            <h1>Welcome to Dilytics Chatbot</h1>
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
    st.session_state.selected_module = "None"

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


def show_query_result(sql_query, df, key_prefix):
    """Renders the shared Generated-SQL / Data / Chart layout used
    for both the Cortex Analyst path and the file-upload SQL path,
    so both feel identical to the user."""

    if sql_query:

        with st.expander(
            "Generated SQL",
            expanded=False
        ):

            st.code(
                sql_query,
                language="sql"
            )

    if df is None:
        return

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
                key_prefix=key_prefix
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

MODULE_GREETING_SUGGESTIONS = {
    "Supply Chain": [
        "What is the total purchase order count?",
        "How many shipments are currently in transit?",
        "Which suppliers are high risk?",
        "What are the top products by ordered value?",
        "What is the supplier on-time delivery percentage?",
    ],
    "Inventory": [
        "What is the total available inventory as of the latest snapshot?",
        "What is the total quantity of inventory currently on hand?",
        "How many products and warehouses are out of stock?",
        "What is the total inventory value by product category?",
        "How many products need to be reordered?",
    ],
    "None": [],
}

# Backward-compatible alias — kept in case anything else references it.
GREETING_SUGGESTIONS = MODULE_GREETING_SUGGESTIONS["Supply Chain"]

MODULE_HELP_TEXT = {
    "Supply Chain": """
You can ask me questions about **Supply Chain data**.

Try things like:

- What is the total purchase order count?
- What is the total ordered value?
- How many shipments are currently in transit?
- Which suppliers are high risk?
- What is the supplier on-time delivery percentage?
- What are the top products by ordered value?

Ask a question in your own words — Cortex Analyst will turn it
into a query against the supply chain semantic view.
""",
    "Inventory": """
You can ask me questions about **Inventory data**.

Try things like:

- What is the total available inventory as of the latest snapshot?
- What is the total quantity of inventory currently on hand?
- How many products and warehouses are out of stock?
- What is the total inventory value by product category?
- How many products need to be reordered?
- What are the top 10 products by inventory value?

Ask a question in your own words — Cortex Analyst will turn it
into a query against the inventory semantic view.
""",
    "None": """
No module is selected yet, and no file is active.

- To ask about **Supply Chain** or **Inventory** data, click
  **🧩 Module** in the sidebar and pick one.
- To ask about your own data, click **📁 Upload Files** and
  attach a file — the Module option is disabled automatically
  while a file is active.
""",
}


def generate_sql_from_prompt(prompt):
    """Returns (explanation, sql, result_df).

    result_df is pre-computed data (used for the file-upload path,
    which runs its own SQL engine); it's None for the Cortex
    Analyst path, where the caller executes `sql` against the
    live Snowflake session instead."""

    p = prompt.lower().strip()

    module = st.session_state.get("selected_module", "None")
    active_file = st.session_state.get("active_file")

    if p in GREETING_PHRASES:

        if active_file:
            greeting_subject = f"your uploaded file **{active_file}**"
        elif module != "None":
            greeting_subject = f"your **{module}** data"
        else:
            greeting_subject = "your data"

        return (
            f"Hi there! 👋 Ask me anything about {greeting_subject}.\n\n"
            "Here are a few things you can try:",
            None,
            None
        )

    if (
        "what can i ask" in p
        or "what questions" in p
        or "what can you do" in p
        or "examples" in p
        or p == "help"
    ):

        if active_file:
            return (
                f"You can ask me questions about your uploaded file "
                f"**{active_file}** — try things like \"how many "
                "records are there\", \"summarize this file\", or "
                "ask about any KPI in the data.",
                None,
                None
            )

        return (
            MODULE_HELP_TEXT.get(
                module,
                MODULE_HELP_TEXT["None"]
            ),
            None,
            None
        )

    # File Q&A takes priority whenever a file is active — the
    # sidebar disables Module selection while a file is active,
    # so the two are mutually exclusive.
    if active_file and active_file in st.session_state.stored_files:

        explanation, sql_query, result_df = answer_from_file(prompt, active_file)

        return explanation, sql_query, result_df

    if module == "None":

        return (
            "Please select a module (**Supply Chain** or "
            "**Inventory**) from the **🧩 Module** menu in the "
            "sidebar, or upload a file, before asking a data "
            "question.",
            None,
            None
        )

    explanation, sql_query = call_cortex_analyst(prompt, module)

    return explanation, sql_query, None


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
        # File Q&A and Module (Cortex Analyst) Q&A are mutually
        # exclusive, but the Module button is always clickable —
        # picking a module here switches mode away from the active
        # file automatically. The currently-active mode is shown
        # with a highlighted border instead of disabling anything.
        module_is_current_mode = (
            not st.session_state.active_file
            and st.session_state.selected_module != "None"
        )

        with st.container(
            key=(
                "module_btn_active"
                if module_is_current_mode
                else "module_btn_inactive"
            )
        ):

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
                "None",
                "Supply Chain",
                "Inventory"
            ]

            current_index = (
                module_options.index(st.session_state.selected_module)
                if st.session_state.selected_module in module_options
                else 0
            )

            new_module = st.selectbox(
                "Select module",
                module_options,
                index=current_index,
                key="module_selectbox",
                label_visibility="collapsed"
            )

            if new_module != st.session_state.selected_module:

                st.session_state.selected_module = new_module

                # Picking an actual module switches mode away from
                # any active file.
                if new_module != "None" and st.session_state.active_file:

                    st.session_state.active_file = None
                    st.rerun()

        st.write("")

        # ---------------- Upload Files ----------------
        file_is_current_mode = bool(st.session_state.active_file)

        with st.container(
            key=(
                "upload_btn_active"
                if file_is_current_mode
                else "upload_btn_inactive"
            )
        ):

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

                                # Using a file switches mode away
                                # from any selected module.
                                st.session_state.selected_module = "None"

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
        if st.button(
            "🕒 History",
            use_container_width=True,
            type="primary",
            key="btn_history"
        ):

            st.session_state.show_history_panel = (
                not st.session_state.show_history_panel
            )

        if st.session_state.show_history_panel:

            all_sessions = list(
                reversed(list(st.session_state.chat_sessions.items()))
            )

            # Only hide *other* empty sessions — always show the
            # current one so it's clear the app is tracking it.
            visible_sessions = [
                (s_id, s_data)
                for s_id, s_data in all_sessions
                if s_data["messages"] or s_id == st.session_state.current_session_id
            ]

            if not visible_sessions:

                st.caption("No conversations yet.")

            for s_id, s_data in visible_sessions:

                label = s_data["title"]

                if len(label) > 20:
                    label = label[:18] + "..."

                is_current = (s_id == st.session_state.current_session_id)
                icon = "✅" if is_current else "🗨️"

                if st.button(
                    f"{icon} {label}",
                    key=f"sess_{s_id}",
                    use_container_width=True
                ):

                    st.session_state.current_session_id = s_id
                    st.rerun()

        st.write("")

        # ---------------- Clear All Sessions ----------------
        if st.button(
            "🗑️ Clear All Sessions",
            use_container_width=True,
            type="primary",
            key="btn_clear_sessions"
        ):

            # Full reset — chats, uploaded files, active file, and
            # module selection all go back to their fresh-start
            # defaults, not just the chat history.
            st.session_state.chat_sessions = {}
            st.session_state.stored_files = {}
            st.session_state.active_file = None
            st.session_state.selected_file = None
            st.session_state.selected_module = "None"
            st.session_state.show_module_selector = False
            st.session_state.show_files_panel = False
            st.session_state.show_history_panel = False

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
            ("🗑️", "rail_clear_sessions"),
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

    _selected_module = st.session_state.get("selected_module", "None")
    _active_file = st.session_state.get("active_file")

    if _active_file:
        _hero_module = _active_file
    elif _selected_module != "None":
        _hero_module = _selected_module
    else:
        _hero_module = "Data"

    st.markdown(
        f"""
        <div class="dily-hero">
            <div class="dily-hero-copy">
                <span class="dily-hero-badge">DILYTICS</span>
                <h1>Chat with your {_hero_module}<br>data using <span>Cortex AI</span></h1>
                <p class="sub">
                    Ask questions and get instant
                    insights across your {_hero_module.lower()} data.
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
# CHAT INPUT
# ============================================================

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

user_prompt = (
    user_prompt
    or suggestion_click_prompt
)

if uploaded_chat_files:

    typed_prompt = (user_prompt or "").strip()

    for f in uploaded_chat_files:

        if f.name not in st.session_state.stored_files:

            text_content, parsed_df = extract_data_from_upload(f)

            st.session_state.stored_files[f.name] = {
                "text": text_content,
                "type": f.type,
                "df": parsed_df
            }

        # Newly uploaded file becomes the active file automatically —
        # file Q&A and Module Q&A are mutually exclusive, so this
        # also disables the Module button (see sidebar section).
        st.session_state.active_file = f.name

    file_names = ", ".join(f.name for f in uploaded_chat_files)
    attach_note = f"(Attached: {file_names})"

    if typed_prompt:

        # A question was typed alongside the upload — treat it as
        # a real question and let it flow through the normal
        # PROCESS QUESTION section below.
        user_prompt = f"{typed_prompt}\n\n{attach_note}"

    else:

        # No question was typed — automatically analyze the file
        # and post the observations as an assistant turn, without
        # waiting for the user to ask anything.
        if len(messages) == 0:

            st.session_state.chat_sessions[
                current_id
            ]["title"] = file_names[:25] + (
                "..." if len(file_names) > 25 else ""
            )

        messages.append(
            {
                "role": "user",
                "content": attach_note
            }
        )

        with st.chat_message("user"):
            st.markdown(attach_note)

        last_uploaded = uploaded_chat_files[-1].name

        with st.chat_message("assistant"):

            explanation, sql_query, preview_df = generate_file_overview(
                last_uploaded
            )

            st.markdown(explanation)

            show_query_result(
                sql_query,
                preview_df,
                key_prefix=f"overview_{current_id}"
            )

        messages.append(
            {
                "role": "assistant",
                "content": explanation,
                "sql": sql_query,
                "data": preview_df,
                "suggestions": None
            }
        )

        user_prompt = None


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

        explanation, sql_query, file_df = (
            generate_sql_from_prompt(
                user_prompt
            )
        )

        is_greeting_prompt = (
            user_prompt.strip().lower()
            in GREETING_PHRASES
        )

        suggestions = (
            MODULE_GREETING_SUGGESTIONS.get(
                st.session_state.get("selected_module", "None"),
                MODULE_GREETING_SUGGESTIONS["None"]
            )
            if is_greeting_prompt
            else None
        )

        st.markdown(
            explanation
        )

        df = None

        if file_df is not None:

            # File-Q&A path: the SQL was already generated AND
            # executed against the uploaded file's in-memory table
            # inside answer_from_file(). Just render it — same
            # Generated SQL / Data / Chart layout as the Cortex
            # Analyst path below.
            df = file_df

            show_query_result(
                sql_query,
                df,
                key_prefix=f"live_{current_id}"
            )

        elif sql_query:

            # Cortex Analyst path: sql_query needs to be executed
            # against the live Snowflake session.
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
    /* Enabled state: lit up with a light-white border so it reads
       clearly as clickable, distinct from the disabled state below. */
    section[data-testid="stSidebar"] div[data-testid="stButton"] > button[kind="primary"]:not(:disabled) {
        border-color: rgba(245, 245, 247, 0.55);
        color: #ffffff !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stButton"] > button[kind="primary"]:hover {
        background: transparent;
        color: #2dd4bf !important;
        border-color: #2dd4bf;
    }
    /* Disabled state: dimmed and non-interactive looking. */
    section[data-testid="stSidebar"] div[data-testid="stButton"] > button[kind="primary"]:disabled {
        background: transparent;
        color: #55555f !important;
        border-color: #22222b;
        opacity: 0.55;
        cursor: not-allowed;
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
    .dily-login-hero .dily-logo-box {
        display: inline-block;
        margin-bottom: 18px;
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

# Each module points at a different Cortex Analyst semantic view.
# Add the secret key here whenever a new module goes live, and
# add the matching value under [snowflake] in your Streamlit
# secrets (e.g. semantic_view_supply_chain = "...",
# semantic_view_inventory = "...").
MODULE_SEMANTIC_VIEW_KEYS = {
    "Supply Chain": "semantic_view_supply_chain",
    "Inventory": "semantic_view_inventory",
}


def call_cortex_analyst(prompt, module="Supply Chain"):

    try:

        secret_key = MODULE_SEMANTIC_VIEW_KEYS.get(
            module,
            "semantic_view"
        )

        semantic_view = st.secrets["snowflake"].get(
            secret_key,
            ""
        )

        # Backward compatibility: older deployments only ever set
        # `semantic_view` (no module suffix) for Supply Chain.
        if not semantic_view and module == "Supply Chain":

            semantic_view = st.secrets["snowflake"].get(
                "semantic_view",
                ""
            )

        if not semantic_view:
            return (
                f"Cortex Analyst is not configured yet for the "
                f"**{module}** module. Please add `{secret_key}` "
                f"under `[snowflake]` in your Streamlit secrets.",
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
# Extracts data from an uploaded file. Tabular files (csv/xlsx/xls)
# are parsed into a full pandas DataFrame — nothing is truncated —
# so questions can be answered with real SQL over the WHOLE file
# instead of guesswork over a text snippet. Non-tabular files
# (txt/pdf/docx) fall back to plain extracted text.
# ============================================================

def extract_data_from_upload(uploaded_file):
    """Returns (text, dataframe). `dataframe` is a full pandas
    DataFrame for tabular files (csv/xlsx/xls), or None otherwise.
    `text` is always a string (used as a text preview / fallback
    context for non-tabular files)."""

    name = uploaded_file.name
    ext = name.split(".")[-1].lower() if "." in name else ""

    try:

        if ext == "txt":
            return uploaded_file.read().decode("utf-8", errors="ignore"), None

        elif ext == "csv":
            df = pd.read_csv(uploaded_file)
            return df.to_csv(index=False), df

        elif ext in ("xlsx", "xls"):
            df = pd.read_excel(uploaded_file)
            return df.to_csv(index=False), df

        elif ext == "pdf":
            try:
                from pypdf import PdfReader
            except ImportError:
                from PyPDF2 import PdfReader
            reader = PdfReader(uploaded_file)
            return "\n".join(
                (page.extract_text() or "") for page in reader.pages
            ), None

        elif ext == "docx":
            import docx
            document = docx.Document(uploaded_file)
            return "\n".join(p.text for p in document.paragraphs), None

        elif ext in ("png", "jpg", "jpeg"):
            return "[Image file uploaded — no text extracted.]", None

        else:
            return "[Unsupported file type for text extraction.]", None

    except ImportError as e:
        return (
            f"[Could not read '{name}' — missing library ({e}). "
            f"Install pypdf / python-docx to enable this file type.]",
            None
        )

    except Exception as e:
        return f"[Could not read '{name}': {e}]", None


def _call_groq_json(system_prompt, user_message):
    """Calls the Groq chat completions API and returns the raw
    response text (expected to be a JSON object). Raises on
    network/HTTP errors so callers can report them."""

    groq_api_key = st.secrets.get("groq", {}).get("api_key", "")

    if not groq_api_key:
        raise RuntimeError(
            "File Q&A is not configured yet. Please add `api_key` "
            "under a `[groq]` section in your Streamlit secrets "
            "(get a free key at console.groq.com)."
        )

    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {groq_api_key}",
        "Content-Type": "application/json"
    }

    request_body = {
        "model": "openai/gpt-oss-20b",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        "temperature": 0.1
    }

    response = requests.post(
        url,
        headers=headers,
        json=request_body,
        timeout=60
    )

    if response.status_code != 200:
        try:
            error_json = response.json()
            error_message = (
                error_json.get("error", {}).get("message")
                or response.text
            )
        except Exception:
            error_message = response.text

        raise RuntimeError(error_message)

    result = response.json()

    return (
        result.get("choices", [{}])[0]
        .get("message", {})
        .get("content", "")
        .strip()
    )


def _parse_json_response(raw_text):
    """Best-effort parse of a JSON object out of an LLM response,
    stripping markdown code fences if present."""

    import json

    cleaned = raw_text.strip()

    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:]
        cleaned = cleaned.strip()

    return json.loads(cleaned)


def answer_from_file(prompt, fname):
    """Answer a question about the active uploaded file, via the
    Groq API. Tabular files (csv/xlsx/xls) are queried with real
    SQL over the FULL dataset (loaded into an in-memory SQLite
    table) so KPI-style questions return the same shape as the
    Cortex Analyst path: (explanation, sql, result_dataframe).
    Non-tabular files fall back to a plain text-context answer."""

    file_data = st.session_state.stored_files.get(fname, {})
    df = file_data.get("df")

    # ---------------- Tabular file: text-to-SQL over SQLite ----------------
    if df is not None:

        try:

            import sqlite3

            total_rows = len(df)

            schema_lines = [
                f"- {col} ({str(dtype)})"
                for col, dtype in df.dtypes.items()
            ]
            schema_text = "\n".join(schema_lines)

            sample_csv = df.head(5).to_csv(index=False)

            system_prompt = (
                "You are a data analyst. You have access to a SQLite "
                "table named `uploaded_data` with this schema:\n"
                f"{schema_text}\n\n"
                f"The table has exactly {total_rows} rows in total "
                "(not just the sample below). Here are the first 5 "
                f"rows as a sample of the data format:\n{sample_csv}\n\n"
                "Given the user's question, respond with ONLY a JSON "
                "object (no markdown, no code fences) with exactly "
                "two fields:\n"
                '  "explanation": a short natural-language summary of '
                "what the answer shows.\n"
                '  "sql": a single valid SQLite SELECT query against '
                "`uploaded_data` that answers the question using the "
                "FULL table (never assume only the sample rows exist). "
                "If the question is a greeting or cannot be answered "
                "with a query, set \"sql\" to null and just answer in "
                '"explanation".'
            )

            raw_response = _call_groq_json(system_prompt, prompt)

            try:
                parsed = _parse_json_response(raw_response)
            except Exception:
                # Model didn't return clean JSON — treat the whole
                # response as the explanation with no query.
                return raw_response, None, None

            explanation = parsed.get("explanation", "").strip()
            sql_query = parsed.get("sql")

            if not sql_query:
                return (
                    explanation or "I couldn't generate an answer from the file.",
                    None,
                    None
                )

            conn = sqlite3.connect(":memory:")

            try:
                df.to_sql("uploaded_data", conn, index=False, if_exists="replace")
                result_df = pd.read_sql_query(sql_query, conn)
            finally:
                conn.close()

            return explanation or "Here is the result from your file.", sql_query, result_df

        except RuntimeError as e:
            return f"Error answering from the uploaded file.\n\n**Error:** {str(e)}", None, None

        except Exception as e:
            return (
                "The generated query could not be run against the "
                f"file.\n\n**Error:** {str(e)}",
                None,
                None
            )

    # ---------------- Non-tabular file: plain text context ----------------
    try:

        file_text = file_data.get("text", "")
        context = file_text[:60000]

        system_prompt = (
            "You are a helpful assistant. Use the document content "
            "provided by the user to answer their question. If the "
            "answer is not in the document, say so clearly."
        )

        user_message = (
            f"DOCUMENT:\n{context}\n\n"
            f"QUESTION: {prompt}"
        )

        answer = _call_groq_json(system_prompt, user_message)

        if answer:
            return answer, None, None

        return "I couldn't generate an answer from the file.", None, None

    except RuntimeError as e:
        return f"Error answering from the uploaded file.\n\n**Error:** {str(e)}", None, None

    except Exception as e:
        return f"Error answering from the uploaded file.\n\n**Error:** {str(e)}", None, None


def generate_file_overview(fname):
    """Automatically summarizes a freshly uploaded file. For
    tabular files the numbers are computed directly from the real
    data with pandas (row/column counts, missing values, numeric
    ranges) — not asked of an LLM — so nothing is guessed. Returns
    (explanation, sql, preview_df)."""

    file_data = st.session_state.stored_files.get(fname, {})
    df = file_data.get("df")

    if df is None:
        # Non-tabular file — ask the LLM to summarize the extracted text.
        return answer_from_file(
            "Give me an overview and the key observations about "
            "this document.",
            fname
        )

    total_rows = len(df)
    total_cols = len(df.columns)

    lines = [
        f"**{fname}** — {total_rows:,} rows, {total_cols} columns.",
        "",
        "**Columns:**"
    ]

    for col in df.columns:
        dtype = df[col].dtype
        null_count = int(df[col].isna().sum())
        null_note = f", {null_count} missing" if null_count else ""
        lines.append(f"- `{col}` ({dtype}){null_note}")

    numeric_cols = df.select_dtypes(include="number").columns.tolist()

    if numeric_cols:

        lines.append("")
        lines.append("**Numeric summary:**")

        for col in numeric_cols:
            series = df[col].dropna()
            if series.empty:
                continue
            lines.append(
                f"- `{col}`: min {series.min():,.2f}, "
                f"avg {series.mean():,.2f}, max {series.max():,.2f}"
            )

    categorical_cols = df.select_dtypes(include="object").columns.tolist()

    if categorical_cols:

        lines.append("")
        lines.append("**Categorical columns:**")

        for col in categorical_cols[:5]:
            distinct = df[col].nunique(dropna=True)
            top_value = (
                df[col].value_counts().idxmax()
                if distinct > 0 else "—"
            )
            lines.append(
                f"- `{col}`: {distinct} distinct values, "
                f"most common: \"{top_value}\""
            )

    explanation = "\n".join(lines)
    preview_df = df.head(10)

    return explanation, None, preview_df


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

    st.write("")
    st.write("")

    st.markdown(
        """
        <div class="dily-login-hero">
            <h1>Welcome to Dilytics Chatbot</h1>
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
    st.session_state.selected_module = "None"

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


def show_query_result(sql_query, df, key_prefix):
    """Renders the shared Generated-SQL / Data / Chart layout used
    for both the Cortex Analyst path and the file-upload SQL path,
    so both feel identical to the user."""

    if sql_query:

        with st.expander(
            "Generated SQL",
            expanded=False
        ):

            st.code(
                sql_query,
                language="sql"
            )

    if df is None:
        return

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
                key_prefix=key_prefix
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

MODULE_GREETING_SUGGESTIONS = {
    "Supply Chain": [
        "What is the total purchase order count?",
        "How many shipments are currently in transit?",
        "Which suppliers are high risk?",
        "What are the top products by ordered value?",
        "What is the supplier on-time delivery percentage?",
    ],
    "Inventory": [
        "What is the total available inventory as of the latest snapshot?",
        "What is the total quantity of inventory currently on hand?",
        "How many products and warehouses are out of stock?",
        "What is the total inventory value by product category?",
        "How many products need to be reordered?",
    ],
    "None": [],
}

# Backward-compatible alias — kept in case anything else references it.
GREETING_SUGGESTIONS = MODULE_GREETING_SUGGESTIONS["Supply Chain"]

MODULE_HELP_TEXT = {
    "Supply Chain": """
You can ask me questions about **Supply Chain data**.

Try things like:

- What is the total purchase order count?
- What is the total ordered value?
- How many shipments are currently in transit?
- Which suppliers are high risk?
- What is the supplier on-time delivery percentage?
- What are the top products by ordered value?

Ask a question in your own words — Cortex Analyst will turn it
into a query against the supply chain semantic view.
""",
    "Inventory": """
You can ask me questions about **Inventory data**.

Try things like:

- What is the total available inventory as of the latest snapshot?
- What is the total quantity of inventory currently on hand?
- How many products and warehouses are out of stock?
- What is the total inventory value by product category?
- How many products need to be reordered?
- What are the top 10 products by inventory value?

Ask a question in your own words — Cortex Analyst will turn it
into a query against the inventory semantic view.
""",
    "None": """
No module is selected yet, and no file is active.

- To ask about **Supply Chain** or **Inventory** data, click
  **🧩 Module** in the sidebar and pick one.
- To ask about your own data, click **📁 Upload Files** and
  attach a file — the Module option is disabled automatically
  while a file is active.
""",
}


def generate_sql_from_prompt(prompt):
    """Returns (explanation, sql, result_df).

    result_df is pre-computed data (used for the file-upload path,
    which runs its own SQL engine); it's None for the Cortex
    Analyst path, where the caller executes `sql` against the
    live Snowflake session instead."""

    p = prompt.lower().strip()

    module = st.session_state.get("selected_module", "None")
    active_file = st.session_state.get("active_file")

    if p in GREETING_PHRASES:

        if active_file:
            greeting_subject = f"your uploaded file **{active_file}**"
        elif module != "None":
            greeting_subject = f"your **{module}** data"
        else:
            greeting_subject = "your data"

        return (
            f"Hi there! 👋 Ask me anything about {greeting_subject}.\n\n"
            "Here are a few things you can try:",
            None,
            None
        )

    if (
        "what can i ask" in p
        or "what questions" in p
        or "what can you do" in p
        or "examples" in p
        or p == "help"
    ):

        if active_file:
            return (
                f"You can ask me questions about your uploaded file "
                f"**{active_file}** — try things like \"how many "
                "records are there\", \"summarize this file\", or "
                "ask about any KPI in the data.",
                None,
                None
            )

        return (
            MODULE_HELP_TEXT.get(
                module,
                MODULE_HELP_TEXT["None"]
            ),
            None,
            None
        )

    # File Q&A takes priority whenever a file is active — the
    # sidebar disables Module selection while a file is active,
    # so the two are mutually exclusive.
    if active_file and active_file in st.session_state.stored_files:

        explanation, sql_query, result_df = answer_from_file(prompt, active_file)

        return explanation, sql_query, result_df

    if module == "None":

        return (
            "Please select a module (**Supply Chain** or "
            "**Inventory**) from the **🧩 Module** menu in the "
            "sidebar, or upload a file, before asking a data "
            "question.",
            None,
            None
        )

    explanation, sql_query = call_cortex_analyst(prompt, module)

    return explanation, sql_query, None


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
        # Disabled while a file is active — file Q&A and module
        # (Cortex Analyst) Q&A are mutually exclusive.
        module_disabled = bool(st.session_state.active_file)

        if st.button(
            "🧩 Module",
            use_container_width=True,
            type="primary",
            key="btn_module",
            disabled=module_disabled
        ):

            st.session_state.show_module_selector = (
                not st.session_state.show_module_selector
            )

        if not module_disabled and st.session_state.show_module_selector:

            module_options = [
                "None",
                "Supply Chain",
                "Inventory"
            ]

            current_index = (
                module_options.index(st.session_state.selected_module)
                if st.session_state.selected_module in module_options
                else 0
            )

            st.session_state.selected_module = st.selectbox(
                "Select module",
                module_options,
                index=current_index,
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
        if st.button(
            "🕒 History",
            use_container_width=True,
            type="primary",
            key="btn_history"
        ):

            st.session_state.show_history_panel = (
                not st.session_state.show_history_panel
            )

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

        # ---------------- Clear All Sessions ----------------
        if st.button(
            "🗑️ Clear All Sessions",
            use_container_width=True,
            type="primary",
            key="btn_clear_sessions"
        ):

            # Full reset — chats, uploaded files, active file, and
            # module selection all go back to their fresh-start
            # defaults, not just the chat history.
            st.session_state.chat_sessions = {}
            st.session_state.stored_files = {}
            st.session_state.active_file = None
            st.session_state.selected_file = None
            st.session_state.selected_module = "None"
            st.session_state.show_module_selector = False
            st.session_state.show_files_panel = False
            st.session_state.show_history_panel = False

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
            ("🗑️", "rail_clear_sessions"),
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

    _selected_module = st.session_state.get("selected_module", "None")
    _active_file = st.session_state.get("active_file")

    if _active_file:
        _hero_module = _active_file
    elif _selected_module != "None":
        _hero_module = _selected_module
    else:
        _hero_module = "Data"

    st.markdown(
        f"""
        <div class="dily-hero">
            <div class="dily-hero-copy">
                <span class="dily-hero-badge">DILYTICS</span>
                <h1>Chat with your {_hero_module}<br>data using <span>Cortex AI</span></h1>
                <p class="sub">
                    Ask questions and get instant
                    insights across your {_hero_module.lower()} data.
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
# CHAT INPUT
# ============================================================

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

user_prompt = (
    user_prompt
    or suggestion_click_prompt
)

if uploaded_chat_files:

    typed_prompt = (user_prompt or "").strip()

    for f in uploaded_chat_files:

        if f.name not in st.session_state.stored_files:

            text_content, parsed_df = extract_data_from_upload(f)

            st.session_state.stored_files[f.name] = {
                "text": text_content,
                "type": f.type,
                "df": parsed_df
            }

        # Newly uploaded file becomes the active file automatically —
        # file Q&A and Module Q&A are mutually exclusive, so this
        # also disables the Module button (see sidebar section).
        st.session_state.active_file = f.name

    file_names = ", ".join(f.name for f in uploaded_chat_files)
    attach_note = f"(Attached: {file_names})"

    if typed_prompt:

        # A question was typed alongside the upload — treat it as
        # a real question and let it flow through the normal
        # PROCESS QUESTION section below.
        user_prompt = f"{typed_prompt}\n\n{attach_note}"

    else:

        # No question was typed — automatically analyze the file
        # and post the observations as an assistant turn, without
        # waiting for the user to ask anything.
        if len(messages) == 0:

            st.session_state.chat_sessions[
                current_id
            ]["title"] = file_names[:25] + (
                "..." if len(file_names) > 25 else ""
            )

        messages.append(
            {
                "role": "user",
                "content": attach_note
            }
        )

        with st.chat_message("user"):
            st.markdown(attach_note)

        last_uploaded = uploaded_chat_files[-1].name

        with st.chat_message("assistant"):

            explanation, sql_query, preview_df = generate_file_overview(
                last_uploaded
            )

            st.markdown(explanation)

            show_query_result(
                sql_query,
                preview_df,
                key_prefix=f"overview_{current_id}"
            )

        messages.append(
            {
                "role": "assistant",
                "content": explanation,
                "sql": sql_query,
                "data": preview_df,
                "suggestions": None
            }
        )

        user_prompt = None


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

        explanation, sql_query, file_df = (
            generate_sql_from_prompt(
                user_prompt
            )
        )

        is_greeting_prompt = (
            user_prompt.strip().lower()
            in GREETING_PHRASES
        )

        suggestions = (
            MODULE_GREETING_SUGGESTIONS.get(
                st.session_state.get("selected_module", "None"),
                MODULE_GREETING_SUGGESTIONS["None"]
            )
            if is_greeting_prompt
            else None
        )

        st.markdown(
            explanation
        )

        df = None

        if file_df is not None:

            # File-Q&A path: the SQL was already generated AND
            # executed against the uploaded file's in-memory table
            # inside answer_from_file(). Just render it — same
            # Generated SQL / Data / Chart layout as the Cortex
            # Analyst path below.
            df = file_df

            show_query_result(
                sql_query,
                df,
                key_prefix=f"live_{current_id}"
            )

        elif sql_query:

            # Cortex Analyst path: sql_query needs to be executed
            # against the live Snowflake session.
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
