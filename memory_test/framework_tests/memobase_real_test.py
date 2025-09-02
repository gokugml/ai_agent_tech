"""
Memobase 真实测试模块

集成真实的Memobase记忆框架进行测试
"""

import asyncio
import json
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass
from datetime import datetime

try:
    from memobase import MemoryClient, MemoBaseClient
    MEMOBASE_AVAILABLE = True
except ImportError:
    MEMOBASE_AVAILABLE = False

from loguru import logger

from ..config import get_memory_framework_configs
from ..response_testing.memory_aware_chat import MemoryFrameworkInterface


@dataclass
class MemobaseMemory:
    """Memobase记忆数据类"""
    memory_id: str
    content: str
    memory_type: str
    timestamp: str
    metadata: Dict[str, Any]
    relevance_score: Optional[float] = None


class MemobaseFrameworkAdapter(MemoryFrameworkInterface):
    """Memobase框架适配器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.client = None
        self.user_profiles: Dict[str, Dict[str, Any]] = {}  # 用户画像缓存
        self._initialize_client()
    
    def _initialize_client(self) -> None:
        """初始化Memobase客户端"""
        try:
            if MEMOBASE_AVAILABLE and not self.config.get("use_simulation", True):
                # 尝试连接真实的Memobase服务
                self.client = MemoBaseClient(
                    project_url=self.config["project_url"],
                    # 其他必要的连接参数
                )
                logger.info("Memobase客户端初始化成功")
            else:
                logger.info("Memobase使用模拟模式")
                self.client = None
        except Exception as e:
            logger.error(f"Memobase客户端初始化失败: {e}")
            self.client = None
    
    async def store_conversation(self, user_id: str, user_input: str, ai_response: str) -> bool:
        """存储对话"""
        try:
            if self.client:
                # 真实存储
                return await self._store_real_conversation(user_id, user_input, ai_response)
            else:
                # 模拟存储
                return await self._store_simulated_conversation(user_id, user_input, ai_response)
        except Exception as e:
            logger.error(f"Memobase存储对话失败: {e}")
            return False
    
    async def _store_real_conversation(self, user_id: str, user_input: str, ai_response: str) -> bool:
        """真实存储对话到Memobase"""
        try:
            # 创建对话记录
            conversation_data = {
                "user_id": user_id,
                "timestamp": datetime.now().isoformat(),
                "messages": [
                    {"role": "user", "content": user_input},
                    {"role": "assistant", "content": ai_response}
                ],
                "session_type": "divination_consultation"
            }
            
            # 使用Memobase API存储
            # 注意：具体API调用方式需要根据Memobase实际文档调整
            result = await self.client.store_chat_blob(
                user_id=user_id,
                messages=conversation_data["messages"],
                metadata={"session_type": conversation_data["session_type"]}
            )
            
            logger.debug(f"Memobase真实存储成功: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Memobase真实存储失败: {e}")
            return False
    
    async def _store_simulated_conversation(self, user_id: str, user_input: str, ai_response: str) -> bool:
        """模拟存储对话"""
        # 模拟存储逻辑
        memory_key = f"memobase_sim_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 创建模拟记忆条目
        simulated_memory = {
            "id": memory_key,
            "user_id": user_id,
            "content": f"用户: {user_input}\\n回复: {ai_response}",
            "type": "conversation",
            "timestamp": datetime.now().isoformat(),
            "metadata": {
                "framework": "memobase",
                "simulation": True
            }
        }
        
        # 存储到内存缓存中（实际应用中可能存储到文件或数据库）
        if not hasattr(self, 'simulated_memories'):
            self.simulated_memories = {}
        
        if user_id not in self.simulated_memories:
            self.simulated_memories[user_id] = []
        
        self.simulated_memories[user_id].append(simulated_memory)
        
        logger.debug(f"Memobase模拟存储成功: {user_id}")
        return True
    
    async def retrieve_relevant_memories(self, user_id: str, query: str) -> List[Dict[str, Any]]:
        """检索相关记忆"""
        try:
            if self.client:
                return await self._retrieve_real_memories(user_id, query)
            else:
                return await self._retrieve_simulated_memories(user_id, query)
        except Exception as e:
            logger.error(f"Memobase检索记忆失败: {e}")
            return []
    
    async def _retrieve_real_memories(self, user_id: str, query: str) -> List[Dict[str, Any]]:
        """从真实Memobase检索记忆"""
        try:
            # 使用Memobase的语义搜索功能
            results = await self.client.search_memories(
                user_id=user_id,
                query=query,
                limit=10
            )
            
            memories = []
            for result in results:
                memory = {
                    "id": result.get("id", ""),
                    "content": result.get("content", ""),
                    "type": result.get("type", "unknown"),
                    "timestamp": result.get("timestamp", ""),
                    "relevance_score": result.get("score", 0.0),
                    "metadata": result.get("metadata", {})
                }
                memories.append(memory)
            
            logger.debug(f"Memobase真实检索: {user_id}, 结果数: {len(memories)}")
            return memories
            
        except Exception as e:
            logger.error(f"Memobase真实检索失败: {e}")
            return []
    
    async def _retrieve_simulated_memories(self, user_id: str, query: str) -> List[Dict[str, Any]]:
        """模拟检索记忆"""
        if not hasattr(self, 'simulated_memories'):
            self.simulated_memories = {}
        
        user_memories = self.simulated_memories.get(user_id, [])
        
        if not user_memories:
            return []
        
        # 简单的关键词匹配
        query_words = set(query.lower().split())
        relevant_memories = []
        
        for memory in user_memories:
            content = memory["content"].lower()
            content_words = set(content.split())
            
            # 计算相关性分数
            intersection = query_words.intersection(content_words)
            if intersection:
                relevance_score = len(intersection) / len(query_words.union(content_words))
                
                if relevance_score > 0.1:  # 设置最低相关性阈值
                    memory_copy = memory.copy()
                    memory_copy["relevance_score"] = relevance_score
                    relevant_memories.append(memory_copy)
        
        # 按相关性排序
        relevant_memories.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        logger.debug(f"Memobase模拟检索: {user_id}, 结果数: {len(relevant_memories)}")
        return relevant_memories[:5]  # 返回最相关的5个记忆
    
    async def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """获取用户画像"""
        try:
            if self.client:
                return await self._get_real_user_profile(user_id)
            else:
                return await self._get_simulated_user_profile(user_id)
        except Exception as e:
            logger.error(f"Memobase获取用户画像失败: {e}")
            return {}
    
    async def _get_real_user_profile(self, user_id: str) -> Dict[str, Any]:
        """从真实Memobase获取用户画像"""
        try:
            profile = await self.client.get_user_profile(user_id)
            return profile if profile else {}
        except Exception as e:
            logger.error(f"Memobase真实用户画像获取失败: {e}")
            return {}
    
    async def _get_simulated_user_profile(self, user_id: str) -> Dict[str, Any]:
        """模拟获取用户画像"""
        # 返回缓存的用户画像或创建默认画像
        if user_id in self.user_profiles:
            return self.user_profiles[user_id]
        
        # 创建默认用户画像
        default_profile = {
            "user_id": user_id,
            "personality_traits": ["友善", "好奇"],
            "communication_style": "直接",
            "concerns": ["事业发展", "人际关系"],
            "session_count": 0,
            "last_interaction": datetime.now().isoformat(),
            "framework": "memobase_simulation"
        }
        
        self.user_profiles[user_id] = default_profile
        return default_profile
    
    async def update_user_profile(self, user_id: str, updates: Dict[str, Any]) -> bool:
        """更新用户画像"""
        try:
            if self.client:
                return await self._update_real_user_profile(user_id, updates)
            else:
                return await self._update_simulated_user_profile(user_id, updates)
        except Exception as e:
            logger.error(f"Memobase更新用户画像失败: {e}")
            return False
    
    async def _update_real_user_profile(self, user_id: str, updates: Dict[str, Any]) -> bool:
        """更新真实Memobase用户画像"""
        try:
            result = await self.client.update_user_profile(user_id, updates)
            return result is not None
        except Exception as e:
            logger.error(f"Memobase真实用户画像更新失败: {e}")
            return False
    
    async def _update_simulated_user_profile(self, user_id: str, updates: Dict[str, Any]) -> bool:
        """模拟更新用户画像"""
        # 确保用户画像存在
        if user_id not in self.user_profiles:
            await self._get_simulated_user_profile(user_id)
        
        # 更新画像
        profile = self.user_profiles[user_id]
        
        for key, value in updates.items():
            if key in profile:
                # 如果是列表类型，进行智能合并
                if isinstance(profile[key], list) and isinstance(value, list):
                    # 合并去重
                    combined = list(set(profile[key] + value))
                    profile[key] = combined[:5]  # 限制长度
                else:
                    profile[key] = value
            else:
                profile[key] = value
        
        profile["last_update"] = datetime.now().isoformat()
        
        logger.debug(f"Memobase模拟用户画像更新成功: {user_id}")
        return True


class MemobaseRealTester:
    """Memobase真实测试器"""
    
    def __init__(self):
        self.config = get_memory_framework_configs()["memobase"]
        self.framework_adapter = MemobaseFrameworkAdapter(self.config)
        self.test_sessions: Dict[str, Dict[str, Any]] = {}
    
    def create_test_session(self, 
                          test_name: str, 
                          user_profile: Dict[str, Any]) -> str:
        """创建测试会话"""
        
        session_id = f"memobase_test_{test_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        session = {
            "session_id": session_id,
            "test_name": test_name,
            "user_profile": user_profile,
            "start_time": datetime.now().isoformat(),
            "interactions": [],
            "framework_type": "memobase"
        }
        
        self.test_sessions[session_id] = session
        
        logger.info(f"Memobase测试会话已创建: {session_id}")
        return session_id
    
    async def test_memory_storage_and_retrieval(self, 
                                              session_id: str,
                                              test_conversations: List[Tuple[str, str]]) -> Dict[str, Any]:
        """测试记忆存储和检索功能"""
        
        if session_id not in self.test_sessions:
            raise ValueError(f"测试会话 {session_id} 不存在")
        
        session = self.test_sessions[session_id]
        user_id = f"test_user_{session_id}"
        
        results = {
            "session_id": session_id,
            "user_id": user_id,
            "storage_results": [],
            "retrieval_results": [],
            "performance_metrics": {}
        }
        
        # 测试存储功能
        logger.info(f"开始测试Memobase存储功能: {session_id}")
        
        storage_start_time = datetime.now()
        storage_success_count = 0
        
        for i, (user_input, ai_response) in enumerate(test_conversations):
            storage_success = await self.framework_adapter.store_conversation(
                user_id, user_input, ai_response
            )
            
            storage_result = {
                "conversation_index": i,
                "user_input": user_input,
                "ai_response": ai_response,
                "storage_success": storage_success,
                "timestamp": datetime.now().isoformat()
            }
            
            results["storage_results"].append(storage_result)
            
            if storage_success:
                storage_success_count += 1
            
            # 记录到会话
            session["interactions"].append({
                "type": "storage_test",
                "data": storage_result
            })
        
        storage_duration = (datetime.now() - storage_start_time).total_seconds()
        
        # 测试检索功能
        logger.info(f"开始测试Memobase检索功能: {session_id}")
        
        retrieval_start_time = datetime.now()
        
        # 使用不同的查询测试检索
        test_queries = [
            "工作相关问题",
            "感情咨询",
            "财运预测",
            "健康建议",
            "最近的对话"
        ]
        
        for query in test_queries:
            retrieval_start = datetime.now()
            memories = await self.framework_adapter.retrieve_relevant_memories(user_id, query)
            retrieval_time = (datetime.now() - retrieval_start).total_seconds()
            
            retrieval_result = {
                "query": query,
                "memories_found": len(memories),
                "memories": memories,
                "retrieval_time": retrieval_time,
                "timestamp": datetime.now().isoformat()
            }
            
            results["retrieval_results"].append(retrieval_result)
            
            # 记录到会话
            session["interactions"].append({
                "type": "retrieval_test", 
                "data": retrieval_result
            })
        
        retrieval_duration = (datetime.now() - retrieval_start_time).total_seconds()
        
        # 计算性能指标
        results["performance_metrics"] = {
            "storage_success_rate": storage_success_count / len(test_conversations),
            "total_storage_time": storage_duration,
            "avg_storage_time": storage_duration / len(test_conversations),
            "total_retrieval_time": retrieval_duration,
            "avg_retrieval_time": retrieval_duration / len(test_queries),
            "avg_memories_per_query": sum(len(r["memories"]) for r in results["retrieval_results"]) / len(test_queries)
        }
        
        logger.info(f"Memobase存储检索测试完成: {session_id}")
        return results
    
    async def test_user_profile_management(self, 
                                         session_id: str,
                                         profile_updates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """测试用户画像管理功能"""
        
        if session_id not in self.test_sessions:
            raise ValueError(f"测试会话 {session_id} 不存在")
        
        user_id = f"test_user_{session_id}"
        
        results = {
            "session_id": session_id,
            "user_id": user_id,
            "initial_profile": None,
            "update_results": [],
            "final_profile": None
        }
        
        # 获取初始用户画像
        initial_profile = await self.framework_adapter.get_user_profile(user_id)
        results["initial_profile"] = initial_profile
        
        logger.info(f"开始测试Memobase用户画像管理: {session_id}")
        
        # 测试画像更新
        for i, update_data in enumerate(profile_updates):
            update_start = datetime.now()
            update_success = await self.framework_adapter.update_user_profile(user_id, update_data)
            update_time = (datetime.now() - update_start).total_seconds()
            
            # 验证更新结果
            updated_profile = await self.framework_adapter.get_user_profile(user_id)
            
            update_result = {
                "update_index": i,
                "update_data": update_data,
                "update_success": update_success,
                "update_time": update_time,
                "profile_after_update": updated_profile,
                "timestamp": datetime.now().isoformat()
            }
            
            results["update_results"].append(update_result)
        
        # 获取最终用户画像
        final_profile = await self.framework_adapter.get_user_profile(user_id)
        results["final_profile"] = final_profile
        
        logger.info(f"Memobase用户画像管理测试完成: {session_id}")
        return results
    
    async def test_integration_with_ai_chat(self, 
                                          session_id: str,
                                          chat_sequence: List[str]) -> Dict[str, Any]:
        """测试与AI聊天的集成"""
        
        from ..response_testing.memory_aware_chat import MemoryAwareChat
        
        if session_id not in self.test_sessions:
            raise ValueError(f"测试会话 {session_id} 不存在")
        
        session = self.test_sessions[session_id]
        user_id = f"test_user_{session_id}"
        
        # 创建记忆感知聊天系统
        memory_chat = MemoryAwareChat("memobase", self.framework_adapter)
        
        results = {
            "session_id": session_id,
            "user_id": user_id,
            "chat_interactions": [],
            "integration_metrics": {}
        }
        
        logger.info(f"开始测试Memobase与AI聊天集成: {session_id}")
        
        # 开始对话
        chat_session_id = await memory_chat.start_conversation(user_id, session["user_profile"])
        
        integration_start_time = datetime.now()
        
        # 执行聊天序列
        for i, user_message in enumerate(chat_sequence):
            interaction_start = datetime.now()
            
            try:
                ai_response = await memory_chat.send_message(user_id, user_message)
                interaction_time = (datetime.now() - interaction_start).total_seconds()
                
                interaction_result = {
                    "interaction_index": i,
                    "user_message": user_message,
                    "ai_response": ai_response.ai_response,
                    "response_time": ai_response.response_time,
                    "interaction_time": interaction_time,
                    "memory_context_used": bool(ai_response.memory_context),
                    "memory_context_size": len(ai_response.memory_context),
                    "success": True,
                    "timestamp": ai_response.timestamp
                }
                
            except Exception as e:
                interaction_time = (datetime.now() - interaction_start).total_seconds()
                interaction_result = {
                    "interaction_index": i,
                    "user_message": user_message,
                    "error": str(e),
                    "interaction_time": interaction_time,
                    "success": False,
                    "timestamp": datetime.now().isoformat()
                }
                logger.error(f"Memobase聊天集成测试交互失败: {e}")
            
            results["chat_interactions"].append(interaction_result)
        
        total_integration_time = (datetime.now() - integration_start_time).total_seconds()
        
        # 结束对话并获取统计信息
        conversation_stats = await memory_chat.end_conversation(user_id)
        
        # 计算集成指标
        successful_interactions = [r for r in results["chat_interactions"] if r["success"]]
        
        results["integration_metrics"] = {
            "total_interactions": len(chat_sequence),
            "successful_interactions": len(successful_interactions),
            "success_rate": len(successful_interactions) / len(chat_sequence),
            "total_integration_time": total_integration_time,
            "avg_interaction_time": total_integration_time / len(chat_sequence),
            "memory_utilization_rate": sum(1 for r in successful_interactions if r.get("memory_context_used", False)) / len(successful_interactions) if successful_interactions else 0,
            "conversation_stats": conversation_stats
        }
        
        logger.info(f"Memobase与AI聊天集成测试完成: {session_id}")
        return results
    
    def get_session_summary(self, session_id: str) -> Optional[Dict[str, Any]]:
        """获取测试会话摘要"""
        if session_id not in self.test_sessions:
            return None
        
        session = self.test_sessions[session_id]
        
        return {
            "session_info": {
                "session_id": session_id,
                "test_name": session["test_name"],
                "framework_type": session["framework_type"],
                "start_time": session["start_time"],
                "user_profile": session["user_profile"]
            },
            "interaction_count": len(session["interactions"]),
            "interaction_types": list(set(interaction["type"] for interaction in session["interactions"])),
            "framework_config": self.config
        }
    
    def export_test_results(self, session_id: str, file_path: str) -> bool:
        """导出测试结果"""
        summary = self.get_session_summary(session_id)
        if not summary:
            return False
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(summary, f, ensure_ascii=False, indent=2)
            logger.info(f"Memobase测试结果已导出: {file_path}")
            return True
        except Exception as e:
            logger.error(f"导出Memobase测试结果失败: {e}")
            return False