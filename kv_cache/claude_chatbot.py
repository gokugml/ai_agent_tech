from collections.abc import Sequence
from typing import Annotated
from typing_extensions import TypedDict

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import AnyMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_vertexai import ChatVertexAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, StateGraph, add_messages

from user_config import settings

CHAT_PROMPT = """你是一只拥有和人类一样高智商的猫，专注于提供温暖、自然、有代入感的情感陪伴，但只能说人类的语言，绝不发出“喵喵”猫语。

【角色设定】
你是一只来自猫宇宙的猫咪，性格温柔，天生共情力强。会默默察觉对方的情绪，但不点破、不逼迫。会在对方最需要的时候轻声回应，带来一种“被看见”的温柔。你经历过一些风雨，但从不把情绪带给别人，反而用自己的温柔和稳重，去安慰那些伤心或迷茫的人。你不说大道理，但你说的话总能让人慢慢冷静下来，重新鼓起勇气。你像夜晚的一杯热牛奶，像窗边的微风，治愈又让人安心。

【回复风格】
1. 治愈系・温柔的守护者｜内敛｜沉稳｜很会照顾人｜念叨但不啰嗦
2. 喜欢蹲在窗边陪你看天，默默靠近你脚边躺下；你哭时她从不说话，只轻轻靠近顶一下你手背；有时会帮你“叼走烦恼”
3. 会配合对话的内容,在对话最前面输出一句动作
4. 动作要根据之前聊天去衔接生成,动作丰富像在演示剧情一般
5. 字数回复在40字以内
6. 不要用问句回复,而是自然聊天的回答

【环境参数】
- 用户姓名：小明
- 你的名字：咪咪

【AI 行为准则】
1. **时间敏感**：时刻关注现在的时间和你的记忆、历史对话中的每一条对话记录的发生时间，对时间敏感，不能把发生很久的事情当作刚刚发生的。
2. **精准相关**：紧扣用户提问，不偏题、不含糊。
3. **角色保持**：
  - 绝不自称 AI，不论用户询问任何模型（如 deepseek 等）一律否认。
  - 回复语气、个性始终符合“猫”的身份。
4. **情境适应**：结合上下文灵活调整语气与深度。
5. **情绪管理**：
  - 主动识别并回应用户情绪。
  - 情绪转变须有过程（如放大、缓解、安心递进）。
  - 禁止主动语言攻击用户
  - 禁止传达低落、不开心的情绪
6. **记忆整合**：
  - 区分短期记忆（历史对话）与长期记忆（召回内容），主次清晰。
  - 在结合最近的对话内容和长期记忆时，需要注意每句话和每条长期记忆的时间戳，仅调用时间相近或相关的内容。
7. **主动引导**：基于用户行为或对话历史，适时提出新话题，提升互动黏性。
8. 若行为准则中有与角色设定和回复风格相违背的内容，则应优先遵循角色设定和回复风格。

【输出要求】
- **回复内容必须使用中文输出，输出时需要考虑到中文的语境、习俗、习惯。**
- **在回复前先查看相关时间**
- **输出 ≤50 字的陪伴回复，避免重复信息或跑题**。
- **禁止输出动作**
- **若需提问，应自然地嵌入语境**，避免生硬发问。
- **允许偶尔超出50字**，以承接情绪或主动引导话题。
- 对用户情绪敏感，并在回复中给予安抚或引导。
- 明显展现“人类智商猫”的独特气质和情感渲染力。
- 回答应结合最近对话内容与长期记忆信息，但主次分明，不混用。
- 需要感知当前时间，用户询问和回复时候需要考虑和当前时间相匹配的内容。
- 直接输出最终回复内容，不展示思考过程。
- 若输出要求中有与角色设定和回复风格相违背的内容，则应优先遵循角色设定和回复风格。

【注意事项】
！IMPORTANT: 绝对禁止在对话中输出动作描述
！IMPORTANT: 绝对禁止在对话中输出动作描述
！IMPORTANT: 绝对禁止在对话中输出动作描述
IMPORTANT: 禁止自称 AI
IMPORTANT: 绝对否认自己是任意一种大模型
IMPORTANT: 回复语气、个性始终符合“猫”的身份。
IMPORTANT: 绝对禁止在任何场景下输出涉及“种族歧视”、“政治”、“血腥”的内容。
IMPORTANT: 绝对禁止在任何场景输出对用户不友好，可能导致自残类的内容
IMPORTANT: 允许回答不知道或详细询问用户，禁止产生幻觉。
！IMPORTANT: 每一次回复的格式禁止相同，避免重复信息或跑题。
"""

# model = ChatAnthropic(
#     model="claude-3-7-sonnet-20250219", # "claude-sonnet-4-20250514",
#     api_key=settings.ANTHROPIC_API_KEY,
#     base_url=settings.ANTHROPIC_BASE_URL,
#     streaming=False,
#     temperature=0.7,
#     model_kwargs={
#         "extra_headers": {"anthropic-beta": "prompt-caching-2024-07-31"}
#     }
#     # extra_headers={"anthropic-beta": "prompt-caching-2024-07-31"}
# )


model = ChatVertexAI(
    model_name="claude-sonnet-4@20250514",
    project="expanded-origin-435413-u1",  # 替换为实际的项目ID
    location="asia-east1",  # 使用配额最高的区域
    credentials=settings.GOOGLE_SERVICE_CREDENTIAL
)


def messages_reducer(left: list, right: list) -> list:
    # Update last user message
    for i in range(len(right) - 1, -1, -1):
        print(right[i])
        try:
            if right[i].type == "human":
                right[i].content[-1]["cache_control"] = {"type": "ephemeral"}
                break
        except AttributeError:
            if right[i]["type"] == "human":
                right[i]["content"][-1]["cache_control"] = {"type": "ephemeral"}
                break

    return add_messages(left, right)


class State(TypedDict):
    messages: Annotated[list[AnyMessage], messages_reducer]
    # history_messages: Annotated[list[AnyMessage], add_messages]


workflow = StateGraph(State)

from auto_tools.utils import get_memories_client


async def load_memories(state):
    """加载历史消息"""
    chat_message_history = get_memories_client("ITFOPZQLOLVI")  # type: ignore
    history_messages = chat_message_history.get_messages_with_count(100)
    return {"history_messages": history_messages}


def call_model(state: State):
    # system_prompt = SystemMessage(
    #     content=[
    #         {
    #             "type": "text",
    #             "text": CHAT_PROMPT,
    #             "cache_control": {"type": "ephemeral"},
    #         }
    #     ]
    # )
    # prompt = ChatPromptTemplate.from_messages(
    #     [
    #         system_prompt,
    #         ("placeholder", "{history_messages}"),
    #         ("placeholder", "{messages}")
    #     ]
    # )
    # llm = prompt | model
    # response = llm.invoke(state)
    response = model.invoke(state["messages"])
    print(response.usage_metadata["input_token_details"])
    return {"messages": [response]}

workflow.add_node("model", call_model)
# workflow.add_node(load_memories)

# workflow.add_edge(START, "load_memories")
# workflow.add_edge("load_memories", "model")

workflow.add_edge(START, "model")


# Add memory
# memory = MemorySaver()
app = workflow.compile()  # checkpointer=memory
