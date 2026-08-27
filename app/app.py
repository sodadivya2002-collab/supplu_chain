import streamlit as st

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Dilytics AI",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# MODULE CONFIGURATION
# ============================================================

MODULES = {
    "Supply Chain": {
        "title": "Dilytics Supply Chain Chatbot",
        "subtitle": "Ask anything about your supply chain data in natural language."
    },

    "Inventory": {
        "title": "Dilytics Inventory Chatbot",
        "subtitle": "Ask anything about your inventory data in natural language."
    },

    "Purchase Orders": {
        "title": "Dilytics Purchase Orders Chatbot",
        "subtitle": "Ask anything about your purchase orders in natural language."
    },

    "Shipments & Deliveries": {
        "title": "Dilytics Shipments & Deliveries Chatbot",
        "subtitle": "Ask anything about your shipments and deliveries in natural language."
    },

    "Suppliers": {
        "title": "Dilytics Suppliers Chatbot",
        "subtitle": "Ask anything about your suppliers in natural language."
    },

    "Warehouses": {
        "title": "Dilytics Warehouses Chatbot",
        "subtitle": "Ask anything about your warehouses in natural language."
    },

    "Products": {
        "title": "Dilytics Products Chatbot",
        "subtitle": "Ask anything about your products in natural language."
    },

    "Analytics & Reports": {
        "title": "Dilytics Analytics & Reports Chatbot",
        "subtitle": "Ask anything about your supply chain analytics and reports."
    }
}


# ============================================================
# SESSION STATE
# ============================================================

if "selected_module" not in st.session_state:
    st.session_state.selected_module = "Supply Chain"


# ============================================================
# GLOBAL CSS
# ============================================================

