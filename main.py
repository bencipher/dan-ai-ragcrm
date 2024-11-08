from taipy.gui import Gui, State, notify

from config import (
    get_data,
    initialize_agent,
    light_theme,
    dark_theme,
    dataframe,
)

from agents import executor
from pages.root import root
from pages.file_manager import file_handler


import pandas as pd


pages = {
    "/": root,
    "dataset": file_handler,
}

context = "The following is a conversation with an AI assistant. The assistant is helpful, creative, clever, and very friendly.\n\nHuman: Hello, who are you?\nAI: I am an AI created by OpenAI. How can I help you today? "

conversation = {
    "Conversation": [
        "Who are you?",
        "Hi! I am your AI assistant. Upload your data and let's chat",
    ]
}

current_user_message = ""
uploaded_data = False


def request(state: State, user_message: str) -> str:
    """
    chat with the agent
    """
    print(f"Called with {user_message}")
    if state.uploaded_data:
        response = executor.invoke({"input": user_message})
        return response.get("output")
    return "Please upload a dataset you would like for me to analyse before continuing the conversation"


def send_message(state: State) -> None:
    """
    Send the user's message to the agent and update the conversation.

    Args:
        - state: The current state.
    """
    print(f"Current {state.__dict__=}")
    # Add the user's message to the context
    state.context += f"Human: \n {state.current_user_message}\n\n AI:"
    # Send the user's message to the API and get the response
    answer = request(state, state.current_user_message)
    # Add the response to the context for future messages
    state.context += answer
    # Update the conversation
    conv = state.conversation._dict.copy()
    conv["Conversation"] += [state.current_user_message]
    conv["Conversation"] += [answer]
    state.conversation = conv
    # Clear the input field
    state.current_user_message = ""


path = None
dataset = None


class State:
    def __init__(self):
        self.uploaded_data = False


def handle_file_post(state):  # rescue
    try:
        global dataframe
        dataframe = get_data(state.path)
        initialize_agent()
        state.uploaded_data = True
        state.dataset = dataframe
    except ValueError as e:
        print(e)


app = Gui(pages=pages)

if __name__ == "__main__":

    app.run(
        title="AI Excel Chat RAG",
        use_reloader=True,
        port=3636,
        light_theme=light_theme,
        dark_theme=dark_theme,
    )
