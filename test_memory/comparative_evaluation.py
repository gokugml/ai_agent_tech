"""
记忆系统对比评测程序

同时对MemoBase和Memu两个记忆系统进行评测，并生成对比分析报告
"""

import os
import sys
from typing import Dict, List, Any
from datetime import datetime
import json

# 添加项目根目录到路径
sys.path.append(os.path.dirname(__file__))

try:
    from test_memobase.memory_evaluator import MemoryEvaluator as MemoBaseEvaluator
    from test_memu.memu_evaluator import MemuEvaluator
    EVALUATORS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ 导入评测器失败: {e}")
    EVALUATORS_AVAILABLE = False


class ComparativeEvaluator:
    """记忆系统对比评测器"""
    
    def __init__(self):
        if not EVALUATORS_AVAILABLE:
            raise RuntimeError("无法导入必要的评测器模块")
        
        self.memobase_evaluator = None
        self.memu_evaluator = None
        self.results = {}
    
    def run_memobase_evaluation(self) -> Dict[str, Any]:
        """运行MemoBase评测"""
        print("🚀 开始MemoBase记忆系统评测...")
        print("=" * 60)
        
        try:
            self.memobase_evaluator = MemoBaseEvaluator()
            
            # 设置测试环境但不插入数据（避免重复插入）
            self.memobase_evaluator.setup_test_user()
            
            # 执行评测
            results = self.memobase_evaluator.evaluate_all_scenarios()
            
            print("✅ MemoBase评测完成!\n")
            return results
            
        except Exception as e:
            print(f"❌ MemoBase评测失败: {e}")
            return {
                "error": str(e),
                "memory_framework": "MemoBase",
                "evaluation_timestamp": datetime.now().isoformat(),
                "overall_average": 0.0,
                "total_test_cases": 0
            }
    
    def run_memu_evaluation(self) -> Dict[str, Any]:
        """运行Memu评测"""
        print("🚀 开始Memu记忆系统评测...")
        print("=" * 60)
        
        try:
            self.memu_evaluator = MemuEvaluator()
            
            # 设置测试数据
            self.memu_evaluator.setup_test_data()
            
            # 执行评测
            results = self.memu_evaluator.evaluate_all_scenarios()
            
            print("✅ Memu评测完成!\n")
            return results
            
        except Exception as e:
            print(f"❌ Memu评测失败: {e}")
            import traceback
            traceback.print_exc()
            return {
                "error": str(e),
                "memory_framework": "Memu",
                "evaluation_timestamp": datetime.now().isoformat(),
                "overall_average": 0.0,
                "total_test_cases": 0
            }
    
    def generate_comparative_report(self, memobase_results: Dict[str, Any], memu_results: Dict[str, Any]) -> str:
        """生成对比评测报告"""
        
        report = []
        report.append("=" * 100)
        report.append("🧠 记忆系统对比评测报告")
        report.append("=" * 100)
        report.append(f"评测时间: {datetime.now().isoformat()}")
        report.append(f"MemoBase测试用例: {memobase_results.get('total_test_cases', 0)}")
        report.append(f"Memu测试用例: {memu_results.get('total_test_cases', 0)}")
        report.append("")
        
        # 整体对比
        report.append("📊 整体性能对比")
        report.append("-" * 60)
        
        memobase_avg = memobase_results.get('overall_average', 0.0)
        memu_avg = memu_results.get('overall_average', 0.0)
        
        report.append(f"{'记忆系统':<15} {'综合得分':<10} {'Context/聚类':<12} {'Profile/记忆项目':<15}")
        report.append("-" * 60)
        
        # MemoBase结果
        memobase_context = memobase_results.get('overall_context_avg', 0.0)
        memobase_profile = memobase_results.get('overall_profile_avg', 0.0)
        report.append(f"{'MemoBase':<15} {memobase_avg:<10.2f} {memobase_context:<12.2f} {memobase_profile:<15.2f}")
        
        # Memu结果
        memu_clustered = memu_results.get('overall_clustered_avg', 0.0)
        memu_memory = memu_results.get('overall_memory_items_avg', 0.0)
        report.append(f"{'Memu':<15} {memu_avg:<10.2f} {memu_clustered:<12.2f} {memu_memory:<15.2f}")
        
        # 性能差异分析
        report.append("")
        report.append("📈 性能差异分析")
        report.append("-" * 60)
        
        if memobase_avg > memu_avg:
            winner = "MemoBase"
            advantage = memobase_avg - memu_avg
        elif memu_avg > memobase_avg:
            winner = "Memu"
            advantage = memu_avg - memobase_avg
        else:
            winner = "平分"
            advantage = 0.0
        
        report.append(f"🏆 综合性能优胜: {winner}")
        if advantage > 0:
            report.append(f"📊 性能优势: {advantage:.2f} 分 ({advantage/10*100:.1f}%)")
        
        # 各维度对比
        report.append("")
        report.append("🔍 各维度详细对比")
        report.append("-" * 60)
        
        # Context vs 聚类分类
        context_diff = memobase_context - memu_clustered
        if abs(context_diff) > 0.5:
            context_winner = "MemoBase Context检索" if context_diff > 0 else "Memu 聚类分类检索"
            report.append(f"检索维度1: {context_winner} 领先 {abs(context_diff):.2f} 分")
        else:
            report.append("检索维度1: MemoBase Context检索 vs Memu 聚类分类检索 - 性能相当")
        
        # Profile vs 记忆项目
        profile_diff = memobase_profile - memu_memory
        if abs(profile_diff) > 0.5:
            profile_winner = "MemoBase Profile检索" if profile_diff > 0 else "Memu 记忆项目检索"
            report.append(f"检索维度2: {profile_winner} 领先 {abs(profile_diff):.2f} 分")
        else:
            report.append("检索维度2: MemoBase Profile检索 vs Memu 记忆项目检索 - 性能相当")
        
        # 场景级对比分析
        if ("scenario_results" in memobase_results and "scenario_results" in memu_results):
            report.append("")
            report.append("🎯 场景级性能对比")
            report.append("-" * 60)
            
            memobase_scenarios = memobase_results["scenario_results"]
            memu_scenarios = memu_results["scenario_results"]
            
            scenario_comparison = []
            
            for scenario_name in memobase_scenarios.keys():
                if scenario_name in memu_scenarios:
                    mb_score = memobase_scenarios[scenario_name]["scenario_overall_avg"]
                    mu_score = memu_scenarios[scenario_name]["scenario_overall_avg"]
                    
                    diff = mb_score - mu_score
                    if abs(diff) > 0.5:
                        winner = "MemoBase" if diff > 0 else "Memu"
                        scenario_comparison.append({
                            "scenario": scenario_name,
                            "winner": winner,
                            "mb_score": mb_score,
                            "mu_score": mu_score,
                            "diff": abs(diff)
                        })
            
            # 显示有显著差异的场景
            if scenario_comparison:
                report.append("显著性能差异的场景:")
                for comp in sorted(scenario_comparison, key=lambda x: x["diff"], reverse=True)[:3]:
                    report.append(f"  {comp['scenario']}: {comp['winner']} 领先 {comp['diff']:.2f}分")
                    report.append(f"    MemoBase: {comp['mb_score']:.2f}, Memu: {comp['mu_score']:.2f}")
        
        # 错误信息
        if "error" in memobase_results:
            report.append("")
            report.append("❌ MemoBase评测错误:")
            report.append(f"   {memobase_results['error']}")
        
        if "error" in memu_results:
            report.append("")
            report.append("❌ Memu评测错误:")
            report.append(f"   {memu_results['error']}")
        
        # 评测建议
        report.append("")
        report.append("💡 评测建议")
        report.append("-" * 60)
        
        if memobase_avg > 7.0 or memu_avg > 7.0:
            report.append("✅ 两个记忆系统都表现良好，可根据具体场景需求选择")
        elif max(memobase_avg, memu_avg) > 5.0:
            report.append("⚠️ 记忆系统有一定效果，但仍有优化空间")
        else:
            report.append("❌ 记忆系统效果有待改进，建议检查数据质量和检索算法")
        
        if abs(memobase_avg - memu_avg) < 1.0:
            report.append("🤝 两系统性能相近，可考虑混合使用或根据成本选择")
        
        report.append("")
        report.append("=" * 100)
        
        return "\n".join(report)
    
    def save_comparative_results(self, memobase_results: Dict[str, Any], memu_results: Dict[str, Any]) -> None:
        """保存对比评测结果"""
        
        comparative_data = {
            "evaluation_timestamp": datetime.now().isoformat(),
            "memobase_results": memobase_results,
            "memu_results": memu_results,
            "comparison_summary": {
                "memobase_overall": memobase_results.get('overall_average', 0.0),
                "memu_overall": memu_results.get('overall_average', 0.0),
                "performance_difference": abs(memobase_results.get('overall_average', 0.0) - 
                                           memu_results.get('overall_average', 0.0)),
                "winner": "MemoBase" if memobase_results.get('overall_average', 0.0) > 
                         memu_results.get('overall_average', 0.0) else "Memu"
            }
        }
        
        # 保存详细对比数据
        output_path = os.path.join(os.path.dirname(__file__), "comparative_evaluation_results.json")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(comparative_data, f, ensure_ascii=False, indent=2)
        
        print(f"📁 对比评测结果已保存至: {output_path}")
    
    def run_comparative_evaluation(self) -> None:
        """运行完整的对比评测"""
        print("🧠 记忆系统对比评测程序启动")
        print("=" * 80)
        print("正在评测 MemoBase 和 Memu 两个记忆系统的性能差异...")
        print("")
        
        try:
            # 1. 运行MemoBase评测
            memobase_results = self.run_memobase_evaluation()
            
            # 2. 运行Memu评测
            memu_results = self.run_memu_evaluation()
            
            # 3. 生成对比报告
            comparative_report = self.generate_comparative_report(memobase_results, memu_results)
            print(comparative_report)
            
            # 4. 保存结果
            self.save_comparative_results(memobase_results, memu_results)
            
            print("✅ 记忆系统对比评测完成!")
            
        except Exception as e:
            print(f"❌ 对比评测过程中发生错误: {e}")
            import traceback
            traceback.print_exc()
            raise


def main():
    """主函数"""
    if not EVALUATORS_AVAILABLE:
        print("❌ 无法加载评测器，请检查模块导入")
        return
    
    evaluator = ComparativeEvaluator()
    evaluator.run_comparative_evaluation()


if __name__ == "__main__":
    main()