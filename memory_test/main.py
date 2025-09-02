#!/usr/bin/env python3
"""
AI回复效果真实测试框架 - 主入口

使用示例:
    python main.py --scenario first_divination_basic --framework memobase --count 5
    python main.py --compare-frameworks --scenario-count 3
"""

import asyncio
import argparse
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

from loguru import logger
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, TaskID
from rich.panel import Panel
from rich.text import Text

# 配置日志
logger.remove()
logger.add(
    sys.stderr, 
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | {message}",
    level="INFO"
)

console = Console()

# 导入框架模块
try:
    from memory_test.input_generation.template_designer import InputTemplateDesigner
    from memory_test.input_generation.ai_input_generator import AIInputGenerator
    from memory_test.response_testing.real_ai_tester import RealAITester
    from memory_test.response_testing.response_evaluator import ResponseQualityEvaluator
    from memory_test.framework_tests.memobase_real_test import MemobaseRealTester
    from memory_test.framework_tests.memu_real_test import MemuRealTester
    from memory_test.evaluation.conversation_analyzer import ConversationAnalyzer
    from memory_test.evaluation.memory_impact_assessor import MemoryImpactAssessor
    from memory_test.config import settings, ensure_results_directory
except ImportError as e:
    console.print(f"[red]导入错误: {e}[/red]")
    console.print("[yellow]请确保在正确的目录下运行，并且已安装所需依赖[/yellow]")
    sys.exit(1)


