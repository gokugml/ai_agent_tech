"""AI对话代理节点"""

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage

from config import settings
from test_chatbot_memu.state import ChatbotState
from test_chatbot_memu.tools.memory_tools import (
    retrieve_default_categories_tool,
    retrieve_related_clustered_categories_tool,
    retrieve_related_memory_items_tool,
)


def ai_agent_node(state: ChatbotState) -> ChatbotState:
    """AI对话代理节点
    
    处理用户消息，可调用记忆工具获取相关记忆，生成AI回复
    """
    # 初始化Claude模型
    llm = ChatAnthropic(
        model="claude-3-5-sonnet-20241022",
        api_key=settings.ANTHROPIC_API_KEY,
        temperature=0.7,
    )
    
    # 绑定记忆工具
    llm_with_tools = llm.bind_tools([
        retrieve_default_categories_tool,
        retrieve_related_clustered_categories_tool,
        retrieve_related_memory_items_tool,
    ])
    
    # 构建系统提示
    system_prompt = """你是一个智能聊天助手。你可以通过以下工具获取用户的历史记忆：

1. retrieve_default_categories_tool: 获取用户的基本档案和默认分类记忆
2. retrieve_related_clustered_categories_tool: 根据话题获取相关聚类分类记忆
3. retrieve_related_memory_items_tool: 根据查询获取具体的相关记忆项

请根据用户的问题智能决定是否需要调用这些工具来获取相关记忆，然后基于记忆内容和用户问题提供有用的回复。

使用记忆工具时的参数说明：
- user_id: 使用session_id作为用户ID
- agent_id: 使用固定值"chatbot_memu"
- query/category_query: 根据用户问题提取关键词

请用简洁友好的语调与用户对话。"""
    
    # 获取当前会话的消息历史
    messages = [SystemMessage(content=system_prompt)] + list(state["messages"])
    
    # 调用AI模型生成回复
    response = llm_with_tools.invoke(messages)
    
    # 返回更新后的状态
    return {"messages": [response]}