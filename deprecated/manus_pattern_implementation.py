# Manus "遮蔽，而非移除" 设计模式在 LangChain & LangGraph 中的实现
# 基于 https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus

"""
核心理念：
1. 保持所有工具定义不变（避免KV缓存失效）
2. 通过logits掩蔽和响应预填充约束工具选择
3. 使用一致的工具命名前缀实现分类
4. 状态机驱动的工具可用性管理
"""

from typing import TypedDict, List, Dict, Optional
from langchain.tools import tool
from langchain.chat_models import init_chat_model
from langchain.schema.runnable import RunnableLambda
from langgraph.graph import StateGraph, END
import re

from user_config import settings


# ============================================================================
# 1. 工具分类与命名规范
# ============================================================================

@tool
def web_search(query: str) -> str:
    """搜索网络信息"""
    # 实现网络搜索逻辑
    return f"搜索结果：{query}"

@tool
def web_scrape(url: str) -> str:
    """抓取网页内容"""
    # 实现网页抓取逻辑
    return f"网页内容：{url}"

@tool
def finance_get_stock_price(symbol: str) -> float:
    """获取股票价格"""
    # 实现股价获取逻辑
    return 150.25

@tool
def finance_get_fundamentals(symbol: str) -> dict:
    """获取基本面数据"""
    # 实现基本面数据获取逻辑
    return {"pe_ratio": 25.5, "market_cap": 1000000000}

@tool
def code_execute_python(code: str) -> str:
    """执行Python代码"""
    # 实现代码执行逻辑
    return f"执行结果：{code}"

@tool
def file_read(path: str) -> str:
    """读取文件内容"""
    # 实现文件读取逻辑
    return f"文件内容：{path}"

@tool
def file_write(path: str, content: str) -> str:
    """写入文件内容"""
    # 实现文件写入逻辑
    return f"已写入文件：{path}"


# ============================================================================
# 2. LangChain 实现
# ============================================================================

class ContextAwareToolManager:
    """状态感知的工具管理器"""
    
    def __init__(self, all_tools):
        self.all_tools = all_tools
        self.tool_categories = self._categorize_tools(all_tools)
    
    def _categorize_tools(self, tools):
        """按前缀自动分类工具"""
        categories = {}
        for tool in tools:
            prefix = tool.name.split('_')[0]
            if prefix not in categories:
                categories[prefix] = []
            categories[prefix].append(tool)
        return categories
    
    def get_tools_for_context(self, user_query: str, conversation_state: dict):
        """根据查询内容和对话状态返回相关工具类别"""
        available_tools = self.all_tools.copy()  # 保持完整工具定义
        
        # 基于查询内容推断需要的工具类别
        relevant_categories = self._analyze_query_intent(user_query)
        
        # 根据对话状态调整
        if conversation_state.get('has_data'):
            relevant_categories.append('code')
        
        if conversation_state.get('needs_file_ops'):
            relevant_categories.append('file')
            
        return available_tools, relevant_categories
    
    def _analyze_query_intent(self, query: str) -> List[str]:
        """分析查询意图，返回相关工具类别"""
        query_lower = query.lower()
        categories = []
        
        if any(keyword in query_lower for keyword in ['stock', 'price', 'finance', '股票', '价格']):
            categories.append('finance')
        if any(keyword in query_lower for keyword in ['search', 'web', 'find', '搜索', '查找']):
            categories.append('web')
        if any(keyword in query_lower for keyword in ['code', 'python', 'execute', '代码', '执行']):
            categories.append('code')
        if any(keyword in query_lower for keyword in ['file', 'read', 'write', '文件', '读取', '写入']):
            categories.append('file')
            
        # 默认可用类别
        if not categories:
            categories = ['web', 'finance']
            
        return categories


