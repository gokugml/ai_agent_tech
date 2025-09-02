"""
真实AI测试器

使用真实的AI模型进行回复测试，验证AI根据记忆和用户输入的真实回复效果
"""

import asyncio
import json
import time
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import uuid

try:
    import openai
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import anthropic
    from anthropic import AsyncAnthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

from loguru import logger

from ..config import get_ai_client_config


@dataclass
class AIResponse:
    """AI回复数据类"""
    response_id: str
    session_id: str
    user_input: str
    ai_response: str
    response_time: float  # 回复时间（秒）
    token_usage: Dict[str, int]  # token使用情况
    memory_context: Dict[str, Any]  # 使用的记忆上下文
    metadata: Dict[str, Any]
    timestamp: str


@dataclass
class TestSession:
    """测试会话数据类"""
    session_id: str
    framework_type: str  # "memu" 或 "memobase"
    user_profile: Dict[str, Any]
    conversation_history: List[Dict[str, str]]
    responses: List[AIResponse]
    session_start_time: str
    session_end_time: Optional[str] = None
    total_interactions: int = 0


class MemoryAwarePromptBuilder:
    """记忆感知提示构建器"""
    
    def __init__(self):
        self.system_prompt_template = '''你是一位专业的算命师，具有深厚的易学知识和丰富的咨询经验。

你的能力包括：
1. 八字命理分析
2. 五行相生相克理论
3. 流年运势预测
4. 人生指导和建议
5. 情感和事业咨询

{memory_context}

与用户交流时，请注意：
1. 保持专业、温和的语调
2. 基于传统文化理论进行分析
3. 给出具体、实用的建议
4. 适当引用历史信息和之前的分析
5. 回复长度适中，条理清晰

用户信息：
- 性格特征：{personality_traits}
- 沟通偏好：{communication_style}
- 当前关注：{current_concerns}'''

        self.memory_integration_templates = {
            "previous_consultation": "根据之前的咨询记录：{previous_info}",
            "prediction_verification": "关于之前的预测验证：{verification_info}",
            "user_feedback": "考虑到您的反馈：{feedback_info}",
            "life_changes": "根据您最近的生活变化：{changes_info}",
            "continuous_guidance": "延续之前的指导思路：{guidance_info}"
        }
    
    def build_system_prompt(self, 
                          user_profile: Dict[str, Any],
                          memory_context: Dict[str, Any]) -> str:
        """构建系统提示"""
        
        # 构建记忆上下文
        memory_text = self._format_memory_context(memory_context)
        
        # 格式化用户信息
        personality_traits = ", ".join(user_profile.get("personality_traits", ["普通"]))
        communication_style = user_profile.get("communication_style", "直接")
        current_concerns = ", ".join(user_profile.get("concerns", ["一般咨询"]))
        
        return self.system_prompt_template.format(
            memory_context=memory_text,
            personality_traits=personality_traits,
            communication_style=communication_style,
            current_concerns=current_concerns
        )
    
    def _format_memory_context(self, memory_context: Dict[str, Any]) -> str:
        """格式化记忆上下文"""
        if not memory_context:
            return "这是您第一次咨询，我将为您提供全面的分析。"
        
        context_parts = []
        
        # 处理不同类型的记忆信息
        if "previous_predictions" in memory_context:
            prev_info = memory_context["previous_predictions"]
            context_parts.append(
                self.memory_integration_templates["previous_consultation"].format(
                    previous_info=self._summarize_previous_predictions(prev_info)
                )
            )
        
        if "verification_feedback" in memory_context:
            feedback_info = memory_context["verification_feedback"]
            context_parts.append(
                self.memory_integration_templates["prediction_verification"].format(
                    verification_info=self._summarize_verification(feedback_info)
                )
            )
        
        if "life_changes" in memory_context:
            changes_info = memory_context["life_changes"]
            context_parts.append(
                self.memory_integration_templates["life_changes"].format(
                    changes_info=self._summarize_life_changes(changes_info)
                )
            )
        
        if "user_feedback" in memory_context:
            feedback = memory_context["user_feedback"]
            context_parts.append(
                self.memory_integration_templates["user_feedback"].format(
                    feedback_info=self._summarize_user_feedback(feedback)
                )
            )
        
        if "conversation_style" in memory_context:
            style_info = memory_context["conversation_style"]
            context_parts.append(f"根据您的沟通偏好：{style_info}")
        
        return "\\n\\n".join(context_parts) if context_parts else "这是一次新的咨询会话。"
    
    def _summarize_previous_predictions(self, predictions: List[Dict[str, Any]]) -> str:
        """总结之前的预测"""
        if not predictions:
            return "暂无历史预测记录"
        
        summary_parts = []
        for pred in predictions[-3:]:  # 只取最近3个预测
            topic = pred.get("topic", "未知")
            prediction = pred.get("prediction", "")[:100]  # 限制长度
            confidence = pred.get("confidence", 0)
            summary_parts.append(f"{topic}：{prediction}（置信度：{confidence:.1f}）")
        
        return "；".join(summary_parts)
    
    def _summarize_verification(self, verifications: List[Dict[str, Any]]) -> str:
        """总结验证情况"""
        if not verifications:
            return "暂无验证反馈"
        
        correct_count = sum(1 for v in verifications if v.get("verification_status") == "correct")
        total_count = len(verifications)
        accuracy_rate = correct_count / total_count if total_count > 0 else 0
        
        return f"历史预测验证：{correct_count}/{total_count}项准确（准确率：{accuracy_rate:.1%}）"
    
    def _summarize_life_changes(self, changes: List[Dict[str, Any]]) -> str:
        """总结生活变化"""
        if not changes:
            return "暂无重大生活变化"
        
        change_types = []
        for change in changes[-3:]:
            change_type = change.get("type", "未知变化")
            description = change.get("description", "")[:50]
            change_types.append(f"{change_type}：{description}")
        
        return "；".join(change_types)
    
    def _summarize_user_feedback(self, feedback: List[Dict[str, Any]]) -> str:
        """总结用户反馈"""
        if not feedback:
            return "暂无用户反馈"
        
        recent_feedback = feedback[-2:] if len(feedback) > 1 else feedback
        feedback_summary = []
        
        for fb in recent_feedback:
            content = fb.get("content", "")[:80]
            sentiment = fb.get("sentiment", "neutral")
            feedback_summary.append(f"{content}（态度：{sentiment}）")
        
        return "；".join(feedback_summary)


