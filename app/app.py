import streamlit as st

st.set_page_config(
    page_title="Supply Chain Chatbot",
    page_icon="📦",
    layout="centered"
)

st.title("📦 Supply Chain Chatbot")
st.write("Ask me anything about orders, inventory, shipments, or suppliers.")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I'm your Supply Chain Assistant. How can I help you today?"}
    ]

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Type your question here..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Simple logic for responses (we can improve this later with Snowflake + LLM)
    prompt_lower = prompt.lower()

    if "order" in prompt_lower:
        response = "You can track orders by providing an Order ID. Example: 'What is the status of order 12345?'"
    elif "inventory" in prompt_lower or "stock" in prompt_lower:
        response = "I can help you check inventory levels. Please tell me the product name or SKU."
    elif "shipment" in prompt_lower or "delivery" in prompt_lower:
        response = "For shipment tracking, please provide the tracking number or Order ID."
    elif "hello" in prompt_lower or "hi" in prompt_lower:
        response = "Hello! How can I assist you with supply chain today?"
    else:
        response = f"I understood your question: **{prompt}**\n\n(This is a basic version. We will connect it to Snowflake and AI later.)"

    # Add assistant response
    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.markdown(response)
