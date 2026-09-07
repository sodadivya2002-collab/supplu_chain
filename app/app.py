import streamlit as st
import pandas as pd
import re
import difflib
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
       highlight, never a disable.
       Two selector forms are included (plain class + the
       stVerticalBlockBorderWrapper form some Streamlit versions
       use) so the highlight still applies even if one form's
       markup changes between Streamlit releases. */
    .st-key-module_btn_active div[data-testid="stButton"] > button[kind="primary"],
    .st-key-upload_btn_active div[data-testid="stButton"] > button[kind="primary"],
    div[data-testid="stVerticalBlockBorderWrapper"].st-key-module_btn_active button[kind="primary"],
    div[data-testid="stVerticalBlockBorderWrapper"].st-key-upload_btn_active button[kind="primary"],
    .st-key-module_btn_active button[kind="primary"],
    .st-key-upload_btn_active button[kind="primary"] {
        border-color: #2dd4bf !important;
        color: #2dd4bf !important;
        box-shadow: 0 0 0 1px rgba(45, 212, 191, 0.25) !important;
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
# instead of guesswork over a text snippet.
#
# PDFs and DOCX files now ALSO get a table extracted (via
# pdfplumber / python-docx) whenever the document contains one, so
# numeric questions ("what's the total amount?", "average unit
# price?") work on those file types too — not just CSV/XLSX. Plain
# extracted text is always kept alongside as a fallback / for
# non-tabular passages.
#
# Images are OCR'd with pytesseract (fully local, free) so a
# photographed invoice or scanned page becomes searchable text.
#
# Everything below uses only local, free, open-source Python
# libraries — no paid API and no LLM call, so results stay
# 100% deterministic and reproducible from what's actually in the
# file. Required packages: pandas, pypdf (or PyPDF2), pdfplumber,
# python-docx, pytesseract, Pillow, and (optional, improves text
# search quality) scikit-learn. On Streamlit Community Cloud, also
# add a `packages.txt` file containing the line `tesseract-ocr` so
# OCR has the system binary it needs.
# ============================================================

def _coerce_numeric_columns(df):
    """Best-effort: converts any column that looks numeric (after
    stripping thousands separators) into an actual numeric dtype,
    so aggregations work on tables pulled out of PDFs/DOCX where
    everything starts out as plain text."""

    for col in df.columns:
        coerced = pd.to_numeric(
            df[col].astype(str).str.replace(",", "", regex=False).str.strip(),
            errors="coerce"
        )
        if coerced.notna().mean() > 0.7:
            df[col] = coerced

    return df


def extract_all_tables_from_pdf(uploaded_file):
    """Uses pdfplumber (pure-Python, free, fully local) to pull
    EVERY table out of the PDF (not just the biggest one) and
    returns them as a list of DataFrames, in the order they appear.
    Returns an empty list if pdfplumber isn't installed, the PDF
    has no extractable tables, or anything goes wrong — callers
    always fall back to the plain-text extraction in that case."""

    try:
        import pdfplumber
    except ImportError:
        return []

    dataframes = []

    try:
        uploaded_file.seek(0)

        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                for table in (page.extract_tables() or []):
                    if not table or len(table) < 2:
                        continue

                    header, *rows = table
                    header = [
                        (h.strip() if h else f"column_{i}")
                        for i, h in enumerate(header)
                    ]

                    try:
                        df = pd.DataFrame(rows, columns=header)
                        dataframes.append(_coerce_numeric_columns(df))
                    except Exception:
                        continue

    except Exception:
        return []

    return dataframes


def extract_all_tables_from_docx(document):
    """Pulls EVERY table out of a python-docx Document (not just
    the biggest one) into a list of DataFrames, in document order.
    Returns an empty list if the document has no usable tables."""

    dataframes = []

    for table in document.tables:

        try:
            data = [
                [cell.text.strip() for cell in row.cells]
                for row in table.rows
            ]

            if len(data) < 2:
                continue

            header, *rows = data
            df = pd.DataFrame(rows, columns=header)
            dataframes.append(_coerce_numeric_columns(df))

        except Exception:
            continue

    return dataframes


def extract_text_via_ocr(uploaded_file):
    """OCRs an image with pytesseract — free and fully local, no
    API key or internet call required. Requires the `tesseract-ocr`
    system binary to be installed on the host (on Streamlit
    Community Cloud, add a `packages.txt` file containing the line
    `tesseract-ocr`). Returns an empty string (never raises) if OCR
    isn't available so the app degrades gracefully instead of
    crashing."""

    try:
        import pytesseract
        from PIL import Image
    except ImportError:
        return ""

    try:
        uploaded_file.seek(0)
        image = Image.open(uploaded_file)
        return pytesseract.image_to_string(image)
    except Exception:
        return ""


def extract_data_from_upload(uploaded_file):
    """Returns (text, tables). `tables` is an ordered dict of
    {label: DataFrame} — every sheet found for xlsx/xls, every
    table found for docx/pdf, or a single "Data" entry for csv.
    It's an empty dict for files with no tabular content (txt,
    images, or non-tabular pdf/docx). `text` is always a string:
    the full extracted text, used for search/overview and as the
    OCR result for images.

    Multi-sheet workbooks and multi-table Word docs are fully
    preserved here (not collapsed to "the first/biggest one") so
    the person can pick which sheet/table to query — see the
    sheet/table selector shown next to the active file."""

    name = uploaded_file.name
    ext = name.split(".")[-1].lower() if "." in name else ""

    try:

        if ext == "txt":
            return uploaded_file.read().decode("utf-8", errors="ignore"), {}

        elif ext == "csv":
            df = pd.read_csv(uploaded_file)
            return df.to_csv(index=False), {"Data": df}

        elif ext in ("xlsx", "xls"):

            # sheet_name=None reads every sheet in the workbook,
            # returned as {sheet_name: DataFrame} — nothing is
            # dropped, unlike reading just the first sheet.
            sheets = pd.read_excel(uploaded_file, sheet_name=None)

            tables = {
                sheet_name: sheet_df
                for sheet_name, sheet_df in sheets.items()
                if sheet_df is not None and not sheet_df.empty
            }

            text = "\n\n".join(
                f"--- Sheet: {sheet_name} ---\n{sheet_df.to_csv(index=False)}"
                for sheet_name, sheet_df in tables.items()
            )

            return text, tables

        elif ext == "pdf":

            pdf_tables = extract_all_tables_from_pdf(uploaded_file)

            uploaded_file.seek(0)

            try:
                from pypdf import PdfReader
            except ImportError:
                from PyPDF2 import PdfReader

            reader = PdfReader(uploaded_file)
            text = "\n".join(
                (page.extract_text() or "") for page in reader.pages
            )

            tables = {
                f"Table {i + 1}": df for i, df in enumerate(pdf_tables)
            }

            return text, tables

        elif ext == "docx":

            import docx
            document = docx.Document(uploaded_file)

            text = "\n".join(p.text for p in document.paragraphs)
            docx_tables = extract_all_tables_from_docx(document)

            tables = {
                f"Table {i + 1}": df for i, df in enumerate(docx_tables)
            }

            return text, tables

        elif ext in ("png", "jpg", "jpeg"):

            ocr_text = extract_text_via_ocr(uploaded_file)

            if ocr_text.strip():
                return ocr_text, {}

            return (
                "[Image uploaded — OCR found no readable text. If "
                "text was expected, make sure `pytesseract`, "
                "`Pillow`, and the `tesseract-ocr` system package "
                "are installed.]",
                {}
            )

        else:
            return "[Unsupported file type for text extraction.]", {}

    except ImportError as e:
        return (
            f"[Could not read '{name}' — missing library ({e}). "
            f"Install pypdf / python-docx / pdfplumber / pytesseract "
            f"to enable this file type.]",
            {}
        )

    except Exception as e:
        return f"[Could not read '{name}': {e}]", {}


# ------------------------------------------------------------
# DETERMINISTIC QUERY ENGINE (pandas only — no LLM anywhere)
# ------------------------------------------------------------
# Every number this
# engine returns comes straight out of a pandas call that this
# code builds and runs itself — nothing is guessed, invented, or
# hallucinated by a model. There are two levels of it:
#
#   1. A lightweight keyword/pattern parser (below) that maps a
#      typed question to an aggregation + column(s), for the
#      "ask anything" chat feel. If it can't confidently match a
#      real column and operation, it says so instead of guessing.
#   2. A menu-driven "Guided Query" builder (further down) that
#      lets the user pick column/operation/group-by/filter from
#      dropdowns — this is always exact, since nothing is parsed.
#
# It now also understands numeric comparisons ("orders over 500",
# "amount greater than 1000"), "list/show me" style questions
# (returns the matching rows instead of a single number), and
# "top N" questions — on top of the original equality-filter and
# aggregation support.
# ------------------------------------------------------------

_AGG_KEYWORDS = [
    # Checked in order — "distinct"/"unique" must be checked before
    # the generic "how many"/"count" keywords, since phrasings like
    # "how many distinct suppliers" contain both and should resolve
    # to nunique, not a plain row count.
    (["distinct", "unique"], "nunique"),
    (["how many", "count", "number of", "no. of", "no of"], "count"),
    (["total", "sum", "overall"], "sum"),
    (["average", "avg", "mean"], "mean"),
    (["median"], "median"),
    (["maximum", "max ", "highest", "largest", "biggest", "top"], "max"),
    (["minimum", "min ", "lowest", "smallest"], "min"),
]

_GROUPBY_PATTERNS = [
    r"(?:grouped by|group by|breakdown by|broken down by)\s+([a-z0-9_ ]+?)(?:\?|$|,|\.)",
    r"\bby\s+([a-z0-9_ ]+?)(?:\?|$|,|\.)",
    r"\bper\s+([a-z0-9_ ]+?)(?:\?|$|,|\.)",
    r"for each\s+([a-z0-9_ ]+?)(?:\?|$|,|\.)",
]

_FILTER_PATTERNS = [
    r"where\s+([a-z0-9_ ]+?)\s+(?:is|=|==|equals?)\s+([a-z0-9_ .\-]+?)(?:\?|$|,|\.)",
    r"for\s+([a-z0-9_ ]+?)\s*=\s*([a-z0-9_ .\-]+?)(?:\?|$|,|\.)",
]

# Ordered longest-phrase-first so "greater than or equal to" wins
# over "greater than" when both would otherwise match.
_COMPARISON_PHRASES = [
    (["greater than or equal to", "at least", "no less than", "minimum of"], ">="),
    (["less than or equal to", "at most", "no more than", "maximum of"], "<="),
    (["greater than", "more than", "over", "above", "exceeding", "exceeds"], ">"),
    (["less than", "under", "below", "fewer than"], "<"),
]

_LIST_KEYWORDS = [
    "list ", "list all", "show me", "show all", "which ",
    "what are the", "give me the list", "give me all"
]


_GENERIC_COLUMN_WORDS = {"name", "id", "value", "amount", "code", "type", "date"}


def _singularize(word):
    """Crude but safe English singularizer — good enough to match
    'suppliers' to a column word 'supplier' without over-matching
    unrelated short words."""

    if len(word) > 4 and word.endswith("ies"):
        return word[:-3] + "y"
    if len(word) > 4 and word.endswith("es") and word[-3] not in "aeiou":
        return word[:-2]
    if len(word) > 3 and word.endswith("s") and not word.endswith("ss"):
        return word[:-1]
    return word


def _words(text):
    return [_singularize(w) for w in re.findall(r"[a-z0-9]+", text.lower())]


def _match_column(token, columns):
    """Fuzzy-matches a user-typed word/phrase to one of the file's
    actual column names, singular/plural-insensitive. Tries an
    exact match first, then a word-subset match (only if exactly
    one column qualifies), then a close-spelling match — and
    returns None (never a guess) if the match is ambiguous or
    nothing lines up confidently."""

    token_words = set(_words(token))

    if not token_words:
        return None

    lower_map = {c.lower().replace("_", " "): c for c in columns}
    token_clean = " ".join(sorted(token_words))

    for lower_name, real_name in lower_map.items():
        if set(_words(lower_name)) == token_words:
            return real_name

    # Word-subset match in either direction (handles "suppliers" ->
    # "Supplier Name", and "order value" -> exact column of the
    # same words). Only accepted if exactly one column qualifies —
    # ties mean the question is ambiguous, so refuse rather than
    # guess.
    subset_hits = [
        real_name
        for lower_name, real_name in lower_map.items()
        if (token_words <= set(_words(lower_name)))
        or (set(_words(lower_name)) <= token_words)
    ]

    if len(subset_hits) == 1:
        return subset_hits[0]

    if len(subset_hits) > 1:
        return None

    close = difflib.get_close_matches(
        token_clean, list(lower_map.keys()), n=2, cutoff=0.75
    )

    if len(close) == 1:
        return lower_map[close[0]]

    return None


def _detect_aggregation(p):
    for keywords, agg in _AGG_KEYWORDS:
        for kw in keywords:
            if kw in p:
                return agg
    return None


def _detect_groupby(p, columns):
    for pattern in _GROUPBY_PATTERNS:
        match = re.search(pattern, p)
        if match:
            matched_col = _match_column(match.group(1), columns)
            if matched_col:
                return matched_col
    return None


def _detect_filter(p, columns):
    for pattern in _FILTER_PATTERNS:
        match = re.search(pattern, p)
        if match:
            matched_col = _match_column(match.group(1), columns)
            if matched_col:
                return matched_col, match.group(2).strip()
    return None


def _detect_numeric_filter(p, columns):
    """Finds a numeric comparison anywhere in the question, either
    symbolic ("amount > 1000") or phrased in English ("amount
    greater than 1000", "orders over 500"). Returns
    (column, operator, value) or None. Never guesses which column
    if the wording doesn't confidently line up with a real one."""

    # Symbolic form first: "column >= 100"
    match = re.search(
        r"([a-z0-9_ ]+?)\s*(>=|<=|>|<)\s*([0-9][0-9,]*\.?[0-9]*)", p
    )
    if match:
        col = _match_column(match.group(1), columns)
        if col:
            try:
                return col, match.group(2), float(match.group(3).replace(",", ""))
            except ValueError:
                pass

    for phrases, op in _COMPARISON_PHRASES:
        for phrase in phrases:
            pattern = (
                r"([a-z0-9_ ]+?)\s+" + re.escape(phrase) +
                r"\s+([0-9][0-9,]*\.?[0-9]*)"
            )
            match = re.search(pattern, p)
            if match:
                col = _match_column(match.group(1), columns)
                if col:
                    try:
                        return (
                            col, op,
                            float(match.group(2).replace(",", ""))
                        )
                    except ValueError:
                        continue

    return None


_ID_COLUMN_PATTERN = re.compile(r"(^|_)(id|code|key|no|num|number)$")


def _looks_like_identifier_column(col):
    """True for columns that are identifiers (EVENT_ID, ORDER_CODE,
    CUSTOMER_KEY, ...) rather than measurable metrics. These should
    only ever be matched when the person names them explicitly and
    in full — never via the looser 'significant word overlap'
    match used for ordinary metric columns, since that lets an
    unrelated word elsewhere in the question (e.g. 'events' in
    'how many people attended the events') falsely pull in an ID
    column and produce a meaningless count/sum/average of it."""

    normalized = re.sub(r"[^a-z0-9]+", "_", col.strip().lower()).strip("_")
    return bool(_ID_COLUMN_PATTERN.search(normalized))


def _detect_metric_column(p, columns, numeric_columns):
    """Finds the single column the question is most plausibly
    referring to. A column only counts as matched if either (a)
    every word in its name appears in the question, or (b) — for
    non-identifier columns only — every one of its non-generic
    words (i.e. excluding filler like 'name'/'value'/'id') appears
    in the question. Identifier columns (EVENT_ID, ORDER_CODE, ...)
    require the stricter full match (a), so they're never picked up
    just because a related-sounding word is mentioned elsewhere. If
    more than one column ties for the best match, this returns None
    rather than guessing which one the user meant."""

    q_words = set(_words(p))

    def score(col):
        col_words = _words(col)
        if not col_words:
            return 0
        if all(w in q_words for w in col_words):
            return 100 + len(col_words)
        if _looks_like_identifier_column(col):
            return 0
        significant = [w for w in col_words if w not in _GENERIC_COLUMN_WORDS]
        if significant and all(w in q_words for w in significant):
            return 50 + len(significant)
        return 0

    def best(cols):
        scored = sorted(
            ((score(c), c) for c in cols if score(c) > 0),
            key=lambda x: -x[0]
        )
        if not scored:
            return None
        if len(scored) > 1 and scored[0][0] == scored[1][0]:
            return None
        return scored[0][1]

    # Prefer a numeric column match (most questions ask about a
    # metric); fall back to any column (covers count/nunique on a
    # categorical column, e.g. "how many distinct suppliers").
    return best(numeric_columns) or best(columns)


def _is_list_intent(p):
    return any(kw in p for kw in _LIST_KEYWORDS)


def answer_question_from_dataframe(prompt, df):
    """Deterministically answers a question about `df` using only
    pandas. Returns (explanation, computation_description,
    result_df). `computation_description` is the exact pandas
    call that was executed, shown to the user for full
    transparency — there is no SQL involved and nothing is
    inferred beyond simple keyword matching to real column names."""

    p = f" {prompt.lower().strip()} "

    columns = list(df.columns)
    numeric_columns = df.select_dtypes(include="number").columns.tolist()

    if re.search(r"how many (rows|records|entries)|total (rows|records)|row count", p):
        return (
            f"There are **{len(df):,} rows** in this file.",
            "len(df)",
            None
        )

    working_df = df
    filter_note = ""

    # Equality filter, e.g. "where status is Delayed"
    filter_result = _detect_filter(p, columns)
    if filter_result:
        filter_col, filter_val = filter_result
        mask = (
            working_df[filter_col]
            .astype(str)
            .str.strip()
            .str.lower()
            == filter_val.strip().lower()
        )
        working_df = working_df[mask]
        filter_note += f" where `{filter_col}` = \"{filter_val}\""

    # Numeric comparison filter, e.g. "orders over 500" /
    # "amount >= 1000". Can be combined with the equality filter
    # above (both narrow the same working_df further).
    numeric_filter = _detect_numeric_filter(p, columns)
    if numeric_filter:
        filt_col, op, filt_val = numeric_filter
        try:
            numeric_series = pd.to_numeric(working_df[filt_col], errors="coerce")
            ops = {
                ">": numeric_series > filt_val,
                "<": numeric_series < filt_val,
                ">=": numeric_series >= filt_val,
                "<=": numeric_series <= filt_val,
            }
            working_df = working_df[ops[op]]
            filter_note += f" where `{filt_col}` {op} {filt_val:,g}"
        except Exception:
            pass

    # "list"/"show me"/"top N" intent — the answer is a table of
    # matching rows rather than a single aggregate number.
    top_n_match = re.search(r"top\s+(\d+)", p)
    list_intent = _is_list_intent(p) or top_n_match

    if list_intent and (filter_note or top_n_match or _is_list_intent(p)):

        result_rows = working_df
        sort_col = _detect_metric_column(p, columns, numeric_columns)

        if top_n_match:
            n = int(top_n_match.group(1))
            if sort_col:
                result_rows = result_rows.sort_values(
                    by=sort_col, ascending=False
                )
            result_rows = result_rows.head(n)

        truncated_note = ""
        if len(result_rows) > 500:
            result_rows = result_rows.head(500)
            truncated_note = " (showing first 500 matching rows)"

        explanation = (
            f"**{len(working_df):,} matching row(s)**{filter_note}"
            f"{truncated_note}:"
        )

        computation = "df" + (
            "[conditions]" if filter_note else ""
        ) + (
            f".sort_values('{sort_col}', ascending=False).head({top_n_match.group(1)})"
            if top_n_match and sort_col else ""
        )

        return explanation, computation, result_rows

    aggregation = _detect_aggregation(p)
    group_col = _detect_groupby(p, columns)
    metric_col = _detect_metric_column(p, columns, numeric_columns)

    if aggregation is None:

        if filter_note:
            # A filter was recognized even though no aggregation
            # word was found — most likely the user wanted to see
            # the matching rows. Return them rather than refusing.
            truncated_note = ""
            result_rows = working_df
            if len(result_rows) > 500:
                result_rows = result_rows.head(500)
                truncated_note = " (showing first 500 matching rows)"

            return (
                f"**{len(working_df):,} matching row(s)**{filter_note}"
                f"{truncated_note}:",
                "df[conditions]",
                result_rows
            )

        return (
            "I couldn't confidently match that question to a specific "
            "calculation, so rather than guess I've left it unanswered. "
            "Try rephrasing with a clear operation (total / average / "
            "count / max / min), a comparison (\"over 500\", \"at "
            "least 10\"), or a \"list\"/\"top N\" request — or use the "
            "**🎛️ Guided Query** panel below the chat for a menu-driven "
            "question that's always exact.\n\n"
            f"Available columns: {', '.join(columns)}",
            None,
            None
        )

    if aggregation == "count" and metric_col is None:
        return (
            f"**Count{filter_note}: {len(working_df):,}**",
            "len(df)" + (" [after filter]" if filter_note else ""),
            None
        )

    if metric_col is None:
        return (
            "I recognized the operation but couldn't confidently match "
            "it to one of this file's actual columns, so I won't guess "
            f"at a result. Available columns: {', '.join(columns)}",
            None,
            None
        )

    if group_col and group_col != metric_col:

        try:
            grouped = (
                working_df.groupby(group_col)[metric_col]
                .agg(aggregation)
                .reset_index()
                .sort_values(by=metric_col, ascending=False)
            )
        except Exception as e:
            return (
                f"Could not compute `{aggregation}` of `{metric_col}` "
                f"grouped by `{group_col}`.\n\n**Error:** {str(e)}",
                None,
                None
            )

        explanation = (
            f"**{aggregation.capitalize()} of `{metric_col}` by "
            f"`{group_col}`**{filter_note}:"
        )

        computation = (
            f"df.groupby('{group_col}')['{metric_col}'].{aggregation}()"
        )

        return explanation, computation, grouped

    try:
        result_value = getattr(working_df[metric_col], aggregation)()
    except Exception as e:
        return (
            f"Could not compute `{aggregation}` of `{metric_col}`.\n\n"
            f"**Error:** {str(e)}",
            None,
            None
        )

    result_display = (
        f"{result_value:,.2f}" if isinstance(result_value, float)
        else f"{result_value:,}"
    )

    explanation = (
        f"**{aggregation.capitalize()} of `{metric_col}`{filter_note}: "
        f"{result_display}**"
    )

    computation = f"df['{metric_col}'].{aggregation}()"

    return explanation, computation, None


try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    _SKLEARN_AVAILABLE = True
except ImportError:
    _SKLEARN_AVAILABLE = False


def _keyword_search_text(prompt, text, top_n=3):
    """Extractive, deterministic search over plain text: splits the
    document into paragraphs and ranks them by relevance to the
    question, then returns the best-matching passages verbatim — no
    rewriting, no LLM, so nothing can be fabricated.

    Ranking uses TF-IDF + cosine similarity (via scikit-learn, a
    free local statistics library — not an LLM) when available,
    since it handles longer documents and varied phrasing much
    better than raw word overlap. If scikit-learn isn't installed,
    this falls back to simple keyword-overlap scoring so the
    feature still works everywhere."""

    paragraphs = [
        para.strip() for para in re.split(r"\n\s*\n|\n", text)
        if para.strip()
    ]

    if not paragraphs:
        return []

    if _SKLEARN_AVAILABLE and len(paragraphs) > 1:

        try:
            vectorizer = TfidfVectorizer(stop_words="english")
            tfidf_matrix = vectorizer.fit_transform(paragraphs + [prompt])
            similarities = cosine_similarity(
                tfidf_matrix[-1], tfidf_matrix[:-1]
            ).flatten()

            ranked = sorted(
                zip(similarities, paragraphs), key=lambda x: -x[0]
            )

            results = [para for score, para in ranked[:top_n] if score > 0]

            if results:
                return results

        except Exception:
            pass  # fall through to the keyword-overlap method below

    stopwords = {
        "the", "a", "an", "is", "are", "was", "were", "of", "in",
        "on", "for", "to", "and", "or", "what", "which", "how",
        "does", "do", "this", "that", "with", "about", "as", "by",
        "at", "from", "it", "its", "be", "has", "have", "many"
    }

    question_words = {
        w for w in re.findall(r"[a-z0-9']+", prompt.lower())
        if w not in stopwords and len(w) > 2
    }

    if not question_words:
        return []

    scored = []

    for para in paragraphs:
        para_words = set(re.findall(r"[a-z0-9']+", para.lower()))
        overlap = len(question_words & para_words)
        if overlap > 0:
            scored.append((overlap, para))

    scored.sort(key=lambda x: x[0], reverse=True)

    return [para for _, para in scored[:top_n]]


def answer_from_file(prompt, fname):
    """Answers a question about the active uploaded file using only
    deterministic Python: pandas for tabular files (csv/xlsx/xls,
    and now PDFs/DOCX that contain a table), TF-IDF/keyword search
    over the extracted text for everything else (including OCR'd
    image text). No LLM is involved anywhere in this function, so
    a result can never drift from what's actually in the file —
    every number or passage returned is either computed directly
    by pandas or quoted verbatim from the document."""

    file_data = st.session_state.stored_files.get(fname, {})
    df = file_data.get("df")

    if df is not None:
        return answer_question_from_dataframe(prompt, df)

    file_text = file_data.get("text", "")
    matches = _keyword_search_text(prompt, file_text)

    if not matches:
        return (
            "I couldn't find any passages in this document matching "
            "your question's key words. Try rephrasing with more of "
            "the specific terms you're looking for.",
            None,
            None
        )

    explanation = (
        "Here are the passages from the document that best match "
        "your question, shown exactly as written (nothing here is "
        "paraphrased, summarized, or inferred):\n\n"
        + "\n\n---\n\n".join(f"> {m}" for m in matches)
    )

    return explanation, None, None


def render_guided_query_builder(df):
    """Menu-driven query builder: metric column + aggregation +
    optional group-by + optional equality filter, all picked from
    dropdowns. Nothing here is parsed from free text, so the result
    is always exactly what the dropdowns say — the guaranteed-
    accurate fallback whenever a typed question isn't confidently
    understood by the keyword parser above. Returns
    (explanation, computation_description, result_df) only on the
    turn the user clicks "Run Query"; otherwise returns None."""

    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    all_cols = list(df.columns)

    if not numeric_cols:
        return None

    with st.expander("🎛️ Guided Query (menu-driven, always exact)", expanded=False):

        gcol1, gcol2, gcol3 = st.columns(3)

        metric_col = gcol1.selectbox("Metric column", numeric_cols, key="gq_metric")

        agg_choice = gcol2.selectbox(
            "Aggregation",
            ["Sum", "Average", "Count", "Min", "Max", "Median", "Distinct count"],
            key="gq_agg"
        )

        group_col_choice = gcol3.selectbox(
            "Group by (optional)",
            ["(none)"] + all_cols,
            key="gq_group"
        )

        fcol1, fcol2 = st.columns(2)

        filter_col_choice = fcol1.selectbox(
            "Filter column (optional)",
            ["(none)"] + all_cols,
            key="gq_filter_col"
        )

        filter_val = None

        if filter_col_choice != "(none)":

            distinct_values = df[filter_col_choice].dropna().unique().tolist()

            if 0 < len(distinct_values) <= 200:
                filter_val = fcol2.selectbox(
                    "Equals",
                    distinct_values,
                    key="gq_filter_val"
                )
            else:
                filter_val = fcol2.text_input(
                    "Equals",
                    key="gq_filter_val_text"
                ) or None

        if st.button("Run Query", key="gq_run", type="primary"):

            agg_map = {
                "Sum": "sum", "Average": "mean", "Count": "count",
                "Min": "min", "Max": "max", "Median": "median",
                "Distinct count": "nunique"
            }

            aggregation = agg_map[agg_choice]

            working_df = df
            filter_note = ""

            if filter_col_choice != "(none)" and filter_val is not None:
                working_df = working_df[working_df[filter_col_choice] == filter_val]
                filter_note = f" where `{filter_col_choice}` = \"{filter_val}\""

            try:

                if group_col_choice != "(none)" and group_col_choice != metric_col:

                    result_df = (
                        working_df.groupby(group_col_choice)[metric_col]
                        .agg(aggregation)
                        .reset_index()
                        .sort_values(by=metric_col, ascending=False)
                    )

                    explanation = (
                        f"**{agg_choice} of `{metric_col}` by "
                        f"`{group_col_choice}`**{filter_note}:"
                    )

                    computation = (
                        f"df.groupby('{group_col_choice}')"
                        f"['{metric_col}'].{aggregation}()"
                    )

                    return explanation, computation, result_df

                result_value = getattr(working_df[metric_col], aggregation)()

                result_display = (
                    f"{result_value:,.2f}" if isinstance(result_value, float)
                    else f"{result_value:,}"
                )

                explanation = (
                    f"**{agg_choice} of `{metric_col}`{filter_note}: "
                    f"{result_display}**"
                )

                computation = f"df['{metric_col}'].{aggregation}()"

                return explanation, computation, None

            except Exception as e:

                return (
                    f"Could not run that query.\n\n**Error:** {str(e)}",
                    None,
                    None
                )

    return None


def generate_file_question_suggestions(fname):
    """Returns a list of ~5 short, clickable KPI/analysis
    questions grounded in the actual columns of the uploaded file
    `fname`. Built purely from the schema (column names + dtypes)
    with plain Python — no LLM involved — so every suggested
    question is guaranteed answerable and grounded in real
    columns. Cached per filename so this only runs once per
    upload."""

    cached = st.session_state.file_question_suggestions.get(fname)

    if cached:
        return cached

    file_data = st.session_state.stored_files.get(fname, {})
    df = file_data.get("df")

    if df is None:
        # Non-tabular file (pdf/docx/txt/image) — generic fallback.
        fallback = [
            "Summarize this document.",
            "What are the key points in this file?",
        ]
        st.session_state.file_question_suggestions[fname] = fallback
        return fallback

    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    categorical_cols = df.select_dtypes(include="object").columns.tolist()

    questions = ["How many total records are there?"]

    if categorical_cols:
        questions.append(
            f"What is the breakdown by {categorical_cols[0]}?"
        )

    if numeric_cols:
        questions.append(
            f"What is the average {numeric_cols[0]}?"
        )

    if len(categorical_cols) > 1:
        questions.append(
            f"How many records fall under each {categorical_cols[1]}?"
        )

    if numeric_cols and categorical_cols:
        questions.append(
            f"What is the total {numeric_cols[0]} by {categorical_cols[0]}?"
        )

    questions = questions[:5]

    st.session_state.file_question_suggestions[fname] = questions

    return questions


def generate_file_overview(fname):
    """Automatically summarizes a freshly uploaded file using only
    pandas-computed facts — row/column counts, missing values,
    numeric ranges, distinct value counts. Nothing here is an LLM
    guess at what the data "means"; it's exactly what's in the
    file. Returns (explanation, computation, preview_df)."""

    file_data = st.session_state.stored_files.get(fname, {})
    df = file_data.get("df")

    if df is None:
        # Non-tabular file — show the first few extractive matches
        # against a generic "overview" query instead of an LLM
        # summary, so nothing here is paraphrased or invented.
        return answer_from_file(
            "summary overview key points",
            fname
        )

    total_rows = len(df)
    total_cols = len(df.columns)

    lines = [f"**{fname}** — {total_rows:,} rows, {total_cols} columns."]

    all_tables = file_data.get("tables", {}) or {}
    active_label = file_data.get("active_table")

    if len(all_tables) > 1:
        other_labels = [l for l in all_tables if l != active_label]
        lines.append(
            f"\nThis file has **{len(all_tables)} sheets/tables** — "
            f"currently answering from **{active_label}**. Others "
            f"available: {', '.join(other_labels)}. Use the "
            f"\"Sheet / table to query\" dropdown above the chat box "
            f"to switch."
        )

    lines.append("")
    lines.append("**Columns:**")

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

if "show_suggestions_panel" not in st.session_state:
    st.session_state.show_suggestions_panel = False

if "file_question_suggestions" not in st.session_state:
    # Cache of generated question suggestions per uploaded
    # filename, so this only runs once per upload.
    st.session_state.file_question_suggestions = {}


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
    """Renders the shared Generated-SQL/Computation + Data/Chart
    layout. Used for the Cortex Analyst path (real SQL, run against
    Snowflake) and for the file-upload path (a plain description of
    the exact pandas call that was run — never SQL, since no SQL
    engine is involved for uploaded files anymore)."""

    if sql_query:

        is_sql = sql_query.strip().lower().startswith(
            ("select", "with")
        )

        label = "Generated SQL" if is_sql else "Computation"
        language = "sql" if is_sql else "python"

        with st.expander(
            label,
            expanded=False
        ):

            st.code(
                sql_query,
                language=language
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


def _is_question_suggestion_request(p):
    """True for phrasings like 'suggest me some kpi analysis
    questions related to this document', 'suggest some questions
    related to this file', 'give me some example questions', etc."""

    suggestion_triggers = [
        "suggest",
        "give me some question",
        "give me question",
        "sample questions",
        "example questions",
    ]

    mentions_questions = "question" in p

    return mentions_questions and any(
        trigger in p for trigger in suggestion_triggers
    )


def generate_sql_from_prompt(prompt):
    """Returns (explanation, sql, result_df, suggestions).

    result_df is pre-computed data (used for the file-upload path,
    which runs its own SQL engine); it's None for the Cortex
    Analyst path, where the caller executes `sql` against the
    live Snowflake session instead. `suggestions` is a list of
    short question strings to render as clickable buttons under
    the assistant's reply, or None when there's nothing to
    suggest."""

    p = prompt.lower().strip()

    module = st.session_state.get("selected_module", "None")
    active_file = st.session_state.get("active_file")

    if p in GREETING_PHRASES:

        if active_file:
            greeting_subject = f"your uploaded file **{active_file}**"
            greeting_suggestions = generate_file_question_suggestions(active_file)
        elif module != "None":
            greeting_subject = f"your **{module}** data"
            greeting_suggestions = MODULE_GREETING_SUGGESTIONS.get(module, [])
        else:
            greeting_subject = "your data"
            greeting_suggestions = None

        return (
            f"Hi there! 👋 Ask me anything about {greeting_subject}.\n\n"
            "Here are a few things you can try:",
            None,
            None,
            greeting_suggestions
        )

    if _is_question_suggestion_request(p):

        if active_file:

            suggestions = generate_file_question_suggestions(active_file)

            return (
                f"Here are some questions you could ask about "
                f"**{active_file}**:",
                None,
                None,
                suggestions
            )

        if module != "None":

            suggestions = MODULE_GREETING_SUGGESTIONS.get(module, [])

            return (
                f"Here are some questions you could ask about your "
                f"**{module}** data:",
                None,
                None,
                suggestions
            )

        return (
            "Select a module (**Supply Chain** or **Inventory**) "
            "from the **🧩 Module** menu, or upload a file first — "
            "then I can suggest specific questions for that data.",
            None,
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

            suggestions = generate_file_question_suggestions(active_file)

            return (
                f"You can ask me questions about your uploaded file "
                f"**{active_file}** — here are a few to try:",
                None,
                None,
                suggestions
            )

        return (
            MODULE_HELP_TEXT.get(
                module,
                MODULE_HELP_TEXT["None"]
            ),
            None,
            None,
            MODULE_GREETING_SUGGESTIONS.get(module, None) if module != "None" else None
        )

    # Quick diagnostic: "what columns" / "list columns" / "column
    # names" — always answered directly from the schema, useful
    # when a fuzzy column match doesn't behave as expected.
    if active_file and re.search(r"\b(what|list|show)\b.*\bcolumns?\b", p):

        active_df = (
            st.session_state.stored_files
            .get(active_file, {})
            .get("df")
        )

        if active_df is not None:

            col_lines = "\n".join(
                f"- `{c}` ({active_df[c].dtype})" for c in active_df.columns
            )

            return (
                f"**Columns in `{active_file}`:**\n\n{col_lines}",
                None,
                None,
                None
            )

    # File Q&A takes priority whenever a file is active — the
    # sidebar disables Module selection while a file is active,
    # so the two are mutually exclusive.
    if active_file and active_file in st.session_state.stored_files:

        explanation, sql_query, result_df = answer_from_file(prompt, active_file)

        return explanation, sql_query, result_df, None

    if module == "None":

        return (
            "Please select a module (**Supply Chain** or "
            "**Inventory**) from the **🧩 Module** menu in the "
            "sidebar, or upload a file, before asking a data "
            "question.",
            None,
            None,
            None
        )

    explanation, sql_query = call_cortex_analyst(prompt, module)

    return explanation, sql_query, None, None


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
# Order: New Chat, Module, Upload, Suggested Questions, History,
# Clear Session. Every button below is styled the same way
# (outlined, no fill — see CSS block above).
# ============================================================

pending_prompt_from_click = None

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

            module_button_label = (
                "🧩 Module ✅"
                if module_is_current_mode
                else "🧩 Module"
            )

            if st.button(
                module_button_label,
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

            upload_button_label = (
                "📁 Upload Files ✅"
                if file_is_current_mode
                else "📁 Upload Files"
            )

            if st.button(
                upload_button_label,
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

        # ---------------- Suggested Questions ----------------
        if st.button(
            "💡 Suggested Questions",
            use_container_width=True,
            type="primary",
            key="btn_suggestions"
        ):

            st.session_state.show_suggestions_panel = (
                not st.session_state.show_suggestions_panel
            )

        if st.session_state.show_suggestions_panel:

            if st.session_state.active_file:

                sidebar_suggestions = generate_file_question_suggestions(
                    st.session_state.active_file
                )

                st.caption(
                    f"Questions about **{st.session_state.active_file}**:"
                )

            elif st.session_state.selected_module != "None":

                sidebar_suggestions = MODULE_GREETING_SUGGESTIONS.get(
                    st.session_state.selected_module,
                    []
                )

                st.caption(
                    f"Questions about **{st.session_state.selected_module}**:"
                )

            else:

                sidebar_suggestions = []

                st.caption(
                    "Select a module or upload a file first to see "
                    "suggested questions here."
                )

            for sq_i, sq in enumerate(sidebar_suggestions):

                if st.button(
                    sq,
                    key=f"sidebar_sugg_{sq_i}",
                    use_container_width=True
                ):

                    pending_prompt_from_click = sq

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

        show_query_result(
            msg.get("sql"),
            msg.get("data"),
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

    _active_file_data = st.session_state.stored_files.get(
        st.session_state.active_file, {}
    )
    _available_tables = _active_file_data.get("tables", {}) or {}

    if len(_available_tables) > 1:

        _table_labels = list(_available_tables.keys())
        _current_label = _active_file_data.get(
            "active_table", _table_labels[0]
        )
        _current_index = (
            _table_labels.index(_current_label)
            if _current_label in _table_labels
            else 0
        )

        _picked_label = st.selectbox(
            "Sheet / table to query",
            _table_labels,
            index=_current_index,
            key=f"table_picker_{st.session_state.active_file}"
        )

        if _picked_label != _active_file_data.get("active_table"):

            _active_file_data["active_table"] = _picked_label
            _active_file_data["df"] = _available_tables[_picked_label]

            # A sheet/table switch changes the active dataframe, so
            # cached question suggestions (built from the old
            # sheet's columns) need to be regenerated.
            st.session_state.file_question_suggestions.pop(
                st.session_state.active_file, None
            )

            st.rerun()

    _active_df = _active_file_data.get("df")

    if _active_df is not None:

        _guided_result = render_guided_query_builder(_active_df)

        if _guided_result:

            _g_explanation, _g_computation, _g_df = _guided_result

            messages.append(
                {
                    "role": "user",
                    "content": "Guided query"
                }
            )

            messages.append(
                {
                    "role": "assistant",
                    "content": _g_explanation,
                    "sql": _g_computation,
                    "data": _g_df,
                    "suggestions": None
                }
            )

            st.rerun()


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
    or pending_prompt_from_click
)

if uploaded_chat_files:

    typed_prompt = (user_prompt or "").strip()

    for f in uploaded_chat_files:

        if f.name not in st.session_state.stored_files:

            text_content, parsed_tables = extract_data_from_upload(f)

            first_label = next(iter(parsed_tables), None)

            st.session_state.stored_files[f.name] = {
                "text": text_content,
                "type": f.type,
                "tables": parsed_tables,
                "active_table": first_label,
                "df": parsed_tables.get(first_label) if first_label else None
            }

        st.session_state.active_file = f.name

    file_names = ", ".join(f.name for f in uploaded_chat_files)
    attach_note = f"(Attached: {file_names})"

    if typed_prompt:

        user_prompt = f"{typed_prompt}\n\n{attach_note}"

    else:

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

        explanation, sql_query, file_df, suggestions = (
            generate_sql_from_prompt(
                user_prompt
            )
        )

        st.markdown(
            explanation
        )

        df = None

        if file_df is not None:

            df = file_df

            show_query_result(
                sql_query,
                df,
                key_prefix=f"live_{current_id}"
            )

        elif sql_query:

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
