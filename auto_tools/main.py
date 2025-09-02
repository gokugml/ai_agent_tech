import asyncio
from collections.abc import Sequence
from datetime import UTC, datetime
from typing import Annotated, Any, TypedDict

from google import genai
from google.genai import types
from langchain_core.messages import AIMessage, AnyMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

from auto_tools.tools import all_tools
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


def create_or_get_cache_by_genai():
    """创建或获取缓存的 system prompt"""
    try:
        # 手动设置 API key
        api_key = settings.GOOGLE_API_KEY
        if hasattr(api_key, "get_secret_value"):
            api_key = api_key.get_secret_value()
        client = genai.Client(api_key=str(api_key))
        
        # 尝试列出现有缓存
        try:
            caches = client.caches.list()
            for cache in caches:
                if cache.display_name == "Interest Analysis System Cache":
                    return cache.name
        except Exception:
            pass
        
        # 如果没有找到现有缓存，创建新的
        # 使用支持缓存的模型
        model_name = "models/gemini-2.5-flash"
        
        # 创建一个 content 来包含缓存的内容，需要足够的 token (至少1024个)
        long_context = """
        这是一个兴趣爱好分析系统的缓存内容。系统的主要功能是分析用户聊天内容中体现的兴趣爱好特征。
        
        系统分析流程包括：
        1. 首先识别说话人的性别特征
        2. 根据性别调用相应的分析工具
        3. 分析用户在聊天中提到的各种兴趣爱好
        4. 识别运动偏好，如篮球、足球、游泳、跑步等
        5. 识别娱乐偏好，如电影、音乐、游戏、读书等
        6. 识别社交偏好，如聚会、独处、线上交流等
        7. 识别学习偏好，如编程、语言学习、专业技能等
        8. 识别生活方式偏好，如旅行、美食、购物、家居等
        
        分析维度包括：
        - 兴趣的强度和持续性
        - 参与频率和投入程度
        - 社交属性（个人/团体活动）
        - 技能要求和成长性
        - 成本和时间投入
        - 季节性和地域性特征
        
        输出要求：
        - 使用客观、准确的描述
        - 避免主观判断和偏见
        - 提供结构化的分析结果
        - 突出最主要的兴趣特征
        - 给出兴趣发展建议
        
        这个系统可以处理各种类型的聊天内容，包括：
        - 日常对话中的兴趣表达
        - 专门的兴趣讨论
        - 间接的兴趣暗示
        - 群体聊天中的兴趣互动
        - 兴趣相关的计划和安排
        
        通过深度分析，系统能够准确识别用户的核心兴趣爱好，为个性化推荐和社交匹配提供数据支持。
        """ * 3  # 重复3次以达到足够的token数量
        
        cache_content = types.Content(
            role="user",
            parts=[types.Part(text=long_context)]
        )
        
        cache = client.caches.create(
            model=model_name,
            config=types.CreateCachedContentConfig(
                display_name="Interest Analysis System Cache",
                system_instruction=PROMPT,
                contents=[cache_content],
                ttl="3600s",  # 1小时缓存
            )
        )
        return cache.name
    except Exception:
        return None


# 创建缓存
# cached_content = create_or_get_cache()

# 创建模型实例
# if cached_content:
#     # 使用缓存时，需要使用相同的模型名
#     model = ChatGoogleGenerativeAI(
#         model="gemini-2.5-flash",
#         google_api_key=settings.GOOGLE_API_KEY,
#         temperature=0.3,
#         cached_content=cached_content,
#     )
# else:
#     # 没有缓存时使用普通模型
#     model = ChatGoogleGenerativeAI(
#         model="gemini-2.5-flash",
#         google_api_key=settings.GOOGLE_API_KEY,
#         temperature=0.3,
#     )

async def load_memories(state, config: RunnableConfig):
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


model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=settings.GOOGLE_API_KEY,
    temperature=0.3,
)


async def agent(state: State):
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", PROMPT),
            ("user", f"聊天内容：{format_history(state["history_messages"], tz=UTC)}"),
            ("placeholder", "{messages}")
        ]
    )
    
    llm = prompt | model.bind_tools(all_tools)
    response = await llm.ainvoke({"messages": state["messages"]})
    print(response.response_metadata)
    return {"messages": response}


# def tools_condition(state, messages_key: str = "messages"):
#     if isinstance(state, list):
#         ai_message = state[-1]
#     elif isinstance(state, dict) and (messages := state.get(messages_key, [])):
#         ai_message = messages[-1]
#     elif messages := getattr(state, messages_key, []):
#         ai_message = messages[-1]
#     else:
#         raise ValueError(f"No messages found in input state to tool_edge: {state}")
#     if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
#         return [Send()] 


# agent = create_react_agent(
#     model=model,
#     tools=all_tools,
#     prompt=PROMPT,
#     debug=True,
# )


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
graph = workflow.compile(name="test_auto_tools")

async def main():
    config = {
        "configurable":
            {
                "session_id": "ITFOPZQLOLVI"
            }
    }
    async for event in graph.astream(input={}, config=config, debug=True):
        print(event)

if __name__ == "__main__":
    asyncio.run(main())
