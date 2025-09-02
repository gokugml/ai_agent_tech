#!/usr/bin/env python3
"""
记忆框架集成测试

测试真实的 MemU 和 Memobase 框架是否可以正常工作
"""

import os
from loguru import logger
from config import settings

def test_memu():
    """测试 MemU 框架"""
    logger.info("🧠 测试 MemU 框架...")
    
    try:
        from memu_test.memu_tester import MemuTester
        
        # 创建测试器
        tester = MemuTester("test_user_memu")
        
        # 初始化
        success = tester.initialize_memory()
        
        if success:
            logger.success("✅ MemU 测试器初始化成功")
            
            # 测试基本功能
            test_content = {"test": "Hello MemU", "type": "greeting"}
            store_success = tester.store_memory("test_memory", test_content)
            
            if store_success:
                logger.success("✅ MemU 记忆存储成功")
            else:
                logger.warning("⚠️ MemU 记忆存储失败")
            
            # 获取统计信息
            stats = tester.get_memory_stats()
            logger.info(f"📊 MemU 统计信息: {stats}")
            
            # 清理
            tester.cleanup()
            
        else:
            logger.error("❌ MemU 测试器初始化失败")
            
    except Exception as e:
        logger.error(f"❌ MemU 测试出错: {e}")

def test_memobase():
    """测试 Memobase 框架"""
    logger.info("🗄️ 测试 Memobase 框架...")
    
    try:
        from memobase_test.memobase_tester import MemobaseTester
        
        # 创建测试器
        tester = MemobaseTester("test_user_memobase")
        
        # 初始化
        success = tester.initialize_memory()
        
        if success:
            logger.success("✅ Memobase 测试器初始化成功")
            
            # 测试基本功能 - 使用字符串内容让其自动转换为消息格式
            test_content = "Hello Memobase, this is a test memory."
            store_success = tester.store_memory("test_memory", test_content)
            
            if store_success:
                logger.success("✅ Memobase 记忆存储成功")
            else:
                logger.warning("⚠️ Memobase 记忆存储失败")
            
            # 获取统计信息
            stats = tester.get_memory_stats()
            logger.info(f"📊 Memobase 统计信息: {stats}")
            
            # 清理
            tester.cleanup()
            
        else:
            logger.error("❌ Memobase 测试器初始化失败")
            
    except Exception as e:
        logger.error(f"❌ Memobase 测试出错: {e}")

def main():
    """主测试函数"""
    logger.info("🚀 开始记忆框架集成测试")
    logger.info("=" * 50)
    
    # 显示配置信息
    logger.info(f"MemU 模式: {settings.MEMU_MODE}")
    logger.info(f"Memobase 模式: {settings.MEMOBASE_MODE}")
    logger.info("")
    
    # 测试两个框架
    test_memu()
    logger.info("")
    test_memobase()
    
    logger.info("")
    logger.info("=" * 50)
    logger.success("🎉 记忆框架集成测试完成")

if __name__ == "__main__":
    main()