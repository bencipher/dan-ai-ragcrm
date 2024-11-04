from langchain.agents import AgentExecutor
from config import df_data_mine, llm, memory

from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent

from templates import suffix_template
from langchain.agents.format_scratchpad import format_log_to_str
from langchain.agents.output_parsers import ReActSingleInputOutputParser
from prompt import agent_prompt
from tools import (
    advanced_analysis_tool,
    email_tool,
    simple_analysis_tool,
    task_planner_tool,
)

global_agent = create_pandas_dataframe_agent(
    llm,
    df=df_data_mine,
    verbose=True,
    agent_type="tool-calling",
    allow_dangerous_code=True,
    return_intermediate_steps=True,
    early_stopping_method="force",
    max_iterations=30,
    suffix=suffix_template,
)


llm_with_stop = llm.bind(stop=["\nObservation"])

supervisor_agent = (
    {
        "input": lambda x: x["input"],
        "agent_scratchpad": lambda x: format_log_to_str(x["intermediate_steps"]),
        "chat_history": lambda x: x["chat_history_summary"],
    }
    | agent_prompt()
    | llm_with_stop
    | ReActSingleInputOutputParser()
)
tools = [email_tool, task_planner_tool, simple_analysis_tool, advanced_analysis_tool]

executor = AgentExecutor(
    agent=supervisor_agent, tools=tools, verbose=True, memory=memory
)
