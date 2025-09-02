"""最小化聊天机器人主图定义"""

from langgraph.graph import StateGraph, START, END

from test_chatbot_memu.state import ChatbotState
from test_chatbot_memu.nodes.ai_agent import ai_agent_node
from test_chatbot_memu.nodes.memory_store import memory_store_node


def should_store_memory(state: ChatbotState) -> bool:
    """判断是否需要存储记忆
    
    只有当消息数量大于等于2时才存储记忆
    """
    return len(state["messages"]) >= 2


# 创建StateGraph
graph_builder = StateGraph(ChatbotState)

# 添加节点
graph_builder.add_node("ai_agent", ai_agent_node)
graph_builder.add_node("memory_store", memory_store_node)

# 添加边
graph_builder.add_edge(START, "ai_agent")
graph_builder.add_conditional_edges(
    "ai_agent",
    should_store_memory,
    {
        True: "memory_store",
        False: END,
    }
)
graph_builder.add_edge("memory_store", END)

# 编译图
graph = graph_builder.compile()