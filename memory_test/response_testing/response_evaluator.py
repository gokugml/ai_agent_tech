"""
回复质量评估器

评估AI回复的质量、相关性和记忆利用度
"""

import re
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import statistics

from loguru import logger

from .real_ai_tester import AIResponse


@dataclass
class ResponseQuality:
    """回复质量评估结果"""
    response_id: str
    overall_score: float  # 0-1 总体质量分数
    dimensions: Dict[str, float]  # 各维度分数
    strengths: List[str]  # 优势
    weaknesses: List[str]  # 不足
    suggestions: List[str]  # 改进建议
    evaluation_details: Dict[str, Any]  # 详细评估信息


@dataclass
class ConversationEvaluation:
    """对话评估结果"""
    session_id: str
    overall_conversation_score: float
    response_scores: List[ResponseQuality]
    conversation_flow_score: float
    memory_utilization_score: float
    consistency_score: float
    user_satisfaction_estimate: float
    evaluation_summary: Dict[str, Any]


class ResponseQualityEvaluator:
    """回复质量评估器"""
    
    def __init__(self):
        self.evaluation_criteria = {
            "relevance": {
                "weight": 0.25,
                "description": "回复与用户输入的相关性"
            },
            "coherence": {
                "weight": 0.20,
                "description": "回复的逻辑性和连贯性"
            },
            "informativeness": {
                "weight": 0.20,
                "description": "回复的信息含量和实用性"
            },
            "appropriateness": {
                "weight": 0.15,
                "description": "回复的语气和风格适宜性"
            },
            "memory_integration": {
                "weight": 0.20,
                "description": "对历史记忆的有效利用"
            }
        }
        
        # 算命咨询专业术语
        self.divination_keywords = {
            "basic_terms": ["八字", "五行", "命盘", "流年", "大运", "天干", "地支", "纳音", "神煞"],
            "prediction_terms": ["运势", "财运", "事业运", "桃花运", "健康运", "学业运"],
            "guidance_terms": ["建议", "注意", "宜", "忌", "化解", "改善", "调理"],
            "time_terms": ["今年", "明年", "下半年", "近期", "长远", "流年", "月运"]
        }
        
        # 质量指标关键词
        self.quality_indicators = {
            "positive": ["准确", "详细", "有用", "清楚", "专业", "贴心", "全面"],
            "negative": ["模糊", "空泛", "重复", "无关", "错误", "简单"]
        }
    
    def evaluate_single_response(self, 
                                response: AIResponse,
                                user_context: Optional[Dict[str, Any]] = None) -> ResponseQuality:
        """评估单个回复质量"""
        
        logger.info(f"开始评估回复: {response.response_id}")
        
        # 各维度评估
        relevance_score = self._evaluate_relevance(response)
        coherence_score = self._evaluate_coherence(response)
        informativeness_score = self._evaluate_informativeness(response)
        appropriateness_score = self._evaluate_appropriateness(response, user_context)
        memory_integration_score = self._evaluate_memory_integration(response)
        
        dimensions = {
            "relevance": relevance_score,
            "coherence": coherence_score,
            "informativeness": informativeness_score,
            "appropriateness": appropriateness_score,
            "memory_integration": memory_integration_score
        }
        
        # 计算加权总分
        overall_score = sum(
            score * self.evaluation_criteria[dim]["weight"]
            for dim, score in dimensions.items()
        )
        
        # 生成评估反馈
        strengths, weaknesses, suggestions = self._generate_feedback(
            dimensions, response, user_context
        )
        
        # 收集详细评估信息
        evaluation_details = {
            "response_length": len(response.ai_response),
            "has_memory_context": bool(response.memory_context),
            "memory_context_size": len(response.memory_context),
            "response_time": response.response_time,
            "token_usage": response.token_usage,
            "professional_terms_count": self._count_professional_terms(response.ai_response),
            "structural_analysis": self._analyze_response_structure(response.ai_response)
        }
        
        quality = ResponseQuality(
            response_id=response.response_id,
            overall_score=overall_score,
            dimensions=dimensions,
            strengths=strengths,
            weaknesses=weaknesses,
            suggestions=suggestions,
            evaluation_details=evaluation_details
        )
        
        logger.info(f"回复评估完成: {response.response_id}, 总分: {overall_score:.3f}")
        return quality
    
    def _evaluate_relevance(self, response: AIResponse) -> float:
        """评估相关性"""
        user_input = response.user_input.lower()
        ai_response = response.ai_response.lower()
        
        # 关键词匹配
        user_words = set(re.findall(r'\\b\\w+\\b', user_input))
        response_words = set(re.findall(r'\\b\\w+\\b', ai_response))
        
        if not user_words:
            return 0.5
        
        # 直接关键词匹配
        direct_match = len(user_words.intersection(response_words)) / len(user_words)
        
        # 语义相关性（简单实现）
        semantic_score = self._calculate_semantic_relevance(user_input, ai_response)
        
        # 专题匹配
        topic_score = self._calculate_topic_relevance(user_input, ai_response)
        
        # 综合计算
        relevance_score = (direct_match * 0.4 + semantic_score * 0.3 + topic_score * 0.3)
        return min(1.0, relevance_score)
    
    def _evaluate_coherence(self, response: AIResponse) -> float:
        """评估连贯性"""
        text = response.ai_response
        
        # 基本结构检查
        sentences = self._split_sentences(text)
        if len(sentences) < 1:
            return 0.0
        
        # 句子完整性
        completeness_score = self._check_sentence_completeness(sentences)
        
        # 逻辑连接词检查
        logical_connection_score = self._check_logical_connections(text)
        
        # 主题一致性
        topic_consistency_score = self._check_topic_consistency(sentences)
        
        # 重复性检查
        repetition_penalty = self._check_repetition(sentences)
        
        coherence_score = (
            completeness_score * 0.3 +
            logical_connection_score * 0.25 +
            topic_consistency_score * 0.25 +
            (1.0 - repetition_penalty) * 0.2
        )
        
        return max(0.0, min(1.0, coherence_score))
    
    def _evaluate_informativeness(self, response: AIResponse) -> float:
        """评估信息量"""
        text = response.ai_response
        
        # 专业术语密度
        professional_terms = self._count_professional_terms(text)
        term_density = min(1.0, professional_terms / max(1, len(text.split()) / 10))
        
        # 具体性评估（数字、时间、具体建议）
        specificity_score = self._evaluate_specificity(text)
        
        # 建议实用性
        practical_advice_score = self._evaluate_practical_advice(text)
        
        # 内容深度
        depth_score = self._evaluate_content_depth(text)
        
        informativeness_score = (
            term_density * 0.25 +
            specificity_score * 0.25 +
            practical_advice_score * 0.25 +
            depth_score * 0.25
        )
        
        return min(1.0, informativeness_score)
    
    def _evaluate_appropriateness(self, 
                                response: AIResponse,
                                user_context: Optional[Dict[str, Any]] = None) -> float:
        """评估适宜性"""
        text = response.ai_response
        
        # 语气评估
        tone_score = self._evaluate_tone(text)
        
        # 专业性评估
        professionalism_score = self._evaluate_professionalism(text)
        
        # 用户风格匹配
        style_match_score = 1.0  # 默认值
        if user_context:
            style_match_score = self._evaluate_style_matching(text, user_context)
        
        # 敏感内容检查
        sensitivity_score = self._check_sensitivity(text)
        
        appropriateness_score = (
            tone_score * 0.3 +
            professionalism_score * 0.3 +
            style_match_score * 0.2 +
            sensitivity_score * 0.2
        )
        
        return min(1.0, appropriateness_score)
    
    def _evaluate_memory_integration(self, response: AIResponse) -> float:
        """评估记忆整合度"""
        memory_context = response.memory_context
        ai_response = response.ai_response
        
        if not memory_context:
            return 0.0  # 没有记忆上下文
        
        # 记忆引用检查
        memory_reference_score = self._check_memory_references(ai_response, memory_context)
        
        # 连续性评估
        continuity_score = self._evaluate_continuity(ai_response, memory_context)
        
        # 记忆相关性
        memory_relevance_score = self._evaluate_memory_relevance(memory_context)
        
        integration_score = (
            memory_reference_score * 0.4 +
            continuity_score * 0.3 +
            memory_relevance_score * 0.3
        )
        
        return min(1.0, integration_score)
    
    def _generate_feedback(self,
                         dimensions: Dict[str, float],
                         response: AIResponse,
                         user_context: Optional[Dict[str, Any]]) -> Tuple[List[str], List[str], List[str]]:
        """生成评估反馈"""
        
        strengths = []
        weaknesses = []
        suggestions = []
        
        # 分析各维度表现
        for dim, score in dimensions.items():
            if score >= 0.8:
                strengths.append(f"{self.evaluation_criteria[dim]['description']}表现优秀")
            elif score < 0.5:
                weaknesses.append(f"{self.evaluation_criteria[dim]['description']}需要改进")
                suggestions.append(f"建议提升{self.evaluation_criteria[dim]['description']}")
        
        # 具体内容分析
        text = response.ai_response
        
        # 长度分析
        if len(text) < 50:
            weaknesses.append("回复过于简短")
            suggestions.append("建议提供更详细的分析和建议")
        elif len(text) > 500:
            weaknesses.append("回复可能过于冗长")
            suggestions.append("建议精简表达，突出重点")
        
        # 专业性分析
        prof_terms = self._count_professional_terms(text)
        if prof_terms > 5:
            strengths.append("专业术语使用恰当")
        elif prof_terms < 2:
            suggestions.append("建议增加专业术语的使用")
        
        # 记忆利用分析
        if response.memory_context:
            if dimensions["memory_integration"] > 0.7:
                strengths.append("有效利用了历史记忆信息")
            else:
                suggestions.append("建议更好地整合历史记忆信息")
        
        return strengths, weaknesses, suggestions
    
    def evaluate_conversation(self, responses: List[AIResponse]) -> ConversationEvaluation:
        """评估整个对话"""
        
        if not responses:
            return ConversationEvaluation(
                session_id="empty",
                overall_conversation_score=0.0,
                response_scores=[],
                conversation_flow_score=0.0,
                memory_utilization_score=0.0,
                consistency_score=0.0,
                user_satisfaction_estimate=0.0,
                evaluation_summary={}
            )
        
        session_id = responses[0].session_id
        logger.info(f"开始评估对话: {session_id}, 回复数: {len(responses)}")
        
        # 评估每个回复
        response_scores = []
        for response in responses:
            quality = self.evaluate_single_response(response)
            response_scores.append(quality)
        
        # 对话流畅度评估
        conversation_flow_score = self._evaluate_conversation_flow(responses)
        
        # 记忆利用度评估
        memory_utilization_score = self._evaluate_memory_utilization(responses)
        
        # 一致性评估
        consistency_score = self._evaluate_consistency(responses)
        
        # 用户满意度估算
        user_satisfaction_estimate = self._estimate_user_satisfaction(response_scores)
        
        # 总体对话分数
        individual_scores = [rs.overall_score for rs in response_scores]
        overall_conversation_score = (
            statistics.mean(individual_scores) * 0.5 +
            conversation_flow_score * 0.2 +
            memory_utilization_score * 0.15 +
            consistency_score * 0.15
        )
        
        # 生成评估摘要
        evaluation_summary = self._generate_conversation_summary(
            response_scores, conversation_flow_score, 
            memory_utilization_score, consistency_score
        )
        
        conversation_eval = ConversationEvaluation(
            session_id=session_id,
            overall_conversation_score=overall_conversation_score,
            response_scores=response_scores,
            conversation_flow_score=conversation_flow_score,
            memory_utilization_score=memory_utilization_score,
            consistency_score=consistency_score,
            user_satisfaction_estimate=user_satisfaction_estimate,
            evaluation_summary=evaluation_summary
        )
        
        logger.info(f"对话评估完成: {session_id}, 总分: {overall_conversation_score:.3f}")
        return conversation_eval
    
    # 辅助方法实现
    def _calculate_semantic_relevance(self, user_input: str, ai_response: str) -> float:
        """计算语义相关性（简化实现）"""
        # 检查问答匹配模式
        question_indicators = ["什么", "怎么", "如何", "为什么", "能否", "可以"]
        answer_indicators = ["是", "可以", "建议", "应该", "需要"]
        
        has_question = any(indicator in user_input for indicator in question_indicators)
        has_answer = any(indicator in ai_response for indicator in answer_indicators)
        
        if has_question and has_answer:
            return 0.8
        elif has_question and not has_answer:
            return 0.3
        else:
            return 0.6
    
    def _calculate_topic_relevance(self, user_input: str, ai_response: str) -> float:
        """计算主题相关性"""
        topics = {
            "事业": ["工作", "职业", "事业", "升职", "跳槽", "同事"],
            "感情": ["恋爱", "结婚", "分手", "感情", "爱情", "对象"],
            "财运": ["钱", "财运", "投资", "理财", "收入", "财富"],
            "健康": ["健康", "身体", "生病", "医院", "保养", "养生"]
        }
        
        input_topics = set()
        response_topics = set()
        
        for topic, keywords in topics.items():
            if any(keyword in user_input for keyword in keywords):
                input_topics.add(topic)
            if any(keyword in ai_response for keyword in keywords):
                response_topics.add(topic)
        
        if not input_topics:
            return 0.5
        
        overlap = len(input_topics.intersection(response_topics))
        return overlap / len(input_topics)
    
    def _split_sentences(self, text: str) -> List[str]:
        """分割句子"""
        sentences = re.split(r'[。！？.!?]', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _check_sentence_completeness(self, sentences: List[str]) -> float:
        """检查句子完整性"""
        complete_count = 0
        for sentence in sentences:
            if len(sentence) > 3 and not sentence.endswith(('，', ',')):
                complete_count += 1
        
        return complete_count / len(sentences) if sentences else 0.0
    
    def _check_logical_connections(self, text: str) -> float:
        """检查逻辑连接"""
        connectors = ["因为", "所以", "但是", "然而", "另外", "同时", "此外", "因此"]
        connector_count = sum(1 for conn in connectors if conn in text)
        
        # 根据文本长度调整期望的连接词数量
        expected_connectors = len(text) / 100
        score = min(1.0, connector_count / max(1, expected_connectors))
        return score
    
    def _check_topic_consistency(self, sentences: List[str]) -> float:
        """检查主题一致性（简化实现）"""
        if len(sentences) <= 1:
            return 1.0
        
        # 检查关键词在句子间的分布
        all_words = set()
        for sentence in sentences:
            words = set(re.findall(r'\\b\\w+\\b', sentence.lower()))
            all_words.update(words)
        
        if not all_words:
            return 0.5
        
        # 计算句子间的词汇重叠
        overlaps = []
        for i in range(len(sentences) - 1):
            words1 = set(re.findall(r'\\b\\w+\\b', sentences[i].lower()))
            words2 = set(re.findall(r'\\b\\w+\\b', sentences[i + 1].lower()))
            
            if words1 and words2:
                overlap = len(words1.intersection(words2)) / len(words1.union(words2))
                overlaps.append(overlap)
        
        return statistics.mean(overlaps) if overlaps else 0.5
    
    def _check_repetition(self, sentences: List[str]) -> float:
        """检查重复性"""
        if len(sentences) <= 1:
            return 0.0
        
        repetition_count = 0
        for i in range(len(sentences)):
            for j in range(i + 1, len(sentences)):
                similarity = self._calculate_sentence_similarity(sentences[i], sentences[j])
                if similarity > 0.7:
                    repetition_count += 1
        
        max_possible_repetitions = len(sentences) * (len(sentences) - 1) / 2
        return repetition_count / max_possible_repetitions if max_possible_repetitions > 0 else 0.0
    
    def _calculate_sentence_similarity(self, sent1: str, sent2: str) -> float:
        """计算句子相似度"""
        words1 = set(re.findall(r'\\b\\w+\\b', sent1.lower()))
        words2 = set(re.findall(r'\\b\\w+\\b', sent2.lower()))
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    def _count_professional_terms(self, text: str) -> int:
        """统计专业术语"""
        count = 0
        for category, terms in self.divination_keywords.items():
            for term in terms:
                count += text.count(term)
        return count
    
    def _analyze_response_structure(self, text: str) -> Dict[str, Any]:
        """分析回复结构"""
        return {
            "sentence_count": len(self._split_sentences(text)),
            "word_count": len(text.split()),
            "character_count": len(text),
            "paragraph_count": len([p for p in text.split('\\n') if p.strip()]),
            "has_greeting": any(greeting in text for greeting in ["您好", "你好", "感谢"]),
            "has_conclusion": any(conclusion in text for conclusion in ["总之", "最后", "建议", "祝愿"])
        }
    
    def _evaluate_specificity(self, text: str) -> float:
        """评估具体性"""
        # 检查数字、时间、具体描述
        numbers = len(re.findall(r'\\d+', text))
        time_expressions = len(re.findall(r'(今年|明年|下半年|\\d+月|\\d+日)', text))
        specific_terms = len(re.findall(r'(具体|详细|准确|明确)', text))
        
        specificity_score = min(1.0, (numbers + time_expressions + specific_terms) / 10)
        return specificity_score
    
    def _evaluate_practical_advice(self, text: str) -> float:
        """评估实用建议"""
        advice_indicators = ["建议", "应该", "可以", "需要", "注意", "避免", "建议您"]
        advice_count = sum(1 for indicator in advice_indicators if indicator in text)
        
        return min(1.0, advice_count / 3)
    
    def _evaluate_content_depth(self, text: str) -> float:
        """评估内容深度"""
        depth_indicators = ["原因", "影响", "关系", "分析", "解释", "机制"]
        depth_count = sum(1 for indicator in depth_indicators if indicator in text)
        
        return min(1.0, depth_count / 5)
    
    def _evaluate_tone(self, text: str) -> float:
        """评估语气"""
        # 检查礼貌用语
        polite_terms = ["您", "请", "谢谢", "不好意思", "抱歉"]
        polite_count = sum(1 for term in polite_terms if term in text)
        
        # 检查负面语气
        negative_terms = ["不行", "不可能", "绝对不", "肯定不"]
        negative_count = sum(1 for term in negative_terms if term in text)
        
        tone_score = min(1.0, polite_count / 3) - min(0.5, negative_count / 2)
        return max(0.0, tone_score)
    
    def _evaluate_professionalism(self, text: str) -> float:
        """评估专业性"""
        professional_score = self._count_professional_terms(text) / max(1, len(text.split()) / 5)
        return min(1.0, professional_score)
    
    def _evaluate_style_matching(self, text: str, user_context: Dict[str, Any]) -> float:
        """评估风格匹配"""
        # 简化实现，根据用户偏好调整
        user_style = user_context.get("communication_style", "normal")
        
        if user_style == "简洁":
            return 1.0 if len(text) < 200 else 0.5
        elif user_style == "详细":
            return 1.0 if len(text) > 100 else 0.5
        else:
            return 0.8  # 默认匹配度
    
    def _check_sensitivity(self, text: str) -> float:
        """检查敏感内容"""
        sensitive_terms = ["死", "灾祸", "破财", "血光", "凶险"]
        sensitive_count = sum(1 for term in sensitive_terms if term in text)
        
        return max(0.0, 1.0 - sensitive_count / 5)
    
    def _check_memory_references(self, ai_response: str, memory_context: Dict[str, Any]) -> float:
        """检查记忆引用"""
        if not memory_context:
            return 0.0
        
        reference_indicators = ["之前", "上次", "根据您的", "如您所说", "您提到的"]
        reference_count = sum(1 for indicator in reference_indicators if indicator in ai_response)
        
        return min(1.0, reference_count / 2)
    
    def _evaluate_continuity(self, ai_response: str, memory_context: Dict[str, Any]) -> float:
        """评估连续性"""
        # 检查是否延续之前的话题
        context_summary = memory_context.get("context_summary", "")
        if not context_summary:
            return 0.0
        
        # 简单的关键词匹配
        context_words = set(context_summary.split())
        response_words = set(ai_response.split())
        
        overlap = len(context_words.intersection(response_words))
        return min(1.0, overlap / max(1, len(context_words)))
    
    def _evaluate_memory_relevance(self, memory_context: Dict[str, Any]) -> float:
        """评估记忆相关性"""
        relevance_scores = memory_context.get("relevance_scores", {})
        if not relevance_scores:
            return 0.0
        
        avg_relevance = statistics.mean(relevance_scores.values())
        return avg_relevance
    
    def _evaluate_conversation_flow(self, responses: List[AIResponse]) -> float:
        """评估对话流畅度"""
        if len(responses) < 2:
            return 1.0
        
        flow_scores = []
        for i in range(1, len(responses)):
            prev_response = responses[i - 1].ai_response
            curr_input = responses[i].user_input
            curr_response = responses[i].ai_response
            
            # 检查话题连续性
            topic_continuity = self._check_topic_continuity(prev_response, curr_input, curr_response)
            flow_scores.append(topic_continuity)
        
        return statistics.mean(flow_scores) if flow_scores else 0.5
    
    def _evaluate_memory_utilization(self, responses: List[AIResponse]) -> float:
        """评估记忆利用度"""
        memory_responses = [r for r in responses if r.memory_context]
        if not responses:
            return 0.0
        
        utilization_rate = len(memory_responses) / len(responses)
        
        # 评估记忆使用质量
        if memory_responses:
            quality_scores = [
                self._evaluate_memory_integration(r) for r in memory_responses
            ]
            avg_quality = statistics.mean(quality_scores)
        else:
            avg_quality = 0.0
        
        return (utilization_rate * 0.5 + avg_quality * 0.5)
    
    def _evaluate_consistency(self, responses: List[AIResponse]) -> float:
        """评估一致性"""
        if len(responses) < 2:
            return 1.0
        
        # 检查语气一致性
        tone_consistency = self._check_tone_consistency(responses)
        
        # 检查观点一致性
        viewpoint_consistency = self._check_viewpoint_consistency(responses)
        
        return (tone_consistency * 0.5 + viewpoint_consistency * 0.5)
    
    def _estimate_user_satisfaction(self, response_scores: List[ResponseQuality]) -> float:
        """估算用户满意度"""
        if not response_scores:
            return 0.0
        
        overall_scores = [rs.overall_score for rs in response_scores]
        avg_score = statistics.mean(overall_scores)
        
        # 考虑分数分布
        score_variance = statistics.variance(overall_scores) if len(overall_scores) > 1 else 0
        consistency_bonus = max(0, 0.1 - score_variance)
        
        satisfaction = avg_score + consistency_bonus
        return min(1.0, satisfaction)
    
    def _generate_conversation_summary(self,
                                     response_scores: List[ResponseQuality],
                                     flow_score: float,
                                     memory_score: float,
                                     consistency_score: float) -> Dict[str, Any]:
        """生成对话评估摘要"""
        
        if not response_scores:
            return {"message": "无有效回复数据"}
        
        overall_scores = [rs.overall_score for rs in response_scores]
        
        summary = {
            "response_count": len(response_scores),
            "average_response_score": statistics.mean(overall_scores),
            "best_response_score": max(overall_scores),
            "worst_response_score": min(overall_scores),
            "score_variance": statistics.variance(overall_scores) if len(overall_scores) > 1 else 0,
            "conversation_flow_score": flow_score,
            "memory_utilization_score": memory_score,
            "consistency_score": consistency_score,
            
            # 维度统计
            "dimension_averages": self._calculate_dimension_averages(response_scores),
            
            # 改进建议
            "improvement_suggestions": self._generate_improvement_suggestions(response_scores),
            
            # 评估时间
            "evaluation_timestamp": datetime.now().isoformat()
        }
        
        return summary
    
    def _check_topic_continuity(self, prev_response: str, curr_input: str, curr_response: str) -> float:
        """检查话题连续性"""
        # 提取关键词
        prev_words = set(re.findall(r'\\b\\w+\\b', prev_response.lower()))
        input_words = set(re.findall(r'\\b\\w+\\b', curr_input.lower()))
        curr_words = set(re.findall(r'\\b\\w+\\b', curr_response.lower()))
        
        # 计算连续性
        prev_curr_overlap = len(prev_words.intersection(curr_words))
        input_curr_overlap = len(input_words.intersection(curr_words))
        
        continuity_score = (prev_curr_overlap + input_curr_overlap) / max(1, len(curr_words))
        return min(1.0, continuity_score)
    
    def _check_tone_consistency(self, responses: List[AIResponse]) -> float:
        """检查语气一致性"""
        tone_scores = []
        for response in responses:
            tone_score = self._evaluate_tone(response.ai_response)
            tone_scores.append(tone_score)
        
        if len(tone_scores) < 2:
            return 1.0
        
        variance = statistics.variance(tone_scores)
        consistency = max(0.0, 1.0 - variance)
        return consistency
    
    def _check_viewpoint_consistency(self, responses: List[AIResponse]) -> float:
        """检查观点一致性（简化实现）"""
        # 检查是否有矛盾的建议
        all_text = " ".join([r.ai_response for r in responses])
        
        contradictory_pairs = [
            (["宜", "应该"], ["忌", "不应该"]),
            (["有利", "良好"], ["不利", "不好"]),
            (["积极", "正面"], ["消极", "负面"])
        ]
        
        contradiction_count = 0
        for positive_terms, negative_terms in contradictory_pairs:
            has_positive = any(term in all_text for term in positive_terms)
            has_negative = any(term in all_text for term in negative_terms)
            
            if has_positive and has_negative:
                contradiction_count += 1
        
        consistency = max(0.0, 1.0 - contradiction_count / len(contradictory_pairs))
        return consistency
    
    def _calculate_dimension_averages(self, response_scores: List[ResponseQuality]) -> Dict[str, float]:
        """计算各维度平均分"""
        if not response_scores:
            return {}
        
        dimensions = response_scores[0].dimensions.keys()
        averages = {}
        
        for dim in dimensions:
            scores = [rs.dimensions[dim] for rs in response_scores]
            averages[dim] = statistics.mean(scores)
        
        return averages
    
    def _generate_improvement_suggestions(self, response_scores: List[ResponseQuality]) -> List[str]:
        """生成改进建议"""
        suggestions = []
        
        if not response_scores:
            return ["需要提供有效的回复数据进行评估"]
        
        # 分析薄弱环节
        dimension_averages = self._calculate_dimension_averages(response_scores)
        
        for dim, avg_score in dimension_averages.items():
            if avg_score < 0.6:
                description = self.evaluation_criteria[dim]["description"]
                suggestions.append(f"需要重点改进：{description}")
        
        # 检查一致性问题
        overall_scores = [rs.overall_score for rs in response_scores]
        if len(overall_scores) > 1:
            variance = statistics.variance(overall_scores)
            if variance > 0.1:
                suggestions.append("需要提高回复质量的一致性")
        
        # 检查记忆利用
        memory_usage = sum(1 for rs in response_scores if rs.evaluation_details.get("has_memory_context", False))
        memory_rate = memory_usage / len(response_scores)
        if memory_rate < 0.5:
            suggestions.append("建议更频繁地利用历史记忆信息")
        
        return suggestions if suggestions else ["整体表现良好，继续保持当前水准"]