import streamlit as st
import json

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Dilytics Supply Chain AI",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "recent_chats" not in st.session_state:
    st.session_state.recent_chats = []


# ============================================================
# SNOWFLAKE CONNECTION
# ============================================================

@st.cache_resource
def get_snowflake_session():

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

    session = get_snowflake_session()

    snowflake_connected = True

except Exception as e:

    session = None

    snowflake_connected = False

    connection_error = str(e)


# ============================================================
# RUN YOUR SNOWFLAKE CORTEX AGENT
# ============================================================

def ask_agent(question):

    if session is None:
        return f"Snowflake connection failed: {connection_error}"

    try:

        # ----------------------------------------------------
        # AGENT NAME
        # ----------------------------------------------------

        agent_name = (
            "SUPPLY_CHAIN_DW.GOLD.AGENT_SUPPLY_CHAIN"
        )

        # ----------------------------------------------------
        # REQUEST BODY
        # ----------------------------------------------------

        request_body = {
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
            ],
            "stream": False
        }

        request_json = json.dumps(request_body)

        # ----------------------------------------------------
        # CALL CORTEX AGENT
        # ----------------------------------------------------

        query = f"""
        SELECT
            SNOWFLAKE.CORTEX.DATA_AGENT_RUN(
                '{agent_name}',
                $$ {request_json} $$
            ) AS RESPONSE
        """

        result = session.sql(query).collect()

        if not result:
            return "No response was returned from the Supply Chain Agent."

        raw_response = result[0]["RESPONSE"]

        # ----------------------------------------------------
        # PARSE RESPONSE
        # ----------------------------------------------------

        if isinstance(raw_response, str):

            try:
                response_json = json.loads(raw_response)
            except Exception:
                return raw_response

        else:

            response_json = raw_response

        # ----------------------------------------------------
        # GET TEXT FROM RESPONSE
        # ----------------------------------------------------

        if isinstance(response_json, dict):

            if "content" in response_json:

                content = response_json["content"]

                if isinstance(content, list):

                    text_parts = []

                    for item in content:

                        if isinstance(item, dict):

                            if item.get("type") == "text":

                                text_parts.append(
                                    item.get("text", "")
                                )

                    if text_parts:

                        return "\n".join(text_parts)

            if "message" in response_json:

                return str(response_json["message"])

            if "response" in response_json:

                return str(response_json["response"])

        return str(response_json)

    except Exception as e:

        return f"⚠️ Error while calling Supply Chain Agent: {str(e)}"


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
<style>

/* ============================================================
   REMOVE STREAMLIT DEFAULT UI
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
    max-width: none !important;
}

[data-testid="stAppViewContainer"] {
    padding: 0 !important;
}

[data-testid="stMainBlockContainer"] {
    padding: 0 !important;
    margin: 0 !important;
    max-width: none !important;
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

    background: #ffffff !important;

    border-right: 1px solid #d8e2ef;

    z-index: 2000 !important;
}

section[data-testid="stSidebar"] > div {

    width: 350px !important;

    padding: 0 !important;

}


/* ============================================================
   SIDEBAR CONTENT
   ============================================================ */

.sidebar-inner {

    padding: 18px 28px 30px 28px;

    box-sizing: border-box;

}


/* ============================================================
   DILYTICS LOGO
   ============================================================ */

.dilytics-logo {

    width: 190px;

    height: 58px;

    background: #e50909;

    color: #ffffff;

    display: flex;

    align-items: center;

    justify-content: center;

    font-family: Arial, sans-serif;

    font-size: 26px;

    font-weight: 800;

    letter-spacing: 1px;

    margin-bottom: 28px;

}


/* ============================================================
   SEMANTIC MART
   ============================================================ */

.semantic-live {

    display: inline-flex;

    align-items: center;

    gap: 8px;

    padding: 9px 15px;

    border-radius: 24px;

    border: 1px solid #9ee5cb;

    background: #f2fff9;

    color: #08775d;

    font-family: Arial, sans-serif;

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

    width: 100%;

    height: 50px;

    border: 1px solid #cdd8e6;

    border-radius: 9px;

    display: flex;

    align-items: center;

    justify-content: center;

    color: #092d61;

    font-family: Arial, sans-serif;

    font-size: 15px;

    margin-bottom: 28px;

    box-sizing: border-box;

}


/* ============================================================
   SIDEBAR DIVIDER
   ============================================================ */

