"""
MemU 记忆框架适配器

基于现有测试代码创建的 MemU 集成适配器
"""

import time
from typing import Any

from config import settings
from loguru import logger


class MemuMemoryAdapter:
    """MemU 记忆框架适配器"""

    def __init__(self):
        self.client = None
        self._initialize_client()

    def _initialize_client(self) -> None:
        """初始化 MemU 客户端"""
        try:
            # 尝试导入 MemU
            from memu import MemuClient

            # 验证必要的配置参数
            if not settings.MEMU_BASE_URL or not settings.MEMU_API_KEY:
                raise ValueError("MemU 配置不完整，缺少 BASE_URL 或 API_KEY")

            self.client = MemuClient(base_url=settings.MEMU_BASE_URL, api_key=settings.MEMU_API_KEY)

            # 测试连接（如果支持）
            if hasattr(self.client, "health_check") or hasattr(self.client, "ping"):
                try:
                    if hasattr(self.client, "health_check"):
                        self.client.health_check()
                    elif hasattr(self.client, "ping"):
                        self.client.ping()
                    logger.info("MemU 客户端初始化成功并通过连接测试")
                except Exception as health_error:
                    logger.warning(f"MemU 连接测试失败，但客户端初始化成功: {health_error}")
            else:
                logger.info("MemU 客户端初始化成功")

        except ImportError as e:
            logger.error(f"MemU 库未安装: {e}")
            raise ImportError(f"MemU 库不可用: {e}") from e
        except Exception as e:
            logger.error(f"MemU 客户端初始化失败: {e.__class__.__name__}: {e}")
            raise

    async def store_conversation(self, session_id: str, user_input: str, ai_response: str) -> bool:
        """存储对话到 MemU

        Args:
            session_id: 会话ID（作为user_id）
            user_input: 用户输入
            ai_response: AI回复

        Returns:
            存储是否成功
        """
        try:
            return self._store_real_conversation(session_id, user_input, ai_response)
        except Exception as e:
            logger.error(f"MemU 存储对话失败: {e}")
            return False

    def _store_real_conversation(self, session_id: str, user_input: str, ai_response: str) -> bool:
        """存储到真实 MemU 服务"""
        try:
            # 根据 MemU 最佳实践，使用结构化的对话格式
            conversation_data = {
                "messages": [
                    {"role": "user", "content": user_input, "timestamp": int(time.time())},
                    {"role": "assistant", "content": ai_response, "timestamp": int(time.time())},
                ],
                "context": {
                    "domain": "fortune_telling",
                    "session_type": "consultation",
                    "topics": self._extract_topics_advanced(user_input),
                    "sentiment": self._analyze_sentiment(user_input),
                    "response_type": self._classify_response_type(ai_response),
                },
                "metadata": {
                    "framework": "memu",
                    "session_id": session_id,
                    "timestamp": int(time.time()),
                    "language": "zh-CN",
                },
            }

            # 先尝试新的 API 格式，如果失败则回退到原格式
            try:
                # 新的结构化 API
                memo_response = self.client.memorize_structured_conversation(
                    conversation_data=conversation_data,
                    user_id=session_id,
                    user_name=settings.MEMU_USER_NAME,
                    agent_id=settings.MEMU_AGENT_ID,
                    agent_name=settings.MEMU_AGENT_NAME,
                )
            except (AttributeError, TypeError):
                # 回退到原有的简单格式
                conversation = f"user: {user_input}\n\nassistant: {ai_response}"
                memo_response = self.client.memorize_conversation(
                    conversation=conversation,
                    user_id=session_id,
                    user_name=settings.MEMU_USER_NAME,
                    agent_id=settings.MEMU_AGENT_ID,
                    agent_name=settings.MEMU_AGENT_NAME,
                )

            # 处理响应结果
            if hasattr(memo_response, "task_id"):
                logger.info(f"MemU 存储成功，Task ID: {memo_response.task_id}")
            elif hasattr(memo_response, "id"):
                logger.info(f"MemU 存储成功，Memory ID: {memo_response.id}")
            else:
                logger.info(f"MemU 存储成功，响应: {memo_response}")
            return True

        except AttributeError as e:
            logger.error(f"MemU API接口变更或客户端问题: {e}")
            logger.info("尝试重新初始化客户端...")
            self._initialize_client()
            return False
        except ConnectionError as e:
            logger.error(f"MemU 连接错误: {e}")
            return False
        except TimeoutError as e:
            logger.error(f"MemU 请求超时: {e}")
            return False
        except ValueError as e:
            logger.error(f"MemU 参数错误: {e}")
            return False
        except Exception as e:
            logger.error(f"MemU 真实存储失败: {e.__class__.__name__}: {e}")
            return False

    def retrieve_default_categories(self) -> str:
        """获取默认分类 - 用于系统初始化

        根据MemU官方文档，这是最基础且高度推荐的方法
        延迟：~50ms
        """
        try:
            return self.client.retrieve_default_categories()
        except Exception as e:
            logger.error(f"MemU 获取默认分类失败: {e}")
            return ""

    def retrieve_related_clustered_categories(self, category_query: str) -> str:
        """语义聚类检索

        根据MemU官方文档，用于高级语义搜索
        延迟：~200ms

        Args:
            category_query: 分类查询内容
        """
        try:
            return self.client.retrieve_related_clustered_categories(category_query)
        except Exception as e:
            logger.error(f"MemU 语义聚类检索失败: {e}")
            return ""

    def retrieve_related_memory_items(self, query: str, include_categories: list[str] = None) -> str:
        """上下文相关检索

        根据MemU官方文档，用于检索与当前上下文或查询相关的具体记忆项
        延迟：~200ms

        Args:
            query: 查询内容
            include_categories: 可选的包含分类列表
        """
        try:
            return self.client.retrieve_related_memory_items(query, include_categories)
        except Exception as e:
            logger.error(f"MemU 上下文相关检索失败: {e}")
            return ""

    async def retrieve_memories(self, session_id: str, query: str, limit: int = 5) -> list[dict[str, Any]]:
        """检索相关记忆 - 兼容性方法

        Args:
            session_id: 会话ID（在新API中不需要，仅用于日志记录）
            query: 查询内容
            limit: 返回数量限制（在新API中不支持，仅用于日志记录）

        Returns:
            格式化的记忆列表
        """
        try:
            # 记录参数信息
            logger.debug(f"MemU检索请求: session_id={session_id}, limit={limit}")

            # 使用新的MemU API进行检索
            memory_content = self.retrieve_related_memory_items(query)

            # 将字符串结果转换为兼容的格式
            if memory_content:
                return [
                    {
                        "id": f"memu_memory_{int(time.time())}",
                        "content": memory_content,
                        "type": "memory_items",
                        "timestamp": int(time.time()),
                        "relevance_score": 0.8,  # 默认相关性评分
                        "metadata": {"source": "memu_api", "query": query},
                    }
                ]
            return []
        except Exception as e:
            logger.error(f"MemU 检索记忆失败: {e}")
            return []

    # 移除了错误的API实现方法 _retrieve_real_memories
    # 现在使用官方文档中的正确API方法

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
            memory_type = memory.get("type", "unknown")
            content = memory.get("content", "")
            timestamp = memory.get("timestamp", 0)
            relevance_score = memory.get("relevance_score", 0)
            context = memory.get("context", {})

            if isinstance(timestamp, int | float):
                time_str = time.strftime("%Y-%m-%d %H:%M", time.localtime(timestamp))
            else:
                time_str = str(timestamp)

            # 根据 MemU 最佳实践，提供更丰富的上下文信息
            relevance_indicator = ""
            if relevance_score > 0.7:
                relevance_indicator = " [高度相关]"
            elif relevance_score > 0.4:
                relevance_indicator = " [相关]"

            # 添加上下文信息
            context_info = ""
            if context:
                topics = context.get("topics", [])
                if topics:
                    context_info = f" - 话题: {', '.join(topics)}"

                sentiment = context.get("sentiment")
                if sentiment:
                    context_info += f" - 情感: {sentiment}"

            if memory_type == "conversation":
                formatted_parts.append(f"{i}. 历史对话{relevance_indicator} ({time_str}){context_info}:\n{content}")
            elif memory_type == "analysis":
                formatted_parts.append(f"{i}. 对话分析{relevance_indicator} ({time_str}){context_info}:\n{content}")
            else:
                formatted_parts.append(f"{i}. 记忆{relevance_indicator} ({time_str}){context_info}:\n{content}")

        return "\n\n".join(formatted_parts)

    def _extract_topics_advanced(self, text: str) -> list[str]:
        """高级话题提取，根据 MemU 最佳实践优化"""
        topics = []
        topic_mapping = {
            "事业": ["事业", "工作", "职业", "升職", "转行", "创业"],
            "感情": ["感情", "恋爱", "婚姻", "伴侣", "结婚", "离婚"],
            "财运": ["财运", "财富", "投资", "理财", "赚钱", "收入"],
            "健康": ["健康", "病痛", "身体", "调理", "养生"],
            "学业": ["学业", "考试", "读书", "学习", "教育"],
            "家庭": ["家庭", "父母", "子女", "亲情", "家人"],
        }

        for topic, keywords in topic_mapping.items():
            if any(keyword in text for keyword in keywords):
                topics.append(topic)

        return topics if topics else ["一般咨询"]

    def _analyze_sentiment(self, text: str) -> str:
        """简单的情感分析"""
        positive_words = ["开心", "高兴", "好", "不错", "顺利", "满意"]
        negative_words = ["烦恼", "焦虑", "难过", "失望", "困难", "不顺"]

        if any(word in text for word in positive_words):
            return "积极"
        elif any(word in text for word in negative_words):
            return "消极"
        else:
            return "中性"

    def _classify_response_type(self, text: str) -> str:
        """分类回复类型，根据 MemU 最佳实践优化"""
        if "建议" in text or "应该" in text or "可以" in text:
            return "实用建议"
        elif "分析" in text or "从命理" in text or "八字" in text:
            return "命理分析"
        elif "预测" in text or "运势" in text or "将来" in text:
            return "运势预测"
        elif "注意" in text or "小心" in text or "警惕" in text:
            return "提醒警示"
        elif "解释" in text or "意思" in text:
            return "解答说明"
        else:
            return "一般指导"
