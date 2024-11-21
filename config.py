import os
import pandas as pd
import streamlit as st
from functools import lru_cache

from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from dotenv import load_dotenv

from persistence import load_filebytes_to_df
from templates import suffix_template

load_dotenv()


model = os.environ.get("MODEL", "DEFAULT")

if model.upper() == "OPENAI":
    llm = ChatOpenAI(
        temperature=0,
        model="gpt-4o-mini",
        streaming=True,
    )
elif model.upper() == "GEMINI":
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-pro",
        temperature=0,
        max_retries=3,
    )
else:
    llm = ChatGroq(
        model="gemma2-9b-it",
        temperature=0,
        max_retries=3,
        streaming=True,
    )
print(f"{model=} - {llm=}")
memory = ConversationBufferMemory(
    memory_key="chat_history_summary",
    llm=llm,
    return_messages=True,
    max_token_limit=1000,
)

# Initialize global variables
dataframe = None
agent = None


# @lru_cache(maxsize=1)
def get_data(params) -> pd.DataFrame:
    global dataframe
    if dataframe is None:
        dataframe = load_filebytes_to_df(params)
    return dataframe


def get_current_df():
    dataframe = st.session_state.dataset
    if dataframe is None:
        raise RuntimeError("No dataset to work with for analysis")
    return dataframe


def initialize_agent() -> None:
    global agent
    dataframe = get_current_df()
    if dataframe is not None:
        agent = create_pandas_dataframe_agent(
            llm,
            df=dataframe,  # Use the loaded DataFrame
            verbose=True,
            agent_type="tool-calling",
            allow_dangerous_code=True,
            return_intermediate_steps=True,
            early_stopping_method="force",
            max_iterations=30,
            suffix=suffix_template,
            prefix="Go through the data head to be able to get the  right key for the dataset",
        )
        print(f"{agent=}")
    else:
        raise ValueError("DataFrame is not available. Please upload a dataset first.")


def get_current_agent():
    """Return the current agent if initialized, otherwise raise an error."""
    print(f"Getting current agent: \n{agent=}\n")
    if agent is None:
        raise RuntimeError(
            "Agent has not been initialized. Please ensure the dataset is loaded and the agent is created."
        )
    return agent


# dataframe = None