.sidebar-divider {

    height: 1px;

    width: 100%;

    background: #d9e2ed;

    margin: 0 0 28px 0;

}


/* ============================================================
   SIDEBAR HEADING
   ============================================================ */

.sidebar-heading {

    color: #092d61;

    font-family: Arial, sans-serif;

    font-size: 15px;

    font-weight: 700;

    margin-bottom: 26px;

}


/* ============================================================
   RECENT CHAT
   ============================================================ */

.no-recent {

    color: #71809a;

    font-family: Arial, sans-serif;

    font-size: 14px;

    margin-bottom: 30px;

}


/* ============================================================
   QUICK LINKS
   ============================================================ */

.quick-link {

    height: 52px;

    display: flex;

    align-items: center;

    color: #173860;

    font-family: Arial, sans-serif;

    font-size: 14px;

}

.quick-icon {

    width: 30px;

    font-size: 19px;

}

.quick-arrow {

    margin-left: auto;

    color: #174c91;

    font-size: 18px;

}


/* ============================================================
   MAIN AREA
   ============================================================ */

.main-area {

    margin-left: 350px;

    width: calc(100% - 350px);

    min-height: 100vh;

    background: #edf5ff;

}


/* ============================================================
   FIXED BLUE HEADER
   ============================================================ */

.blue-header {

    position: fixed;

    left: 350px;

    right: 0;

    top: 0;

    height: 84px;

    background: #0957d9;

    z-index: 1500;

    display: flex;

    align-items: center;

    padding: 0 30px;

    box-sizing: border-box;

}


/* ============================================================
   HEADER TITLE
   ============================================================ */

.header-main-title {

    color: white;

    font-family: Arial, sans-serif;

    font-size: 31px;

    font-weight: 700;

    margin-left: 28px;

    white-space: nowrap;

}


/* ============================================================
   HEADER RIGHT
   ============================================================ */

.header-right {

    margin-left: auto;

    display: flex;

    align-items: center;

    gap: 25px;

    color: white;

}

.header-bell {

    font-size: 25px;

}

.header-question {

    font-size: 22px;

}

.header-dot {

    font-size: 18px;

}


/* ============================================================
   HERO
   ============================================================ */

.hero {

    margin-left: 350px;

    margin-top: 84px;

    width: calc(100% - 350px);

    height: 365px;

    background:

        linear-gradient(
            135deg,
            #f4f8ff 0%,
            #e8f2ff 55%,
            #edf5ff 100%
        );

    display: flex;

    flex-direction: column;

    align-items: center;

    padding-top: 32px;

    box-sizing: border-box;

}


/* ============================================================
   BOT
   ============================================================ */

.bot-circle {

    width: 70px;

    height: 70px;

    background: white;

    border-radius: 50%;

    display: flex;

    align-items: center;

    justify-content: center;

    font-size: 32px;

    box-shadow:
        0 7px 20px rgba(40, 80, 140, 0.10);

    margin-bottom: 14px;

}


/* ============================================================
   HERO TITLE
   ============================================================ */

.hero-title {

    margin: 0;

    padding: 0;

    color: #092d61;

    font-family: Arial, sans-serif;

    font-size: 40px;

    font-weight: 750;

    line-height: 1.1;

    text-align: center;

}


/* ============================================================
   TITLE LINE
   ============================================================ */

