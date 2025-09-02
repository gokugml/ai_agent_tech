from langgraph.graph import END, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from src.nodes.agent import agent
from src.nodes.memobase_memory import memory_store, retrieve_default_categories
from src.state import State
from src.tools.memobase_memory import memory_tools

workflow = StateGraph(State)

workflow.add_node(agent)
workflow.add_node(memory_store)
workflow.add_node(retrieve_default_categories)
workflow.add_node("tools", ToolNode(memory_tools))

workflow.set_entry_point("retrieve_default_categories")
workflow.add_edge("retrieve_default_categories", "agent")
workflow.add_conditional_edges("agent", tools_condition, {"tools": "tools", END: "memory_store"})
workflow.add_edge("tools", "agent")
workflow.add_edge("memory_store", END)

graph = workflow.compile()
