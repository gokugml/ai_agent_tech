"""
记忆检索工具

LangGraph 工具，供 AI 代理按需调用来检索历史记忆
"""

from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from loguru import logger
from memory.memobase_adapter import MemobaseMemoryAdapter
from memory.memu_adapter import MemuMemoryAdapter

# 全局记忆适配器实例
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


@tool
async def retrieve_memory(
    query: str, memory_type: str = "general", limit: int = 5, time_range: str = "all", config: RunnableConfig = None
) -> str:
    """检索相关记忆信息

    基于 MemU 最佳实践的高级记忆检索工具，支持语义检索和上下文感知。

    Args:
        query: 查询内容，描述你想查找的信息
        memory_type: 记忆类型 (general|conversation|analysis|prediction|topic_specific)
        limit: 返回的记忆数量限制 (1-10)
        time_range: 时间范围 (recent|week|month|all)

    Returns:
        格式化的记忆信息文本
    """
    try:
        # 从配置中获取状态信息
        if not config or "configurable" not in config:
            return "无法获取会话信息，记忆检索失败。"

        # 获取状态（这里需要通过某种方式传递状态）
        # 实际实现中，LangGraph 会将状态传递给工具
        state_dict = config.get("configurable", {})
        session_id = state_dict.get("session_id")
        memory_framework = state_dict.get("memory_framework")

        if not session_id or not memory_framework:
            return "会话信息不完整，无法进行记忆检索。"

        # 验证参数
        if limit < 1 or limit > 10:
            limit = 5

        # 获取对应的记忆适配器
        adapter = get_memory_adapter(memory_framework)

        # 根据 MemU 最佳实践，构造更精准的查询
        enhanced_query = _enhance_query_for_context(query, memory_type, time_range)

        # 执行记忆检索（使用新的MemU API）
        if memory_framework == "memu":
            # MemU框架使用新API
            memories = await adapter.retrieve_memories(session_id, enhanced_query, limit)
        else:
            # 其他框架保持原有API
            memories = await adapter.retrieve_memories(session_id, enhanced_query, limit)

        if not memories:
            return f"未找到与 '{query}' 相关的历史记忆。"

        # 格式化记忆信息
        formatted_memories = adapter.format_memories_for_prompt(memories)

        logger.info(f"记忆检索成功: {memory_framework}, 查询: '{query}', 结果数: {len(memories)}")
        return formatted_memories

    except Exception as e:
        logger.error(f"记忆检索失败: {e}")
        return f"记忆检索过程中出现错误，可能是网络连接或服务问题: {str(e)}"


@tool
async def search_conversation_history(
    topic: str, depth: str = "surface", limit: int = 3, config: RunnableConfig = None
) -> str:
    """搜索特定话题的对话历史

    基于 MemU 最佳实践的高级话题检索，支持不同深度的分析。

    Args:
        topic: 话题关键词 (如：事业、感情、财运、健康等)
        depth: 检索深度 (surface|浅层|deep|深入|comprehensive|全面)
        limit: 返回的对话数量限制 (1-8)

    Returns:
        相关的历史对话内容
    """
    # 根据深度调整查询策略
    if depth in ["deep", "深入"]:
        query = f"{topic} 相关对话 详细分析 深入讨论"
        limit = min(limit + 2, 8)
    elif depth in ["comprehensive", "全面"]:
        query = f"{topic} 全面 历史 趋势 变化"
        limit = min(limit + 3, 8)
    else:
        query = f"{topic} 相关对话"

    return await retrieve_memory(query, "topic_specific", limit, "all", config)


@tool
async def get_user_interaction_pattern(config: RunnableConfig = None) -> str:
    """获取用户交互模式分析

    分析用户的历史交互模式，了解其咨询习惯和偏好。

    Returns:
        用户交互模式的分析结果
    """
    try:
        if not config or "configurable" not in config:
            return "无法获取会话信息。"

        state_dict = config.get("configurable", {})
        session_id = state_dict.get("session_id")
        memory_framework = state_dict.get("memory_framework")

        if not session_id or not memory_framework:
            return "会话信息不完整。"

        # 获取记忆适配器
        adapter = get_memory_adapter(memory_framework)

        # 获取所有历史记忆进行分析
        if memory_framework == "memu":
            # MemU框架使用新API
            all_memories = await adapter.retrieve_memories(session_id, "所有对话", 20)
        else:
            all_memories = await adapter.retrieve_memories(session_id, "所有对话", 20)

        if not all_memories:
            return "用户首次咨询，暂无历史交互数据。"

        # 简单的模式分析
        analysis_parts = []

        # 统计咨询次数
        conversation_count = len([m for m in all_memories if m.get("type") == "conversation"])
        analysis_parts.append(f"历史咨询次数: {conversation_count}")

        # 分析咨询话题
        topics = []
        for memory in all_memories:
            content = memory.get("content", "").lower()
            if "事业" in content or "工作" in content:
                topics.append("事业发展")
            if "感情" in content or "恋爱" in content:
                topics.append("感情关系")
            if "财运" in content or "投资" in content:
                topics.append("财富运势")
            if "健康" in content:
                topics.append("健康养生")

        if topics:
            unique_topics = list(set(topics))
            analysis_parts.append(f"关注话题: {', '.join(unique_topics)}")

        # 分析咨询频率（基于时间戳）
        if len(all_memories) >= 2:
            recent_memory = max(all_memories, key=lambda x: x.get("timestamp", 0))
            analysis_parts.append(f"最近咨询时间: {recent_memory.get('timestamp', '未知')}")

        analysis_parts.append("用户特征: 对命理咨询有一定了解，希望获得深入分析")

        return "\\n".join(analysis_parts)

    except Exception as e:
        logger.error(f"用户模式分析失败: {e}")
        return f"分析过程中出现错误: {str(e)}"