class MemoryTestRunner:
    """记忆测试运行器"""
    
    def __init__(self):
        self.console = console
        self.results_dir = ensure_results_directory()
        
    async def run_single_framework_test(self,
                                      framework_name: str,
                                      scenario_id: str,
                                      input_count: int = 5) -> Dict[str, Any]:
        """运行单个框架测试"""
        
        self.console.print(Panel(
            f"[bold blue]开始测试框架: {framework_name}[/bold blue]\\n"
            f"场景: {scenario_id}\\n"
            f"输入数量: {input_count}",
            title="测试开始"
        ))
        
        results = {
            "framework": framework_name,
            "scenario": scenario_id,
            "input_count": input_count,
            "start_time": datetime.now().isoformat(),
            "test_results": {}
        }
        
        try:
            with Progress() as progress:
                # 步骤1: 创建输入模板
                task1 = progress.add_task("[cyan]创建输入模板...", total=1)
                
                designer = InputTemplateDesigner()
                template = designer.create_personalized_template(scenario_id)
                
                progress.update(task1, completed=1)
                self.console.print("✅ 输入模板创建完成")
                
                # 步骤2: 生成AI输入
                task2 = progress.add_task("[cyan]生成AI输入...", total=1)
                
                generator = AIInputGenerator()
                inputs = await generator.generate_user_input(template, input_count)
                
                progress.update(task2, completed=1)
                self.console.print(f"✅ 生成 {len(inputs)} 个AI输入")
                
                # 步骤3: 测试AI回复
                task3 = progress.add_task("[cyan]测试AI回复...", total=len(inputs))
                
                ai_tester = RealAITester(framework_name)
                session_id = ai_tester.create_test_session(template["user_context"])
                
                responses = []
                for i, input_data in enumerate(inputs):
                    # 构建记忆上下文 - 修复记忆集成问题
                    memory_context = self._build_memory_context(session_id, input_data, responses)
                    
                    response = await ai_tester.generate_ai_response(
                        session_id,
                        input_data.user_message,
                        memory_context
                    )
                    responses.append(response)
                    progress.update(task3, advance=1)
                
                self.console.print(f"✅ 完成 {len(responses)} 轮AI对话")
                
                # 步骤4: 评估回复质量
                task4 = progress.add_task("[cyan]评估回复质量...", total=1)
                
                evaluator = ResponseQualityEvaluator()
                conversation_eval = evaluator.evaluate_conversation(responses)
                
                progress.update(task4, completed=1)
                self.console.print("✅ 回复质量评估完成")
                
                # 步骤5: 深度对话分析
                task5 = progress.add_task("[cyan]进行深度分析...", total=1)
                
                analyzer = ConversationAnalyzer()
                conversation_analysis = analyzer.analyze_single_conversation(responses)
                
                progress.update(task5, completed=1)
                self.console.print("✅ 深度对话分析完成")
            
            # 整理结果
            results["test_results"] = {
                "responses": [
                    {
                        "user_input": r.user_input,
                        "ai_response": r.ai_response,
                        "response_time": r.response_time,
                        "timestamp": r.timestamp
                    } for r in responses
                ],
                "quality_evaluation": {
                    "overall_score": conversation_eval.overall_conversation_score,
                    "conversation_flow_score": conversation_eval.conversation_flow_score,
                    "memory_utilization_score": conversation_eval.memory_utilization_score,
                    "user_satisfaction_estimate": conversation_eval.user_satisfaction_estimate
                },
                "conversation_analysis": conversation_analysis,
                "session_summary": ai_tester.get_session_summary(session_id)
            }
            
            results["end_time"] = datetime.now().isoformat()
            results["success"] = True
            
            # 显示结果摘要
            self._display_test_summary(results)
            
            return results
            
        except Exception as e:
            logger.error(f"测试过程中出现错误: {e}")
            results["error"] = str(e)
            results["success"] = False
            return results
    
    async def run_framework_comparison(self,
                                     scenario_ids: List[str],
                                     input_count_per_scenario: int = 3) -> Dict[str, Any]:
        """运行框架对比测试"""
        
        self.console.print(Panel(
            f"[bold magenta]开始框架对比测试[/bold magenta]\\n"
            f"测试场景: {', '.join(scenario_ids)}\\n"
            f"每场景输入数: {input_count_per_scenario}",
            title="框架对比测试"
        ))
        
        comparison_results = {
            "test_type": "framework_comparison",
            "scenarios": scenario_ids,
            "input_count_per_scenario": input_count_per_scenario,
            "start_time": datetime.now().isoformat(),
            "frameworks": {}
        }
        
        frameworks = ["memobase", "memu"]
        all_responses = {"memobase": [], "memu": []}
        
        try:
            with Progress() as progress:
                total_tests = len(frameworks) * len(scenario_ids)
                main_task = progress.add_task("[bold green]总体进度", total=total_tests)
                
                for framework in frameworks:
                    framework_responses = []
                    
                    for scenario_id in scenario_ids:
                        self.console.print(f"\\n[bold cyan]测试 {framework.upper()} - {scenario_id}[/bold cyan]")
                        
                        # 运行单个测试
                        result = await self.run_single_framework_test(
                            framework, scenario_id, input_count_per_scenario
                        )
                        
                        if result["success"]:
                            # 提取响应数据用于对比
                            responses_data = result["test_results"]["responses"]
                            framework_responses.extend(responses_data)
                        
                        progress.update(main_task, advance=1)
                    
                    all_responses[framework] = framework_responses
                    comparison_results["frameworks"][framework] = {
                        "total_responses": len(framework_responses),
                        "test_scenarios": scenario_ids
                    }
                
                # 进行框架对比分析
                if all_responses["memobase"] and all_responses["memu"]:
                    self.console.print("\\n[bold yellow]正在进行框架对比分析...[/bold yellow]")
                    
                    # 这里简化处理，实际使用中需要转换为AIResponse对象
                    comparison_summary = self._simple_framework_comparison(all_responses)
                    comparison_results["comparison_analysis"] = comparison_summary
                else:
                    self.console.print("\\n[red]框架对比数据不足，跳过对比分析[/red]")
            
            comparison_results["end_time"] = datetime.now().isoformat()
            comparison_results["success"] = True
            
            # 显示对比结果
            self._display_comparison_results(comparison_results)
            
            return comparison_results
            
        except Exception as e:
            logger.error(f"框架对比测试出现错误: {e}")
            comparison_results["error"] = str(e)
            comparison_results["success"] = False
            return comparison_results
    
    def _simple_framework_comparison(self, all_responses: Dict[str, List]) -> Dict[str, Any]:
        """简单的框架对比分析"""
        
        memobase_responses = all_responses["memobase"]
        memu_responses = all_responses["memu"]
        
        # 计算基础指标
        memobase_avg_length = sum(len(r["ai_response"]) for r in memobase_responses) / len(memobase_responses)
        memu_avg_length = sum(len(r["ai_response"]) for r in memu_responses) / len(memu_responses)
        
        memobase_avg_time = sum(r["response_time"] for r in memobase_responses) / len(memobase_responses)
        memu_avg_time = sum(r["response_time"] for r in memu_responses) / len(memu_responses)
        
        # 简单评分（实际使用中会更复杂）
        length_winner = "Memobase" if memobase_avg_length > memu_avg_length else "MemU"
        speed_winner = "Memobase" if memobase_avg_time < memu_avg_time else "MemU"
        
        return {
            "metrics": {
                "memobase": {
                    "avg_response_length": memobase_avg_length,
                    "avg_response_time": memobase_avg_time,
                    "total_responses": len(memobase_responses)
                },
                "memu": {
                    "avg_response_length": memu_avg_length, 
                    "avg_response_time": memu_avg_time,
                    "total_responses": len(memu_responses)
                }
            },
            "winners": {
                "content_richness": length_winner,
                "response_speed": speed_winner
            },
            "summary": f"内容丰富度: {length_winner}, 响应速度: {speed_winner}"
        }
    
    def _display_test_summary(self, results: Dict[str, Any]) -> None:
        """显示测试结果摘要"""
        
        if not results["success"]:
            self.console.print(f"[red]测试失败: {results.get('error', '未知错误')}[/red]")
            return
        
        test_results = results["test_results"]
        quality_eval = test_results["quality_evaluation"]
        
        # 创建结果表格
        table = Table(title=f"测试结果摘要 - {results['framework'].upper()}")
        table.add_column("指标", style="cyan")
        table.add_column("数值", style="magenta")
        table.add_column("评级", style="green")
        
        # 添加数据行
        overall_score = quality_eval["overall_score"]
        table.add_row(
            "总体质量分数",
            f"{overall_score:.3f}",
            self._get_score_rating(overall_score)
        )
        
        flow_score = quality_eval["conversation_flow_score"] 
        table.add_row(
            "对话流畅度",
            f"{flow_score:.3f}",
            self._get_score_rating(flow_score)
        )
        
        memory_score = quality_eval["memory_utilization_score"]
        table.add_row(
            "记忆利用度",
            f"{memory_score:.3f}",
            self._get_score_rating(memory_score)
        )
        
        satisfaction = quality_eval["user_satisfaction_estimate"]
        table.add_row(
            "用户满意度估算",
            f"{satisfaction:.3f}",
            self._get_score_rating(satisfaction)
        )
        
        response_count = len(test_results["responses"])
        table.add_row("对话轮数", str(response_count), "📊")
        
        self.console.print(table)
        
        # 显示关键洞察
        analysis = test_results["conversation_analysis"]
        insights = analysis.get("insights_and_recommendations", [])
        
        if insights:
            self.console.print("\\n[bold blue]关键洞察:[/bold blue]")
            for i, insight in enumerate(insights[:3], 1):
                self.console.print(f"  {i}. {insight}")
    
    def _display_comparison_results(self, results: Dict[str, Any]) -> None:
        """显示框架对比结果"""
        
        if not results["success"]:
            self.console.print(f"[red]对比测试失败: {results.get('error', '未知错误')}[/red]")
            return
        
        if "comparison_analysis" not in results:
            self.console.print("[yellow]缺少对比分析数据[/yellow]")
            return
        
        analysis = results["comparison_analysis"]
        
        # 显示对比表格
        table = Table(title="框架对比结果")
        table.add_column("框架", style="cyan")
        table.add_column("平均回复长度", style="magenta")
        table.add_column("平均响应时间", style="green")
        table.add_column("总回复数", style="yellow")
        
        metrics = analysis["metrics"]
        for framework, data in metrics.items():
            table.add_row(
                framework.upper(),
                f"{data['avg_response_length']:.0f} 字符",
                f"{data['avg_response_time']:.2f} 秒",
                str(data['total_responses'])
            )
        
        self.console.print(table)
        
        # 显示获胜者
        winners = analysis["winners"]
        self.console.print(f"\\n[bold green]对比结果:[/bold green]")
        self.console.print(f"• 内容丰富度获胜: [bold]{winners['content_richness']}[/bold]")
        self.console.print(f"• 响应速度获胜: [bold]{winners['response_speed']}[/bold]")
        
        self.console.print(f"\\n[italic]{analysis['summary']}[/italic]")
    
    def _get_score_rating(self, score: float) -> str:
        """根据分数获取评级"""
        if score >= 0.9:
            return "🌟 优秀"
        elif score >= 0.8:
            return "✅ 良好"
        elif score >= 0.7:
            return "🔶 一般"
        elif score >= 0.6:
            return "⚠️ 待改进"
        else:
            return "❌ 较差"
    
    def _build_memory_context(self, session_id: str, input_data, previous_responses: List) -> Dict[str, Any]:
        """构建记忆上下文"""
        memory_context = {}
        
        # 如果有历史对话，添加到上下文中
        if previous_responses:
            # 提取最近的对话历史
            recent_history = []
            for response in previous_responses[-3:]:  # 最近3轮对话
                recent_history.append({
                    "user": response.user_input,
                    "assistant": response.ai_response[:200] + "..." if len(response.ai_response) > 200 else response.ai_response
                })
            
            memory_context["conversation_history"] = recent_history
            
            # 添加一些模拟的用户偏好和历史信息
            memory_context["user_preferences"] = {
                "prefers_detailed_analysis": len(previous_responses) > 1,
                "communication_style": "direct" if len(input_data.user_message) < 20 else "detailed",
                "areas_of_interest": ["事业发展", "人际关系", "财运分析"]
            }
            
            # 模拟一些历史预测记录
            if len(previous_responses) >= 2:
                memory_context["previous_predictions"] = {
                    "last_consultation_date": "2025-08-01",
                    "key_predictions": [
                        "事业方面会有新的机遇",
                        "人际关系将有所改善",
                        "需要注意健康方面的调养"
                    ],
                    "accuracy_feedback": "部分预测已经验证"
                }
        
        return memory_context
    
    def _json_serializer(self, obj):
        """自定义JSON序列化器，处理dataclass和其他不可序列化对象"""
        if hasattr(obj, '__dict__'):
            # 对于有__dict__属性的对象，转换为字典
            return obj.__dict__
        elif hasattr(obj, '_asdict'):
            # 对于namedtuple
            return obj._asdict()
        elif str(type(obj)).startswith('<enum'):
            # 对于枚举类型
            return obj.value
        else:
            # 对于其他类型，转换为字符串
            return str(obj)
    
    async def save_results(self, results: Dict[str, Any], filename_prefix: str = "test_results") -> str:
        """保存测试结果"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{filename_prefix}_{timestamp}.json"
        filepath = self.results_dir / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2, default=self._json_serializer)
            
            self.console.print(f"\\n[green]测试结果已保存到: {filepath}[/green]")
            return str(filepath)
            
        except Exception as e:
            self.console.print(f"\\n[red]保存结果失败: {e}[/red]")
            return ""


async def main():
    """主函数"""
    
    parser = argparse.ArgumentParser(
        description="AI回复效果真实测试框架",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python main.py --scenario first_divination_basic --framework memobase --count 5
  python main.py --compare-frameworks --scenario-count 3
  python main.py --list-scenarios
        """
    )
    
    # 基础参数
    parser.add_argument("--scenario", type=str, default="first_divination_basic",
                       help="测试场景ID (默认: first_divination_basic)")
    parser.add_argument("--framework", type=str, choices=["memobase", "memu"], 
                       default="memobase", help="记忆框架类型 (默认: memobase)")
    parser.add_argument("--count", type=int, default=5, 
                       help="生成输入的数量 (默认: 5)")
    
    # 对比测试参数
    parser.add_argument("--compare-frameworks", action="store_true",
                       help="运行框架对比测试")
    parser.add_argument("--scenario-count", type=int, default=3,
                       help="对比测试中每个场景的输入数量 (默认: 3)")
    
    # 其他参数
    parser.add_argument("--list-scenarios", action="store_true", 
                       help="列出所有可用的测试场景")
    parser.add_argument("--output-dir", type=str, 
                       help="结果输出目录 (默认: test_results)")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="详细输出模式")
    
    args = parser.parse_args()
    
    # 配置日志级别
    if args.verbose:
        logger.remove()
        logger.add(sys.stderr, level="DEBUG")
    
    # 创建测试运行器
    runner = MemoryTestRunner()
    
    try:
        # 列出场景
        if args.list_scenarios:
            from input_generation.scenario_templates import ScenarioTemplateLibrary
            
            library = ScenarioTemplateLibrary()
            scenarios = library.get_all_template_ids()
            
            console.print("[bold blue]可用的测试场景:[/bold blue]")
            for i, scenario in enumerate(scenarios, 1):
                template = library.get_template(scenario)
                console.print(f"  {i:2d}. [cyan]{scenario}[/cyan]")
                console.print(f"      {template.context_setup[:80]}...")
            return
        
        # 运行框架对比测试
        if args.compare_frameworks:
            # 选择几个代表性场景
            scenarios = [
                "first_divination_basic",
                "skeptical_consultation", 
                "follow_up_session"
            ]
            
            results = await runner.run_framework_comparison(scenarios, args.scenario_count)
            await runner.save_results(results, "framework_comparison")
        
        # 运行单框架测试
        else:
            results = await runner.run_single_framework_test(
                args.framework, args.scenario, args.count
            )
            await runner.save_results(results, f"{args.framework}_test")
        
        console.print("\\n[bold green]测试完成! 🎉[/bold green]")
        
    except KeyboardInterrupt:
        console.print("\\n[yellow]测试被用户中断[/yellow]")
    except Exception as e:
        console.print(f"\\n[red]测试过程中出现未预期的错误: {e}[/red]")
        logger.exception("详细错误信息:")


if __name__ == "__main__":
    asyncio.run(main())