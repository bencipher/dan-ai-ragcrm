from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory

from persistence import get_uploaded_data


df_data_mine = get_uploaded_data()

llm = ChatOpenAI(temperature=0, model="gpt-4o-mini", streaming=True)
memory = ConversationBufferMemory(
    memory_key="chat_history_summary",
    llm=llm,
    return_messages=True,
    max_token_limit=1000,
)


light_theme = {
    "palette": {"background": {"default": "#d580ff"}, "primary": {"main": "#ffffff"}}
}

dark_theme = {
    "palette": {"background": {"default": "#471061"}, "primary": {"main": "#000000"}}
}
