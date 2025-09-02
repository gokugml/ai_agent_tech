"""
Memobase 记忆框架测试器

使用真实的 Memobase 记忆框架进行测试，支持自托管模式
"""

import os
import json
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

try:
    from memobase import MemoBaseClient, ChatBlob
except ImportError:
    print("警告: memobase 未正确安装，将使用模拟模式")
    MemoBaseClient = None
    ChatBlob = None

from config import settings
from loguru import logger

class MemobaseTester:
    """Memobase 记忆框架测试器"""
    
    def __init__(self, user_id: str = "test_user"):
        """
        初始化 Memobase 测试器
        
        Args:
            user_id: 测试用户ID
        """
        self.user_id = user_id
        self.client = None
        self.user = None
        self.fallback_mode = MemoBaseClient is None or ChatBlob is None
        self.conversation_history: List[Dict] = []
        self.start_time = None
        
        if not self.fallback_mode:
            self._initialize_client()
        else:
            logger.warning("Memobase 库未安装，使用模拟模式")
            self._initialize_fallback()
    
    def _initialize_client(self):
        """初始化真实的 Memobase 客户端"""
        try:
            # 根据官方文档正确初始化：project_url 在前，api_key 在后
            self.client = MemoBaseClient(
                project_url=settings.MEMOBASE_URL,
                api_key=settings.MEMOBASE_API_KEY
            )
            
            # 测试连接
            ping_result = self.client.ping()
            if ping_result:
                logger.info(f"已连接到 Memobase 自托管服务: {settings.MEMOBASE_URL}")
            else:
                raise Exception("ping 测试失败")
                
        except Exception as e:
            logger.error(f"Memobase 客户端初始化失败: {e}")
            self.fallback_mode = True
            self._initialize_fallback()
    
    def _initialize_fallback(self):
        """初始化模拟模式"""
        self.memory_store = {}
        self.chat_style = {}
        self.divination_history = []
        logger.info("Memobase 测试器运行在模拟模式")
        
    def initialize_memory(self) -> bool:
        """
        初始化记忆系统
        
        Returns:
            bool: 初始化是否成功
        """
        try:
            self.start_time = datetime.now()
            
            if not self.fallback_mode and self.client:
                # 尝试多种用户创建方式
                try:
                    # 方式1：只传 id
                    created_user_id = self.client.add_user(id=self.user_id)
                    self.user = self.client.get_user(created_user_id)
                    logger.info(f"Memobase 用户创建成功（方式1），ID: {created_user_id}")
                    return True
                except Exception as e1:
                    try:
                        # 方式2：传空数据
                        created_user_id = self.client.add_user()
                        self.user = self.client.get_user(created_user_id)
                        logger.info(f"Memobase 用户创建成功（方式2），ID: {created_user_id}")
                        return True
                    except Exception as e2:
                        try:
                            # 方式3：直接获取用户（如果已存在）
                            self.user = self.client.get_user(self.user_id)
                            logger.info(f"Memobase 用户已存在，直接获取: {self.user_id}")
                            return True
                        except Exception as e3:
                            raise Exception(f"所有用户创建方式都失败: {e1}, {e2}, {e3}")
            else:
                # 模拟模式初始化
                self.memory_store = {
                    "conversations": [],
                    "chat_style": {},
                    "divination_history": [],
                    "extracted_info": [],
                    "verification_feedback": []
                }
                return True
                
        except Exception as e:
            logger.error(f"Memobase 初始化失败: {e}")
            return False
    
    def store_memory(self, memory_type: str, content: Any, metadata: Optional[Dict] = None) -> bool:
        """
        存储记忆内容
        
        Args:
            memory_type: 记忆类型
            content: 记忆内容
            metadata: 元数据
            
        Returns:
            bool: 存储是否成功
        """
        try:
            if not self.fallback_mode and self.user:
                # 使用真实 Memobase API 存储记忆，使用 ChatBlob 格式
                if isinstance(content, str):
                    # 将字符串内容转换为消息格式
                    messages = [{"role": "user", "content": f"[{memory_type}] {content}"}]
                elif isinstance(content, dict):
                    # 将字典内容转换为消息格式
                    content_str = f"[{memory_type}] {str(content)}"
                    messages = [{"role": "user", "content": content_str}]
                elif isinstance(content, list) and all(isinstance(item, dict) and 'role' in item for item in content):
                    # 如果已经是正确的消息格式，直接使用
                    messages = content
                else:
                    # 其他类型转换为字符串消息
                    content_str = f"[{memory_type}] {str(content)}"
                    messages = [{"role": "user", "content": content_str}]
                
                chat_blob = ChatBlob(
                    messages=messages,
                    metadata={
                        'type': memory_type,
                        'timestamp': datetime.now().isoformat(),
                        **(metadata or {})
                    }
                )
                
                self.user.insert(chat_blob)
                logger.debug(f"Memobase 记忆存储成功: {memory_type}")
                return True
            else:
                # 模拟模式存储
                timestamp = datetime.now().isoformat()
                
                if memory_type not in self.memory_store:
                    self.memory_store[memory_type] = []
                
                self.memory_store[memory_type].append({
                    "timestamp": timestamp,
                    "content": content,
                    "metadata": metadata or {}
                })
                
                return True
                
        except Exception as e:
            logger.error(f"Memobase 存储记忆失败: {e}")
            return False
    
    def retrieve_memory(self, memory_type: str, query: Optional[str] = None, limit: int = 10) -> List[Dict]:
        """
        检索记忆内容
        
        Args:
            memory_type: 记忆类型
            query: 查询关键词
            limit: 返回结果数量限制
            
        Returns:
            检索到的记忆列表
        """
        try:
            if not self.fallback_mode and self.user:
                # 使用真实 Memobase API 检索记忆，使用 context 方法
                if query:
                    # 如果有查询关键词，构造相关的消息来获取上下文
                    recent_chats = [{"role": "user", "content": query}]
                    context_result = self.user.context(chats=recent_chats, max_token_size=1000)
                else:
                    # 获取默认的上下文
                    context_result = self.user.context(max_token_size=1000)
                
                # 简化返回结果格式，以便与其他方法兼容
                return [{
                    'content': context_result,
                    'metadata': {'type': memory_type, 'retrieved_via': 'context'},
                    'timestamp': datetime.now().isoformat()
                }]
            else:
                # 模拟模式检索
                if memory_type not in self.memory_store:
                    return []
                
                memories = self.memory_store[memory_type]
                
                if query:
                    # 简单的关键词匹配
                    memories = [m for m in memories if query.lower() in str(m["content"]).lower()]
                
                return memories[-limit:] if limit > 0 else memories
                
        except Exception as e:
            logger.error(f"Memobase 检索记忆失败: {e}")
            return []
    
    def update_chat_style(self, style_indicators: Dict[str, float]) -> None:
        """
        更新用户聊天风格记忆
        
        Args:
            style_indicators: 风格指标字典
        """
        try:
            if not self.fallback_mode and self.user:
                # 使用真实 Memobase API 更新风格偏好
                style_content = {
                    "chat_style_update": style_indicators,
                    "learning_context": "style_adaptation"
                }
                self.store_memory("chat_style", style_content)
            else:
                # 模拟模式更新
                current_style = self.memory_store.get("chat_style", {})
                
                # 更新风格偏好
                for key, value in style_indicators.items():
                    if key in current_style:
                        # 加权平均更新（简化实现）
                        current_style[key] = (current_style[key] + value) / 2
                    else:
                        current_style[key] = value
                
                self.memory_store["chat_style"] = current_style
                
        except Exception as e:
            logger.error(f"Memobase 更新聊天风格失败: {e}")
    
    def get_chat_style(self) -> Dict[str, Any]:
        """
        获取当前学习到的聊天风格
        
        Returns:
            聊天风格字典
        """
        try:
            if not self.fallback_mode and self.user:
                # 从 Memobase 检索聊天风格信息
                style_memories = self.retrieve_memory("chat_style")
                
                # 解析最新的风格偏好
                current_style = {}
                for memory in style_memories:
                    content = memory.get('content', {})
                    if isinstance(content, dict) and 'chat_style_update' in content:
                        current_style.update(content['chat_style_update'])
                
                return current_style
            else:
                # 模拟模式获取
                return self.memory_store.get("chat_style", {})
                
        except Exception as e:
            logger.error(f"Memobase 获取聊天风格失败: {e}")
            return {}
    
    def add_conversation_turn(self, user_input: str, ai_response: str, 
                           metadata: Optional[Dict] = None) -> None:
        """
        添加对话轮次
        
        Args:
            user_input: 用户输入
            ai_response: AI回复
            metadata: 元数据
        """
        try:
            conversation_data = {
                "user_input": user_input,
                "ai_response": ai_response,
                "turn_number": len(self.conversation_history) + 1,
                "metadata": metadata or {}
            }
            
            # 存储到本地历史
            turn = {
                "timestamp": datetime.now().isoformat(),
                **conversation_data
            }
            self.conversation_history.append(turn)
            
            # 存储到 Memobase
            self.store_memory("conversation", conversation_data)
            
        except Exception as e:
            logger.error(f"Memobase 添加对话轮次失败: {e}")
    
    def store_divination_result(self, prediction: str, verification_status: Optional[str] = None,
                              accuracy_score: Optional[float] = None) -> None:
        """
        存储算命结果
        
        Args:
            prediction: 预测内容
            verification_status: 验证状态
            accuracy_score: 准确性分数
        """
        try:
            divination_data = {
                "prediction": prediction,
                "verification_status": verification_status,
                "accuracy_score": accuracy_score,
                "timestamp": datetime.now().isoformat()
            }
            
            # 存储到 Memobase
            self.store_memory("divination_history", divination_data)
            
        except Exception as e:
            logger.error(f"Memobase 算命结果存储失败: {e}")
    
    def extract_divination_info(self, conversation_text: str) -> Dict[str, Any]:
        """
        从对话中提取算命相关信息
        
        Args:
            conversation_text: 对话文本
            
        Returns:
            提取的信息字典
        """
        try:
            extracted_info = {
                "life_changes": [],
                "time_references": [],
                "emotional_states": [],
                "verification_feedback": []
            }
            
            text_lower = conversation_text.lower()
            
            # 使用更复杂的语义分析（此处简化）
            life_change_patterns = {
                "job_change": ["换工作", "跳槽", "新工作", "辞职"],
                "relationship": ["结婚", "分手", "离婚", "恋爱"],
                "health": ["生病", "住院", "康复", "手术"],
                "financial": ["买房", "投资", "破财", "中奖"],
                "location": ["搬家", "出国", "回国", "旅行"]
            }
            
            for category, keywords in life_change_patterns.items():
                for keyword in keywords:
                    if keyword in text_lower:
                        extracted_info["life_changes"].append({
                            "category": category,
                            "keyword": keyword,
                            "confidence": 0.8
                        })
            
            # 时间参考关键词
            time_keywords = ["去年", "今年", "明年", "上个月", "下个月", "最近"]
            for keyword in time_keywords:
                if keyword in text_lower:
                    extracted_info["time_references"].append(keyword)
            
            # 验证反馈关键词
            verification_keywords = ["确实", "没错", "不对", "不是这样", "准确"]
            for keyword in verification_keywords:
                if keyword in text_lower:
                    extracted_info["verification_feedback"].append(keyword)
            
            # 存储提取的信息
            if any(extracted_info.values()):
                self.store_memory("extracted_info", extracted_info)
            
            return extracted_info
            
        except Exception as e:
            logger.error(f"Memobase 信息提取失败: {e}")
            return {}
    
    def get_divination_history(self, limit: int = 10) -> List[Dict]:
        """
        获取算命历史记录
        
        Args:
            limit: 返回记录数量限制
            
        Returns:
            算命历史列表
        """
        try:
            return self.retrieve_memory("divination_history", limit=limit)
        except Exception as e:
            logger.error(f"Memobase 算命历史获取失败: {e}")
            return []
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """
        获取记忆统计信息
        
        Returns:
            统计信息字典
        """
        try:
            if not self.fallback_mode and self.user:
                # 从真实 Memobase 获取统计信息 - 使用可用的方法
                # User 对象没有 get_chat_blobs 方法，使用基础信息
                return {
                    "framework": "Memobase (真实)",
                    "total_conversations": len(self.conversation_history),
                    "user_connected": True,
                    "runtime_seconds": (datetime.now() - self.start_time).total_seconds() if self.start_time else 0
                }
            else:
                # 模拟模式统计
                memory_counts = {k: len(v) if isinstance(v, list) else 1 
                               for k, v in self.memory_store.items()}
                
                return {
                    "framework": "Memobase (模拟)",
                    "total_conversations": len(self.conversation_history),
                    "memory_counts": memory_counts,
                    "total_memories": sum(memory_counts.values()),
                    "runtime_seconds": (datetime.now() - self.start_time).total_seconds() if self.start_time else 0
                }
                
        except Exception as e:
            logger.error(f"Memobase 获取统计信息失败: {e}")
            return {"framework": "Memobase (错误)", "error": str(e)}
    
    def export_test_results(self, file_path: str) -> bool:
        """
        导出测试结果
        
        Args:
            file_path: 导出文件路径
            
        Returns:
            bool: 导出是否成功
        """
        try:
            results = {
                "user_id": self.user_id,
                "framework": "Memobase",
                "fallback_mode": self.fallback_mode,
                "conversation_history": self.conversation_history,
                "memories": self.retrieve_memory("conversation", limit=1000),
                "chat_styles": self.get_chat_style(),
                "divination_history": self.get_divination_history(limit=100),
                "stats": self.get_memory_stats(),
                "export_time": datetime.now().isoformat()
            }
            
            # 在模拟模式下包含内存存储
            if self.fallback_mode:
                results["memory_store"] = self.memory_store
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Memobase 测试结果已导出: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Memobase 结果导出失败: {e}")
            return False
    
    def cleanup(self):
        """清理资源"""
        try:
            if not self.fallback_mode and self.client and self.user:
                # 清理 Memobase 资源（如果需要删除测试数据）
                if not settings.KEEP_TEST_DATA:
                    # Memobase 不支持删除用户，所以这里只做日志记录
                    logger.info(f"Memobase 测试数据保留: {self.user_id}")
            else:
                # 清理模拟数据
                if hasattr(self, 'memory_store'):
                    self.memory_store.clear()
                if hasattr(self, 'chat_style'):
                    self.chat_style.clear()
                if hasattr(self, 'divination_history'):
                    self.divination_history.clear()
                
            self.conversation_history.clear()
            
        except Exception as e:
            logger.error(f"Memobase 资源清理失败: {e}")
    
    def close(self):
        """兼容性方法，调用 cleanup"""
        self.cleanup()