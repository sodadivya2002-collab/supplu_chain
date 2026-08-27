import streamlit as st
from snowflake.snowpark import Session
import json

# -------------------- Page Config --------------------
st.set_page_config(
    page_title="Supply Chain Chatbot",
    page_icon="📦",
    layout="centered"
)

st.title("📦 Supply Chain Chatbot")
st.caption("Powered by Snowflake Cortex AI")

# -------------------- Snowflake Connection --------------------
@st.cache_resource
def get_snowflake_session():
    """Create and cache Snowflake session using Streamlit secrets"""
    connection_parameters = {
        "account": st.secrets["snowflake"]["XYUHKAV-XRB12650"],
        "user": st.secrets["snowflake"]["PBCS"],
        "password": st.secrets["snowflake"]["Dilytics@12345"],
        "role": st.secrets["snowflake"]["ACCOUNTADMIN"],
        "warehouse": st.secrets["snowflake"]["COMPUTE_WH"],
        "database": st.secrets["snowflake"]["SUPPLY_CHAIN_DW"],
        "schema": st.secrets["snowflake"]["GOLD"]
    }
    return Session.builder.configs(connection_parameters).create()

# Create session
try:
    session = get_snowflake_session()
    st.sidebar.success("✅ Connected to Snowflake")
except Exception as e:
    st.sidebar.error(f"❌ Snowflake connection failed: {e}")
    st.stop()

# -------------------- Cortex Function --------------------
def ask_cortex(user_question: str) -> str:
    """
    Send the user question to Snowflake Cortex COMPLETE
    and return the AI response.
    """
    system_prompt = """
    You are an expert Supply Chain Assistant.
    Answer questions about orders, inventory, shipments, suppliers, and logistics clearly and professionally.
    If the question is outside supply chain, politely say so.
    """

    full_prompt = f"{system_prompt}\n\nUser Question: {user_question}"

    try:
        # Call Cortex COMPLETE
        result = session.sql(f"""
            SELECT SNOWFLAKE.CORTEX.COMPLETE(
                'llama3.1-70b',
                $$ {full_prompt} $$
            ) AS response
        """).collect()

        return result[0]["RESPONSE"]

    except Exception as e:
        return f"⚠️ Error while calling Cortex: {str(e)}"

# -------------------- Chat History --------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hello! 👋 I'm your Supply Chain Assistant powered by Snowflake Cortex. How can I help you today?"
        }
    ]

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# -------------------- Chat Input --------------------
if prompt := st.chat_input("Ask about orders, inventory, shipments..."):
    
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get response from Cortex
    with st.chat_message("assistant"):
        with st.spinner("Thinking with Snowflake Cortex..."):
            response = ask_cortex(prompt)
            st.markdown(response)

    # Save assistant response
    st.session_state.messages.append({"role": "assistant", "content": response})
