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
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "recent_chats" not in st.session_state:
    st.session_state.recent_chats = []


# ============================================================
# CSS
# ============================================================

st.html("""
<style>

/* =========================================================
   GLOBAL
   ========================================================= */

html, body {
    margin: 0;
    padding: 0;
}

.stApp {
    background: #f4f8ff;
}

.block-container {
    padding: 0 !important;
    margin: 0 !important;
    max-width: 100% !important;
}

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

header {
    visibility: hidden;
}


/* =========================================================
   TOP BLUE HEADER
   ========================================================= */

.top-header {
    width: 100%;
    height: 84px;

    background: #0754d8;

    display: flex;
    align-items: center;

    padding: 0 34px;

    box-sizing: border-box;
}


/* =========================================================
   DILYTICS LOGO
   ========================================================= */

.dilytics-logo {
    width: 190px;
    height: 64px;

    background: #e00000;

    color: white;

    display: flex;
    align-items: center;
    justify-content: center;

    font-family: Arial, sans-serif;

    font-size: 27px;
    font-weight: 800;

    letter-spacing: 1px;

    flex-shrink: 0;
}


/* =========================================================
   HEADER DIVIDER
   ========================================================= */

.header-divider {
    width: 2px;
    height: 48px;

    background: rgba(255,255,255,0.75);

    margin-left: 28px;
    margin-right: 28px;
}


/* =========================================================
   STATIC HEADER TITLE
   ========================================================= */

.header-title {
    color: white;

    font-family: Arial, sans-serif;

    font-size: 30px;

    font-weight: 700;

    white-space: nowrap;
}


/* =========================================================
   HEADER RIGHT
   ========================================================= */

.header-right {
    margin-left: auto;

    display: flex;
    align-items: center;

    gap: 25px;

    color: white;

    font-size: 23px;
}


/* =========================================================
   SIDEBAR
   ========================================================= */

section[data-testid="stSidebar"] {

    background: #ffffff;

    border-right: 1px solid #d9e2ef;
}


section[data-testid="stSidebar"] > div {

    padding-top: 18px;
    padding-left: 14px;
    padding-right: 14px;
}


/* =========================================================
   SIDEBAR STATUS
   ========================================================= */

.semantic-status {

    display: inline-flex;

    align-items: center;

    gap: 7px;

    background: #ecfbf4;

    border: 1px solid #a9ecd0;

    color: #087752;

    border-radius: 20px;

    padding: 7px 14px;

    font-size: 13px;

    font-weight: 600;

    margin-bottom: 18px;
}


.status-dot {

    width: 8px;
    height: 8px;

    background: #18a974;

    border-radius: 50%;
}


/* =========================================================
   SIDEBAR BUTTON
   ========================================================= */

section[data-testid="stSidebar"] .stButton > button {

    height: 43px;

    border-radius: 8px;

    font-size: 14px;

    font-weight: 500;
}


/* =========================================================
   SIDEBAR HEADINGS
   ========================================================= */

.sidebar-heading {

    color: #13284d;

    font-size: 14px;

    font-weight: 700;

    margin-top: 17px;

    margin-bottom: 10px;
}


.sidebar-line {

    height: 1px;

    background: #dce4ee;

    margin: 17px 0;
}


.recent-chat {

    color: #66738a;

    font-size: 13px;

    padding: 7px 2px;
}


/* =========================================================
   QUICK LINKS
   ========================================================= */

.quick-link {

    display: flex;

    align-items: center;

    justify-content: space-between;

    padding: 8px 3px;

    color: #1a2b4d;

    font-size: 13px;
}


.quick-left {

    display: flex;

    align-items: center;

    gap: 9px;
}


/* =========================================================
   MAIN PAGE
   ========================================================= */

.main-area {

    width: 100%;

    background:
        radial-gradient(
            circle at 50% 25%,
            #ffffff 0%,
            #eef5ff 55%,
            #e4efff 100%
        );

    min-height: calc(100vh - 84px);

    padding-bottom: 25px;

    box-sizing: border-box;
}


/* =========================================================
   HERO
   ========================================================= */

.hero {

    width: 100%;

    text-align: center;

    padding-top: 34px;

    box-sizing: border-box;
}


/* =========================================================
   BOT CIRCLE
   ========================================================= */

.bot-circle {

    width: 70px;
    height: 70px;

    margin: 0 auto 17px auto;

    background: white;

    border-radius: 50%;

    display: flex;

    align-items: center;

    justify-content: center;

    font-size: 34px;

    box-shadow:
        0 7px 20px rgba(20,70,150,0.11);
}


/* =========================================================
   MAIN TITLE
   ========================================================= */

.hero-title {

    margin: 0;

    padding: 0;

    color: #102a56;

    font-family: Arial, sans-serif;

    font-size: 40px;

    font-weight: 750;

    line-height: 1.2;

    white-space: nowrap;
}


/* =========================================================
   TITLE LINE
   ========================================================= */

.title-line {

    width: 140px;

    height: 4px;

    background: #0754d8;

    margin: 17px auto 18px auto;
}


/* =========================================================
   SUBTITLE
   ========================================================= */

.hero-subtitle {

    color: #29466f;

    font-family: Arial, sans-serif;

    font-size: 17px;

    line-height: 1.4;

    margin: 0;
}


/* =========================================================
   CARDS
   ========================================================= */

.cards-wrapper {

    width: calc(100% - 70px);

    max-width: 1500px;

    margin: 42px auto 0 auto;
}


/* =========================================================
   CARD
   ========================================================= */

.question-card {

    height: 125px;

    background: #ffffff;

    border: 1px solid #d7e2f0;

    border-radius: 15px;

    display: flex;

    flex-direction: column;

    align-items: center;

    justify-content: center;

    text-align: center;

    box-sizing: border-box;

    box-shadow:
        0 4px 13px rgba(30,70,140,0.06);
}


.question-icon {

    font-size: 34px;

    line-height: 1;

    margin-bottom: 12px;
}


.question-title {

    color: #102a56;

    font-size: 15px;

    font-weight: 700;

    line-height: 1.25;
}


/* =========================================================
   SEARCH AREA
   ========================================================= */

.search-wrapper {

    width: calc(100% - 140px);

    max-width: 1250px;

    margin: 32px auto 0 auto;
}


/* =========================================================
   VISUAL SEARCH BAR
   ========================================================= */

.search-box {

    width: 100%;

    height: 62px;

    background: white;

    border: 1px solid #d1ddec;

    border-radius: 32px;

    display: flex;

    align-items: center;

    padding: 0 12px 0 22px;

    box-sizing: border-box;

    box-shadow:
        0 4px 16px rgba(20,70,140,0.10);
}


.search-icon {

    font-size: 27px;

    margin-right: 14px;
}


.search-placeholder {

    flex: 1;

    color: #8290a5;

    font-size: 16px;
}


.search-button {

    width: 46px;
    height: 46px;

    border-radius: 50%;

    background: #0754d8;

    color: white;

    display: flex;

    align-items: center;

    justify-content: center;

    font-size: 22px;
}


/* =========================================================
   REAL STREAMLIT CHAT INPUT
   ========================================================= */

div[data-testid="stChatInput"] {

    width: calc(100% - 140px) !important;

    max-width: 1250px !important;

    margin: 12px auto 0 auto !important;
}


div[data-testid="stChatInput"] textarea {

    border-radius: 30px !important;
}


/* =========================================================
   CHAT MESSAGES
   ========================================================= */

.chat-message {

    width: calc(100% - 140px);

    max-width: 1250px;

    margin: 15px auto;

    padding: 15px 20px;

    background: white;

    border: 1px solid #dce5f2;

    border-radius: 13px;

    box-shadow:
        0 4px 14px rgba(30,70,140,0.06);

    box-sizing: border-box;
}


/* =========================================================
   RESPONSIVE
   ========================================================= */

@media (max-width: 1100px) {

    .dilytics-logo {
        width: 160px;
        font-size: 23px;
    }

    .header-title {
        font-size: 24px;
    }

    .hero-title {
        font-size: 34px;
    }

    .cards-wrapper {
        width: calc(100% - 35px);
    }

}


@media (max-width: 800px) {

    .header-title {
        display: none;
    }

    .header-divider {
        display: none;
    }

    .hero-title {
        font-size: 30px;
        white-space: normal;
    }

    .search-wrapper {
        width: calc(100% - 35px);
    }

    div[data-testid="stChatInput"] {
        width: calc(100% - 35px) !important;
    }

}

</style>
""")


