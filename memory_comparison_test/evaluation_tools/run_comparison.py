#!/usr/bin/env python3
"""
记忆框架对比测试运行脚本

使用此脚本运行完整的 memu vs memobase 对比测试
"""

import os
import sys
from datetime import datetime

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from evaluation_tools.comparison_evaluator import MemoryFrameworkComparator

def main():
    """主函数：运行完整的对比测试"""
    print("=" * 60)
    print("🧠 记忆框架对比测试系统")
    print("🔄 Memu vs Memobase 全面评估")
    print("=" * 60)
    
    # 创建对比评估器
    comparator = MemoryFrameworkComparator("test_user_2024")
    
    try:
        # 运行综合对比测试
        results = comparator.run_comprehensive_comparison()
        
        if "error" in results:
            print(f"❌ 测试失败: {results['error']}")
            return
        
        # 生成报告文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_dir = "../comparison_results"
        os.makedirs(results_dir, exist_ok=True)
        
        # 导出详细结果
        detailed_file = os.path.join(results_dir, f"detailed_comparison_{timestamp}.json")
        comparator.export_results(results, detailed_file)
        
        # 生成简要报告
        generate_summary_report(results, results_dir, timestamp)
        
        # 显示关键结果
        display_key_results(results)
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 清理资源
        comparator.cleanup()

def generate_summary_report(results: dict, results_dir: str, timestamp: str):
    """生成简要报告"""
    summary_file = os.path.join(results_dir, f"summary_report_{timestamp}.md")
    
    overall_comparison = results.get("overall_comparison", {})
    performance_metrics = results.get("performance_metrics", {})
    
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("# 记忆框架对比测试报告\n\n")
        f.write(f"**测试时间**: {results.get('test_info', {}).get('start_time', 'Unknown')}\n")
        f.write(f"**测试用户**: {results.get('test_info', {}).get('user_id', 'Unknown')}\n\n")
        
        f.write("## 总体结果\n\n")
        winner = overall_comparison.get("overall_winner", "未知")
        f.write(f"**总体获胜者**: {winner}\n\n")
        
        f.write("### 各类别获胜情况\n\n")
        category_winners = overall_comparison.get("category_winners", {})
        category_names = {
            "style_learning_tests": "聊天风格学习",
            "accuracy_boost_tests": "算命准确性提升",
            "info_extraction_tests": "信息提取"
        }
        
        for category, chinese_name in category_names.items():
            winner = category_winners.get(category, "未知")
            f.write(f"- **{chinese_name}**: {winner}\n")
        
        f.write("\n### 优势分析\n\n")
        strength_analysis = overall_comparison.get("strength_analysis", {})
        
        for framework in ["memu", "memobase"]:
            framework_data = strength_analysis.get(framework, {})
            wins = framework_data.get("wins", 0)
            strong_areas = framework_data.get("strong_areas", [])
            characteristics = framework_data.get("characteristics", [])
            
            f.write(f"#### {framework.upper()}\n")
            f.write(f"- **获胜次数**: {wins}\n")
            f.write(f"- **优势领域**: {', '.join(strong_areas) if strong_areas else '无明显优势'}\n")
            f.write(f"- **特点**: {', '.join(characteristics)}\n\n")
        
        f.write("## 性能指标\n\n")
        for framework, metrics in performance_metrics.items():
            f.write(f"### {framework.upper()}\n")
            for metric_name, metric_value in metrics.items():
                f.write(f"- **{metric_name}**: {metric_value}\n")
            f.write("\n")
        
        f.write("## 建议\n\n")
        f.write("基于测试结果，建议：\n\n")
        
        if winner == "memu":
            f.write("- 优先考虑使用 Memu 框架\n")
            f.write("- Memu 在大多数测试场景中表现更佳\n")
        elif winner == "memobase":
            f.write("- 优先考虑使用 Memobase 框架\n")
            f.write("- Memobase 在大多数测试场景中表现更佳\n")
        else:
            f.write("- 两个框架各有优势，可根据具体需求选择\n")
            f.write("- 考虑混合使用两个框架的策略\n")
        
        f.write("\n---\n")
        f.write(f"*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
    
    print(f"✅ 简要报告已生成: {summary_file}")

def display_key_results(results: dict):
    """显示关键结果"""
    print("\n" + "=" * 50)
    print("📊 关键测试结果")
    print("=" * 50)
    
    overall_comparison = results.get("overall_comparison", {})
    
    # 总体获胜者
    winner = overall_comparison.get("overall_winner", "未知")
    print(f"\n🏆 总体获胜者: {winner.upper()}")
    
    # 各类别结果
    print(f"\n📋 各类别测试结果:")
    category_winners = overall_comparison.get("category_winners", {})
    category_names = {
        "style_learning_tests": "聊天风格学习",
        "accuracy_boost_tests": "算命准确性提升", 
        "info_extraction_tests": "信息提取"
    }
    
    for category, chinese_name in category_names.items():
        winner = category_winners.get(category, "未知")
        emoji = "🥇" if winner != "tie" else "🤝"
        print(f"  {emoji} {chinese_name}: {winner}")
    
    # 优势分析
    print(f"\n💪 优势分析:")
    strength_analysis = overall_comparison.get("strength_analysis", {})
    
    for framework in ["memu", "memobase"]:
        framework_data = strength_analysis.get(framework, {})
        wins = framework_data.get("wins", 0)
        strong_areas = framework_data.get("strong_areas", [])
        
        print(f"  🔸 {framework.upper()}: {wins}次获胜")
        if strong_areas:
            print(f"    优势领域: {', '.join(strong_areas)}")
    
    print("\n✅ 测试完成！查看详细报告文件获取更多信息。")

if __name__ == "__main__":
    main()