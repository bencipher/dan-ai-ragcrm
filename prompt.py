from langchain_core.prompts import PromptTemplate
from langchain import hub
from templates import (
    AGENT_TEMPLATE,
    EMAIL_TEMPLATE,
    KPI_TEMPLATE,
    QA_MD_TEMPLATE,
    TASK_TEMPLATE,
)

from langchain.tools.render import render_text_description

markdown_prompt = PromptTemplate(
    template=QA_MD_TEMPLATE,
    input_variables=["user_question", "kpi_questions", "analysis_result"],
)

task_prompt = PromptTemplate(
    template=TASK_TEMPLATE, input_variables=["context", "data"]
)

kpi_prompt = PromptTemplate(
    input_variables=["query", "dataframe_summary"], template=KPI_TEMPLATE
)

email_prompt = PromptTemplate(input_variables=["context"], template=EMAIL_TEMPLATE)

default_prompt = hub.pull("hwchase17/react-chat")
prompt = default_prompt.copy(update={"template": AGENT_TEMPLATE})

def agent_prompt(tools) -> PromptTemplate:
    return prompt.partial(
        tools=render_text_description(tools),
        tool_names=", ".join([t.name for t in tools]),
    )
