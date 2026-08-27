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

/* ============================================================
   GLOBAL RESET
   ============================================================ */

html, body {
    margin: 0 !important;
    padding: 0 !important;
}

.stApp {
    background: #eef5ff;
}

.block-container {
    padding: 0 !important;
    margin: 0 !important;
    max-width: 100% !important;
}

header {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

#MainMenu {
    visibility: hidden;
}


/* ============================================================
   SIDEBAR
   ============================================================ */

section[data-testid="stSidebar"] {
    background: #ffffff;
    border-right: 1px solid #d7e0ec;
}

section[data-testid="stSidebar"] > div {
    padding-top: 20px !important;
    padding-left: 14px !important;
    padding-right: 14px !important;
}


/* ============================================================
   SIDEBAR STATUS
   ============================================================ */

.semantic-status {
    display: inline-flex;
    align-items: center;
    gap: 7px;

    padding: 7px 14px;

    border: 1px solid #a9e8ce;
    border-radius: 22px;

    background: #effcf6;

    color: #087651;

    font-size: 13px;
    font-weight: 600;

    margin-bottom: 20px;
}

.status-dot {
    width: 8px;
    height: 8px;

    border-radius: 50%;

    background: #15a36f;
}


/* ============================================================
   SIDEBAR BUTTON
   ============================================================ */

section[data-testid="stSidebar"] .stButton > button {

    width: 100%;

    height: 45px;

    background: #ffffff;

    border: 1px solid #ccd5e1;

    border-radius: 9px;

    color: #122c55;

    font-size: 14px;

    font-weight: 500;
}


/* ============================================================
   SIDEBAR DIVIDER
   ============================================================ */

.sidebar-divider {
    width: 100%;

    height: 1px;

    background: #dce4ee;

    margin: 20px 0;
}


/* ============================================================
   SIDEBAR HEADINGS
   ============================================================ */

.sidebar-heading {

    color: #102b55;

    font-size: 14px;

    font-weight: 700;

    margin-bottom: 13px;
}


/* ============================================================
   RECENT CONVERSATION
   ============================================================ */

.recent-chat {

    color: #71809a;

    font-size: 13px;

    padding: 7px 2px;
}


/* ============================================================
   QUICK LINKS
   ============================================================ */

.quick-link {

    display: flex;

    align-items: center;

    justify-content: space-between;

    width: 100%;

    padding: 9px 2px;

    color: #17335f;

    font-size: 13px;
}

.quick-link-left {

    display: flex;

    align-items: center;

    gap: 10px;
}


/* ============================================================
   MAIN APPLICATION
   ============================================================ */

.main-container {

    width: 100%;

    min-height: 100vh;

    background: #eef5ff;

    overflow-x: hidden;
}


/* ============================================================
   TOP HEADER
   EXACTLY 70PX
   ============================================================ */

.top-header {

    width: 100%;

    height: 70px;

    background: #0754d8;

    display: flex;

    align-items: center;

    padding: 0 28px;

    box-sizing: border-box;
}


/* ============================================================
   DILYTICS LOGO
   ============================================================ */

.dilytics-logo {

    width: 190px;

    height: 54px;

    background: #df0000;

    display: flex;

    align-items: center;

    justify-content: center;

    color: #ffffff;

    font-family: Arial, sans-serif;

    font-size: 26px;

    font-weight: 800;

    letter-spacing: 1px;

    flex-shrink: 0;
}


/* ============================================================
   HEADER DIVIDER
   ============================================================ */

.header-divider {

    width: 2px;

    height: 43px;

    background: rgba(255,255,255,0.75);

    margin-left: 27px;

    margin-right: 27px;
}


/* ============================================================
   HEADER TITLE
   ============================================================ */

.header-title {

    color: #ffffff;

    font-family: Arial, sans-serif;

    font-size: 29px;

    font-weight: 700;

    white-space: nowrap;
}


/* ============================================================
   HEADER RIGHT ICONS
   ============================================================ */

