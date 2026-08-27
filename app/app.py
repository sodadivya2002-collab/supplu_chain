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
   GLOBAL
   ============================================================ */

html,
body {
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

    background: #ffffff !important;

    border-right: 1px solid #d8e1ec;

    width: 350px !important;

    min-width: 350px !important;

    position: fixed !important;

    left: 0;

    top: 0;

    bottom: 0;

    z-index: 1000;
}


/* Sidebar content */

section[data-testid="stSidebar"] > div {

    padding: 14px 18px 20px 18px !important;

}


/* ============================================================
   DILYTICS LOGO IN SIDEBAR
   ============================================================ */

.sidebar-logo {

    width: 190px;

    height: 58px;

    background: #df0000;

    color: #ffffff;

    display: flex;

    align-items: center;

    justify-content: center;

    font-family: Arial, sans-serif;

    font-size: 27px;

    font-weight: 800;

    letter-spacing: 1px;

    margin-bottom: 22px;

}


/* ============================================================
   SEMANTIC STATUS
   ============================================================ */

.semantic-status {

    display: inline-flex;

    align-items: center;

    gap: 7px;

    background: #effcf6;

    border: 1px solid #a9e8ce;

    color: #087651;

    border-radius: 22px;

    padding: 7px 14px;

    font-size: 13px;

    font-weight: 600;

    margin-bottom: 20px;
}


.status-dot {

    width: 8px;

    height: 8px;

    border-radius: 50%;

    background: #16a673;
}


/* ============================================================
   SIDEBAR BUTTON
   ============================================================ */

section[data-testid="stSidebar"] .stButton > button {

    width: 100%;

    height: 45px;

    background: #ffffff;

    border: 1px solid #cdd7e4;

    border-radius: 9px;

    color: #102b55;

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

    margin: 22px 0;

}


/* ============================================================
   SIDEBAR HEADING
   ============================================================ */

.sidebar-heading {

    color: #102b55;

    font-size: 14px;

    font-weight: 700;

    margin-bottom: 13px;

}


/* ============================================================
   RECENT CHAT
   ============================================================ */

.recent-chat {

    color: #71809a;

    font-size: 13px;

    padding: 8px 2px;

}


/* ============================================================
   QUICK LINKS
   ============================================================ */

.quick-link {

    display: flex;

    align-items: center;

    justify-content: space-between;

    width: 100%;

    padding: 10px 2px;

    color: #17335f;

    font-size: 13px;

}


.quick-link-left {

    display: flex;

    align-items: center;

    gap: 10px;

}


/* ============================================================
   MAIN CONTENT
   ============================================================ */

.main-content {

    margin-left: 350px;

    width: calc(100% - 350px);

    min-height: 100vh;

    background: #eef5ff;

}


/* ============================================================
   FIXED BLUE HEADER
   ============================================================ */

.top-header {

    position: fixed;

    top: 0;

    left: 350px;

    right: 0;

    height: 70px;

    background: #0754d8;

    z-index: 900;

    display: flex;

    align-items: center;

    padding: 0 28px;

    box-sizing: border-box;

}


/* ============================================================
   HEADER TITLE
   ============================================================ */

.header-title {

    color: white;

    font-family: Arial, sans-serif;

    font-size: 30px;

    font-weight: 700;

    white-space: nowrap;

}


/* ============================================================
   HEADER DIVIDER
   ============================================================ */

.header-divider {

    width: 2px;

    height: 42px;

    background: rgba(255,255,255,0.75);

    margin-right: 25px;

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

    font-size: 21px;

}


/* ============================================================
   HERO
   ============================================================ */

.hero-section {

    width: 100%;

    padding-top: 95px;

    padding-bottom: 22px;

    background:
        radial-gradient(
            circle at 50% 20%,
            #ffffff 0%,
            #f5f9ff 45%,
            #e8f2ff 100%
        );

    text-align: center;

    box-sizing: border-box;

}


/* ============================================================
   ROBOT
   ============================================================ */

.bot-circle {

    width: 60px;

    height: 60px;

    margin: 0 auto 12px auto;

    border-radius: 50%;

    background: #ffffff;

    display: flex;

    align-items: center;

    justify-content: center;

    font-size: 30px;

    box-shadow:
        0 5px 18px rgba(30,70,140,0.10);

}


/* ============================================================
   HERO TITLE
   ============================================================ */

.hero-title {

    margin: 0;

    color: #102b55;

    font-family: Arial, sans-serif;

    font-size: 38px;

    font-weight: 750;

    line-height: 1.15;

}


/* ============================================================
   TITLE LINE
   ============================================================ */

.title-line {

    width: 120px;

    height: 4px;

    background: #0754d8;

    margin: 12px auto 12px auto;

}


/* ============================================================
   SUBTITLE
   ============================================================ */

.hero-subtitle {

    margin: 0;

    color: #29466f;

    font-family: Arial, sans-serif;

    font-size: 16px;

}


/* ============================================================
   CARDS AREA
   ============================================================ */

