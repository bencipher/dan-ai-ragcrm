from langchain.agents import AgentExecutor
from config import llm, memory


from langchain.agents.format_scratchpad import format_log_to_str
from langchain.agents.output_parsers import ReActSingleInputOutputParser
from prompt import agent_prompt
from tools import (
    advanced_analysis_tool,
    email_tool,
    simple_analysis_tool,
    task_planner_tool,
)

llm_with_stop = llm.bind(stop=["\nObservation"])
tools = [email_tool, task_planner_tool, simple_analysis_tool, advanced_analysis_tool]

supervisor_agent = (
    {
        "input": lambda x: x["input"],
        "agent_scratchpad": lambda x: format_log_to_str(x["intermediate_steps"]),
        "chat_history": lambda x: x["chat_history_summary"],
    }
    | agent_prompt(tools)
    | llm_with_stop
    | ReActSingleInputOutputParser()
)

executor = AgentExecutor(
    agent=supervisor_agent,
    tools=tools,
    verbose=True,
    memory=memory,
    handle_parsing_errors=True,
)
