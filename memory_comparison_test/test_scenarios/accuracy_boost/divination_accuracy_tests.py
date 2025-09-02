"""
算命准确性提升测试场景

测试基于历史反馈提升算命准确性的能力
"""

from typing import Dict, List, Any, Optional
import json
from datetime import datetime, timedelta

class DivinationAccuracyTestScenarios:
    """算命准确性测试场景集合"""
    
    def __init__(self):
        self.test_cases = self._load_test_cases()
    
    def _load_test_cases(self) -> List[Dict[str, Any]]:
        """加载测试用例"""
        return [
            {
                "scenario_id": "feedback_learning",
                "description": "测试AI根据用户反馈调整预测准确性的能力",
                "test_phases": [
                    {
                        "phase": "initial_predictions",
                        "predictions": [
                            {
                                "topic": "career",
                                "prediction": "你在2023年下半年会有职业变动，可能是升职或换工作",
                                "confidence": 0.7,
                                "time_frame": "2023年7-12月"
                            },
                            {
                                "topic": "finance", 
                                "prediction": "今年财运一般，需要谨慎投资",
                                "confidence": 0.6,
                                "time_frame": "2023年全年"
                            },
                            {
                                "topic": "health",
                                "prediction": "注意肠胃健康，秋天要特别小心",
                                "confidence": 0.5,
                                "time_frame": "2023年秋季"
                            }
                        ]
                    },
                    {
                        "phase": "user_feedback",
                        "feedback_data": [
                            {
                                "topic": "career",
                                "user_response": "确实，我10月换了工作，你说得很准",
                                "verification_status": "correct",
                                "accuracy_score": 0.9,
                                "feedback_time": "2023-11-15"
                            },
                            {
                                "topic": "finance",
                                "user_response": "财运还可以啊，我股票赚了不少",
                                "verification_status": "incorrect", 
                                "accuracy_score": 0.2,
                                "feedback_time": "2023-12-01"
                            },
                            {
                                "topic": "health",
                                "user_response": "肠胃确实有点问题，去医院看了",
                                "verification_status": "correct",
                                "accuracy_score": 0.8,
                                "feedback_time": "2023-10-20"
                            }
                        ]
                    },
                    {
                        "phase": "adjusted_predictions",
                        "new_predictions_test": {
                            "description": "基于反馈调整新预测",
                            "expected_adjustments": {
                                "career": {
                                    "confidence_boost": 0.2,
                                    "detail_increase": "应该给出更具体的时间和方式"
                                },
                                "finance": {
                                    "confidence_decrease": 0.3,
                                    "approach_change": "应该更谨慎，询问更多背景信息"
                                },
                                "health": {
                                    "confidence_boost": 0.1,
                                    "specificity_increase": "应该给出更具体的建议"
                                }
                            }
                        }
                    }
                ]
            },
            {
                "scenario_id": "pattern_recognition",
                "description": "测试AI识别个人命理模式的能力",
                "test_sequence": [
                    {
                        "round": 1,
                        "prediction": "你的事业运较强，适合在技术或创新领域发展",
                        "user_background": "程序员，在科技公司工作",
                        "verification": "确实，我一直在互联网公司做开发"
                    },
                    {
                        "round": 2, 
                        "prediction": "你在人际关系上比较直接，可能有时会得罪人",
                        "user_feedback": "哈哈，我同事都说我说话太直",
                        "verification": "correct"
                    },
                    {
                        "round": 3,
                        "prediction": "你的财运与技术能力相关，建议专注技能提升",
                        "user_feedback": "对，我每次加薪都是因为技术进步",
                        "verification": "correct"
                    },
                    {
                        "round": 4,
                        "test_question": "根据前面的模式，预测这个人明年的发展方向",
                        "expected_pattern_application": {
                            "career_focus": "技术能力提升",
                            "relationship_advice": "注意沟通方式",
                            "financial_guidance": "通过技能变现"
                        }
                    }
                ]
            },
            {
                "scenario_id": "cross_domain_correlation",
                "description": "测试跨领域信息关联分析能力",
                "correlation_tests": [
                    {
                        "user_shares": [
                            "最近工作压力很大，经常加班",
                            "身体感觉有点疲劳，睡眠不好",
                            "和女朋友关系也有点紧张"
                        ],
                        "ai_analysis_test": {
                            "expected_correlations": [
                                "工作压力 -> 健康问题",
                                "工作压力 -> 感情关系紧张",
                                "健康问题 -> 情绪影响感情"
                            ],
                            "holistic_advice": "应该提供综合性的生活调整建议"
                        }
                    },
                    {
                        "follow_up_prediction": "明年这个人的运势预测",
                        "expected_integration": {
                            "career": "建议调整工作节奏",
                            "health": "重点关注身体恢复",
                            "relationship": "修复感情关系的建议"
                        }
                    }
                ]
            },
            {
                "scenario_id": "temporal_accuracy",
                "description": "测试时间预测的精确度提升",
                "time_learning_sequence": [
                    {
                        "initial_prediction": "你今年春天会有好消息",
                        "actual_outcome": "4月收到升职通知",
                        "timing_accuracy": "准确",
                        "learned_pattern": "春天=3-5月，好消息=职业发展"
                    },
                    {
                        "follow_up_prediction": "下次预测同类事件的时间应该更精确",
                        "test_case": "预测下一个职业机会的时间",
                        "expected_improvement": "应该给出更具体的月份范围"
                    }
                ]
            }
        ]
    
    def get_scenario(self, scenario_id: str) -> Dict[str, Any]:
        """获取特定测试场景"""
        for scenario in self.test_cases:
            if scenario["scenario_id"] == scenario_id:
                return scenario
        return None
    
    def evaluate_accuracy_improvement(self, scenario_id: str, 
                                    initial_predictions: List[Dict],
                                    feedback_data: List[Dict],
                                    adjusted_predictions: List[Dict]) -> Dict[str, float]:
        """
        评估准确性提升效果
        
        Args:
            scenario_id: 场景ID
            initial_predictions: 初始预测
            feedback_data: 用户反馈数据
            adjusted_predictions: 调整后的预测
            
        Returns:
            评估分数字典
        """
        scores = {
            "feedback_integration": 0.0,
            "confidence_adjustment": 0.0,
            "specificity_improvement": 0.0,
            "pattern_learning": 0.0,
            "overall": 0.0
        }
        
        scenario = self.get_scenario(scenario_id)
        if not scenario:
            return scores
        
        # 评估反馈整合能力
        if scenario_id == "feedback_learning":
            for feedback in feedback_data:
                topic = feedback["topic"]
                
                # 找到对应的调整后预测
                adjusted_pred = None
                for pred in adjusted_predictions:
                    if pred.get("topic") == topic:
                        adjusted_pred = pred
                        break
                
                if adjusted_pred:
                    # 评估置信度调整是否合理
                    if feedback["verification_status"] == "correct":
                        # 正确预测应该提高置信度
                        if adjusted_pred.get("confidence", 0) > 0.7:
                            scores["confidence_adjustment"] += 0.33
                    else:
                        # 错误预测应该降低置信度  
                        if adjusted_pred.get("confidence", 1) < 0.5:
                            scores["confidence_adjustment"] += 0.33
        
        # 评估特异性提升
        initial_avg_length = sum(len(pred.get("prediction", "")) for pred in initial_predictions) / len(initial_predictions) if initial_predictions else 0
        adjusted_avg_length = sum(len(pred.get("prediction", "")) for pred in adjusted_predictions) / len(adjusted_predictions) if adjusted_predictions else 0
        
        if adjusted_avg_length > initial_avg_length * 1.2:  # 详细度提升20%以上
            scores["specificity_improvement"] = 0.8
        elif adjusted_avg_length > initial_avg_length:
            scores["specificity_improvement"] = 0.5
        
        # 评估模式学习能力
        correct_feedback_count = sum(1 for fb in feedback_data if fb["verification_status"] == "correct")
        if correct_feedback_count > 0:
            scores["pattern_learning"] = correct_feedback_count / len(feedback_data)
        
        # 评估反馈整合的全面性
        feedback_topics = set(fb["topic"] for fb in feedback_data)
        adjusted_topics = set(pred.get("topic") for pred in adjusted_predictions)
        integration_ratio = len(feedback_topics.intersection(adjusted_topics)) / len(feedback_topics) if feedback_topics else 0
        scores["feedback_integration"] = integration_ratio
        
        # 计算总体分数
        scores["overall"] = sum(scores[key] for key in scores if key != "overall") / 4
        
        return scores
    
    def evaluate_correlation_analysis(self, user_shares: List[str], 
                                    ai_analysis: str) -> Dict[str, float]:
        """
        评估跨领域关联分析能力
        
        Args:
            user_shares: 用户分享的信息
            ai_analysis: AI的分析结果
            
        Returns:
            评估分数字典
        """
        scores = {
            "correlation_identification": 0.0,
            "holistic_thinking": 0.0,
            "practical_advice": 0.0,
            "overall": 0.0
        }
        
        # 检查是否识别出关键关联
        expected_correlations = [
            ("工作", "健康"),
            ("工作", "感情"),
            ("压力", "睡眠"),
            ("疲劳", "关系")
        ]
        
        identified_correlations = 0
        for term1, term2 in expected_correlations:
            if term1 in ai_analysis and term2 in ai_analysis:
                identified_correlations += 1
        
        scores["correlation_identification"] = identified_correlations / len(expected_correlations)
        
        # 检查整体性思维
        holistic_indicators = ["综合", "整体", "平衡", "协调", "统筹"]
        holistic_score = sum(1 for indicator in holistic_indicators if indicator in ai_analysis)
        scores["holistic_thinking"] = min(holistic_score / 2, 1.0)
        
        # 检查实用建议
        advice_indicators = ["建议", "应该", "可以", "尝试", "调整"]
        advice_score = sum(1 for indicator in advice_indicators if indicator in ai_analysis)
        scores["practical_advice"] = min(advice_score / 3, 1.0)
        
        scores["overall"] = sum(scores[key] for key in scores if key != "overall") / 3
        
        return scores
    
    def generate_test_data(self, scenario_id: str) -> Dict[str, Any]:
        """
        生成测试数据
        
        Args:
            scenario_id: 场景ID
            
        Returns:
            测试数据字典
        """
        scenario = self.get_scenario(scenario_id)
        if not scenario:
            return {}
        
        return {
            "scenario": scenario,
            "timestamp": datetime.now().isoformat(),
            "test_instructions": f"请按照 {scenario['description']} 进行测试",
            "evaluation_metrics": [
                "feedback_integration",
                "confidence_adjustment", 
                "specificity_improvement",
                "pattern_learning"
            ]
        }