"""
记忆影响评估器

评估记忆框架对AI回复质量的具体影响
"""

import statistics
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import json

from loguru import logger

from ..response_testing.real_ai_tester import AIResponse
from ..response_testing.response_evaluator import ResponseQuality


@dataclass
class MemoryImpactMetrics:
    """记忆影响指标"""
    framework_type: str
    total_responses: int
    responses_with_memory: int
    responses_without_memory: int
    
    # 质量对比
    avg_quality_with_memory: float
    avg_quality_without_memory: float
    quality_improvement: float
    
    # 响应时间对比
    avg_time_with_memory: float
    avg_time_without_memory: float
    time_overhead: float
    
    # 内容对比
    avg_length_with_memory: int
    avg_length_without_memory: int
    length_difference: int
    
    # 记忆有效性
    memory_relevance_score: float
    memory_utilization_rate: float
    memory_consistency_score: float


@dataclass
class FrameworkComparison:
    """框架对比结果"""
    framework_a: str
    framework_b: str
    
    # 整体表现对比
    overall_winner: str
    confidence_level: float
    
    # 各维度对比
    quality_comparison: Dict[str, Any]
    performance_comparison: Dict[str, Any]
    memory_effectiveness_comparison: Dict[str, Any]
    user_satisfaction_comparison: Dict[str, Any]
    
    # 优势分析
    framework_a_strengths: List[str]
    framework_b_strengths: List[str]
    
    # 建议
    recommendations: List[str]


