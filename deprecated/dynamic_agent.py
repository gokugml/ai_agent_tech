# LangGraph 动态工具选择代理
# 实现基于状态机的动态工具选择，采用 Manus 模式

from typing import TypedDict, Any, Optional, Annotated
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
import json
import re

from tools import tool_registry
from tool_selector import AdvancedToolSelector
from user_config import settings

# ============================================================================
# 状态定义
# ============================================================================

class DynamicAgentState(TypedDict):
    """动态代理状态"""
    messages: Annotated[list[BaseMessage], add_messages]  # 消息历史
    user_query: str                                       # 当前用户查询
    available_tool_categories: list[str]                  # 可用工具类别
    selected_tools: list[Any]                            # 选中的工具列表
    selection_confidence: float                           # 工具选择置信度
    selection_method: str                                 # 使用的选择方法
    conversation_state: dict[str, Any]                    # 对话状态
    iteration_count: int                                  # 迭代计数
    max_iterations: int                                   # 最大迭代次数
    tool_call_results: list[dict[str, Any]]              # 工具调用结果
    is_complete: bool                                     # 是否完成

# ============================================================================
# 核心节点函数
# ============================================================================

def analyze_query_node(state: DynamicAgentState) -> DynamicAgentState:
    """分析查询节点 - 确定工具选择策略"""
    
    user_query = state.get("user_query", "")
    if not user_query and state.get("messages"):
        # 从最后一条用户消息中提取查询
        for msg in reversed(state["messages"]):
            if isinstance(msg, HumanMessage):
                user_query = msg.content
                break
    
    # 分析查询复杂度，决定选择方法
    selection_method = "hybrid"  # 默认使用混合方法
    
    # 简单查询用关键词匹配
    if len(str(user_query).split()) <= 5:
        selection_method = "keywords"
    # 复杂查询或多步骤查询用混合方法
    elif any(keyword in str(user_query).lower() for keyword in ["然后", "接着", "之后", "同时", "and then", "also"]):
        selection_method = "hybrid"
    # 如果有明确的上下文信息，使用上下文方法
    elif state.get("conversation_state", {}).get("has_data") or len(state.get("messages", [])) > 2:
        selection_method = "context"
    
    return {
        **state,
        "user_query": user_query,
        "selection_method": selection_method,
        "iteration_count": state.get("iteration_count", 0),
        "max_iterations": state.get("max_iterations", 5),
        "is_complete": False
    }

def select_tools_node(state: DynamicAgentState) -> DynamicAgentState:
    """工具选择节点 - 动态选择相关工具"""
    
    selector = AdvancedToolSelector(tool_registry)
    
    # 执行工具选择
    selected_tools, selected_categories, confidence = selector.select_tools(
        query=state["user_query"],
        method=state.get("selection_method", "hybrid"),
        conversation_state=state.get("conversation_state", {}),
        max_categories=3
    )
    
    # 更新选择历史
    selector.update_selection_history(state["user_query"], selected_categories)
    
    return {
        **state,
        "available_tool_categories": selected_categories,
        "selected_tools": selected_tools,
        "selection_confidence": confidence
    }

def constrained_llm_call_node(state: DynamicAgentState) -> DynamicAgentState:
    """受约束的LLM调用节点 - 实现Manus模式的工具约束"""
    
    # 初始化LLM
    try:
        llm = init_chat_model(
            model="google_genai:gemini-2.5-flash",
            api_key=settings.GOOGLE_API_KEY,
            temperature=0.3,
        )
    except Exception as e:
        print(f"LLM初始化失败: {e}")
        return {**state, "is_complete": True}
    
    # 构建约束提示
    available_categories = state.get("available_tool_categories", [])
    selected_tools = state.get("selected_tools", [])
    
    if available_categories:
        category_constraint = f"你必须只使用以下类别的工具：{', '.join([f'{cat}_' for cat in available_categories])}"
    else:
        category_constraint = "当前没有可用的工具"
    
    # 构建工具信息
    tool_descriptions = []
    for tool in selected_tools:
        tool_descriptions.append(f"- {tool.name}: {tool.description}")
    
    tools_info = "\\n".join(tool_descriptions) if tool_descriptions else "无可用工具"
    
    system_prompt = f"""你是一个AI助手，可以使用工具来帮助用户完成任务。

工具使用约束：{category_constraint}

可用工具:
{tools_info}

IMPORTANT: 你必须严格遵守工具使用约束。只能使用指定类别的工具。

工具调用格式：
<tool_call>
{{"name": "工具名", "arguments": {{"参数名": "参数值"}}}}
</tool_call>

如果不需要使用工具，直接回答用户问题。
如果需要使用工具，必须按照上述格式调用工具。
"""
    
    # 构建消息列表
    messages = [{"role": "system", "content": system_prompt}]
    
    # 添加历史消息（转换格式）
    for msg in state.get("messages", []):
        if isinstance(msg, HumanMessage):
            messages.append({"role": "user", "content": msg.content})
        elif isinstance(msg, AIMessage):
            messages.append({"role": "assistant", "content": msg.content})
        elif isinstance(msg, ToolMessage):
            messages.append({"role": "tool", "content": msg.content})
    
    # 如果没有用户消息，添加当前查询
    if not any(msg.get("role") == "user" for msg in messages[1:]):  # 跳过system消息
        messages.append({"role": "user", "content": state["user_query"]})
    
    try:
        # 调用LLM（使用所有工具，但通过提示约束）
        response = llm.bind(tools=selected_tools).invoke(messages)
        
        # 将响应添加到消息历史
        ai_message = AIMessage(content=response.content)
        
        return {
            **state,
            "messages": state.get("messages", []) + [ai_message]
        }
        
    except Exception as e:
        print(f"LLM调用失败: {e}")
        error_message = AIMessage(content=f"抱歉，处理您的请求时出现错误：{str(e)}")
        return {
            **state,
            "messages": state.get("messages", []) + [error_message],
            "is_complete": True
        }

