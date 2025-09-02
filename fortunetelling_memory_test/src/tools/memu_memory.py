from langchain_core.runnables import RunnableConfig
from langchain_core.tools import StructuredTool, tool
from memu import MemuClient
from pydantic import BaseModel, Field

from src.config import settings

client = MemuClient(base_url=settings.MEMU_BASE_URL, api_key=settings.MEMU_API_KEY)

@tool
def retrieve_related_clustered_categories(category_query: str, config: RunnableConfig):
    """Description:
    - Retrieves categories that have been automatically clustered based on semantic similarity
    - Returns the full contents in auto-generated memory categories

    When to Use:
    - For advanced semantic search for user queries
    """
    if config.get("configurable"):
        response = client.retrieve_related_clustered_categories(
            user_id=config["configurable"].get("session_id"),
            agent_id="test_chatbot",
            category_query=category_query,
        )
        return response
    raise RuntimeError("notfound configurable")


def retrieve_related_memory_items(query, config: RunnableConfig):
    if config.get("configurable"):
        response = client.retrieve_related_memory_items(query=query, user_id=config["configurable"].get("session_id"), agent_id="test_chatbot")
        return response
    raise RuntimeError("notfound configurable")


class RetrieveMemoryItemInput(BaseModel):
    query: str = Field(description="Query text")
    
    class Config:
        json_schema_extra = {
            "examples": [
                {"query": "What did I discuss about project X last month?"},
                {"query": "Retrieving relevant memories for context-aware responses"},
                {"query": "Building a timeline of specific events"},
            ]
        }


retrieve_related_memory_items_tool = StructuredTool(
    name="Retrieve_Related_Memory_Items",
    description="""Description:
Retrieves specific memory items related to the current context or query
Returns actual memory content rather than just categories

When to Use: For answering specific queries about past events or information
""",
    args_schema=RetrieveMemoryItemInput,
    func=retrieve_related_memory_items,
)


memory_tools = [retrieve_related_clustered_categories, retrieve_related_memory_items_tool]
