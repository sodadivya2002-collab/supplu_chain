import streamlit as st

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
# GLOBAL CSS
# ============================================================

st.markdown("""
<style>

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

header[data-testid="stHeader"] {
    display: none;
}

/* Remove Streamlit default spacing */
.block-container {
    padding: 0 !important;
    margin: 0 !important;
    max-width: 100% !important;
}

[data-testid="stAppViewContainer"] {
    padding: 0 !important;
    margin: 0 !important;
}

[data-testid="stAppViewContainer"] > .main {
    padding: 0 !important;
    margin: 0 !important;
}

[data-testid="stMainBlockContainer"] {
    padding: 0 !important;
    margin: 0 !important;
    max-width: 100% !important;
}

/* =========================================================
   SIDEBAR
   ========================================================= */

section[data-testid="stSidebar"] {
    width: 282px !important;
    min-width: 282px !important;
    max-width: 282px !important;

    background: #ffffff !important;

    border-right: 1px solid #d9e2ef;

    position: fixed !important;
    left: 0 !important;
    top: 0 !important;
    bottom: 0 !important;

    z-index: 1000 !important;
}

section[data-testid="stSidebar"] > div {
    width: 282px !important;
    padding: 0 !important;
}

/* Sidebar scrolling */
section[data-testid="stSidebar"] .block-container {
    padding: 0 20px !important;
}

/* =========================================================
   SIDEBAR LOGO
   ========================================================= */

.sidebar-logo {
    width: 220px;
    height: 58px;

    background: #ed1111;

    margin: 24px auto 28px auto;

    display: flex;
    align-items: center;
    justify-content: center;

    color: white;

    font-family: Arial, sans-serif;

    font-size: 26px;
    font-weight: 800;

    letter-spacing: 1px;
}

/* =========================================================
   SIDEBAR STATUS
   ========================================================= */

.semantic-status {
    width: 190px;
    height: 42px;

    margin: 0 auto 30px auto;

    border: 1px solid #9ee8cf;

    border-radius: 24px;

    background: #f4fffb;

    display: flex;
    align-items: center;
    justify-content: center;

    font-family: Arial, sans-serif;

    font-size: 14px;
    font-weight: 600;

    color: #087b61;
}

.semantic-dot {
    width: 10px;
    height: 10px;

    border-radius: 50%;

    background: #16a879;

    margin-right: 8px;
}

/* =========================================================
   NEW CHAT
   ========================================================= */

.new-chat-box {
    width: 100%;
    height: 50px;

    border: 1px solid #cfd9e6;

    border-radius: 10px;

    display: flex;
    align-items: center;
    justify-content: center;

    font-family: Arial, sans-serif;

    font-size: 15px;

    color: #092d62;

    margin-bottom: 28px;

    background: white;
}

/* =========================================================
   SIDEBAR SECTIONS
   ========================================================= */

.sidebar-line {
    width: 100%;
    height: 1px;

    background: #d9e2ef;

    margin: 0 0 25px 0;
}

.sidebar-heading {
    font-family: Arial, sans-serif;

    font-size: 15px;
    font-weight: 700;

    color: #072d63;

    margin-bottom: 28px;
}

.sidebar-empty {
    font-family: Arial, sans-serif;

    font-size: 14px;

    color: #7d8ba0;

    margin-bottom: 30px;
}

.quick-link {
    height: 54px;

    display: flex;

    align-items: center;

    font-family: Arial, sans-serif;

    font-size: 15px;

    color: #092d62;
}

.quick-icon {
    width: 30px;

    font-size: 20px;
}

.quick-arrow {
    margin-left: auto;

    color: #275b9e;

    font-size: 17px;
}

/* =========================================================
   MAIN AREA
   ========================================================= */

.main-wrapper {
    margin-left: 282px;

    width: calc(100% - 282px);

    min-height: 100vh;

    background: #eef5ff;
}

/* =========================================================
   TOP BLUE HEADER
   ========================================================= */

.top-header {
    position: fixed;

    left: 282px;
    right: 0;

    top: 0;

    height: 88px;

    background: #1057d5;

    z-index: 900;

    display: flex;

    align-items: center;

    padding: 0 32px;

    box-sizing: border-box;
}

.header-title {
    color: white;

    font-family: Arial, sans-serif;

    font-size: 32px;

    font-weight: 700;

    margin-left: 30px;
}

.header-divider {
    width: 2px;

    height: 48px;

    background: rgba(255,255,255,0.7);

    margin-left: 0;
}

.header-right {
    margin-left: auto;

    display: flex;

    align-items: center;

    gap: 28px;

    color: white;

    font-size: 25px;
}

.header-bell {
    font-size: 27px;
}

.header-question {
    font-size: 23px;
}

.header-user {
    font-size: 20px;
}

/* =========================================================
   HERO
   ========================================================= */

.hero {
    margin-top: 88px;

    height: 440px;

    background:
        linear-gradient(
            135deg,
            #f4f8ff 0%,
            #e8f2ff 50%,
            #edf5ff 100%
        );

    display: flex;

    flex-direction: column;

    align-items: center;

    justify-content: flex-start;

    box-sizing: border-box;

    padding-top: 48px;
}

/* Robot */

.bot-circle {
    width: 82px;
    height: 82px;

    border-radius: 50%;

    background: white;

    box-shadow: 0 8px 25px rgba(36, 82, 145, 0.10);

    display: flex;

    align-items: center;

    justify-content: center;

    font-size: 38px;

    margin-bottom: 18px;
}

/* Hero title */

.hero-title {
    margin: 0;

    padding: 0;

    color: #092d62;

    font-family: Arial, sans-serif;

    font-size: 42px;

    font-weight: 750;

    line-height: 1.15;

    text-align: center;
}

/* Blue underline */

.hero-line {
    width: 150px;

    height: 4px;

    background: #1458d4;

    margin-top: 18px;

    margin-bottom: 18px;
}

/* Subtitle */

.hero-subtitle {
    margin: 0;

    padding: 0;

    color: #153e70;

    font-family: Arial, sans-serif;

    font-size: 18px;

    text-align: center;
}

/* =========================================================
   CATEGORY CARDS
   ========================================================= */

.cards-area {
    background: #eef5ff;

    padding: 0 26px 30px 26px;

    display: grid;

    grid-template-columns:
        repeat(6, minmax(0, 1fr));

    gap: 20px;

    box-sizing: border-box;
}

.category-card {
    height: 184px;

    background: white;

    border: 1px solid #d4e1f1;

    border-radius: 18px;

    box-shadow:
        0 5px 15px rgba(38, 83, 139, 0.05);

    display: flex;

    flex-direction: column;

    align-items: center;

    justify-content: center;

    text-align: center;

    box-sizing: border-box;
}

.category-icon {
    font-size: 48px;

    line-height: 1;

    margin-bottom: 18px;
}

.category-name {
    color: #092d62;

    font-family: Arial, sans-serif;

    font-size: 16px;

    font-weight: 700;

    line-height: 1.35;
}

/* =========================================================
   SEARCH AREA
   ========================================================= */

.search-area {
    background: #eef5ff;

    padding: 12px 8% 32px 8%;

    box-sizing: border-box;
}

.search-box {
    height: 82px;

    width: 100%;

    background: white;

    border: 1px solid #cbdced;

    border-radius: 45px;

    box-shadow:
        0 5px 18px rgba(38, 83, 139, 0.08);

    display: flex;

    align-items: center;

    padding: 0 18px 0 28px;

    box-sizing: border-box;
}

.search-icon {
    font-size: 34px;

    margin-right: 20px;
}

.search-placeholder {
    color: #7b8ba2;

    font-family: Arial, sans-serif;

    font-size: 17px;

    flex: 1;
}

.search-button {
    width: 54px;

    height: 54px;

    border-radius: 50%;

    background: #1057d5;

    color: white;

    display: flex;

    align-items: center;

    justify-content: center;

    font-size: 28px;
}

/* =========================================================
   STREAMLIT CHAT INPUT
   ========================================================= */

[data-testid="stChatInput"] {
    position: fixed !important;

    left: calc(282px + 8%) !important;

    right: 8% !important;

    bottom: 25px !important;

    width: auto !important;

    z-index: 950 !important;
}

[data-testid="stChatInput"] > div {
    border-radius: 45px !important;

    border: 1px solid #cbdced !important;

    background: white !important;

    box-shadow:
        0 5px 18px rgba(38, 83, 139, 0.08) !important;
}

[data-testid="stChatInput"] textarea {
    font-size: 17px !important;

    padding-left: 20px !important;
}

/* =========================================================
   RESPONSIVE
   ========================================================= */

@media (max-width: 1200px) {

    section[data-testid="stSidebar"] {
        width: 250px !important;
        min-width: 250px !important;
        max-width: 250px !important;
    }

    section[data-testid="stSidebar"] > div {
        width: 250px !important;
    }

    .main-wrapper {
        margin-left: 250px;
        width: calc(100% - 250px);
    }

    .top-header {
        left: 250px;
    }

    [data-testid="stChatInput"] {
        left: calc(250px + 6%) !important;
        right: 6% !important;
    }

    .hero-title {
        font-size: 36px;
    }

    .cards-area {
        gap: 12px;
        padding-left: 18px;
        padding-right: 18px;
    }

    .category-card {
        height: 165px;
    }

    .category-icon {
        font-size: 40px;
    }
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        '<div class="sidebar-logo">DILYTICS</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '''
        <div class="semantic-status">
            <span class="semantic-dot"></span>
            Semantic Mart Live
        </div>
        ''',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="new-chat-box">＋&nbsp; New Chat</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="sidebar-line"></div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="sidebar-heading">◷ &nbsp; Recent Conversations</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="sidebar-empty">No recent conversations</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="sidebar-line"></div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="sidebar-heading">🔗 &nbsp; Quick Links</div>',
        unsafe_allow_html=True
    )

    links = [
        ("📋", "Purchase Orders"),
        ("🚚", "Shipments"),
        ("📦", "Inventory"),
        ("👥", "Suppliers"),
        ("🏭", "Warehouses"),
        ("🚛", "Carriers"),
        ("📦", "Products"),
    ]

    for icon, name in links:

        st.markdown(
            f'''
            <div class="quick-link">
                <span class="quick-icon">{icon}</span>
                <span>{name}</span>
                <span class="quick-arrow">›</span>
            </div>
            ''',
            unsafe_allow_html=True
        )

    st.markdown(
        '<div style="height:25px;"></div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '''
        <div class="new-chat-box">
            🗑️ &nbsp; Clear All Sessions
        </div>
        ''',
        unsafe_allow_html=True
    )


# ============================================================
# MAIN AREA
# ============================================================

st.markdown('<div class="main-wrapper">', unsafe_allow_html=True)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '''
    <div class="top-header">

        <div class="header-divider"></div>

        <div class="header-title">
            Dilytics Supply Chain AI
        </div>

        <div class="header-right">
            <span class="header-bell">🔔</span>
            <span class="header-question">?</span>
            <span class="header-user">●</span>
        </div>

    </div>
    ''',
    unsafe_allow_html=True
)


# ============================================================
# HERO
# ============================================================

st.markdown(
    '''
    <div class="hero">

        <div class="bot-circle">
            🤖
        </div>

        <h1 class="hero-title">
            Dilytics Supply Chain AI
        </h1>

        <div class="hero-line"></div>

        <div class="hero-subtitle">
            Ask anything about your supply chain data in natural language.
        </div>

    </div>
    ''',
    unsafe_allow_html=True
)


# ============================================================
# CATEGORY CARDS
# ============================================================

st.markdown(
    '''
    <div class="cards-area">

        <div class="category-card">
            <div class="category-icon">📋</div>
            <div class="category-name">
                Purchase<br>Orders
            </div>
        </div>

        <div class="category-card">
            <div class="category-icon">🚚</div>
            <div class="category-name">
                Shipments<br>& Deliveries
            </div>
        </div>

        <div class="category-card">
            <div class="category-icon">📊</div>
            <div class="category-name">
                Inventory<br>& Warehouses
            </div>
        </div>

        <div class="category-card">
            <div class="category-icon">👥</div>
            <div class="category-name">
                Suppliers
            </div>
        </div>

        <div class="category-card">
            <div class="category-icon">📦</div>
            <div class="category-name">
                Products
            </div>
        </div>

        <div class="category-card">
            <div class="category-icon">📈</div>
            <div class="category-name">
                Analytics<br>& Reports
            </div>
        </div>

    </div>
    ''',
    unsafe_allow_html=True
)


# ============================================================
# SEARCH DECORATION
# ============================================================

st.markdown(
    '''
    <div class="search-area">

        <div class="search-box">

            <div class="search-icon">
                🔍
            </div>

            <div class="search-placeholder">
                Ask your supply chain question...
            </div>

            <div class="search-button">
                ➤
            </div>

        </div>

    </div>
    ''',
    unsafe_allow_html=True
)


st.markdown('</div>', unsafe_allow_html=True)


# ============================================================
# CHAT FUNCTION
# ============================================================
#
# IMPORTANT:
# Replace ONLY this function with your CURRENT WORKING
# Snowflake Agent function.
#
# Do NOT use SNOWFLAKE.CORTEX.COMPLETE here if your trial
# account does not support COMPLETE.
# ============================================================

def ask_agent(question):
    """
    PUT YOUR EXISTING WORKING AGENT CODE HERE.

    Example:

        response = agent.run(question)
        return response

    """

    # TEMPORARY RESPONSE
    # Replace this with your existing Agent call.
    return (
        "Your Supply Chain Agent is connected. "
        "Replace the ask_agent() function with your existing "
        "working Agent logic."
    )


# ============================================================
# CHAT
# ============================================================

if "messages" not in st.session_state:

    st.session_state.messages = []


for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])


# ============================================================
# CHAT INPUT
# ============================================================

if question := st.chat_input(
    "Ask your supply chain question..."
):

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question
        }
    )

    with st.chat_message("user"):

        st.markdown(question)

    with st.chat_message("assistant"):

        with st.spinner("Thinking..."):

            try:

                answer = ask_agent(question)

            except Exception as e:

                answer = f"⚠️ Error: {str(e)}"

        st.markdown(answer)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )
