import hashlib
import io
import os
import pprint
import pandas as pd
from pandas.errors import EmptyDataError
import streamlit as st
from config import get_data, initialize_agent
from agents import executor
from langchain_community.callbacks.streamlit import StreamlitCallbackHandler

# Set up page configuration
st.set_page_config(page_title="AI Excel Chat RAG", layout="wide")

# Initialize session state variables


dataframe = None

file_formats = {
    "csv": pd.read_csv,
    "xls": pd.read_excel,
    "xlsx": pd.read_excel,
    "xlsm": pd.read_excel,
    "xlsb": pd.read_excel,
}


@st.cache_data(ttl="2h")
def load_data(uploaded_file):
    try:
        ext = os.path.splitext(uploaded_file.name)[1][1:].lower()
    except:
        ext = uploaded_file.split(".")[-1]
    if ext in file_formats:
        try:
            data = file_formats[ext](uploaded_file)
            return data
        except EmptyDataError:
            st.error("No data is inside the file")
    else:
        st.error(f"Unsupported file format: {ext}")
        return None


def clear_submit():
    """Clears the session state related to the dataset and any previous conversations."""
    st.session_state.dataset = None
    st.session_state.conversation = []
    st.session_state.submit = False


# Page layout
st.title("AI Excel Chat RAG")
st.subheader("Chat with your AI assistant")

uploaded_file = st.file_uploader(
    "Upload a Data file",
    type=list(file_formats.keys()),
    help="Various File formats are Support",
    on_change=clear_submit,
)


if "conversation" not in st.session_state or st.sidebar.button(
    "Clear conversation history"
):
    st.session_state.conversation = []
if "uploaded_data" not in st.session_state:
    st.session_state.uploaded_data = False
if "dataset" not in st.session_state:
    st.session_state.dataset = None


if uploaded_file:
    st.session_state.dataset = load_data(uploaded_file)
    initialize_agent()
    st.session_state.uploaded_data = True
    st.chat_message("assistant").write(
        "Now that you have uploaded your data, let's chat about your data, do you have any question!"
    )


# Function to communicate with the agent
def chat_with_agent(user_message: str) -> str:
    if st.session_state.uploaded_data:
        try:
            response = executor.invoke({"input": user_message})
            return response.get("output")
        except Exception as e:
            return f"Error generating response: {str(e)}"
    else:
        return "Please upload a dataset to start the analysis."


if prompt := st.chat_input(
    placeholder="What is this data about?", disabled=not st.session_state.uploaded_data
):
    st.session_state.conversation.append({"role": "user", "content": prompt})
    # st.chat_message("user").write(prompt)
    with st.chat_message("assistant"):
        st_cb = StreamlitCallbackHandler(st.container(), expand_new_thoughts=False)
        response = chat_with_agent(st.session_state.conversation)
        st.session_state.conversation.append({"role": "assistant", "content": response})

for msg in st.session_state.conversation:
    st.chat_message(msg["role"]).write(msg["content"])