.header-right {

    margin-left: auto;

    display: flex;

    align-items: center;

    gap: 24px;

    color: #ffffff;

    font-size: 21px;
}


/* ============================================================
   HERO SECTION
   ============================================================ */

.hero-section {

    width: 100%;

    background:
        radial-gradient(
            circle at 50% 15%,
            #ffffff 0%,
            #f5f9ff 40%,
            #e8f2ff 100%
        );

    text-align: center;

    padding-top: 25px;

    padding-bottom: 22px;

    box-sizing: border-box;
}


/* ============================================================
   BOT
   ============================================================ */

.bot-circle {

    width: 60px;

    height: 60px;

    margin: 0 auto 12px auto;

    background: #ffffff;

    border-radius: 50%;

    display: flex;

    align-items: center;

    justify-content: center;

    font-size: 29px;

    box-shadow:
        0 5px 17px rgba(30,70,140,0.11);
}


/* ============================================================
   MAIN TITLE
   ============================================================ */

.hero-title {

    margin: 0;

    padding: 0;

    color: #102b55;

    font-family: Arial, sans-serif;

    font-size: 37px;

    font-weight: 750;

    line-height: 1.15;
}


/* ============================================================
   BLUE LINE
   ============================================================ */

.title-line {

    width: 115px;

    height: 4px;

    background: #0754d8;

    margin: 11px auto 12px auto;
}


/* ============================================================
   SUBTITLE
   ============================================================ */

.hero-subtitle {

    margin: 0;

    padding: 0;

    color: #29466f;

    font-family: Arial, sans-serif;

    font-size: 16px;

    line-height: 1.3;
}


/* ============================================================
   CARDS SECTION
   ============================================================ */

.cards-section {

    width: 100%;

    padding: 20px 8px 0 8px;

    box-sizing: border-box;

    background: #eef5ff;
}


/* ============================================================
   CARD
   ============================================================ */

.question-card {

    width: 100%;

    height: 128px;

    background: #ffffff;

    border: 1px solid #d4e0ef;

    border-radius: 15px;

    display: flex;

    flex-direction: column;

    align-items: center;

    justify-content: center;

    text-align: center;

    box-sizing: border-box;

    box-shadow:
        0 3px 10px rgba(30,70,140,0.05);
}


/* ============================================================
   CARD ICON
   ============================================================ */

.question-icon {

    font-size: 35px;

    line-height: 1;

    margin-bottom: 10px;
}


/* ============================================================
   CARD TITLE
   ============================================================ */

.question-title {

    color: #102b55;

    font-size: 15px;

    font-weight: 700;

    line-height: 1.25;
}


/* ============================================================
   SEARCH AREA
   ============================================================ */

.search-area {

    width: 100%;

    background: #eef5ff;

    padding: 20px 0 25px 0;
}


/* ============================================================
   STREAMLIT CHAT INPUT
   ============================================================ */

div[data-testid="stChatInput"] {

    width: calc(100% - 120px) !important;

    max-width: 1250px !important;

    margin: 0 auto !important;
}


/* ============================================================
   CHAT INPUT CONTAINER
   ============================================================ */

div[data-testid="stChatInput"] > div {

    border-radius: 35px !important;

    border: 1px solid #cbd9ea !important;

    background: #ffffff !important;

    box-shadow:
        0 4px 15px rgba(30,70,140,0.09) !important;
}


/* ============================================================
   CHAT TEXT
   ============================================================ */

div[data-testid="stChatInput"] textarea {

    font-size: 16px !important;

    color: #19365f !important;
}


/* ============================================================
   CHAT HISTORY
   ============================================================ */

.chat-area {

    width: calc(100% - 120px);

    max-width: 1250px;

    margin: 15px auto;

    box-sizing: border-box;
}


.chat-message {

    background: #ffffff;

    border: 1px solid #d8e2ef;

    border-radius: 13px;

    padding: 15px 20px;

    margin-bottom: 12px;

    color: #172f56;

    font-size: 15px;

    line-height: 1.5;
}


