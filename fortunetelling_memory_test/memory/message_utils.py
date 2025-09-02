"""
消息提取工具

从 LangGraph messages 中提取最新对话对的工具函数
"""

from collections.abc import Sequence

from langchain_core.messages import AIMessage, AnyMessage, HumanMessage, filter_messages
from loguru import logger


def extract_latest_conversation(messages: Sequence[AnyMessage]) -> tuple[str, str]:
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
    return last_human, last_ai


def get_latest_user_input(messages: Sequence[AnyMessage]) -> str:
    """获取最新的用户输入

    Args:
        messages: LangGraph 消息序列

    Returns:
        最新的用户输入内容，如果没有则返回空字符串
    """
    if not messages:
        return ""

    # 使用 filter_messages 获取所有用户消息，取最后一条
    human_messages = filter_messages(messages, include_types=[HumanMessage])
    return human_messages[-1].content if human_messages else ""


def get_conversation_history(messages: Sequence[AnyMessage], limit: int = 10) -> list[dict[str, str]]:
    """获取对话历史

    提取最近的对话历史，用于记忆检索时的上下文。

    Args:
        messages: LangGraph 消息序列
        limit: 最多返回的对话轮数

    Returns:
        对话历史列表，格式为 [{"user": "...", "assistant": "..."}, ...]
    """
    if not messages:
        return []

    conversation_pairs = []
    current_user = None

    for msg in messages:
        if isinstance(msg, HumanMessage):
            # 如果有未配对的用户消息，先保存
            if current_user:
                conversation_pairs.append(
                    {
                        "user": current_user,
                        "assistant": "",  # 没有对应的AI回复
                    }
                )
            current_user = msg.content

        elif isinstance(msg, AIMessage) and current_user:
            # 确保不是工具调用结果
            if msg.content and not msg.tool_calls:
                conversation_pairs.append({"user": current_user, "assistant": msg.content})
                current_user = None  # 清空，准备下一对

    # 如果最后还有未配对的用户消息
    if current_user:
        conversation_pairs.append({"user": current_user, "assistant": ""})

    # 返回最近的对话
    return conversation_pairs[-limit:] if conversation_pairs else []


def count_conversation_turns(messages: Sequence[AnyMessage]) -> int:
    """统计对话轮数

    Args:
        messages: LangGraph 消息序列

    Returns:
        完整的对话轮数（一问一答为一轮）
    """
    if not messages:
        return 0

    user_count = sum(1 for msg in messages if isinstance(msg, HumanMessage))
    ai_count = sum(1 for msg in messages if isinstance(msg, AIMessage) and msg.content and not msg.tool_calls)

    # 取较小值作为完整轮数
    return min(user_count, ai_count)


def has_complete_conversation(messages: Sequence[AnyMessage]) -> bool:
    """检查是否有完整的对话

    Args:
        messages: LangGraph 消息序列

    Returns:
        是否存在至少一轮完整的对话（用户输入+AI回复）
    """
    user_input, ai_response = extract_latest_conversation(messages)
    return bool(user_input and ai_response)


def format_conversation_for_memory(user_input: str, ai_response: str) -> dict[str, str]:
    """格式化对话用于记忆存储

    Args:
        user_input: 用户输入
        ai_response: AI回复

    Returns:
        格式化的对话字典
    """
    return {"user": user_input, "assistant": ai_response, "timestamp": str(int(__import__("time").time()))}
