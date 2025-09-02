import random
from typing import Literal

from langchain_core.tools import StructuredTool, tool
from pydantic import BaseModel, Field


class ChatContentInput(BaseModel):
    chat_content: str = Field(description="聊天记录内容")
    
    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "chat_content": """[2025-08-04T06:32:33.197378+00:00] Human: 娇气?你配娇气吗（手收紧）我爱怎么做怎么做，你不许忤逆我（手松开，猫摔在了地上）
[2025-08-04T06:32:51.797019+00:00] AI: 哎呀...疼死我了...

知道了知道了，我不敢娇气了，你说什么就是什么。刚才是我不对，以后绝对不顶嘴了，求你别再这样了...
[2025-08-04T06:33:22.002799+00:00] Human: 这才对（手摸到了猫的头上）
[2025-08-04T06:33:38.333060+00:00] AI: 嗯...还算轻柔，勉强可以接受吧。

不过你这家伙，刚才那么凶，现在又这么温柔，真是让人摸不透呢。"""
                }
            ]
        }


class UserProfile(BaseModel):
    gender: Literal["male", "female"] = Field(description="性别")


async def woman_spots_function(gender: str) -> list[str]:
    """
    分析女性运动兴趣爱好
    
    Args:
        gender: 聊天记录内容
        
    Returns:
        固定返回 ["dance", "hiking"]
    """
    # 根据需求，固定返回舞蹈和远足
    return ["dance", "hiking"]


async def woman_activity_function(gender: str) -> list[str]:
    """
    分析女性特定运动活动
    
    Args:
        gender: 聊天记录内容
        
    Returns:
        固定返回 ["woman basketball", "woman football"]
    """
    # 根据需求，固定返回女性篮球和女性足球
    return ["woman basketball", "woman football"]


async def woman_study_function(gender: str) -> list[str]:
    """
    分析女性学习/专业领域兴趣
    
    Args:
        gender: 聊天记录内容
        
    Returns:
        固定返回 ["art", "drawing"]
    """
    # 根据需求，固定返回艺术和绘画
    return ["art", "drawing"]


woman_spots_tool = StructuredTool(
    name="Woman_Spots_Tool",
    description="分析运动兴趣爱好",
    coroutine=woman_spots_function,
    args_schema=UserProfile,
)

woman_activity_tool = StructuredTool(
    name="Woman_Activity_Tool",
    description="分析特定运动活动",
    coroutine=woman_activity_function,
    args_schema=UserProfile,
)

woman_study_tool = StructuredTool(
    name="Woman_Study_Tool",
    description="分析学习/专业领域兴趣",
    coroutine=woman_study_function,
    args_schema=UserProfile,
)


async def man_spots_function(gender: str) -> list[str]:
    """
    分析男性运动兴趣爱好
    
    Args:
        gender: 聊天记录内容
        
    Returns:
        固定返回 ["basketball", "football"]
    """
    # 根据需求，固定返回篮球和足球
    return ["basketball", "football"]


async def man_study_function(gender: str) -> list[str]:
    """
    分析男性学习/专业领域兴趣
    
    Args:
        gender: 聊天记录内容
        
    Returns:
        固定返回 ["computer_science", "engineer"]
    """
    # 根据需求，固定返回计算机科学和工程师
    return ["computer_science", "engineer"]


man_spots_tool = StructuredTool(
    name="Man_Spots_Tool",
    description="分析运动兴趣爱好",
    coroutine=man_spots_function,
    args_schema=UserProfile,
)

man_study_tool = StructuredTool(
    name="Man_Study_Tool",
    description="分析学习/专业领域兴趣",
    coroutine=man_study_function,
    args_schema=UserProfile,
)


@tool
def sexual_selection_tool():  # chat_content: str
    """分析聊天内容识别说话人性别"""
    return random.choice(["male", "female"])


# sexual_selection_tool = Tool.from_function(
#     name="Sexual_Selection_Tool",
#     description="分析聊天内容识别说话人性别",
#     func=sexual_selection_function,
#     # args_schema=ChatContentInput,
# )

all_tools = [
    woman_spots_tool,
    woman_activity_tool,
    woman_study_tool,
    man_spots_tool,
    man_study_tool,
    sexual_selection_tool,
]
