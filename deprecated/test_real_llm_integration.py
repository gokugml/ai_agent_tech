# 真正调用LLM的集成测试
# 验证端到端的动态工具选择功能

import sys
import os
import time

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dynamic_agent import DynamicToolAgent
from tool_selector import AdvancedToolSelector  
from tools import tool_registry
from user_config import settings

def test_llm_integration():
    """测试真正的LLM集成功能"""
    print("🚀 开始LLM集成测试")
    print("=" * 60)
    
    # 检查API密钥
    if not hasattr(settings, 'GOOGLE_API_KEY') or not settings.GOOGLE_API_KEY:
        print("❌ 未配置GOOGLE_API_KEY，无法进行LLM测试")
        return False
    
    print(f"✅ API密钥已配置: {str(settings.GOOGLE_API_KEY)[:20]}...")
    
    # 初始化代理
    agent = DynamicToolAgent()
    
    print("\n📋 测试用例:")
    
    test_cases = [
        {
            "name": "金融查询",
            "query": "帮我查询苹果公司最新的股价信息",
            "expected_categories": ["finance", "web"],
            "timeout": 30
        },
        {
            "name": "网络搜索",
            "query": "搜索关于Claude AI最新发展的新闻",
            "expected_categories": ["web"],
            "timeout": 30
        },
        {
            "name": "数据分析",
            "query": "分析销售数据并生成报告",
            "conversation_state": {"has_data": True},
            "expected_categories": ["code", "file"],
            "timeout": 30
        },
        {
            "name": "邮件发送",
            "query": "将分析结果发送邮件给团队",
            "conversation_state": {"has_data": True},
            "expected_categories": ["email", "code"],
            "timeout": 30
        }
    ]
    
    success_count = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- 测试 {i}: {test_case['name']} ---")
        print(f"查询: {test_case['query']}")
        
        start_time = time.time()
        
        try:
            # 调用代理（真正的LLM调用）
            result = agent.invoke(
                user_query=test_case["query"],
                conversation_state=test_case.get("conversation_state", {}),
                max_iterations=2
            )
            
            elapsed_time = time.time() - start_time
            
            print(f"⏱️  响应时间: {elapsed_time:.2f}秒")
            print(f"🔧 选择的工具类别: {result['tool_categories_used']}")
            print(f"📊 选择置信度: {result['selection_confidence']:.2f}")
            print(f"🔄 迭代次数: {result['iterations']}")
            print(f"🛠️  工具调用次数: {len(result['tool_results'])}")
            
            # 显示响应内容（前200字符）
            response_preview = result['response'][:200].replace('\n', ' ')
            print(f"💬 响应预览: {response_preview}...")
            
            # 验证工具选择是否合理
            expected = test_case.get("expected_categories", [])
            actual = result["tool_categories_used"]
            
            if expected:
                overlap = set(expected) & set(actual)
                match_rate = len(overlap) / len(expected) if expected else 1.0
                print(f"🎯 类别匹配度: {match_rate:.2f} ({len(overlap)}/{len(expected)})")
                
                if match_rate >= 0.5:
                    print("✅ 工具选择合理")
                    success_count += 1
                else:
                    print("⚠️  工具选择可能不够理想")
            else:
                if actual:
                    print("✅ 成功选择了工具类别")
                    success_count += 1
                else:
                    print("⚠️  未选择任何工具类别")
            
            # 检查是否有实际的工具调用
            if result['tool_results']:
                print("✅ 成功执行了工具调用")
                for tool_result in result['tool_results'][:3]:  # 显示前3个
                    print(f"   🔧 {tool_result['tool_name']}: {str(tool_result['result'])[:100]}...")
            else:
                print("ℹ️  无工具调用（可能是直接回答）")
            
            print(f"✅ 测试 {i} 完成")
            
        except Exception as e:
            elapsed_time = time.time() - start_time
            print(f"❌ 测试 {i} 失败: {str(e)}")
            print(f"⏱️  错误发生时间: {elapsed_time:.2f}秒")
            
            # 打印详细错误信息（用于调试）
            import traceback
            print("📋 详细错误信息:")
            traceback.print_exc()
    
    print(f"\n📊 测试总结:")
    print(f"成功: {success_count}/{len(test_cases)}")
    print(f"成功率: {success_count/len(test_cases)*100:.1f}%")
    
    return success_count == len(test_cases)