.hero-line {

    width: 140px;

    height: 4px;

    background: #0b58d8;

    margin-top: 14px;

    margin-bottom: 14px;

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

.cards-container {

    margin-left: 350px;

    width: calc(100% - 350px);

    background: #edf5ff;

    padding: 18px 18px 20px 18px;

    box-sizing: border-box;

    display: grid;

    grid-template-columns:
        repeat(6, minmax(0, 1fr));

    gap: 16px;

}


.card {

    height: 145px;

    background: #ffffff;

    border: 1px solid #d4e1ef;

    border-radius: 15px;

    display: flex;

    flex-direction: column;

    align-items: center;

    justify-content: center;

    text-align: center;

    box-sizing: border-box;

}


.card-icon {

    font-size: 42px;

    line-height: 1;

    margin-bottom: 12px;

}


.card-text {

    color: #092d61;

    font-family: Arial, sans-serif;

    font-size: 15px;

    font-weight: 700;

    line-height: 1.3;

}


/* ============================================================
   SEARCH AREA
   ============================================================ */

.search-area {

    margin-left: 350px;

    width: calc(100% - 350px);

    background: #edf5ff;

    padding: 8px 8% 35px 8%;

    box-sizing: border-box;

}


/* ============================================================
   SEARCH BAR
   ============================================================ */

.search-decoration {

    height: 68px;

    width: 100%;

    border-radius: 40px;

    background: white;

    border: 1px solid #cbdced;

    box-shadow:

        0 4px 16px rgba(40, 80, 140, 0.08);

    display: flex;

    align-items: center;

    padding: 0 16px 0 25px;

    box-sizing: border-box;

}


.search-symbol {

    font-size: 29px;

    margin-right: 16px;

}


.search-text {

    flex: 1;

    color: #7b8da5;

    font-family: Arial, sans-serif;

    font-size: 16px;

}


.search-circle {

    width: 48px;

    height: 48px;

    border-radius: 50%;

    background: #0957d9;

    color: white;

    display: flex;

    align-items: center;

    justify-content: center;

    font-size: 23px;

}


/* ============================================================
   ACTUAL STREAMLIT CHAT INPUT
   ============================================================ */

[data-testid="stChatInput"] {

    position: fixed !important;

    left: calc(350px + 8%) !important;

    right: 8% !important;

    bottom: 22px !important;

    width: auto !important;

    z-index: 1800 !important;

}


[data-testid="stChatInput"] > div {

    border-radius: 40px !important;

    border: 1px solid #cbdced !important;

    background: white !important;

    box-shadow:
        0 4px 16px rgba(40, 80, 140, 0.08) !important;

}


/* ============================================================
   CHAT HISTORY
   ============================================================ */

.chat-history {

    margin-left: 350px;

    width: calc(100% - 350px);

    padding: 15px 8% 120px 8%;

    box-sizing: border-box;

    background: #edf5ff;

}


.chat-user {

    background: white;

    border: 1px solid #d8e2ef;

    border-radius: 12px;

    padding: 13px 18px;

    margin-bottom: 10px;

    color: #173860;

    font-family: Arial, sans-serif;

}


.chat-assistant {

    background: #f7fbff;

    border: 1px solid #d8e2ef;

    border-radius: 12px;

    padding: 13px 18px;

    margin-bottom: 15px;

    color: #173860;

    font-family: Arial, sans-serif;

}


/* ============================================================
   RESPONSIVE
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

    .main-area {

        margin-left: 300px;

        width: calc(100% - 300px);

    }

    .blue-header {

        left: 300px;

    }

    .hero {

        margin-left: 300px;

        width: calc(100% - 300px);

    }

    .cards-container,

    .search-area,

    .chat-history {

        margin-left: 300px;

        width: calc(100% - 300px);

    }

    [data-testid="stChatInput"] {

        left: calc(300px + 6%) !important;

        right: 6% !important;

    }

    .hero-title {

        font-size: 34px;

    }

    .cards-container {

        gap: 10px;

        padding-left: 12px;

        padding-right: 12px;

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
        <div class="sidebar-inner">

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
# BLUE HEADER
# ============================================================

st.markdown(
    """
    <div class="blue-header">

        <div class="header-main-title">
            Dilytics Supply Chain AI
        </div>

        <div class="header-right">

            <span class="header-bell">
                🔔
            </span>

            <span class="header-question">
                ?
            </span>

            <span class="header-dot">
                ●
            </span>

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

        <div class="bot-circle">
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
# SIX CARDS
# ============================================================

st.markdown(
    """
    <div class="cards-container">

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
# DECORATIVE SEARCH BAR
# ============================================================

st.markdown(
    """
    <div class="search-area">

        <div class="search-decoration">

            <div class="search-symbol">
                🔍
            </div>

            <div class="search-text">
                Ask your supply chain question...
            </div>

            <div class="search-circle">
                ➤
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
        '<div class="chat-history">',
        unsafe_allow_html=True
    )

    for message in st.session_state.messages:

        if message["role"] == "user":

            st.markdown(
                f"""
                <div class="chat-user">
                    <b>👤 You</b><br><br>
                    {message["content"]}
                </div>
                """,
                unsafe_allow_html=True
            )

        else:

            st.markdown(
                f"""
                <div class="chat-assistant">
                    <b>🤖 Dilytics AI</b><br><br>
                    {message["content"]}
                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown(
        '</div>',
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

    st.session_state.recent_chats.append(question)

    with st.spinner("Thinking..."):

        answer = ask_agent(question)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )

    st.rerun()