# ============================================================
# HEADER
# ============================================================

st.html("""
<div class="top-header">

    <div class="dilytics-logo">
        DILYTICS
    </div>

    <div class="header-divider"></div>

    <div class="header-title">
        Dilytics Supply Chain AI
    </div>

    <div class="header-right">
        <span>🔔</span>
        <span>?</span>
        <span>●</span>
    </div>

</div>
""")


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.html("""
    <div class="semantic-status">
        <span class="status-dot"></span>
        Semantic Mart Live
    </div>
    """)


    if st.button(
        "＋  New Chat",
        use_container_width=True
    ):

        st.session_state.messages = []

        st.rerun()


    st.html("""
    <div class="sidebar-line"></div>

    <div class="sidebar-heading">
        ◷ &nbsp; Recent Conversations
    </div>
    """)


    if st.session_state.recent_chats:

        for chat in reversed(
            st.session_state.recent_chats[-5:]
        ):

            display_chat = chat

            if len(display_chat) > 35:
                display_chat = display_chat[:35] + "..."

            st.html(f"""
            <div class="recent-chat">
                💬 &nbsp; {display_chat}
            </div>
            """)

    else:

        st.html("""
        <div class="recent-chat">
            No recent conversations
        </div>
        """)


    st.html("""
    <div class="sidebar-line"></div>

    <div class="sidebar-heading">
        🔗 &nbsp; Quick Links
    </div>
    """)


    quick_links = [
        ("📋", "Purchase Orders"),
        ("🚚", "Shipments"),
        ("📦", "Inventory"),
        ("👥", "Suppliers"),
        ("🏭", "Warehouses"),
        ("🚛", "Carriers"),
        ("🛍️", "Products")
    ]


    for icon, name in quick_links:

        st.html(f"""
        <div class="quick-link">

            <div class="quick-left">

                <span>{icon}</span>

                <span>{name}</span>

            </div>

            <span>›</span>

        </div>
        """)


    st.html("""
    <div class="sidebar-line"></div>
    """)


    if st.button(
        "🗑️  Clear All Sessions",
        use_container_width=True
    ):

        st.session_state.messages = []

        st.session_state.recent_chats = []

        st.rerun()


