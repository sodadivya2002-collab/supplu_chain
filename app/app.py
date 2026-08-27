import streamlit as st
from snowflake.snowpark import Session

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Supply Chain Chatbot",
    page_icon="📦",
    layout="centered"
)

# ============================================================
# HEADER
# ============================================================

st.title("📦 Supply Chain Chatbot")
st.caption("Powered by Snowflake Cortex AI")

# ============================================================
# SNOWFLAKE CONNECTION
# ============================================================

@st.cache_resource
def get_snowflake_session():
    """
    Create and cache a Snowflake Snowpark session
    using credentials stored in Streamlit Secrets.
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

    return Session.builder.configs(connection_parameters).create()


# ============================================================
# CREATE SNOWFLAKE SESSION
# ============================================================

try:
    session = get_snowflake_session()

    st.sidebar.success("✅ Connected to Snowflake")

except Exception as e:

    st.sidebar.error(
        f"❌ Snowflake connection failed: {str(e)}"
    )

    st.stop()


# ============================================================
# CORTEX AI FUNCTION
# ============================================================

def ask_cortex(user_question: str) -> str:
    """
    Send the user's question to Snowflake Cortex COMPLETE
    and return the generated response.
    """

    system_prompt = """
You are an expert Supply Chain Assistant.

Your job is to answer questions related to:

- Sales orders
- Purchase orders
- Inventory
- Shipments
- Deliveries
- Suppliers
- Materials
- Plants
- Warehouses
- Logistics
- Supply chain operations

Answer questions clearly, professionally, and concisely.

If the question is outside the supply-chain domain,
politely explain that you are designed to help with
supply-chain-related questions.
"""

    # Combine system instructions with user question
    full_prompt = f"""
{system_prompt}

User Question:
{user_question}
"""

    try:

        # Escape single quotes so the question does not
        # break the SQL statement.
        safe_prompt = full_prompt.replace("'", "''")

        result = session.sql(
            f"""
            SELECT SNOWFLAKE.CORTEX.COMPLETE(
                'llama3.1-70b',
                '{safe_prompt}'
            ) AS response
            """
        ).collect()

        if result:

            response = result[0]["RESPONSE"]

            if response:
                return response

            return "⚠️ Cortex returned an empty response."

        return "⚠️ No response was returned from Snowflake Cortex."

    except Exception as e:

        return f"⚠️ Error while calling Snowflake Cortex: {str(e)}"


# ============================================================
# INITIALIZE CHAT HISTORY
# ============================================================

if "messages" not in st.session_state:

    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "Hello! 👋 I'm your Supply Chain Assistant "
                "powered by Snowflake Cortex.\n\n"
                "How can I help you today?"
            )
        }
    ]


# ============================================================
# DISPLAY CHAT HISTORY
# ============================================================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])


# ============================================================
# CHAT INPUT
# ============================================================

if prompt := st.chat_input(
    "Ask about orders, inventory, shipments..."
):

    # --------------------------------------------------------
    # Add user message to chat history
    # --------------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    # --------------------------------------------------------
    # Display user message
    # --------------------------------------------------------

    with st.chat_message("user"):

        st.markdown(prompt)

    # --------------------------------------------------------
    # Generate Cortex response
    # --------------------------------------------------------

    with st.chat_message("assistant"):

        with st.spinner("Thinking with Snowflake Cortex..."):

            response = ask_cortex(prompt)

            st.markdown(response)

    # --------------------------------------------------------
    # Save assistant response
    # --------------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response
        }
    )