class ConstrainedToolAgent:
    """使用约束工具选择的代理"""
    
    def __init__(self, model, tool_manager):
        self.model = model
        self.tool_manager = tool_manager
        
    def _constrain_tool_selection(self, tools, allowed_categories):
        """通过系统提示约束工具选择，而非移除工具定义"""
        
        if len(allowed_categories) == 1:
            constraint = f"你必须只使用以 '{allowed_categories[0]}_' 开头的工具"
        else:
            prefixes = "', '".join([f"{cat}_" for cat in allowed_categories])
            constraint = f"你必须只使用以下前缀开头的工具：'{prefixes}'"
            
        return constraint
    
    def _create_prefilled_response(self, mode: str, categories: List[str] = None) -> str:
        """创建预填充响应，控制工具调用模式"""
        
        if mode == "auto":
            # 自动模式：模型可以选择是否调用工具
            return ""
        elif mode == "required":
            # 必需模式：必须调用工具
            return "<tool_call>"
        elif mode == "specific" and categories and len(categories) == 1:
            # 指定模式：必须调用特定类别的工具
            category = categories[0]
            return f'<tool_call>{{"name": "{category}_'
        
        return ""
    
    def invoke(self, user_input: str, conversation_state: dict = None, mode: str = "auto"):
        """调用代理，使用Manus模式的工具约束"""
        
        if conversation_state is None:
            conversation_state = {}
            
        tools, allowed_categories = self.tool_manager.get_tools_for_context(
            user_input, conversation_state
        )
        
        # 保持所有工具定义，但添加使用约束
        constraint = self._constrain_tool_selection(tools, allowed_categories)
        
        # 创建响应预填充
        prefill = self._create_prefilled_response(mode, allowed_categories)
        
        system_prompt = f"""
你是一个AI助手，可以使用以下工具：{[t.name for t in tools]}

约束条件：{constraint}

工具调用格式：
<tool_call>
{{"name": "工具名", "arguments": {{"参数": "值"}}}}
</tool_call>

使用工具来帮助回答用户的查询。
        """
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]
        
        # 如果有预填充，添加到助手消息
        if prefill:
            messages.append({"role": "assistant", "content": prefill})
        
        # 使用完整工具集，但通过提示词约束选择
        return self.model.bind(tools=tools).invoke(messages)


# ============================================================================
# 3. LangGraph 实现
# ============================================================================

class AgentState(TypedDict):
    """代理状态定义"""
    messages: List[dict]
    available_tool_categories: List[str]
    context_stage: str
    has_data: bool
    needs_file_ops: bool
    user_query: str


def get_all_tools():
    """获取所有可用工具"""
    return [
        web_search, web_scrape,
        finance_get_stock_price, finance_get_fundamentals,
        code_execute_python,
        file_read, file_write
    ]


def determine_tool_categories(state: AgentState) -> AgentState:
    """根据当前状态确定可用工具类别"""
    
    user_query = state.get("user_query", "")
    last_message = state["messages"][-1]["content"] if state["messages"] else ""
    
    # 分析查询内容
    tool_manager = ContextAwareToolManager(get_all_tools())
    _, categories = tool_manager.get_tools_for_context(
        user_query or last_message, 
        {
            "has_data": state.get("has_data", False),
            "needs_file_ops": state.get("needs_file_ops", False)
        }
    )
    
    # 根据上下文阶段调整
    if state.get("context_stage") == "initial":
        # 初始阶段，限制工具类别
        pass
    elif state.get("has_data"):
        # 有数据后可以使用代码工具
        if "code" not in categories:
            categories.append("code")
    
    return {
        **state,
        "available_tool_categories": categories
    }


def constrained_tool_call(state: AgentState) -> AgentState:
    """使用约束的工具调用"""
    
    # 获取所有工具但只允许特定类别
    all_tools = get_all_tools()
    allowed_categories = state.get("available_tool_categories", [])
    
    # 构建约束提示（遮蔽而非移除）
    if allowed_categories:
        category_constraint = f"只能使用以下前缀开头的工具：{', '.join([f'{cat}_' for cat in allowed_categories])}"
    else:
        category_constraint = "可以使用所有可用工具"
    
    # 确定调用模式
    mode = "auto"
    if state.get("force_tool_use"):
        mode = "required"
    elif len(allowed_categories) == 1 and state.get("specific_tool_needed"):
        mode = "specific"
    
    # 创建预填充响应
    model = init_chat_model(
        model="google_genai:gemini-2.5-flash",
        api_key=settings.GOOGLE_API_KEY,
        temperature=0.3,
    )
    agent = ConstrainedToolAgent(model, ContextAwareToolManager(all_tools))
    response = agent.invoke(state.get("user_query", ""))
    prefill = agent._create_prefilled_response(mode, allowed_categories)
    
    system_message = f"""
你是一个AI助手，可以使用工具来帮助用户。

可用工具类别约束：{category_constraint}

工具调用格式：
<tool_call>
{{"name": "工具名", "arguments": {{"参数": "值"}}}}
</tool_call>
    """
    
    # 构建消息，包含预填充
    messages = [{"role": "system", "content": system_message}] + state["messages"]
    if prefill:
        messages.append({"role": "assistant", "content": prefill})
    
    # 这里应该调用实际的模型
    
    
    # 模拟响应
    # response = {"role": "assistant", "content": "模拟的工具调用响应"}
    
    return {
        **state,
        "messages": state["messages"] + [response]
    }


