"""
记忆存储节点

在对话结束后自动将最新的对话存储到相应的记忆框架
"""

from typing import Any

from loguru import logger
from memory.memobase_adapter import MemobaseMemoryAdapter
from memory.memu_adapter import MemuMemoryAdapter
from memory.message_utils import extract_latest_conversation, has_complete_conversation
from state import MemoryTestState

# 全局适配器实例（重用实例以保持状态）
_memu_adapter = None
_memobase_adapter = None


def get_memory_adapter(framework_type: str):
    """获取记忆适配器实例"""
    global _memu_adapter, _memobase_adapter

    if framework_type == "memu":
        if _memu_adapter is None:
            _memu_adapter = MemuMemoryAdapter()
        return _memu_adapter
    elif framework_type == "memobase":
        if _memobase_adapter is None:
            _memobase_adapter = MemobaseMemoryAdapter()
        return _memobase_adapter
    else:
        raise ValueError(f"不支持的记忆框架类型: {framework_type}")


async def memory_store_node(state: MemoryTestState) -> dict[str, Any]:
    """记忆存储节点

    从 messages 中提取最新的对话对并存储到相应的记忆框架。
    这个节点在每轮对话结束后自动触发。

    Args:
        state: 当前状态

    Returns:
        状态更新字典（通常为空，因为只是存储记忆）
    """
    try:
        logger.info(f"开始存储记忆: {state.get('session_id')} -> {state.get('memory_framework')}")

        # 检查是否有完整的对话
        if not has_complete_conversation(state["messages"]):
            logger.debug("未找到完整的对话对，跳过存储")
            return {}

        # 提取最新的对话对
        user_input, ai_response = extract_latest_conversation(state["messages"])

        if not user_input or not ai_response:
            logger.warning("提取的对话对不完整，跳过存储")
            logger.debug(f"用户输入: '{user_input}', AI回复: '{ai_response}'")
            return {}

        # 获取记忆适配器
        memory_framework = state["memory_framework"]
        adapter = get_memory_adapter(memory_framework)

        # 存储对话
        success = await adapter.store_conversation(
            session_id=state["session_id"], user_input=user_input, ai_response=ai_response
        )

        if success:
            logger.info(f"记忆存储成功: {memory_framework}")
        else:
            logger.error(f"记忆存储失败: {memory_framework}")

        # 记忆存储节点不修改状态，只是进行存储操作
        return {}

    except Exception as e:
        logger.error(f"记忆存储节点处理失败: {e}")
        # 即使存储失败，也不影响对话流程
        return {}


def should_store_memory(state: MemoryTestState) -> bool:
    """判断是否应该存储记忆

    这个函数用于条件路由，决定是否需要进入记忆存储节点。

    Args:
        state: 当前状态

    Returns:
        是否需要存储记忆
    """
    try:
        # 检查基本条件
        if not state.get("session_id") or not state.get("memory_framework"):
            return False

        # 检查是否有完整的对话
        return has_complete_conversation(state["messages"])

    except Exception as e:
        logger.error(f"判断是否存储记忆时出错: {e}")
        return False


async def batch_store_conversation_history(state: MemoryTestState, max_conversations: int = 10) -> bool:
    """批量存储对话历史

    当用户首次使用某个记忆框架时，可以调用此函数批量存储历史对话。
    这对于数据迁移或初始化很有用。

    Args:
        state: 当前状态
        max_conversations: 最多存储的对话轮数

    Returns:
        是否存储成功
    """
    try:
        from memory.message_utils import get_conversation_history

        logger.info(f"开始批量存储对话历史: {state.get('session_id')}")

        # 获取对话历史
        conversation_history = get_conversation_history(state["messages"], max_conversations)

        if not conversation_history:
            logger.info("没有对话历史需要存储")
            return True

        # 获取记忆适配器
        adapter = get_memory_adapter(state["memory_framework"])

        # 逐个存储对话
        success_count = 0
        for conversation in conversation_history:
            user_input = conversation.get("user", "")
            ai_response = conversation.get("assistant", "")

            if user_input and ai_response:
                success = await adapter.store_conversation(
                    session_id=state["session_id"], user_input=user_input, ai_response=ai_response
                )
                if success:
                    success_count += 1

        logger.info(f"批量存储完成: {success_count}/{len(conversation_history)} 轮对话")
        return success_count > 0

    except Exception as e:
        logger.error(f"批量存储对话历史失败: {e}")
        return False


def get_memory_statistics(state: MemoryTestState) -> dict[str, Any]:
    """获取记忆统计信息

    Args:
        state: 当前状态

    Returns:
        记忆统计信息
    """
    try:
        from memory.message_utils import count_conversation_turns, get_conversation_history

        stats = {
            "session_id": state.get("session_id"),
            "memory_framework": state.get("memory_framework"),
            "total_conversation_turns": count_conversation_turns(state["messages"]),
            "total_messages": len(state["messages"]),
            "has_complete_conversation": has_complete_conversation(state["messages"]),
        }

        # 获取对话历史统计
        conversation_history = get_conversation_history(state["messages"])
        stats["conversation_history_count"] = len(conversation_history)

        # 分析对话内容类型
        topic_counts = {"事业": 0, "感情": 0, "财运": 0, "健康": 0, "其他": 0}

        for conversation in conversation_history:
            user_input = conversation.get("user", "").lower()
            for topic in topic_counts:
                if topic in user_input:
                    topic_counts[topic] += 1
                    break
            else:
                topic_counts["其他"] += 1

        stats["topic_distribution"] = topic_counts

        return stats

    except Exception as e:
        logger.error(f"获取记忆统计信息失败: {e}")
        return {"error": str(e)}