st.markdown("""
<style>

    /* ========================================================
       REMOVE DEFAULT STREAMLIT SPACE
       ======================================================== */

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    header {
        visibility: hidden;
    }

    .stApp {
        background: #eef5ff;
    }

    .block-container {
        padding-top: 0 !important;
        padding-bottom: 0 !important;
        padding-left: 0 !important;
        padding-right: 0 !important;
        max-width: none !important;
    }


    /* ========================================================
       SIDEBAR
       ======================================================== */

    section[data-testid="stSidebar"] {
        width: 350px !important;
        min-width: 350px !important;
        background: #ffffff !important;
        border-right: 1px solid #d8e0ec;
    }

    section[data-testid="stSidebar"] > div {
        padding-top: 20px !important;
        padding-left: 28px !important;
        padding-right: 28px !important;
    }


    /* DILYTICS LOGO */

    .dilytics-logo {
        width: 200px;
        height: 68px;

        background: #ed0000;

        display: flex;
        align-items: center;
        justify-content: center;

        color: white;

        font-size: 28px;
        font-weight: 800;

        letter-spacing: 1px;

        margin-bottom: 28px;
    }


    /* SEMANTIC MART */

    .semantic-live {
        display: inline-flex;

        align-items: center;

        padding: 10px 16px;

        border-radius: 24px;

        border: 1px solid #9be5cf;

        background: #f2fffa;

        color: #08795c;

        font-size: 14px;

        font-weight: 600;

        margin-bottom: 22px;
    }

    .semantic-dot {
        width: 9px;
        height: 9px;

        background: #16aa7a;

        border-radius: 50%;

        margin-right: 9px;
    }


    /* ========================================================
       MODULE DROPDOWN
       ======================================================== */

    .module-label {
        color: #12284f;

        font-size: 13px;

        font-weight: 600;

        margin-bottom: 6px;
    }

    div[data-testid="stSidebar"] div[data-testid="stSelectbox"] {
        margin-bottom: 25px !important;
    }

    div[data-testid="stSidebar"]
    div[data-baseweb="select"] {

        min-height: 46px !important;

        background: #f1f3f7 !important;

        border: none !important;

        border-radius: 9px !important;
    }

    div[data-testid="stSidebar"]
    div[data-baseweb="select"] > div {

        color: #172b4d !important;

        font-size: 14px !important;

        font-weight: 500 !important;
    }


    /* ========================================================
       NEW CHAT
       ======================================================== */

    .new-chat-button {

        width: 100%;

        height: 48px;

        background: white;

        border: 1px solid #cfd8e6;

        border-radius: 9px;

        color: #12284f;

        font-size: 15px;

        display: flex;

        align-items: center;

        justify-content: center;

        margin-bottom: 30px;
    }


    /* SIDEBAR SEPARATOR */

    .sidebar-line {

        width: 100%;

        height: 1px;

        background: #dce3ed;

        margin: 10px 0 28px 0;
    }


    /* SIDEBAR HEADINGS */

    .sidebar-heading {

        color: #12284f;

        font-size: 15px;

        font-weight: 700;

        margin-bottom: 28px;
    }


    .sidebar-empty {

        color: #7f8998;

        font-size: 14px;

        margin-bottom: 35px;
    }


    .quick-link {

        height: 54px;

        display: flex;

        align-items: center;

        justify-content: space-between;

        color: #12284f;

        font-size: 14px;
    }

    .quick-link-left {

        display: flex;

        align-items: center;

        gap: 12px;
    }

    .quick-icon {

        font-size: 19px;
    }

    .quick-arrow {

        color: #24528b;

        font-size: 16px;
    }


    /* ========================================================
       TOP BLUE HEADER
       ======================================================== */

    .top-header {

        position: fixed;

        top: 0;
        left: 350px;
        right: 0;

        height: 86px;

        background: #0754d8;

        z-index: 999;

        display: flex;

        align-items: center;

        justify-content: flex-end;

        padding: 0 34px;

        box-sizing: border-box;
    }


    .header-icons {

        display: flex;

        align-items: center;

        gap: 28px;

        color: white;

        font-size: 22px;
    }

    .header-question {
        font-size: 20px;
    }

    .header-user {
        font-size: 18px;
    }


    /* ========================================================
       MAIN AREA
       ======================================================== */

    .main-area {

        margin-left: 350px;

        padding-top: 86px;

        min-height: 100vh;

        background: #eef5ff;
    }


    /* ========================================================
       HERO
       ======================================================== */

    .hero {

        height: 555px;

        background:
            radial-gradient(
                circle at 50% 25%,
                #ffffff 0%,
                #f1f7ff 45%,
                #e6f0ff 100%
            );

        display: flex;

        flex-direction: column;

        align-items: center;

        justify-content: flex-start;

        padding-top: 64px;

        box-sizing: border-box;

        text-align: center;
    }


    /* BOT */

    .bot-circle {

        width: 76px;

        height: 76px;

        border-radius: 50%;

        background: white;

        display: flex;

        align-items: center;

        justify-content: center;

        font-size: 30px;

        box-shadow:
            0 8px 22px rgba(30,70,130,0.10);

        margin-bottom: 22px;

        flex-shrink: 0;
    }


    /* DYNAMIC TITLE */

    .hero-title {

        width: 100%;

        height: 58px;

        display: flex;

        align-items: center;

        justify-content: center;

        color: #102a54;

        font-size: 40px;

        font-weight: 750;

        line-height: 1.1;

        margin: 0;

        padding: 0;

        white-space: nowrap;

        flex-shrink: 0;
    }


    /* TITLE LINE */

    .hero-line {

        width: 120px;

        height: 4px;

        background: #0754d8;

        margin-top: 15px;

        margin-bottom: 17px;

        flex-shrink: 0;
    }


    /* SUBTITLE */

    .hero-subtitle {

        width: 100%;

        height: 26px;

        display: flex;

        align-items: center;

        justify-content: center;

        color: #24466f;

        font-size: 17px;

        line-height: 1.3;

        margin: 0;

        flex-shrink: 0;
    }


    /* ========================================================
       BOTTOM SEARCH AREA
       ======================================================== */

    .search-area {

        height: 125px;

        background: white;

        display: flex;

        align-items: center;

        justify-content: center;
    }


    .search-box {

        width: 78%;

        height: 62px;

        background: #ffffff;

        border: 1px solid #d3dfef;

        border-radius: 34px;

        box-shadow:
            0 5px 20px rgba(30,70,140,0.10);

        display: flex;

        align-items: center;

        padding: 0 12px 0 24px;

        box-sizing: border-box;
    }


    .search-icon {

        font-size: 26px;

        margin-right: 14px;
    }


    .search-placeholder {

        flex: 1;

        color: #8491a4;

        font-size: 16px;
    }


    .search-button {

        width: 44px;

        height: 44px;

        border-radius: 50%;

        background: #0754d8;

        color: white;

        display: flex;

        align-items: center;

        justify-content: center;

        font-size: 20px;
    }


    /* ========================================================
       RESPONSIVE
       ======================================================== */

    @media (max-width: 1100px) {

        section[data-testid="stSidebar"] {
            width: 290px !important;
            min-width: 290px !important;
        }

        .top-header {
            left: 290px;
        }

        .main-area {
            margin-left: 290px;
        }

        .hero-title {
            font-size: 34px;
        }

    }

</style>
""", unsafe_allow_html=True)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    # --------------------------------------------------------
    # DILYTICS LOGO
    # --------------------------------------------------------

    st.markdown("""
    <div class="dilytics-logo">
        DILYTICS
    </div>
    """, unsafe_allow_html=True)


    # --------------------------------------------------------
    # SEMANTIC MART LIVE
    # --------------------------------------------------------

    st.markdown("""
    <div class="semantic-live">
        <span class="semantic-dot"></span>
        Semantic Mart Live
    </div>
    """, unsafe_allow_html=True)


    # --------------------------------------------------------
    # MODULE DROPDOWN
    # --------------------------------------------------------

    st.markdown("""
    <div class="module-label">
        Module
    </div>
    """, unsafe_allow_html=True)


    selected_module = st.selectbox(
        "Module",
        list(MODULES.keys()),
        index=list(MODULES.keys()).index(
            st.session_state.selected_module
        ),
        label_visibility="collapsed"
    )


    st.session_state.selected_module = selected_module


    # --------------------------------------------------------
    # NEW CHAT
    # --------------------------------------------------------

    st.markdown("""
    <div class="new-chat-button">
        ＋&nbsp;&nbsp; New Chat
    </div>
    """, unsafe_allow_html=True)


    # --------------------------------------------------------
    # RECENT CONVERSATIONS
    # --------------------------------------------------------

    st.markdown(
        '<div class="sidebar-line"></div>',
        unsafe_allow_html=True
    )

    st.markdown("""
    <div class="sidebar-heading">
        ◷ &nbsp; Recent Conversations
    </div>

    <div class="sidebar-empty">
        No recent conversations
    </div>
    """, unsafe_allow_html=True)


    # --------------------------------------------------------
    # QUICK LINKS
    # --------------------------------------------------------

    st.markdown(
        '<div class="sidebar-line"></div>',
        unsafe_allow_html=True
    )

    st.markdown("""
    <div class="sidebar-heading">
        🔗 &nbsp; Quick Links
    </div>
    """, unsafe_allow_html=True)


    quick_links = [
        ("📋", "Purchase Orders"),
        ("🚚", "Shipments & Deliveries"),
        ("📦", "Inventory"),
        ("👥", "Suppliers"),
        ("🏭", "Warehouses"),
        ("📦", "Products"),
        ("📈", "Analytics & Reports")
    ]


    for icon, name in quick_links:

        st.markdown(f"""
        <div class="quick-link">

            <div class="quick-link-left">

                <span class="quick-icon">
                    {icon}
                </span>

                <span>
                    {name}
                </span>

            </div>

            <span class="quick-arrow">
                ›
            </span>

        </div>
        """, unsafe_allow_html=True)


# ============================================================
# GET CURRENT MODULE INFORMATION
# ============================================================

current_module = MODULES[selected_module]

current_title = current_module["title"]

current_subtitle = current_module["subtitle"]


# ============================================================
# TOP HEADER
# ============================================================

st.markdown("""
<div class="top-header">

    <div class="header-icons">

        <span>🔔</span>

        <span class="header-question">?</span>

        <span class="header-user">●</span>

    </div>

</div>
""", unsafe_allow_html=True)


# ============================================================
# MAIN AREA
# ============================================================

st.markdown(f"""

<div class="main-area">

    <!-- HERO -->

    <div class="hero">

        <div class="bot-circle">
            🤖
        </div>


        <div class="hero-title">
            {current_title}
        </div>


        <div class="hero-line"></div>


        <div class="hero-subtitle">
            {current_subtitle}
        </div>

    </div>


    <!-- SEARCH -->

    <div class="search-area">

        <div class="search-box">

            <div class="search-icon">
                🔍
            </div>

            <div class="search-placeholder">
                Ask your {selected_module.lower()} question...
            </div>

            <div class="search-button">
                ➤
            </div>

        </div>

    </div>

</div>

""", unsafe_allow_html=True)