def execute_tool_calls(state: AgentState) -> AgentState:
    """执行工具调用"""
    
    last_message = state["messages"][-1]
    
    # 这里应该解析和执行实际的工具调用
    # 模拟工具执行结果
    tool_response = {"role": "tool", "content": "工具执行结果"}
    
    # 更新状态
    new_state = {
        **state,
        "messages": state["messages"] + [tool_response],
        "has_data": True  # 标记已有数据
    }
    
    return new_state


def should_continue(state: AgentState) -> str:
    """判断是否应该继续执行"""
    
    last_message = state["messages"][-1]
    
    # 如果最后一条消息包含工具调用，继续执行
    if "<tool_call>" in last_message.get("content", ""):
        return "execute_tools"
    
    # 如果需要更多工具调用，继续
    if state.get("needs_more_tools", False):
        return "determine_tools"
    
    # 否则结束
    return "end"


def build_manus_pattern_agent():
    """构建采用 Manus 模式的 LangGraph 代理"""
    
    # 定义状态图
    workflow = StateGraph(AgentState)
    
    # 添加节点
    workflow.add_node("determine_tools", determine_tool_categories)
    workflow.add_node("tool_call", constrained_tool_call)
    workflow.add_node("execute_tools", execute_tool_calls)
    
    # 设置入口点
    workflow.set_entry_point("determine_tools")
    
    # 添加边
    workflow.add_edge("determine_tools", "tool_call")
    workflow.add_edge("tool_call", "execute_tools")
    
    # 添加条件边
    workflow.add_conditional_edges(
        "execute_tools",
        should_continue,
        {
            "execute_tools": "execute_tools",
            "determine_tools": "determine_tools", 
            "end": END
        }
    )
    
    return workflow.compile()


# ============================================================================
# 4. 使用示例
# ============================================================================

def langchain_example():
    """LangChain 实现示例"""
    
    # 初始化工具管理器和代理
    all_tools = get_all_tools()
    tool_manager = ContextAwareToolManager(all_tools)
    model = init_chat_model(
        model="google_genai:gemini-2.5-flash",
        api_key=settings.GOOGLE_API_KEY,
        temperature=0.3,
    )
    agent = ConstrainedToolAgent(model, tool_manager)
    
    # 示例1：自动模式
    print("=== LangChain 自动模式 ===")
    result1 = agent.invoke(
        "请帮我查询特斯拉的股价",
        conversation_state={},
        mode="auto"
    )
    print(f"结果: {result1}")
    
    # 示例2：必需模式（强制使用工具）
    print("\n=== LangChain 必需模式 ===")
    result2 = agent.invoke(
        "分析这些数据",
        conversation_state={"has_data": True},
        mode="required"
    )
    print(f"结果: {result2}")
    
    # 示例3：指定模式（只能使用特定类别工具）
    print("\n=== LangChain 指定模式 ===")
    result3 = agent.invoke(
        "搜索最新的AI新闻",
        conversation_state={},
        mode="specific"
    )
    print(f"结果: {result3}")


def langgraph_example():
    """LangGraph 实现示例"""
    
    print("\n=== LangGraph 状态机示例 ===")
    
    # 构建代理
    agent = build_manus_pattern_agent()
    
    # 初始状态
    initial_state = {
        "messages": [{"role": "user", "content": "请帮我查询苹果公司的股价和基本面数据"}],
        "available_tool_categories": [],
        "context_stage": "initial",
        "has_data": False,
        "needs_file_ops": False,
        "user_query": "请帮我查询苹果公司的股价和基本面数据"
    }
    
    # 执行代理
    try:
        result = agent.invoke(initial_state)
        print(f"最终结果: {result}")
    except Exception as e:
        print(f"执行出错: {e}")


