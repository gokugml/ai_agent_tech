# 动态工具选择模块
# 提供完整的动态工具选择和管理功能

from .tools import (
    tool_registry, 
    get_all_tools, 
    get_tools_by_category,
    get_available_categories,
    select_tools_for_query
)

from .tool_selector import AdvancedToolSelector

from .dynamic_agent import (
    DynamicToolAgent,
    build_dynamic_tool_agent,
    DynamicAgentState
)

__all__ = [
    # 工具注册表
    'tool_registry',
    'get_all_tools',
    'get_tools_by_category', 
    'get_available_categories',
    'select_tools_for_query',
    
    # 工具选择器
    'AdvancedToolSelector',
    
    # 动态代理
    'DynamicToolAgent',
    'build_dynamic_tool_agent',
    'DynamicAgentState'
]

__version__ = "1.0.0"
__author__ = "AI Agent Tech Team"
__description__ = "LangGraph动态工具选择系统，基于Manus模式实现"