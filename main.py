import streamlit as st
from config import get_data, initialize_agent
from agents import executor

# Set up page configuration
st.set_page_config(page_title="AI Excel Chat RAG", layout="wide")

# Initialize session state variables
if "conversation" not in st.session_state:
    st.session_state.conversation = [
        {"role": "user", "content": "Who are you?"},
        {
            "role": "assistant",
            "content": "Hi! I am your AI assistant. Upload your data and let's chat!",
        },
    ]
if "uploaded_data" not in st.session_state:
    st.session_state.uploaded_data = False
if "dataset" not in st.session_state:
    st.session_state.dataset = None


# Function to handle file upload and agent initialization
def handle_file_upload(uploaded_file):
    if uploaded_file is not None:
        try:
            st.session_state.dataset = get_data(uploaded_file)
            initialize_agent()
            st.session_state.uploaded_data = True
            st.success("File uploaded successfully! You can now start chatting.")
        except ValueError as e:
            st.error(f"Failed to load the file: {e}")


# Function to communicate with the agent
def chat_with_agent(user_message: str) -> str:
    if st.session_state.uploaded_data:
        response = executor.invoke({"input": user_message})
        return response.get("output")
    else:
        return "Please upload a dataset to start the analysis."


# Function to handle sending a message
def send_message():
    user_message = st.session_state["user_input"]
    # Add user message to conversation history
    st.session_state.conversation.append({"role": "user", "content": user_message})
    # Get response from the agent
    response = chat_with_agent(user_message)
    # Add AI response to conversation history
    st.session_state.conversation.append({"role": "assistant", "content": response})
    # Clear the input field
    st.session_state["user_input"] = ""


# Page layout
st.title("AI Excel Chat RAG")

# File uploader
uploaded_file = st.file_uploader("Upload your dataset file", type=["csv", "xlsx"])
if uploaded_file:
    handle_file_upload(uploaded_file)

# Chat Interface
if st.session_state.uploaded_data:
    st.subheader("Chat with your AI assistant")
    for entry in st.session_state.conversation:
        if entry["role"] == "user":
            st.markdown(f"**You**: {entry['content']}")
        elif entry["role"] == "assistant":
            st.markdown(f"**AI**: {entry['content']}")

    # User input and send button
    st.text_input("Your message:", key="user_input")
    if st.button("Send"):
        send_message()
else:
    st.info("Upload a dataset file to start the conversation.")
