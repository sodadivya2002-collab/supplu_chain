import streamlit as st
from snowflake.snowpark import Session

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Supply Chain Chatbot",
    page_icon="📦",
    layout="wide"   # wide layout so the chat area can stretch full width
)

# ============================================================
# GLOBAL CSS
# - Removes the "floating" rounded chat input bar and makes it
#   a flat, full-width bar docked to the bottom.
# - Stretches the chat message column to the full page width
#   instead of Streamlit's default centered ~700px column.
# - Flattens chat bubbles (square corners, full width, no shadow)
#   instead of the default rounded floating bubble look.
# ============================================================

st.markdown(
    """
    <style>

    /* ============================================================
       KILL THE "FLOATING CARD" LOOK
       Streamlit (and many custom themes) wrap the whole app in an
       outer container that has a gradient/colored page background,
       while the actual content sits in a smaller white rounded
       panel with a box-shadow and margin around it — this is what
       reads as a "floating card". The rules below flatten every
       layer of that wrapper so the content fills the full browser
       viewport edge-to-edge instead.
       ============================================================ */

    html, body,
    [data-testid="stAppViewContainer"],
    [data-testid="stApp"],
    .stApp {
        background: #ffffff !important;   /* no gradient page background */
        background-image: none !important;
        margin: 0 !important;
        padding: 0 !important;
        max-width: 100% !important;
        width: 100% !important;
        height: 100% !important;
        border-radius: 0 !important;
        box-shadow: none !important;
    }

    [data-testid="stMain"],
    [data-testid="stMainBlockContainer"],
    .main,
    .block-container {
        max-width: 100% !important;
        width: 100% !important;
        margin: 0 !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        padding-top: 1.5rem !important;
        border-radius: 0 !important;
        box-shadow: none !important;
        background: #ffffff !important;
    }

    /* Some setups nest an extra wrapping <div> that carries the card
       styling (rounded corners / shadow / fixed max-width). Force
       every direct wrapper under the app container to go flat. */
    [data-testid="stAppViewContainer"] > div,
    [data-testid="stMain"] > div {
        border-radius: 0 !important;
        box-shadow: none !important;
        max-width: 100% !important;
        width: 100% !important;
    }

    /* ---- Chat message list: full width, flat panels ---- */
    [data-testid="stChatMessage"] {
        max-width: 100% !important;
        width: 100% !important;
        border-radius: 6px !important;      /* flat, not pill-shaped */
        box-shadow: none !important;        /* remove floating shadow */
        border: 1px solid #e6e6e6 !important;
        margin-bottom: 0.6rem !important;
        padding: 0.9rem 1.1rem !important;
    }

    /* Differentiate user vs assistant with flat background colors
       instead of floating shadowed bubbles */
    [data-testid="stChatMessage"]:has(img[alt="user"]) {
        background-color: #f4f6f8 !important;
    }
    [data-testid="stChatMessage"]:has(img[alt="assistant"]) {
        background-color: #ffffff !important;
    }

    /* ---- Chat input: flat, full-width, docked bar (no floating pill) ---- */
    [data-testid="stBottom"],
    [data-testid="stBottom"] > div,
    [data-testid="stBottomBlockContainer"] {
        max-width: 100% !important;
        width: 100% !important;
        margin: 0 !important;
        box-shadow: none !important;
        border-radius: 0 !important;
        background: #ffffff !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }
    [data-testid="stChatInput"] {
        max-width: 100% !important;
        width: 100% !important;
        border-radius: 4px !important;
        box-shadow: none !important;
        border-top: 1px solid #e0e0e0 !important;
    }
    [data-testid="stChatInput"] textarea,
    [data-testid="stChatInput"] > div {
        border-radius: 4px !important;
        box-shadow: none !important;
        background: #ffffff !important;
    }

    /* ---- Sidebar: center the logo and New Chat button ---- */
    section[data-testid="stSidebar"] .block-container {
        padding-top: 1.5rem !important;
    }
    .sidebar-logo {
        display: flex;
        justify-content: center;
        margin-bottom: 1rem;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# ============================================================
# SIDEBAR: LOGO + NEW CHAT BUTTON
# ============================================================
# NOTE: Place your logo file (e.g. "dilytics_logo.png") in the
# same directory as this script, or update LOGO_PATH below to
# point to wherever you keep it.
# ============================================================

LOGO_PATH = "dilytics_logo.png"

with st.sidebar:

    st.markdown('<div class="sidebar-logo">', unsafe_allow_html=True)
    try:
        st.image(LOGO_PATH, use_container_width=True)
    except Exception:
        # Fallback so the app doesn't crash if the logo file isn't found yet
        st.markdown("### Dilytics")
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("➕ New Chat", use_container_width=True):
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": (
                    "Hello! 👋 I'm your Supply Chain Assistant "
                    "powered by Snowflake Cortex.\n\n"
                    "How can I help you today?"
                )
            }
        ]
        st.rerun()

# ============================================================
# HEADER
# ============================================================

st.title("📦 Supply Chain Chatbot")
st.caption("Powered by Snowflake Cortex AI")

# ============================================================
# SNOWFLAKE CONNECTION
# ============================================================

@st.cache_resource
def get_snowflake_session():
    """
    Create and cache a Snowflake Snowpark session
    using credentials stored in Streamlit Secrets.
    """

    connection_parameters = {
        "account": st.secrets["snowflake"]["account"],
        "user": st.secrets["snowflake"]["user"],
        "password": st.secrets["snowflake"]["password"],
        "role": st.secrets["snowflake"]["role"],
        "warehouse": st.secrets["snowflake"]["warehouse"],
        "database": st.secrets["snowflake"]["database"],
        "schema": st.secrets["snowflake"]["schema"]
    }

    return Session.builder.configs(connection_parameters).create()


# ============================================================
# CREATE SNOWFLAKE SESSION
# ============================================================

try:
    session = get_snowflake_session()

    st.sidebar.success("✅ Connected to Snowflake")

except Exception as e:

    st.sidebar.error(
        f"❌ Snowflake connection failed: {str(e)}"
    )

    st.stop()


# ============================================================
# CORTEX AI FUNCTION
# ============================================================

def ask_cortex(user_question: str) -> str:
    """
    Send the user's question to Snowflake Cortex COMPLETE
    and return the generated response.
    """

    system_prompt = """
You are an expert Supply Chain Assistant.

Your job is to answer questions related to:

- Sales orders
- Purchase orders
- Inventory
- Shipments
- Deliveries
- Suppliers
- Materials
- Plants
- Warehouses
- Logistics
- Supply chain operations

Answer questions clearly, professionally, and concisely.

If the question is outside the supply-chain domain,
politely explain that you are designed to help with
supply-chain-related questions.
"""

    # Combine system instructions with user question
    full_prompt = f"""
{system_prompt}

User Question:
{user_question}
"""

    try:

        # Escape single quotes so the question does not
        # break the SQL statement.
        safe_prompt = full_prompt.replace("'", "''")

        result = session.sql(
            f"""
            SELECT SNOWFLAKE.CORTEX.COMPLETE(
                'llama3.1-70b',
                '{safe_prompt}'
            ) AS response
            """
        ).collect()

        if result:

            response = result[0]["RESPONSE"]

            if response:
                return response

            return "⚠️ Cortex returned an empty response."

        return "⚠️ No response was returned from Snowflake Cortex."

    except Exception as e:

        return f"⚠️ Error while calling Snowflake Cortex: {str(e)}"


# ============================================================
# INITIALIZE CHAT HISTORY
# ============================================================

if "messages" not in st.session_state:

    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "Hello! 👋 I'm your Supply Chain Assistant "
                "powered by Snowflake Cortex.\n\n"
                "How can I help you today?"
            )
        }
    ]


# ============================================================
# DISPLAY CHAT HISTORY
# ============================================================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])


# ============================================================
# CHAT INPUT
# ============================================================

if prompt := st.chat_input(
    "Ask about orders, inventory, shipments..."
):

    # --------------------------------------------------------
    # Add user message to chat history
    # --------------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    # --------------------------------------------------------
    # Display user message
    # --------------------------------------------------------

    with st.chat_message("user"):

        st.markdown(prompt)

    # --------------------------------------------------------
    # Generate Cortex response
    # --------------------------------------------------------

    with st.chat_message("assistant"):

        with st.spinner("Thinking with Snowflake Cortex..."):

            response = ask_cortex(prompt)

            st.markdown(response)

    # --------------------------------------------------------
    # Save assistant response
    # --------------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response
        }
    )
