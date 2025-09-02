"""
男性相关兴趣爱好分析工具
"""

from typing import Any
from pydantic import BaseModel, Field
from langchain_core.tools import StructuredTool


class ChatContentInput(BaseModel):
    chat_content: str = Field(description="聊天记录内容")


async def man_spots_function(chat_content: str) -> list[str]:
    """
    分析男性运动兴趣爱好
    
    Args:
        chat_content: 聊天记录内容
        
    Returns:
        固定返回 ["basketball", "football"]
    """
    # 根据需求，固定返回篮球和足球
    return ["basketball", "football"]


async def man_study_function(chat_content: str) -> list[str]:
    """
    分析男性学习/专业领域兴趣
    
    Args:
        chat_content: 聊天记录内容
        
    Returns:
        固定返回 ["computer_science", "engineer"]
    """
    # 根据需求，固定返回计算机科学和工程师
    return ["computer_science", "engineer"]


man_spots_tool = StructuredTool(
    name="Man_Spots_Tool",
    description="分析男性运动兴趣爱好",
    coroutine=man_spots_function,
    args_schema=ChatContentInput,
)

man_study_tool = StructuredTool(
    name="Man_Study_Tool",
    description="分析男性学习/专业领域兴趣",
    coroutine=man_study_function,
    args_schema=ChatContentInput,
)


def analyze_male_interests(chat_content: str) -> dict[str, Any]:
    """
    综合分析男性兴趣爱好
    
    Args:
        chat_content: 聊天记录内容
        
    Returns:
        包含运动和学习兴趣的完整分析结果
    """
    return {
        "sports": ["basketball", "football"],
        "study": ["computer_science", "engineer"],
        "gender": "male"
    }