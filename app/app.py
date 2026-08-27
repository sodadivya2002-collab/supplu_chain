import streamlit as st
import json

# ============================================================
# PAGE
# ============================================================

st.set_page_config(
    page_title="Dilytics Supply Chain AI",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# SESSION
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []


# ============================================================
# SNOWFLAKE CONNECTION
# ============================================================

@st.cache_resource
def get_session():

    from snowflake.snowpark import Session

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


try:

    session = get_session()
    connected = True

except Exception as e:

    session = None
    connected = False
    connection_error = str(e)


# ============================================================
# ASK SUPPLY CHAIN AGENT
# ============================================================

def ask_supply_chain(question):

    if session is None:
        return f"Snowflake connection failed: {connection_error}"

    try:

        agent_name = (
            "SUPPLY_CHAIN_DW.GOLD.AGENT_SUPPLY_CHAIN"
        )

        request = {
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": question
                        }
                    ]
                }
            ]
        }

        request_json = json.dumps(request)

        sql = f"""
        SELECT SNOWFLAKE.CORTEX.DATA_AGENT_RUN(
            '{agent_name}',
            PARSE_JSON($${request_json}$$)
        ) AS RESPONSE
        """

        result = session.sql(sql).collect()

        if not result:
            return "No response received from the Supply Chain Agent."

        response = result[0]["RESPONSE"]

        if isinstance(response, str):

            try:
                response_json = json.loads(response)
            except Exception:
                return response

        else:
            response_json = response

        if isinstance(response_json, dict):

            if "content" in response_json:

                content = response_json["content"]

                if isinstance(content, list):

                    texts = []

                    for item in content:

                        if isinstance(item, dict):

                            if item.get("type") == "text":

                                texts.append(
                                    item.get("text", "")
                                )

                    if texts:
                        return "\n".join(texts)

            if "message" in response_json:
                return str(response_json["message"])

            if "response" in response_json:
                return str(response_json["response"])

        return str(response_json)

    except Exception as e:

        return f"⚠️ Error while calling Supply Chain Agent: {e}"


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
<style>

/* ============================================================
   REMOVE STREAMLIT DEFAULT SPACING
   ============================================================ */

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

header[data-testid="stHeader"] {
    display: none;
}

[data-testid="stToolbar"] {
    display: none;
}

.block-container {
    padding: 0 !important;
    margin: 0 !important;
    max-width: 100% !important;
}

[data-testid="stMainBlockContainer"] {
    padding: 0 !important;
}


/* ============================================================
   SIDEBAR
   ============================================================ */

section[data-testid="stSidebar"] {

    width: 350px !important;
    min-width: 350px !important;
    max-width: 350px !important;

    position: fixed !important;

    left: 0 !important;
    top: 0 !important;
    bottom: 0 !important;

    background: white !important;

    border-right: 1px solid #d8e1ec;

    z-index: 9999 !important;
}

section[data-testid="stSidebar"] > div {

    width: 350px !important;

    padding: 0 !important;

}


/* ============================================================
   SIDEBAR
   ============================================================ */

.sidebar-content {

    padding: 22px 28px;

}


/* ============================================================
   DILYTICS LOGO
   ============================================================ */

.dilytics-logo {

    width: 190px;
    height: 58px;

    background: #e50909;

    color: white;

    display: flex;
    align-items: center;
    justify-content: center;

    font-family: Arial, sans-serif;

    font-size: 26px;
    font-weight: 800;

    letter-spacing: 1px;

    margin-bottom: 30px;

}


/* ============================================================
   SEMANTIC MART
   ============================================================ */

.semantic-live {

    display: inline-flex;

    align-items: center;

    gap: 8px;

    padding: 9px 15px;

    border: 1px solid #9de5cb;

    background: #f1fff9;

    border-radius: 25px;

    color: #08785c;

    font-size: 14px;

    font-weight: 600;

    margin-bottom: 30px;

}

.semantic-dot {

    width: 9px;
    height: 9px;

    background: #15a979;

    border-radius: 50%;

}


/* ============================================================
   NEW CHAT
   ============================================================ */

.new-chat {

    height: 50px;

    width: 100%;

    border: 1px solid #ccd6e3;

    border-radius: 9px;

    display: flex;

    align-items: center;

    justify-content: center;

    color: #0b315f;

    font-size: 15px;

    margin-bottom: 28px;

}


/* ============================================================
   DIVIDER
   ============================================================ */

.sidebar-divider {

    height: 1px;

    background: #d8e1ec;

    width: 100%;

    margin: 0 0 28px 0;

}


/* ============================================================
   SIDEBAR HEADINGS
   ============================================================ */

.sidebar-heading {

    color: #092d61;

    font-size: 15px;

    font-weight: 700;

    margin-bottom: 28px;

}

.no-recent {

    color: #7c899d;

    font-size: 14px;

    margin-bottom: 32px;

}


/* ============================================================
   QUICK LINKS
   ============================================================ */

