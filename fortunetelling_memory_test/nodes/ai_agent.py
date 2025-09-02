"""
AI 对话代理节点

主要的算命师 AI 代理，配备记忆检索工具
"""

from typing import Any

from config import settings
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from loguru import logger
from memory.message_utils import get_latest_user_input
from prompts.system_prompts import get_system_prompt
from state import MemoryTestState
from tools.memory_tools import MEMORY_TOOLS


def create_ai_client():
    """创建 AI 客户端"""
    # 验证配置
    settings.validate_ai_config()

    # 根据配置选择 AI 提供商
    if settings.preferred_ai_provider == "anthropic":
        return ChatAnthropic(
            model=settings.ANTHROPIC_MODEL,
            api_key=settings.ANTHROPIC_API_KEY,
            base_url=settings.ANTHROPIC_BASE_URL,
            temperature=settings.AI_TEMPERATURE,
            # max_tokens=settings.AI_MAX_TOKENS,
        )
    elif settings.preferred_ai_provider == "openai":
        return ChatOpenAI(
            model=settings.OPENAI_MODEL,
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL,
            temperature=settings.AI_TEMPERATURE,
            # max_tokens=settings.AI_MAX_TOKENS,
        )
    else:
        raise ValueError("未找到可用的 AI API 密钥 (ANTHROPIC_API_KEY 或 OPENAI_API_KEY)")


async def ai_agent_node(state: MemoryTestState, config: RunnableConfig = None) -> dict[str, Any]:
    """AI 对话代理节点

    这是主要的 AI 节点，负责：
    1. 接收用户输入
    2. 智能决策是否使用记忆工具
    3. 生成专业的算命师回复

    Args:
        state: 当前状态
        config: 运行时配置

    Returns:
        状态更新字典
    """
    try:
        logger.info(f"AI代理节点开始处理: {state.get('session_id')}")

        # 获取用户最新输入
        user_input = get_latest_user_input(state["messages"])
        if not user_input:
            logger.warning("未找到用户输入")
            return {"messages": [AIMessage(content="请告诉我您想要咨询的问题。")]}

        # 创建 AI 客户端
        ai_client = create_ai_client()

        # 构建系统提示
        system_prompt = get_system_prompt(state["user_profile"], state["memory_framework"])

        # 准备消息列表
        # messages = [SystemMessage(content=system_prompt)]

        # # 添加历史对话（最近5轮）
        # recent_messages = state["messages"][-10:] if len(state["messages"]) > 10 else state["messages"]
        # messages.extend(recent_messages)

        prompt = ChatPromptTemplate.from_messages([("system", system_prompt), ("placeholder", "{messages}")])

        llm = prompt | ai_client.bind_tools(MEMORY_TOOLS)

        response = await llm.ainvoke({"messages": state["messages"]})

        # 配置工具调用
        # ai_with_tools = ai_client.bind_tools(MEMORY_TOOLS)

        # 传递状态信息给工具（通过 config）
        # tool_config = RunnableConfig(
        #     configurable={
        #         "session_id": state["session_id"],
        #         "memory_framework": state["memory_framework"],
        #         "user_profile": state["user_profile"]
        #     }
        # )

        # # 调用 AI 生成回复
        # response = await ai_with_tools.ainvoke(messages, config=tool_config)

        logger.info(f"AI回复生成成功 [{settings.preferred_ai_provider.upper()}]: {state.get('session_id')}")

        # 返回 AI 回复
        return {"messages": response}

    except Exception as e:
        logger.error(f"AI代理节点处理失败: {e}")

        # 返回错误回复
        error_message = "抱歉，我在分析过程中遇到了一些问题。请稍后再试，或者重新描述您的问题。"
        return {"messages": [AIMessage(content=error_message)]}


def should_use_memory_tools(user_input: str, conversation_turns: int) -> bool:
    """判断是否应该使用记忆工具

    这是一个启发式函数，帮助 AI 决策何时调用记忆工具。
    虽然 AI 可以自主决策，但这个函数可以作为参考。

    Args:
        user_input: 用户输入
        conversation_turns: 对话轮数

    Returns:
        是否建议使用记忆工具
    """
    # 历史相关关键词
    history_keywords = ["之前", "上次", "以前", "之前说过", "记得", "提到过"]

    # 话题相关关键词
    topic_keywords = ["事业", "感情", "财运", "健康", "工作", "恋爱", "投资"]

    # 趋势相关关键词
    trend_keywords = ["发展", "变化", "趋势", "未来", "接下来", "后面"]

    # 检查关键词匹配
    user_input_lower = user_input.lower()

    # 明确提到历史
    if any(keyword in user_input_lower for keyword in history_keywords):
        return True

    # 询问特定话题且对话轮数大于1
    if any(keyword in user_input_lower for keyword in topic_keywords) and conversation_turns > 1:
        return True

    # 询问趋势发展且对话轮数大于2
    if any(keyword in user_input_lower for keyword in trend_keywords) and conversation_turns > 2:
        return True

    return False


def analyze_user_intent(user_input: str) -> dict[str, Any]:
    """分析用户意图

    Args:
        user_input: 用户输入

    Returns:
        意图分析结果
    """
    intent = {"primary_topic": "general", "consultation_type": "general", "urgency": "normal", "detail_level": "medium"}

    user_input_lower = user_input.lower()

    # 主要话题识别
    if any(word in user_input_lower for word in ["事业", "工作", "职业", "升职"]):
        intent["primary_topic"] = "career"
    elif any(word in user_input_lower for word in ["感情", "恋爱", "结婚", "分手"]):
        intent["primary_topic"] = "relationship"
    elif any(word in user_input_lower for word in ["财运", "投资", "理财", "赚钱"]):
        intent["primary_topic"] = "wealth"
    elif any(word in user_input_lower for word in ["健康", "身体", "病"]):
        intent["primary_topic"] = "health"

    # 咨询类型
    if any(word in user_input_lower for word in ["预测", "未来", "会怎样"]):
        intent["consultation_type"] = "prediction"
    elif any(word in user_input_lower for word in ["分析", "为什么", "原因"]):
        intent["consultation_type"] = "analysis"
    elif any(word in user_input_lower for word in ["建议", "怎么办", "如何"]):
        intent["consultation_type"] = "advice"

    # 紧急程度
    if any(word in user_input_lower for word in ["急", "紧急", "马上", "立即"]):
        intent["urgency"] = "high"

    # 详细程度
    if len(user_input) > 100 or "详细" in user_input_lower:
        intent["detail_level"] = "high"
    elif len(user_input) < 20:
        intent["detail_level"] = "low"

    return intent
