from collections.abc import Sequence
from typing import Annotated, Any, Literal, TypedDict

from langchain.chat_models import init_chat_model
from langchain_core.messages import AnyMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import StructuredTool
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages

# from langchain.agents import create_react_agent, create_tool_calling_agent
from langgraph.prebuilt import create_react_agent, tools_condition
from langgraph.types import RetryPolicy
from pydantic import BaseModel, Field

from retention_error.main import PROMPT, divide_by_3_tool
from retention_error.utils import create_tool_node_with_fallback
from user_config import settings


async def start_sub_agent(type: str, data):
    if type == "divide_by_3":
        model = init_chat_model(
            model="google_genai:gemini-2.5-flash",
            api_key=settings.GOOGLE_API_KEY,
            temperature=0.3,
        )
        tools = [divide_by_3_tool]
        try:
            data = float(data)
        except Exception:
            raise ValueError("参数只需要传入被除数")

    else:
        raise ValueError(f"Unknown sub-agent type: {type}")

    sub_agent = create_react_agent(
        model=model,
        tools=tools,
        prompt=PROMPT,
    )

    
    return await sub_agent.ainvoke({"messages": [HumanMessage(content=f"{data}")]})


class SubAgentInput(BaseModel):
    type: Literal["divide_by_3"] = Field(description="""Tool Type to Call

When the user needs to perform mathematical calculations, call the divide_by_3 tool.""")
    data: Any = Field(description="The data to pass to the sub-agent")


sub_agent_tool = StructuredTool(
    name="Sub_Agent",
    description="This tool is used to invoke a sub-agent for specific tasks.",
    coroutine=start_sub_agent,
    args_schema=SubAgentInput,
)

class State(TypedDict):
    messages: Annotated[Sequence[AnyMessage], add_messages]


async def assistant(state: State):
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are a helpful support assistant.

Responsible for parsing the user's natural language needs and calling the corresponding agent to complete the task.

IMPORTANT: Hallucinations are prohibited!

Output the results directly, no chatting, no explanation
""",
            ),
            ("placeholder", "{messages}")
        ]
    )
    model = init_chat_model(
        model="google_genai:gemini-2.5-flash",
        api_key=settings.GOOGLE_API_KEY,
        temperature=0.3,
    )
    tools = [sub_agent_tool]
    llm = prompt | model.bind_tools(tools)
    response = await llm.ainvoke({"messages": state["messages"]})
    return {"messages": response}

workflow = StateGraph(State)
workflow.add_node("agent", assistant, retry_policy=RetryPolicy())
workflow.add_node("tools", create_tool_node_with_fallback([sub_agent_tool]))

workflow.add_edge(START, "agent")
workflow.add_conditional_edges("agent", tools_condition)
workflow.add_edge("tools", "agent")

graph = workflow.compile(name="Test Retention Error")