.quick-link {

    height: 52px;

    display: flex;

    align-items: center;

    color: #183b67;

    font-size: 14px;

}

.quick-icon {

    width: 30px;

    font-size: 19px;

}

.quick-arrow {

    margin-left: auto;

    font-size: 18px;

    color: #174c91;

}


/* ============================================================
   MAIN HEADER
   ============================================================ */

.top-header {

    position: fixed;

    top: 0;

    left: 350px;

    right: 0;

    height: 84px;

    background: #0957d9;

    z-index: 9000;

    display: flex;

    align-items: center;

    padding: 0 30px;

    box-sizing: border-box;

}


/* ============================================================
   HEADER TITLE
   ============================================================ */

.top-title {

    color: white;

    font-family: Arial, sans-serif;

    font-size: 32px;

    font-weight: 700;

    margin-left: 30px;

    white-space: nowrap;

}


/* ============================================================
   HEADER RIGHT
   ============================================================ */

.top-right {

    margin-left: auto;

    display: flex;

    align-items: center;

    gap: 25px;

    color: white;

}

.top-bell {
    font-size: 25px;
}

.top-question {
    font-size: 22px;
}

.top-user {
    font-size: 16px;
}


/* ============================================================
   MAIN HERO
   ============================================================ */

.hero {

    margin-left: 350px;

    padding-top: 84px;

    height: 430px;

    box-sizing: border-box;

    background: #edf5ff;

    display: flex;

    flex-direction: column;

    align-items: center;

    justify-content: flex-start;

}


/* ============================================================
   BOT
   ============================================================ */

.bot {

    width: 70px;

    height: 70px;

    margin-top: 32px;

    margin-bottom: 18px;

    border-radius: 50%;

    background: white;

    display: flex;

    align-items: center;

    justify-content: center;

    font-size: 31px;

    box-shadow:
        0 7px 20px rgba(0, 50, 120, 0.10);

}


/* ============================================================
   HERO TITLE
   ============================================================ */

.hero-title {

    color: #092d61;

    font-family: Arial, sans-serif;

    font-size: 42px;

    font-weight: 750;

    line-height: 1.1;

    text-align: center;

    margin: 0;

}


/* ============================================================
   BLUE LINE
   ============================================================ */

.hero-line {

    width: 140px;

    height: 4px;

    background: #0957d9;

    margin-top: 15px;

    margin-bottom: 15px;

}


/* ============================================================
   SUBTITLE
   ============================================================ */

.hero-subtitle {

    color: #24466f;

    font-family: Arial, sans-serif;

    font-size: 17px;

    text-align: center;

    margin: 0;

}


/* ============================================================
   CARDS
   ============================================================ */

.cards {

    margin-left: 350px;

    background: #edf5ff;

    padding: 0 0 20px 0;

    display: grid;

    grid-template-columns:
        repeat(6, 1fr);

    gap: 18px;

}


/* ============================================================
   CARD
   ============================================================ */

.card {

    height: 145px;

    background: white;

    border: 1px solid #d4e1ef;

    border-radius: 15px;

    display: flex;

    flex-direction: column;

    align-items: center;

    justify-content: center;

    text-align: center;

    box-sizing: border-box;

}


/* ============================================================
   CARD ICON
   ============================================================ */

.card-icon {

    font-size: 42px;

    margin-bottom: 12px;

}


/* ============================================================
   CARD TEXT
   ============================================================ */

.card-text {

    color: #092d61;

    font-family: Arial, sans-serif;

    font-size: 15px;

    font-weight: 700;

    line-height: 1.3;

}


/* ============================================================
   CHAT HISTORY
   ============================================================ */

.chat-area {

    margin-left: 350px;

    background: #edf5ff;

    padding: 10px 8% 120px 8%;

}


/* ============================================================
   USER MESSAGE
   ============================================================ */

.user-message {

    background: white;

    border: 1px solid #d5e0ed;

    border-radius: 12px;

    padding: 14px 18px;

    margin-bottom: 12px;

    color: #173860;

}


/* ============================================================
   ASSISTANT MESSAGE
   ============================================================ */

.assistant-message {

    background: #f7fbff;

    border: 1px solid #d5e0ed;

    border-radius: 12px;

    padding: 14px 18px;

    margin-bottom: 15px;

    color: #173860;

}


/* ============================================================
   STREAMLIT CHAT INPUT
   ============================================================ */

[data-testid="stChatInput"] {

    position: fixed !important;

    left: calc(350px + 8%) !important;

    right: 8% !important;

    bottom: 22px !important;

    width: auto !important;

    z-index: 9998 !important;

}

[data-testid="stChatInput"] > div {

    border-radius: 40px !important;

    border: 1px solid #cbdced !important;

    background: white !important;

    box-shadow:
        0 4px 16px rgba(40, 80, 140, 0.08) !important;

}


/* ============================================================
   SMALLER SCREEN
   ============================================================ */

