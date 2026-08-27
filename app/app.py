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
# CSS
# ============================================================

st.html("""
<style>

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
    max-width: 100% !important;
}


/* =========================================================
   TOP HEADER
   ========================================================= */

.top-header {
    width: 100%;
    height: 90px;

    background: #0754d8;

    display: flex;
    align-items: center;

    padding: 0 30px;

    box-sizing: border-box;
}


/* LOGO */

.dilytics-logo {
    background: #d90000;

    color: white;

    font-size: 27px;
    font-weight: 800;

    letter-spacing: 1px;

    padding: 9px 20px;

    min-width: 175px;

    text-align: center;
}


/* DIVIDER */

.header-divider {
    width: 2px;
    height: 48px;

    background: rgba(255,255,255,0.65);

    margin-left: 30px;
    margin-right: 30px;
}


/* TITLE */

.header-title {
    color: white;

    font-size: 31px;

    font-weight: 700;

    white-space: nowrap;
}


/* RIGHT SIDE */

.header-right {
    margin-left: auto;

    display: flex;

    align-items: center;

    gap: 25px;

    color: white;

    font-size: 24px;
}


/* =========================================================
   SIDEBAR
   ========================================================= */

section[data-testid="stSidebar"] {

    background: #ffffff;

    border-right: 1px solid #d9e2ef;
}


section[data-testid="stSidebar"] > div {

    padding-top: 20px;
}


/* STATUS */

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
}


.status-dot {

    width: 8px;

    height: 8px;

    background: #18a974;

    border-radius: 50%;
}


/* NEW CHAT */

div[data-testid="stSidebar"] button {

    border-radius: 8px;
}


/* SIDEBAR HEADINGS */

.sidebar-heading {

    color: #13284d;

    font-size: 15px;

    font-weight: 700;

    margin-top: 20px;

    margin-bottom: 12px;
}


/* DIVIDER */

.sidebar-line {

    height: 1px;

    background: #dce4ee;

    margin: 20px 0;
}


/* QUICK LINKS */

.quick-link {

    display: flex;

    align-items: center;

    justify-content: space-between;

    padding: 9px 3px;

    color: #1a2b4d;

    font-size: 14px;
}


.quick-left {

    display: flex;

    align-items: center;

    gap: 10px;
}


/* =========================================================
   MAIN CONTENT
   ========================================================= */

.main-wrapper {

    background:
        radial-gradient(
            circle at 50% 30%,
            #ffffff 0%,
            #eef5ff 55%,
            #e4efff 100%
        );

    min-height: calc(100vh - 90px);

    padding: 50px 45px 40px 45px;

    box-sizing: border-box;
}


/* =========================================================
   HERO
   ========================================================= */

.hero {

    text-align: center;

    max-width: 1100px;

    margin: 0 auto;
}


/* BOT */

.bot-circle {

    width: 82px;

    height: 82px;

    margin: 0 auto 22px auto;

    background: white;

    border-radius: 50%;

    display: flex;

    align-items: center;

    justify-content: center;

    font-size: 42px;

    box-shadow:
        0 8px 25px rgba(20,70,150,0.12);
}


/* TITLE */

.hero-title {

    margin: 0;

    color: #12284f;

    font-size: 50px;

    font-weight: 750;

    line-height: 1.15;
}


/* BLUE LINE */

.title-line {

    width: 150px;

    height: 4px;

    background: #0754d8;

    margin: 22px auto;
}


/* SUBTITLE */

.hero-subtitle {

    color: #31486c;

    font-size: 19px;

    margin-bottom: 35px;
}


/* =========================================================
   QUESTION CARDS
   ========================================================= */

.question-card {

    background: white;

    border: 1px solid #dce5f2;

    border-radius: 16px;

    min-height: 145px;

    display: flex;

    flex-direction: column;

    align-items: center;

    justify-content: center;

    text-align: center;

    padding: 15px;

    box-sizing: border-box;

    box-shadow:
        0 5px 18px rgba(30,70,140,0.07);

    transition: 0.2s;
}


.question-card:hover {

    transform: translateY(-3px);

    box-shadow:
        0 10px 25px rgba(30,70,140,0.12);
}


.question-icon {

    font-size: 36px;

    margin-bottom: 12px;
}


.question-title {

    color: #12284f;

    font-size: 16px;

    font-weight: 650;
}


/* =========================================================
   SEARCH BAR
   ========================================================= */

.search-container {

    max-width: 1050px;

    margin: 65px auto 0 auto;

    position: relative;
}


/* GOOGLE STYLE SEARCH */

.search-box {

    width: 100%;

    height: 62px;

    background: white;

    border: 1px solid #d4dce8;

    border-radius: 35px;

    display: flex;

    align-items: center;

    padding: 0 12px 0 22px;

    box-sizing: border-box;

    box-shadow:
        0 4px 15px rgba(20,70,140,0.10);
}


.search-icon {

    font-size: 23px;

    color: #68778e;

    margin-right: 13px;
}


.search-placeholder {

    flex: 1;

    color: #8490a2;

    font-size: 16px;
}


.search-button {

    width: 45px;

    height: 45px;

    border-radius: 50%;

    background: #0754d8;

    color: white;

    display: flex;

    align-items: center;

    justify-content: center;

    font-size: 21px;
}


/* =========================================================
   RESPONSIVE
   ========================================================= */

@media (max-width: 1100px) {

    .hero-title {
        font-size: 42px;
    }

    .header-title {
        font-size: 25px;
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


    st.write("")


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


    st.caption(
        "No recent conversations"
    )


    st.html("""
    <div class="sidebar-line"></div>

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

        st.rerun()


# ============================================================
# MAIN AREA
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
            Ask anything about your supply chain
            data in natural language.
        </div>

    </div>

</div>
""")


# ============================================================
# QUESTION CARDS
# ============================================================

col1, col2, col3, col4, col5, col6 = st.columns(
    6,
    gap="medium"
)


cards = [

    ("📋", "Purchase Orders"),

    ("🚚", "Shipments & Deliveries"),

    ("📊", "Inventory & Warehouses"),

    ("👥", "Suppliers"),

    ("📦", "Products"),

    ("📈", "Analytics & Reports")

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
# SEARCH BAR
# ============================================================

st.html("""
<div class="search-container">

    <div class="search-box">

        <div class="search-icon">
            🔍
        </div>

        <div class="search-placeholder">
            Ask a question about suppliers, purchase orders,
            shipments, deliveries, warehouses, carriers,
            products, or inventory...
        </div>

        <div class="search-button">
            ➤
        </div>

    </div>

</div>
""")


# ============================================================
# ACTUAL STREAMLIT SEARCH INPUT
# ============================================================

st.write("")

question = st.chat_input(
    "Ask your supply chain question..."
)


if question:

    if "messages" not in st.session_state:

        st.session_state.messages = []


    st.session_state.messages.append(
        {
            "role": "user",
            "content": question
        }
    )


    with st.chat_message("user"):

        st.write(question)


    # --------------------------------------------------------
    # CONNECT YOUR EXISTING AGENT / SNOWFLAKE CODE HERE
    # --------------------------------------------------------

    response = (
        "Your Supply Chain AI is ready to process: "
        + question
    )


    with st.chat_message("assistant"):

        st.write(response)


    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response
        }
    )
