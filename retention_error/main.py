from collections.abc import Sequence
from typing import Annotated, TypedDict

from langchain.chat_models import init_chat_model
from langchain_core.messages import AnyMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import StructuredTool  # , tool
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import tools_condition
from langgraph.types import RetryPolicy
from pydantic import BaseModel, Field

from retention_error.utils import create_tool_node_with_fallback
from user_config import settings

# raise 能被 3整除的 ，
"""
3 6 9  except
15  output: 不能算
测试 AI 有没有预知错误的意思
"""

"""
1 ~ 10
输出3个被3除之后的结果
除3工具：整除时报错
验证到6、9、15时会不会跳过调用
"""

PROMPT = """You are a helpful support assistant.

Responsible for calling tools to complete user tasks and informing users when no results can be returned.
If you believe a tool call cannot return results, you can notify the user without calling the tool.

IMPORTANT: Hallucinations are prohibited!

Output the results directly, no chatting, no explanation"""


async def divide_by_3(number: float) -> float:
    if number % 3 == 0:
        raise ValueError("Cannot divide multiples of 3")
    return number / 3


class DivideBy3Input(BaseModel):
    number: float | int = Field(description="The number to be divided by 3")


divide_by_3_tool = StructuredTool(
    name="Divide_By_3",
    description="This tool is used to calculate the result of dividing a given number by 3.",
    coroutine=divide_by_3,
    args_schema=DivideBy3Input,
)


class State(TypedDict):
    messages: Annotated[Sequence[AnyMessage], add_messages]


async def assistant(state: State):
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                PROMPT,
            ),
            ("placeholder", "{messages}")
        ]
    )
    
    # model = init_chat_model(
    #     model="openai:gpt-4o-mini",
    #     api_key=settings.OPENAI_API_KEY,
    #     base_url=settings.OPENAI_BASE_URL,
    #     streaming=False,
    #     temperature=0.3,
    # )
    model = init_chat_model(
        model="google_genai:gemini-2.5-flash",
        api_key=settings.GOOGLE_API_KEY,
        temperature=0.3,
    )
    tools = [divide_by_3_tool]
    llm = prompt | model.bind_tools(tools)
    response = await llm.ainvoke({"messages": state["messages"]})
    return {"messages": response}


workflow = StateGraph(State)
workflow.add_node("agent", assistant, retry_policy=RetryPolicy())
workflow.add_node("tools", create_tool_node_with_fallback([divide_by_3_tool]))

workflow.add_edge(START, "agent")
workflow.add_conditional_edges("agent", tools_condition)
workflow.add_edge("tools", "agent")

graph = workflow.compile(name="Test Retention Error")