# ============================================================
# MAIN AREA
# ============================================================

st.html("""
<div class="main-area">

    <div class="hero">

        <div class="bot-circle">
            🤖
        </div>

        <h1 class="hero-title">
            Dilytics Supply Chain AI
        </h1>

        <div class="title-line"></div>

        <div class="hero-subtitle">
            Ask anything about your supply chain data in natural language.
        </div>

    </div>

</div>
""")


# ============================================================
# QUESTION CARDS
# ============================================================

st.html("""
<div class="cards-wrapper">
</div>
""")


col1, col2, col3, col4, col5, col6 = st.columns(
    6,
    gap="small"
)


cards = [

    ("📋", "Purchase<br>Orders"),

    ("🚚", "Shipments<br>& Deliveries"),

    ("📊", "Inventory<br>& Warehouses"),

    ("👥", "Suppliers"),

    ("📦", "Products"),

    ("📈", "Analytics<br>& Reports")

]


for col, (icon, title) in zip(
    [col1, col2, col3, col4, col5, col6],
    cards
):

    with col:

        st.html(f"""
        <div class="question-card">

            <div class="question-icon">
                {icon}
            </div>

            <div class="question-title">
                {title}
            </div>

        </div>
        """)


# ============================================================
# SEARCH BAR
# ============================================================

st.html("""
<div class="search-wrapper">

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
""")


# ============================================================
# YOUR ACTUAL CHAT INPUT
# ============================================================

question = st.chat_input(
    "Ask your supply chain question..."
)


if question:

    # --------------------------------------------------------
    # SAVE USER QUESTION
    # --------------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question
        }
    )


    st.session_state.recent_chats.append(
        question
    )


    # ========================================================
    # IMPORTANT
    # ========================================================
    #
    # PUT YOUR EXISTING WORKING SNOWFLAKE AGENT FUNCTION HERE.
    #
    # For example:
    #
    # response = ask_agent(question)
    #
    # DO NOT use SNOWFLAKE.CORTEX.COMPLETE here if your
    # account is a trial account.
    # ========================================================

    response = (
        "Your Supply Chain AI received your question:\n\n"
        + question
    )


    # --------------------------------------------------------
    # SAVE RESPONSE
    # --------------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response
        }
    )


# ============================================================
# DISPLAY CHAT HISTORY
# ============================================================

if st.session_state.messages:

    for message in st.session_state.messages:

        if message["role"] == "user":

            st.markdown(
                f"""
                <div class="chat-message">

                    <b style="color:#0754d8;">
                        👤 You
                    </b>

                    <div style="
                        margin-top:7px;
                        color:#172b50;
                        font-size:15px;
                    ">
                        {message["content"]}
                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )

        else:

            st.markdown(
                f"""
                <div class="chat-message">

                    <b style="color:#0754d8;">
                        🤖 Dilytics AI
                    </b>

                    <div style="
                        margin-top:7px;
                        color:#172b50;
                        font-size:15px;
                        line-height:1.5;
                    ">
                        {message["content"]}
                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )
