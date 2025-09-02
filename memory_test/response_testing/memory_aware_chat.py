"""
记忆感知聊天系统

集成记忆框架，让AI能够访问和利用历史信息进行回复
"""

import asyncio
from typing import Dict, List, Any, Optional, Union, Protocol
from dataclasses import dataclass
from abc import ABC, abstractmethod
from datetime import datetime

from loguru import logger

from .real_ai_tester import RealAITester, AIResponse


class MemoryFrameworkInterface(Protocol):
    """记忆框架接口协议"""
    
    async def store_conversation(self, user_id: str, user_input: str, ai_response: str) -> bool:
        """存储对话"""
        ...
    
    async def retrieve_relevant_memories(self, user_id: str, query: str) -> List[Dict[str, Any]]:
        """检索相关记忆"""
        ...
    
    async def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """获取用户画像"""
        ...
    
    async def update_user_profile(self, user_id: str, updates: Dict[str, Any]) -> bool:
        """更新用户画像"""
        ...


@dataclass
class MemoryContext:
    """记忆上下文数据类"""
    user_id: str
    retrieved_memories: List[Dict[str, Any]]
    user_profile: Dict[str, Any]
    conversation_history: List[Dict[str, str]]
    context_summary: str
    relevance_scores: Dict[str, float]
    memory_types: List[str]


class MemoryContextBuilder:
    """记忆上下文构建器"""
    
    def __init__(self, memory_framework: MemoryFrameworkInterface):
        self.memory_framework = memory_framework
        
    async def build_context(self, 
                          user_id: str, 
                          current_query: str,
                          conversation_history: Optional[List[Dict[str, str]]] = None) -> MemoryContext:
        """构建记忆上下文"""
        
        try:
            # 并行获取记忆信息
            memories_task = self.memory_framework.retrieve_relevant_memories(user_id, current_query)
            profile_task = self.memory_framework.get_user_profile(user_id)
            
            retrieved_memories = await memories_task
            user_profile = await profile_task
            
            # 分析记忆类型和相关性
            memory_types = self._analyze_memory_types(retrieved_memories)
            relevance_scores = self._calculate_relevance_scores(retrieved_memories, current_query)
            
            # 生成上下文总结
            context_summary = self._generate_context_summary(
                retrieved_memories, 
                user_profile, 
                current_query
            )
            
            context = MemoryContext(
                user_id=user_id,
                retrieved_memories=retrieved_memories,
                user_profile=user_profile,
                conversation_history=conversation_history or [],
                context_summary=context_summary,
                relevance_scores=relevance_scores,
                memory_types=memory_types
            )
            
            logger.debug(f"构建记忆上下文: {user_id}, 记忆数: {len(retrieved_memories)}")
            return context
            
        except Exception as e:
            logger.error(f"构建记忆上下文失败: {e}")
            # 返回空上下文
            return MemoryContext(
                user_id=user_id,
                retrieved_memories=[],
                user_profile={},
                conversation_history=conversation_history or [],
                context_summary="暂无可用的记忆上下文",
                relevance_scores={},
                memory_types=[]
            )
    
    def _analyze_memory_types(self, memories: List[Dict[str, Any]]) -> List[str]:
        """分析记忆类型"""
        types = set()
        for memory in memories:
            memory_type = memory.get("type", "unknown")
            types.add(memory_type)
        return list(types)
    
    def _calculate_relevance_scores(self, 
                                  memories: List[Dict[str, Any]], 
                                  query: str) -> Dict[str, float]:
        """计算相关性分数"""
        scores = {}
        
        for i, memory in enumerate(memories):
            memory_id = memory.get("id", f"memory_{i}")
            content = memory.get("content", "")
            
            # 简单的关键词匹配计分
            query_words = set(query.lower().split())
            content_words = set(content.lower().split())
            
            if query_words and content_words:
                intersection = query_words.intersection(content_words)
                score = len(intersection) / len(query_words.union(content_words))
            else:
                score = 0.0
            
            # 考虑记忆的时间衰减
            timestamp = memory.get("timestamp")
            if timestamp:
                try:
                    memory_time = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                    time_diff = (datetime.now() - memory_time.replace(tzinfo=None)).days
                    time_decay = max(0.1, 1.0 - (time_diff / 365))  # 一年内衰减
                    score *= time_decay
                except Exception:
                    pass
            
            scores[memory_id] = score
        
        return scores
    
    def _generate_context_summary(self, 
                                memories: List[Dict[str, Any]], 
                                user_profile: Dict[str, Any], 
                                current_query: str) -> str:
        """生成上下文总结"""
        
        if not memories and not user_profile:
            return "这是一次新的对话，暂无历史记忆信息。"
        
        summary_parts = []
        
        # 用户画像总结
        if user_profile:
            profile_summary = self._summarize_user_profile(user_profile)
            if profile_summary:
                summary_parts.append(f"用户画像：{profile_summary}")
        
        # 记忆总结
        if memories:
            memory_summary = self._summarize_memories(memories)
            if memory_summary:
                summary_parts.append(f"相关记忆：{memory_summary}")
        
        return " | ".join(summary_parts)
    
    def _summarize_user_profile(self, profile: Dict[str, Any]) -> str:
        """总结用户画像"""
        summary_parts = []
        
        # 基本信息
        if "personality_traits" in profile:
            traits = profile["personality_traits"][:3]  # 只取前3个特征
            summary_parts.append(f"性格特征：{', '.join(traits)}")
        
        if "communication_style" in profile:
            style = profile["communication_style"]
            summary_parts.append(f"沟通风格：{style}")
        
        if "concerns" in profile:
            concerns = profile["concerns"][:2]  # 只取前2个关注点
            summary_parts.append(f"主要关注：{', '.join(concerns)}")
        
        return "；".join(summary_parts)
    
    def _summarize_memories(self, memories: List[Dict[str, Any]]) -> str:
        """总结记忆内容"""
        if len(memories) == 0:
            return "暂无相关记忆"
        
        # 按类型分组
        memory_by_type = {}
        for memory in memories[:5]:  # 只处理前5个最相关的记忆
            mem_type = memory.get("type", "general")
            content = memory.get("content", "")[:100]  # 限制长度
            
            if mem_type not in memory_by_type:
                memory_by_type[mem_type] = []
            memory_by_type[mem_type].append(content)
        
        # 生成摘要
        summary_parts = []
        for mem_type, contents in memory_by_type.items():
            type_summary = f"{mem_type}({len(contents)}项)"
            summary_parts.append(type_summary)
        
        return "；".join(summary_parts)


class MemoryAwareChat:
    """记忆感知聊天系统"""
    
    def __init__(self, 
                 framework_type: str,
                 memory_framework: MemoryFrameworkInterface):
        self.framework_type = framework_type
        self.memory_framework = memory_framework
        self.ai_tester = RealAITester(framework_type)
        self.context_builder = MemoryContextBuilder(memory_framework)
        
        # 对话会话映射
        self.user_sessions: Dict[str, str] = {}  # user_id -> session_id
    
    async def start_conversation(self, user_id: str, user_profile: Dict[str, Any]) -> str:
        """开始对话"""
        
        # 创建AI测试会话
        session_id = self.ai_tester.create_test_session(user_profile)
        self.user_sessions[user_id] = session_id
        
        logger.info(f"开始记忆感知对话: {user_id} -> {session_id} (框架: {self.framework_type})")
        return session_id
    
    async def send_message(self, user_id: str, message: str) -> AIResponse:
        """发送消息并获取回复"""
        
        if user_id not in self.user_sessions:
            raise ValueError(f"用户 {user_id} 没有活跃的对话会话")
        
        session_id = self.user_sessions[user_id]
        
        try:
            # 构建记忆上下文
            memory_context = await self._build_memory_context(user_id, message, session_id)
            
            # 生成AI回复
            ai_response = await self.ai_tester.generate_ai_response(
                session_id, 
                message, 
                self._convert_memory_context_to_dict(memory_context)
            )
            
            # 存储对话到记忆框架
            await self._store_conversation(user_id, message, ai_response.ai_response)
            
            # 更新用户画像
            await self._update_user_profile_from_interaction(
                user_id, 
                message, 
                ai_response.ai_response
            )
            
            logger.info(f"消息处理完成: {user_id}, 回复长度: {len(ai_response.ai_response)}")
            
            return ai_response
            
        except Exception as e:
            logger.error(f"发送消息失败: {e}")
            raise
    
    async def _build_memory_context(self, 
                                  user_id: str, 
                                  message: str, 
                                  session_id: str) -> MemoryContext:
        """构建记忆上下文"""
        
        # 获取当前会话的对话历史
        session = self.ai_tester.active_sessions.get(session_id)
        conversation_history = session.conversation_history if session else []
        
        # 构建记忆上下文
        context = await self.context_builder.build_context(
            user_id, 
            message, 
            conversation_history
        )
        
        return context
    
    def _convert_memory_context_to_dict(self, context: MemoryContext) -> Dict[str, Any]:
        """将记忆上下文转换为字典"""
        return {
            "user_profile": context.user_profile,
            "retrieved_memories": context.retrieved_memories,
            "context_summary": context.context_summary,
            "memory_types": context.memory_types,
            "relevance_scores": context.relevance_scores,
            "total_memories": len(context.retrieved_memories)
        }
    
    async def _store_conversation(self, user_id: str, user_input: str, ai_response: str) -> None:
        """存储对话"""
        try:
            await self.memory_framework.store_conversation(user_id, user_input, ai_response)
            logger.debug(f"对话已存储: {user_id}")
        except Exception as e:
            logger.error(f"存储对话失败: {e}")
    
    async def _update_user_profile_from_interaction(self, 
                                                  user_id: str, 
                                                  user_input: str, 
                                                  ai_response: str) -> None:
        """根据交互更新用户画像"""
        try:
            # 分析用户输入特征
            updates = self._analyze_user_input_characteristics(user_input)
            
            if updates:
                await self.memory_framework.update_user_profile(user_id, updates)
                logger.debug(f"用户画像已更新: {user_id}")
        except Exception as e:
            logger.error(f"更新用户画像失败: {e}")
    
    def _analyze_user_input_characteristics(self, user_input: str) -> Dict[str, Any]:
        """分析用户输入特征"""
        updates = {}
        
        # 分析沟通风格
        input_length = len(user_input)
        if input_length < 20:
            updates["communication_tendency"] = "简洁"
        elif input_length > 100:
            updates["communication_tendency"] = "详细"
        
        # 分析情绪色彩
        positive_keywords = ["谢谢", "好", "不错", "满意", "喜欢"]
        negative_keywords = ["不好", "担心", "焦虑", "问题", "困扰"]
        
        positive_count = sum(1 for word in positive_keywords if word in user_input)
        negative_count = sum(1 for word in negative_keywords if word in user_input)
        
        if positive_count > negative_count:
            updates["emotional_tendency"] = "积极"
        elif negative_count > positive_count:
            updates["emotional_tendency"] = "消极"
        
        # 分析主题偏好
        topic_keywords = {
            "事业": ["工作", "职业", "事业", "升职", "跳槽"],
            "感情": ["恋爱", "结婚", "分手", "感情", "爱情"],
            "财运": ["钱", "财运", "投资", "理财", "收入"],
            "健康": ["健康", "身体", "生病", "医院", "保养"]
        }
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in user_input for keyword in keywords):
                if "preferred_topics" not in updates:
                    updates["preferred_topics"] = []
                updates["preferred_topics"].append(topic)
        
        return updates
    
    async def end_conversation(self, user_id: str) -> Optional[Dict[str, Any]]:
        """结束对话"""
        if user_id not in self.user_sessions:
            return None
        
        session_id = self.user_sessions[user_id]
        
        # 获取会话摘要
        session_summary = self.ai_tester.get_session_summary(session_id)
        
        # 清理会话
        self.ai_tester.cleanup_session(session_id)
        del self.user_sessions[user_id]
        
        logger.info(f"对话已结束: {user_id}")
        return session_summary
    
    async def get_conversation_statistics(self, user_id: str) -> Optional[Dict[str, Any]]:
        """获取对话统计信息"""
        if user_id not in self.user_sessions:
            return None
        
        session_id = self.user_sessions[user_id]
        return self.ai_tester.get_session_summary(session_id)
    
    def get_framework_type(self) -> str:
        """获取框架类型"""
        return self.framework_type
    
    def is_conversation_active(self, user_id: str) -> bool:
        """检查对话是否活跃"""
        return user_id in self.user_sessions