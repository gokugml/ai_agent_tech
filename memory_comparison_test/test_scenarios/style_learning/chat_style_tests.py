"""
聊天风格学习测试场景

测试 AI 学习用户聊天风格偏好的能力
"""

from typing import Dict, List, Any
import json

class ChatStyleTestScenarios:
    """聊天风格测试场景集合"""
    
    def __init__(self):
        self.test_cases = self._load_test_cases()
    
    def _load_test_cases(self) -> List[Dict[str, Any]]:
        """加载测试用例"""
        return [
            {
                "scenario_id": "concise_preference",
                "description": "测试用户偏好简洁回复的学习能力",
                "user_type": "简洁型用户",
                "conversation_rounds": [
                    {
                        "round": 1,
                        "user_input": "我最近运势怎么样？",
                        "expected_ai_style": "详细解释",
                        "user_feedback_signals": ["太长了", "简单点说"],
                        "style_indicators": {"verbosity": -1.0, "detail_level": -0.8}
                    },
                    {
                        "round": 2,
                        "user_input": "我的财运如何？",
                        "expected_ai_style": "中等详细度",
                        "user_feedback_signals": ["还是太复杂", "直接告诉我结果"],
                        "style_indicators": {"verbosity": -1.5, "directness": 1.0}
                    },
                    {
                        "round": 3,
                        "user_input": "感情方面有什么预测吗？",
                        "expected_ai_style": "简洁回复",
                        "user_feedback_signals": ["这样刚好", "简洁明了"],
                        "style_indicators": {"verbosity": 0.5, "satisfaction": 1.0}
                    },
                    {
                        "round": 4,
                        "user_input": "明年工作运势怎样？",
                        "expected_ai_adaptation": "应该给出简洁的回复",
                        "evaluation_criteria": {
                            "response_length": "短（< 50字）",
                            "detail_level": "低",
                            "structure": "直接结论"
                        }
                    }
                ]
            },
            {
                "scenario_id": "detailed_preference", 
                "description": "测试用户偏好详细解释的学习能力",
                "user_type": "详细型用户",
                "conversation_rounds": [
                    {
                        "round": 1,
                        "user_input": "我的八字分析结果是什么？",
                        "expected_ai_style": "标准回复",
                        "user_feedback_signals": ["为什么是这样？", "能详细解释吗？"],
                        "style_indicators": {"curiosity": 1.0, "detail_demand": 1.0}
                    },
                    {
                        "round": 2,
                        "user_input": "这个预测的依据是什么？",
                        "expected_ai_style": "增加解释",
                        "user_feedback_signals": ["还有其他原因吗？", "背景是什么？"],
                        "style_indicators": {"depth_seeking": 1.5, "explanation_need": 1.2}
                    },
                    {
                        "round": 3,
                        "user_input": "我的五行缺什么？",
                        "expected_ai_style": "详细分析",
                        "user_feedback_signals": ["很好", "这样解释很清楚"],
                        "style_indicators": {"satisfaction": 1.0, "detail_appreciation": 1.0}
                    },
                    {
                        "round": 4,
                        "user_input": "未来一年的运势展望？",
                        "expected_ai_adaptation": "应该提供详细的分析和背景解释",
                        "evaluation_criteria": {
                            "response_length": "长（> 150字）",
                            "detail_level": "高",
                            "explanation_depth": "包含原理和背景"
                        }
                    }
                ]
            },
            {
                "scenario_id": "interactive_preference",
                "description": "测试用户偏好互动式交流的学习能力", 
                "user_type": "互动型用户",
                "conversation_rounds": [
                    {
                        "round": 1,
                        "user_input": "帮我看看运势",
                        "expected_ai_style": "标准回复",
                        "user_feedback_signals": ["我想知道具体哪方面", "你觉得我应该注意什么？"],
                        "style_indicators": {"interaction_seeking": 1.0, "guidance_need": 1.0}
                    },
                    {
                        "round": 2,
                        "user_input": "那感情方面呢？",
                        "expected_ai_style": "增加互动元素",
                        "user_feedback_signals": ["我应该怎么做？", "你有什么建议？"],
                        "style_indicators": {"advice_seeking": 1.2, "engagement_level": 1.5}
                    },
                    {
                        "round": 3,
                        "user_input": "工作上有什么需要注意的？",
                        "expected_ai_style": "互动式回复",
                        "user_feedback_signals": ["这个建议不错", "我想听更多意见"],
                        "style_indicators": {"satisfaction": 1.0, "interaction_preference": 1.0}
                    },
                    {
                        "round": 4,
                        "user_input": "整体来看我今年怎么样？",
                        "expected_ai_adaptation": "应该主动提问和给出建议",
                        "evaluation_criteria": {
                            "interaction_elements": "包含问题和建议",
                            "engagement_level": "高",
                            "advice_provision": "主动提供指导"
                        }
                    }
                ]
            },
            {
                "scenario_id": "formal_vs_casual",
                "description": "测试正式与随意语言风格的适应能力",
                "user_type": "随意型用户", 
                "conversation_rounds": [
                    {
                        "round": 1,
                        "user_input": "大师，我想算算命",
                        "expected_ai_style": "正式专业语调",
                        "user_feedback_signals": ["别这么正式啦", "随便聊聊就行"],
                        "style_indicators": {"formality": -1.0, "casualness": 1.0}
                    },
                    {
                        "round": 2,
                        "user_input": "我这人运气一直不好，咋回事？",
                        "expected_ai_style": "放松语调",
                        "user_feedback_signals": ["哈哈对", "就是这个意思"],
                        "style_indicators": {"casualness": 1.2, "comfort_level": 1.0}
                    },
                    {
                        "round": 3,
                        "user_input": "那我应该注意啥？",
                        "expected_ai_style": "口语化回复",
                        "user_feedback_signals": ["说得挺对", "感觉很亲切"],
                        "style_indicators": {"satisfaction": 1.0, "rapport": 1.0}
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
    
    def get_all_scenarios(self) -> List[Dict[str, Any]]:
        """获取所有测试场景"""
        return self.test_cases
    
    def evaluate_style_adaptation(self, scenario_id: str, ai_responses: List[str]) -> Dict[str, float]:
        """
        评估AI的风格适应效果
        
        Args:
            scenario_id: 场景ID
            ai_responses: AI在各轮的回复
            
        Returns:
            评估分数字典
        """
        scenario = self.get_scenario(scenario_id)
        if not scenario:
            return {"error": 1.0}
        
        scores = {
            "adaptation_speed": 0.0,
            "final_match": 0.0,
            "consistency": 0.0,
            "overall": 0.0
        }
        
        rounds = scenario["conversation_rounds"]
        
        # 简化的评估逻辑
        for i, response in enumerate(ai_responses):
            if i < len(rounds):
                round_data = rounds[i]
                
                # 根据场景类型评估
                if scenario["scenario_id"] == "concise_preference":
                    # 评估回复长度是否逐渐变短
                    expected_length = max(50 - i * 15, 20)  # 逐渐缩短
                    actual_length = len(response)
                    length_score = max(0, 1 - abs(actual_length - expected_length) / expected_length)
                    scores["adaptation_speed"] += length_score / len(ai_responses)
                
                elif scenario["scenario_id"] == "detailed_preference":
                    # 评估回复是否逐渐变得更详细
                    expected_length = min(50 + i * 30, 200)  # 逐渐增长
                    actual_length = len(response)
                    length_score = max(0, 1 - abs(actual_length - expected_length) / expected_length)
                    scores["adaptation_speed"] += length_score / len(ai_responses)
                
                elif scenario["scenario_id"] == "interactive_preference":
                    # 评估互动元素（问号数量作为简单指标）
                    question_count = response.count('？') + response.count('?')
                    interaction_score = min(question_count / 2, 1.0)  # 期望有1-2个问题
                    scores["adaptation_speed"] += interaction_score / len(ai_responses)
        
        # 计算最终匹配度（基于最后一轮回复）
        if ai_responses and len(rounds) > 0:
            final_round = rounds[-1]
            final_response = ai_responses[-1]
            
            if "evaluation_criteria" in final_round:
                criteria = final_round["evaluation_criteria"]
                
                if "response_length" in criteria:
                    if "短" in criteria["response_length"] and len(final_response) < 50:
                        scores["final_match"] += 0.5
                    elif "长" in criteria["response_length"] and len(final_response) > 150:
                        scores["final_match"] += 0.5
                
                if "interaction_elements" in criteria:
                    if "问题" in criteria["interaction_elements"] and ('？' in final_response or '?' in final_response):
                        scores["final_match"] += 0.3
                    if "建议" in criteria["interaction_elements"] and ('建议' in final_response or '应该' in final_response):
                        scores["final_match"] += 0.2
        
        # 计算一致性（回复风格的稳定性）
        if len(ai_responses) > 1:
            length_variance = np.var([len(r) for r in ai_responses])
            scores["consistency"] = max(0, 1 - length_variance / 1000)  # 归一化方差
        
        # 计算总体得分
        scores["overall"] = (scores["adaptation_speed"] + scores["final_match"] + scores["consistency"]) / 3
        
        return scores


# 添加numpy导入（简化版本）
try:
    import numpy as np
except ImportError:
    # 如果没有numpy，使用简单的方差计算
    class SimpleNP:
        @staticmethod
        def var(data):
            if len(data) <= 1:
                return 0
            mean = sum(data) / len(data)
            return sum((x - mean) ** 2 for x in data) / len(data)
    
    np = SimpleNP()