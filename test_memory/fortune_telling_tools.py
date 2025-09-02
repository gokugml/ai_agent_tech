"""
算命场景专用MemoBase记忆检索工具集

基于评测数据分析，为不同算命子场景设计专用的LangChain工具
模仿memobase_memory.py的实现方式，使用StructuredTool
"""

from typing import Optional, Literal
from pydantic import BaseModel, Field
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import StructuredTool
from memobase import MemoBaseClient

# MemoBase客户端配置
client = MemoBaseClient(
    project_url="https://api.memobase.dev",
    api_key="sk-proj-c20d8e576c03e093-51ccbf00c41cf79b6c5b7eada48c7852",
)


# ================================
# 工具函数实现
# ================================

def recall_fortune_basic_info(info_type: str, query_text: str, config: RunnableConfig):
    """算命基础信息检索 - Profile专用
    
    适用场景：查询出生时间、生肖、星座等固定个人信息
    评测得分：5.83/10 - 在算命场景下表现稳定
    """
    if config.get("configurable"):
        user = client.get_or_create_user(user_id=config["configurable"].get("session_id"))
        
        # 映射信息类型到Profile主题
        topic_mapping = {
            "birth_date": "basic_info",
            "birth_time": "basic_info", 
            "birth_place": "basic_info",
            "name": "basic_info",
            "gender": "basic_info",
            "family_background": "family"
        }
        
        topic = topic_mapping.get(info_type, "basic_info")
        response = user.profile(query=query_text, topic=topic, need_json=True)
        
        if not response:
            return f"未找到关于{info_type}的相关信息"
        
        return response
    
    raise RuntimeError("notfound configurable")


def recall_fortune_events(event_type: str, query_text: str, time_range: Optional[str], config: RunnableConfig):
    """算命事件时间线检索 - Search Event专用
    
    适用场景：追踪算命咨询历史、预测结果变化、仪式过程
    评测得分：8.33/10 - 在算命场景下表现优异
    """
    if config.get("configurable"):
        user = client.get_or_create_user(user_id=config["configurable"].get("session_id"))
        
        # 构建检索查询，包含时间范围
        search_query = query_text
        if time_range:
            search_query = f"{query_text} {time_range}"
        
        event_results = user.search_event(query=search_query)
        
        if not event_results:
            return f"未找到关于{event_type}的相关事件记录"
        
        # 格式化返回结果
        formatted_result = []
        for event in event_results:
            formatted_result.append({
                "event_id": str(getattr(event, 'id', 'unknown')),
                "created_at": str(getattr(event, 'created_at', 'unknown')),
                "event_type": event_type,
                "content": str(getattr(event, 'event_data', event)),
                "similarity": getattr(event, 'similarity', 'N/A')
            })
        
        return {
            "event_type": event_type,
            "time_range": time_range,
            "total_events": len(formatted_result),
            "events": formatted_result
        }
    
    raise RuntimeError("notfound configurable")


def recall_fortune_facts(fact_type: str, query_text: str, precise_match: bool, config: RunnableConfig):
    """算命关键事实检索 - Search Event Gist专用
    
    适用场景：精确提取算命结论、幸运元素、禁忌事项
    评测得分：5.67/10 - 适合精确事实查询
    """
    if config.get("configurable"):
        user = client.get_or_create_user(user_id=config["configurable"].get("session_id"))
        
        gist_results = user.search_event_gist(query=query_text)
        
        if not gist_results:
            return f"未找到关于{fact_type}的精确事实信息"
        
        # 格式化返回结果，突出精确性
        formatted_result = []
        for gist in gist_results:
            formatted_result.append({
                "fact_id": str(getattr(gist, 'id', 'unknown')),
                "fact_type": fact_type,
                "content": str(getattr(gist, 'gist_data', gist)),
                "confidence": getattr(gist, 'confidence', 'N/A'),
                "similarity": getattr(gist, 'similarity', 'N/A')
            })
        
        return {
            "fact_type": fact_type,
            "precise_match": precise_match,
            "total_facts": len(formatted_result),
            "facts": formatted_result
        }
    
    raise RuntimeError("notfound configurable")


def recall_fortune_decisions(decision_category: str, current_situation: str, query_text: str, config: RunnableConfig):
    """算命人生决策综合检索 - Context专用
    
    适用场景：复杂的人生决策咨询，需要综合多维度信息
    评测得分：3.33/10 - 通用性检索，在算命场景相对较弱但覆盖面广
    """
    if config.get("configurable"):
        user = client.get_or_create_user(user_id=config["configurable"].get("session_id"))
        
        # 构建包含决策背景的复合查询
        comprehensive_query = f"{query_text} 当前情况: {current_situation} 决策类型: {decision_category}"
        
        context_result = user.context(query=comprehensive_query)
        
        if not context_result:
            return f"未找到关于{decision_category}决策的相关综合信息"
        
        return {
            "decision_category": decision_category,
            "current_situation": current_situation,
            "comprehensive_memory": context_result
        }
    
    raise RuntimeError("notfound configurable")


# ================================
# Pydantic 输入模型定义
# ================================

class FortuneBasicInfoInput(BaseModel):
    """基础个人信息查询输入模型"""
    info_type: Literal["birth_date", "birth_time", "birth_place", "name", "gender", "family_background"] = Field(
        description="查询的个人信息类型：出生日期、出生时间、出生地点、姓名、性别、家庭背景"
    )
    query_text: str = Field(
        description="具体查询内容，如'我的出生时间是什么'、'我的生肖是什么'"
    )
    
    class Config:
        json_schema_extra = {
            "examples": [
                {"info_type": "birth_date", "query_text": "我的出生时间是什么？"},
                {"info_type": "birth_time", "query_text": "我算运势时提供的出生时间"},
                {"info_type": "gender", "query_text": "我的性别信息"}
            ]
        }