@media (max-width: 1200px) {

    section[data-testid="stSidebar"] {

        width: 300px !important;
        min-width: 300px !important;
        max-width: 300px !important;

    }

    section[data-testid="stSidebar"] > div {

        width: 300px !important;

    }

    .top-header {

        left: 300px;

    }

    .hero {

        margin-left: 300px;

    }

    .cards {

        margin-left: 300px;

    }

    .chat-area {

        margin-left: 300px;

    }

    [data-testid="stChatInput"] {

        left: calc(300px + 6%) !important;

        right: 6% !important;

    }

    .hero-title {

        font-size: 34px;

    }

}

</style>
""",
    unsafe_allow_html=True
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        """
        <div class="sidebar-content">

            <div class="dilytics-logo">
                DILYTICS
            </div>

            <div class="semantic-live">
                <span class="semantic-dot"></span>
                Semantic Mart Live
            </div>

            <div class="new-chat">
                ＋&nbsp; New Chat
            </div>

            <div class="sidebar-divider"></div>

            <div class="sidebar-heading">
                ◷ &nbsp; Recent Conversations
            </div>

            <div class="no-recent">
                No recent conversations
            </div>

            <div class="sidebar-divider"></div>

            <div class="sidebar-heading">
                🔗 &nbsp; Quick Links
            </div>

            <div class="quick-link">
                <span class="quick-icon">📋</span>
                <span>Purchase Orders</span>
                <span class="quick-arrow">›</span>
            </div>

            <div class="quick-link">
                <span class="quick-icon">🚚</span>
                <span>Shipments</span>
                <span class="quick-arrow">›</span>
            </div>

            <div class="quick-link">
                <span class="quick-icon">📦</span>
                <span>Inventory</span>
                <span class="quick-arrow">›</span>
            </div>

            <div class="quick-link">
                <span class="quick-icon">👥</span>
                <span>Suppliers</span>
                <span class="quick-arrow">›</span>
            </div>

            <div class="quick-link">
                <span class="quick-icon">🏭</span>
                <span>Warehouses</span>
                <span class="quick-arrow">›</span>
            </div>

            <div class="quick-link">
                <span class="quick-icon">🚛</span>
                <span>Carriers</span>
                <span class="quick-arrow">›</span>
            </div>

            <div class="quick-link">
                <span class="quick-icon">📦</span>
                <span>Products</span>
                <span class="quick-arrow">›</span>
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# FIXED TOP HEADER
# ============================================================

st.markdown(
    """
    <div class="top-header">

        <div class="top-title">
            Dilytics Supply Chain AI
        </div>

        <div class="top-right">

            <span class="top-bell">🔔</span>

            <span class="top-question">?</span>

            <span class="top-user">●</span>

        </div>

    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# HERO
# ============================================================

st.markdown(
    """
    <div class="hero">

        <div class="bot">
            🤖
        </div>

        <div class="hero-title">
            Dilytics Supply Chain AI
        </div>

        <div class="hero-line"></div>

        <div class="hero-subtitle">
            Ask anything about your supply chain data in natural language.
        </div>

    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# CARDS
# ============================================================

st.markdown(
    """
    <div class="cards">

        <div class="card">

            <div class="card-icon">
                📋
            </div>

            <div class="card-text">
                Purchase<br>
                Orders
            </div>

        </div>


        <div class="card">

            <div class="card-icon">
                🚚
            </div>

            <div class="card-text">
                Shipments<br>
                & Deliveries
            </div>

        </div>


        <div class="card">

            <div class="card-icon">
                📊
            </div>

            <div class="card-text">
                Inventory<br>
                & Warehouses
            </div>

        </div>


        <div class="card">

            <div class="card-icon">
                👥
            </div>

            <div class="card-text">
                Suppliers
            </div>

        </div>


        <div class="card">

            <div class="card-icon">
                📦
            </div>

            <div class="card-text">
                Products
            </div>

        </div>


        <div class="card">

            <div class="card-icon">
                📈
            </div>

            <div class="card-text">
                Analytics<br>
                & Reports
            </div>

        </div>

    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# CHAT HISTORY
# ============================================================

if st.session_state.messages:

    st.markdown(
        '<div class="chat-area">',
        unsafe_allow_html=True
    )

    for message in st.session_state.messages:

        if message["role"] == "user":

            st.markdown(
                f"""
                <div class="user-message">
                    👤 <b>You</b><br><br>
                    {message["content"]}
                </div>
                """,
                unsafe_allow_html=True
            )

        else:

            st.markdown(
                f"""
                <div class="assistant-message">
                    🤖 <b>Dilytics AI</b><br><br>
                    {message["content"]}
                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )


# ============================================================
# REAL CHAT INPUT
# ============================================================

question = st.chat_input(
    "Ask your supply chain question..."
)


# ============================================================
# PROCESS QUESTION
# ============================================================

if question:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question
        }
    )

    with st.spinner("Thinking..."):

        answer = ask_supply_chain(question)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )

    st.rerun()
