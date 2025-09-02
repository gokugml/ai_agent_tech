# 工具选择器 - 实现多种选择策略
# 支持关键词匹配、上下文分析、LLM选择等方式

from typing import List, Dict, Any, Optional, Tuple
from langchain.chat_models import init_chat_model
from tools import tool_registry, ToolRegistry
from user_config import settings
import json
import re

class AdvancedToolSelector:
    """高级工具选择器，支持多种选择策略"""
    
    def __init__(self, tool_registry: ToolRegistry):
        self.registry = tool_registry
        self.selection_history = []  # 历史选择记录
        self.user_preferences = {}   # 用户偏好
        
        # 初始化LLM（如果需要）
        try:
            self.llm = init_chat_model(
                model="google_genai:gemini-2.5-flash",
                api_key=settings.GOOGLE_API_KEY,
                temperature=0.1,  # 低温度保证选择一致性
            )
        except:
            self.llm = None
            print("LLM初始化失败，将使用规则基础选择")
    
    def select_tools(self, 
                    query: str, 
                    method: str = "hybrid",
                    conversation_state: Optional[Dict[str, Any]] = None,
                    max_categories: int = 3) -> Tuple[List[Any], List[str], float]:
        """
        选择工具的主入口函数
        
        Args:
            query: 用户查询
            method: 选择方法 ("keywords", "context", "llm", "hybrid")
            conversation_state: 对话状态
            max_categories: 最大类别数
            
        Returns:
            (selected_tools, selected_categories, confidence_score)
        """
        
        if method == "keywords":
            return self._select_by_keywords(query, max_categories)
        elif method == "context":
            return self._select_by_context(query, conversation_state or {}, max_categories)
        elif method == "llm":
            return self._select_by_llm(query, max_categories)
        elif method == "hybrid":
            return self._select_by_hybrid(query, conversation_state or {}, max_categories)
        else:
            # 默认回退到关键词匹配
            return self._select_by_keywords(query, max_categories)
    
    def _select_by_keywords(self, query: str, max_categories: int) -> Tuple[List[Any], List[str], float]:
        """基于关键词匹配选择工具"""
        
        query_lower = query.lower()
        category_scores = {}
        
        # 详细的关键词映射，包含权重
        keyword_mappings = {
            "web": {
                "high": ["search", "搜索", "find", "查找", "google", "百度"],
                "medium": ["web", "网络", "internet", "online", "scrape", "抓取"],
                "low": ["download", "下载", "fetch", "获取"]
            },
            "finance": {
                "high": ["stock", "股票", "price", "价格", "finance", "金融"],
                "medium": ["investment", "投资", "market", "市场", "trading", "交易"],
                "low": ["money", "钱", "profit", "利润", "return", "收益"]
            },
            "code": {
                "high": ["code", "代码", "python", "programming", "编程"],
                "medium": ["execute", "执行", "run", "运行", "script", "脚本"],
                "low": ["function", "函数", "class", "类", "algorithm", "算法"]
            },
            "file": {
                "high": ["file", "文件", "read", "读取", "write", "写入"],
                "medium": ["save", "保存", "load", "加载", "path", "路径"],
                "low": ["directory", "目录", "folder", "文件夹"]
            },
            "db": {
                "high": ["database", "数据库", "sql", "query", "查询"],
                "medium": ["table", "表", "record", "记录", "data", "数据"],
                "low": ["insert", "插入", "update", "更新", "delete", "删除"]
            },
            "image": {
                "high": ["image", "图像", "picture", "图片", "photo", "照片"],
                "medium": ["analyze", "分析", "resize", "调整", "edit", "编辑"],
                "low": ["generate", "生成", "create", "创建"]
            },
            "email": {
                "high": ["email", "邮件", "mail", "send", "发送"],
                "medium": ["inbox", "收件箱", "message", "消息"],
                "low": ["reply", "回复", "forward", "转发"]
            }
        }
        
        # 计算每个类别的得分
        for category, keyword_groups in keyword_mappings.items():
            score = 0
            for priority, keywords in keyword_groups.items():
                weight = {"high": 3, "medium": 2, "low": 1}[priority]
                matches = sum(1 for keyword in keywords if keyword in query_lower)
                score += matches * weight
            
            if score > 0:
                category_scores[category] = score
        
        # 如果没有匹配，使用默认类别
        if not category_scores:
            category_scores = {"web": 1, "finance": 1}
        
        # 按得分排序并限制数量
        sorted_categories = sorted(category_scores.items(), key=lambda x: x[1], reverse=True)
        selected_categories = [cat for cat, score in sorted_categories[:max_categories]]
        
        # 计算置信度
        total_score = sum(category_scores.values())
        max_score = max(category_scores.values()) if category_scores else 1
        confidence = min(max_score / max(total_score, 1), 1.0) * 0.8  # 关键词匹配的最高置信度是0.8
        
        # 获取对应的工具
        selected_tools = self.registry.get_tools_by_categories(selected_categories)
        
        return selected_tools, selected_categories, confidence
    
    def _select_by_context(self, query: str, conversation_state: Dict[str, Any], max_categories: int) -> Tuple[List[Any], List[str], float]:
        """基于上下文选择工具"""
        
        # 先用关键词匹配作为基础
        base_tools, base_categories, base_confidence = self._select_by_keywords(query, max_categories)
        
        # 根据对话状态调整
        context_adjustments = []
        
        if conversation_state.get("has_data", False):
            context_adjustments.append("code")
        
        if conversation_state.get("needs_file_ops", False):
            context_adjustments.append("file")
            
        if conversation_state.get("working_with_images", False):
            context_adjustments.append("image")
            
        if conversation_state.get("database_session", False):
            context_adjustments.append("db")
            
        if conversation_state.get("email_context", False):
            context_adjustments.append("email")
        
        # 合并类别，优先保留基础类别
        adjusted_categories = base_categories.copy()
        for adj_cat in context_adjustments:
            if adj_cat not in adjusted_categories and len(adjusted_categories) < max_categories:
                adjusted_categories.append(adj_cat)
        
        # 如果有上下文调整，提高置信度
        confidence_boost = min(len(context_adjustments) * 0.1, 0.2)
        final_confidence = min(base_confidence + confidence_boost, 0.95)
        
        # 获取调整后的工具
        final_tools = self.registry.get_tools_by_categories(adjusted_categories)
        
        return final_tools, adjusted_categories, final_confidence
    
    def _select_by_llm(self, query: str, max_categories: int) -> Tuple[List[Any], List[str], float]:
        """使用LLM选择工具类别"""
        
        if not self.llm:
            # LLM不可用，回退到关键词匹配
            return self._select_by_keywords(query, max_categories)
        
        # 构建LLM提示
        available_categories = self.registry.get_available_categories()
        category_info = self.registry.get_category_info()
        
        categories_desc = "\\n".join([
            f"- {cat}: {info['description']} (包含工具: {', '.join(info['tools'][:3])}{'...' if len(info['tools']) > 3 else ''})"
            for cat, info in category_info.items()
        ])
        
        prompt = f"""根据用户查询，从可用的工具类别中选择最相关的1-{max_categories}个类别。

用户查询: {query}

可用工具类别:
{categories_desc}

请返回JSON格式的响应，包含:
1. selected_categories: 选中的类别列表
2. confidence: 选择置信度 (0-1)
3. reasoning: 选择理由

示例:
{{
    "selected_categories": ["web", "finance"],
    "confidence": 0.85,
    "reasoning": "查询涉及搜索股票信息，需要网络搜索和金融工具"
}}"""

        try:
            # 调用LLM
            response = self.llm.invoke([{"role": "user", "content": prompt}])
            response_content = response.content
            
            # 解析JSON响应
            # 提取JSON部分（处理LLM可能返回额外文本的情况）
            json_match = re.search(r'\\{[^}]*"selected_categories"[^}]*\\}', response_content, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                result = json.loads(json_str)
                
                selected_categories = result.get("selected_categories", [])
                confidence = result.get("confidence", 0.5)
                reasoning = result.get("reasoning", "")
                
                # 验证类别有效性
                valid_categories = [cat for cat in selected_categories if cat in available_categories]
                if not valid_categories:
                    # 如果没有有效类别，回退到关键词匹配
                    return self._select_by_keywords(query, max_categories)
                
                # 限制类别数量
                final_categories = valid_categories[:max_categories]
                final_tools = self.registry.get_tools_by_categories(final_categories)
                
                return final_tools, final_categories, min(confidence, 0.95)
                
        except Exception as e:
            print(f"LLM选择失败: {e}")
        
        # 出错时回退到关键词匹配
        return self._select_by_keywords(query, max_categories)
    
    def _select_by_hybrid(self, query: str, conversation_state: Dict[str, Any], max_categories: int) -> Tuple[List[Any], List[str], float]:
        """混合策略：结合多种选择方法"""
        
        # 1. 获取关键词匹配结果
        keyword_tools, keyword_categories, keyword_confidence = self._select_by_keywords(query, max_categories)
        
        # 2. 获取上下文增强结果  
        context_tools, context_categories, context_confidence = self._select_by_context(query, conversation_state, max_categories)
        
        # 3. 如果LLM可用，获取LLM结果
        llm_categories = []
        llm_confidence = 0
        if self.llm:
            try:
                llm_tools, llm_categories, llm_confidence = self._select_by_llm(query, max_categories)
            except:
                pass
        
        # 4. 融合结果
        # 创建类别得分字典
        category_scores = {}
        
        # 关键词结果权重40%
        for cat in keyword_categories:
            category_scores[cat] = category_scores.get(cat, 0) + keyword_confidence * 0.4
        
        # 上下文结果权重35%
        for cat in context_categories:
            category_scores[cat] = category_scores.get(cat, 0) + context_confidence * 0.35
            
        # LLM结果权重25%（如果可用）
        if llm_categories:
            for cat in llm_categories:
                category_scores[cat] = category_scores.get(cat, 0) + llm_confidence * 0.25
        
        # 5. 选择得分最高的类别
        if not category_scores:
            # 如果没有结果，使用默认
            return self._select_by_keywords(query, max_categories)
        
        sorted_categories = sorted(category_scores.items(), key=lambda x: x[1], reverse=True)
        final_categories = [cat for cat, score in sorted_categories[:max_categories]]
        
        # 6. 计算综合置信度
        final_confidence = min(sum(score for cat, score in sorted_categories[:max_categories]) / max_categories, 0.95)
        
        # 7. 获取最终工具集
        final_tools = self.registry.get_tools_by_categories(final_categories)
        
        return final_tools, final_categories, final_confidence
    
    def update_selection_history(self, query: str, selected_categories: List[str], user_feedback: Optional[str] = None):
        """更新选择历史记录"""
        
        history_entry = {
            "query": query,
            "selected_categories": selected_categories,
            "timestamp": None,  # 实际使用时应该添加时间戳
            "user_feedback": user_feedback
        }
        
        self.selection_history.append(history_entry)
        
        # 保持历史记录大小限制
        if len(self.selection_history) > 100:
            self.selection_history = self.selection_history[-100:]
    
    def analyze_user_preferences(self) -> Dict[str, float]:
        """分析用户偏好"""
        
        if not self.selection_history:
            return {}
        
        category_usage = {}
        total_selections = len(self.selection_history)
        
        for entry in self.selection_history:
            for category in entry["selected_categories"]:
                category_usage[category] = category_usage.get(category, 0) + 1
        
        # 计算偏好权重
        preferences = {}
        for category, count in category_usage.items():
            preferences[category] = count / total_selections
            
        return preferences
    
    def get_selection_statistics(self) -> Dict[str, Any]:
        """获取选择统计信息"""
        
        if not self.selection_history:
            return {"total_selections": 0}
        
        stats = {
            "total_selections": len(self.selection_history),
            "category_usage": {},
            "user_preferences": self.analyze_user_preferences(),
            "recent_categories": []
        }
        
        # 统计类别使用情况
        for entry in self.selection_history:
            for category in entry["selected_categories"]:
                stats["category_usage"][category] = stats["category_usage"].get(category, 0) + 1
        
        # 最近的类别（最后10次选择）
        recent_entries = self.selection_history[-10:]
        recent_categories = []
        for entry in recent_entries:
            recent_categories.extend(entry["selected_categories"])
        
        stats["recent_categories"] = list(set(recent_categories))
        
        return stats

# ============================================================================
# 使用示例和测试
# ============================================================================

def test_tool_selector():
    """测试工具选择器的各种功能"""
    
    selector = AdvancedToolSelector(tool_registry)
    
    test_cases = [
        {
            "query": "查询苹果公司的股价",
            "method": "keywords",
            "expected_categories": ["finance"]
        },
        {
            "query": "搜索最新的AI新闻", 
            "method": "keywords",
            "expected_categories": ["web"]
        },
        {
            "query": "执行这段Python代码并保存结果",
            "method": "context",
            "conversation_state": {"has_data": True},
            "expected_categories": ["code", "file"]
        },
        {
            "query": "分析用户数据库中的用户行为",
            "method": "hybrid",
            "conversation_state": {"database_session": True},
            "expected_categories": ["db", "code"]
        }
    ]
    
    print("=== 工具选择器测试 ===")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\\n测试用例 {i}:")
        print(f"查询: {test_case['query']}")
        print(f"方法: {test_case['method']}")
        
        tools, categories, confidence = selector.select_tools(
            query=test_case["query"],
            method=test_case["method"],
            conversation_state=test_case.get("conversation_state", {}),
            max_categories=3
        )
        
        print(f"选择的类别: {categories}")
        print(f"置信度: {confidence:.2f}")
        print(f"工具数量: {len(tools)}")
        print(f"工具名称: {[t.name for t in tools[:5]]}{'...' if len(tools) > 5 else ''}")
        
        # 更新历史记录
        selector.update_selection_history(test_case["query"], categories)
    
    # 显示统计信息
    print("\\n=== 选择统计 ===")
    stats = selector.get_selection_statistics()
    print(f"总选择次数: {stats['total_selections']}")
    print(f"类别使用统计: {stats['category_usage']}")
    print(f"用户偏好: {stats['user_preferences']}")

if __name__ == "__main__":
    test_tool_selector()