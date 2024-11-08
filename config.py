import os
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
import pandas as pd
from functools import lru_cache

from persistence import load_file_to_df
from dotenv import load_dotenv

from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from templates import suffix_template

load_dotenv()


llm = ChatOpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
    temperature=0,
    model="gpt-4o-mini",
    streaming=True,
)

memory = ConversationBufferMemory(
    memory_key="chat_history_summary",
    llm=llm,
    return_messages=True,
    max_token_limit=1000,
)

# Initialize global variables
dataframe = None
agent = None


@lru_cache(maxsize=1)
def get_data(filepath: str) -> pd.DataFrame:
    global dataframe
    if dataframe is None:
        dataframe = load_file_to_df(filepath)  # Load your DataFrame here
    return dataframe


def get_current_df():
    if dataframe is None:
        raise RuntimeError("No dataset to work with for analysis")
    return dataframe


def initialize_agent() -> None:
    global agent
    if dataframe is not None:
        print(f"Reinitialized agent with {dataframe=}")
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
            prefix="Go through the data head  to be able to get the  right key for the dataset",
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


# YOU HIGH COMPONENT
light_theme = {
    "palette": {"background": {"default": "#d580ff"}, "primary": {"main": "#ffffff"}}
}

dark_theme = {
    "palette": {"background": {"default": "#471061"}, "primary": {"main": "#000000"}}
}

# dataframe = None
