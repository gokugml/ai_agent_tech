"""
Fortune Telling Memory Test - Main Graph

LangGraph 主图定义，整合 AI 对话代理和记忆存储功能
"""

from typing import Any, Literal

from langchain_core.messages import HumanMessage
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from loguru import logger
from nodes.ai_agent import ai_agent_node
from nodes.memory_store import memory_store_node, should_store_memory
from state import MemoryTestState, create_initial_state
from tools.memory_tools import MEMORY_TOOLS


def create_fortune_telling_graph() -> StateGraph:
    """创建算命师 LangGraph

    节点流程:
    START -> AI对话代理 -> 记忆存储 -> END

    Returns:
        配置好的 LangGraph
    """

    # 创建状态图
    workflow = StateGraph(MemoryTestState)

    # 添加节点
    workflow.add_node("ai_agent", ai_agent_node)
    workflow.add_node("memory_tools", ToolNode(MEMORY_TOOLS, name="memory_tools"))
    workflow.add_node("memory_store", memory_store_node)

    # 设置入口点
    workflow.set_entry_point("ai_agent")
    
    workflow.add_conditional_edges("ai_agent", tools_condition, {"tools": "memory_tools", END: "memory_store"})
    workflow.add_edge("memory_tools", "ai_agent")

    # 添加条件边：AI代理 -> 记忆存储（如果有完整对话）
    # workflow.add_conditional_edges("ai_agent", should_store_memory, {True: "memory_store", False: END})

    # 记忆存储 -> 结束
    workflow.add_edge("memory_store", END)

    # 编译图
    return workflow.compile()


# 创建全局图实例
graph = create_fortune_telling_graph()


def format_user_input(user_message: str) -> HumanMessage:
    """格式化用户输入为 LangGraph 消息

    Args:
        user_message: 用户输入文本

    Returns:
        格式化的人类消息
    """
    return HumanMessage(content=user_message.strip())


async def run_fortune_telling_session(
    session_id: str,
    memory_framework: Literal["memu", "memobase"],
    user_profile: dict[str, Any],
    user_messages: list[str],
) -> dict[str, Any]:
    """运行完整的算命咨询会话

    这是一个便民函数，用于测试完整的对话流程。
    在实际使用中，LangGraph Studio 会管理会话状态。

    Args:
        session_id: 会话ID
        memory_framework: 记忆框架类型
        user_profile: 用户档案信息
        user_messages: 用户消息列表

    Returns:
        会话结果字典
    """
    try:
        logger.info(f"开始算命咨询会话: {session_id}")

        # 创建初始状态
        initial_state = create_initial_state(
            session_id=session_id, memory_framework=memory_framework, user_profile=user_profile
        )

        # 运行对话
        current_state = initial_state
        conversation_results = []

        for i, user_message in enumerate(user_messages):
            logger.info(f"处理第 {i + 1} 轮对话")

            # 添加用户消息到状态
            user_msg = format_user_input(user_message)
            current_state["messages"] = current_state["messages"] + [user_msg]

            # 运行图
            result = await graph.ainvoke(current_state)

            # 更新状态
            current_state = result

            # 记录对话结果
            ai_response = None
            if result["messages"]:
                for msg in reversed(result["messages"]):
                    if hasattr(msg, "content") and msg.content:
                        ai_response = msg.content
                        break

            conversation_results.append(
                {
                    "turn": i + 1,
                    "user_input": user_message,
                    "ai_response": ai_response,
                    "message_count": len(result["messages"]),
                }
            )

        # 返回会话摘要
        return {
            "session_id": session_id,
            "memory_framework": memory_framework,
            "total_turns": len(user_messages),
            "final_state": current_state,
            "conversation_results": conversation_results,
            "success": True,
        }

    except Exception as e:
        logger.error(f"算命咨询会话失败: {e}")
        return {"session_id": session_id, "error": str(e), "success": False}


def create_sample_user_profile() -> dict[str, Any]:
    """创建示例用户档案

    Returns:
        示例用户档案
    """
    return {
        "birth_info": {"date": "1990-05-15", "time": "14:30", "location": "北京"},
        "gender": "女",
        "age": 33,
        "concerns": ["事业发展", "感情关系"],
        "fortune_analysis": {"five_elements": "水木相生", "zodiac": "马", "basic_fortune": "命格较好，有贵人相助"},
    }


async def demo_conversation():
    """演示对话流程

    这个函数可以用来测试整个系统是否正常工作。
    """
    print("🔮 算命师记忆测试演示")
    print("=" * 50)

    # 创建示例数据
    session_id = "demo_session_001"
    memory_framework = "memu"
    user_profile = create_sample_user_profile()

    user_messages = [
        "你好，我想了解一下我的运势",
        "我最近在考虑换工作，这个决定合适吗？",
        "你之前提到我有贵人相助，能具体说说吗？",
    ]

    print(f"会话ID: {session_id}")
    print(f"记忆框架: {memory_framework}")
    print(f"用户档案: {user_profile['birth_info']}")
    print(f"消息数量: {len(user_messages)}")
    print()

    try:
        # 运行会话
        result = await run_fortune_telling_session(
            session_id=session_id,
            memory_framework=memory_framework,
            user_profile=user_profile,
            user_messages=user_messages,
        )

        if result["success"]:
            print("✅ 会话成功完成")
            for conversation in result["conversation_results"]:
                print(f"\\n--- 第 {conversation['turn']} 轮 ---")
                print(f"👤 用户: {conversation['user_input']}")
                print(f"🔮 算命师: {conversation['ai_response'][:100]}...")
        else:
            print(f"❌ 会话失败: {result['error']}")

    except Exception as e:
        print(f"❌ 演示失败: {e}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(demo_conversation())
