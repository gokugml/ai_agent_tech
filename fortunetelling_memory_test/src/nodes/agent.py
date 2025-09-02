from langchain.chat_models import init_chat_model
from langchain.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig

from src.config import settings
from src.prompts.system_prompt import get_system_prompt
from src.state import State
from src.tools.memobase_memory import memory_tools


def agent(state: State):
    model = init_chat_model(
        model="openai:gpt-4o-mini",
        api_key=settings.OPENAI_API_KEY,
        base_url=settings.OPENAI_BASE_URL,
        temperature=0.6,
    )
    system_prompt = get_system_prompt(state["profile"], state.get("retrieved_profile"))
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("placeholder", "{messages}"),
    ]
    )
    llm = prompt | model.bind_tools(memory_tools)
    response = llm.invoke({"messages": state["messages"]})
    return {"messages": response}
