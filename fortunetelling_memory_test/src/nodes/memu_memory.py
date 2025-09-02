from collections.abc import Sequence
from datetime import datetime

from langchain_core.messages import AIMessage, AnyMessage, HumanMessage, filter_messages
from langchain_core.runnables import RunnableConfig
from loguru import logger
from memu import MemuClient

from src.config import settings
from src.state import State

client = MemuClient(
    base_url=settings.MEMU_BASE_URL,
    api_key=settings.MEMU_API_KEY,
)


def extract_latest_conversation(messages: Sequence[AnyMessage]) -> list[dict[str, str]]:
    """从消息历史中提取最新的用户输入和AI回复

    使用 filter_messages 筛选最后一条用户消息和最后一条AI消息。
    由于一次调用只会有一条用户输入和一条最终AI输出，这种方式足够了。

    Args:
        messages: LangGraph 消息序列

    Returns:
        (user_input, ai_response) 元组，如果未找到则返回空字符串
    """
    if not messages:
        return "", ""

    # 获取最后一条用户消息
    human_messages: list[HumanMessage] = filter_messages(messages, include_types=[HumanMessage])
    last_human = human_messages[-1].text() if human_messages else ""

    # 获取最后一条AI消息（排除工具调用）
    ai_messages: list[AIMessage] = filter_messages(messages, include_types=[AIMessage], exclude_tool_calls=True)
    last_ai = ai_messages[-1].text() if ai_messages else ""

    logger.debug(f"提取对话对 - 用户: '{last_human[:50]}...', AI: '{last_ai[:50]}...'")
    return [
        {"role": "user", "content": last_human},
        {"role": "assistant", "content": last_ai},
    ]


def retrieve_default_categories(state: State, config: RunnableConfig):
    if config.get("configurable"):
        response = client.retrieve_default_categories(user_id=config["configurable"].get("session_id"), agent_id="test_chatbot")
        return {"retrieved_profile": response}
    raise RuntimeError("notfound configurable")


def memory_store(state: State, config: RunnableConfig):
    if config.get("configurable"):
        conversation = extract_latest_conversation(state["messages"])
        client.memorize_conversation(
            conversation=conversation,
            user_id=config["configurable"].get("session_id"),
            user_name=config["configurable"].get("session_id"),
            agent_id="test_chatbot",
            agent_name="Test ChatBot",
            session_date=datetime.now().isoformat(),
        )