/* ============================================================
   RESPONSIVE
   ============================================================ */

@media (max-width: 1100px) {

    .dilytics-logo {
        width: 160px;
        font-size: 22px;
    }

    .header-title {
        font-size: 24px;
    }

    .hero-title {
        font-size: 33px;
    }

    div[data-testid="stChatInput"] {
        width: calc(100% - 50px) !important;
    }

    .chat-area {
        width: calc(100% - 50px);
    }
}


@media (max-width: 750px) {

    .header-title {
        display: none;
    }

    .header-divider {
        display: none;
    }

    .dilytics-logo {
        width: 150px;
    }

    .hero-title {
        font-size: 29px;
    }

}

</style>
""")


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    # Status
    st.html("""
    <div class="semantic-status">
        <span class="status-dot"></span>
        Semantic Mart Live
    </div>
    """)

    # New Chat
    if st.button(
        "＋  New Chat",
        use_container_width=True
    ):
        st.session_state.messages = []
        st.rerun()

    # Divider
    st.html("""
    <div class="sidebar-divider"></div>

    <div class="sidebar-heading">
        ◷ &nbsp; Recent Conversations
    </div>
    """)

    # Recent conversations
    if st.session_state.recent_chats:

        for chat in reversed(
            st.session_state.recent_chats[-5:]
        ):

            display_chat = chat

            if len(display_chat) > 34:
                display_chat = display_chat[:34] + "..."

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

    # Divider
    st.html("""
    <div class="sidebar-divider"></div>

    <div class="sidebar-heading">
        🔗 &nbsp; Quick Links
    </div>
    """)

    # Quick links
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

            <div class="quick-link-left">

                <span>{icon}</span>

                <span>{name}</span>

            </div>

            <span>›</span>

        </div>
        """)

    # Divider
    st.html("""
    <div class="sidebar-divider"></div>
    """)

    # Clear sessions
    if st.button(
        "🗑️  Clear All Sessions",
        use_container_width=True
    ):

        st.session_state.messages = []
        st.session_state.recent_chats = []

        st.rerun()


# ============================================================
# MAIN CONTAINER
# ============================================================

st.html("""
<div class="main-container">


    <!-- ====================================================
         TOP HEADER - 70 PX
         ==================================================== -->

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


    <!-- ====================================================
         HERO
         ==================================================== -->

    <div class="hero-section">

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
# SIX MAIN CARDS
# ============================================================

st.html("""
<div class="cards-section">
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


for column, (icon, title) in zip(
    [col1, col2, col3, col4, col5, col6],
    cards
):

    with column:

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
# SEARCH AREA
# ============================================================

st.html("""
<div class="search-area">
</div>
""")


# ============================================================
# CHAT INPUT
# ============================================================

question = st.chat_input(
    "Ask your supply chain question..."
)


# ============================================================
# YOUR EXISTING AGENT
# ============================================================

if question:

    # Save question
    st.session_state.messages.append(
        {
            "role": "user",
            "content": question
        }
    )

    # Save recent conversation
    st.session_state.recent_chats.append(
        question
    )


    # ========================================================
    # IMPORTANT:
    #
    # REPLACE THIS WITH YOUR CURRENT WORKING AGENT CALL.
    #
    # Example:
    #
    # response = ask_agent(question)
    #
    # or whatever function you currently use.
    # ========================================================

    response = (
        "Your Supply Chain AI received your question:\n\n"
        + question
    )


    # Save answer
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

    st.html("""
    <div class="chat-area">
    """)

    for message in st.session_state.messages:

        if message["role"] == "user":

            st.markdown(
                f"""
                <div class="chat-message">

                    <b>👤 You</b>

                    <div style="margin-top:7px;">
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

                    <b>🤖 Dilytics AI</b>

                    <div style="margin-top:7px;">
                        {message["content"]}
                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )

    st.html("""
    </div>
    """)