def execute_tools_node(state: DynamicAgentState) -> DynamicAgentState:
    """工具执行节点 - 解析并执行工具调用"""
    
    # 获取最后一条AI消息
    last_message = None
    for msg in reversed(state.get("messages", [])):
        if isinstance(msg, AIMessage):
            last_message = msg
            break
    
    if not last_message:
        return {**state, "is_complete": True}
    
    message_content = last_message.content
    # tool_results = []  # 保留以防后续需要
    
    # 查找工具调用
    tool_call_pattern = r'<tool_call>\\s*({.*?})\\s*</tool_call>'
    tool_calls = re.findall(tool_call_pattern, str(message_content), re.DOTALL)
    
    if not tool_calls:
        # 没有工具调用，任务完成
        return {**state, "is_complete": True}
    
    # 执行工具调用
    selected_tools = state.get("selected_tools", [])
    tool_dict = {tool.name: tool for tool in selected_tools}
    
    executed_results = []
    
    for tool_call_json in tool_calls:
        try:
            # 解析工具调用JSON
            tool_call = json.loads(tool_call_json)
            tool_name = tool_call.get("name")
            tool_args = tool_call.get("arguments", {})
            
            # 检查工具是否可用
            if tool_name not in tool_dict:
                result = f"错误：工具 {tool_name} 不在允许的工具列表中"
            else:
                # 执行工具
                tool_func = tool_dict[tool_name]
                try:
                    if isinstance(tool_args, dict):
                        result = tool_func.invoke(tool_args)
                    else:
                        result = f"错误：工具参数格式不正确：{tool_args}"
                except Exception as e:
                    result = f"工具执行错误：{str(e)}"
            
            executed_results.append({
                "tool_name": tool_name,
                "arguments": tool_args,
                "result": result
            })
            
            # 添加工具消息到历史 (保留以防后续需要)
            # tool_message = ToolMessage(content=result, tool_call_id=tool_name)
            
        except json.JSONDecodeError as e:
            error_result = f"工具调用JSON解析错误：{str(e)}"
            executed_results.append({
                "tool_name": "unknown",
                "arguments": {},
                "result": error_result
            })
            # tool_message = ToolMessage(content=error_result, tool_call_id="error")  # 保留以防后续需要
    
    # 更新对话状态
    new_conversation_state = state.get("conversation_state", {}).copy()
    
    # 根据执行的工具更新状态
    for result in executed_results:
        tool_name = result["tool_name"]
        if tool_name.startswith("file_"):
            new_conversation_state["needs_file_ops"] = True
        elif tool_name.startswith("db_"):
            new_conversation_state["database_session"] = True
        elif tool_name.startswith("code_"):
            new_conversation_state["has_data"] = True
        elif tool_name.startswith("image_"):
            new_conversation_state["working_with_images"] = True
    
    return {
        **state,
        "tool_call_results": state.get("tool_call_results", []) + executed_results,
        "conversation_state": new_conversation_state,
        "iteration_count": state.get("iteration_count", 0) + 1
    }

def should_continue_node(state: DynamicAgentState) -> str:
    """判断是否应该继续的决策节点"""
    
    # 检查是否已完成
    if state.get("is_complete", False):
        return "end"
    
    # 检查迭代次数
    if state.get("iteration_count", 0) >= state.get("max_iterations", 5):
        return "end"
    
    # 检查是否有工具调用结果需要处理
    if state.get("tool_call_results"):
        # 如果有工具执行结果，可能需要进一步处理
        last_results = state.get("tool_call_results", [])[-3:]  # 检查最近3个结果
        
        # 如果最近的结果表明需要更多工具
        for result in last_results:
            if "需要" in result.get("result", "") or "error" in result.get("result", "").lower():
                return "select_tools"
    
    # 检查最后一条消息是否包含未执行的工具调用
    last_message = None
    for msg in reversed(state.get("messages", [])):
        if isinstance(msg, AIMessage):
            last_message = msg
            break
    
    if last_message and "<tool_call>" in last_message.content:
        return "execute_tools"
    
    # 默认结束
    return "end"

# ============================================================================
# 构建LangGraph工作流
# ============================================================================

