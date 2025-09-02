"""聊天机器人状态定义"""

from typing import Annotated, Sequence, TypedDict

from langgraph.graph.message import AnyMessage, add_messages


class ChatbotState(TypedDict):
    """聊天机器人状态"""
    session_id: str
    messages: Annotated[Sequence[AnyMessage], add_messages]