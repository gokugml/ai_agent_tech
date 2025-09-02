"""
Memu记忆系统能力评测主程序

基于LangChain和Memu，对不同场景下的记忆能力进行定量评测
"""

import os
import sys
from typing import Dict, List, Any, Tuple
from datetime import datetime
import json

# 添加项目根目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../../fortunetelling_memory_test'))

from memu import MemuClient
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage

from test_memory.chats import chats
from test_memory.test_case import test_cases
from user_config import settings


class MemuEvaluator:
    """Memu记忆系统评测器"""
    
    def __init__(self):
        # 从fortunetelling_memory_test项目获取Memu配置
        try:
            from fortunetelling_memory_test.src.config import settings as ft_settings
            
            # 初始化Memu客户端
            self.memu_client = MemuClient(
                base_url=ft_settings.MEMU_BASE_URL,
                api_key=ft_settings.MEMU_API_KEY
            )
            self.memu_settings = ft_settings
        except ImportError:
            # 使用默认配置
            self.memu_client = MemuClient(
                base_url="https://api.memu.so",
                api_key=os.getenv("MEMU_API_KEY")
            )
            self.memu_settings = None
        
        # 初始化Claude模型用于评分
        self.claude_model = ChatAnthropic(
            model="claude-3-5-sonnet-20241022",
            api_key=settings.ANTHROPIC_API_KEY.get_secret_value()
        )
        
        self.user_id = "test_memu_evaluation_001"
        self.agent_id = "test_chatbot"
        self.agent_name = "Test ChatBot"
        self.evaluation_results: List[Dict[str, Any]] = []
    
    def setup_test_data(self) -> None:
        """设置测试数据并存储到Memu"""
        print("🔧 设置Memu测试数据...")
        
        try:
            # 将测试聊天数据存储到Memu
            conversation_pairs = []
            
            # 将chats转换为对话对格式
            for i in range(0, len(chats), 2):
                if i + 1 < len(chats):
                    user_msg = chats[i]
                    assistant_msg = chats[i + 1]
                    
                    if user_msg["role"] == "user" and assistant_msg["role"] == "assistant":
                        conversation_text = f"user: {user_msg['content']}\n\nassistant: {assistant_msg['content']}"
                        conversation_pairs.append(conversation_text)
            
            print(f"📝 准备存储 {len(conversation_pairs)} 对对话到Memu...")
            
            # 存储每个对话对到Memu
            for idx, conversation in enumerate(conversation_pairs):
                self.memu_client.memorize_conversation(
                    conversation=conversation,
                    user_id=self.user_id,
                    user_name="测试用户",
                    agent_id=self.agent_id,
                    agent_name=self.agent_name,
                    session_date=datetime.now().isoformat(),
                )
                
                if idx % 5 == 0:  # 每5个对话显示一次进度
                    print(f"  已存储 {idx + 1}/{len(conversation_pairs)} 对话")
            
            print(f"✅ 成功存储 {len(conversation_pairs)} 对对话到Memu")
            
        except Exception as e:
            print(f"❌ 数据存储失败: {e}")
            # 继续评测，使用空数据
    
    def retrieve_clustered_categories(self, query: str) -> str:
        """执行聚类分类检索"""
        try:
            categories = self.memu_client.retrieve_related_clustered_categories(
                user_id=self.user_id,
                agent_id=self.agent_id,
                category_query=query
            )
            
            if not categories:
                return ""
            
            # 格式化分类结果
            formatted_categories = []
            for category in categories:
                formatted_categories.append(
                    f"分类: {getattr(category, 'category_name', 'unknown')}\n"
                    f"内容: {getattr(category, 'content', str(category))}"
                )
            
            return "\n\n".join(formatted_categories)
            
        except Exception as e:
            print(f"❌ 聚类分类检索失败: {e}")
            return ""
    
    def retrieve_memory_items(self, query: str) -> str:
        """执行记忆项目检索"""
        try:
            memory_items = self.memu_client.retrieve_related_memory_items(
                query=query,
                user_id=self.user_id,
                agent_id=self.agent_id
            )
            
            if not memory_items:
                return ""
            
            # 格式化记忆项目结果
            formatted_items = []
            for item in memory_items:
                formatted_items.append(
                    f"记忆ID: {getattr(item, 'id', 'unknown')}\n"
                    f"内容: {getattr(item, 'content', str(item))}\n"
                    f"相关性: {getattr(item, 'relevance_score', 'N/A')}"
                )
            
            return "\n\n".join(formatted_items)
            
        except Exception as e:
            print(f"❌ 记忆项目检索失败: {e}")
            return ""
    
    def evaluate_similarity(self, query: str, retrieved_content: str, expected_content: str, retrieval_type: str) -> Tuple[float, str]:
        """使用Claude模型评估检索内容与预期内容的相似度"""
        
        system_prompt = """你是一个专业的记忆系统评测专家。请评估检索到的内容与预期内容的语义相似度。

评分标准 (0-10分):
- 10分：检索内容完全匹配预期，包含所有关键信息且准确
- 8-9分：检索内容基本匹配预期，包含大部分关键信息，细节略有差异  
- 6-7分：检索内容部分匹配预期，包含主要信息，但缺少一些重要细节
- 4-5分：检索内容与预期有一定关联，但信息不完整或有明显偏差
- 2-3分：检索内容与预期关联度较低，大部分信息不匹配
- 0-1分：检索内容与预期完全不匹配或为空

请根据语义相似度给出0-10的数字评分，并简要说明评分理由。"""

        human_prompt = f"""
用户查询: {query}
检索类型: {retrieval_type}

检索到的内容:
{retrieved_content if retrieved_content else "（无检索结果）"}

预期内容:
{expected_content}

请给出评分 (0-10) 和简要理由："""

        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=human_prompt)
            ]
            
            response = self.claude_model.invoke(messages)
            response_text = response.content
            
            # 从响应中提取评分
            score = self._extract_score_from_response(response_text)
            return score, response_text
            
        except Exception as e:
            print(f"❌ AI评分失败: {e}")
            return 0.0, f"评分失败: {str(e)}"
    
    def _extract_score_from_response(self, response: str) -> float:
        """从Claude响应中提取数字评分"""
        import re
        
        # 尝试提取数字评分
        patterns = [
            r'评分.*?([0-9](?:\.[0-9])?)',
            r'分数.*?([0-9](?:\.[0-9])?)',
            r'([0-9](?:\.[0-9])?)\s*分',
            r'([0-9](?:\.[0-9])?)/10',
            r'([0-9](?:\.[0-9])?)\s*(?:分|$)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, response)
            if matches:
                try:
                    score = float(matches[0])
                    return min(max(score, 0.0), 10.0)  # 确保分数在0-10范围内
                except ValueError:
                    continue
        
        # 如果无法提取数字，返回默认值
        return 0.0
    
    def evaluate_single_test_case(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """评测单个测试用例"""
        query = test_case["query"]
        expected = test_case["expected"]
        
        print(f"🔍 评测查询: {query}")
        
        # 执行两种检索
        clustered_result = self.retrieve_clustered_categories(query)
        memory_items_result = self.retrieve_memory_items(query)
        
        # AI评分
        clustered_score, clustered_reason = self.evaluate_similarity(query, clustered_result, expected, "聚类分类检索")
        memory_items_score, memory_items_reason = self.evaluate_similarity(query, memory_items_result, expected, "记忆项目检索")
        
        result = {
            "query": query,
            "expected": expected,
            # 检索结果
            "clustered_result": clustered_result,
            "memory_items_result": memory_items_result,
            # 评分结果
            "clustered_score": clustered_score,
            "memory_items_score": memory_items_score,
            # 评分详情
            "clustered_evaluation": clustered_reason,
            "memory_items_evaluation": memory_items_reason,
            # 综合评分
            "overall_average": (clustered_score + memory_items_score) / 2,
            "core_method_score": memory_items_score  # memory_items作为核心通用方法
        }
        
        print(f"  📊 聚类分类得分: {clustered_score:.1f}/10")
        print(f"  📊 记忆项目得分(通用): {memory_items_score:.1f}/10")
        print(f"  📊 综合平均得分: {result['overall_average']:.1f}/10\n")
        
        return result
    
    def evaluate_all_scenarios(self) -> Dict[str, Any]:
        """评测所有记忆场景"""
        print("🚀 开始Memu完整记忆能力评测...\n")
        
        scenario_results = {}
        total_scores = {"clustered": [], "memory_items": [], "overall_average": [], "core_method": []}
        
        for scenario in test_cases:
            scenario_name = scenario["sence"]
            test_case_list = scenario["test_case"]
            
            print(f"📋 评测场景: {scenario_name}")
            print("=" * 50)
            
            scenario_result = {
                "scenario_name": scenario_name,
                "test_results": [],
                "scenario_clustered_avg": 0,
                "scenario_memory_items_avg": 0,
                "scenario_overall_avg": 0
            }
            
            clustered_scores = []
            memory_items_scores = []
            
            for test_case in test_case_list:
                result = self.evaluate_single_test_case(test_case)
                scenario_result["test_results"].append(result)
                
                clustered_scores.append(result["clustered_score"])
                memory_items_scores.append(result["memory_items_score"])
                total_scores["clustered"].append(result["clustered_score"])
                total_scores["memory_items"].append(result["memory_items_score"])
                total_scores["overall_average"].append(result["overall_average"])
                total_scores["core_method"].append(result["core_method_score"])
            
            # 计算场景平均分
            scenario_result["scenario_clustered_avg"] = sum(clustered_scores) / len(clustered_scores)
            scenario_result["scenario_memory_items_avg"] = sum(memory_items_scores) / len(memory_items_scores)
            scenario_result["scenario_overall_avg"] = (scenario_result["scenario_clustered_avg"] + 
                                                     scenario_result["scenario_memory_items_avg"]) / 2
            
            scenario_results[scenario_name] = scenario_result
            
            print(f"🎯 场景 '{scenario_name}' 评测完成:")
            print(f"  聚类分类平均分: {scenario_result['scenario_clustered_avg']:.2f}/10")
            print(f"  记忆项目平均分: {scenario_result['scenario_memory_items_avg']:.2f}/10") 
            print(f"  场景总分: {scenario_result['scenario_overall_avg']:.2f}/10\n")
        
        # 计算整体评测结果
        overall_results = {
            "scenario_results": scenario_results,
            "overall_clustered_avg": sum(total_scores["clustered"]) / len(total_scores["clustered"]),
            "overall_memory_items_avg": sum(total_scores["memory_items"]) / len(total_scores["memory_items"]),
            "overall_average": sum(total_scores["overall_average"]) / len(total_scores["overall_average"]),
            "overall_core_method_avg": sum(total_scores["core_method"]) / len(total_scores["core_method"]),
            "total_test_cases": len(total_scores["overall_average"]),
            "evaluation_timestamp": datetime.now().isoformat(),
            "memory_framework": "Memu",
            "methods_tested": ["retrieve_related_clustered_categories", "retrieve_related_memory_items"]
        }
        
        return overall_results
    
    def generate_report(self, results: Dict[str, Any]) -> str:
        """生成评测报告"""
        report = []
        report.append("=" * 80)
        report.append("🧠 Memu记忆系统能力评测报告")
        report.append("=" * 80)
        report.append(f"评测时间: {results['evaluation_timestamp']}")
        report.append(f"记忆框架: {results['memory_framework']}")
        report.append(f"测试用例总数: {results['total_test_cases']}")
        report.append("")
        
        # 整体评测结果
        report.append("📊 整体评测结果")
        report.append("-" * 40)
        report.append(f"聚类分类检索平均分: {results['overall_clustered_avg']:.2f}/10")
        report.append(f"记忆项目检索平均分: {results['overall_memory_items_avg']:.2f}/10")
        report.append(f"综合平均分: {results['overall_average']:.2f}/10")
        
        # 评级
        avg_score = results['overall_average']
        if avg_score >= 9.0:
            grade = "🏆 优秀 (A+)"
        elif avg_score >= 8.0:
            grade = "🥇 良好 (A)"
        elif avg_score >= 7.0:
            grade = "🥈 中等 (B)"
        elif avg_score >= 6.0:
            grade = "🥉 及格 (C)"
        else:
            grade = "❌ 需改进 (D)"
        
        report.append(f"整体评级: {grade}")
        report.append("")
        
        # 各场景详细结果
        report.append("📋 各场景详细结果")
        report.append("-" * 40)
        
        for scenario_name, scenario_result in results["scenario_results"].items():
            report.append(f"\n🎯 {scenario_name}")
            report.append(f"  聚类分类平均: {scenario_result['scenario_clustered_avg']:.2f}/10")
            report.append(f"  记忆项目平均: {scenario_result['scenario_memory_items_avg']:.2f}/10")
            report.append(f"  场景总分: {scenario_result['scenario_overall_avg']:.2f}/10")
            
            # 显示该场景下表现最好和最差的测试用例
            test_results = scenario_result["test_results"]
            if test_results:
                best_case = max(test_results, key=lambda x: x["average_score"])
                worst_case = min(test_results, key=lambda x: x["average_score"])
                
                report.append(f"  ✅ 最佳表现 ({best_case['average_score']:.1f}分): {best_case['query']}")
                report.append(f"  ⚠️ 待改进 ({worst_case['average_score']:.1f}分): {worst_case['query']}")
        
        report.append("")
        report.append("=" * 80)
        
        return "\n".join(report)
    
    def save_detailed_results(self, results: Dict[str, Any], filename: str = "memu_evaluation_detailed.json") -> None:
        """保存详细评测结果到JSON文件"""
        output_path = os.path.join(os.path.dirname(__file__), filename)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"📁 详细评测结果已保存至: {output_path}")
    
    def run_evaluation(self) -> None:
        """运行完整的记忆能力评测"""
        print("🧠 Memu记忆系统能力评测程序启动")
        print("=" * 50)
        
        try:
            # 1. 设置测试环境
            # self.setup_test_data()
            
            # 2. 执行评测
            results = self.evaluate_all_scenarios()
            
            # 3. 生成报告
            report = self.generate_report(results)
            print(report)
            
            # 4. 保存详细结果
            self.save_detailed_results(results)
            
            print("✅ Memu记忆能力评测完成!")
            
        except Exception as e:
            print(f"❌ 评测过程中发生错误: {e}")
            import traceback
            traceback.print_exc()
            raise


def main():
    """主函数"""
    evaluator = MemuEvaluator()
    evaluator.run_evaluation()


if __name__ == "__main__":
    main()