class FortuneEventInput(BaseModel):
    """算命事件查询输入模型"""
    event_type: Literal["fortune_consultation", "prediction_result", "ritual_ceremony", "advice_received"] = Field(
        description="算命事件类型：算命咨询、预测结果、仪式仪轨、建议指导"
    )
    query_text: str = Field(
        description="事件查询内容，如'我上次算命的结果是什么'、'之前给我的建议有哪些'"
    )
    time_range: Optional[str] = Field(
        default=None,
        description="时间范围限制，如'上个月'、'去年'、'最近一次'"
    )
    
    class Config:
        json_schema_extra = {
            "examples": [
                {"event_type": "fortune_consultation", "query_text": "我上次算命是什么时候？", "time_range": "最近一次"},
                {"event_type": "prediction_result", "query_text": "之前的预测结果如何", "time_range": "上个月"},
                {"event_type": "advice_received", "query_text": "算命师给过什么建议"}
            ]
        }


class FortuneFactInput(BaseModel):
    """算命关键事实查询输入模型"""
    fact_type: Literal["prediction_outcome", "lucky_elements", "taboo_items", "life_guidance", "career_advice"] = Field(
        description="事实类型：预测结果、幸运元素、禁忌事项、人生指导、事业建议"
    )
    query_text: str = Field(
        description="精确事实查询，如'我的幸运数字是什么'、'我需要避免什么'"
    )
    precise_match: bool = Field(
        default=True,
        description="是否需要精确匹配，True表示查找确定的事实，False表示相关性匹配"
    )
    
    class Config:
        json_schema_extra = {
            "examples": [
                {"fact_type": "lucky_elements", "query_text": "我的幸运颜色是什么", "precise_match": True},
                {"fact_type": "prediction_outcome", "query_text": "算命师的具体预测结果", "precise_match": True},
                {"fact_type": "taboo_items", "query_text": "我需要避免什么", "precise_match": False}
            ]
        }


class FortuneDecisionInput(BaseModel):
    """人生决策查询输入模型"""
    decision_category: Literal["career", "relationship", "health", "finance", "family", "education"] = Field(
        description="决策类别：事业、感情、健康、财运、家庭、教育"
    )
    current_situation: str = Field(
        description="当前面临的具体情况描述"
    )
    query_text: str = Field(
        description="决策相关的查询内容"
    )
    
    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "decision_category": "career", 
                    "current_situation": "面临跨部门项目选择",
                    "query_text": "我应该接受这个新项目吗？"
                },
                {
                    "decision_category": "relationship",
                    "current_situation": "考虑结婚",
                    "query_text": "现在是结婚的好时机吗？"
                }
            ]
        }


# ================================
# StructuredTool 工具定义
# ================================

fortune_basic_info_tool = StructuredTool(
    name="Fortune_Basic_Info_Retrieval",
    description="""检索算命相关的基础个人信息，如出生时间、生肖、星座、姓名等固定个人资料。
    
适合查询：我的出生时间、我的生肖是什么、我的星座、我的八字信息等。
评测得分：5.83/10 - 在算命场景下表现稳定""",
    args_schema=FortuneBasicInfoInput,
    func=recall_fortune_basic_info,
)

fortune_event_timeline_tool = StructuredTool(
    name="Fortune_Event_Timeline_Retrieval", 
    description="""检索算命相关的事件时间线，包括历次算命咨询、预测结果、建议指导的时间顺序记录。
    
适合查询：我上次算命是什么时候、之前的预测结果如何、算命师给过什么建议等。
评测得分：8.33/10 - 在算命场景下表现优异""",
    args_schema=FortuneEventInput,
    func=recall_fortune_events,
)

fortune_key_fact_tool = StructuredTool(
    name="Fortune_Key_Fact_Retrieval",
    description="""检索算命相关的精确事实和关键信息，如预测结论、幸运数字、禁忌事项、人生建议等。
    
适合查询：我的幸运颜色是什么、需要避免什么、算命师的具体预测结果等。
评测得分：5.67/10 - 适合精确事实查询""",
    args_schema=FortuneFactInput,
    func=recall_fortune_facts,
)

fortune_life_decision_tool = StructuredTool(
    name="Fortune_Life_Decision_Retrieval",
    description="""综合检索与人生重大决策相关的记忆信息，包括个人资料、历史事件、算命建议等多维度信息。
    
适合查询：事业选择建议、感情决策参考、重大人生转折点的指导等复杂问题。
评测得分：3.33/10 - 通用性检索，覆盖面广""",
    args_schema=FortuneDecisionInput,
    func=recall_fortune_decisions,
)

# 工具集合导出
fortune_memory_tools = [
    fortune_basic_info_tool,
    fortune_event_timeline_tool,
    fortune_key_fact_tool,
    fortune_life_decision_tool
]


# ================================
# 使用示例
# ================================

if __name__ == "__main__":
    print("算命场景MemoBase记忆检索工具集合已定义完成！")
    print("\n工具列表：")
    print("1. Fortune_Basic_Info_Retrieval - 基础个人信息检索（Profile专用，得分5.83）")
    print("2. Fortune_Event_Timeline_Retrieval - 事件时间线检索（Search Event专用，得分8.33）") 
    print("3. Fortune_Key_Fact_Retrieval - 关键事实检索（Search Event Gist专用，得分5.67）")
    print("4. Fortune_Life_Decision_Retrieval - 综合决策检索（Context专用，得分3.33）")
    print("\n所有工具都使用StructuredTool实现，兼容LangChain框架")
    print("基于真实评测数据设计，推荐优先使用得分较高的工具")