"""
AI输入生成器

使用AI模型根据模板和上下文生成更真实、多样化的用户输入
"""

import asyncio
import json
import random
from typing import Dict, List, Any, Optional, Union, AsyncGenerator
from dataclasses import dataclass
from datetime import datetime
import re

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
class GeneratedInput:
    """生成的输入数据类"""
    input_id: str
    template_id: str
    user_message: str
    context_info: Dict[str, Any]
    metadata: Dict[str, Any]
    generation_timestamp: str
    confidence_score: float  # 0-1，生成质量置信度


class AIInputGenerator:
    """AI输入生成器"""
    
    def __init__(self):
        self.ai_config = get_ai_client_config()
        self.client = None
        self._initialize_client()
        
        # 生成提示模板
        self.generation_prompts = {
            "user_input": self._get_user_input_generation_prompt(),
            "conversation_continuation": self._get_conversation_continuation_prompt(),
            "style_adaptation": self._get_style_adaptation_prompt()
        }
    
    def _initialize_client(self) -> None:
        """初始化AI客户端"""
        try:
            if self.ai_config["provider"] == "claude" and ANTHROPIC_AVAILABLE:
                claude_kwargs = {"api_key": self.ai_config["api_key"]}
                if self.ai_config.get("base_url"):
                    claude_kwargs["base_url"] = self.ai_config["base_url"]
                self.client = AsyncAnthropic(**claude_kwargs)
                logger.info("Claude客户端初始化成功")
            elif self.ai_config["provider"] == "openai" and OPENAI_AVAILABLE:
                self.client = AsyncOpenAI(
                    api_key=self.ai_config["api_key"],
                    base_url=self.ai_config.get("base_url")
                )
                logger.info("OpenAI客户端初始化成功")
            else:
                logger.warning("AI客户端初始化失败，将使用模拟模式")
                self.client = None
        except Exception as e:
            logger.error(f"AI客户端初始化错误: {e}")
            self.client = None
    
    def _get_user_input_generation_prompt(self) -> str:
        """获取用户输入生成提示"""
        return '''你是一个专业的用户行为模拟专家。请根据提供的用户背景和场景模板，生成真实、自然的用户输入。

用户背景信息：
- 性格类型：{personality}
- 沟通风格：{communication_style}
- 年龄范围：{age_range}
- 职业：{occupation}
- 关注点：{concerns}
- 情绪状态：{emotional_state}

场景设置：
{context_setup}

参考提示语：
{reference_prompts}

请生成3-5个不同的用户输入，要求：
1. 符合用户的性格特征和沟通风格
2. 自然、真实，避免模式化
3. 体现用户的当前情绪和关注点
4. 每个输入都略有不同，增加多样性
5. 适合算命咨询的场景

请严格按照以下JSON格式输出，不要添加任何其他文字：

{
  "generated_inputs": [
    {
      "message": "用户消息内容",
      "style_indicators": ["直接", "礼貌", "急切"],
      "emotional_tone": "neutral",
      "complexity_level": 3
    },
    {
      "message": "另一个用户消息",
      "style_indicators": ["详细", "礼貌"],
      "emotional_tone": "anxious",
      "complexity_level": 2
    }
  ]
}'''
    
    def _get_conversation_continuation_prompt(self) -> str:
        """获取对话续写提示"""
        return '''根据之前的对话历史和用户特征，生成用户的后续输入。

对话历史：
{conversation_history}

用户特征：
- 性格：{personality}
- 沟通风格：{communication_style}
- 当前情绪：{emotional_state}

上一轮AI回复：
{last_ai_response}

请生成用户对AI回复的自然响应，要求：
1. 符合用户性格和对话逻辑
2. 可能包含进一步的问题或澄清
3. 体现用户对AI回复的反应
4. 推进对话向更深层次发展

输出JSON格式的用户消息。'''
    
    def _get_style_adaptation_prompt(self) -> str:
        """获取风格适应提示"""
        return '''根据用户的反馈，调整生成输入的风格。

用户反馈：{user_feedback}
当前风格：{current_style}
目标调整：{adjustment_target}

请生成调整后的用户输入，体现风格变化。'''
    
    async def generate_user_input(self, 
                                template_data: Dict[str, Any], 
                                count: int = 3) -> List[GeneratedInput]:
        """生成用户输入"""
        
        if not self.client:
            return self._generate_fallback_inputs(template_data, count)
        
        try:
            # 准备提示
            prompt = self._prepare_generation_prompt(template_data)
            
            # 调用AI生成
            if self.ai_config["provider"] == "claude":
                response = await self._generate_with_claude(prompt)
            else:
                response = await self._generate_with_openai(prompt)
            
            # 解析响应
            generated_inputs = self._parse_ai_response(response, template_data)
            
            return generated_inputs[:count]
            
        except Exception as e:
            logger.error(f"AI生成用户输入失败: {e}")
            return self._generate_fallback_inputs(template_data, count)
    
    def _prepare_generation_prompt(self, template_data: Dict[str, Any]) -> str:
        """准备生成提示"""
        user_context = template_data["user_context"]
        conversation_context = template_data["conversation_context"]
        scenario_info = template_data["scenario_info"]
        
        return self.generation_prompts["user_input"].format(
            personality=scenario_info["personality"],
            communication_style=scenario_info["communication_style"],
            age_range=user_context["age_range"],
            occupation=user_context["occupation"],
            concerns=", ".join(user_context["concerns"]),
            emotional_state=conversation_context["emotional_state"],
            context_setup=template_data["context_setup"],
            reference_prompts="\\n".join(template_data["conversation_prompts"])
        )
    
    async def _generate_with_claude(self, prompt: str) -> str:
        """使用Claude生成"""
        try:
            message = await self.client.messages.create(
                model=self.ai_config["model"],
                max_tokens=self.ai_config["max_tokens"],
                temperature=self.ai_config["temperature"],
                messages=[{"role": "user", "content": prompt}]
            )
            return message.content[0].text
        except Exception as e:
            logger.error(f"Claude生成失败: {e}")
            raise
    
    async def _generate_with_openai(self, prompt: str) -> str:
        """使用OpenAI生成"""
        try:
            completion = await self.client.chat.completions.create(
                model=self.ai_config["model"],
                messages=[{"role": "user", "content": prompt}],
                max_tokens=self.ai_config["max_tokens"],
                temperature=self.ai_config["temperature"]
            )
            return completion.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI生成失败: {e}")
            raise
    
    def _parse_ai_response(self, response: str, template_data: Dict[str, Any]) -> List[GeneratedInput]:
        """解析AI响应"""
        generated_inputs = []
        
        try:
            # 多种方式尝试解析JSON
            data = {}
            
            # 方法1: 直接尝试解析整个响应
            try:
                data = json.loads(response.strip())
                logger.debug("成功直接解析JSON响应")
            except json.JSONDecodeError:
                # 方法2: 提取JSON块
                if "{" in response and "}" in response:
                    # 找到最外层的JSON结构
                    json_patterns = [
                        r'\{[^{}]*"generated_inputs"[^{}]*\[[^\]]*\][^{}]*\}',  # 完整结构
                        r'\{.*?"generated_inputs".*?\}',  # 带数组的结构
                        r'\{.*?\}',  # 任意JSON结构
                    ]
                    
                    for pattern in json_patterns:
                        json_match = re.search(pattern, response, re.DOTALL)
                        if json_match:
                            try:
                                json_str = json_match.group(0)
                                data = json.loads(json_str)
                                logger.debug(f"使用模式 {pattern} 成功解析JSON")
                                break
                            except json.JSONDecodeError:
                                continue
                
                # 方法3: 如果仍然失败，尝试修复常见的JSON问题
                if not data and "{" in response:
                    try:
                        # 提取可能的JSON内容并尝试修复
                        json_content = response[response.find("{"):response.rfind("}")+1]
                        # 移除可能的注释和多余空行
                        json_content = re.sub(r'//.*?\n', '', json_content)
                        json_content = re.sub(r'/\*.*?\*/', '', json_content, flags=re.DOTALL)
                        data = json.loads(json_content)
                        logger.debug("通过修复解析JSON成功")
                    except:
                        logger.warning(f"所有JSON解析方法都失败，响应内容: {response[:200]}...")
            
            # 处理解析后的数据
            if data and "generated_inputs" in data:
                for i, input_data in enumerate(data.get("generated_inputs", [])):
                    generated_input = GeneratedInput(
                        input_id=f"{template_data['template_id']}_gen_{i}_{datetime.now().strftime('%H%M%S')}",
                        template_id=template_data["template_id"],
                        user_message=input_data["message"],
                        context_info={
                            "style_indicators": input_data.get("style_indicators", []),
                            "emotional_tone": input_data.get("emotional_tone", "neutral"),
                            "complexity_level": input_data.get("complexity_level", 3)
                        },
                        metadata={
                            "generation_method": "ai_generated",
                            "ai_provider": self.ai_config["provider"],
                            "template_base": template_data.get("base_template", "unknown")
                        },
                        generation_timestamp=datetime.now().isoformat(),
                        confidence_score=0.8
                    )
                    generated_inputs.append(generated_input)
        
        except Exception as e:
            logger.error(f"解析AI响应失败: {e}")
            logger.debug(f"原始响应内容: {response}")
        
        # 如果解析失败，尝试简单提取
        if not generated_inputs:
            logger.warning("JSON解析完全失败，使用简单提取方法")
            generated_inputs = self._extract_simple_responses(response, template_data)
        
        return generated_inputs
    
    def _extract_simple_responses(self, response: str, template_data: Dict[str, Any]) -> List[GeneratedInput]:
        """简单提取响应"""
        lines = response.split('\\n')
        messages = []
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('-'):
                # 简单清理
                if '"' in line:
                    line = line.strip('"')
                if line.endswith('.') or line.endswith('。'):
                    messages.append(line)
        
        generated_inputs = []
        for i, message in enumerate(messages[:3]):  # 最多取3个
            generated_input = GeneratedInput(
                input_id=f"{template_data['template_id']}_simple_{i}_{datetime.now().strftime('%H%M%S')}",
                template_id=template_data["template_id"],
                user_message=message,
                context_info={"extraction_method": "simple"},
                metadata={"generation_method": "simple_extraction"},
                generation_timestamp=datetime.now().isoformat(),
                confidence_score=0.6
            )
            generated_inputs.append(generated_input)
        
        return generated_inputs
    
    def _generate_fallback_inputs(self, template_data: Dict[str, Any], count: int) -> List[GeneratedInput]:
        """生成后备输入（当AI不可用时）"""
        
        base_prompts = template_data["conversation_prompts"]
        user_context = template_data["user_context"]
        conversation_context = template_data["conversation_context"]
        
        generated_inputs = []
        
        for i in range(min(count, len(base_prompts))):
            # 基于模板进行简单变化
            base_message = base_prompts[i]
            
            # 添加个性化元素
            if conversation_context["emotional_state"] == "anxious":
                base_message = f"我有点担心，{base_message.lower()}"
            elif conversation_context["emotional_state"] == "excited":
                base_message = f"我很期待，{base_message}"
            
            # 添加职业相关内容
            if "工作" in base_message or "职业" in base_message:
                base_message += f"（我是{user_context['occupation']}）"
            
            generated_input = GeneratedInput(
                input_id=f"{template_data['template_id']}_fallback_{i}_{datetime.now().strftime('%H%M%S')}",
                template_id=template_data["template_id"],
                user_message=base_message,
                context_info={
                    "generation_method": "template_based",
                    "emotional_adjustment": conversation_context["emotional_state"]
                },
                metadata={
                    "generation_method": "fallback",
                    "user_occupation": user_context["occupation"]
                },
                generation_timestamp=datetime.now().isoformat(),
                confidence_score=0.5
            )
            generated_inputs.append(generated_input)
        
        return generated_inputs
    
    async def generate_conversation_continuation(self,
                                              conversation_history: List[Dict[str, str]],
                                              user_context: Dict[str, Any],
                                              last_ai_response: str) -> Optional[GeneratedInput]:
        """生成对话续写"""
        
        if not self.client:
            return self._generate_fallback_continuation(conversation_history, user_context, last_ai_response)
        
        try:
            # 准备续写提示
            prompt = self._prepare_continuation_prompt(conversation_history, user_context, last_ai_response)
            
            # 生成续写
            if self.ai_config["provider"] == "claude":
                response = await self._generate_with_claude(prompt)
            else:
                response = await self._generate_with_openai(prompt)
            
            # 解析为单个输入
            generated_input = GeneratedInput(
                input_id=f"continuation_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000, 9999)}",
                template_id="conversation_continuation",
                user_message=response.strip().strip('"'),
                context_info={"type": "continuation"},
                metadata={"generation_method": "ai_continuation"},
                generation_timestamp=datetime.now().isoformat(),
                confidence_score=0.7
            )
            
            return generated_input
            
        except Exception as e:
            logger.error(f"生成对话续写失败: {e}")
            return self._generate_fallback_continuation(conversation_history, user_context, last_ai_response)
    
    def _prepare_continuation_prompt(self, 
                                   conversation_history: List[Dict[str, str]],
                                   user_context: Dict[str, Any], 
                                   last_ai_response: str) -> str:
        """准备续写提示"""
        
        history_text = "\\n".join([
            f"用户: {turn['user']}\\n回复: {turn['assistant']}"
            for turn in conversation_history[-3:]  # 只取最近3轮对话
        ])
        
        return self.generation_prompts["conversation_continuation"].format(
            conversation_history=history_text,
            personality=user_context.get("personality_traits", ["普通"])[0],
            communication_style=user_context.get("communication_style", "直接"),
            emotional_state=user_context.get("emotional_state", "neutral"),
            last_ai_response=last_ai_response
        )
    
    def _generate_fallback_continuation(self,
                                      conversation_history: List[Dict[str, str]],
                                      user_context: Dict[str, Any],
                                      last_ai_response: str) -> GeneratedInput:
        """生成后备续写"""
        
        # 简单的规则生成
        fallback_responses = [
            "好的，我明白了。还有什么需要注意的吗？",
            "这个说法很有道理。那我接下来应该怎么做？",
            "谢谢您的分析。我想再了解一些细节。",
            "听起来不错。您能再具体说说吗？",
            "我觉得您说得对。还有其他建议吗？"
        ]
        
        message = random.choice(fallback_responses)
        
        return GeneratedInput(
            input_id=f"fallback_continuation_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            template_id="fallback_continuation",
            user_message=message,
            context_info={"type": "fallback_continuation"},
            metadata={"generation_method": "rule_based"},
            generation_timestamp=datetime.now().isoformat(),
            confidence_score=0.4
        )
    
    async def batch_generate_inputs(self, 
                                  template_list: List[Dict[str, Any]], 
                                  inputs_per_template: int = 3) -> Dict[str, List[GeneratedInput]]:
        """批量生成输入"""
        
        results = {}
        
        # 控制并发数
        semaphore = asyncio.Semaphore(3)
        
        async def generate_for_template(template_data):
            async with semaphore:
                template_id = template_data["template_id"]
                try:
                    inputs = await self.generate_user_input(template_data, inputs_per_template)
                    return template_id, inputs
                except Exception as e:
                    logger.error(f"批量生成模板 {template_id} 失败: {e}")
                    return template_id, []
        
        # 并发生成
        tasks = [generate_for_template(template) for template in template_list]
        completed_tasks = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 收集结果
        for result in completed_tasks:
            if isinstance(result, Exception):
                logger.error(f"批量任务执行异常: {result}")
                continue
            
            template_id, inputs = result
            results[template_id] = inputs
        
        return results