class RealAITester:
    """真实AI测试器"""
    
    def __init__(self, framework_type: str = "general"):
        self.framework_type = framework_type
        self.ai_config = get_ai_client_config()
        self.client = None
        self.prompt_builder = MemoryAwarePromptBuilder()
        self.active_sessions: Dict[str, TestSession] = {}
        
        self._initialize_client()
    
    def _initialize_client(self) -> None:
        """初始化AI客户端"""
        try:
            if self.ai_config["provider"] == "claude" and ANTHROPIC_AVAILABLE:
                claude_kwargs = {"api_key": self.ai_config["api_key"]}
                if self.ai_config.get("base_url"):
                    claude_kwargs["base_url"] = self.ai_config["base_url"]
                self.client = AsyncAnthropic(**claude_kwargs)
                logger.info(f"Claude客户端初始化成功 (框架: {self.framework_type})")
            elif self.ai_config["provider"] == "openai" and OPENAI_AVAILABLE:
                self.client = AsyncOpenAI(
                    api_key=self.ai_config["api_key"],
                    base_url=self.ai_config.get("base_url")
                )
                logger.info(f"OpenAI客户端初始化成功 (框架: {self.framework_type})")
            else:
                logger.warning(f"AI客户端初始化失败，将使用模拟模式 (框架: {self.framework_type})")
                self.client = None
        except Exception as e:
            logger.error(f"AI客户端初始化错误: {e}")
            self.client = None
    
    def create_test_session(self, user_profile: Dict[str, Any]) -> str:
        """创建测试会话"""
        session_id = f"session_{self.framework_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        
        session = TestSession(
            session_id=session_id,
            framework_type=self.framework_type,
            user_profile=user_profile,
            conversation_history=[],
            responses=[],
            session_start_time=datetime.now().isoformat(),
            total_interactions=0
        )
        
        self.active_sessions[session_id] = session
        logger.info(f"创建测试会话: {session_id}")
        
        return session_id
    
    async def generate_ai_response(self,
                                 session_id: str,
                                 user_input: str,
                                 memory_context: Optional[Dict[str, Any]] = None) -> AIResponse:
        """生成AI回复"""
        
        if session_id not in self.active_sessions:
            raise ValueError(f"会话 {session_id} 不存在")
        
        session = self.active_sessions[session_id]
        start_time = time.time()
        
        try:
            # 构建提示
            system_prompt = self.prompt_builder.build_system_prompt(
                session.user_profile, 
                memory_context or {}
            )
            
            # 生成AI回复
            if self.client:
                ai_response_text, token_usage = await self._call_ai_model(
                    system_prompt, 
                    user_input, 
                    session.conversation_history
                )
            else:
                ai_response_text, token_usage = self._generate_fallback_response(
                    user_input, 
                    memory_context or {}
                )
            
            response_time = time.time() - start_time
            
            # 创建回复对象
            ai_response = AIResponse(
                response_id=f"resp_{session_id}_{len(session.responses)}_{int(time.time())}",
                session_id=session_id,
                user_input=user_input,
                ai_response=ai_response_text,
                response_time=response_time,
                token_usage=token_usage,
                memory_context=memory_context or {},
                metadata={
                    "framework_type": self.framework_type,
                    "ai_provider": self.ai_config["provider"],
                    "model": self.ai_config["model"],
                    "has_memory_context": bool(memory_context)
                },
                timestamp=datetime.now().isoformat()
            )
            
            # 更新会话
            session.responses.append(ai_response)
            session.conversation_history.append({
                "user": user_input,
                "assistant": ai_response_text
            })
            session.total_interactions += 1
            
            logger.info(f"生成AI回复: {session_id}, 耗时: {response_time:.2f}s")
            
            return ai_response
            
        except Exception as e:
            logger.error(f"生成AI回复失败: {e}")
            # 返回错误回复
            return AIResponse(
                response_id=f"error_{session_id}_{int(time.time())}",
                session_id=session_id,
                user_input=user_input,
                ai_response=f"抱歉，回复生成时出现了问题：{str(e)}",
                response_time=time.time() - start_time,
                token_usage={"error": 1},
                memory_context=memory_context or {},
                metadata={"error": str(e)},
                timestamp=datetime.now().isoformat()
            )
    
    async def _call_ai_model(self,
                           system_prompt: str,
                           user_input: str,
                           conversation_history: List[Dict[str, str]]) -> Tuple[str, Dict[str, int]]:
        """调用AI模型"""
        
        # 构建消息列表
        messages = [{"role": "system", "content": system_prompt}]
        
        # 添加历史对话（最近5轮）
        for turn in conversation_history[-5:]:
            messages.append({"role": "user", "content": turn["user"]})
            messages.append({"role": "assistant", "content": turn["assistant"]})
        
        # 添加当前用户输入
        messages.append({"role": "user", "content": user_input})
        
        if self.ai_config["provider"] == "claude":
            return await self._call_claude(messages)
        else:
            return await self._call_openai(messages)
    
    async def _call_claude(self, messages: List[Dict[str, str]]) -> Tuple[str, Dict[str, int]]:
        """调用Claude API"""
        try:
            # Claude API需要分离system和其他消息
            system_content = ""
            claude_messages = []
            
            for msg in messages:
                if msg["role"] == "system":
                    system_content = msg["content"]
                else:
                    claude_messages.append(msg)
            
            response = await self.client.messages.create(
                model=self.ai_config["model"],
                max_tokens=self.ai_config["max_tokens"],
                temperature=self.ai_config["temperature"],
                system=system_content,
                messages=claude_messages
            )
            
            return response.content[0].text, {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens
            }
            
        except Exception as e:
            logger.error(f"Claude API调用失败: {e}")
            raise
    
    async def _call_openai(self, messages: List[Dict[str, str]]) -> Tuple[str, Dict[str, int]]:
        """调用OpenAI API"""
        try:
            completion = await self.client.chat.completions.create(
                model=self.ai_config["model"],
                messages=messages,
                max_tokens=self.ai_config["max_tokens"],
                temperature=self.ai_config["temperature"]
            )
            
            return completion.choices[0].message.content, {
                "input_tokens": completion.usage.prompt_tokens,
                "output_tokens": completion.usage.completion_tokens
            }
            
        except Exception as e:
            logger.error(f"OpenAI API调用失败: {e}")
            raise
    
    def _generate_fallback_response(self,
                                  user_input: str,
                                  memory_context: Dict[str, Any]) -> Tuple[str, Dict[str, int]]:
        """生成后备回复"""
        
        # 简单的规则生成
        responses = [
            f"感谢您的咨询：{user_input[:20]}...。根据您的情况，我建议您保持积极的心态。",
            f"关于您提到的问题，从命理角度来看，当前是一个需要谨慎的时期。",
            f"您的关注很有道理。建议您在最近多注意自己的选择和决定。",
            f"根据分析，您现在的运势整体平稳，建议保持现状并寻求新的机会。"
        ]
        
        # 根据记忆上下文调整
        if memory_context:
            if "previous_predictions" in memory_context:
                responses.append("结合之前的分析，您的运势正在按照预期发展。")
            if "verification_feedback" in memory_context:
                responses.append("感谢您的反馈，这有助于我为您提供更准确的指导。")
        
        selected_response = responses[hash(user_input) % len(responses)]
        
        return selected_response, {"fallback_tokens": len(selected_response)}
    
    async def run_conversation_test(self,
                                  session_id: str,
                                  input_sequence: List[str],
                                  memory_provider_func: Optional[callable] = None) -> List[AIResponse]:
        """运行对话测试"""
        
        if session_id not in self.active_sessions:
            raise ValueError(f"会话 {session_id} 不存在")
        
        responses = []
        
        for i, user_input in enumerate(input_sequence):
            try:
                # 获取记忆上下文
                memory_context = None
                if memory_provider_func:
                    memory_context = await memory_provider_func(session_id, i)
                
                # 生成AI回复
                response = await self.generate_ai_response(
                    session_id, 
                    user_input, 
                    memory_context
                )
                responses.append(response)
                
                # 添加延迟，模拟真实对话节奏
                await asyncio.sleep(0.5)
                
            except Exception as e:
                logger.error(f"对话测试第{i+1}轮失败: {e}")
                continue
        
        # 结束会话
        self.active_sessions[session_id].session_end_time = datetime.now().isoformat()
        
        return responses
    
    def get_session_summary(self, session_id: str) -> Optional[Dict[str, Any]]:
        """获取会话摘要"""
        if session_id not in self.active_sessions:
            return None
        
        session = self.active_sessions[session_id]
        
        # 计算统计信息
        total_response_time = sum(r.response_time for r in session.responses)
        avg_response_time = total_response_time / len(session.responses) if session.responses else 0
        
        total_input_tokens = sum(r.token_usage.get("input_tokens", 0) for r in session.responses)
        total_output_tokens = sum(r.token_usage.get("output_tokens", 0) for r in session.responses)
        
        memory_usage_count = sum(1 for r in session.responses if r.memory_context)
        
        return {
            "session_info": {
                "session_id": session_id,
                "framework_type": session.framework_type,
                "total_interactions": session.total_interactions,
                "session_duration": self._calculate_session_duration(session),
                "user_profile": session.user_profile
            },
            "performance_metrics": {
                "avg_response_time": avg_response_time,
                "total_response_time": total_response_time,
                "token_usage": {
                    "input_tokens": total_input_tokens,
                    "output_tokens": total_output_tokens,
                    "total_tokens": total_input_tokens + total_output_tokens
                }
            },
            "memory_utilization": {
                "memory_used_count": memory_usage_count,
                "memory_usage_rate": memory_usage_count / len(session.responses) if session.responses else 0
            },
            "responses": [asdict(r) for r in session.responses]
        }
    
    def _calculate_session_duration(self, session: TestSession) -> float:
        """计算会话持续时间"""
        if not session.session_end_time:
            end_time = datetime.now()
        else:
            end_time = datetime.fromisoformat(session.session_end_time)
        
        start_time = datetime.fromisoformat(session.session_start_time)
        return (end_time - start_time).total_seconds()
    
    def export_session_data(self, session_id: str, file_path: str) -> bool:
        """导出会话数据"""
        summary = self.get_session_summary(session_id)
        if not summary:
            return False
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(summary, f, ensure_ascii=False, indent=2)
            logger.info(f"会话数据已导出: {file_path}")
            return True
        except Exception as e:
            logger.error(f"导出会话数据失败: {e}")
            return False
    
    def cleanup_session(self, session_id: str) -> bool:
        """清理会话"""
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
            logger.info(f"会话已清理: {session_id}")
            return True
        return False
    
    def get_active_sessions(self) -> List[str]:
        """获取活跃会话列表"""
        return list(self.active_sessions.keys())