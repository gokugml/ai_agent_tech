"""
输入模板设计器

负责设计和创建结构化的用户输入模板，为AI输入生成器提供基础
"""

import json
import random
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from jinja2 import Template, Environment, BaseLoader

from .scenario_templates import (
    InputTemplate, ScenarioTemplateLibrary, ScenarioType, 
    UserPersonality, CommunicationStyle
)


@dataclass
class UserContext:
    """用户上下文信息"""
    user_id: str
    age_range: str  # "20-25", "26-35", etc.
    gender: str  # "male", "female", "other"
    occupation: str
    location: str
    relationship_status: str
    previous_sessions: int
    personality_traits: List[str]
    concerns: List[str]
    goals: List[str]


@dataclass
class ConversationContext:
    """对话上下文信息"""
    session_type: str  # "first_time", "follow_up", "update"
    time_of_day: str  # "morning", "afternoon", "evening"
    urgency_level: int  # 1-5
    emotional_state: str  # "calm", "anxious", "excited", "sad"
    previous_outcomes: Optional[List[str]] = None
    recent_events: Optional[List[str]] = None


class TemplateVariableGenerator:
    """模板变量生成器"""
    
    def __init__(self):
        self.name_pools = {
            "male": ["张伟", "李强", "王磊", "刘洋", "陈杰", "杨阳", "赵明", "孙涛"],
            "female": ["李娜", "王丽", "张敏", "刘芳", "陈静", "杨红", "赵雪", "孙美"],
        }
        
        self.occupation_pools = [
            "软件工程师", "销售经理", "教师", "医生", "会计", "设计师", 
            "市场营销", "人力资源", "律师", "创业者", "学生", "公务员"
        ]
        
        self.location_pools = [
            "北京", "上海", "广州", "深圳", "杭州", "南京", 
            "武汉", "成都", "重庆", "西安", "青岛", "大连"
        ]
        
        self.concern_pools = {
            "career": ["升职加薪", "跳槽机会", "职业发展", "工作压力", "同事关系"],
            "relationship": ["单身脱单", "恋情发展", "婚姻和谐", "家庭矛盾", "子女教育"],
            "health": ["身体健康", "心理压力", "作息调整", "养生保健", "疾病预防"],
            "finance": ["投资理财", "买房买车", "债务压力", "收入增长", "财运提升"],
            "personal": ["个人成长", "学习进修", "兴趣发展", "人际交往", "生活平衡"]
        }
    
    def generate_user_context(self, personality: UserPersonality) -> UserContext:
        """生成用户上下文"""
        gender = random.choice(["male", "female"])
        
        context = UserContext(
            user_id=f"user_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000, 9999)}",
            age_range=random.choice(["18-25", "26-35", "36-45", "46-55", "55+"]),
            gender=gender,
            occupation=random.choice(self.occupation_pools),
            location=random.choice(self.location_pools),
            relationship_status=random.choice(["单身", "恋爱中", "已婚", "离异", "丧偶"]),
            previous_sessions=random.randint(0, 5),
            personality_traits=self._get_personality_traits(personality),
            concerns=random.sample(
                sum(self.concern_pools.values(), []), 
                k=random.randint(2, 4)
            ),
            goals=self._generate_goals()
        )
        
        return context
    
    def _get_personality_traits(self, personality: UserPersonality) -> List[str]:
        """根据性格类型生成特征"""
        trait_mapping = {
            UserPersonality.SKEPTICAL: ["理性", "谨慎", "质疑", "逻辑性强"],
            UserPersonality.TRUSTING: ["开放", "信任", "乐观", "易受影响"],
            UserPersonality.ANALYTICAL: ["分析性", "深思", "系统性", "求知欲强"],
            UserPersonality.EMOTIONAL: ["感性", "直觉", "情绪化", "重视感受"],
            UserPersonality.PRACTICAL: ["实用主义", "目标导向", "效率优先", "务实"]
        }
        
        base_traits = trait_mapping.get(personality, ["普通"])
        additional_traits = ["友善", "好奇", "积极", "独立", "有耐心"]
        
        return base_traits + random.sample(additional_traits, k=2)
    
    def _generate_goals(self) -> List[str]:
        """生成用户目标"""
        goals_pool = [
            "改善财务状况", "找到真爱", "职业突破", "健康生活", 
            "家庭和睦", "个人成长", "学习新技能", "旅行体验"
        ]
        return random.sample(goals_pool, k=random.randint(2, 3))
    
    def generate_conversation_context(self, template: InputTemplate) -> ConversationContext:
        """生成对话上下文"""
        context = ConversationContext(
            session_type="first_time" if not template.requires_memory else random.choice(["follow_up", "update"]),
            time_of_day=random.choice(["morning", "afternoon", "evening"]),
            urgency_level=random.randint(1, template.complexity_level),
            emotional_state=self._get_emotional_state(template.user_personality)
        )
        
        if template.requires_memory:
            context.previous_outcomes = self._generate_previous_outcomes()
            context.recent_events = self._generate_recent_events()
        
        return context
    
    def _get_emotional_state(self, personality: UserPersonality) -> str:
        """根据性格生成情绪状态"""
        emotion_mapping = {
            UserPersonality.SKEPTICAL: ["calm", "cautious", "analytical"],
            UserPersonality.TRUSTING: ["hopeful", "excited", "trusting"],
            UserPersonality.ANALYTICAL: ["focused", "curious", "methodical"],
            UserPersonality.EMOTIONAL: ["anxious", "excited", "sensitive"],
            UserPersonality.PRACTICAL: ["determined", "focused", "pragmatic"]
        }
        
        emotions = emotion_mapping.get(personality, ["neutral"])
        return random.choice(emotions)
    
    def _generate_previous_outcomes(self) -> List[str]:
        """生成之前的结果"""
        outcomes = [
            "工作方面的预测比较准确",
            "感情预测部分实现了",
            "财运预测还在观察中",
            "健康建议很有帮助",
            "时间预测有些偏差"
        ]
        return random.sample(outcomes, k=random.randint(1, 3))
    
    def _generate_recent_events(self) -> List[str]:
        """生成最近发生的事件"""
        events = [
            "换了新工作",
            "搬到新住址",
            "开始新恋情",
            "结束了一段关系", 
            "家里有新成员",
            "投资了新项目",
            "学习新技能",
            "健康出现小问题"
        ]
        return random.sample(events, k=random.randint(1, 2))


