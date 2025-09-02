"""
记忆系统能力评测主程序

基于LangChain和MemoBase，对不同场景下的记忆能力进行定量评测
"""

import os
import sys
from typing import Dict, List, Any, Tuple
from datetime import datetime
import json

# 添加项目根目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from memobase import ChatBlob, MemoBaseClient
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage

from test_memory.chats import chats
from test_memory.test_case import test_cases
from user_config import settings


class MemoryEvaluator:
    """记忆系统评测器"""
    
    def __init__(self):
        # 初始化MemoBase客户端
        self.memo_client = MemoBaseClient(
            project_url="https://api.memobase.dev",
            api_key=settings.MEMOBASE_API_KEY.get_secret_value(),
        )
        
        # 初始化Claude模型用于评分
        self.claude_model = ChatAnthropic(
            model="claude-3-5-sonnet-20241022",
            api_key=settings.ANTHROPIC_API_KEY.get_secret_value()
        )
        
        # 获取或创建测试用户
        self.user = None
        self.evaluation_results: List[Dict[str, Any]] = []
    
    def setup_test_user(self) -> None:
        """设置测试用户并插入聊天数据"""
        print("🔧 设置测试用户...")
        
        # 创建新用户或使用现有用户
        try:
            # 尝试使用现有用户ID，如果不存在则创建新的
            user_id = "39703f16-8a39-4384-9820-47b4f1ce849e"
            self.user = self.memo_client.get_user(user_id)
            print(f"✅ 使用现有用户: {user_id}")
        except Exception:
            # 如果获取失败，创建新用户
            user_id = self.memo_client.add_user()
            self.user = self.memo_client.get_user(user_id)
            print(f"✅ 创建新用户: {user_id}")
        
        # 插入测试聊天数据
        # print("📝 插入聊天数据到MemoBase...")
        # chat_blob = ChatBlob(messages=chats)
        # self.user.insert(chat_blob)
        # self.user.flush()
        # print(f"✅ 成功插入 {len(chats)} 条聊天记录")
    
    def retrieve_context(self, query: str) -> str:
        """执行context检索"""
        try:
            context_result = self.user.context(chats=[{"role": "user", "content": query}])
            return context_result if context_result else ""
        except Exception as e:
            print(f"❌ Context检索失败: {e}")
            return ""
    
    def retrieve_profile(self, query: str) -> str:
        """执行profile检索 - 专门的用户属性跟踪"""
        try:
            profile_results = self.user.profile(chats=[{"role": "user", "content": query}])
            
            # 格式化profile结果
            if not profile_results:
                return ""
            
            formatted_profiles = []
            for profile in profile_results:
                formatted_profiles.append(
                    f"主题: {profile.topic}\n"
                    f"子主题: {profile.sub_topic}\n"
                    f"内容: {profile.content}"
                )
            
            return "\n\n".join(formatted_profiles)
        except Exception as e:
            print(f"❌ Profile检索失败: {e}")
            return ""
    
    def retrieve_search_event(self, query: str) -> str:
        """执行search_event检索 - 事件时间线检索"""
        try:
            # 注意：这里需要根据MemoBase实际API调整方法名
            event_results = self.user.search_event(query=query)
            
            if not event_results:
                return ""
            
            # 格式化事件结果
            formatted_events = []
            for event in event_results:
                formatted_events.append(
                    f"事件ID: {getattr(event, 'id', 'unknown')}\n"
                    f"时间: {getattr(event, 'timestamp', 'unknown')}\n"
                    f"内容: {getattr(event, 'content', str(event))}\n"
                    f"标签: {getattr(event, 'tags', [])}"
                )
            
            return "\n\n".join(formatted_events)
        except Exception as e:
            print(f"❌ Search Event检索失败: {e}")
            return ""
    
    def retrieve_search_event_gist(self, query: str) -> str:
        """执行search_event_gist检索 - 精确事实检索"""
        try:
            # 注意：这里需要根据MemoBase实际API调整方法名
            gist_results = self.user.search_event_gist(query=query)
            
            if not gist_results:
                return ""
            
            # 格式化精确事实结果
            formatted_gists = []
            for gist in gist_results:
                formatted_gists.append(
                    f"事实ID: {getattr(gist, 'id', 'unknown')}\n"
                    f"内容: {getattr(gist, 'content', str(gist))}\n"
                    f"置信度: {getattr(gist, 'confidence', 'N/A')}"
                )
            
            return "\n\n".join(formatted_gists)
        except Exception as e:
            print(f"❌ Search Event Gist检索失败: {e}")
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
        """评测单个测试用例 - 支持4种MemoBase检索方法"""
        query = test_case["query"]
        expected = test_case["expected"]
        
        print(f"🔍 评测查询: {query}")
        
        # 执行4种检索方法
        context_result = self.retrieve_context(query)
        profile_result = self.retrieve_profile(query)
        search_event_result = self.retrieve_search_event(query)
        search_event_gist_result = self.retrieve_search_event_gist(query)
        
        # AI评分 - 4种方法
        context_score, context_reason = self.evaluate_similarity(query, context_result, expected, "Context检索(通用)")
        profile_score, profile_reason = self.evaluate_similarity(query, profile_result, expected, "Profile检索(用户属性)")
        search_event_score, search_event_reason = self.evaluate_similarity(query, search_event_result, expected, "Event检索(事件时间线)")
        search_event_gist_score, search_event_gist_reason = self.evaluate_similarity(query, search_event_gist_result, expected, "EventGist检索(精确事实)")
        
        result = {
            "query": query,
            "expected": expected,
            # 检索结果
            "context_result": context_result,
            "profile_result": profile_result,
            "search_event_result": search_event_result,
            "search_event_gist_result": search_event_gist_result,
            # 评分结果
            "context_score": context_score,
            "profile_score": profile_score,
            "search_event_score": search_event_score,
            "search_event_gist_score": search_event_gist_score,
            # 评分详情
            "context_evaluation": context_reason,
            "profile_evaluation": profile_reason,
            "search_event_evaluation": search_event_reason,
            "search_event_gist_evaluation": search_event_gist_reason,
            # 综合评分
            "overall_average": (context_score + profile_score + search_event_score + search_event_gist_score) / 4,
            "core_method_score": context_score  # Context作为核心通用方法
        }
        
        print(f"  📊 Context得分(通用): {context_score:.1f}/10")
        print(f"  📊 Profile得分(属性): {profile_score:.1f}/10")
        print(f"  📊 Event得分(时间线): {search_event_score:.1f}/10")
        print(f"  📊 EventGist得分(事实): {search_event_gist_score:.1f}/10")
        print(f"  📊 综合平均得分: {result['overall_average']:.1f}/10\n")
        
        return result
    
    def evaluate_all_scenarios(self) -> Dict[str, Any]:
        """评测所有记忆场景"""
        print("🚀 开始完整记忆能力评测...\n")
        
        scenario_results = {}
        total_scores = {
            "context": [], "profile": [], "search_event": [], "search_event_gist": [], 
            "overall_average": [], "core_method": []
        }
        
        for scenario in test_cases:
            scenario_name = scenario["sence"]
            test_case_list = scenario["test_case"]
            
            print(f"📋 评测场景: {scenario_name}")
            print("=" * 60)
            
            scenario_result = {
                "scenario_name": scenario_name,
                "test_results": [],
                "scenario_context_avg": 0,
                "scenario_profile_avg": 0,
                "scenario_search_event_avg": 0,
                "scenario_search_event_gist_avg": 0,
                "scenario_overall_avg": 0,
                "scenario_core_method_avg": 0
            }
            
            context_scores = []
            profile_scores = []
            search_event_scores = []
            search_event_gist_scores = []
            overall_scores = []
            core_method_scores = []
            
            for test_case in test_case_list:
                result = self.evaluate_single_test_case(test_case)
                scenario_result["test_results"].append(result)
                
                # 收集各方法得分
                context_scores.append(result["context_score"])
                profile_scores.append(result["profile_score"])
                search_event_scores.append(result["search_event_score"])
                search_event_gist_scores.append(result["search_event_gist_score"])
                overall_scores.append(result["overall_average"])
                core_method_scores.append(result["core_method_score"])
                
                # 添加到总体统计
                total_scores["context"].append(result["context_score"])
                total_scores["profile"].append(result["profile_score"])
                total_scores["search_event"].append(result["search_event_score"])
                total_scores["search_event_gist"].append(result["search_event_gist_score"])
                total_scores["overall_average"].append(result["overall_average"])
                total_scores["core_method"].append(result["core_method_score"])
            
            # 计算场景平均分
            scenario_result["scenario_context_avg"] = sum(context_scores) / len(context_scores)
            scenario_result["scenario_profile_avg"] = sum(profile_scores) / len(profile_scores)
            scenario_result["scenario_search_event_avg"] = sum(search_event_scores) / len(search_event_scores)
            scenario_result["scenario_search_event_gist_avg"] = sum(search_event_gist_scores) / len(search_event_gist_scores)
            scenario_result["scenario_overall_avg"] = sum(overall_scores) / len(overall_scores)
            scenario_result["scenario_core_method_avg"] = sum(core_method_scores) / len(core_method_scores)
            
            scenario_results[scenario_name] = scenario_result
            
            print(f"🎯 场景 '{scenario_name}' 评测完成:")
            print(f"  Context平均分(通用): {scenario_result['scenario_context_avg']:.2f}/10")
            print(f"  Profile平均分(属性): {scenario_result['scenario_profile_avg']:.2f}/10")
            print(f"  Event平均分(时间线): {scenario_result['scenario_search_event_avg']:.2f}/10")
            print(f"  EventGist平均分(事实): {scenario_result['scenario_search_event_gist_avg']:.2f}/10")
            print(f"  场景综合得分: {scenario_result['scenario_overall_avg']:.2f}/10\n")
        
        # 计算整体评测结果
        overall_results = {
            "scenario_results": scenario_results,
            "overall_context_avg": sum(total_scores["context"]) / len(total_scores["context"]),
            "overall_profile_avg": sum(total_scores["profile"]) / len(total_scores["profile"]),
            "overall_search_event_avg": sum(total_scores["search_event"]) / len(total_scores["search_event"]),
            "overall_search_event_gist_avg": sum(total_scores["search_event_gist"]) / len(total_scores["search_event_gist"]),
            "overall_average": sum(total_scores["overall_average"]) / len(total_scores["overall_average"]),
            "overall_core_method_avg": sum(total_scores["core_method"]) / len(total_scores["core_method"]),
            "total_test_cases": len(total_scores["overall_average"]),
            "evaluation_timestamp": datetime.now().isoformat(),
            "memory_framework": "MemoBase",
            "methods_tested": ["context", "profile", "search_event", "search_event_gist"]
        }
        
        return overall_results
    
    def generate_report(self, results: Dict[str, Any]) -> str:
        """生成评测报告"""
        report = []
        report.append("=" * 80)
        report.append("🧠 记忆系统能力评测报告")
        report.append("=" * 80)
        report.append(f"评测时间: {results['evaluation_timestamp']}")
        report.append(f"测试用例总数: {results['total_test_cases']}")
        report.append("")
        
        # 整体评测结果
        report.append("📊 整体评测结果")
        report.append("-" * 40)
        report.append(f"Context检索平均分: {results['overall_context_avg']:.2f}/10")
        report.append(f"Profile检索平均分: {results['overall_profile_avg']:.2f}/10")
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
            report.append(f"  Context平均: {scenario_result['scenario_context_avg']:.2f}/10")
            report.append(f"  Profile平均: {scenario_result['scenario_profile_avg']:.2f}/10")
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
    
    def save_detailed_results(self, results: Dict[str, Any], filename: str = "memory_evaluation_detailed.json") -> None:
        """保存详细评测结果到JSON文件"""
        output_path = os.path.join(os.path.dirname(__file__), filename)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"📁 详细评测结果已保存至: {output_path}")
    
    def run_evaluation(self) -> None:
        """运行完整的记忆能力评测"""
        print("🧠 记忆系统能力评测程序启动")
        print("=" * 50)
        
        try:
            # 1. 设置测试环境
            self.setup_test_user()
            
            # 2. 执行评测
            results = self.evaluate_all_scenarios()
            
            # 3. 生成报告
            report = self.generate_report(results)
            print(report)
            
            # 4. 保存详细结果
            self.save_detailed_results(results)
            
            print("✅ 记忆能力评测完成!")
            
        except Exception as e:
            print(f"❌ 评测过程中发生错误: {e}")
            raise


def main():
    """主函数"""
    evaluator = MemoryEvaluator()
    evaluator.run_evaluation()


if __name__ == "__main__":
    main()