def main():
    """主函数，演示两种实现方式"""
    
    print("Manus '遮蔽，而非移除' 设计模式实现示例")
    print("=" * 50)
    
    # LangChain 实现示例
    langchain_example()
    
    # LangGraph 实现示例  
    langgraph_example()
    
    print("\n" + "=" * 50)
    print("核心优势：")
    print("1. KV缓存友好：工具定义始终保持不变")
    print("2. 状态一致性：之前的工具调用引用保持有效")
    print("3. 灵活约束：通过提示词和预填充实现精确控制")
    print("4. 可扩展性：新工具只需遵循命名规范即可自动分类")


if __name__ == "__main__":
    main()


# ============================================================================
# 5. 高级特性
# ============================================================================

class AdvancedManusPattern:
    """高级Manus模式实现"""
    
    def __init__(self):
        self.tool_usage_history = []
        self.context_memory = {}
    
    def adaptive_tool_selection(self, state: AgentState) -> List[str]:
        """基于历史使用情况自适应选择工具类别"""
        
        # 分析工具使用模式
        recent_tools = self.tool_usage_history[-5:]  # 最近5次使用
        frequent_categories = self._get_frequent_categories(recent_tools)
        
        # 结合当前上下文
        current_categories = determine_tool_categories(state)["available_tool_categories"]
        
        # 智能合并
        optimized_categories = self._merge_categories(frequent_categories, current_categories)
        
        return optimized_categories
    
    def _get_frequent_categories(self, recent_tools: List[str]) -> List[str]:
        """获取最常使用的工具类别"""
        category_count = {}
        for tool in recent_tools:
            category = tool.split('_')[0] if '_' in tool else 'unknown'
            category_count[category] = category_count.get(category, 0) + 1
        
        # 返回使用频率最高的类别
        return sorted(category_count.keys(), key=lambda x: category_count[x], reverse=True)
    
    def _merge_categories(self, frequent: List[str], current: List[str]) -> List[str]:
        """智能合并工具类别"""
        # 优先考虑当前上下文，但参考历史偏好
        merged = list(set(current + frequent[:2]))  # 最多添加2个历史偏好类别
        return merged
    
    def dynamic_constraint_generation(self, categories: List[str], confidence: float) -> str:
        """动态生成约束提示"""
        
        if confidence > 0.8:
            # 高置信度：强约束
            return f"严格限制：只能使用 {', '.join([f'{cat}_' for cat in categories])} 类别的工具"
        elif confidence > 0.5:
            # 中等置信度：软约束
            return f"建议优先使用 {', '.join([f'{cat}_' for cat in categories])} 类别的工具，必要时可使用其他工具"
        else:
            # 低置信度：宽松约束
            return "可以使用任何合适的工具来完成任务"


# ============================================================================
# 6. 测试与验证
# ============================================================================

def test_tool_categorization():
    """测试工具分类功能"""
    
    tools = get_all_tools()
    manager = ContextAwareToolManager(tools)
    
    test_cases = [
        ("查询特斯拉股价", ["finance"]),
        ("搜索AI新闻", ["web"]),
        ("执行Python代码", ["code"]),
        ("股价分析和网络搜索", ["finance", "web"]),
    ]
    
    print("=== 工具分类测试 ===")
    for query, expected in test_cases:
        _, categories = manager.get_tools_for_context(query, {})
        print(f"查询: {query}")
        print(f"期望类别: {expected}")
        print(f"实际类别: {categories}")
        print(f"匹配: {set(expected).issubset(set(categories))}")
        print("-" * 30)


def test_constraint_generation():
    """测试约束生成功能"""
    
    agent = ConstrainedToolAgent(None, None)
    
    test_cases = [
        (["finance"], "你必须只使用以 'finance_' 开头的工具"),
        (["web", "code"], "你必须只使用以下前缀开头的工具：'web_', 'code_'"),
    ]
    
    print("=== 约束生成测试 ===")
    for categories, expected in test_cases:
        constraint = agent._constrain_tool_selection([], categories)
        print(f"类别: {categories}")
        print(f"约束: {constraint}")
        print(f"匹配: {expected in constraint}")
        print("-" * 30)


if __name__ == "__main__":
    # 运行测试
    test_tool_categorization()
    test_constraint_generation()
    
    # 运行主示例
    main()