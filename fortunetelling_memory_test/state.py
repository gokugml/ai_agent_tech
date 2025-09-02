"""
State 类型定义

定义了 LangGraph 使用的状态结构，保持最简洁的设计
"""

from collections.abc import Sequence
from typing import Annotated, Any, Literal
from typing_extensions import TypedDict

from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages


class MemoryTestState(TypedDict):
    """记忆测试状态类型

    设计原则：
    1. 保持最简洁的结构
    2. 完全依赖 messages 提取对话数据
    3. 支持动态记忆框架选择
    """

    # 会话标识（用户手动输入）
    session_id: str

    # 记忆框架选择
    memory_framework: Literal["memu", "memobase"]

    # 历史对话（LangGraph 标准格式）
    messages: Annotated[Sequence[AnyMessage], add_messages]

    # 用户档案信息（生辰八字、命理结果等）
    user_profile: dict[str, Any]


def create_initial_state(
    session_id: str, memory_framework: Literal["memu", "memobase"], user_profile: dict[str, Any]
) -> MemoryTestState:
    """创建初始状态

    Args:
        session_id: 用户会话ID
        memory_framework: 记忆框架类型
        user_profile: 用户档案信息

    Returns:
        初始化的状态对象
    """
    return MemoryTestState(
        session_id=session_id, memory_framework=memory_framework, messages=[], user_profile=user_profile
    )


def get_user_profile_summary(user_profile: dict[str, Any]) -> str:
    """获取用户档案摘要

    用于在提示中简洁地描述用户信息

    Args:
        user_profile: 用户档案字典

    Returns:
        用户信息摘要字符串
    """
    summary_parts = []

    # 生辰八字信息
    if "birth_info" in user_profile:
        birth_info = user_profile["birth_info"]
        if "date" in birth_info:
            summary_parts.append(f"出生日期：{birth_info['date']}")
        if "time" in birth_info:
            summary_parts.append(f"出生时间：{birth_info['time']}")
        if "location" in birth_info:
            summary_parts.append(f"出生地点：{birth_info['location']}")

    # 基本信息
    if "gender" in user_profile:
        summary_parts.append(f"性别：{user_profile['gender']}")

    if "age" in user_profile:
        summary_parts.append(f"年龄：{user_profile['age']}")

    # 关注问题
    if "concerns" in user_profile:
        concerns = user_profile["concerns"]
        if isinstance(concerns, list):
            summary_parts.append(f"关注领域：{', '.join(concerns)}")
        else:
            summary_parts.append(f"关注领域：{concerns}")

    # 命理结果（如果有预设）
    if "fortune_analysis" in user_profile:
        analysis = user_profile["fortune_analysis"]
        if "five_elements" in analysis:
            summary_parts.append(f"五行：{analysis['five_elements']}")
        if "zodiac" in analysis:
            summary_parts.append(f"生肖：{analysis['zodiac']}")

    return "\\n".join(summary_parts) if summary_parts else "暂无详细信息"
