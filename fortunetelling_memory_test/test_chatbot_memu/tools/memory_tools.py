"""MemU记忆召回工具"""

from langchain_core.tools import tool

from config import settings
from memu import MemuClient

# MemU客户端配置
memu_client = MemuClient(
    base_url="https://api.memu.so", 
    api_key=settings.MEMU_API_KEY,
)


@tool
def retrieve_default_categories_tool(user_id: str, agent_id: str) -> str:
    """获取用户的默认分类记忆
    
    Args:
        user_id: 用户ID
        agent_id: 代理ID
    
    Returns:
        默认分类记忆的文本内容
    """
    try:
        resp = memu_client.retrieve_default_categories(
            user_id=user_id, 
            agent_id=agent_id
        )
        
        if not resp.default_categories:
            return "暂无默认分类记忆"
        
        memories = []
        for category in resp.default_categories:
            memories.append(f"分类: {category.category}")
            memories.append(f"内容: {category.content}")
            memories.append("---")
        
        return "\n".join(memories)
    except Exception as e:
        return f"获取默认分类记忆失败: {str(e)}"


@tool
def retrieve_related_clustered_categories_tool(
    user_id: str, 
    agent_id: str, 
    category_query: str
) -> str:
    """根据查询获取相关的聚类分类记忆
    
    Args:
        user_id: 用户ID
        agent_id: 代理ID
        category_query: 分类查询内容
    
    Returns:
        相关聚类分类记忆的文本内容
    """
    try:
        resp = memu_client.retrieve_related_clustered_categories(
            user_id=user_id,
            agent_id=agent_id,
            category_query=category_query
        )
        
        if not resp.clustered_categories:
            return f"未找到与'{category_query}'相关的聚类分类记忆"
        
        memories = []
        for clustered in resp.clustered_categories:
            memories.append(f"摘要: {clustered.summary}")
            memories.append(f"相似度分数: {clustered.similarity_score}")
            if clustered.memories:
                memories.append("记忆内容:")
                for memory in clustered.memories:
                    memories.append(f"  - {memory}")
            memories.append("---")
        
        return "\n".join(memories)
    except Exception as e:
        return f"获取聚类分类记忆失败: {str(e)}"


@tool
def retrieve_related_memory_items_tool(
    user_id: str, 
    agent_id: str, 
    query: str
) -> str:
    """根据查询获取相关的记忆项
    
    Args:
        user_id: 用户ID
        agent_id: 代理ID
        query: 查询内容
    
    Returns:
        相关记忆项的文本内容
    """
    try:
        resp = memu_client.retrieve_related_memory_items(
            user_id=user_id,
            agent_id=agent_id,
            query=query
        )

        if not resp.related_memories:
            return f"未找到与'{query}'相关的记忆"

        memories = []
        for related_memory in resp.related_memories:
            memory = related_memory.memory
            memories.append(f"分类: {memory.category}")
            memories.append(f"内容: {memory.content}")
            memories.append(f"相似度分数: {related_memory.similarity_score}")
            if memory.happened_at:
                memories.append(f"发生时间: {memory.happened_at}")
            memories.append("---")
        
        return "\n".join(memories)
    except Exception as e:
        return f"获取相关记忆失败: {str(e)}"