.cards-area {

    width: 100%;

    padding: 20px 12px 20px 12px;

    background: #eef5ff;

    box-sizing: border-box;

}


/* ============================================================
   CARD
   ============================================================ */

.question-card {

    height: 125px;

    width: 100%;

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

    font-size: 34px;

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
   CHAT AREA
   ============================================================ */

.chat-area {

    width: 100%;

    background: #eef5ff;

    padding-bottom: 40px;

}


/* ============================================================
   STREAMLIT CHAT INPUT
   ============================================================ */

div[data-testid="stChatInput"] {

    width: calc(100% - 120px) !important;

    max-width: 1250px !important;

    margin: 5px auto 25px auto !important;

}


/* Chat input appearance */

div[data-testid="stChatInput"] > div {

    border-radius: 35px !important;

    background: #ffffff !important;

    border: 1px solid #cbd9ea !important;

    box-shadow:
        0 4px 15px rgba(30,70,140,0.09) !important;

}


/* ============================================================
   CHAT MESSAGES
   ============================================================ */

.chat-message {

    width: calc(100% - 120px);

    max-width: 1250px;

    margin: 12px auto;

    padding: 15px 20px;

    background: #ffffff;

    border: 1px solid #d8e2ef;

    border-radius: 13px;

    color: #172f56;

    font-size: 15px;

    line-height: 1.5;

}


/* ============================================================
   RESPONSIVE
   ============================================================ */

@media (max-width: 1100px) {

    section[data-testid="stSidebar"] {

        width: 290px !important;

        min-width: 290px !important;

    }

    .main-content {

        margin-left: 290px;

        width: calc(100% - 290px);

    }

    .top-header {

        left: 290px;

    }

    .header-title {

        font-size: 25px;

    }

    .hero-title {

        font-size: 33px;

    }

}


@media (max-width: 750px) {

    section[data-testid="stSidebar"] {

        width: 250px !important;

        min-width: 250px !important;

    }

    .main-content {

        margin-left: 250px;

        width: calc(100% - 250px);

    }

    .top-header {

        left: 250px;

    }

    .header-title {

        font-size: 20px;

    }

    .hero-title {

        font-size: 28px;

    }

}

</style>
""")


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    # --------------------------------------------------------
    # DILYTICS LOGO
    # --------------------------------------------------------

    st.html("""
    <div class="sidebar-logo">
        DILYTICS
    </div>
    """)


    # --------------------------------------------------------
    # SEMANTIC MART
    # --------------------------------------------------------

    st.html("""
    <div class="semantic-status">

        <span class="status-dot"></span>

        Semantic Mart Live

    </div>
    """)


    # --------------------------------------------------------
    # NEW CHAT
    # --------------------------------------------------------

    if st.button(
        "＋  New Chat",
        use_container_width=True
    ):

        st.session_state.messages = []

        st.rerun()


    # --------------------------------------------------------
    # RECENT CONVERSATIONS
    # --------------------------------------------------------

    st.html("""
    <div class="sidebar-divider"></div>

    <div class="sidebar-heading">
        ◷ &nbsp; Recent Conversations
    </div>
    """)


    if st.session_state.recent_chats:

        for chat in reversed(
            st.session_state.recent_chats[-5:]
        ):

            text = chat

            if len(text) > 32:
                text = text[:32] + "..."

            st.html(f"""
            <div class="recent-chat">
                💬 &nbsp; {text}
            </div>
            """)

    else:

        st.html("""
        <div class="recent-chat">
            No recent conversations
        </div>
        """)


    # --------------------------------------------------------
    # QUICK LINKS
    # --------------------------------------------------------

    st.html("""
    <div class="sidebar-divider"></div>

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

            <div class="quick-link-left">

                <span>{icon}</span>

                <span>{name}</span>

            </div>

            <span>›</span>

        </div>
        """)


    # --------------------------------------------------------
    # CLEAR
    # --------------------------------------------------------

    st.html("""
    <div class="sidebar-divider"></div>
    """)


    if st.button(
        "🗑️  Clear All Sessions",
        use_container_width=True
    ):

        st.session_state.messages = []

        st.session_state.recent_chats = []

        st.rerun()


# ============================================================
# MAIN CONTENT START
# ============================================================

st.html("""
<div class="main-content">


    <!-- ====================================================
         BLUE HEADER
         ==================================================== -->

    <div class="top-header">

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
# SIX CARDS
# ============================================================

st.html("""
<div class="cards-area">
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
# CHAT INPUT
# ============================================================

st.html("""
<div class="chat-area">
</div>
""")


question = st.chat_input(
    "Ask your supply chain question..."
)


# ============================================================
# YOUR EXISTING AGENT CODE
# ============================================================

if question:

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
    #
    # PUT YOUR CURRENT WORKING AGENT CALL HERE.
    #
    # Example:
    #
    # response = ask_agent(question)
    #
    # ========================================================

    response = (
        "Your Supply Chain AI received your question:\n\n"
        + question
    )


    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response
        }
    )


# ============================================================
# CHAT HISTORY
# ============================================================

if st.session_state.messages:

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
