"""
增强版记忆系统对比评测程序

支持MemoBase 4种方法和Memu 2种方法的详细对比分析
包含三层分析：核心对比、专用方法评估、综合框架对比
"""

import os
import sys
from typing import Dict, List, Any, Tuple
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


class EnhancedComparativeEvaluator:
    """增强版记忆系统对比评测器"""
    
    def __init__(self):
        if not EVALUATORS_AVAILABLE:
            raise RuntimeError("无法导入必要的评测器模块")
        
        self.memobase_evaluator = None
        self.memu_evaluator = None
        self.results = {}
        
        # 场景-方法适配度预期矩阵（基于方法特点的理论适配度）
        self.method_scenario_fitness = {
            # MemoBase方法
            "context": {
                "时间序列偏好变化（测试时间关联 + 偏好追踪能力）": 8,
                "个人信息碎片化（测试零散信息整合）": 9,
                "复杂关系网络（测试人际关联记忆）": 9,
                "算命场景专门测试（测试算命核心信息记忆）": 8,
                "聊天习惯分析（测试用户行为模式记忆）": 9,
                "情境化行为模式（测试场景-行为关联记忆）": 9,
                "长期人生轨迹（测试时间轴-事件关联记忆）": 8
            },
            "profile": {
                "时间序列偏好变化（测试时间关联 + 偏好追踪能力）": 7,
                "个人信息碎片化（测试零散信息整合）": 9,
                "复杂关系网络（测试人际关联记忆）": 6,
                "算命场景专门测试（测试算命核心信息记忆）": 9,
                "聊天习惯分析（测试用户行为模式记忆）": 8,
                "情境化行为模式（测试场景-行为关联记忆）": 7,
                "长期人生轨迹（测试时间轴-事件关联记忆）": 7
            },
            "search_event": {
                "时间序列偏好变化（测试时间关联 + 偏好追踪能力）": 9,
                "个人信息碎片化（测试零散信息整合）": 6,
                "复杂关系网络（测试人际关联记忆）": 7,
                "算命场景专门测试（测试算命核心信息记忆）": 6,
                "聊天习惯分析（测试用户行为模式记忆）": 6,
                "情境化行为模式（测试场景-行为关联记忆）": 8,
                "长期人生轨迹（测试时间轴-事件关联记忆）": 9
            },
            "search_event_gist": {
                "时间序列偏好变化（测试时间关联 + 偏好追踪能力）": 6,
                "个人信息碎片化（测试零散信息整合）": 8,
                "复杂关系网络（测试人际关联记忆）": 5,
                "算命场景专门测试（测试算命核心信息记忆）": 9,
                "聊天习惯分析（测试用户行为模式记忆）": 5,
                "情境化行为模式（测试场景-行为关联记忆）": 6,
                "长期人生轨迹（测试时间轴-事件关联记忆）": 6
            },
            # Memu方法
            "retrieve_related_memory_items": {
                "时间序列偏好变化（测试时间关联 + 偏好追踪能力）": 8,
                "个人信息碎片化（测试零散信息整合）": 8,
                "复杂关系网络（测试人际关联记忆）": 8,
                "算命场景专门测试（测试算命核心信息记忆）": 8,
                "聊天习惯分析（测试用户行为模式记忆）": 8,
                "情境化行为模式（测试场景-行为关联记忆）": 8,
                "长期人生轨迹（测试时间轴-事件关联记忆）": 8
            },
            "retrieve_related_clustered_categories": {
                "时间序列偏好变化（测试时间关联 + 偏好追踪能力）": 6,
                "个人信息碎片化（测试零散信息整合）": 7,
                "复杂关系网络（测试人际关联记忆）": 8,
                "算命场景专门测试（测试算命核心信息记忆）": 5,
                "聊天习惯分析（测试用户行为模式记忆）": 7,
                "情境化行为模式（测试场景-行为关联记忆）": 6,
                "长期人生轨迹（测试时间轴-事件关联记忆）": 6
            }
        }
    
    def run_memobase_evaluation(self) -> Dict[str, Any]:
        """运行MemoBase评测"""
        print("🚀 开始MemoBase记忆系统评测（4种方法）...")
        print("=" * 70)
        
        try:
            self.memobase_evaluator = MemoBaseEvaluator()
            
            # 设置测试环境
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
        print("🚀 开始Memu记忆系统评测（2种方法）...")
        print("=" * 70)
        
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
    
    def generate_method_scenario_matrix(self, memobase_results: Dict[str, Any], memu_results: Dict[str, Any]) -> Dict[str, Any]:
        """生成场景-方法适配矩阵"""
        
        matrix_data = {}
        
        if "scenario_results" in memobase_results and "scenario_results" in memu_results:
            memobase_scenarios = memobase_results["scenario_results"]
            memu_scenarios = memu_results["scenario_results"]
            
            for scenario_name in memobase_scenarios.keys():
                if scenario_name in memu_scenarios:
                    mb_scenario = memobase_scenarios[scenario_name]
                    mu_scenario = memu_scenarios[scenario_name]
                    
                    matrix_data[scenario_name] = {
                        # MemoBase 4种方法
                        "memobase_context": mb_scenario.get("scenario_context_avg", 0),
                        "memobase_profile": mb_scenario.get("scenario_profile_avg", 0),
                        "memobase_search_event": mb_scenario.get("scenario_search_event_avg", 0),
                        "memobase_search_event_gist": mb_scenario.get("scenario_search_event_gist_avg", 0),
                        # Memu 2种方法
                        "memu_memory_items": mu_scenario.get("scenario_memory_items_avg", 0),
                        "memu_clustered": mu_scenario.get("scenario_clustered_avg", 0),
                        # 预期适配度
                        "expected_fitness": {
                            "context": self.method_scenario_fitness["context"].get(scenario_name, 5),
                            "profile": self.method_scenario_fitness["profile"].get(scenario_name, 5),
                            "search_event": self.method_scenario_fitness["search_event"].get(scenario_name, 5),
                            "search_event_gist": self.method_scenario_fitness["search_event_gist"].get(scenario_name, 5),
                            "memory_items": self.method_scenario_fitness["retrieve_related_memory_items"].get(scenario_name, 5),
                            "clustered": self.method_scenario_fitness["retrieve_related_clustered_categories"].get(scenario_name, 5)
                        }
                    }
        
        return matrix_data
    
    def analyze_core_method_comparison(self, memobase_results: Dict[str, Any], memu_results: Dict[str, Any]) -> Dict[str, Any]:
        """分析核心方法对比 - Context vs Memory Items"""
        
        memobase_core = memobase_results.get("overall_core_method_avg", 0.0)
        memu_core = memu_results.get("overall_core_method_avg", 0.0)
        
        analysis = {
            "memobase_context_score": memobase_core,
            "memu_memory_items_score": memu_core,
            "performance_difference": abs(memobase_core - memu_core),
            "winner": "MemoBase Context" if memobase_core > memu_core else "Memu Memory Items",
            "advantage_percentage": abs(memobase_core - memu_core) / 10 * 100,
            "comparison_result": "significant" if abs(memobase_core - memu_core) > 1.0 else "moderate" if abs(memobase_core - memu_core) > 0.5 else "comparable"
        }
        
        return analysis
    
    def analyze_specialized_methods(self, memobase_results: Dict[str, Any], memu_results: Dict[str, Any]) -> Dict[str, Any]:
        """分析专用方法表现"""
        
        specialized_analysis = {
            "memobase_specialized": {
                "profile_avg": memobase_results.get("overall_profile_avg", 0.0),
                "search_event_avg": memobase_results.get("overall_search_event_avg", 0.0),
                "search_event_gist_avg": memobase_results.get("overall_search_event_gist_avg", 0.0)
            },
            "memu_specialized": {
                "clustered_categories_avg": memu_results.get("overall_clustered_avg", 0.0)
            },
            "best_specialized_method": None,
            "specialized_method_ranking": []
        }
        
        # 排名专用方法
        method_scores = [
            ("MemoBase Profile", specialized_analysis["memobase_specialized"]["profile_avg"]),
            ("MemoBase Search Event", specialized_analysis["memobase_specialized"]["search_event_avg"]),
            ("MemoBase Search Event Gist", specialized_analysis["memobase_specialized"]["search_event_gist_avg"]),
            ("Memu Clustered Categories", specialized_analysis["memu_specialized"]["clustered_categories_avg"])
        ]
        
        method_scores.sort(key=lambda x: x[1], reverse=True)
        specialized_analysis["specialized_method_ranking"] = method_scores
        specialized_analysis["best_specialized_method"] = method_scores[0] if method_scores else None
        
        return specialized_analysis
    
    def generate_enhanced_comparative_report(self, memobase_results: Dict[str, Any], memu_results: Dict[str, Any]) -> str:
        """生成增强版对比评测报告"""
        
        # 生成分析数据
        matrix_data = self.generate_method_scenario_matrix(memobase_results, memu_results)
        core_analysis = self.analyze_core_method_comparison(memobase_results, memu_results)
        specialized_analysis = self.analyze_specialized_methods(memobase_results, memu_results)
        
        report = []
        report.append("=" * 120)
        report.append("🧠 增强版记忆系统对比评测报告")
        report.append("=" * 120)
        report.append(f"评测时间: {datetime.now().isoformat()}")
        report.append(f"MemoBase方法数: 4种 | Memu方法数: 2种")
        report.append(f"测试场景数: {len(matrix_data)}")
        report.append("")
        
        # 第一层：核心方法对比分析
        report.append("🎯 第一层分析：核心通用方法对比")
        report.append("=" * 80)
        report.append("对比核心通用记忆召回能力：")
        report.append(f"• MemoBase Context检索 vs Memu Memory Items检索")
        report.append("")
        
        report.append("📊 核心方法性能对比")
        report.append("-" * 50)
        report.append(f"MemoBase Context得分: {core_analysis['memobase_context_score']:.2f}/10")
        report.append(f"Memu Memory Items得分: {core_analysis['memu_memory_items_score']:.2f}/10")
        report.append(f"性能差异: {core_analysis['performance_difference']:.2f}分 ({core_analysis['advantage_percentage']:.1f}%)")
        report.append(f"🏆 核心通用方法优胜: {core_analysis['winner']}")
        
        comparison_result = core_analysis['comparison_result']
        if comparison_result == "significant":
            report.append("📈 差异评估: 显著差异 (>1.0分)")
        elif comparison_result == "moderate":
            report.append("📈 差异评估: 中等差异 (0.5-1.0分)")
        else:
            report.append("📈 差异评估: 性能相当 (<0.5分)")
        
        report.append("")
        
        # 第二层：专用方法评估
        report.append("🔧 第二层分析：专用方法性能评估")
        report.append("=" * 80)
        
        report.append("📋 专用方法排名")
        report.append("-" * 50)
        for idx, (method_name, score) in enumerate(specialized_analysis["specialized_method_ranking"], 1):
            report.append(f"{idx}. {method_name}: {score:.2f}/10")
        
        if specialized_analysis["best_specialized_method"]:
            best_method, best_score = specialized_analysis["best_specialized_method"]
            report.append(f"\n🥇 最佳专用方法: {best_method} ({best_score:.2f}分)")
        
        report.append("")
        report.append("📊 MemoBase专用方法详情")
        report.append("-" * 50)
        mb_specialized = specialized_analysis["memobase_specialized"]
        report.append(f"Profile检索(用户属性): {mb_specialized['profile_avg']:.2f}/10")
        report.append(f"Search Event检索(事件时间线): {mb_specialized['search_event_avg']:.2f}/10")
        report.append(f"Search Event Gist检索(精确事实): {mb_specialized['search_event_gist_avg']:.2f}/10")
        
        report.append("")
        report.append("📊 Memu专用方法详情")
        report.append("-" * 50)
        mu_specialized = specialized_analysis["memu_specialized"]
        report.append(f"Clustered Categories检索(语义聚类): {mu_specialized['clustered_categories_avg']:.2f}/10")
        
        # 第三层：场景-方法适配矩阵
        report.append("")
        report.append("🎲 第三层分析：场景-方法适配分析")
        report.append("=" * 80)
        
        report.append("📈 场景适配度矩阵 (实际得分 vs 理论适配度)")
        report.append("-" * 80)
        
        # 表头
        header = f"{'场景':<25} {'MB-Ctx':<8} {'MB-Prof':<9} {'MB-Evt':<8} {'MB-EG':<8} {'MU-Mem':<8} {'MU-Cat':<8}"
        report.append(header)
        report.append("-" * 80)
        
        # 数据行
        for scenario_name, data in matrix_data.items():
            scenario_short = scenario_name.split("（")[0][:20]  # 截取场景名称
            row = f"{scenario_short:<25} {data['memobase_context']:<8.1f} {data['memobase_profile']:<9.1f} " \
                  f"{data['memobase_search_event']:<8.1f} {data['memobase_search_event_gist']:<8.1f} " \
                  f"{data['memu_memory_items']:<8.1f} {data['memu_clustered']:<8.1f}"
            report.append(row)
        
        # 场景推荐分析
        report.append("")
        report.append("🎯 场景最佳方法推荐")
        report.append("-" * 80)
        
        for scenario_name, data in matrix_data.items():
            scenario_short = scenario_name.split("（")[0]
            
            # 找出该场景下得分最高的方法
            method_scores = [
                ("MemoBase Context", data['memobase_context']),
                ("MemoBase Profile", data['memobase_profile']),
                ("MemoBase Search Event", data['memobase_search_event']),
                ("MemoBase Search Event Gist", data['memobase_search_event_gist']),
                ("Memu Memory Items", data['memu_memory_items']),
                ("Memu Clustered Categories", data['memu_clustered'])
            ]
            
            best_method, best_score = max(method_scores, key=lambda x: x[1])
            report.append(f"• {scenario_short}: {best_method} ({best_score:.1f}分)")
        
        # 第四层：综合框架对比
        report.append("")
        report.append("🏗️ 第四层分析：综合框架对比")
        report.append("=" * 80)
        
        memobase_overall = memobase_results.get("overall_average", 0.0)
        memu_overall = memu_results.get("overall_average", 0.0)
        
        report.append("📊 综合性能对比")
        report.append("-" * 50)
        report.append(f"MemoBase综合得分: {memobase_overall:.2f}/10")
        report.append(f"Memu综合得分: {memu_overall:.2f}/10")
        
        if memobase_overall > memu_overall:
            winner = "MemoBase"
            advantage = memobase_overall - memu_overall
        else:
            winner = "Memu"
            advantage = memu_overall - memobase_overall
        
        report.append(f"🏆 综合性能优胜: {winner}")
        report.append(f"📊 综合优势: {advantage:.2f}分 ({advantage/10*100:.1f}%)")
        
        # 使用建议
        report.append("")
        report.append("💡 使用建议和最佳实践")
        report.append("-" * 80)
        
        if core_analysis["comparison_result"] == "significant":
            if core_analysis["memobase_context_score"] > core_analysis["memu_memory_items_score"]:
                report.append("✅ 核心推荐: MemoBase的Context方法在通用记忆召回上有显著优势")
            else:
                report.append("✅ 核心推荐: Memu的Memory Items方法在通用记忆召回上有显著优势")
        else:
            report.append("🤝 核心推荐: 两个框架的通用召回能力相近，可根据其他因素选择")
        
        # 专用场景推荐
        if specialized_analysis["best_specialized_method"]:
            best_specialized, best_score = specialized_analysis["best_specialized_method"]
            report.append(f"🎯 专用功能推荐: {best_specialized} 在专用检索场景表现最佳")
        
        # 架构特点总结
        report.append("")
        report.append("🔍 框架特点总结")
        report.append("-" * 50)
        report.append("MemoBase优势:")
        report.append("  • 方法丰富(4种)，可针对不同场景选择最优方法")
        report.append("  • Profile检索特别适合用户属性跟踪") 
        report.append("  • Event系列检索适合时间线和事实查询")
        
        report.append("")
        report.append("Memu优势:")
        report.append("  • 简洁高效(2种方法)，降低选择复杂度")
        report.append("  • Memory Items提供稳定的通用召回能力")
        report.append("  • Clustered Categories适合语义相关性分析")
        
        report.append("")
        report.append("=" * 120)
        
        return "\n".join(report)
    
    def save_enhanced_results(self, memobase_results: Dict[str, Any], memu_results: Dict[str, Any]) -> None:
        """保存增强版评测结果"""
        
        matrix_data = self.generate_method_scenario_matrix(memobase_results, memu_results)
        core_analysis = self.analyze_core_method_comparison(memobase_results, memu_results)
        specialized_analysis = self.analyze_specialized_methods(memobase_results, memu_results)
        
        enhanced_data = {
            "evaluation_timestamp": datetime.now().isoformat(),
            "evaluation_type": "enhanced_comparative",
            "frameworks_compared": ["MemoBase", "Memu"],
            "methods_tested": {
                "memobase": memobase_results.get("methods_tested", []),
                "memu": memu_results.get("methods_tested", [])
            },
            "raw_results": {
                "memobase_results": memobase_results,
                "memu_results": memu_results
            },
            "analysis": {
                "core_method_comparison": core_analysis,
                "specialized_method_analysis": specialized_analysis,
                "scenario_method_matrix": matrix_data
            },
            "summary": {
                "memobase_overall": memobase_results.get("overall_average", 0.0),
                "memu_overall": memu_results.get("overall_average", 0.0),
                "winner": "MemoBase" if memobase_results.get("overall_average", 0.0) > 
                         memu_results.get("overall_average", 0.0) else "Memu",
                "core_method_winner": core_analysis["winner"]
            }
        }
        
        # 保存详细对比数据
        output_path = os.path.join(os.path.dirname(__file__), "enhanced_comparative_results.json")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(enhanced_data, f, ensure_ascii=False, indent=2)
        
        print(f"📁 增强版对比评测结果已保存至: {output_path}")
    
    def run_enhanced_comparative_evaluation(self) -> None:
        """运行增强版完整对比评测"""
        print("🧠 增强版记忆系统对比评测程序启动")
        print("=" * 100)
        print("正在深度评测 MemoBase(4种方法) 和 Memu(2种方法) 的性能差异...")
        print("包含三层分析：核心对比 + 专用方法评估 + 场景适配分析")
        print("")
        
        try:
            # 1. 运行MemoBase评测（4种方法）
            memobase_results = self.run_memobase_evaluation()
            
            # 2. 运行Memu评测（2种方法）
            memu_results = self.run_memu_evaluation()
            
            # 3. 生成增强版对比报告
            enhanced_report = self.generate_enhanced_comparative_report(memobase_results, memu_results)
            print(enhanced_report)
            
            # 4. 保存详细结果
            self.save_enhanced_results(memobase_results, memu_results)
            
            print("✅ 增强版记忆系统对比评测完成!")
            
        except Exception as e:
            print(f"❌ 增强版评测过程中发生错误: {e}")
            import traceback
            traceback.print_exc()
            raise


def main():
    """主函数"""
    if not EVALUATORS_AVAILABLE:
        print("❌ 无法加载评测器，请检查模块导入")
        return
    
    evaluator = EnhancedComparativeEvaluator()
    evaluator.run_enhanced_comparative_evaluation()


if __name__ == "__main__":
    main()