#!/usr/bin/env python3
"""
MemU 适配器修复验证测试
测试修复后的 MemU 记忆检索和存储功能
"""

import asyncio
import sys
import os
import time
from typing import Dict, Any

# 添加项目路径以便导入
sys.path.insert(0, '/home/colsrch/programs/PixClip/ai_agent_tech/fortunetelling_memory_test')

from loguru import logger
from memory.memu_adapter import MemuMemoryAdapter


class MockMemuClient:
    """模拟 MemU 客户端用于测试"""
    
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key
        logger.info(f"Mock MemU 客户端初始化: {base_url}")
    
    def memorize_conversation(self, conversation: str, user_id: str, **kwargs) -> object:
        """模拟记忆存储"""
        logger.info(f"Mock 存储对话: user_id={user_id}")
        logger.debug(f"对话内容: {conversation[:100]}...")
        
        # 模拟返回对象
        class MockResponse:
            def __init__(self):
                self.task_id = f"mock_task_{int(time.time())}"
                self.id = f"mock_memory_{int(time.time())}"
        
        return MockResponse()
    
    def retrieve_memories(self, user_id: str, query: str, limit: int = 5) -> list:
        """模拟记忆检索"""
        logger.info(f"Mock 检索记忆: user_id={user_id}, query={query[:50]}...")
        
        # 模拟返回结果
        return [
            {
                "memory_id": f"mock_mem_1_{int(time.time())}",
                "content": f"模拟记忆内容，与查询 '{query}' 相关",
                "memory_type": "conversation",
                "created_at": "2025-08-26T14:00:00Z",
                "relevance_score": 0.85,
                "metadata": {"source": "mock", "test": True}
            },
            {
                "id": f"mock_mem_2_{int(time.time())}",
                "text": f"另一个模拟记忆，包含关键词：{query.split()[0] if query.split() else 'test'}",
                "type": "analysis", 
                "timestamp": int(time.time()),
                "score": 0.75,
                "metadata": {"source": "mock", "test": True}
            }
        ]


def test_adapter_initialization():
    """测试适配器初始化"""
    logger.info("🧪 测试适配器初始化...")
    
    # 测试模拟模式初始化
    adapter = MemuMemoryAdapter()
    assert adapter.use_simulation == True, "应该默认使用模拟模式"
    assert adapter.client is None, "模拟模式下客户端应为 None"
    
    logger.success("✅ 适配器初始化测试通过")


def test_mock_client_injection():
    """测试注入模拟客户端"""
    logger.info("🧪 测试模拟客户端注入...")
    
    adapter = MemuMemoryAdapter()
    
    # 注入模拟客户端进行测试
    adapter.client = MockMemuClient("http://mock.memu.test", "mock_api_key")
    adapter.use_simulation = False
    
    logger.success("✅ 模拟客户端注入成功")
    return adapter


async def test_memory_storage(adapter: MemuMemoryAdapter):
    """测试记忆存储功能"""
    logger.info("🧪 测试记忆存储功能...")
    
    session_id = "test_session_001"
    user_input = "我最近工作压力很大，想算算我的事业运势"
    ai_response = "根据你的八字分析，你目前正处于事业发展的关键期..."
    
    # 测试存储
    result = await adapter.store_conversation(session_id, user_input, ai_response)
    
    assert result == True, "存储应该成功"
    logger.success("✅ 记忆存储测试通过")


async def test_memory_retrieval(adapter: MemuMemoryAdapter):
    """测试记忆检索功能"""
    logger.info("🧪 测试记忆检索功能...")
    
    session_id = "test_session_001"
    query = "事业运势"
    
    # 测试检索
    memories = await adapter.retrieve_memories(session_id, query, limit=3)
    
    assert isinstance(memories, list), "应该返回列表"
    assert len(memories) > 0, "应该返回一些记忆"
    
    # 验证记忆格式
    for memory in memories:
        assert "id" in memory, "记忆应该有 id 字段"
        assert "content" in memory, "记忆应该有 content 字段"
        assert "type" in memory, "记忆应该有 type 字段"
        
    logger.success(f"✅ 记忆检索测试通过，检索到 {len(memories)} 条记忆")


async def test_simulated_mode():
    """测试模拟模式功能"""
    logger.info("🧪 测试模拟模式功能...")
    
    adapter = MemuMemoryAdapter()
    session_id = "sim_test_001"
    
    # 存储几条对话
    conversations = [
        ("你好，我想算算我的财运", "根据你的生辰八字，你今年财运不错..."),
        ("那我的感情运势呢？", "感情方面需要注意..."),
        ("我应该投资吗？", "从命理角度看，现在不是投资的好时机...")
    ]
    
    for user_msg, ai_msg in conversations:
        result = await adapter.store_conversation(session_id, user_msg, ai_msg)
        assert result == True, "模拟存储应该成功"
    
    # 检索相关记忆
    memories = await adapter.retrieve_memories(session_id, "财运投资", limit=5)
    assert len(memories) > 0, "应该检索到相关记忆"
    
    # 测试记忆格式化
    formatted = adapter.format_memories_for_prompt(memories)
    assert isinstance(formatted, str), "格式化结果应该是字符串"
    assert len(formatted) > 0, "格式化结果不应为空"
    
    logger.success("✅ 模拟模式测试通过")


async def test_error_handling():
    """测试错误处理"""
    logger.info("🧪 测试错误处理...")
    
    adapter = MemuMemoryAdapter()
    
    # 测试无效的模拟客户端
    class BrokenClient:
        def memorize_conversation(self, **kwargs):
            raise AttributeError("测试异常：API 接口变更")
        
        def retrieve_memories(self, **kwargs):
            raise ConnectionError("测试异常：连接失败")
    
    adapter.client = BrokenClient()
    adapter.use_simulation = False
    
    # 测试存储错误处理（应该回退到模拟模式）
    result = await adapter.store_conversation("test", "hello", "world")
    assert result == True, "错误处理后应该成功存储到模拟模式"
    
    # 测试检索错误处理（应该回退到模拟模式）
    memories = await adapter.retrieve_memories("test", "hello", 3)
    assert isinstance(memories, list), "错误处理后应该返回模拟结果"
    
    logger.success("✅ 错误处理测试通过")


async def run_all_tests():
    """运行所有测试"""
    logger.info("🚀 开始 MemU 适配器修复验证测试...")
    
    try:
        # 基础测试
        test_adapter_initialization()
        
        # 模拟客户端测试
        mock_adapter = test_mock_client_injection()
        await test_memory_storage(mock_adapter)
        await test_memory_retrieval(mock_adapter)
        
        # 模拟模式测试
        await test_simulated_mode()
        
        # 错误处理测试
        await test_error_handling()
        
        logger.success("🎉 所有测试通过！MemU 适配器修复验证成功")
        return True
        
    except Exception as e:
        logger.error(f"❌ 测试失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


if __name__ == "__main__":
    # 配置日志
    logger.remove()
    logger.add(sys.stdout, level="INFO", format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}")
    
    # 运行测试
    success = asyncio.run(run_all_tests())
    
    if success:
        print("\n✅ MemU 适配器修复验证测试全部通过")
        sys.exit(0)
    else:
        print("\n❌ 部分测试失败，请检查修复效果")
        sys.exit(1)