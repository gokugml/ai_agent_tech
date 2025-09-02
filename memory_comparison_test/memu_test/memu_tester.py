"""
MemU 框架测试器

使用真实的 MemU 记忆框架进行测试
"""

import os
import json
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime

try:
    from memu import MemuClient
except ImportError:
    print("警告: memu-py 未正确安装，将使用模拟模式")
    MemuClient = None

from config import settings
from loguru import logger


class MemuTester:
    """MemU 记忆框架测试器"""
    
    def __init__(self, user_id: str = "test_user"):
        """
        初始化 MemU 测试器
        
        Args:
            user_id: 测试用户ID
        """
        self.user_id = user_id
        self.client = None
        self.fallback_mode = MemuClient is None
        self.conversation_history = []
        self.start_time = None
        
        if not self.fallback_mode:
            self._initialize_client()
        else:
            logger.warning("MemU 库未安装，使用模拟模式")
            self._initialize_fallback()
    
    def _initialize_client(self):
        """初始化真实的 MemU 客户端"""
        try:
            if settings.MEMU_MODE == "cloud":
                self.client = MemuClient(
                    base_url=settings.MEMU_CLOUD_BASE_URL,
                    api_key=settings.memu_api_key
                )
                logger.info("已连接到 MemU 云服务")
            else:
                # 自托管版本：尝试不同的初始化方式
                try:
                    # 先尝试不传 api_key
                    self.client = MemuClient(base_url=settings.MEMU_SELFHOST_URL)
                except Exception as e1:
                    try:
                        # 再尝试传空字符串
                        self.client = MemuClient(
                            base_url=settings.MEMU_SELFHOST_URL, 
                            api_key=None
                        )
                    except Exception as e2:
                        # 最后尝试传默认值
                        self.client = MemuClient(
                            base_url=settings.MEMU_SELFHOST_URL,
                            api_key=settings.MEMU_SELFHOST_API_KEY or "dummy"
                        )
                logger.info(f"已连接到 MemU 自托管服务: {settings.MEMU_SELFHOST_URL}")
                
        except Exception as e:
            logger.error(f"MemU 客户端初始化失败: {e}")
            self.fallback_mode = True
            self._initialize_fallback()
    
    def _initialize_fallback(self):
        """初始化模拟模式"""
        self.memory_store = {}
        self.chat_style = {}
        logger.info("MemU 测试器运行在模拟模式")
        
    def initialize_memory(self) -> bool:
        """
        初始化记忆系统
        
        Returns:
            bool: 初始化是否成功
        """
        try:
            self.start_time = datetime.now()
            
            if not self.fallback_mode and self.client:
                # MemU 自托管版本不需要显式创建用户，直接初始化即可
                # 用户会在第一次 memorize_conversation 时自动创建
                logger.info(f"MemU 客户端已初始化，用户ID: {self.user_id}")
                return True
            else:
                # 模拟模式初始化
                self.memory_store = {
                    "user_profile": {},
                    "chat_style": {},
                    "divination_history": [],
                    "verification_feedback": [],
                    "life_events": [],
                    "preferences": {}
                }
                return True
                
        except Exception as e:
            logger.error(f"MemU 初始化失败: {e}")
            return False
    
    def store_memory(self, memory_type: str, content: Any) -> bool:
        """
        存储记忆内容
        
        Args:
            memory_type: 记忆类型
            content: 记忆内容
            
        Returns:
            bool: 存储是否成功
        """
        try:
            if not self.fallback_mode and self.client:
                # 使用真实 MemU API 存储记忆
                # 将内容格式化为对话文本
                conversation_text = f"[{memory_type}] {content}"
                
                response = self.client.memorize_conversation(
                    conversation=conversation_text,
                    user_id=self.user_id,
                    user_name="TestUser",
                    agent_id="memu_tester",
                    agent_name="MemU Tester"
                )
                logger.debug(f"MemU 记忆存储成功: {memory_type}")
                return True
            else:
                # 模拟模式存储
                timestamp = datetime.now().isoformat()
                
                if memory_type not in self.memory_store:
                    self.memory_store[memory_type] = []
                
                self.memory_store[memory_type].append({
                    "timestamp": timestamp,
                    "content": content,
                    "metadata": {
                        'type': memory_type,
                        'timestamp': datetime.now().isoformat()
                    }
                })
                logger.debug(f"MemU 记忆存储成功: {memory_type}")
                return True
                
        except Exception as e:
            logger.error(f"MemU 存储记忆失败: {e}")
            return False
    
    def retrieve_memory(self, memory_type: str, query: Optional[str] = None) -> Any:
        """
        检索记忆内容
        
        Args:
            memory_type: 记忆类型
            query: 查询关键词
            
        Returns:
            检索到的记忆内容
        """
        try:
            if not self.fallback_mode and self.client:
                # MemU 自托管版本的检索需要使用 HTTP 请求，暂时使用模拟模式
                # 等真实连接建立后再实现具体的检索逻辑
                logger.debug(f"MemU 自托管版本检索记忆: {memory_type}")
                return []
            else:
                # 模拟模式检索
                if memory_type not in self.memory_store:
                    return None
                    
                memories = self.memory_store[memory_type]
                
                if query:
                    # 简单的关键词匹配
                    if isinstance(memories, list):
                        return [m for m in memories if query.lower() in str(m["content"]).lower()]
                    else:
                        return {k: v for k, v in memories.items() if query.lower() in str(v).lower()}
                
                return memories
                
        except Exception as e:
            logger.error(f"MemU 检索记忆失败: {e}")
            return None
    
    def update_chat_style(self, style_indicators: Dict[str, Any]) -> None:
        """
        更新用户聊天风格记忆
        
        Args:
            style_indicators: 风格指标字典
        """
        try:
            if not self.fallback_mode and self.client:
                # 使用真实 MemU API 更新风格偏好
                style_content = {
                    "chat_style_update": style_indicators,
                    "learning_context": "style_adaptation"
                }
                self.store_memory("chat_style", style_content)
            else:
                # 模拟模式更新
                if not hasattr(self, 'chat_style'):
                    self.chat_style = {}
                
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
            logger.error(f"MemU 更新聊天风格失败: {e}")
    
    def get_chat_style(self) -> Dict[str, Any]:
        """
        获取当前学习到的聊天风格
        
        Returns:
            聊天风格字典
        """
        try:
            if not self.fallback_mode and self.client:
                # 从 MemU 检索聊天风格信息
                memories = self.retrieve_memory("chat_style")
                
                # 解析最新的风格偏好
                current_style = {}
                if isinstance(memories, list):
                    for memory in memories:
                        content = memory.get('content', {})
                        if 'chat_style_update' in content:
                            current_style.update(content['chat_style_update'])
                
                return current_style
            else:
                # 模拟模式获取
                return self.memory_store.get("chat_style", {})
                
        except Exception as e:
            logger.error(f"MemU 获取聊天风格失败: {e}")
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
            self.conversation_history.append({
                "timestamp": datetime.now().isoformat(),
                **conversation_data
            })
            
            # 存储到 MemU
            if not self.fallback_mode and self.client:
                self.store_memory("conversation", conversation_data)
            
        except Exception as e:
            logger.error(f"MemU 添加对话轮次失败: {e}")
    
    def extract_divination_info(self, conversation_text: str) -> Dict[str, Any]:
        """
        从对话中提取算命相关信息
        
        Args:
            conversation_text: 对话文本
            
        Returns:
            提取的信息字典
        """
        try:
            if not self.fallback_mode and self.client:
                # 使用真实 MemU 的智能提取功能
                response = self.client.extract_information(
                    user_id=self.user_id,
                    text=conversation_text,
                    extraction_schema=[
                        'life_changes',
                        'time_references',
                        'emotional_states',
                        'verification_feedback'
                    ]
                )
                return response.get('extracted_info', {})
            else:
                # 模拟模式提取
                extracted_info = {
                    "life_changes": [],
                    "time_references": [],
                    "emotional_states": [],
                    "verification_feedback": []
                }
                
                # 关键词匹配提取
                text_lower = conversation_text.lower()
                
                # 生活变化关键词
                life_change_keywords = ["换工作", "搬家", "结婚", "分手", "生病", "买房"]
                for keyword in life_change_keywords:
                    if keyword in text_lower:
                        extracted_info["life_changes"].append(keyword)
                
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
                
                return extracted_info
                
        except Exception as e:
            logger.error(f"MemU 信息提取失败: {e}")
            return {}
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """
        获取记忆统计信息
        
        Returns:
            统计信息字典
        """
        try:
            if not self.fallback_mode and self.client:
                # 从真实 MemU 获取统计信息
                # MemU 自托管版本没有 get_user_stats 方法，使用基础信息
                stats = {"memory_count": len(getattr(self, 'memory_store', {}))}
                return {
                    "framework": "MemU (真实)",
                    "total_conversations": len(self.conversation_history),
                    "total_memories": stats.get('memory_count', 0),
                    "api_calls": stats.get('api_calls', 0),
                    "storage_size_kb": stats.get('storage_size', 0) / 1024,
                    "runtime_seconds": (datetime.now() - self.start_time).total_seconds() if self.start_time else 0
                }
            else:
                # 模拟模式统计
                return {
                    "framework": "MemU (模拟)",
                    "total_conversations": len(self.conversation_history),
                    "memory_types": list(self.memory_store.keys()),
                    "memory_sizes": {k: len(v) if isinstance(v, list) else len(str(v)) 
                                   for k, v in self.memory_store.items()},
                    "runtime_seconds": (datetime.now() - self.start_time).total_seconds() if self.start_time else 0
                }
                
        except Exception as e:
            logger.error(f"MemU 获取统计信息失败: {e}")
            return {"framework": "MemU (错误)", "error": str(e)}
    
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
                "framework": "MemU",
                "fallback_mode": self.fallback_mode,
                "conversation_history": self.conversation_history,
                "stats": self.get_memory_stats(),
                "export_time": datetime.now().isoformat()
            }
            
            # 在模拟模式下包含内存存储
            if self.fallback_mode:
                results["memory_store"] = self.memory_store
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            
            logger.info(f"MemU 测试结果已导出: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"MemU 结果导出失败: {e}")
            return False
    
    def cleanup(self):
        """清理资源"""
        try:
            if not self.fallback_mode and self.client:
                # 清理 MemU 资源（如果需要删除测试数据）
                if not settings.KEEP_TEST_DATA:
                    # MemU 自托管版本没有 delete_user 方法，数据将保留在服务端
                    logger.info(f"MemU 测试数据保留在服务端: {self.user_id}")
            else:
                # 清理模拟数据
                if hasattr(self, 'memory_store'):
                    self.memory_store.clear()
                if hasattr(self, 'chat_style'):
                    self.chat_style.clear()
                
            self.conversation_history.clear()
            
        except Exception as e:
            logger.error(f"MemU 资源清理失败: {e}")