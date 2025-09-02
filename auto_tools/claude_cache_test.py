import asyncio
from collections.abc import Sequence
from datetime import UTC, datetime
from typing import Annotated, Any, TypedDict

from langchain_anthropic import ChatAnthropic, convert_to_anthropic_tool
from langchain_core.messages import AIMessage, AnyMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

from auto_tools.tools import all_tools, sexual_selection_tool
from auto_tools.utils import get_memories_client
from user_config import settings

PROMPT = """你是一个兴趣爱好分析专家。请按照以下流程分析聊天内容：

1. 首先使用 Sexual_Selection_Tool 分析聊天内容中说话人的性别
2. 根据识别出的性别，调用对应的工具分析兴趣爱好：
3. 整合所有分析结果，返回完整的兴趣爱好报告

请严格按照这个顺序执行，确保先分析性别，再根据性别调用相应的工具。

IMPORTANT: 尽可能一次性调用多个 tool
IMPORTANT: 使用纯文本输出，不要解释，禁止输出幻觉
"""


class State(TypedDict):
    messages: Annotated[Sequence[AnyMessage], add_messages]
    history_messages: Annotated[Sequence[AnyMessage], add_messages]


async def load_memories(state, config: RunnableConfig):
    """加载历史消息"""
    chat_message_history = get_memories_client(config["configurable"]["session_id"])  # type: ignore
    history_messages = chat_message_history.get_messages_with_count(200)
    return {"history_messages": history_messages}


def format_history(
    messages: Sequence[AnyMessage],
    tz: Any,
    human_prefix: str = "Human",
    ai_prefix: str = "AI",
) -> str:
    """把 BaseMessage 列表格式化成带时间的字符串。"""
    lines = []
    for msg in messages:
        ts: float | None = msg.additional_kwargs.get("chat_timestamp", None)
        if ts:
            local_ts = datetime.fromtimestamp(ts, tz=tz)
            ts_str = local_ts.isoformat()
        else:
            ts_str = "UNKNOWN"

        if isinstance(msg, HumanMessage):
            role = human_prefix
        elif isinstance(msg, AIMessage):
            role = ai_prefix
        else:
            raise ValueError("messages type error")
        lines.append(f"[{ts_str}] {role}: {msg.content}")
    return "\n".join(lines)


# 创建Claude模型实例
def create_claude_model():
    """创建Claude模型，支持缓存"""
    api_key = settings.ANTHROPIC_API_KEY
    model = ChatAnthropic(
        model="claude-sonnet-4-20250514",
        api_key=api_key,
        base_url=settings.ANTHROPIC_BASE_URL,
        streaming=False,
        temperature=0.3,
        extra_headers={"anthropic-beta": "prompt-caching-2024-07-31"}
    )
    return model, PROMPT


model, system_prompt = create_claude_model()


async def agent(state: State):
    """Claude代理节点"""
    prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessage(
                content=[
                    {
                        "type": "text",
                        "text": system_prompt
                    }
                ]
            ),
            HumanMessage(
                content=[
                    {
                        "type": "text",
                        "text": f"聊天内容：{format_history(state['history_messages'], tz=UTC)}",
                        "cache_control": {"type": "ephemeral"}
                    }
                ]
            ),
            ("placeholder", "{messages}")
        ]
    )
    
    cache_sexual_selection_tool = convert_to_anthropic_tool(sexual_selection_tool)
    cache_sexual_selection_tool["cache_control"] = {"type": "ephemeral"}
    
    llm = prompt | model.bind_tools([*all_tools[:-1], cache_sexual_selection_tool])
    response = await llm.ainvoke({"messages": state["messages"]})
    
    # 输出响应元数据，包括缓存相关信息
    print("📊 Claude响应元数据:")
    print(response.response_metadata)
    print(response.usage_metadata["input_token_details"])
    
    # 检查是否使用了缓存
    usage = response.response_metadata.get("usage", {})
    if "cache_creation_input_tokens" in usage or "cache_read_input_tokens" in usage:
        print("🚀 检测到缓存使用！")
        if cache_creation := usage.get("cache_creation_input_tokens"):
            print(f"   缓存创建Token数: {cache_creation}")
        if cache_read := usage.get("cache_read_input_tokens"):
            print(f"   缓存读取Token数: {cache_read}")
    else:
        print("ℹ️ 未检测到缓存使用")
    
    return {"messages": response}


# 创建LangGraph工作流
workflow = StateGraph(State)

workflow.add_node(load_memories)
workflow.add_node(agent)
workflow.add_node("tools", ToolNode(all_tools))

workflow.add_edge(START, "load_memories")
workflow.add_edge("load_memories", "agent")
workflow.add_conditional_edges(
    "agent",
    tools_condition,
    ["tools", END]
)
workflow.add_edge("tools", "agent")

graph = workflow.compile(name="claude_cache_test")


async def main():
    """主测试函数"""
    print("🚀 开始Claude Sonnet-4缓存测试")
    print("=" * 60)
    
    # 检查API配置
    if not settings.ANTHROPIC_API_KEY:
        print("❌ 未配置ANTHROPIC_API_KEY，无法进行Claude测试")
        return False
    
    print("✅ Claude API配置已就绪")
    
    config = {
        "configurable":
            {
                "session_id": "ITFOPZQLOLVI"
            }
    }
    
    # 执行第一次调用（可能创建缓存）
    print("\n📝 执行第一次调用（缓存创建）...")
    start_time = asyncio.get_event_loop().time()
    
    async for event in graph.astream(
        input={}, 
        config=config, 
        debug=False
    ):
        print(f"事件: {list(event.keys())}")
    
    first_call_time = asyncio.get_event_loop().time() - start_time
    print(f"⏱️ 第一次调用耗时: {first_call_time:.2f}秒")
    
    # 等待一秒后执行第二次调用（应该使用缓存）
    await asyncio.sleep(1)
    print("\n📝 执行第二次调用（缓存重用）...")
    start_time = asyncio.get_event_loop().time()
    
    async for event in graph.astream(
        input={}, 
        config=config, 
        debug=False
    ):
        print(f"事件: {list(event.keys())}")
    
    second_call_time = asyncio.get_event_loop().time() - start_time
    print(f"⏱️ 第二次调用耗时: {second_call_time:.2f}秒")
    
    # 分析性能差异
    if second_call_time < first_call_time * 0.8:
        print("🎉 检测到明显的缓存性能提升！")
        print(f"性能提升: {((first_call_time - second_call_time) / first_call_time * 100):.1f}%")
    else:
        print("ℹ️ 未检测到明显的缓存性能提升")
    
    print("\n✅ Claude缓存测试完成")
    return True


if __name__ == "__main__":
    asyncio.run(main())