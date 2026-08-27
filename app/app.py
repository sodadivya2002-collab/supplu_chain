import streamlit as st

st.set_page_config(
    page_title="Supply Chain Chatbot",
    page_icon="📦",
    layout="wide"
)

st.title("📦 Supply Chain Chatbot")
st.caption("Ask about orders, inventory, shipments or upload documents")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
if prompt := st.chat_input("Type your question here..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Temporary bot response (we will improve this later)
    reply = f"You asked: **{prompt}**\n\nThis is a placeholder response. Real logic coming soon!"

    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.markdown(reply)
