# 工具定义和分类系统
# 采用前缀命名方式实现动态工具选择，保持KV缓存一致性

from typing import Dict, List, Any, Optional, Callable
from langchain.tools import tool
import json

# ============================================================================
# 1. 网络工具 (web_ prefix)
# ============================================================================

@tool
def web_search(query: str) -> str:
    """搜索网络信息"""
    return f"网络搜索结果: {query}"

@tool  
def web_scrape(url: str) -> str:
    """抓取网页内容"""
    return f"网页内容: {url}"

@tool
def web_download(url: str, path: str) -> str:
    """下载网络文件"""
    return f"已下载 {url} 到 {path}"

# ============================================================================
# 2. 金融工具 (finance_ prefix)
# ============================================================================

@tool
def finance_get_stock_price(symbol: str) -> str:
    """获取股票价格"""
    return f"股票 {symbol} 价格: $150.25"

@tool
def finance_get_fundamentals(symbol: str) -> str:
    """获取基本面数据"""
    return f"股票 {symbol} 基本面: PE比率25.5, 市值10亿"

@tool
def finance_calculate_returns(symbol: str, period: str) -> str:
    """计算收益率"""
    return f"股票 {symbol} {period} 收益率: 12.5%"

# ============================================================================
# 3. 代码工具 (code_ prefix)
# ============================================================================

@tool
def code_execute_python(code: str) -> str:
    """执行Python代码"""
    return f"代码执行结果: {code[:50]}..."

@tool
def code_generate_snippet(description: str, language: str) -> str:
    """生成代码片段"""
    return f"生成的{language}代码: {description}"

@tool
def code_analyze_complexity(code: str) -> str:
    """分析代码复杂度"""
    return f"代码复杂度分析: 时间复杂度O(n), 空间复杂度O(1)"

# ============================================================================
# 4. 文件工具 (file_ prefix)  
# ============================================================================

@tool
def file_read(path: str) -> str:
    """读取文件内容"""
    return f"文件内容: {path}"

@tool
def file_write(path: str, content: str) -> str:
    """写入文件内容"""
    return f"已写入文件: {path}"

@tool
def file_list_directory(path: str) -> str:
    """列出目录内容"""
    return f"目录 {path} 内容: file1.txt, file2.py, folder1/"

# ============================================================================
# 5. 数据库工具 (db_ prefix)
# ============================================================================

@tool
def db_query(sql: str) -> str:
    """执行数据库查询"""
    return f"查询结果: {sql[:30]}..."

@tool
def db_insert(table: str, data: dict) -> str:
    """插入数据"""
    return f"已插入数据到表 {table}: {data}"

@tool
def db_backup(database: str) -> str:
    """备份数据库"""
    return f"已备份数据库: {database}"

# ============================================================================
# 6. 图像工具 (image_ prefix)
# ============================================================================

@tool
def image_analyze(image_path: str) -> str:
    """分析图像内容"""
    return f"图像分析结果: {image_path} 包含人物、建筑物"

@tool
def image_resize(image_path: str, width: int, height: int) -> str:
    """调整图像尺寸"""
    return f"已调整 {image_path} 尺寸为 {width}x{height}"

@tool
def image_generate(prompt: str) -> str:
    """生成图像"""
    return f"已生成图像: {prompt}"

# ============================================================================
# 7. 邮件工具 (email_ prefix)
# ============================================================================

@tool
def email_send(to: str, subject: str, body: str) -> str:
    """发送邮件"""
    return f"已发送邮件到 {to}: {subject}"

@tool
def email_read_inbox() -> str:
    """读取收件箱"""
    return "收件箱: 3封未读邮件"

# ============================================================================
# 工具管理系统
# ============================================================================

class ToolRegistry:
    """工具注册表，管理所有可用工具"""
    
    def __init__(self):
        self.tools = {}
        self.categories = {}
        self._register_all_tools()
    
    def _register_all_tools(self):
        """注册所有工具"""
        # 获取所有工具函数
        all_tools = [
            # 网络工具
            web_search, web_scrape, web_download,
            # 金融工具  
            finance_get_stock_price, finance_get_fundamentals, finance_calculate_returns,
            # 代码工具
            code_execute_python, code_generate_snippet, code_analyze_complexity,
            # 文件工具
            file_read, file_write, file_list_directory,
            # 数据库工具
            db_query, db_insert, db_backup,
            # 图像工具
            image_analyze, image_resize, image_generate,
            # 邮件工具
            email_send, email_read_inbox
        ]
        
        # 按工具名注册
        for tool_func in all_tools:
            self.tools[tool_func.name] = tool_func
            
        # 按类别分组
        self._categorize_tools()
    
    def _categorize_tools(self):
        """按前缀自动分类工具"""
        self.categories = {}
        for tool_name, tool_func in self.tools.items():
            prefix = tool_name.split('_')[0]
            if prefix not in self.categories:
                self.categories[prefix] = {}
            self.categories[prefix][tool_name] = tool_func
    
    def get_all_tools(self) -> List[Any]:
        """获取所有工具列表"""
        return list(self.tools.values())
    
    def get_tools_by_category(self, category: str) -> List[Any]:
        """根据类别获取工具"""
        if category in self.categories:
            return list(self.categories[category].values())
        return []
    
    def get_tools_by_categories(self, categories: List[str]) -> List[Any]:
        """根据多个类别获取工具"""
        tools = []
        for category in categories:
            tools.extend(self.get_tools_by_category(category))
        return tools
    
    def get_available_categories(self) -> List[str]:
        """获取所有可用的工具类别"""
        return list(self.categories.keys())
    
    def get_category_info(self) -> Dict[str, Dict]:
        """获取类别信息"""
        info = {}
        for category, tools in self.categories.items():
            info[category] = {
                "count": len(tools),
                "tools": list(tools.keys()),
                "description": self._get_category_description(category)
            }
        return info
    
    def _get_category_description(self, category: str) -> str:
        """获取类别描述"""
        descriptions = {
            "web": "网络相关操作：搜索、抓取、下载",
            "finance": "金融数据处理：股价、基本面、收益分析",  
            "code": "代码处理：执行、生成、分析",
            "file": "文件操作：读取、写入、目录管理",
            "db": "数据库操作：查询、插入、备份",
            "image": "图像处理：分析、调整、生成",
            "email": "邮件管理：发送、接收"
        }
        return descriptions.get(category, f"{category}相关工具")

