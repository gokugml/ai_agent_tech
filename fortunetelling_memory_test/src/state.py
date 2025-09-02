from collections.abc import Sequence
from typing import Annotated, Any, TypedDict

from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages


class State(TypedDict):
    messages: Annotated[Sequence[AnyMessage], add_messages]
    profile: dict[str, Any]
    retrieved_profile: Any


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