class InputTemplateDesigner:
    """输入模板设计器"""
    
    def __init__(self):
        self.template_library = ScenarioTemplateLibrary()
        self.variable_generator = TemplateVariableGenerator()
        self.jinja_env = Environment(loader=BaseLoader())
    
    def create_personalized_template(self, 
                                   base_template_id: str,
                                   user_context: Optional[UserContext] = None,
                                   conversation_context: Optional[ConversationContext] = None) -> Dict[str, Any]:
        """创建个性化模板"""
        
        base_template = self.template_library.get_template(base_template_id)
        if not base_template:
            raise ValueError(f"模板 {base_template_id} 不存在")
        
        # 生成上下文
        if user_context is None:
            user_context = self.variable_generator.generate_user_context(base_template.user_personality)
        
        if conversation_context is None:
            conversation_context = self.variable_generator.generate_conversation_context(base_template)
        
        # 创建个性化模板
        personalized_template = {
            "template_id": f"{base_template_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "base_template": base_template_id,
            "user_context": asdict(user_context),
            "conversation_context": asdict(conversation_context),
            "scenario_info": {
                "type": base_template.scenario_type.value,
                "personality": base_template.user_personality.value,
                "communication_style": base_template.communication_style.value,
                "complexity_level": base_template.complexity_level,
                "requires_memory": base_template.requires_memory
            },
            "context_setup": base_template.context_setup,
            "conversation_prompts": base_template.conversation_prompts,
            "expected_info_types": base_template.expected_info_types,
            "generation_timestamp": datetime.now().isoformat()
        }
        
        return personalized_template
    
    def create_template_variations(self, 
                                 base_template_id: str, 
                                 count: int = 5) -> List[Dict[str, Any]]:
        """创建模板变体"""
        variations = []
        
        for i in range(count):
            try:
                variation = self.create_personalized_template(base_template_id)
                variations.append(variation)
            except Exception as e:
                print(f"创建变体 {i} 时出错: {e}")
                continue
        
        return variations
    
    def render_template_with_variables(self, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """使用变量渲染模板"""
        
        # 提取变量
        variables = {
            **template_data["user_context"],
            **template_data["conversation_context"],
            "current_time": datetime.now().strftime("%Y年%m月%d日 %H:%M"),
            "session_count": template_data["user_context"]["previous_sessions"] + 1
        }
        
        # 渲染提示语
        rendered_prompts = []
        for prompt in template_data["conversation_prompts"]:
            try:
                template = self.jinja_env.from_string(prompt)
                rendered_prompt = template.render(**variables)
                rendered_prompts.append(rendered_prompt)
            except Exception as e:
                # 如果渲染失败，使用原始提示
                rendered_prompts.append(prompt)
        
        # 渲染上下文设置
        try:
            context_template = self.jinja_env.from_string(template_data["context_setup"])
            rendered_context = context_template.render(**variables)
        except Exception:
            rendered_context = template_data["context_setup"]
        
        # 返回渲染后的模板
        rendered_template = template_data.copy()
        rendered_template["conversation_prompts"] = rendered_prompts
        rendered_template["context_setup"] = rendered_context
        rendered_template["rendering_variables"] = variables
        
        return rendered_template
    
    def export_template(self, template_data: Dict[str, Any], file_path: str) -> bool:
        """导出模板到文件"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(template_data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"导出模板失败: {e}")
            return False
    
    def load_template(self, file_path: str) -> Optional[Dict[str, Any]]:
        """从文件加载模板"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载模板失败: {e}")
            return None
    
    def get_template_statistics(self) -> Dict[str, Any]:
        """获取模板统计信息"""
        return self.template_library.get_template_summary()