import hashlib
import io
import pandas as pd
import streamlit as st
from config import get_data, initialize_agent
from agents import executor

# Set up page configuration
st.set_page_config(page_title="AI Excel Chat RAG", layout="wide")

# Initialize session state variables
if "conversation" not in st.session_state:
    st.session_state.conversation = [
        {
            "role": "assistant",
            "content": "Hi! I am your AI assistant. let's chat about your data, do you have any question!",
        },
    ]
if "uploaded_data" not in st.session_state:
    st.session_state.uploaded_data = False
if "dataset" not in st.session_state:
    st.session_state.dataset = None


def hash_io(input_io):
    data = input_io.read()
    input_io.seek(0)
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.md5(data).hexdigest()


dataframe = None


@st.cache_data(ttl="2h")
def handle_file_upload(uploaded_file):
    if uploaded_file is not None:
        try:
            # Read the uploaded file into a DataFrame
            # Use the appropriate method based on the file type
            if uploaded_file.type == "text/csv":
                st.session_state.dataset = pd.read_csv(
                    uploaded_file
                )  # Read CSV directly
            elif uploaded_file.type in [
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "application/vnd.ms-excel",
            ]:
                st.session_state.dataset = pd.read_excel(
                    uploaded_file
                )  # Read Excel directly
            else:
                st.error("Unsupported file type. Please upload a CSV or Excel file.")
                return
            global dataframe
            if dataframe is None:
                dataframe = st.session_state.dataset
            print(f"{dataframe=}")
            initialize_agent()
            st.session_state.uploaded_data = True
            st.success("File uploaded successfully! You can now start chatting.")
        except Exception as e:
            st.error(f"Failed to load the file: {e}")

# Function to communicate with the agent
def chat_with_agent(user_message: str) -> str:
    if st.session_state.uploaded_data:
        response = executor.invoke({"input": user_message})
        return response.get("output")
    else:
        return "Please upload a dataset to start the analysis."


# Function to handle sending a message
def send_message(user_message):
    st.session_state.conversation.append({"role": "user", "content": user_message})
    response = chat_with_agent(user_message)
    st.session_state.conversation.append({"role": "assistant", "content": response})


# Page layout
st.title("AI Excel Chat RAG")
st.subheader("Chat with your AI assistant")

# File uploader
uploaded_file = st.file_uploader("Upload your dataset file", type=["csv", "xlsx"])
if uploaded_file:
    handle_file_upload(uploaded_file)


def display():
    for entry in st.session_state.conversation:
        if entry["role"] == "user":
            st.markdown(f"**You**: {entry['content']}")
        elif entry["role"] == "assistant":
            st.markdown(f"**AI**: {entry['content']}")


# Chat Interface
if st.session_state.uploaded_data:
    user_message = st.text_input("Your message:", key="user_input")
    if st.button("Send"):
        send_message(user_message)
    display()
else:
    st.info("Upload a dataset file to start the conversation.")