def test_tool_selector_with_llm():
    """单独测试工具选择器的LLM功能"""
    print("\n🧠 测试工具选择器LLM功能")
    print("=" * 60)
    
    if not hasattr(settings, 'GOOGLE_API_KEY') or not settings.GOOGLE_API_KEY:
        print("❌ 未配置GOOGLE_API_KEY，跳过LLM选择器测试")
        return False
    
    selector = AdvancedToolSelector(tool_registry)
    
    test_queries = [
        "查询特斯拉股票价格并保存到文件",
        "搜索AI新闻然后发送邮件总结",
        "分析图片中的数据并生成代码",
        "执行Python脚本并将结果存入数据库"
    ]
    
    for query in test_queries:
        print(f"\n查询: {query}")
        
        try:
            # 测试不同的选择方法
            methods = ["keywords", "llm", "hybrid"]
            
            for method in methods:
                start_time = time.time()
                
                tools, categories, confidence = selector.select_tools(
                    query=query,
                    method=method,
                    max_categories=3
                )
                
                elapsed_time = time.time() - start_time
                
                print(f"  {method:8}: {categories} (置信度: {confidence:.2f}, 用时: {elapsed_time:.2f}s)")
        
        except Exception as e:
            print(f"  错误: {str(e)}")
    
    print("✅ 工具选择器LLM测试完成")
    return True

def test_workflow_robustness():
    """测试工作流的健壮性"""
    print("\n🛡️  测试工作流健壮性")
    print("=" * 60)
    
    agent = DynamicToolAgent()
    
    # 测试边界情况
    edge_cases = [
        {
            "name": "空查询",
            "query": "",
            "should_handle": True
        },
        {
            "name": "无意义查询",
            "query": "asdfjkl qwerty zxcvbn",
            "should_handle": True
        },
        {
            "name": "超长查询",
            "query": "这是一个非常长的查询 " * 100,
            "should_handle": True
        },
        {
            "name": "混合语言",
            "query": "search for 股票 price and send email to team",
            "should_handle": True
        },
        {
            "name": "特殊字符",
            "query": "@#$%^&*() search stock price!!! ???",
            "should_handle": True
        }
    ]
    
    robust_count = 0
    
    for case in edge_cases:
        print(f"\n测试: {case['name']}")
        print(f"查询: {case['query'][:50]}...")
        
        try:
            result = agent.invoke(
                user_query=case["query"],
                max_iterations=1  # 减少迭代以加快测试
            )
            
            # 检查是否有合理的响应
            has_response = len(result['response']) > 0
            has_categories = len(result['tool_categories_used']) > 0
            
            print(f"  有响应: {'✅' if has_response else '❌'}")
            print(f"  有工具选择: {'✅' if has_categories else '❌'}")
            print(f"  置信度: {result['selection_confidence']:.2f}")
            
            if has_response:
                robust_count += 1
                print("  状态: ✅ 健壮")
            else:
                print("  状态: ❌ 不够健壮")
                
        except Exception as e:
            print(f"  错误: {str(e)}")
            print("  状态: ❌ 异常")
    
    print(f"\n健壮性测试结果: {robust_count}/{len(edge_cases)}")
    return robust_count >= len(edge_cases) * 0.8  # 80%通过率

def run_complete_integration_test():
    """运行完整的集成测试"""
    print("🔥 开始完整LLM集成测试")
    print("=" * 80)
    
    # 检查环境
    print("🔍 检查测试环境...")
    
    if not hasattr(settings, 'GOOGLE_API_KEY'):
        print("❌ 未找到user_config.settings.GOOGLE_API_KEY")
        print("请确保在user_config.py中配置了GOOGLE_API_KEY")
        return False
    
    if not settings.GOOGLE_API_KEY:
        print("❌ GOOGLE_API_KEY为空")
        print("请在user_config.py中设置有效的API密钥")
        return False
    
    print("✅ 环境检查通过")
    
    # 运行各项测试
    results = []
    
    try:
        # 1. 工具选择器LLM测试
        print("\n" + "="*80)
        result1 = test_tool_selector_with_llm()
        results.append(("工具选择器LLM", result1))
        
        # 2. 完整代理集成测试
        print("\n" + "="*80)  
        result2 = test_llm_integration()
        results.append(("代理LLM集成", result2))
        
        # 3. 健壮性测试
        print("\n" + "="*80)
        result3 = test_workflow_robustness()
        results.append(("工作流健壮性", result3))
        
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    # 输出最终结果
    print("\n" + "="*80)
    print("🏁 集成测试完成")
    print("="*80)
    
    all_passed = True
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\n🎉 所有LLM集成测试通过！")
        print("✅ 动态工具选择系统完全可用")
    else:
        print("\n⚠️  部分测试失败")
        print("请检查错误信息并修复问题")
    
    return all_passed

if __name__ == "__main__":
    success = run_complete_integration_test()
    exit(0 if success else 1)