class MemoryImpactAssessor:
    """记忆影响评估器"""
    
    def __init__(self):
        # 评估维度权重
        self.evaluation_weights = {
            "quality_improvement": 0.35,
            "response_relevance": 0.25, 
            "memory_efficiency": 0.20,
            "user_experience": 0.20
        }
        
        # 质量阈值
        self.quality_thresholds = {
            "excellent": 0.85,
            "good": 0.70,
            "acceptable": 0.55,
            "poor": 0.40
        }
        
    def assess_memory_impact(self, 
                           responses: List[AIResponse],
                           response_qualities: Optional[List[ResponseQuality]] = None) -> MemoryImpactMetrics:
        """评估记忆对回复的影响"""
        
        if not responses:
            raise ValueError("需要提供回复数据")
        
        logger.info(f"开始评估记忆影响: {len(responses)} 个回复")
        
        # 分组：有记忆 vs 无记忆
        with_memory = [r for r in responses if r.memory_context]
        without_memory = [r for r in responses if not r.memory_context]
        
        # 获取框架类型
        framework_type = responses[0].metadata.get("framework_type", "unknown")
        
        # 计算质量对比
        quality_with_memory, quality_without_memory = self._calculate_quality_comparison(
            with_memory, without_memory, response_qualities
        )
        
        # 计算响应时间对比
        time_with_memory = statistics.mean([r.response_time for r in with_memory]) if with_memory else 0
        time_without_memory = statistics.mean([r.response_time for r in without_memory]) if without_memory else 0
        
        # 计算内容长度对比
        length_with_memory = statistics.mean([len(r.ai_response) for r in with_memory]) if with_memory else 0
        length_without_memory = statistics.mean([len(r.ai_response) for r in without_memory]) if without_memory else 0
        
        # 计算记忆有效性指标
        memory_relevance = self._calculate_memory_relevance(with_memory)
        memory_utilization = len(with_memory) / len(responses) if responses else 0
        memory_consistency = self._calculate_memory_consistency(with_memory)
        
        metrics = MemoryImpactMetrics(
            framework_type=framework_type,
            total_responses=len(responses),
            responses_with_memory=len(with_memory),
            responses_without_memory=len(without_memory),
            
            avg_quality_with_memory=quality_with_memory,
            avg_quality_without_memory=quality_without_memory,
            quality_improvement=quality_with_memory - quality_without_memory,
            
            avg_time_with_memory=time_with_memory,
            avg_time_without_memory=time_without_memory,
            time_overhead=time_with_memory - time_without_memory,
            
            avg_length_with_memory=int(length_with_memory),
            avg_length_without_memory=int(length_without_memory),
            length_difference=int(length_with_memory - length_without_memory),
            
            memory_relevance_score=memory_relevance,
            memory_utilization_rate=memory_utilization,
            memory_consistency_score=memory_consistency
        )
        
        logger.info(f"记忆影响评估完成: 质量提升 {metrics.quality_improvement:.3f}")
        return metrics
    
    def _calculate_quality_comparison(self,
                                    with_memory: List[AIResponse],
                                    without_memory: List[AIResponse],
                                    response_qualities: Optional[List[ResponseQuality]] = None) -> Tuple[float, float]:
        """计算质量对比"""
        
        if response_qualities:
            # 使用已有的质量评估结果
            quality_map = {rq.response_id: rq.overall_score for rq in response_qualities}
            
            with_memory_scores = [
                quality_map.get(r.response_id, 0.5) for r in with_memory
                if r.response_id in quality_map
            ]
            without_memory_scores = [
                quality_map.get(r.response_id, 0.5) for r in without_memory
                if r.response_id in quality_map
            ]
        else:
            # 使用简化质量评估
            with_memory_scores = [self._simple_quality_score(r) for r in with_memory]
            without_memory_scores = [self._simple_quality_score(r) for r in without_memory]
        
        avg_with_memory = statistics.mean(with_memory_scores) if with_memory_scores else 0.0
        avg_without_memory = statistics.mean(without_memory_scores) if without_memory_scores else 0.0
        
        return avg_with_memory, avg_without_memory
    
    def _simple_quality_score(self, response: AIResponse) -> float:
        """简化质量评估"""
        score = 0.5  # 基础分
        
        ai_response = response.ai_response
        user_input = response.user_input
        
        # 长度适中性
        if 50 <= len(ai_response) <= 300:
            score += 0.1
        
        # 相关性（关键词匹配）
        user_words = set(user_input.lower().split())
        ai_words = set(ai_response.lower().split())
        
        if user_words.intersection(ai_words):
            score += 0.2
        
        # 专业性
        professional_terms = ["八字", "运势", "建议", "分析", "预测", "命理"]
        term_count = sum(1 for term in professional_terms if term in ai_response)
        score += min(0.2, term_count * 0.05)
        
        return min(1.0, score)
    
    def _calculate_memory_relevance(self, responses_with_memory: List[AIResponse]) -> float:
        """计算记忆相关性"""
        if not responses_with_memory:
            return 0.0
        
        relevance_scores = []
        
        for response in responses_with_memory:
            memory_context = response.memory_context
            relevance_score = 0.0
            
            # 检查记忆上下文质量
            if "context_summary" in memory_context:
                summary = memory_context["context_summary"]
                if summary and len(summary) > 10:
                    relevance_score += 0.3
            
            # 检查相关性分数
            if "relevance_scores" in memory_context:
                scores = memory_context["relevance_scores"]
                if scores:
                    avg_relevance = statistics.mean(scores.values())
                    relevance_score += avg_relevance * 0.4
            
            # 检查记忆类型多样性
            if "memory_types" in memory_context:
                types = memory_context["memory_types"]
                if len(types) > 1:
                    relevance_score += 0.2
            
            # 检查回复中的记忆引用
            memory_indicators = ["之前", "上次", "根据您", "如您所说"]
            if any(indicator in response.ai_response for indicator in memory_indicators):
                relevance_score += 0.1
            
            relevance_scores.append(min(1.0, relevance_score))
        
        return statistics.mean(relevance_scores)
    
    def _calculate_memory_consistency(self, responses_with_memory: List[AIResponse]) -> float:
        """计算记忆一致性"""
        if len(responses_with_memory) < 2:
            return 1.0
        
        consistency_scores = []
        
        # 检查相邻回复间的记忆一致性
        for i in range(1, len(responses_with_memory)):
            prev_memory = responses_with_memory[i-1].memory_context
            curr_memory = responses_with_memory[i].memory_context
            
            consistency = self._compare_memory_contexts(prev_memory, curr_memory)
            consistency_scores.append(consistency)
        
        return statistics.mean(consistency_scores) if consistency_scores else 1.0
    
    def _compare_memory_contexts(self, 
                               memory1: Dict[str, Any], 
                               memory2: Dict[str, Any]) -> float:
        """比较记忆上下文一致性"""
        consistency_score = 0.0
        
        # 检查用户画像一致性
        if "user_profile" in memory1 and "user_profile" in memory2:
            profile1 = memory1["user_profile"]
            profile2 = memory2["user_profile"]
            
            # 简单检查关键字段
            key_fields = ["personality_traits", "communication_style", "concerns"]
            matches = 0
            for field in key_fields:
                if field in profile1 and field in profile2:
                    if profile1[field] == profile2[field]:
                        matches += 1
            
            consistency_score += (matches / len(key_fields)) * 0.5
        
        # 检查记忆类型一致性
        if "memory_types" in memory1 and "memory_types" in memory2:
            types1 = set(memory1["memory_types"])
            types2 = set(memory2["memory_types"])
            
            if types1 and types2:
                overlap = len(types1.intersection(types2))
                union = len(types1.union(types2))
                type_consistency = overlap / union if union > 0 else 0
                consistency_score += type_consistency * 0.3
        
        # 检查记忆数量稳定性
        count1 = memory1.get("total_memories", 0)
        count2 = memory2.get("total_memories", 0)
        
        if count1 > 0 or count2 > 0:
            max_count = max(count1, count2)
            min_count = min(count1, count2)
            count_stability = min_count / max_count if max_count > 0 else 1.0
            consistency_score += count_stability * 0.2
        
        return min(1.0, consistency_score)
    
    def compare_frameworks(self,
                         framework_a_responses: List[AIResponse],
                         framework_b_responses: List[AIResponse],
                         framework_a_name: str = "Framework A",
                         framework_b_name: str = "Framework B",
                         response_qualities_a: Optional[List[ResponseQuality]] = None,
                         response_qualities_b: Optional[List[ResponseQuality]] = None) -> FrameworkComparison:
        """比较两个记忆框架"""
        
        logger.info(f"开始比较框架: {framework_a_name} vs {framework_b_name}")
        
        # 评估各框架的记忆影响
        metrics_a = self.assess_memory_impact(framework_a_responses, response_qualities_a)
        metrics_b = self.assess_memory_impact(framework_b_responses, response_qualities_b)
        
        # 质量对比
        quality_comparison = self._compare_quality_metrics(metrics_a, metrics_b)
        
        # 性能对比
        performance_comparison = self._compare_performance_metrics(metrics_a, metrics_b)
        
        # 记忆有效性对比
        memory_effectiveness_comparison = self._compare_memory_effectiveness(metrics_a, metrics_b)
        
        # 用户体验对比
        user_satisfaction_comparison = self._compare_user_satisfaction(
            framework_a_responses, framework_b_responses
        )
        
        # 确定整体获胜者
        overall_winner, confidence = self._determine_overall_winner(
            quality_comparison, performance_comparison, 
            memory_effectiveness_comparison, user_satisfaction_comparison
        )
        
        # 分析各框架优势
        strengths_a = self._identify_framework_strengths(metrics_a, "A")
        strengths_b = self._identify_framework_strengths(metrics_b, "B")
        
        # 生成建议
        recommendations = self._generate_framework_recommendations(
            metrics_a, metrics_b, quality_comparison, performance_comparison
        )
        
        comparison = FrameworkComparison(
            framework_a=framework_a_name,
            framework_b=framework_b_name,
            overall_winner=f"{framework_a_name if overall_winner == 'A' else framework_b_name}",
            confidence_level=confidence,
            quality_comparison=quality_comparison,
            performance_comparison=performance_comparison,
            memory_effectiveness_comparison=memory_effectiveness_comparison,
            user_satisfaction_comparison=user_satisfaction_comparison,
            framework_a_strengths=strengths_a,
            framework_b_strengths=strengths_b,
            recommendations=recommendations
        )
        
        logger.info(f"框架比较完成: 获胜者 {comparison.overall_winner}")
        return comparison
    
    def _compare_quality_metrics(self,
                               metrics_a: MemoryImpactMetrics,
                               metrics_b: MemoryImpactMetrics) -> Dict[str, Any]:
        """比较质量指标"""
        
        return {
            "quality_improvement": {
                "framework_a": metrics_a.quality_improvement,
                "framework_b": metrics_b.quality_improvement,
                "winner": "A" if metrics_a.quality_improvement > metrics_b.quality_improvement else "B",
                "difference": abs(metrics_a.quality_improvement - metrics_b.quality_improvement)
            },
            "avg_quality_with_memory": {
                "framework_a": metrics_a.avg_quality_with_memory,
                "framework_b": metrics_b.avg_quality_with_memory,
                "winner": "A" if metrics_a.avg_quality_with_memory > metrics_b.avg_quality_with_memory else "B",
                "difference": abs(metrics_a.avg_quality_with_memory - metrics_b.avg_quality_with_memory)
            },
            "response_consistency": {
                "framework_a": metrics_a.memory_consistency_score,
                "framework_b": metrics_b.memory_consistency_score,
                "winner": "A" if metrics_a.memory_consistency_score > metrics_b.memory_consistency_score else "B",
                "difference": abs(metrics_a.memory_consistency_score - metrics_b.memory_consistency_score)
            }
        }
    
    def _compare_performance_metrics(self,
                                   metrics_a: MemoryImpactMetrics,
                                   metrics_b: MemoryImpactMetrics) -> Dict[str, Any]:
        """比较性能指标"""
        
        return {
            "response_time_overhead": {
                "framework_a": metrics_a.time_overhead,
                "framework_b": metrics_b.time_overhead,
                "winner": "A" if metrics_a.time_overhead < metrics_b.time_overhead else "B",  # 开销越小越好
                "difference": abs(metrics_a.time_overhead - metrics_b.time_overhead)
            },
            "memory_utilization": {
                "framework_a": metrics_a.memory_utilization_rate,
                "framework_b": metrics_b.memory_utilization_rate,
                "winner": "A" if metrics_a.memory_utilization_rate > metrics_b.memory_utilization_rate else "B",
                "difference": abs(metrics_a.memory_utilization_rate - metrics_b.memory_utilization_rate)
            },
            "content_enrichment": {
                "framework_a": metrics_a.length_difference,
                "framework_b": metrics_b.length_difference,
                "winner": "A" if metrics_a.length_difference > metrics_b.length_difference else "B",
                "difference": abs(metrics_a.length_difference - metrics_b.length_difference)
            }
        }
    
    def _compare_memory_effectiveness(self,
                                    metrics_a: MemoryImpactMetrics,
                                    metrics_b: MemoryImpactMetrics) -> Dict[str, Any]:
        """比较记忆有效性"""
        
        return {
            "memory_relevance": {
                "framework_a": metrics_a.memory_relevance_score,
                "framework_b": metrics_b.memory_relevance_score,
                "winner": "A" if metrics_a.memory_relevance_score > metrics_b.memory_relevance_score else "B",
                "difference": abs(metrics_a.memory_relevance_score - metrics_b.memory_relevance_score)
            },
            "memory_consistency": {
                "framework_a": metrics_a.memory_consistency_score,
                "framework_b": metrics_b.memory_consistency_score,
                "winner": "A" if metrics_a.memory_consistency_score > metrics_b.memory_consistency_score else "B",
                "difference": abs(metrics_a.memory_consistency_score - metrics_b.memory_consistency_score)
            },
            "utilization_efficiency": {
                "framework_a": metrics_a.memory_utilization_rate * metrics_a.memory_relevance_score,
                "framework_b": metrics_b.memory_utilization_rate * metrics_b.memory_relevance_score,
                "winner": "A" if (metrics_a.memory_utilization_rate * metrics_a.memory_relevance_score) > 
                                (metrics_b.memory_utilization_rate * metrics_b.memory_relevance_score) else "B",
                "difference": abs((metrics_a.memory_utilization_rate * metrics_a.memory_relevance_score) - 
                                (metrics_b.memory_utilization_rate * metrics_b.memory_relevance_score))
            }
        }
    
    def _compare_user_satisfaction(self,
                                 responses_a: List[AIResponse],
                                 responses_b: List[AIResponse]) -> Dict[str, Any]:
        """比较用户满意度（基于对话特征推测）"""
        
        # 计算对话持续度（更长的对话可能表示更高的参与度）
        engagement_a = len(responses_a) / max(1, len(set(r.session_id for r in responses_a)))
        engagement_b = len(responses_b) / max(1, len(set(r.session_id for r in responses_b)))
        
        # 计算平均回复长度（更详细的回复可能表示更高的满意度）
        avg_length_a = statistics.mean([len(r.ai_response) for r in responses_a]) if responses_a else 0
        avg_length_b = statistics.mean([len(r.ai_response) for r in responses_b]) if responses_b else 0
        
        # 计算响应时间满意度（适中的响应时间最好）
        avg_time_a = statistics.mean([r.response_time for r in responses_a]) if responses_a else 0
        avg_time_b = statistics.mean([r.response_time for r in responses_b]) if responses_b else 0
        
        # 理想响应时间为2-5秒
        time_satisfaction_a = 1.0 - min(1.0, abs(avg_time_a - 3.5) / 10)
        time_satisfaction_b = 1.0 - min(1.0, abs(avg_time_b - 3.5) / 10)
        
        return {
            "engagement_level": {
                "framework_a": engagement_a,
                "framework_b": engagement_b,
                "winner": "A" if engagement_a > engagement_b else "B",
                "difference": abs(engagement_a - engagement_b)
            },
            "response_completeness": {
                "framework_a": avg_length_a,
                "framework_b": avg_length_b,
                "winner": "A" if avg_length_a > avg_length_b else "B",
                "difference": abs(avg_length_a - avg_length_b)
            },
            "response_time_satisfaction": {
                "framework_a": time_satisfaction_a,
                "framework_b": time_satisfaction_b,
                "winner": "A" if time_satisfaction_a > time_satisfaction_b else "B",
                "difference": abs(time_satisfaction_a - time_satisfaction_b)
            }
        }
    
    def _determine_overall_winner(self,
                                quality_comparison: Dict[str, Any],
                                performance_comparison: Dict[str, Any],
                                memory_effectiveness_comparison: Dict[str, Any],
                                user_satisfaction_comparison: Dict[str, Any]) -> Tuple[str, float]:
        """确定整体获胜者"""
        
        # 统计各维度的获胜次数
        scores = {"A": 0, "B": 0}
        total_comparisons = 0
        
        # 质量维度（权重最高）
        for metric in quality_comparison.values():
            if isinstance(metric, dict) and "winner" in metric:
                scores[metric["winner"]] += self.evaluation_weights["quality_improvement"]
                total_comparisons += self.evaluation_weights["quality_improvement"]
        
        # 性能维度
        for metric in performance_comparison.values():
            if isinstance(metric, dict) and "winner" in metric:
                scores[metric["winner"]] += self.evaluation_weights["memory_efficiency"]
                total_comparisons += self.evaluation_weights["memory_efficiency"]
        
        # 记忆有效性维度
        for metric in memory_effectiveness_comparison.values():
            if isinstance(metric, dict) and "winner" in metric:
                scores[metric["winner"]] += self.evaluation_weights["response_relevance"]
                total_comparisons += self.evaluation_weights["response_relevance"]
        
        # 用户体验维度
        for metric in user_satisfaction_comparison.values():
            if isinstance(metric, dict) and "winner" in metric:
                scores[metric["winner"]] += self.evaluation_weights["user_experience"]
                total_comparisons += self.evaluation_weights["user_experience"]
        
        # 确定获胜者和置信度
        if total_comparisons == 0:
            return "tie", 0.0
        
        score_a = scores["A"] / total_comparisons
        score_b = scores["B"] / total_comparisons
        
        if score_a > score_b:
            winner = "A"
            confidence = (score_a - score_b) * 2  # 放大差异
        elif score_b > score_a:
            winner = "B" 
            confidence = (score_b - score_a) * 2
        else:
            winner = "tie"
            confidence = 0.0
        
        confidence = min(1.0, confidence)
        
        return winner, confidence
    
    def _identify_framework_strengths(self, 
                                    metrics: MemoryImpactMetrics, 
                                    framework_label: str) -> List[str]:
        """识别框架优势"""
        
        strengths = []
        
        # 质量提升优势
        if metrics.quality_improvement > 0.1:
            strengths.append("显著提升回复质量")
        
        # 记忆利用优势
        if metrics.memory_utilization_rate > 0.7:
            strengths.append("高效利用历史记忆")
        
        # 记忆相关性优势
        if metrics.memory_relevance_score > 0.7:
            strengths.append("记忆内容高度相关")
        
        # 一致性优势
        if metrics.memory_consistency_score > 0.8:
            strengths.append("记忆使用一致稳定")
        
        # 性能优势
        if metrics.time_overhead < 1.0:
            strengths.append("记忆检索性能良好")
        
        # 内容丰富度优势
        if metrics.length_difference > 50:
            strengths.append("记忆增强内容丰富度")
        
        return strengths
    
    def _generate_framework_recommendations(self,
                                          metrics_a: MemoryImpactMetrics,
                                          metrics_b: MemoryImpactMetrics,
                                          quality_comparison: Dict[str, Any],
                                          performance_comparison: Dict[str, Any]) -> List[str]:
        """生成框架使用建议"""
        
        recommendations = []
        
        # 基于质量差异的建议
        quality_diff = abs(metrics_a.avg_quality_with_memory - metrics_b.avg_quality_with_memory)
        if quality_diff > 0.1:
            better_framework = "A" if metrics_a.avg_quality_with_memory > metrics_b.avg_quality_with_memory else "B"
            recommendations.append(f"在追求回复质量的场景下，推荐使用框架{better_framework}")
        
        # 基于性能差异的建议
        time_diff = abs(metrics_a.time_overhead - metrics_b.time_overhead)
        if time_diff > 0.5:
            faster_framework = "A" if metrics_a.time_overhead < metrics_b.time_overhead else "B"
            recommendations.append(f"在对响应速度要求较高的场景下，推荐使用框架{faster_framework}")
        
        # 基于记忆利用率的建议
        utilization_diff = abs(metrics_a.memory_utilization_rate - metrics_b.memory_utilization_rate)
        if utilization_diff > 0.2:
            better_utilization = "A" if metrics_a.memory_utilization_rate > metrics_b.memory_utilization_rate else "B"
            recommendations.append(f"需要充分利用历史信息的场景下，推荐使用框架{better_utilization}")
        
        # 基于记忆相关性的建议
        relevance_diff = abs(metrics_a.memory_relevance_score - metrics_b.memory_relevance_score)
        if relevance_diff > 0.15:
            better_relevance = "A" if metrics_a.memory_relevance_score > metrics_b.memory_relevance_score else "B"
            recommendations.append(f"需要高度相关记忆检索的场景下，推荐使用框架{better_relevance}")
        
        # 通用建议
        if not recommendations:
            recommendations.append("两个框架表现相近，可根据具体技术栈和部署需求选择")
        
        # 混合使用建议
        if len(recommendations) > 2:
            recommendations.append("考虑在不同场景下混合使用两个框架，发挥各自优势")
        
        return recommendations[:5]  # 限制建议数量
    
    def generate_impact_report(self, 
                             metrics: MemoryImpactMetrics,
                             comparison: Optional[FrameworkComparison] = None) -> Dict[str, Any]:
        """生成记忆影响报告"""
        
        report = {
            "executive_summary": self._generate_executive_summary(metrics),
            "detailed_metrics": {
                "framework_type": metrics.framework_type,
                "response_statistics": {
                    "total_responses": metrics.total_responses,
                    "with_memory": metrics.responses_with_memory,
                    "without_memory": metrics.responses_without_memory,
                    "memory_utilization_rate": f"{metrics.memory_utilization_rate:.1%}"
                },
                "quality_impact": {
                    "quality_improvement": f"{metrics.quality_improvement:+.3f}",
                    "avg_quality_with_memory": f"{metrics.avg_quality_with_memory:.3f}",
                    "avg_quality_without_memory": f"{metrics.avg_quality_without_memory:.3f}",
                    "improvement_percentage": f"{(metrics.quality_improvement / max(0.001, metrics.avg_quality_without_memory)) * 100:+.1f}%"
                },
                "performance_impact": {
                    "time_overhead": f"{metrics.time_overhead:+.2f}s",
                    "avg_time_with_memory": f"{metrics.avg_time_with_memory:.2f}s",
                    "avg_time_without_memory": f"{metrics.avg_time_without_memory:.2f}s",
                    "overhead_percentage": f"{(metrics.time_overhead / max(0.001, metrics.avg_time_without_memory)) * 100:+.1f}%"
                },
                "content_impact": {
                    "length_difference": f"{metrics.length_difference:+d} chars",
                    "avg_length_with_memory": f"{metrics.avg_length_with_memory} chars",
                    "avg_length_without_memory": f"{metrics.avg_length_without_memory} chars"
                },
                "memory_effectiveness": {
                    "relevance_score": f"{metrics.memory_relevance_score:.3f}",
                    "consistency_score": f"{metrics.memory_consistency_score:.3f}",
                    "overall_effectiveness": f"{(metrics.memory_relevance_score + metrics.memory_consistency_score) / 2:.3f}"
                }
            },
            "insights_and_recommendations": self._generate_impact_insights(metrics),
            "report_metadata": {
                "generated_at": datetime.now().isoformat(),
                "framework_type": metrics.framework_type,
                "evaluation_version": "1.0"
            }
        }
        
        if comparison:
            report["framework_comparison"] = {
                "comparison_summary": f"{comparison.overall_winner} 获胜 (置信度: {comparison.confidence_level:.1%})",
                "key_differentiators": comparison.recommendations[:3],
                "detailed_comparison": {
                    "quality": comparison.quality_comparison,
                    "performance": comparison.performance_comparison,
                    "memory_effectiveness": comparison.memory_effectiveness_comparison
                }
            }
        
        return report
    
    def _generate_executive_summary(self, metrics: MemoryImpactMetrics) -> str:
        """生成执行摘要"""
        
        quality_impact = "正面" if metrics.quality_improvement > 0 else "负面" if metrics.quality_improvement < -0.05 else "中性"
        performance_impact = "较小" if metrics.time_overhead < 1.0 else "显著"
        
        summary = f"""
        {metrics.framework_type} 记忆框架影响评估摘要：
        
        • 记忆利用率：{metrics.memory_utilization_rate:.1%} ({metrics.responses_with_memory}/{metrics.total_responses} 个回复使用了记忆)
        • 质量影响：{quality_impact} (提升 {metrics.quality_improvement:+.3f} 分)
        • 性能开销：{performance_impact} (增加 {metrics.time_overhead:+.2f} 秒)
        • 记忆有效性：{metrics.memory_relevance_score:.1%} 相关性，{metrics.memory_consistency_score:.1%} 一致性
        
        结论：记忆框架{"有效提升了" if metrics.quality_improvement > 0.1 else "适度改善了" if metrics.quality_improvement > 0 else "对"}AI回复质量{"" if metrics.quality_improvement > 0 else "影响有限"}。
        """
        
        return summary.strip()
    
    def _generate_impact_insights(self, metrics: MemoryImpactMetrics) -> List[str]:
        """生成影响洞察"""
        
        insights = []
        
        # 质量影响洞察
        if metrics.quality_improvement > 0.15:
            insights.append("记忆框架显著提升了回复质量，建议保持当前的记忆利用策略")
        elif metrics.quality_improvement < -0.05:
            insights.append("记忆框架对质量产生了负面影响，需要优化记忆检索和应用机制")
        
        # 利用率洞察
        if metrics.memory_utilization_rate < 0.3:
            insights.append("记忆利用率偏低，建议增强记忆触发机制或扩大适用场景")
        elif metrics.memory_utilization_rate > 0.8:
            insights.append("记忆利用率很高，说明框架能够有效识别需要历史信息的场景")
        
        # 性能洞察
        if metrics.time_overhead > 2.0:
            insights.append("记忆检索产生了较大的性能开销，建议优化检索算法或缓存策略")
        elif metrics.time_overhead < 0.5:
            insights.append("记忆检索性能良好，对用户体验影响很小")
        
        # 相关性洞察
        if metrics.memory_relevance_score < 0.5:
            insights.append("检索到的记忆相关性较低，需要改进记忆匹配算法")
        elif metrics.memory_relevance_score > 0.8:
            insights.append("记忆检索高度相关，能够为AI提供有价值的上下文信息")
        
        # 一致性洞察
        if metrics.memory_consistency_score < 0.6:
            insights.append("记忆使用存在一致性问题，可能影响用户体验的连贯性")
        
        # 内容丰富度洞察
        if metrics.length_difference > 100:
            insights.append("记忆显著增强了回复的内容丰富度")
        elif metrics.length_difference < 0:
            insights.append("使用记忆后回复变得更简洁，可能表示更精准的信息提取")
        
        return insights