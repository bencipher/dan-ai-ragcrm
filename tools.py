from typing import Union, List
from langchain.tools import StructuredTool
from config import llm, df_data_mine
from agents import global_agent as agent
from models import EmailModel, KPIModel, Task, TaskList
from langchain_core.tools import Tool
from prompt import markdown_prompt, task_prompt, kpi_prompt, email_prompt

dataframe = df_data_mine


def data_analysis_tool():
    """
    This tool gets a clearly defined question or list of questions, and performs analysis to answer those objectives using the underlying dataset
    """

    def get_insights(query: Union[str, List[str]]) -> str:
        print(f"{query=}")
        # json_agent = get_json_agent("./inventory_prices_dict.json")
        report = []
        result = ""

        if isinstance(query, list):
            for q in query:
                response = agent.invoke(q)
                result = response.get("output", response.get("result", ""))
                report.append(result)
        else:
            response = agent.invoke(query)
            result = response.get("output", response.get("result", ""))
            report.append(result)
        return report

    data_tool = StructuredTool.from_function(
        func=get_insights,
        name="analyze_single_metric",
        description="""
            This tool is optimized for specific metric-based insights or KPI analysis.
            Do not use it for vague or broad questions like tell me about the dataset.
            Use when user have single or multiple questions coming from the KPI tool about specific key performance indicators (KPIs) or particular aspects
            of the dataset—like sales trends, customer satisfaction, or financial ratios—this tool identifies
            relevant metrics and provides detailed insights.

            Best suited for queries such as:
                - "Analyze customer retention KPIs."
                - "What are the trends in monthly revenue?"
            """,
    )

    return data_tool


def generate_kpi_questions(context: str) -> List[str]:
    """
    Break down a generic question into more specific objective and direct question for analysis
    Args:
        query (str): User query describing the dataset.

    Returns:
        str: Markdown-formatted string with the domain, KPIs, and questions.

    Example:
        Input: "Analyze sales data."
        Output:
            - **Domain:** Sales
            - **KPIs:** Revenue, Growth Rate
            - **Questions:** What is the total revenue? How has sales changed over time?
    """

    chain = kpi_prompt | llm.with_structured_output(KPIModel)
    output = chain.invoke({"query": context, "dataframe_summary": dataframe})

    # Run the LLM with the formatted prompt
    return output


def generate_email(context: str) -> str:
    """
    Generates a structured email based on provided context and data using a large language model.

    This tool constructs professional emails by interpreting the purpose (e.g., "Provide a project update" or "Send New Year wishes")
    and available data within the given context. It categorizes recipients, generates a clear subject, body, and sign-off,
    and formats the email body in markdown.

    Args:
        context (str): The purpose of the email (e.g., "Project update").

    Returns:
        str: Structured email content formatted in markdown as an `EmailModel` containing:
            - `recipients_email` (List[str]): List of recipient email addresses.
            - `recipient_type` (str): The category of recipients (e.g., "IT", "HR").
            - `body` (str): The email body in markdown.
            - `subject` (str): The email subject line.
            - `sign_off` (str): A professional closing (e.g., "Best regards").
    """

    email_body = email_prompt | llm.with_structured_output(EmailModel)
    return email_body.invoke({"context": context})


def generate_tasks(context: str) -> List[Task]:
    """

        Uses an LLM to create a structured list of tasks from a dataset given a context.

    Args:
        context (str): Description of the goal or project scope.

    Returns:
        TaskList: A structured list of tasks generated from the context.

    Example:
        Context: "Complete phase 1 of the project."
        Data: "email=[j.doe@company.com, l.jones@company.com], department=IT, project='Mobile App for New Client', deadline='October 2025', any_other_field='any other data'"

        Output: TaskList(tasks=[
                Task(task_name="Draft Documentation",
                     task_details="Draft the initial documentation for the project phase, including requirements and objectives.",
                     task_priority="High",
                     task_status="New"),
                Task(task_name="Develop Prototype",
                     task_details="Create a working prototype based on the drafted specifications and requirements before (...specify date based on current time).",
                     task_priority="Medium",
                     task_status="Pending")
            ])
    """

    chain = task_prompt | llm.with_structured_output(TaskList)
    return chain.invoke({"context": context})


def generate_markdown_report(user_question, kpi_breakdown, rough_analysis):

    qa_chain = markdown_prompt | llm

    response = qa_chain.invoke(
        {
            "user_question": user_question,
            "kpi_questions": kpi_breakdown,
            "analysis_result": rough_analysis,
        }
    )
    return response.content


def get_insights(query: Union[str, List[str]]) -> str:
    report = []
    result = ""
    if isinstance(query, list):
        for q in query:
            response = agent.invoke(q)
            result = response.get("output", response.get("result", ""))
            report.append(result)
    else:
        response = agent.invoke(query)
        result = response.get("output", response.get("result", ""))
        report.append(result)
    return report


def complex_analysis(query: str) -> str:
    kpi_questions = generate_kpi_questions(query)
    analysis_result = get_insights(kpi_questions)
    print(analysis_result)
    report = generate_markdown_report(query, kpi_questions, analysis_result)
    return report


email_tool = Tool(
    name="generate_email",
    func=lambda context: generate_email(context),
    description="""
    Generates a professional email based on the provided context and the just analysed data.
        context: The user’s goal or purpose for the email (e.g., 'Provide a project update').
        This tool is structured to use the analysis data and user goal to construct an email with a clear salutation, body, sign-off, and subject."
    """,
)

task_planner_tool = Tool(
    name="generate_tasks",
    func=lambda context: generate_tasks(context),
    description="""
    Produces a structured Markdown list of tasks based on provided context. Each task is assigned a title and description, suitable for outlining project requirements.
    """,
)

simple_analysis_tool = Tool(
    name="analyse_direct_metric_question",
    func=lambda query: get_insights(query),
    description="""analyse simple data analysis question or list of questions e.g. (who has highest revenue, what are the top 3, what is the relationship btw quantity A and B, average, comparison, etc.)""",
)

advanced_analysis_tool = Tool(
    name="analyse_vague_or_broad_question",
    func=lambda query: complex_analysis(query),
    description="""useful when the question does not have any clear metric, variables or kpis to analyse e.g. (what is the dataset about, generate report on the impact of this phenomena on the dataset, describe the dataset)""",
)


def convert_to_structured_tool(tool):
    return StructuredTool.from_function(
        tool.func, name=tool.name, description=tool.description
    )
