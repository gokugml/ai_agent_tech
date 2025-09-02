"""
LangGraph 兴趣爱好分析工作流
"""

from typing import Any, TypedDict

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.language_models.base import BaseLanguageModel
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import create_react_agent

from ..tools.sexual_selection import sexual_selection_tool
from ..tools.male_tools import man_spots_tool, man_study_tool
from ..tools.female_tools import woman_spots_tool, woman_activity_tool, woman_study_tool


class InterestAnalysisState(TypedDict):
    """工作流状态定义"""
    messages: list[BaseMessage]
    chat_content: str
    final_result: dict[str, Any]


def create_interest_analysis_workflow(llm: BaseLanguageModel) -> StateGraph:
    """创建兴趣爱好分析工作流"""
    
    # 创建所有工具的列表
    tools = [
        sexual_selection_tool,
        man_spots_tool,
        man_study_tool,
        woman_spots_tool,
        woman_activity_tool,
        woman_study_tool
    ]
    
    # 系统提示词，指定LLM的运行流程
    system_prompt = """你是一个兴趣爱好分析专家。请按照以下流程分析聊天内容：

1. 首先使用 Sexual_Selection_Tool 分析聊天内容中说话人的性别
2. 根据识别出的性别，调用对应的工具分析兴趣爱好：
   - 如果是男性，使用 Man_Spots_Tool 和 Man_Study_Tool
   - 如果是女性，使用 Woman_Spots_Tool、Woman_Activity_Tool 和 Woman_Study_Tool
3. 整合所有分析结果，返回完整的兴趣爱好报告

请严格按照这个顺序执行，确保先分析性别，再根据性别调用相应的工具。

输入的聊天内容为: {chat_content}

请开始分析。"""
    
    # 创建ReAct Agent
    agent_executor = create_react_agent(llm, tools)
    
    def llm_analysis_node(state: InterestAnalysisState) -> InterestAnalysisState:
        """LLM分析节点"""
        chat_content = state["chat_content"]
        
        # 创建系统消息和用户消息
        messages = [
            SystemMessage(content=system_prompt.format(chat_content=chat_content)),
            HumanMessage(content=f"请分析以下聊天内容的性别和兴趣爱好：\n\n{chat_content}")
        ]
        
        # 调用agent执行分析
        result = agent_executor.invoke({"messages": messages})
        
        # 提取最终结果
        final_result = {
            "analysis_complete": True,
            "agent_response": result["messages"][-1].content if result["messages"] else "分析完成",
            "chat_content": chat_content
        }
        
        return {
            **state,
            "messages": result["messages"],
            "final_result": final_result
        }
    
    # 创建工作流
    workflow = StateGraph(InterestAnalysisState)
    
    # 添加LLM分析节点
    workflow.add_node("llm_analysis", llm_analysis_node)
    
    # 设置入口点和结束点
    workflow.set_entry_point("llm_analysis")
    workflow.add_edge("llm_analysis", END)
    
    return workflow


def analyze_chat_interests(chat_content: str, llm: BaseLanguageModel) -> dict[str, Any]:
    """
    分析聊天内容中的兴趣爱好
    
    Args:
        chat_content: 聊天记录内容
        llm: 语言模型实例
        
    Returns:
        分析结果字典
    """
    workflow = create_interest_analysis_workflow(llm)
    app = workflow.compile()
    
    # 初始状态
    initial_state = {
        "messages": [],
        "chat_content": chat_content,
        "final_result": {}
    }
    
    # 运行工作流
    result = app.invoke(initial_state)
    
    return result["final_result"]