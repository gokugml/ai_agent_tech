"""
Memobase 记忆框架适配器

基于现有测试代码创建的 Memobase 集成适配器
"""

import time
from typing import Any

from config import settings
from loguru import logger


class MemobaseMemoryAdapter:
    """Memobase 记忆框架适配器"""

    def __init__(self):
        self.client = None
        self._initialize_client()

    def _initialize_client(self) -> None:
        """初始化 Memobase 客户端"""
        try:
            # 尝试导入 Memobase
            from memobase import Memobase

            # 验证必要的配置参数
            if not settings.MEMOBASE_PROJECT_URL:
                raise ValueError("Memobase 配置不完整，缺少 PROJECT_URL")

            self.client = Memobase(
                project_url=settings.MEMOBASE_PROJECT_URL, api_key=settings.MEMOBASE_API_KEY
            )
            logger.info("Memobase 客户端初始化成功")

        except ImportError as e:
            logger.error(f"Memobase 库未安装: {e}")
            raise ImportError(f"Memobase 库不可用: {e}") from e
        except Exception as e:
            logger.error(f"Memobase 客户端初始化失败: {e}")
            raise

    async def store_conversation(self, session_id: str, user_input: str, ai_response: str) -> bool:
        """存储对话到 Memobase

        Args:
            session_id: 会话ID（作为user_id）
            user_input: 用户输入
            ai_response: AI回复

        Returns:
            存储是否成功
        """
        try:
            return await self._store_real_conversation(session_id, user_input, ai_response)
        except Exception as e:
            logger.error(f"Memobase 存储对话失败: {e}")
            return False

    async def _store_real_conversation(self, session_id: str, user_input: str, ai_response: str) -> bool:
        """存储到真实 Memobase 服务"""
        try:
            from memobase import ChatBlob

            # 创建 ChatBlob
            chat_blob = ChatBlob(
                messages=[{"role": "user", "content": user_input}, {"role": "assistant", "content": ai_response}]
            )

            # 获取用户并插入
            user = self.client.get_or_create_user(session_id)
            blob_id = user.insert(chat_blob)

            logger.info(f"Memobase 存储成功，Blob ID: {blob_id}")
            return True

        except Exception as e:
            logger.error(f"Memobase 真实存储失败: {e}")
            return False


    async def retrieve_memories(self, session_id: str, query: str, limit: int = 5) -> list[dict[str, Any]]:
        """检索相关记忆

        Args:
            session_id: 会话ID
            query: 查询内容
            limit: 返回数量限制

        Returns:
            相关记忆列表
        """
        try:
            return await self._retrieve_real_memories(session_id, query, limit)
        except Exception as e:
            logger.error(f"Memobase 检索记忆失败: {e}")
            return []

    async def _retrieve_real_memories(self, session_id: str, query: str, limit: int) -> list[dict[str, Any]]:
        """从真实 Memobase 检索记忆"""
        try:
            # 使用 Memobase 的搜索功能
            user = self.client.get_user(session_id)
            results = user.search_memories(query=query, limit=limit)

            memories = []
            for result in results:
                memory = {
                    "id": result.get("id", ""),
                    "content": result.get("content", ""),
                    "type": result.get("type", "chat_blob"),
                    "timestamp": result.get("timestamp", ""),
                    "relevance_score": result.get("score", 0.0),
                    "metadata": result.get("metadata", {}),
                    "messages": result.get("messages", []),
                }
                memories.append(memory)

            logger.debug(f"Memobase 真实检索: {session_id}, 结果数: {len(memories)}")
            return memories

        except Exception as e:
            logger.error(f"Memobase 真实检索失败: {e}")
            return []


    def format_memories_for_prompt(self, memories: list[dict[str, Any]]) -> str:
        """将记忆格式化为提示文本

        Args:
            memories: 记忆列表

        Returns:
            格式化的记忆文本
        """
        if not memories:
            return "暂无相关历史记忆。"

        formatted_parts = []
        for i, memory in enumerate(memories, 1):
            timestamp = memory.get("timestamp", 0)

            if isinstance(timestamp, int | float):
                time_str = time.strftime("%Y-%m-%d %H:%M", time.localtime(timestamp))
            else:
                time_str = str(timestamp)

            # 处理 messages 格式
            messages = memory.get("messages", [])
            if messages:
                conversation_text = ""
                for msg in messages:
                    role = msg.get("role", "unknown")
                    content = msg.get("content", "")
                    if role == "user":
                        conversation_text += f"用户: {content}\\n"
                    elif role == "assistant":
                        conversation_text += f"助手: {content}\\n"

                formatted_parts.append(f"{i}. 历史对话 ({time_str}):\\n{conversation_text.strip()}")
            else:
                # 回退到 content 格式
                content = memory.get("content", "")
                formatted_parts.append(f"{i}. 历史记录 ({time_str}):\\n{content}")

        return "\\n\\n".join(formatted_parts)
