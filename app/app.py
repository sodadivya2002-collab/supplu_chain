import streamlit as st
from snowflake.snowpark import Session
import json


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Dilytics Supply Chain AI",
    page_icon="📦",
    layout="wide"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    /* ========================================================
       MAIN FIXED HEADER
       ======================================================== */

    .fixed-main-header {
        position: sticky;
        top: 0;
        z-index: 999;
        background-color: white;
        padding-top: 10px;
        padding-bottom: 15px;
        margin-bottom: 10px;
    }

    .main-title {
        font-size: 2.4rem;
        font-weight: 700;
        line-height: 1.2;
        color: #30313d;
    }

    .main-subtitle {
        margin-top: 10px;
        font-size: 1rem;
        color: #8b8d98;
    }

    /* ========================================================
       BUTTONS
       ======================================================== */

    div[data-testid="stButton"] > button {
        border-radius: 8px;
        font-weight: 500;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SNOWFLAKE CONNECTION
# ============================================================

@st.cache_resource
def get_snowflake_session():

    """
    Create and cache Snowflake session.

    Snowflake credentials are read from
    Streamlit Cloud Secrets.
    """

    connection_parameters = {

        "account": st.secrets["snowflake"]["account"],

        "user": st.secrets["snowflake"]["user"],

        "password": st.secrets["snowflake"]["password"],

        "role": st.secrets["snowflake"]["role"],

        "warehouse": st.secrets["snowflake"]["warehouse"],

        "database": st.secrets["snowflake"]["database"],

        "schema": st.secrets["snowflake"]["schema"]

    }

    return (
        Session
        .builder
        .configs(connection_parameters)
        .create()
    )


# ============================================================
# CREATE SNOWFLAKE SESSION
# ============================================================

try:

    session = get_snowflake_session()

    st.sidebar.success(
        "✅ Connected to Snowflake"
    )

except Exception as e:

    st.sidebar.error(
        f"❌ Snowflake connection failed: {e}"
    )

    st.stop()


# ============================================================
# CHAT SESSION STATE
# ============================================================

if "messages" not in st.session_state:

    st.session_state.messages = [

        {
            "role": "assistant",

            "content":
                """
Hello! 👋 I'm your **Supply Chain Assistant**
powered by Snowflake.

How can I help you today?
"""
        }

    ]


# ============================================================
# FIXED STATIC MAIN HEADER
# ============================================================

st.markdown(
    """
    <div class="fixed-main-header">

        <div class="main-title">
            💬 Dilytics Supply Chain AI
        </div>

        <div class="main-subtitle">
            Ask questions in natural language to explore
            suppliers, purchase orders, shipments,
            deliveries, warehouses, carriers, and products.
        </div>

    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# RESET THREAD
# ============================================================

reset_col1, reset_col2, reset_col3 = st.columns(
    [4.5, 1.2, 0.3]
)


with reset_col2:

    if st.button(
        "🔄 Reset Thread",
        use_container_width=True
    ):

        st.session_state.messages = [

            {
                "role": "assistant",

                "content":
                    """
Hello! 👋 I'm your **Supply Chain Assistant**
powered by Snowflake.

How can I help you today?
"""
            }

        ]

        st.rerun()


# ============================================================
# SUGGESTED QUESTIONS
# ============================================================

with st.expander(
    "💡 What exact questions can I ask this assistant?",
    expanded=False
):

    st.markdown(
        """
### 📋 Purchase Orders

* What is the total purchase order count?

* What is the total ordered quantity?

* What is the total ordered value?

* What is the total open commitment?

* What is the total rejected value?

* What is the purchase order status breakdown?

* What is the purchase order value by supplier?

* What is the purchase order value by warehouse?


### 🚚 Shipments & Deliveries

* What is the total number of shipments?

* How many shipments are currently in transit?

* How many shipments have been delivered?

* How many shipments are delayed?

* What is the average delivery delay?

* What is the average delivery delay by supplier?

* What are the top delay reasons?


### 🏭 Suppliers

* What is the supplier on-time delivery percentage?

* Which suppliers have the highest purchase order value?

* Which suppliers are high risk?

* Which suppliers are single source?

* Which suppliers have active contracts?

* What are the supplier quality ratings?


### 🚢 Logistics

* What is the total freight cost?

* What is the total landed cost?

* What is freight cost by carrier?

* What is the shipment count by carrier?

* What is the shipment count by shipping mode?


### 📦 Products

* What are the top products by ordered value?

* What is the ordered value by product category?

* What is the ordered quantity by product category?

* What is the ordered value by brand?
"""
    )


# ============================================================
# VERIFIED ONBOARDING QUESTIONS
# ============================================================

st.markdown(
    "### 💡 Verified Onboarding Questions:"
)


q1, q2, q3, q4, q5 = st.columns(5)


quick_question = None


with q1:

    if st.button(
        "📋 Total Purchase Orders",
        use_container_width=True
    ):

        quick_question = (
            "What is the total purchase order count?"
        )


with q2:

    if st.button(
        "📦 Total Ordered Quantity",
        use_container_width=True
    ):

        quick_question = (
            "What is the total ordered quantity?"
        )


with q3:

    if st.button(
        "🏭 Supplier On-Time %",
        use_container_width=True
    ):

        quick_question = (
            "What is the supplier on-time delivery percentage?"
        )


with q4:

    if st.button(
        "❌ Total Rejected Value",
        use_container_width=True
    ):

        quick_question = (
            "What is the total rejected value?"
        )


with q5:

    if st.button(
        "🚚 Total Shipments",
        use_container_width=True
    ):

        quick_question = (
            "What is the total number of shipments?"
        )


# ============================================================
# DISPLAY CHAT HISTORY
# ============================================================

for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )


# ============================================================
# CORTEX FUNCTION
# ============================================================

def ask_cortex(
    user_question: str
) -> str:

    """
    Send user question to Snowflake Cortex.
    """

    system_prompt = """
You are an expert Supply Chain Assistant.

You answer questions about:

- Purchase Orders
- Suppliers
- Shipments
- Deliveries
- Warehouses
- Carriers
- Products
- Logistics
- Freight
- Supplier Performance

Answer clearly and professionally.

If the question is outside the supply chain domain,
politely explain that you specialize in supply chain
questions.
"""


    full_prompt = (
        f"{system_prompt}\n\n"
        f"User Question: {user_question}"
    )


    # Escape single quotes
    safe_prompt = full_prompt.replace(
        "'",
        "''"
    )


    try:

        result = session.sql(
            f"""
            SELECT SNOWFLAKE.CORTEX.COMPLETE(
                'llama3.1-70b',
                '{safe_prompt}'
            ) AS RESPONSE
            """
        ).collect()


        if result:

            return result[0]["RESPONSE"]


        return (
            "I could not generate a response."
        )


    except Exception as e:

        return (
            f"⚠️ Error while calling Snowflake Cortex: "
            f"{str(e)}"
        )


# ============================================================
# CHAT INPUT
# ============================================================

prompt = st.chat_input(
    "Ask about suppliers, purchase orders, shipments, "
    "deliveries, warehouses, carriers, or products..."
)


# ============================================================
# HANDLE QUICK QUESTION
# ============================================================

if quick_question:

    prompt = quick_question


# ============================================================
# PROCESS QUESTION
# ============================================================

if prompt:

    # --------------------------------------------------------
    # USER MESSAGE
    # --------------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )


    with st.chat_message("user"):

        st.markdown(prompt)


    # --------------------------------------------------------
    # ASSISTANT RESPONSE
    # --------------------------------------------------------

    with st.chat_message("assistant"):

        with st.spinner(
            "Thinking with Snowflake..."
        ):

            response = ask_cortex(
                prompt
            )


        st.markdown(
            response
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


    st.rerun()
