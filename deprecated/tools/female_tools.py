"""
女性相关兴趣爱好分析工具
"""

from typing import Any
from pydantic import BaseModel, Field
from langchain_core.tools import StructuredTool


class ChatContentInput(BaseModel):
    chat_content: str = Field(description="聊天记录内容")


async def woman_spots_function(chat_content: str) -> list[str]:
    """
    分析女性运动兴趣爱好
    
    Args:
        chat_content: 聊天记录内容
        
    Returns:
        固定返回 ["dance", "hiking"]
    """
    # 根据需求，固定返回舞蹈和远足
    return ["dance", "hiking"]


async def woman_activity_function(chat_content: str) -> list[str]:
    """
    分析女性特定运动活动
    
    Args:
        chat_content: 聊天记录内容
        
    Returns:
        固定返回 ["woman basketball", "woman football"]
    """
    # 根据需求，固定返回女性篮球和女性足球
    return ["woman basketball", "woman football"]


async def woman_study_function(chat_content: str) -> list[str]:
    """
    分析女性学习/专业领域兴趣
    
    Args:
        chat_content: 聊天记录内容
        
    Returns:
        固定返回 ["art", "drawing"]
    """
    # 根据需求，固定返回艺术和绘画
    return ["art", "drawing"]


woman_spots_tool = StructuredTool(
    name="Woman_Spots_Tool",
    description="分析女性运动兴趣爱好",
    coroutine=woman_spots_function,
    args_schema=ChatContentInput,
)

woman_activity_tool = StructuredTool(
    name="Woman_Activity_Tool",
    description="分析女性特定运动活动",
    coroutine=woman_activity_function,
    args_schema=ChatContentInput,
)

woman_study_tool = StructuredTool(
    name="Woman_Study_Tool",
    description="分析女性学习/专业领域兴趣",
    coroutine=woman_study_function,
    args_schema=ChatContentInput,
)


def analyze_female_interests(chat_content: str) -> dict[str, Any]:
    """
    综合分析女性兴趣爱好
    
    Args:
        chat_content: 聊天记录内容
        
    Returns:
        包含运动、活动和学习兴趣的完整分析结果
    """
    return {
        "sports": ["dance", "hiking"],
        "activities": ["woman basketball", "woman football"],
        "study": ["art", "drawing"],
        "gender": "female"
    }