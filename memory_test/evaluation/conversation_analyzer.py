"""
对话分析器

深入分析AI与用户的对话质量、模式和趋势
"""

import json
import re
import statistics
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from collections import defaultdict, Counter

from loguru import logger

from ..response_testing.real_ai_tester import AIResponse, TestSession
from ..response_testing.response_evaluator import ResponseQuality, ConversationEvaluation


@dataclass
class ConversationPattern:
    """对话模式数据类"""
    pattern_id: str
    pattern_type: str  # "topic_flow", "interaction_style", "memory_usage"
    description: str
    frequency: int
    confidence: float  # 0-1
    examples: List[str]
    metadata: Dict[str, Any]


@dataclass
class ConversationTrend:
    """对话趋势数据类"""
    trend_id: str
    trend_type: str  # "quality_improvement", "response_time", "memory_utilization"
    direction: str  # "increasing", "decreasing", "stable"
    trend_strength: float  # 0-1
    time_period: str
    data_points: List[Tuple[str, float]]  # (timestamp, value)
    analysis_summary: str


@dataclass
class UserBehaviorProfile:
    """用户行为画像"""
    user_id: str
    communication_patterns: Dict[str, Any]
    preference_indicators: Dict[str, float]
    interaction_frequency: Dict[str, int]
    topic_interests: Dict[str, float]
    engagement_metrics: Dict[str, float]
    behavioral_insights: List[str]