# ============================================================================
# 工具选择策略
# ============================================================================

class ToolSelector:
    """工具选择器，实现不同的选择策略"""
    
    def __init__(self, tool_registry: ToolRegistry):
        self.registry = tool_registry
    
    def select_by_keywords(self, query: str) -> List[str]:
        """基于关键词匹配选择工具类别"""
        query_lower = query.lower()
        selected_categories = []
        
        # 定义关键词映射
        keyword_mappings = {
            "web": ["search", "web", "网络", "搜索", "查找", "scrape", "抓取", "download", "下载"],
            "finance": ["stock", "price", "finance", "股票", "价格", "金融", "投资", "收益", "基本面"],
            "code": ["code", "python", "execute", "代码", "执行", "编程", "script", "脚本"],
            "file": ["file", "read", "write", "文件", "读取", "写入", "directory", "目录"],
            "db": ["database", "sql", "query", "数据库", "查询", "插入", "backup", "备份"],
            "image": ["image", "picture", "photo", "图像", "图片", "analyze", "分析", "resize"],
            "email": ["email", "mail", "邮件", "发送", "收件箱", "inbox"]
        }
        
        # 匹配关键词
        for category, keywords in keyword_mappings.items():
            if any(keyword in query_lower for keyword in keywords):
                selected_categories.append(category)
        
        # 如果没有匹配到，返回默认类别
        if not selected_categories:
            selected_categories = ["web", "finance"]  # 默认类别
            
        return selected_categories
    
    def select_by_context(self, query: str, conversation_state: Dict[str, Any]) -> List[str]:
        """基于上下文选择工具类别"""
        # 先用关键词匹配
        categories = self.select_by_keywords(query)
        
        # 根据对话状态调整
        if conversation_state.get("has_data"):
            if "code" not in categories:
                categories.append("code")
        
        if conversation_state.get("needs_file_ops"):
            if "file" not in categories:
                categories.append("file")
                
        if conversation_state.get("working_with_images"):
            if "image" not in categories:
                categories.append("image")
        
        return categories
    
    def select_by_llm(self, query: str, available_categories: List[str]) -> List[str]:
        """使用LLM选择最相关的工具类别"""
        # 这里可以集成真实的LLM调用
        # 为演示目的，使用简化的逻辑
        
        # 构建提示
        categories_info = self.registry.get_category_info()
        categories_desc = "\n".join([
            f"- {cat}: {info['description']}" 
            for cat, info in categories_info.items() 
            if cat in available_categories
        ])
        
        prompt = f"""
根据用户查询选择最相关的工具类别。

用户查询: {query}

可用类别:
{categories_desc}

请返回1-3个最相关的类别名称，用逗号分隔。
"""
        
        # 模拟LLM响应（实际应该调用真实的LLM）
        return self.select_by_keywords(query)  # 回退到关键词匹配

# ============================================================================
# 导出接口
# ============================================================================

# 全局工具注册表实例
tool_registry = ToolRegistry()
tool_selector = ToolSelector(tool_registry)

def get_all_tools() -> List[Any]:
    """获取所有工具"""
    return tool_registry.get_all_tools()

def get_tools_by_category(category: str) -> List[Any]:
    """根据类别获取工具"""
    return tool_registry.get_tools_by_category(category)

def get_available_categories() -> List[str]:
    """获取可用类别"""
    return tool_registry.get_available_categories()

def select_tools_for_query(query: str, method: str = "keywords", **kwargs) -> List[Any]:
    """为查询选择合适的工具"""
    if method == "keywords":
        categories = tool_selector.select_by_keywords(query)
    elif method == "context":
        categories = tool_selector.select_by_context(query, kwargs.get("conversation_state", {}))
    elif method == "llm":
        categories = tool_selector.select_by_llm(query, kwargs.get("available_categories", get_available_categories()))
    else:
        categories = ["web", "finance"]  # 默认
    
    return tool_registry.get_tools_by_categories(categories), categories

if __name__ == "__main__":
    # 测试工具系统
    print("=== 工具系统测试 ===")
    
    # 测试工具注册
    print(f"总工具数: {len(get_all_tools())}")
    print(f"可用类别: {get_available_categories()}")
    
    # 测试类别信息
    for category, info in tool_registry.get_category_info().items():
        print(f"{category}: {info['count']}个工具 - {info['description']}")
    
    # 测试工具选择
    test_queries = [
        "查询苹果股价",
        "搜索AI新闻", 
        "执行Python代码",
        "分析这张图片",
        "发送邮件给客户"
    ]
    
    print("\n=== 工具选择测试 ===")
    for query in test_queries:
        tools, categories = select_tools_for_query(query)
        print(f"查询: {query}")
        print(f"选择类别: {categories}")
        print(f"可用工具: {[t.name for t in tools]}")
        print("-" * 40)