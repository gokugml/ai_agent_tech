from datetime import datetime

from langchain_core.runnables import RunnableConfig
from memobase import ChatBlob, MemoBaseClient

from src.nodes.memu_memory import extract_latest_conversation
from src.state import State

client = MemoBaseClient(
    project_url="https://api.memobase.dev",
    api_key="sk-proj-c20d8e576c03e093-51ccbf00c41cf79b6c5b7eada48c7852",
)


def retrieve_default_categories(state: State, config: RunnableConfig):
    if config.get("configurable"):
        u = client.get_or_create_user(user_id=config["configurable"].get("session_id"))
        # try:
        #     u = client.get_user(user_id=config["configurable"].get("session_id"))
        # except Exception:
        #     print("add usre")
        #     u = client.add_user({"name": config["configurable"].get("session_id")})
        #     print(u)
        # u = client.get_user(user_id=u)
        context = u.context()
        return {"retrieved_profile": context}


def memory_store(state: State, config: RunnableConfig):
    if config.get("configurable"):
        conversation = extract_latest_conversation(state["messages"])
        u = client.get_or_create_user(user_id=config["configurable"].get("session_id"))
        b = ChatBlob(messages=conversation)
        bid = u.insert(b)
        u.flush(sync=True)
        # client.memorize_conversation(
        #     conversation=conversation,
        #     user_id=config["configurable"].get("session_id"),
        #     user_name=config["configurable"].get("session_id"),
        #     agent_id="test_chatbot",
        #     agent_name="Test ChatBot",
        #     session_date=datetime.now().isoformat(),
        # )
