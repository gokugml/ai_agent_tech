from collections.abc import Sequence
from typing import Annotated, TypedDict

from langchain.chat_models import init_chat_model
from langchain_core.messages import AnyMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import StructuredTool  # , tool
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import tools_condition
from langgraph.types import RetryPolicy
from pydantic import BaseModel, Field

from user_config import settings


class GetCoinInfoInput(BaseModel):
    name: str = Field(description="coin name")


def get_coin_info(name: str) -> str:
    """Mock function to simulate getting coin info."""
    coin_map = {
        "bitcoin": "0x0001",
        "ethereum": "0x0002",
    }
    if coin_id := coin_map.get(name.lower()):
        return coin_id
    else:
        raise ValueError(f"Coin '{name}' not found.")


get_coin_info_tool = StructuredTool(
    name="Get_Coin_Info",
    description="This tool retrieves the coin information based on the provided name.",
    func=get_coin_info,
    args_schema=GetCoinInfoInput,
)

