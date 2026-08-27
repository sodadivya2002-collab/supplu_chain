import streamlit as st
from datetime import datetime


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
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    /* ========================================================
       GLOBAL
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

    html, body, [class*="css"] {
        font-family: Arial, Helvetica, sans-serif;
    }

    .stApp {
        background: #f4f8ff;
    }

    .block-container {
        padding: 0 !important;
        max-width: 100% !important;
    }


    /* ========================================================
       TOP HEADER
       ======================================================== */

    .top-header {
        height: 92px;

        width: 100%;

        background: linear-gradient(
            90deg,
            #0645c5 0%,
            #0752d6 50%,
            #0645c5 100%
        );

        display: flex;

        align-items: center;

        padding: 0 28px;

        box-sizing: border-box;
    }


    /* ========================================================
       DILYTICS LOGO
       ======================================================== */

    .dilytics-logo {
        background: #d90000;

        color: white;

        font-size: 28px;

        font-weight: 800;

        letter-spacing: 1px;

        padding: 9px 18px;

        min-width: 170px;

        text-align: center;

        border-radius: 0;

        box-sizing: border-box;
    }


    /* ========================================================
       HEADER DIVIDER
       ======================================================== */

    .header-divider {
        width: 2px;

        height: 50px;

        background: rgba(255,255,255,0.7);

        margin-left: 30px;

        margin-right: 30px;
    }


    /* ========================================================
       HEADER TITLE
       ======================================================== */

    .header-title {
        color: white;

        font-size: 32px;

        font-weight: 700;

        white-space: nowrap;
    }


    .header-sparkle {
        color: white;

        font-size: 28px;

        margin-left: 12px;
    }


    /* ========================================================
       HEADER RIGHT ICONS
       ======================================================== */

    .header-right {
        margin-left: auto;

        display: flex;

        align-items: center;

        gap: 28px;
    }

    .header-icon {
        color: white;

        font-size: 27px;

        line-height: 1;
    }


    /* ========================================================
       SIDEBAR
       ======================================================== */

    section[data-testid="stSidebar"] {

        background: #ffffff;

        border-right: 1px solid #dce5f2;

        min-width: 300px !important;

        max-width: 300px !important;
    }


    section[data-testid="stSidebar"] > div {

        padding-top: 20px;

        padding-left: 22px;

        padding-right: 22px;
    }


    /* ========================================================
       SIDEBAR STATUS
       ======================================================== */

    .semantic-status {

        display: inline-flex;

        align-items: center;

        gap: 7px;

        background: #e9fbf3;

        border: 1px solid #a8efd0;

        color: #087a55;

        border-radius: 25px;

        padding: 8px 15px;

        font-size: 14px;

        font-weight: 600;

        margin-bottom: 22px;
    }

    .status-dot {

        width: 9px;

        height: 9px;

        border-radius: 50%;

        background: #24b47e;

        display: inline-block;
    }


    /* ========================================================
       SIDEBAR NEW CHAT
       ======================================================== */

    .new-chat-btn {

        background: #0754d8;

        color: white;

        width: 100%;

        border-radius: 9px;

        padding: 13px;

        text-align: center;

        font-size: 16px;

        font-weight: 600;

        margin-bottom: 28px;
    }


    /* ========================================================
       SIDEBAR SECTION TITLE
       ======================================================== */

    .sidebar-heading {

        color: #132448;

        font-size: 15px;

        font-weight: 700;

        margin-top: 20px;

        margin-bottom: 12px;
    }


    /* ========================================================
       RECENT CHAT
       ======================================================== */

    .recent-chat {

        display: flex;

        align-items: center;

        gap: 10px;

        color: #18284c;

        font-size: 14px;

        padding: 10px;

        border-radius: 8px;

        margin-bottom: 3px;
    }


    .recent-chat.active {

        background: #e7f0ff;

        color: #073fbd;

        font-weight: 600;
    }


    /* ========================================================
       SIDEBAR DIVIDER
       ======================================================== */

    .sidebar-line {

        height: 1px;

        background: #dce3ec;

        margin: 18px 0;
    }


    /* ========================================================
       QUICK LINKS
       ======================================================== */

    .quick-link {

        display: flex;

        align-items: center;

        justify-content: space-between;

        padding: 9px 2px;

        color: #15284e;

        font-size: 14px;

        font-weight: 500;
    }


    .quick-left {

        display: flex;

        align-items: center;

        gap: 11px;
    }


    .quick-icon {

        color: #0754d8;

        font-size: 17px;
    }


    .quick-arrow {

        color: #162849;

        font-size: 20px;
    }


    /* ========================================================
       MAIN CONTENT
       ======================================================== */

    .main-area {

        min-height: calc(100vh - 92px);

        background:

            radial-gradient(
                ellipse at 50% 30%,
                #ffffff 0%,
                #edf5ff 55%,
                #e4efff 100%
            );

        padding: 55px 45px 35px 45px;

        box-sizing: border-box;

        position: relative;

        overflow: hidden;
    }


    /* ========================================================
       BACKGROUND WAVE
       ======================================================== */

    .wave-left {

        position: absolute;

        left: -100px;

        top: 180px;

        width: 500px;

        height: 250px;

        border-top: 2px solid rgba(60,125,235,0.12);

        border-radius: 50%;

        transform: rotate(20deg);
    }


    .wave-right {

        position: absolute;

        right: -150px;

        top: 130px;

        width: 550px;

        height: 350px;

        border-top: 2px solid rgba(60,125,235,0.12);

        border-radius: 50%;

        transform: rotate(-20deg);
    }


    /* ========================================================
       CENTER HERO
       ======================================================== */

    .hero {

        text-align: center;

        position: relative;

        z-index: 2;

        max-width: 1100px;

        margin: 0 auto;
    }


    .bot-circle {

        width: 95px;

        height: 95px;

        margin: 0 auto 25px auto;

        background: white;

        border-radius: 50%;

        display: flex;

        align-items: center;

        justify-content: center;

        font-size: 48px;

        box-shadow:
            0 8px 25px rgba(0,50,120,0.10);
    }


    .hero-title {

        color: #10244d;

        font-size: 52px;

        font-weight: 750;

        margin: 0;

        line-height: 1.1;
    }


    .title-line {

        width: 165px;

        height: 3px;

        background: #0754d8;

        margin: 28px auto 26px auto;

        position: relative;
    }


    .title-line:after {

        content: "";

        position: absolute;

        left: 50%;

        transform: translateX(-50%);

        width: 80px;

        height: 5px;

        background: #0754d8;
    }


    .hero-subtitle {

        color: #172c56;

        font-size: 20px;

        margin-bottom: 38px;
    }


    /* ========================================================
       QUICK QUESTION CARDS
       ======================================================== */

    .cards {

        display: grid;

        grid-template-columns:
            repeat(6, 1fr);

        gap: 14px;

        max-width: 1100px;

        margin: 0 auto;

        position: relative;

        z-index: 2;
    }


    .question-card {

        min-height: 150px;

        background: rgba(255,255,255,0.92);

        border-radius: 17px;

        box-shadow:
            0 7px 22px rgba(30,75,150,0.08);

        display: flex;

        flex-direction: column;

        align-items: center;

        justify-content: center;

        text-align: center;

        padding: 18px;

        box-sizing: border-box;

        border: 1px solid rgba(220,230,245,0.8);
    }


    .question-icon {

        font-size: 38px;

        margin-bottom: 14px;
    }


    .question-title {

        color: #10244d;

        font-size: 17px;

        font-weight: 650;

        line-height: 1.3;
    }


    /* ========================================================
       SEARCH AREA
       ======================================================== */

    .search-wrapper {

        max-width: 1100px;

        margin: 90px auto 0 auto;

        position: relative;

        z-index: 5;
    }


    /* ========================================================
       STREAMLIT INPUT
       ======================================================== */

    div[data-testid="stTextInput"] {

        width: 100%;
    }


    div[data-testid="stTextInput"] > div {

        background: white;

        border: 2px solid #0754d8;

        border-radius: 50px;

        padding: 5px 9px 5px 20px;

        box-shadow:
            0 7px 20px rgba(20,80,180,0.10);
    }


    div[data-testid="stTextInput"] input {

        border: none !important;

        outline: none !important;

        background: transparent !important;

        font-size: 16px !important;

        color: #15284e !important;
    }


    div[data-testid="stTextInput"] label {

        display: none;
    }


    /* ========================================================
       SEARCH ICON
       ======================================================== */

    .search-icon {

        font-size: 24px;

        color: #52627c;

        margin-right: 5px;
    }


    /* ========================================================
       CHAT MESSAGES
       ======================================================== */

    .chat-message {

        max-width: 1100px;

        margin: 25px auto;

        padding: 20px;

        background: white;

        border-radius: 15px;

        box-shadow:
            0 5px 20px rgba(30,70,130,0.07);

        position: relative;

        z-index: 5;
    }


    /* ========================================================
       RESPONSIVE
       ======================================================== */

    @media (max-width: 1100px) {

        .cards {

            grid-template-columns:
                repeat(3, 1fr);
        }

        .hero-title {

            font-size: 42px;
        }

        .header-title {

            font-size: 25px;
        }
    }


    @media (max-width: 700px) {

        .cards {

            grid-template-columns:
                repeat(2, 1fr);
        }

        .main-area {

            padding: 35px 20px;
        }

        .hero-title {

            font-size: 34px;
        }

        .header-title {

            display: none;
        }

        .header-divider {

            display: none;
        }
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []


if "recent_chats" not in st.session_state:
    st.session_state.recent_chats = []


# ============================================================
# TOP HEADER
# ============================================================

st.markdown(
    """
    <div class="top-header">

        <div class="dilytics-logo">
            DILYTICS
        </div>

        <div class="header-divider"></div>

        <div class="header-title">
            Dilytics Supply Chain AI
        </div>

        <div class="header-sparkle">
            ✦
        </div>

        <div class="header-right">

            <div class="header-icon">
                ♧
            </div>

            <div class="header-icon">
                ?
            </div>

            <div class="header-icon">
                ●
            </div>

        </div>

    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        """
        <div class="semantic-status">
            <span class="status-dot"></span>
            Semantic Mart Live
        </div>
        """,
        unsafe_allow_html=True
    )


    # --------------------------------------------------------
    # NEW CHAT
    # --------------------------------------------------------

    if st.button(
        "＋  New Chat",
        use_container_width=True
    ):

        st.session_state.messages = []

        st.rerun()


    st.markdown(
        '<div class="sidebar-line"></div>',
        unsafe_allow_html=True
    )


    # --------------------------------------------------------
    # RECENT CONVERSATIONS
    # --------------------------------------------------------

    st.markdown(
        """
        <div class="sidebar-heading">
            ◷ &nbsp; Recent Conversations
        </div>
        """,
        unsafe_allow_html=True
    )


    if len(st.session_state.recent_chats) == 0:

        st.markdown(
            """
            <div style="
                color:#7a879d;
                font-size:13px;
                padding:8px 2px;
            ">
                No recent conversations
            </div>
            """,
            unsafe_allow_html=True
        )

    else:

        for chat in reversed(
            st.session_state.recent_chats[-8:]
        ):

            st.markdown(
                f"""
                <div class="recent-chat">
                    💬
                    <span>{chat}</span>
                </div>
                """,
                unsafe_allow_html=True
            )


    # --------------------------------------------------------
    # QUICK LINKS
    # --------------------------------------------------------

    st.markdown(
        '<div class="sidebar-line"></div>',
        unsafe_allow_html=True
    )


    st.markdown(
        """
        <div class="sidebar-heading">
            🔗 &nbsp; Quick Links
        </div>
        """,
        unsafe_allow_html=True
    )


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

        st.markdown(
            f"""
            <div class="quick-link">

                <div class="quick-left">

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
            """,
            unsafe_allow_html=True
        )


    st.markdown(
        '<div class="sidebar-line"></div>',
        unsafe_allow_html=True
    )


    # --------------------------------------------------------
    # CLEAR SESSIONS
    # --------------------------------------------------------

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

st.markdown(
    """
    <div class="main-area">

        <div class="wave-left"></div>

        <div class="wave-right"></div>

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
    """,
    unsafe_allow_html=True
)


# ============================================================
# QUESTION CARDS
# ============================================================

card_col1, card_col2, card_col3, card_col4, card_col5, card_col6 = (
    st.columns(6)
)


questions = [

    (
        "📋",
        "Purchase<br>Orders",
        "What is the total purchase order value?"
    ),

    (
        "🚚",
        "Shipments &<br>Deliveries",
        "Which shipments are delayed?"
    ),

    (
        "📊",
        "Inventory &<br>Warehouses",
        "What is the total available inventory value?"
    ),

    (
        "👥",
        "Suppliers",
        "Which suppliers have the highest purchase order value?"
    ),

    (
        "📦",
        "Products",
        "What are the top 10 products by inventory value?"
    ),

    (
        "📈",
        "Analytics<br>Reports",
        "Give me a supply chain summary."
    )

]


columns = [

    card_col1,
    card_col2,
    card_col3,
    card_col4,
    card_col5,
    card_col6
]


selected_question = None


for column, question in zip(
    columns,
    questions
):

    icon, title, actual_question = question


    with column:

        st.markdown(
            f"""
            <div class="question-card">

                <div class="question-icon">
                    {icon}
                </div>

                <div class="question-title">
                    {title}
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


# ============================================================
# SEARCH AREA
# ============================================================

st.markdown(
    """
    <div style="
        height: 55px;
    ">
    </div>
    """,
    unsafe_allow_html=True
)


search_col1, search_col2 = st.columns(
    [12, 1]
)


with search_col1:

    user_question = st.text_input(
        "Search",
        placeholder=(
            "Ask a question about suppliers, "
            "purchase orders, shipments, deliveries, "
            "warehouses, carriers, products, or inventory..."
        ),
        label_visibility="collapsed"
    )


with search_col2:

    search_clicked = st.button(
        "➤",
        use_container_width=True
    )


# ============================================================
# SEARCH PROCESSING
# ============================================================

if search_clicked and user_question.strip():

    question = user_question.strip()


    # --------------------------------------------------------
    # SAVE RECENT CHAT
    # --------------------------------------------------------

    st.session_state.recent_chats.append(
        question
    )


    # --------------------------------------------------------
    # USER MESSAGE
    # --------------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question
        }
    )


    # --------------------------------------------------------
    # BASIC RESPONSE
    #
    # Replace this section with your existing
    # Snowflake / Cortex / Agent logic.
    # --------------------------------------------------------

    question_lower = question.lower()


    if "purchase order" in question_lower:

        answer = (
            "I can analyze your purchase order data. "
            "Your Snowflake query logic can be connected "
            "here to return the actual purchase order results."
        )


    elif (
        "inventory" in question_lower
        or "stock" in question_lower
    ):

        answer = (
            "I can analyze your inventory data including "
            "inventory value, quantity, warehouses, "
            "categories, brands, stockouts, and excess stock."
        )


    elif (
        "shipment" in question_lower
        or "delivery" in question_lower
    ):

        answer = (
            "I can analyze shipment and delivery information "
            "including delayed shipments, delivery status, "
            "and logistics performance."
        )


    elif "supplier" in question_lower:

        answer = (
            "I can analyze supplier performance, "
            "purchase order values, supplier activity, "
            "and supply-chain performance."
        )


    else:

        answer = (
            "I can help you analyze your Supply Chain data "
            "including purchase orders, suppliers, shipments, "
            "deliveries, inventory, warehouses, products, "
            "and logistics."
        )


    # --------------------------------------------------------
    # SAVE ASSISTANT MESSAGE
    # --------------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )


    st.rerun()


# ============================================================
# DISPLAY CHAT MESSAGES
# ============================================================

if st.session_state.messages:

    st.markdown(
        """
        <div style="
            max-width:1100px;
            margin:35px auto 0 auto;
            position:relative;
            z-index:5;
        ">
        """,
        unsafe_allow_html=True
    )


    for message in st.session_state.messages:

        if message["role"] == "user":

            st.markdown(
                f"""
                <div class="chat-message">

                    <div style="
                        font-weight:600;
                        color:#0754d8;
                        margin-bottom:8px;
                    ">
                        👤 You
                    </div>

                    <div style="
                        color:#15284e;
                        font-size:16px;
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

                    <div style="
                        font-weight:600;
                        color:#0754d8;
                        margin-bottom:8px;
                    ">
                        🤖 Dilytics AI
                    </div>

                    <div style="
                        color:#15284e;
                        font-size:16px;
                        line-height:1.6;
                    ">
                        {message["content"]}
                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )


    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )
