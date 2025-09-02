"""
信息提取测试场景

测试从对话中提取再次算命所需信息的能力
"""

from typing import Dict, List, Any, Optional
import json
import re
from datetime import datetime

class InformationExtractionTestScenarios:
    """信息提取测试场景集合"""
    
    def __init__(self):
        self.test_cases = self._load_test_cases()
    
    def _load_test_cases(self) -> List[Dict[str, Any]]:
        """加载测试用例"""
        return [
            {
                "scenario_id": "life_changes_extraction",
                "description": "测试提取用户生活重大变化的能力",
                "test_conversations": [
                    {
                        "conversation_id": "career_change",
                        "dialogue": [
                            {
                                "user": "最近换了新工作，从互联网公司跳到了传统制造业",
                                "expected_extractions": {
                                    "career_change": {
                                        "type": "job_change",
                                        "from": "互联网公司", 
                                        "to": "传统制造业",
                                        "time": "最近",
                                        "impact_level": "major"
                                    }
                                }
                            },
                            {
                                "user": "工作环境变化很大，压力也比以前大了不少",
                                "expected_extractions": {
                                    "work_environment": {
                                        "change_type": "environment_shift",
                                        "stress_level": "increased",
                                        "comparison": "比以前大"
                                    }
                                }
                            },
                            {
                                "user": "不过薪水涨了30%，这点还是很满意的",
                                "expected_extractions": {
                                    "financial_change": {
                                        "type": "salary_increase",
                                        "percentage": "30%",
                                        "attitude": "满意"
                                    }
                                }
                            }
                        ]
                    },
                    {
                        "conversation_id": "relationship_status", 
                        "dialogue": [
                            {
                                "user": "和男朋友分手了，三年的感情就这样结束了",
                                "expected_extractions": {
                                    "relationship_change": {
                                        "type": "breakup",
                                        "relationship_duration": "三年",
                                        "emotional_state": "失落",
                                        "gender": "male_partner"
                                    }
                                }
                            },
                            {
                                "user": "现在一个人住，刚搬到新的公寓",
                                "expected_extractions": {
                                    "living_situation": {
                                        "type": "living_alone",
                                        "housing_change": "搬到新公寓",
                                        "time": "现在"
                                    }
                                }
                            },
                            {
                                "user": "朋友们都劝我要重新开始，但我觉得还需要时间",
                                "expected_extractions": {
                                    "emotional_recovery": {
                                        "social_support": "朋友劝导",
                                        "personal_readiness": "需要时间",
                                        "recovery_stage": "初期"
                                    }
                                }
                            }
                        ]
                    }
                ]
            },
            {
                "scenario_id": "temporal_information_extraction",
                "description": "测试提取时间相关信息的能力",
                "test_conversations": [
                    {
                        "conversation_id": "time_references",
                        "dialogue": [
                            {
                                "user": "去年这个时候我刚创业，现在公司已经有20个员工了",
                                "expected_extractions": {
                                    "business_timeline": {
                                        "start_time": "去年同期",
                                        "start_action": "创业",
                                        "current_status": "20个员工",
                                        "duration": "约一年"
                                    }
                                }
                            },
                            {
                                "user": "明年计划融资，希望能拿到A轮投资",
                                "expected_extractions": {
                                    "future_plans": {
                                        "time_frame": "明年",
                                        "goal": "A轮融资",
                                        "plan_type": "business_expansion"
                                    }
                                }
                            },
                            {
                                "user": "三个月前还在为资金发愁，没想到现在已经盈利了",
                                "expected_extractions": {
                                    "financial_timeline": {
                                        "past_situation": "资金发愁",
                                        "past_time": "三个月前",
                                        "current_situation": "盈利",
                                        "change_period": "三个月内"
                                    }
                                }
                            }
                        ]
                    }
                ]
            },
            {
                "scenario_id": "emotional_state_tracking",
                "description": "测试追踪用户情感状态变化的能力",
                "test_conversations": [
                    {
                        "conversation_id": "emotional_journey",
                        "dialogue": [
                            {
                                "user": "最近心情一直很低落，感觉做什么都没劲",
                                "expected_extractions": {
                                    "emotional_state": {
                                        "mood": "低落",
                                        "energy_level": "低",
                                        "duration": "最近持续",
                                        "impact": "影响行动力"
                                    }
                                }
                            },
                            {
                                "user": "主要是因为投资失败，损失了不少钱",
                                "expected_extractions": {
                                    "emotional_trigger": {
                                        "cause": "投资失败",
                                        "loss_type": "financial",
                                        "impact_degree": "significant"
                                    }
                                }
                            },
                            {
                                "user": "家人也在担心我，但我不想让他们跟着操心",
                                "expected_extractions": {
                                    "social_impact": {
                                        "family_concern": "担心",
                                        "user_attitude": "不想连累家人",
                                        "emotional_burden": "自我承担"
                                    }
                                }
                            }
                        ]
                    }
                ]
            },
            {
                "scenario_id": "health_status_extraction",
                "description": "测试提取健康状况信息的能力",
                "test_conversations": [
                    {
                        "conversation_id": "health_updates",
                        "dialogue": [
                            {
                                "user": "最近体检发现血压有点高，医生让我多注意饮食",
                                "expected_extractions": {
                                    "health_issue": {
                                        "condition": "高血压",
                                        "discovery_method": "体检",
                                        "time": "最近",
                                        "medical_advice": "注意饮食"
                                    }
                                }
                            },
                            {
                                "user": "现在每天都在坚持锻炼，希望能改善身体状况",
                                "expected_extractions": {
                                    "health_actions": {
                                        "action": "每日锻炼",
                                        "consistency": "坚持",
                                        "goal": "改善身体状况",
                                        "attitude": "积极"
                                    }
                                }
                            }
                        ]
                    }
                ]
            },
            {
                "scenario_id": "complex_multi_domain_extraction",
                "description": "测试复杂多领域信息的综合提取能力",
                "test_conversations": [
                    {
                        "conversation_id": "comprehensive_update",
                        "dialogue": [
                            {
                                "user": "这半年变化挺大的，换了工作，搬了家，还结了婚",
                                "expected_extractions": {
                                    "major_life_changes": {
                                        "time_frame": "半年内",
                                        "career": "换工作",
                                        "housing": "搬家",
                                        "relationship": "结婚",
                                        "change_intensity": "high"
                                    }
                                }
                            },
                            {
                                "user": "新工作在外地，所以和老婆一起搬过来了，她也在找工作",
                                "expected_extractions": {
                                    "relocation_details": {
                                        "trigger": "工作调动",
                                        "location": "外地",
                                        "accompanied_by": "配偶",
                                        "spouse_status": "求职中"
                                    }
                                }
                            },
                            {
                                "user": "现在最担心的就是买房问题，这边房价比老家高太多了",
                                "expected_extractions": {
                                    "current_concerns": {
                                        "primary_worry": "买房",
                                        "financial_pressure": "房价高",
                                        "comparison": "比老家高",
                                        "stress_level": "担心"
                                    }
                                }
                            }
                        ]
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
    
    def extract_information_from_text(self, text: str) -> Dict[str, Any]:
        """
        从文本中提取信息（示例实现）
        
        Args:
            text: 输入文本
            
        Returns:
            提取的信息字典
        """
        extracted_info = {
            "life_changes": [],
            "temporal_references": [],
            "emotional_indicators": [],
            "health_mentions": [],
            "financial_references": [],
            "relationship_changes": []
        }
        
        text_lower = text.lower()
        
        # 职业变化
        career_keywords = ["换工作", "跳槽", "新工作", "辞职", "升职", "创业"]
        for keyword in career_keywords:
            if keyword in text_lower:
                extracted_info["life_changes"].append({
                    "type": "career",
                    "keyword": keyword,
                    "context": text,
                    "confidence": 0.8
                })
        
        # 时间参考
        time_patterns = [
            r"(\d+)年前", r"(\d+)个月前", r"(\d+)天前",
            r"去年", r"今年", r"明年",
            r"最近", r"现在", r"将来"
        ]
        for pattern in time_patterns:
            matches = re.findall(pattern, text)
            if matches or pattern.replace(r"\d+", "").strip("()") in text:
                extracted_info["temporal_references"].append({
                    "pattern": pattern,
                    "context": text,
                    "confidence": 0.7
                })
        
        # 情感指标
        emotion_keywords = {
            "positive": ["开心", "满意", "高兴", "兴奋", "轻松"],
            "negative": ["难过", "沮丧", "焦虑", "担心", "压力大"],
            "neutral": ["平静", "一般", "还好", "普通"]
        }
        for emotion_type, keywords in emotion_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    extracted_info["emotional_indicators"].append({
                        "type": emotion_type,
                        "keyword": keyword,
                        "context": text,
                        "confidence": 0.6
                    })
        
        # 健康相关
        health_keywords = ["身体", "健康", "生病", "医院", "体检", "锻炼", "血压", "感冒"]
        for keyword in health_keywords:
            if keyword in text_lower:
                extracted_info["health_mentions"].append({
                    "keyword": keyword,
                    "context": text,
                    "confidence": 0.7
                })
        
        # 财务相关
        financial_keywords = ["钱", "投资", "收入", "薪水", "买房", "贷款", "理财"]
        for keyword in financial_keywords:
            if keyword in text_lower:
                extracted_info["financial_references"].append({
                    "keyword": keyword,
                    "context": text,
                    "confidence": 0.7
                })
        
        # 关系变化
        relationship_keywords = ["结婚", "分手", "离婚", "恋爱", "男朋友", "女朋友", "老婆", "老公"]
        for keyword in relationship_keywords:
            if keyword in text_lower:
                extracted_info["relationship_changes"].append({
                    "keyword": keyword,
                    "context": text,
                    "confidence": 0.8
                })
        
        return extracted_info
    
    def evaluate_extraction_accuracy(self, scenario_id: str, 
                                   user_inputs: List[str],
                                   ai_extractions: List[Dict]) -> Dict[str, float]:
        """
        评估信息提取准确性
        
        Args:
            scenario_id: 场景ID
            user_inputs: 用户输入列表
            ai_extractions: AI提取的信息列表
            
        Returns:
            评估分数字典
        """
        scores = {
            "recall": 0.0,           # 召回率
            "precision": 0.0,        # 精确率
            "temporal_accuracy": 0.0, # 时间信息准确性
            "completeness": 0.0,      # 完整性
            "overall": 0.0
        }
        
        scenario = self.get_scenario(scenario_id)
        if not scenario:
            return scores
        
        total_expected = 0
        correctly_extracted = 0
        total_extracted = 0
        
        # 遍历测试对话
        for conversation in scenario.get("test_conversations", []):
            for i, dialogue_turn in enumerate(conversation.get("dialogue", [])):
                expected = dialogue_turn.get("expected_extractions", {})
                
                if i < len(ai_extractions):
                    ai_extracted = ai_extractions[i]
                    
                    # 计算期望的提取项数量
                    for category, items in expected.items():
                        total_expected += 1
                        
                        # 检查AI是否提取到了对应的信息
                        if category in ai_extracted:
                            correctly_extracted += 1
                    
                    # 计算AI总共提取的项数量
                    for category, items in ai_extracted.items():
                        if items:  # 如果有内容
                            total_extracted += 1
        
        # 计算召回率和精确率
        if total_expected > 0:
            scores["recall"] = correctly_extracted / total_expected
        
        if total_extracted > 0:
            scores["precision"] = correctly_extracted / total_extracted
        
        # 评估时间信息准确性
        if scenario_id == "temporal_information_extraction":
            time_accuracy_count = 0
            time_total_count = 0
            
            for extraction in ai_extractions:
                for category, content in extraction.items():
                    if "time" in category.lower() or "temporal" in category.lower():
                        time_total_count += 1
                        # 简化评估：检查是否包含时间相关词汇
                        time_words = ["年前", "月前", "天前", "去年", "今年", "明年", "最近", "现在"]
                        if any(word in str(content) for word in time_words):
                            time_accuracy_count += 1
            
            if time_total_count > 0:
                scores["temporal_accuracy"] = time_accuracy_count / time_total_count
        
        # 评估完整性（是否遗漏重要信息类别）
        expected_categories = set()
        extracted_categories = set()
        
        for conversation in scenario.get("test_conversations", []):
            for dialogue_turn in conversation.get("dialogue", []):
                expected_categories.update(dialogue_turn.get("expected_extractions", {}).keys())
        
        for extraction in ai_extractions:
            extracted_categories.update(extraction.keys())
        
        if expected_categories:
            completeness_ratio = len(expected_categories.intersection(extracted_categories)) / len(expected_categories)
            scores["completeness"] = completeness_ratio
        
        # 计算F1分数作为总体评估
        if scores["recall"] + scores["precision"] > 0:
            f1_score = 2 * (scores["recall"] * scores["precision"]) / (scores["recall"] + scores["precision"])
            scores["overall"] = f1_score
        
        return scores
    
    def generate_test_report(self, scenario_id: str, evaluation_results: Dict[str, float]) -> Dict[str, Any]:
        """
        生成测试报告
        
        Args:
            scenario_id: 场景ID
            evaluation_results: 评估结果
            
        Returns:
            测试报告字典
        """
        scenario = self.get_scenario(scenario_id)
        
        report = {
            "scenario_id": scenario_id,
            "scenario_description": scenario.get("description", "") if scenario else "",
            "evaluation_results": evaluation_results,
            "performance_level": self._get_performance_level(evaluation_results.get("overall", 0)),
            "recommendations": self._generate_recommendations(scenario_id, evaluation_results),
            "timestamp": datetime.now().isoformat()
        }
        
        return report
    
    def _get_performance_level(self, overall_score: float) -> str:
        """根据总体分数判断性能等级"""
        if overall_score >= 0.8:
            return "优秀"
        elif overall_score >= 0.6:
            return "良好"
        elif overall_score >= 0.4:
            return "一般"
        else:
            return "需要改进"
    
    def _generate_recommendations(self, scenario_id: str, results: Dict[str, float]) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        if results.get("recall", 0) < 0.6:
            recommendations.append("提高信息识别的敏感度，可能遗漏了重要信息")
        
        if results.get("precision", 0) < 0.6:
            recommendations.append("提高信息提取的准确性，减少误报")
        
        if results.get("temporal_accuracy", 0) < 0.7:
            recommendations.append("改进时间信息的识别和解析能力")
        
        if results.get("completeness", 0) < 0.7:
            recommendations.append("增强多领域信息的综合提取能力")
        
        return recommendations