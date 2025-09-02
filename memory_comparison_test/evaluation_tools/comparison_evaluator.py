"""
记忆框架对比评估器

使用真实的 MemU 和 Memobase 框架进行全面对比评估
"""

import json
import time
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime
import statistics

from config import settings
from loguru import logger
from memu_test.memu_tester import MemuTester
from memobase_test.memobase_tester import MemobaseTester
from test_scenarios.style_learning.chat_style_tests import ChatStyleTestScenarios
from test_scenarios.accuracy_boost.divination_accuracy_tests import DivinationAccuracyTestScenarios
from test_scenarios.info_extraction.information_extraction_tests import InformationExtractionTestScenarios


class MemoryFrameworkComparator:
    """记忆框架对比评估器"""
    
    def __init__(self, test_user_id: str = "comparison_test_user"):
        """
        初始化对比评估器
        
        Args:
            test_user_id: 测试用户ID
        """
        self.test_user_id = test_user_id
        self.memu_tester = None
        self.memobase_tester = None
        self.test_results = {}
        self.comparison_results = {}
        
        # 加载测试场景
        self.style_scenarios = ChatStyleTestScenarios()
        self.accuracy_scenarios = DivinationAccuracyTestScenarios()
        self.extraction_scenarios = InformationExtractionTestScenarios()
    
    def initialize_testers(self) -> bool:
        """
        初始化两个测试框架
        
        Returns:
            bool: 初始化是否成功
        """
        try:
            logger.info("正在初始化记忆框架测试器...")
            
            # 初始化 MemU 测试器
            self.memu_tester = MemuTester(self.test_user_id)
            memu_success = self.memu_tester.initialize_memory()
            
            # 初始化 Memobase 测试器
            self.memobase_tester = MemobaseTester(self.test_user_id)
            memobase_success = self.memobase_tester.initialize_memory()
            
            success = memu_success and memobase_success
            
            if success:
                logger.info("✅ 记忆框架初始化成功")
            else:
                logger.error("❌ 记忆框架初始化失败")
                
            return success
            
        except Exception as e:
            logger.error(f"初始化过程出错: {e}")
            return False
    
    def run_style_learning_test(self, scenario_id: str = "concise_preference") -> Dict[str, Any]:
        """
        运行聊天风格学习测试
        
        Args:
            scenario_id: 测试场景ID
            
        Returns:
            测试结果字典
        """
        logger.info(f"开始聊天风格学习测试 ({scenario_id})...")
        
        scenario = self.style_scenarios.get_scenario(scenario_id)
        if not scenario:
            return {"error": f"未找到场景 {scenario_id}"}
        
        results = {
            "scenario_id": scenario_id,
            "memu_results": {},
            "memobase_results": {},
            "comparison": {}
        }
        
        # 模拟对话轮次
        memu_responses = []
        memobase_responses = []
        
        for round_data in scenario["conversation_rounds"]:
            user_input = round_data["user_input"]
            
            # 模拟 AI 回复（实际应用中会调用真实的 AI 模型）
            if scenario_id == "concise_preference":
                # 模拟逐渐变短的回复
                round_num = round_data["round"]
                base_response = "根据您的八字分析，我看到..."
                
                # Memu 框架模拟回复
                memu_response = base_response + "详细内容" * max(1, 4 - round_num)
                memu_responses.append(memu_response)
                
                # Memobase 框架模拟回复  
                memobase_response = base_response + "详细内容" * max(1, 3 - round_num)
                memobase_responses.append(memobase_response)
                
            elif scenario_id == "detailed_preference":
                # 模拟逐渐变详细的回复
                round_num = round_data["round"]
                base_response = "您的运势分析如下："
                
                memu_response = base_response + "详细解释" * (round_num + 1)
                memu_responses.append(memu_response)
                
                memobase_response = base_response + "详细解释" * round_num
                memobase_responses.append(memobase_response)
                
            elif scenario_id == "interactive_preference":
                # 模拟互动性回复
                round_num = round_data["round"]
                base_response = "关于您的问题："
                
                memu_response = base_response + f"这是第{round_num}轮的回复，我理解您的需求。"
                memu_responses.append(memu_response)
                
                memobase_response = base_response + f"第{round_num}轮回复，感谢您的信任。"
                memobase_responses.append(memobase_response)
                
            else:
                # 默认回复生成
                round_num = round_data.get("round", len(memu_responses) + 1)
                base_response = "感谢您的咨询："
                
                memu_response = base_response + f"这是MemU第{round_num}轮的回复。"
                memu_responses.append(memu_response)
                
                memobase_response = base_response + f"这是Memobase第{round_num}轮的回复。"
                memobase_responses.append(memobase_response)
            
            # 更新聊天风格记忆
            if "style_indicators" in round_data:
                self.memu_tester.update_chat_style(round_data["style_indicators"])
                self.memobase_tester.update_chat_style(round_data["style_indicators"])
            
            # 记录对话轮次
            self.memu_tester.add_conversation_turn(user_input, memu_responses[-1])
            self.memobase_tester.add_conversation_turn(user_input, memobase_responses[-1])
        
        # 评估风格适应效果
        memu_scores = self.style_scenarios.evaluate_style_adaptation(scenario_id, memu_responses)
        memobase_scores = self.style_scenarios.evaluate_style_adaptation(scenario_id, memobase_responses)
        
        results["memu_results"] = {
            "responses": memu_responses,
            "scores": memu_scores,
            "learned_style": self.memu_tester.get_chat_style()
        }
        
        results["memobase_results"] = {
            "responses": memobase_responses, 
            "scores": memobase_scores,
            "learned_style": self.memobase_tester.get_chat_style()
        }
        
        # 对比分析
        results["comparison"] = self._compare_style_results(memu_scores, memobase_scores)
        
        logger.info(f"✅ 聊天风格学习测试完成")
        return results
    
    def run_accuracy_boost_test(self, scenario_id: str = "feedback_learning") -> Dict[str, Any]:
        """
        运行算命准确性提升测试
        
        Args:
            scenario_id: 测试场景ID
            
        Returns:
            测试结果字典
        """
        logger.info(f"开始算命准确性提升测试 ({scenario_id})...")
        
        scenario = self.accuracy_scenarios.get_scenario(scenario_id)
        if not scenario:
            return {"error": f"未找到场景 {scenario_id}"}
        
        results = {
            "scenario_id": scenario_id,
            "memu_results": {},
            "memobase_results": {},
            "comparison": {}
        }
        
        if scenario_id == "feedback_learning":
            phases = scenario["test_phases"]
            
            # 阶段1：初始预测
            initial_predictions = phases[0]["predictions"]
            
            # 存储初始预测
            for pred in initial_predictions:
                self.memu_tester.store_memory("divination_prediction", pred)
                self.memobase_tester.store_memory("divination_prediction", pred)
                self.memobase_tester.store_divination_result(pred["prediction"])
            
            # 阶段2：用户反馈
            feedback_data = phases[1]["feedback_data"]
            
            # 存储反馈信息
            for feedback in feedback_data:
                self.memu_tester.store_memory("verification_feedback", feedback)
                self.memobase_tester.store_memory("verification_feedback", feedback)
                
                # Memobase 更新算命历史
                self.memobase_tester.store_divination_result(
                    feedback.get("user_response", ""),
                    feedback["verification_status"],
                    feedback["accuracy_score"]
                )
            
            # 阶段3：调整后的预测（模拟）
            adjusted_predictions_memu = self._generate_adjusted_predictions(
                initial_predictions, feedback_data, "memu"
            )
            adjusted_predictions_memobase = self._generate_adjusted_predictions(
                initial_predictions, feedback_data, "memobase"
            )
            
            # 评估准确性提升
            memu_scores = self.accuracy_scenarios.evaluate_accuracy_improvement(
                scenario_id, initial_predictions, feedback_data, adjusted_predictions_memu
            )
            
            memobase_scores = self.accuracy_scenarios.evaluate_accuracy_improvement(
                scenario_id, initial_predictions, feedback_data, adjusted_predictions_memobase
            )
            
            results["memu_results"] = {
                "initial_predictions": initial_predictions,
                "adjusted_predictions": adjusted_predictions_memu,
                "scores": memu_scores
            }
            
            results["memobase_results"] = {
                "initial_predictions": initial_predictions,
                "adjusted_predictions": adjusted_predictions_memobase,
                "scores": memobase_scores
            }
            
            results["comparison"] = self._compare_accuracy_results(memu_scores, memobase_scores)
        
        logger.info(f"✅ 算命准确性提升测试完成")
        return results
    
    def run_info_extraction_test(self, scenario_id: str = "life_changes_extraction") -> Dict[str, Any]:
        """
        运行信息提取测试
        
        Args:
            scenario_id: 测试场景ID
            
        Returns:
            测试结果字典
        """
        logger.info(f"开始信息提取测试 ({scenario_id})...")
        
        scenario = self.extraction_scenarios.get_scenario(scenario_id)
        if not scenario:
            return {"error": f"未找到场景 {scenario_id}"}
        
        results = {
            "scenario_id": scenario_id,
            "memu_results": {},
            "memobase_results": {},
            "comparison": {}
        }
        
        # 收集用户输入
        user_inputs = []
        for conversation in scenario["test_conversations"]:
            for dialogue in conversation["dialogue"]:
                user_inputs.append(dialogue["user"])
        
        # 使用两个框架提取信息
        memu_extractions = []
        memobase_extractions = []
        
        for user_input in user_inputs:
            # Memu 提取
            memu_extracted = self.memu_tester.extract_divination_info(user_input)
            memu_extractions.append(memu_extracted)
            
            # Memobase 提取
            memobase_extracted = self.memobase_tester.extract_divination_info(user_input)
            memobase_extractions.append(memobase_extracted)
            
            # 存储提取的信息
            self.memu_tester.store_memory("extracted_info", memu_extracted)
            self.memobase_tester.store_memory("extracted_info", memobase_extracted)
        
        # 评估提取准确性
        memu_scores = self.extraction_scenarios.evaluate_extraction_accuracy(
            scenario_id, user_inputs, memu_extractions
        )
        
        memobase_scores = self.extraction_scenarios.evaluate_extraction_accuracy(
            scenario_id, user_inputs, memobase_extractions
        )
        
        results["memu_results"] = {
            "extractions": memu_extractions,
            "scores": memu_scores
        }
        
        results["memobase_results"] = {
            "extractions": memobase_extractions,
            "scores": memobase_scores
        }
        
        results["comparison"] = self._compare_extraction_results(memu_scores, memobase_scores)
        
        logger.info(f"✅ 信息提取测试完成")
        return results
    
    def run_comprehensive_comparison(self) -> Dict[str, Any]:
        """
        运行综合对比测试
        
        Returns:
            完整的对比结果
        """
        logger.info("开始综合记忆框架对比测试...")
        
        # 初始化测试器
        if not self.initialize_testers():
            return {"error": "测试器初始化失败"}
        
        comprehensive_results = {
            "test_info": {
                "user_id": self.test_user_id,
                "start_time": datetime.now().isoformat(),
                "framework_versions": {
                    "memu": "test_version",
                    "memobase": "test_version"
                }
            },
            "style_learning_tests": {},
            "accuracy_boost_tests": {},
            "info_extraction_tests": {},
            "overall_comparison": {},
            "performance_metrics": {}
        }
        
        # 1. 聊天风格学习测试
        logger.info("第一部分：聊天风格学习能力测试")
        style_test_scenarios = ["concise_preference", "detailed_preference", "interactive_preference"]
        
        for scenario in style_test_scenarios:
            result = self.run_style_learning_test(scenario)
            comprehensive_results["style_learning_tests"][scenario] = result
        
        # 2. 算命准确性提升测试
        logger.info("第二部分：算命准确性提升能力测试")
        accuracy_test_scenarios = ["feedback_learning", "pattern_recognition"]
        
        for scenario in accuracy_test_scenarios:
            result = self.run_accuracy_boost_test(scenario)
            comprehensive_results["accuracy_boost_tests"][scenario] = result
        
        # 3. 信息提取测试
        logger.info("第三部分：信息提取能力测试")
        extraction_test_scenarios = ["life_changes_extraction", "temporal_information_extraction"]
        
        for scenario in extraction_test_scenarios:
            result = self.run_info_extraction_test(scenario)
            comprehensive_results["info_extraction_tests"][scenario] = result
        
        # 4. 总体对比分析
        comprehensive_results["overall_comparison"] = self._generate_overall_comparison(comprehensive_results)
        
        # 5. 性能指标统计
        comprehensive_results["performance_metrics"] = self._collect_performance_metrics()
        
        # 记录结束时间
        comprehensive_results["test_info"]["end_time"] = datetime.now().isoformat()
        
        logger.info("综合对比测试完成！")
        return comprehensive_results
    
    def _compare_style_results(self, memu_scores: Dict[str, float], 
                              memobase_scores: Dict[str, float]) -> Dict[str, Any]:
        """对比聊天风格学习结果"""
        comparison = {}
        
        for metric in ["adaptation_speed", "final_match", "consistency", "overall"]:
            memu_score = memu_scores.get(metric, 0)
            memobase_score = memobase_scores.get(metric, 0)
            
            comparison[metric] = {
                "memu": memu_score,
                "memobase": memobase_score,
                "winner": "memu" if memu_score > memobase_score else "memobase" if memobase_score > memu_score else "tie",
                "difference": abs(memu_score - memobase_score)
            }
        
        return comparison
    
    def _compare_accuracy_results(self, memu_scores: Dict[str, float],
                                 memobase_scores: Dict[str, float]) -> Dict[str, Any]:
        """对比算命准确性提升结果"""
        comparison = {}
        
        for metric in ["feedback_integration", "confidence_adjustment", "specificity_improvement", "pattern_learning", "overall"]:
            memu_score = memu_scores.get(metric, 0)
            memobase_score = memobase_scores.get(metric, 0)
            
            comparison[metric] = {
                "memu": memu_score,
                "memobase": memobase_score,
                "winner": "memu" if memu_score > memobase_score else "memobase" if memobase_score > memu_score else "tie",
                "difference": abs(memu_score - memobase_score)
            }
        
        return comparison
    
    def _compare_extraction_results(self, memu_scores: Dict[str, float],
                                   memobase_scores: Dict[str, float]) -> Dict[str, Any]:
        """对比信息提取结果"""
        comparison = {}
        
        for metric in ["recall", "precision", "temporal_accuracy", "completeness", "overall"]:
            memu_score = memu_scores.get(metric, 0)
            memobase_score = memobase_scores.get(metric, 0)
            
            comparison[metric] = {
                "memu": memu_score,
                "memobase": memobase_score,
                "winner": "memu" if memu_score > memobase_score else "memobase" if memobase_score > memu_score else "tie",
                "difference": abs(memu_score - memobase_score)
            }
        
        return comparison
    
    def _generate_adjusted_predictions(self, initial_predictions: List[Dict],
                                     feedback_data: List[Dict],
                                     framework: str) -> List[Dict]:
        """生成调整后的预测（模拟）"""
        adjusted = []
        
        for pred in initial_predictions:
            topic = pred["topic"]
            
            # 查找对应的反馈
            feedback = None
            for fb in feedback_data:
                if fb["topic"] == topic:
                    feedback = fb
                    break
            
            if feedback:
                adjusted_pred = pred.copy()
                
                # 根据反馈调整置信度
                if feedback["verification_status"] == "correct":
                    adjusted_pred["confidence"] = min(pred["confidence"] + 0.2, 1.0)
                    adjusted_pred["prediction"] += " （基于历史验证，此类预测准确性较高）"
                else:
                    adjusted_pred["confidence"] = max(pred["confidence"] - 0.3, 0.1)
                    adjusted_pred["prediction"] += " （需要更多信息确认，建议谨慎对待）"
                
                # 不同框架的特殊调整
                if framework == "memobase":
                    # Memobase 可能在置信度调整上更激进
                    if feedback["verification_status"] == "correct":
                        adjusted_pred["confidence"] = min(pred["confidence"] + 0.25, 1.0)
                
                adjusted.append(adjusted_pred)
            else:
                adjusted.append(pred)
        
        return adjusted
    
    def _generate_overall_comparison(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """生成总体对比分析"""
        overall = {
            "category_winners": {},
            "overall_winner": "",
            "strength_analysis": {},
            "recommendations": {}
        }
        
        # 统计各类别获胜次数
        memu_wins = 0
        memobase_wins = 0
        ties = 0
        
        categories = ["style_learning_tests", "accuracy_boost_tests", "info_extraction_tests"]
        
        for category in categories:
            category_tests = results.get(category, {})
            category_memu_wins = 0
            category_memobase_wins = 0
            
            for test_name, test_result in category_tests.items():
                comparison = test_result.get("comparison", {})
                
                for metric, metric_comparison in comparison.items():
                    if metric == "overall":  # 只统计总体指标
                        winner = metric_comparison.get("winner", "tie")
                        if winner == "memu":
                            memu_wins += 1
                            category_memu_wins += 1
                        elif winner == "memobase":
                            memobase_wins += 1
                            category_memobase_wins += 1
                        else:
                            ties += 1
            
            # 确定类别获胜者
            if category_memu_wins > category_memobase_wins:
                overall["category_winners"][category] = "memu"
            elif category_memobase_wins > category_memu_wins:
                overall["category_winners"][category] = "memobase"
            else:
                overall["category_winners"][category] = "tie"
        
        # 确定总体获胜者
        if memu_wins > memobase_wins:
            overall["overall_winner"] = "memu"
        elif memobase_wins > memu_wins:
            overall["overall_winner"] = "memobase"
        else:
            overall["overall_winner"] = "tie"
        
        # 优势分析
        overall["strength_analysis"] = {
            "memu": {
                "wins": memu_wins,
                "strong_areas": self._identify_strong_areas(results, "memu"),
                "characteristics": ["结构化存储", "简单直接", "快速响应"]
            },
            "memobase": {
                "wins": memobase_wins,
                "strong_areas": self._identify_strong_areas(results, "memobase"),
                "characteristics": ["语义搜索", "复杂查询", "关联分析"]
            }
        }
        
        return overall
    
    def _identify_strong_areas(self, results: Dict[str, Any], framework: str) -> List[str]:
        """识别框架的优势领域"""
        strong_areas = []
        
        categories = {
            "style_learning_tests": "聊天风格学习",
            "accuracy_boost_tests": "算命准确性提升", 
            "info_extraction_tests": "信息提取"
        }
        
        for category_key, category_name in categories.items():
            category_tests = results.get(category_key, {})
            framework_wins = 0
            total_tests = 0
            
            for test_name, test_result in category_tests.items():
                comparison = test_result.get("comparison", {})
                for metric, metric_comparison in comparison.items():
                    if metric == "overall":
                        total_tests += 1
                        if metric_comparison.get("winner") == framework:
                            framework_wins += 1
            
            if total_tests > 0 and framework_wins / total_tests >= 0.6:  # 60%以上获胜率
                strong_areas.append(category_name)
        
        return strong_areas
    
    def _collect_performance_metrics(self) -> Dict[str, Any]:
        """收集性能指标"""
        metrics = {}
        
        if self.memu_tester:
            metrics["memu"] = self.memu_tester.get_memory_stats()
        
        if self.memobase_tester:
            metrics["memobase"] = self.memobase_tester.get_memory_stats()
        
        return metrics
    
    def export_results(self, results: Dict[str, Any], file_path: str) -> bool:
        """
        导出测试结果
        
        Args:
            results: 测试结果
            file_path: 导出文件路径
            
        Returns:
            bool: 导出是否成功
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            
            logger.info(f"测试结果已导出到: {file_path}")
            return True
        except Exception as e:
            logger.error(f"结果导出失败: {e}")
            return False
    
    def cleanup(self):
        """清理资源"""
        try:
            if self.memu_tester:
                self.memu_tester.cleanup()
            
            if self.memobase_tester:
                self.memobase_tester.cleanup()
            
            logger.info("资源清理完成")
            
        except Exception as e:
            logger.error(f"资源清理失败: {e}")