def build_dynamic_tool_agent():
    """构建动态工具选择代理"""
    
    # 创建状态图
    workflow = StateGraph(DynamicAgentState)
    
    # 添加节点
    workflow.add_node("analyze_query", analyze_query_node)
    workflow.add_node("select_tools", select_tools_node)
    workflow.add_node("llm_call", constrained_llm_call_node)
    workflow.add_node("execute_tools", execute_tools_node)
    
    # 设置入口点
    workflow.set_entry_point("analyze_query")
    
    # 添加边
    workflow.add_edge("analyze_query", "select_tools")
    workflow.add_edge("select_tools", "llm_call")
    
    # 添加条件边
    workflow.add_conditional_edges(
        "llm_call",
        should_continue_node,
        {
            "select_tools": "select_tools",
            "execute_tools": "execute_tools", 
            "end": END
        }
    )
    
    workflow.add_conditional_edges(
        "execute_tools",
        should_continue_node,
        {
            "select_tools": "select_tools",
            "execute_tools": "execute_tools",
            "end": END
        }
    )
    
    return workflow.compile()

# ============================================================================
# 便捷使用接口
# ============================================================================

class DynamicToolAgent:
    """动态工具代理包装类"""
    
    def __init__(self):
        self.workflow = build_dynamic_tool_agent()
        self.selector = AdvancedToolSelector(tool_registry)
    
    def invoke(self, 
               user_query: str, 
               conversation_state: Optional[dict[str, Any]] = None,
               max_iterations: int = 5) -> dict[str, Any]:
        """调用代理处理用户查询"""
        
        # 构建初始状态
        initial_state = {
            "messages": [HumanMessage(content=user_query)],
            "user_query": user_query,
            "available_tool_categories": [],
            "selected_tools": [],
            "selection_confidence": 0.0,
            "selection_method": "hybrid",
            "conversation_state": conversation_state or {},
            "iteration_count": 0,
            "max_iterations": max_iterations,
            "tool_call_results": [],
            "is_complete": False
        }
        
        try:
            # 执行工作流
            result = self.workflow.invoke(initial_state)
            
            # 提取最终响应
            final_response = ""
            for msg in reversed(result.get("messages", [])):
                if isinstance(msg, AIMessage):
                    final_response = msg.content
                    break
            
            return {
                "response": final_response,
                "tool_categories_used": result.get("available_tool_categories", []),
                "selection_confidence": result.get("selection_confidence", 0.0),
                "tool_results": result.get("tool_call_results", []),
                "iterations": result.get("iteration_count", 0),
                "conversation_state": result.get("conversation_state", {}),
                "messages": result.get("messages", [])
            }
            
        except Exception as e:
            return {
                "response": f"处理请求时出现错误：{str(e)}",
                "tool_categories_used": [],
                "selection_confidence": 0.0,
                "tool_results": [],
                "iterations": 0,
                "conversation_state": conversation_state or {},
                "messages": [HumanMessage(content=user_query)]
            }
    
    def get_available_categories(self) -> list[str]:
        """获取所有可用的工具类别"""
        return tool_registry.get_available_categories()
    
    def get_selection_stats(self) -> dict[str, Any]:
        """获取工具选择统计信息"""
        return self.selector.get_selection_statistics()

# ============================================================================
# 使用示例
# ============================================================================

def test_dynamic_agent():
    """测试动态工具代理"""
    
    agent = DynamicToolAgent()
    
    test_cases = [
        {
            "query": "查询苹果公司的股价",
            "conversation_state": {},
            "expected_categories": ["finance"]
        },
        {
            "query": "搜索最新的AI新闻并保存到文件",
            "conversation_state": {},
            "expected_categories": ["web", "file"]
        },
        {
            "query": "分析这些销售数据",
            "conversation_state": {"has_data": True},
            "expected_categories": ["code", "file"]
        },
        {
            "query": "发送邮件给客户，告诉他们分析结果",
            "conversation_state": {"has_data": True},
            "expected_categories": ["email", "code"]
        }
    ]
    
    print("=== 动态工具代理测试 ===")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\\n测试用例 {i}:")
        print(f"查询: {test_case['query']}")
        
        result = agent.invoke(
            user_query=test_case["query"],
            conversation_state=test_case["conversation_state"],
            max_iterations=3
        )
        
        print(f"响应: {result['response'][:100]}...")
        print(f"使用的工具类别: {result['tool_categories_used']}")
        print(f"选择置信度: {result['selection_confidence']:.2f}")
        print(f"工具调用次数: {len(result['tool_results'])}")
        print(f"迭代次数: {result['iterations']}")
        
        # 简单验证
        expected = test_case["expected_categories"]
        actual = result["tool_categories_used"]
        overlap = set(expected) & set(actual)
        print(f"类别匹配度: {len(overlap)}/{len(expected)}")
    
    # 显示统计信息
    print("\\n=== 代理统计信息 ===")
    stats = agent.get_selection_stats()
    print(f"可用工具类别: {agent.get_available_categories()}")
    print(f"选择统计: {stats}")

if __name__ == "__main__":
    test_dynamic_agent()