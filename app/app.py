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
# COMPLETE CSS
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
    padding-top: 0 !important;
    padding-left: 0 !important;
    padding-right: 0 !important;
    padding-bottom: 0 !important;
    margin-top: 0 !important;
    max-width: 100% !important;
}


/* Hide Streamlit default elements */

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
   TOP HEADER
   ========================================================= */

.top-header {
    width: 100%;
    height: 70px;

    background: #0754d8;

    display: flex;
    align-items: center;

    padding: 0 28px;

    box-sizing: border-box;
}


/* =========================================================
   DILYTICS LOGO
   ========================================================= */

.dilytics-logo {
    background: #d90000;

    color: white;

    font-size: 24px;

    font-weight: 800;

    letter-spacing: 1px;

    padding: 8px 18px;

    min-width: 160px;

    text-align: center;

    box-sizing: border-box;
}


/* =========================================================
   HEADER DIVIDER
   ========================================================= */

.header-divider {
    width: 2px;

    height: 40px;

    background: rgba(255,255,255,0.65);

    margin-left: 25px;

    margin-right: 25px;
}


/* =========================================================
   HEADER TITLE
   ========================================================= */

.header-title {
    color: white;

    font-size: 27px;

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

    gap: 22px;

    color: white;

    font-size: 21px;
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

    padding: 7px 13px;

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
   SIDEBAR BUTTONS
   ========================================================= */

section[data-testid="stSidebar"] .stButton > button {

    height: 42px;

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


/* =========================================================
   SIDEBAR DIVIDER
   ========================================================= */

.sidebar-line {

    height: 1px;

    background: #dce4ee;

    margin: 17px 0;
}


/* =========================================================
   RECENT CHAT
   ========================================================= */

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
   MAIN AREA
   ========================================================= */

.main-wrapper {

    width: 100%;

    background:
        radial-gradient(
            circle at 50% 25%,
            #ffffff 0%,
            #eef5ff 55%,
            #e4efff 100%
        );

    min-height: calc(100vh - 70px);

    padding: 28px 35px 25px 35px;

    box-sizing: border-box;
}


/* =========================================================
   HERO
   ========================================================= */

.hero {

    text-align: center;

    max-width: 1050px;

    margin: 0 auto;
}


/* =========================================================
   BOT ICON
   ========================================================= */

.bot-circle {

    width: 60px;

    height: 60px;

    margin: 0 auto 14px auto;

    background: white;

    border-radius: 50%;

    display: flex;

    align-items: center;

    justify-content: center;

    font-size: 30px;

    box-shadow:
        0 6px 18px rgba(20,70,150,0.10);
}


/* =========================================================
   HERO TITLE
   ========================================================= */

.hero-title {

    margin: 0;

    padding: 0;

    color: #12284f;

    font-size: 38px;

    font-weight: 750;

    line-height: 1.15;

    white-space: nowrap;
}


/* =========================================================
   TITLE LINE
   ========================================================= */

.title-line {

    width: 120px;

    height: 3px;

    background: #0754d8;

    margin: 15px auto 15px auto;
}


/* =========================================================
   HERO SUBTITLE
   ========================================================= */

.hero-subtitle {

    color: #31486c;

    font-size: 16px;

    margin: 0 auto;

    line-height: 1.4;
}


/* =========================================================
   QUESTION CARDS AREA
   ========================================================= */

.cards-area {

    max-width: 1050px;

    margin: 25px auto 0 auto;
}


/* =========================================================
   QUESTION CARD
   ========================================================= */

.question-card {

    background: white;

    border: 1px solid #dce5f2;

    border-radius: 13px;

    height: 108px;

    display: flex;

    flex-direction: column;

    align-items: center;

    justify-content: center;

    text-align: center;

    padding: 8px;

    box-sizing: border-box;

    box-shadow:
        0 4px 14px rgba(30,70,140,0.06);
}


.question-icon {

    font-size: 28px;

    line-height: 1;

    margin-bottom: 8px;
}


.question-title {

    color: #12284f;

    font-size: 13px;

    font-weight: 650;

    line-height: 1.25;
}


/* =========================================================
   SEARCH CONTAINER
   ========================================================= */

.search-container {

    max-width: 1050px;

    margin: 32px auto 0 auto;
}


/* =========================================================
   SEARCH BAR
   ========================================================= */

.search-box {

    width: 100%;

    height: 54px;

    background: white;

    border: 1px solid #d4dce8;

    border-radius: 30px;

    display: flex;

    align-items: center;

    padding: 0 9px 0 20px;

    box-sizing: border-box;

    box-shadow:
        0 4px 15px rgba(20,70,140,0.09);
}


.search-icon {

    font-size: 21px;

    color: #68778e;

    margin-right: 11px;
}


.search-placeholder {

    flex: 1;

    color: #8490a2;

    font-size: 14px;

    overflow: hidden;

    white-space: nowrap;

    text-overflow: ellipsis;
}


.search-button {

    width: 38px;

    height: 38px;

    border-radius: 50%;

    background: #0754d8;

    color: white;

    display: flex;

    align-items: center;

    justify-content: center;

    font-size: 17px;
}


/* =========================================================
   STREAMLIT CHAT INPUT
   ========================================================= */

div[data-testid="stChatInput"] {

    max-width: 1050px;

    margin-left: auto;

    margin-right: auto;
}


div[data-testid="stChatInput"] textarea {

    border-radius: 30px !important;
}


/* =========================================================
   CHAT MESSAGE
   ========================================================= */

.chat-message {

    max-width: 1050px;

    margin: 18px auto;

    padding: 16px 20px;

    background: white;

    border: 1px solid #e0e7f1;

    border-radius: 13px;

    box-shadow:
        0 4px 15px rgba(30,70,140,0.06);
}


/* =========================================================
   RESPONSIVE
   ========================================================= */

@media (max-width: 1100px) {

    .hero-title {
        font-size: 32px;
    }

    .header-title {
        font-size: 23px;
    }

}


@media (max-width: 800px) {

    .hero-title {
        font-size: 28px;
        white-space: normal;
    }

    .header-title {
        display: none;
    }

    .header-divider {
        display: none;
    }

    .main-wrapper {
        padding-left: 18px;
        padding-right: 18px;
    }

}

</style>
""")


# ============================================================
# TOP HEADER
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

            short_chat = chat

            if len(short_chat) > 35:
                short_chat = short_chat[:35] + "..."

            st.html(f"""
            <div class="recent-chat">
                💬 &nbsp; {short_chat}
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
# MAIN HERO
# ============================================================

st.html("""
<div class="main-wrapper">

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
    [
        col1,
        col2,
        col3,
        col4,
        col5,
        col6
    ],
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
# SEARCH BAR VISUAL
# ============================================================

st.html("""
<div class="search-container">

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
# ACTUAL CHAT INPUT
# ============================================================

question = st.chat_input(
    "Ask your supply chain question..."
)


# ============================================================
# YOUR EXISTING AGENT LOGIC
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
    # PUT YOUR EXISTING WORKING AGENT CODE HERE
    # ========================================================

    # Example response only.
    #
    # Replace this with your Snowflake Agent call.
    #
    # response = your_agent_function(question)

    response = (
        "Your Supply Chain AI received your question:\n\n"
        + question
    )


    # ========================================================
    # SAVE RESPONSE
    # ========================================================

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
