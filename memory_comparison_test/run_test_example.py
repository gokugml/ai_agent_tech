#!/usr/bin/env python3
"""
记忆框架对比测试示例

演示如何使用测试框架进行简单的对比测试
"""

import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    """运行简单的示例测试"""
    print("🧠 记忆框架对比测试示例")
    print("=" * 40)
    
    try:
        # 导入评估工具
        from evaluation_tools.comparison_evaluator import MemoryFrameworkComparator
        
        # 创建对比器
        print("📋 正在初始化测试框架...")
        comparator = MemoryFrameworkComparator("example_user")
        
        # 初始化测试器
        if not comparator.initialize_testers():
            print("❌ 初始化失败")
            return
        
        print("✅ 初始化成功！")
        
        # 运行简单的风格学习测试
        print("\n🎯 运行聊天风格学习测试...")
        style_result = comparator.run_style_learning_test("concise_preference")
        
        if "error" not in style_result:
            print("✅ 风格学习测试完成")
            
            # 显示简要结果
            comparison = style_result.get("comparison", {})
            overall_comparison = comparison.get("overall", {})
            
            if overall_comparison:
                winner = overall_comparison.get("winner", "未知")
                memu_score = overall_comparison.get("memu", 0)
                memobase_score = overall_comparison.get("memobase", 0)
                
                print(f"\n📊 测试结果:")
                print(f"   Memu 得分: {memu_score:.3f}")
                print(f"   Memobase 得分: {memobase_score:.3f}")
                print(f"   获胜者: {winner}")
        else:
            print(f"❌ 测试失败: {style_result['error']}")
        
        # 运行信息提取测试
        print("\n🔍 运行信息提取测试...")
        extraction_result = comparator.run_info_extraction_test("life_changes_extraction")
        
        if "error" not in extraction_result:
            print("✅ 信息提取测试完成")
            
            # 显示提取示例
            memu_extractions = extraction_result.get("memu_results", {}).get("extractions", [])
            if memu_extractions:
                print(f"\n📝 Memu 提取示例:")
                first_extraction = memu_extractions[0]
                for category, items in first_extraction.items():
                    if items:
                        print(f"   {category}: {len(items)}项")
        else:
            print(f"❌ 测试失败: {extraction_result['error']}")
        
        print(f"\n💡 提示:")
        print(f"   运行完整测试: cd evaluation_tools && python run_comparison.py")
        print(f"   查看详细文档: 阅读 README.md")
        
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("请确保所有必要的文件都已创建")
    except Exception as e:
        print(f"❌ 运行错误: {e}")
    finally:
        # 清理资源
        try:
            comparator.cleanup()
        except:
            pass

if __name__ == "__main__":
    main()