@tool
async def check_prediction_accuracy(config: RunnableConfig = None) -> str:
    """检查历史预测的准确性

    查找之前的预测并分析其准确性，用于调整当前的预测方式。

    Returns:
        历史预测准确性的分析
    """
    try:
        if not config or "configurable" not in config:
            return "无法获取会话信息。"

        state_dict = config.get("configurable", {})
        session_id = state_dict.get("session_id")
        memory_framework = state_dict.get("memory_framework")

        if not session_id or not memory_framework:
            return "会话信息不完整。"

        # 获取记忆适配器
        adapter = get_memory_adapter(memory_framework)

        # 搜索预测相关的记忆
        if memory_framework == "memu":
            prediction_memories = await adapter.retrieve_memories(session_id, "预测 运势", 10)
        else:
            prediction_memories = await adapter.retrieve_memories(session_id, "预测 运势", 10)

        if not prediction_memories:
            return "暂无历史预测记录。"

        # 分析预测内容
        analysis = []
        prediction_count = 0

        for memory in prediction_memories:
            content = memory.get("content", "")
            if "预测" in content or "运势" in content:
                prediction_count += 1

                # 简单提取预测关键信息
                if "事业" in content:
                    analysis.append("事业方面的预测")
                if "财运" in content:
                    analysis.append("财运方面的预测")
                if "感情" in content:
                    analysis.append("感情方面的预测")

        result_parts = []
        result_parts.append(f"历史预测记录: {prediction_count} 次")

        if analysis:
            unique_predictions = list(set(analysis))
            result_parts.append(f"预测类型: {', '.join(unique_predictions)}")

        result_parts.append("建议: 基于历史预测情况，继续关注用户最关心的领域")

        return "\\n".join(result_parts)

    except Exception as e:
        logger.error(f"预测准确性检查失败: {e}")
        return f"检查过程中出现错误: {str(e)}"


def _enhance_query_for_context(query: str, memory_type: str, time_range: str) -> str:
    """根据 MemU 最佳实践增强查询上下文"""
    enhanced_parts = [query]

    # 根据记忆类型增强查询
    type_enhancements = {
        "conversation": "对话 交流 讨论",
        "analysis": "分析 解读 见解",
        "prediction": "预测 运势 将来",
        "topic_specific": "专题 深入 相关",
    }

    if memory_type in type_enhancements:
        enhanced_parts.append(type_enhancements[memory_type])

    # 根据时间范围增强查询
    if time_range == "recent":
        enhanced_parts.append("最近 新近")
    elif time_range == "week":
        enhanced_parts.append("本周 近期")
    elif time_range == "month":
        enhanced_parts.append("本月 近期")

    return " ".join(enhanced_parts)


@tool
async def get_contextual_insights(
    current_question: str, insight_type: str = "pattern", config: RunnableConfig = None
) -> str:
    """获取上下文相关的洞察

    根据 MemU 最佳实践，提供上下文感知的洞察分析。

    Args:
        current_question: 当前用户问题
        insight_type: 洞察类型 (pattern|模式|trend|趋势|context|上下文|correlation|关联)

    Returns:
        上下文相关的洞察信息
    """
    try:
        if not config or "configurable" not in config:
            return "无法获取会话信息。"

        state_dict = config.get("configurable", {})
        session_id = state_dict.get("session_id")
        memory_framework = state_dict.get("memory_framework")

        if not session_id or not memory_framework:
            return "会话信息不完整。"

        adapter = get_memory_adapter(memory_framework)

        # 根据洞察类型构造查询
        if insight_type in ["pattern", "模式"]:
            query = f"{current_question} 类似 模式 规律"
        elif insight_type in ["trend", "趋势"]:
            query = f"{current_question} 变化 趋势 发展"
        elif insight_type in ["context", "上下文"]:
            query = f"{current_question} 背景 原因 关联"
        elif insight_type in ["correlation", "关联"]:
            query = f"{current_question} 相关 影响 联系"
        else:
            query = current_question

        if memory_framework == "memu":
            memories = await adapter.retrieve_memories(session_id, query, 6)
        else:
            memories = await adapter.retrieve_memories(session_id, query, 6)

        if not memories:
            return f"暂无与 '{current_question}' 相关的历史洞察。"

        # 生成洞察分析
        insights = []
        insights.append(f"基于历史交流的 {insight_type} 分析:")

        formatted_memories = adapter.format_memories_for_prompt(memories)
        insights.append(formatted_memories)

        # 添加总结性洞察
        if len(memories) > 1:
            insights.append(f"\n总结: 找到 {len(memories)} 条相关记忆，建议结合历史情况提供更精准的指导。")

        return "\n".join(insights)

    except Exception as e:
        logger.error(f"上下文洞察获取失败: {e}")
        return f"无法获取上下文洞察: {str(e)}"


# 工具列表，供 AI 代理使用
MEMORY_TOOLS = [
    retrieve_memory,
    search_conversation_history,
    get_user_interaction_pattern,
    check_prediction_accuracy,
    get_contextual_insights,
]
