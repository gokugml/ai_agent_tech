from langchain_core.runnables import RunnableConfig
from langchain_core.tools import StructuredTool, tool
from memobase import MemoBaseClient
from pydantic import BaseModel, Field

client = MemoBaseClient(
    project_url="https://api.memobase.dev",
    api_key="sk-proj-c20d8e576c03e093-51ccbf00c41cf79b6c5b7eada48c7852",
)


def recall_memories(chats: list[dict[str, str]], config: RunnableConfig):
    """Retrieving the user's memory
    
    If you only need to retrieve the most "contextual" or relevant profile for the current conversation, you can pass the latest chat information directly
    """
    if config.get("configurable"):
        user = client.get_or_create_user(user_id=config["configurable"].get("session_id"))
        response = user.profile(chats=chats, need_json=True)
        return response
    raise RuntimeError("notfound configurable")


class RecallMemoriesInput(BaseModel):
    chats: list[dict[str, str]] = Field(description="Chat message or query content")
    
    class Config:
        json_schema_extra = {
            "examples": [
                {"chats": [{"role": "user", "content": "Find some restaurants for me"}]},
                {"chats": [
                    {"role": "user", "content": "user_example_input"},
                    {"role": "assistant", "content": "ai_example_output"},
                ]}
            ]
        }


recall_memories_tool = StructuredTool(
    name="Recall_Memories",
    description="""Retrieving the user's memory

If you only need to retrieve the most "contextual" or relevant profile for the current conversation, you can pass the latest chat information directly""",
    args_schema=RecallMemoriesInput,
    runc=recall_memories,
)

memory_tools = [recall_memories_tool]