class ConversationAnalyzer:
    """对话分析器"""
    
    def __init__(self):
        # 话题分类关键词
        self.topic_keywords = {
            "事业发展": ["工作", "职业", "事业", "升职", "跳槽", "同事", "老板", "公司"],
            "感情关系": ["恋爱", "结婚", "分手", "感情", "爱情", "对象", "夫妻", "伴侣"],
            "财富运势": ["钱", "财运", "投资", "理财", "收入", "财富", "买房", "股票"],
            "健康养生": ["健康", "身体", "生病", "医院", "保养", "养生", "锻炼", "饮食"],
            "学习成长": ["学习", "考试", "技能", "知识", "成长", "进修", "培训", "书籍"],
            "人际关系": ["朋友", "人际", "社交", "交往", "沟通", "关系", "合作", "团队"],
            "家庭生活": ["家庭", "父母", "子女", "孩子", "家人", "亲情", "教育", "照顾"]
        }
        
        # 情感色彩关键词
        self.emotion_keywords = {
            "积极": ["开心", "高兴", "满意", "喜欢", "好", "棒", "赞", "感谢", "期待"],
            "消极": ["担心", "焦虑", "烦恼", "困扰", "不好", "失望", "沮丧", "害怕", "难过"],
            "中性": ["了解", "知道", "明白", "清楚", "认为", "觉得", "可能", "也许", "或许"]
        }
        
        # 交互模式关键词
        self.interaction_patterns = {
            "求助型": ["请帮助", "怎么办", "求指导", "给建议", "不知道怎么"],
            "验证型": ["是否", "对吗", "准确吗", "会不会", "有可能"],
            "探索型": ["为什么", "如何", "什么原因", "怎么样", "详细说说"],
            "反馈型": ["确实", "果然", "正如", "你说得对", "很准确"]
        }
    
    def analyze_single_conversation(self, 
                                  responses: List[AIResponse],
                                  session_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """分析单个对话"""
        
        if not responses:
            return {"error": "没有对话数据"}
        
        logger.info(f"开始分析对话: {len(responses)} 轮交互")
        
        analysis = {
            "conversation_id": responses[0].session_id,
            "basic_metrics": self._calculate_basic_metrics(responses),
            "topic_analysis": self._analyze_topics(responses),
            "emotion_analysis": self._analyze_emotions(responses),
            "interaction_patterns": self._analyze_interaction_patterns(responses),
            "memory_usage_analysis": self._analyze_memory_usage(responses),
            "quality_progression": self._analyze_quality_progression(responses),
            "user_behavior": self._analyze_user_behavior(responses),
            "conversation_flow": self._analyze_conversation_flow(responses),
            "insights_and_recommendations": []
        }
        
        # 生成洞察和建议
        analysis["insights_and_recommendations"] = self._generate_insights(analysis)
        
        logger.info(f"对话分析完成: {responses[0].session_id}")
        return analysis
    
    def _calculate_basic_metrics(self, responses: List[AIResponse]) -> Dict[str, Any]:
        """计算基础指标"""
        
        total_interactions = len(responses)
        total_response_time = sum(r.response_time for r in responses)
        avg_response_time = total_response_time / total_interactions
        
        # 统计token使用
        total_input_tokens = sum(r.token_usage.get("input_tokens", 0) for r in responses)
        total_output_tokens = sum(r.token_usage.get("output_tokens", 0) for r in responses)
        
        # 统计回复长度
        response_lengths = [len(r.ai_response) for r in responses]
        user_input_lengths = [len(r.user_input) for r in responses]
        
        # 计算时间分布
        timestamps = [datetime.fromisoformat(r.timestamp.replace("Z", "+00:00")) for r in responses]
        if len(timestamps) > 1:
            conversation_duration = (timestamps[-1] - timestamps[0]).total_seconds()
            avg_interaction_interval = conversation_duration / (len(timestamps) - 1)
        else:
            conversation_duration = 0
            avg_interaction_interval = 0
        
        return {
            "total_interactions": total_interactions,
            "conversation_duration_seconds": conversation_duration,
            "avg_response_time": avg_response_time,
            "total_response_time": total_response_time,
            "avg_interaction_interval": avg_interaction_interval,
            "token_usage": {
                "total_input_tokens": total_input_tokens,
                "total_output_tokens": total_output_tokens,
                "total_tokens": total_input_tokens + total_output_tokens,
                "avg_input_tokens": total_input_tokens / total_interactions,
                "avg_output_tokens": total_output_tokens / total_interactions
            },
            "content_metrics": {
                "avg_response_length": statistics.mean(response_lengths),
                "avg_user_input_length": statistics.mean(user_input_lengths),
                "response_length_variance": statistics.variance(response_lengths) if len(response_lengths) > 1 else 0,
                "max_response_length": max(response_lengths),
                "min_response_length": min(response_lengths)
            }
        }
    
    def _analyze_topics(self, responses: List[AIResponse]) -> Dict[str, Any]:
        """分析话题分布"""
        
        topic_counts = defaultdict(int)
        topic_transitions = []
        current_topics = []
        
        for i, response in enumerate(responses):
            # 分析用户输入和AI回复的话题
            user_topics = self._classify_topics(response.user_input)
            ai_topics = self._classify_topics(response.ai_response)
            
            # 统计话题出现次数
            for topic in user_topics + ai_topics:
                topic_counts[topic] += 1
            
            # 分析话题转换
            if i > 0 and current_topics:
                new_topics = set(user_topics) - set(current_topics)
                if new_topics:
                    topic_transitions.append({
                        "from_topics": current_topics.copy(),
                        "to_topics": list(new_topics),
                        "interaction_index": i
                    })
            
            current_topics = user_topics
        
        # 计算话题分布
        total_topic_mentions = sum(topic_counts.values())
        topic_distribution = {
            topic: count / total_topic_mentions 
            for topic, count in topic_counts.items()
        } if total_topic_mentions > 0 else {}
        
        # 识别主要话题
        main_topics = sorted(topic_distribution.items(), 
                           key=lambda x: x[1], reverse=True)[:3]
        
        return {
            "topic_distribution": topic_distribution,
            "main_topics": main_topics,
            "topic_transitions": topic_transitions,
            "topic_diversity": len(topic_counts),
            "topic_focus_score": max(topic_distribution.values()) if topic_distribution else 0,
            "conversation_coherence": self._calculate_topic_coherence(topic_transitions, len(responses))
        }
    
    def _classify_topics(self, text: str) -> List[str]:
        """分类话题"""
        text_lower = text.lower()
        detected_topics = []
        
        for topic, keywords in self.topic_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                detected_topics.append(topic)
        
        return detected_topics if detected_topics else ["其他"]
    
    def _calculate_topic_coherence(self, transitions: List[Dict], total_interactions: int) -> float:
        """计算话题连贯性"""
        if total_interactions <= 1:
            return 1.0
        
        # 话题转换越少，连贯性越高
        transition_rate = len(transitions) / (total_interactions - 1)
        coherence_score = max(0.0, 1.0 - transition_rate)
        return coherence_score
    
    def _analyze_emotions(self, responses: List[AIResponse]) -> Dict[str, Any]:
        """分析情感趋势"""
        
        emotion_progression = []
        emotion_counts = defaultdict(int)
        
        for i, response in enumerate(responses):
            user_emotion = self._classify_emotion(response.user_input)
            ai_emotion = self._classify_emotion(response.ai_response)
            
            emotion_counts[user_emotion] += 1
            
            emotion_progression.append({
                "interaction_index": i,
                "user_emotion": user_emotion,
                "ai_emotion": ai_emotion,
                "timestamp": response.timestamp
            })
        
        # 计算情感分布
        total_emotions = sum(emotion_counts.values())
        emotion_distribution = {
            emotion: count / total_emotions 
            for emotion, count in emotion_counts.items()
        } if total_emotions > 0 else {}
        
        # 分析情感变化趋势
        emotion_trend = self._analyze_emotion_trend(emotion_progression)
        
        return {
            "emotion_distribution": emotion_distribution,
            "emotion_progression": emotion_progression,
            "emotion_trend": emotion_trend,
            "dominant_emotion": max(emotion_distribution.items(), key=lambda x: x[1])[0] if emotion_distribution else "中性",
            "emotional_stability": self._calculate_emotional_stability(emotion_progression)
        }
    
    def _classify_emotion(self, text: str) -> str:
        """分类情感"""
        text_lower = text.lower()
        emotion_scores = defaultdict(int)
        
        for emotion, keywords in self.emotion_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    emotion_scores[emotion] += 1
        
        if not emotion_scores:
            return "中性"
        
        return max(emotion_scores.items(), key=lambda x: x[1])[0]
    
    def _analyze_emotion_trend(self, progression: List[Dict]) -> Dict[str, Any]:
        """分析情感趋势"""
        if len(progression) < 3:
            return {"trend": "stable", "confidence": 0.5}
        
        # 将情感转换为数值
        emotion_values = {
            "消极": -1,
            "中性": 0,
            "积极": 1
        }
        
        values = []
        for item in progression:
            emotion = item["user_emotion"]
            values.append(emotion_values.get(emotion, 0))
        
        # 计算趋势
        if len(values) > 1:
            # 简单线性回归
            x = list(range(len(values)))
            n = len(values)
            
            sum_x = sum(x)
            sum_y = sum(values)
            sum_xy = sum(x[i] * values[i] for i in range(n))
            sum_x2 = sum(xi * xi for xi in x)
            
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x) if (n * sum_x2 - sum_x * sum_x) != 0 else 0
            
            if slope > 0.1:
                trend = "improving"
            elif slope < -0.1:
                trend = "declining"
            else:
                trend = "stable"
            
            confidence = min(1.0, abs(slope) * 2)
        else:
            trend = "stable"
            confidence = 0.5
        
        return {
            "trend": trend,
            "slope": slope if 'slope' in locals() else 0,
            "confidence": confidence
        }
    
    def _calculate_emotional_stability(self, progression: List[Dict]) -> float:
        """计算情感稳定性"""
        if len(progression) < 2:
            return 1.0
        
        # 统计情感变化次数
        changes = 0
        for i in range(1, len(progression)):
            if progression[i]["user_emotion"] != progression[i-1]["user_emotion"]:
                changes += 1
        
        # 稳定性 = 1 - 变化率
        stability = 1.0 - (changes / (len(progression) - 1))
        return max(0.0, stability)
    
    def _analyze_interaction_patterns(self, responses: List[AIResponse]) -> Dict[str, Any]:
        """分析交互模式"""
        
        pattern_counts = defaultdict(int)
        pattern_sequence = []
        
        for i, response in enumerate(responses):
            user_pattern = self._classify_interaction_pattern(response.user_input)
            pattern_counts[user_pattern] += 1
            pattern_sequence.append({
                "interaction_index": i,
                "pattern": user_pattern,
                "user_input_length": len(response.user_input),
                "ai_response_length": len(response.ai_response)
            })
        
        # 计算模式分布
        total_patterns = sum(pattern_counts.values())
        pattern_distribution = {
            pattern: count / total_patterns 
            for pattern, count in pattern_counts.items()
        } if total_patterns > 0 else {}
        
        # 分析模式转换
        pattern_transitions = []
        for i in range(1, len(pattern_sequence)):
            if pattern_sequence[i]["pattern"] != pattern_sequence[i-1]["pattern"]:
                pattern_transitions.append({
                    "from_pattern": pattern_sequence[i-1]["pattern"],
                    "to_pattern": pattern_sequence[i]["pattern"],
                    "interaction_index": i
                })
        
        return {
            "pattern_distribution": pattern_distribution,
            "pattern_sequence": pattern_sequence,
            "pattern_transitions": pattern_transitions,
            "dominant_pattern": max(pattern_distribution.items(), key=lambda x: x[1])[0] if pattern_distribution else "探索型",
            "pattern_consistency": self._calculate_pattern_consistency(pattern_sequence)
        }
    
    def _classify_interaction_pattern(self, text: str) -> str:
        """分类交互模式"""
        text_lower = text.lower()
        pattern_scores = defaultdict(int)
        
        for pattern, keywords in self.interaction_patterns.items():
            for keyword in keywords:
                if keyword in text_lower:
                    pattern_scores[pattern] += 1
        
        if not pattern_scores:
            return "探索型"  # 默认模式
        
        return max(pattern_scores.items(), key=lambda x: x[1])[0]
    
    def _calculate_pattern_consistency(self, sequence: List[Dict]) -> float:
        """计算模式一致性"""
        if len(sequence) < 2:
            return 1.0
        
        # 统计最频繁的模式
        patterns = [item["pattern"] for item in sequence]
        pattern_counts = Counter(patterns)
        most_common_pattern = pattern_counts.most_common(1)[0][0]
        
        # 一致性 = 主要模式出现比例
        consistency = pattern_counts[most_common_pattern] / len(patterns)
        return consistency
    
    def _analyze_memory_usage(self, responses: List[AIResponse]) -> Dict[str, Any]:
        """分析记忆使用情况"""
        
        memory_usage_stats = {
            "total_responses": len(responses),
            "responses_with_memory": 0,
            "avg_memory_context_size": 0,
            "memory_utilization_rate": 0,
            "memory_effectiveness_scores": []
        }
        
        memory_contexts = []
        
        for response in responses:
            has_memory = bool(response.memory_context)
            memory_usage_stats["responses_with_memory"] += int(has_memory)
            
            context_size = len(response.memory_context) if response.memory_context else 0
            
            # 分析记忆有效性
            effectiveness_score = self._calculate_memory_effectiveness(
                response.user_input,
                response.ai_response,
                response.memory_context
            )
            
            memory_context_data = {
                "response_id": response.response_id,
                "has_memory": has_memory,
                "context_size": context_size,
                "effectiveness_score": effectiveness_score,
                "memory_types": list(response.memory_context.get("memory_types", [])) if response.memory_context else []
            }
            
            memory_contexts.append(memory_context_data)
            
            if has_memory:
                memory_usage_stats["memory_effectiveness_scores"].append(effectiveness_score)
        
        # 计算统计指标
        if memory_usage_stats["responses_with_memory"] > 0:
            memory_usage_stats["memory_utilization_rate"] = memory_usage_stats["responses_with_memory"] / len(responses)
            
            contexts_with_memory = [ctx for ctx in memory_contexts if ctx["has_memory"]]
            memory_usage_stats["avg_memory_context_size"] = statistics.mean([ctx["context_size"] for ctx in contexts_with_memory])
            
            if memory_usage_stats["memory_effectiveness_scores"]:
                memory_usage_stats["avg_memory_effectiveness"] = statistics.mean(memory_usage_stats["memory_effectiveness_scores"])
        
        return {
            "usage_statistics": memory_usage_stats,
            "memory_contexts": memory_contexts,
            "memory_trends": self._analyze_memory_trends(memory_contexts)
        }
    
    def _calculate_memory_effectiveness(self, 
                                     user_input: str,
                                     ai_response: str,
                                     memory_context: Optional[Dict[str, Any]]) -> float:
        """计算记忆有效性"""
        if not memory_context:
            return 0.0
        
        effectiveness_score = 0.0
        
        # 检查记忆引用
        memory_reference_indicators = ["之前", "上次", "根据您的", "如您所说", "您提到的"]
        if any(indicator in ai_response for indicator in memory_reference_indicators):
            effectiveness_score += 0.3
        
        # 检查上下文相关性
        context_summary = memory_context.get("context_summary", "")
        if context_summary:
            # 简单的关键词匹配
            user_words = set(user_input.lower().split())
            context_words = set(context_summary.lower().split())
            
            if user_words.intersection(context_words):
                effectiveness_score += 0.4
        
        # 检查记忆类型多样性
        memory_types = memory_context.get("memory_types", [])
        if len(memory_types) > 1:
            effectiveness_score += 0.2
        
        # 检查相关性分数
        relevance_scores = memory_context.get("relevance_scores", {})
        if relevance_scores:
            avg_relevance = statistics.mean(relevance_scores.values())
            effectiveness_score += avg_relevance * 0.1
        
        return min(1.0, effectiveness_score)
    
    def _analyze_memory_trends(self, memory_contexts: List[Dict]) -> Dict[str, Any]:
        """分析记忆使用趋势"""
        if len(memory_contexts) < 3:
            return {"trend": "insufficient_data"}
        
        # 分析记忆使用频率趋势
        usage_progression = [ctx["has_memory"] for ctx in memory_contexts]
        
        # 分析有效性趋势
        effectiveness_progression = [
            ctx["effectiveness_score"] for ctx in memory_contexts if ctx["has_memory"]
        ]
        
        trends = {
            "memory_usage_trend": self._calculate_binary_trend(usage_progression),
            "context_size_trend": self._calculate_numeric_trend([ctx["context_size"] for ctx in memory_contexts])
        }
        
        if effectiveness_progression:
            trends["effectiveness_trend"] = self._calculate_numeric_trend(effectiveness_progression)
        
        return trends
    
    def _calculate_binary_trend(self, values: List[bool]) -> Dict[str, Any]:
        """计算二元趋势"""
        if len(values) < 3:
            return {"trend": "stable", "confidence": 0.0}
        
        # 计算滑动窗口平均
        window_size = 3
        averages = []
        for i in range(len(values) - window_size + 1):
            window = values[i:i + window_size]
            avg = sum(window) / len(window)
            averages.append(avg)
        
        if len(averages) < 2:
            return {"trend": "stable", "confidence": 0.0}
        
        # 比较首末平均值
        start_avg = averages[0]
        end_avg = averages[-1]
        
        diff = end_avg - start_avg
        
        if diff > 0.2:
            trend = "increasing"
        elif diff < -0.2:
            trend = "decreasing"
        else:
            trend = "stable"
        
        confidence = min(1.0, abs(diff) * 2)
        
        return {"trend": trend, "confidence": confidence, "change": diff}
    
    def _calculate_numeric_trend(self, values: List[float]) -> Dict[str, Any]:
        """计算数值趋势"""
        if len(values) < 3:
            return {"trend": "stable", "confidence": 0.0}
        
        # 简单线性回归
        x = list(range(len(values)))
        n = len(values)
        
        sum_x = sum(x)
        sum_y = sum(values)
        sum_xy = sum(x[i] * values[i] for i in range(n))
        sum_x2 = sum(xi * xi for xi in x)
        
        if (n * sum_x2 - sum_x * sum_x) == 0:
            return {"trend": "stable", "confidence": 0.0}
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        
        # 判断趋势方向
        avg_value = statistics.mean(values)
        relative_slope = slope / avg_value if avg_value != 0 else 0
        
        if relative_slope > 0.1:
            trend = "increasing"
        elif relative_slope < -0.1:
            trend = "decreasing"
        else:
            trend = "stable"
        
        confidence = min(1.0, abs(relative_slope) * 5)
        
        return {"trend": trend, "slope": slope, "confidence": confidence}
    
    def _analyze_quality_progression(self, responses: List[AIResponse]) -> Dict[str, Any]:
        """分析质量发展趋势"""
        
        # 这里需要ResponseQualityEvaluator的结果，但为了保持独立性，我们使用简化的质量评估
        quality_scores = []
        
        for response in responses:
            # 简化的质量评估
            quality_score = self._simple_quality_assessment(response)
            quality_scores.append({
                "response_id": response.response_id,
                "quality_score": quality_score,
                "response_time": response.response_time,
                "timestamp": response.timestamp
            })
        
        # 计算质量趋势
        scores = [item["quality_score"] for item in quality_scores]
        quality_trend = self._calculate_numeric_trend(scores)
        
        # 计算响应时间趋势
        response_times = [item["response_time"] for item in quality_scores]
        time_trend = self._calculate_numeric_trend(response_times)
        
        return {
            "quality_scores": quality_scores,
            "quality_trend": quality_trend,
            "response_time_trend": time_trend,
            "avg_quality": statistics.mean(scores),
            "quality_variance": statistics.variance(scores) if len(scores) > 1 else 0,
            "best_quality_score": max(scores),
            "worst_quality_score": min(scores)
        }
    
    def _simple_quality_assessment(self, response: AIResponse) -> float:
        """简化的质量评估"""
        score = 0.5  # 基础分数
        
        ai_response = response.ai_response
        user_input = response.user_input
        
        # 回复长度适中性
        if 50 <= len(ai_response) <= 300:
            score += 0.1
        
        # 专业术语使用
        professional_terms = ["八字", "运势", "建议", "分析", "预测"]
        term_count = sum(1 for term in professional_terms if term in ai_response)
        score += min(0.2, term_count * 0.05)
        
        # 回复相关性（简单关键词匹配）
        user_words = set(user_input.lower().split())
        ai_words = set(ai_response.lower().split())
        
        if user_words.intersection(ai_words):
            score += 0.1
        
        # 记忆使用
        if response.memory_context:
            score += 0.1
        
        return min(1.0, score)
    
    def _analyze_user_behavior(self, responses: List[AIResponse]) -> UserBehaviorProfile:
        """分析用户行为模式"""
        
        user_inputs = [response.user_input for response in responses]
        
        # 通信模式分析
        communication_patterns = {
            "avg_input_length": statistics.mean([len(inp) for inp in user_inputs]),
            "input_length_variance": statistics.variance([len(inp) for inp in user_inputs]) if len(user_inputs) > 1 else 0,
            "question_ratio": sum(1 for inp in user_inputs if "？" in inp or "?" in inp) / len(user_inputs),
            "politeness_indicators": sum(1 for inp in user_inputs if any(word in inp for word in ["请", "谢谢", "您"])) / len(user_inputs)
        }
        
        # 偏好指标
        preference_indicators = {
            "detail_preference": sum(1 for inp in user_inputs if len(inp) > 100) / len(user_inputs),
            "urgent_queries": sum(1 for inp in user_inputs if any(word in inp for word in ["急", "尽快", "马上"])) / len(user_inputs),
            "follow_up_questions": sum(1 for inp in user_inputs if any(word in inp for word in ["还有", "另外", "再"])) / len(user_inputs)
        }
        
        # 交互频率分析
        timestamps = [datetime.fromisoformat(r.timestamp.replace("Z", "+00:00")) for r in responses]
        if len(timestamps) > 1:
            intervals = [(timestamps[i+1] - timestamps[i]).total_seconds() for i in range(len(timestamps)-1)]
            avg_interval = statistics.mean(intervals)
        else:
            avg_interval = 0
        
        interaction_frequency = {
            "total_interactions": len(responses),
            "avg_interaction_interval": avg_interval,
            "rapid_interactions": sum(1 for interval in (intervals if 'intervals' in locals() else []) if interval < 30)
        }
        
        # 话题兴趣分析
        all_text = " ".join(user_inputs)
        topic_interests = {}
        for topic, keywords in self.topic_keywords.items():
            interest_score = sum(1 for keyword in keywords if keyword in all_text.lower()) / len(keywords)
            topic_interests[topic] = interest_score
        
        # 参与度指标
        engagement_metrics = {
            "response_rate": 1.0,  # 假设用户总是回复
            "session_length": len(responses),
            "content_richness": statistics.mean([len(inp.split()) for inp in user_inputs]),
            "emotional_engagement": self._calculate_emotional_engagement(user_inputs)
        }
        
        # 行为洞察
        behavioral_insights = self._generate_behavioral_insights(
            communication_patterns, preference_indicators, topic_interests, engagement_metrics
        )
        
        return UserBehaviorProfile(
            user_id=responses[0].session_id,  # 使用session_id作为用户标识
            communication_patterns=communication_patterns,
            preference_indicators=preference_indicators,
            interaction_frequency=interaction_frequency,
            topic_interests=topic_interests,
            engagement_metrics=engagement_metrics,
            behavioral_insights=behavioral_insights
        )
    
    def _calculate_emotional_engagement(self, user_inputs: List[str]) -> float:
        """计算情感参与度"""
        emotional_words = []
        for category, keywords in self.emotion_keywords.items():
            emotional_words.extend(keywords)
        
        total_emotional_indicators = 0
        for inp in user_inputs:
            total_emotional_indicators += sum(1 for word in emotional_words if word in inp.lower())
        
        # 情感参与度 = 情感词汇密度
        total_words = sum(len(inp.split()) for inp in user_inputs)
        engagement = total_emotional_indicators / total_words if total_words > 0 else 0
        
        return min(1.0, engagement * 10)  # 放大以便观察
    
    def _generate_behavioral_insights(self,
                                    communication_patterns: Dict[str, Any],
                                    preference_indicators: Dict[str, Any],
                                    topic_interests: Dict[str, Any],
                                    engagement_metrics: Dict[str, Any]) -> List[str]:
        """生成行为洞察"""
        
        insights = []
        
        # 沟通风格洞察
        avg_length = communication_patterns["avg_input_length"]
        if avg_length > 100:
            insights.append("用户偏好详细表达，喜欢提供充分的背景信息")
        elif avg_length < 30:
            insights.append("用户沟通简洁直接，偏好快速获得答案")
        
        # 礼貌程度洞察
        politeness = communication_patterns["politeness_indicators"]
        if politeness > 0.7:
            insights.append("用户表现出高礼貌度，重视正式的交流方式")
        
        # 主题兴趣洞察
        top_interest = max(topic_interests.items(), key=lambda x: x[1]) if topic_interests else ("其他", 0)
        if top_interest[1] > 0.3:
            insights.append(f"用户对{top_interest[0]}话题表现出特别的兴趣")
        
        # 参与度洞察
        session_length = engagement_metrics["session_length"]
        if session_length > 10:
            insights.append("用户表现出高度参与，进行了深入的多轮对话")
        elif session_length < 3:
            insights.append("用户进行了简短的咨询，可能更偏好快速解答")
        
        # 紧急性洞察
        urgency = preference_indicators["urgent_queries"]
        if urgency > 0.3:
            insights.append("用户经常表现出紧迫性，需要及时的回复和指导")
        
        return insights
    
    def _analyze_conversation_flow(self, responses: List[AIResponse]) -> Dict[str, Any]:
        """分析对话流程"""
        
        flow_metrics = {
            "conversation_phases": [],
            "flow_smoothness": 0.0,
            "topic_continuity": 0.0,
            "interaction_rhythm": {}
        }
        
        # 识别对话阶段
        phases = self._identify_conversation_phases(responses)
        flow_metrics["conversation_phases"] = phases
        
        # 计算流畅度
        flow_metrics["flow_smoothness"] = self._calculate_flow_smoothness(responses)
        
        # 计算话题连续性
        flow_metrics["topic_continuity"] = self._calculate_topic_continuity_score(responses)
        
        # 分析交互节奏
        flow_metrics["interaction_rhythm"] = self._analyze_interaction_rhythm(responses)
        
        return flow_metrics
    
    def _identify_conversation_phases(self, responses: List[AIResponse]) -> List[Dict[str, Any]]:
        """识别对话阶段"""
        phases = []
        
        if not responses:
            return phases
        
        # 简化的阶段识别
        phase_keywords = {
            "开场": ["你好", "想问", "咨询", "请教"],
            "深入": ["详细", "具体", "为什么", "如何"],
            "验证": ["是否", "对吗", "准确", "确认"],
            "总结": ["谢谢", "明白", "了解", "总的来说"]
        }
        
        current_phase = "开场"
        phase_start = 0
        
        for i, response in enumerate(responses):
            user_input = response.user_input.lower()
            
            # 检测阶段转换
            for phase_name, keywords in phase_keywords.items():
                if any(keyword in user_input for keyword in keywords):
                    if phase_name != current_phase:
                        # 结束当前阶段
                        if i > phase_start:
                            phases.append({
                                "phase": current_phase,
                                "start_index": phase_start,
                                "end_index": i - 1,
                                "duration": i - phase_start
                            })
                        
                        # 开始新阶段
                        current_phase = phase_name
                        phase_start = i
                        break
        
        # 添加最后阶段
        if len(responses) > phase_start:
            phases.append({
                "phase": current_phase,
                "start_index": phase_start,
                "end_index": len(responses) - 1,
                "duration": len(responses) - phase_start
            })
        
        return phases
    
    def _calculate_flow_smoothness(self, responses: List[AIResponse]) -> float:
        """计算流程流畅度"""
        if len(responses) < 2:
            return 1.0
        
        smoothness_factors = []
        
        for i in range(1, len(responses)):
            prev_response = responses[i-1]
            curr_response = responses[i]
            
            # 响应时间一致性
            time_consistency = 1.0 - min(1.0, abs(prev_response.response_time - curr_response.response_time) / 10)
            smoothness_factors.append(time_consistency)
            
            # 回复长度一致性
            prev_length = len(prev_response.ai_response)
            curr_length = len(curr_response.ai_response)
            length_consistency = 1.0 - min(1.0, abs(prev_length - curr_length) / max(prev_length, curr_length, 1))
            smoothness_factors.append(length_consistency)
        
        return statistics.mean(smoothness_factors) if smoothness_factors else 0.0
    
    def _calculate_topic_continuity_score(self, responses: List[AIResponse]) -> float:
        """计算话题连续性分数"""
        if len(responses) < 2:
            return 1.0
        
        continuity_scores = []
        
        for i in range(1, len(responses)):
            prev_topics = self._classify_topics(responses[i-1].user_input + " " + responses[i-1].ai_response)
            curr_topics = self._classify_topics(responses[i].user_input)
            
            if prev_topics and curr_topics:
                overlap = len(set(prev_topics).intersection(set(curr_topics)))
                total = len(set(prev_topics).union(set(curr_topics)))
                continuity_score = overlap / total if total > 0 else 0
            else:
                continuity_score = 0.5  # 默认值
            
            continuity_scores.append(continuity_score)
        
        return statistics.mean(continuity_scores) if continuity_scores else 0.0
    
    def _analyze_interaction_rhythm(self, responses: List[AIResponse]) -> Dict[str, Any]:
        """分析交互节奏"""
        if len(responses) < 2:
            return {"rhythm_type": "single_interaction"}
        
        # 计算交互间隔
        timestamps = [datetime.fromisoformat(r.timestamp.replace("Z", "+00:00")) for r in responses]
        intervals = [(timestamps[i+1] - timestamps[i]).total_seconds() for i in range(len(timestamps)-1)]
        
        if not intervals:
            return {"rhythm_type": "unknown"}
        
        avg_interval = statistics.mean(intervals)
        interval_variance = statistics.variance(intervals) if len(intervals) > 1 else 0
        
        # 判断节奏类型
        if avg_interval < 30:
            rhythm_type = "rapid"
        elif avg_interval > 300:
            rhythm_type = "slow"
        else:
            rhythm_type = "moderate"
        
        # 判断节奏稳定性
        if interval_variance < (avg_interval * 0.5):
            rhythm_stability = "stable"
        else:
            rhythm_stability = "variable"
        
        return {
            "rhythm_type": rhythm_type,
            "rhythm_stability": rhythm_stability,
            "avg_interval": avg_interval,
            "interval_variance": interval_variance,
            "intervals": intervals
        }
    
    def _generate_insights(self, analysis: Dict[str, Any]) -> List[str]:
        """生成洞察和建议"""
        
        insights = []
        
        # 基于基础指标的洞察
        basic_metrics = analysis.get("basic_metrics", {})
        avg_response_time = basic_metrics.get("avg_response_time", 0)
        
        if avg_response_time > 5:
            insights.append("AI回复时间较长，建议优化响应速度以提升用户体验")
        elif avg_response_time < 1:
            insights.append("AI回复速度很快，用户体验良好")
        
        # 基于话题分析的洞察
        topic_analysis = analysis.get("topic_analysis", {})
        topic_diversity = topic_analysis.get("topic_diversity", 0)
        
        if topic_diversity > 4:
            insights.append("对话涵盖多个话题，表现出用户的广泛兴趣，建议保持话题间的平衡")
        elif topic_diversity == 1:
            insights.append("对话专注于单一话题，建议深入挖掘用户在该领域的具体需求")
        
        # 基于情感分析的洞察
        emotion_analysis = analysis.get("emotion_analysis", {})
        dominant_emotion = emotion_analysis.get("dominant_emotion", "中性")
        
        if dominant_emotion == "消极":
            insights.append("用户情感偏向消极，建议AI提供更多的安慰和积极引导")
        elif dominant_emotion == "积极":
            insights.append("用户情感积极，建议保持当前的沟通方式和内容质量")
        
        # 基于记忆使用的洞察
        memory_analysis = analysis.get("memory_usage_analysis", {})
        memory_utilization = memory_analysis.get("usage_statistics", {}).get("memory_utilization_rate", 0)
        
        if memory_utilization < 0.3:
            insights.append("记忆框架使用率较低，建议增强历史信息的整合和引用")
        elif memory_utilization > 0.8:
            insights.append("记忆框架使用充分，有效利用了用户的历史信息")
        
        # 基于用户行为的洞察
        user_behavior = analysis.get("user_behavior", {})
        if hasattr(user_behavior, 'behavioral_insights'):
            insights.extend(user_behavior.behavioral_insights)
        
        # 基于对话流程的洞察
        conversation_flow = analysis.get("conversation_flow", {})
        flow_smoothness = conversation_flow.get("flow_smoothness", 0)
        
        if flow_smoothness > 0.8:
            insights.append("对话流程流畅，用户与AI的交互自然顺畅")
        elif flow_smoothness < 0.5:
            insights.append("对话流程存在不够流畅的地方，建议改善回复的一致性")
        
        return insights[:8]  # 限制洞察数量