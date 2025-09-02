"""
性别识别工具
"""

import re
from typing import Any
from pydantic import BaseModel, Field
from langchain_core.tools import StructuredTool


class SexualSelectionInput(BaseModel):
    chat_content: str = Field(description="聊天记录内容")


async def sexual_selection_function(chat_content: str) -> dict[str, Any]:
    """
    分析聊天内容识别说话人性别
    
    Args:
        chat_content: 聊天记录内容
        
    Returns:
        Dict containing gender identification result
    """
    
    # 男性特征关键词
    male_keywords = [
        '兄弟', '哥们', '老铁', '大哥', '小伙子', 
        '篮球', '足球', '游戏', '编程', '工程师',
        '哥', '爷', '老爷们', '男人', '小伙'
    ]
    
    # 女性特征关键词  
    female_keywords = [
        '姐妹', '闺蜜', '小姐姐', '美女', '女神',
        '化妆', '购物', '舞蹈', '瑜伽', '艺术',
        '姐', '小仙女', '女人', '妹子', '女孩'
    ]
    
    # 计算关键词匹配得分
    male_score = 0
    female_score = 0
    
    content_lower = chat_content.lower()
    
    for keyword in male_keywords:
        if keyword in content_lower:
            male_score += 1
            
    for keyword in female_keywords:
        if keyword in content_lower:
            female_score += 1
    
    # 基于得分判断性别
    if male_score > female_score:
        gender = "male"
        confidence = male_score / (male_score + female_score + 1)
    elif female_score > male_score:
        gender = "female" 
        confidence = female_score / (male_score + female_score + 1)
    else:
        # 默认返回male，但置信度较低
        gender = "male"
        confidence = 0.3
    
    return {
        "gender": gender,
        "confidence": confidence,
        "male_score": male_score,
        "female_score": female_score
    }


sexual_selection_tool = StructuredTool(
    name="Sexual_Selection_Tool",
    description="分析聊天内容识别说话人性别",
    coroutine=sexual_selection_function,
    args_schema=SexualSelectionInput,
)