"""
场景模板定义

定义各种测试场景的模板结构，用于生成多样化的测试输入
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum


class ScenarioType(Enum):
    """场景类型枚举"""
    DIVINATION_CONSULTATION = "divination_consultation"  # 算命咨询
    FOLLOW_UP_SESSION = "follow_up_session"  # 回访咨询
    FEEDBACK_DISCUSSION = "feedback_discussion"  # 反馈讨论
    LIFE_UPDATE = "life_update"  # 生活更新
    EMOTIONAL_SUPPORT = "emotional_support"  # 情感支持


class UserPersonality(Enum):
    """用户性格类型"""
    SKEPTICAL = "skeptical"  # 怀疑型
    TRUSTING = "trusting"  # 信任型
    ANALYTICAL = "analytical"  # 分析型
    EMOTIONAL = "emotional"  # 情感型
    PRACTICAL = "practical"  # 实用型


class CommunicationStyle(Enum):
    """沟通风格"""
    DIRECT = "direct"  # 直接
    DETAILED = "detailed"  # 详细
    CASUAL = "casual"  # 随意
    FORMAL = "formal"  # 正式
    INTERACTIVE = "interactive"  # 互动


@dataclass
class InputTemplate:
    """输入模板类"""
    template_id: str
    scenario_type: ScenarioType
    user_personality: UserPersonality
    communication_style: CommunicationStyle
    context_setup: str
    conversation_prompts: List[str]
    expected_info_types: List[str]
    complexity_level: int  # 1-5，复杂度等级
    requires_memory: bool  # 是否需要历史记忆
    
    def __str__(self) -> str:
        return f"Template({self.template_id}, {self.scenario_type.value}, {self.complexity_level})"


class ScenarioTemplateLibrary:
    """场景模板库"""
    
    def __init__(self):
        self.templates: Dict[str, InputTemplate] = {}
        self._initialize_templates()
    
    def _initialize_templates(self) -> None:
        """初始化预定义模板"""
        
        # 1. 初次算命咨询模板
        self.templates["first_divination_basic"] = InputTemplate(
            template_id="first_divination_basic",
            scenario_type=ScenarioType.DIVINATION_CONSULTATION,
            user_personality=UserPersonality.TRUSTING,
            communication_style=CommunicationStyle.DIRECT,
            context_setup="用户第一次寻求算命服务，对算命略有了解但不深入。希望了解自己的整体运势。",
            conversation_prompts=[
                "我想算一下我的运势",
                "听说算命很准，想试试看",
                "朋友推荐我来算命，说您很厉害",
                "我最近有点迷茫，想看看未来的方向"
            ],
            expected_info_types=["basic_info", "birth_date", "current_concerns", "life_goals"],
            complexity_level=2,
            requires_memory=False
        )
        
        # 2. 怀疑型用户咨询模板
        self.templates["skeptical_consultation"] = InputTemplate(
            template_id="skeptical_consultation",
            scenario_type=ScenarioType.DIVINATION_CONSULTATION,
            user_personality=UserPersonality.SKEPTICAL,
            communication_style=CommunicationStyle.DETAILED,
            context_setup="用户对算命持怀疑态度，想要测试算命师的能力。会提出质疑和要求证明。",
            conversation_prompts=[
                "算命真的有科学依据吗？",
                "你能证明你的预测是准确的吗？",
                "我之前算过命，但都不准，你有什么不同？",
                "如果你算错了，会怎么处理？"
            ],
            expected_info_types=["skeptical_concerns", "past_experiences", "verification_requests"],
            complexity_level=4,
            requires_memory=False
        )
        
        # 3. 回访咨询模板
        self.templates["follow_up_session"] = InputTemplate(
            template_id="follow_up_session",
            scenario_type=ScenarioType.FOLLOW_UP_SESSION,
            user_personality=UserPersonality.TRUSTING,
            communication_style=CommunicationStyle.DETAILED,
            context_setup="用户之前有过算命经历，现在回来更新情况或寻求新的指导。",
            conversation_prompts=[
                "上次您说的事情真的发生了！",
                "上次的预测有些准确，但有些没发生",
                "我按照您的建议做了，现在想看看接下来怎么办",
                "距离上次算命已经过了几个月，想再看看现在的情况"
            ],
            expected_info_types=["previous_predictions", "verification_status", "life_changes", "new_concerns"],
            complexity_level=3,
            requires_memory=True
        )
        
        # 4. 生活重大变化更新模板
        self.templates["major_life_update"] = InputTemplate(
            template_id="major_life_update",
            scenario_type=ScenarioType.LIFE_UPDATE,
            user_personality=UserPersonality.EMOTIONAL,
            communication_style=CommunicationStyle.CASUAL,
            context_setup="用户经历了重大生活变化，如换工作、结婚、搬家等，想了解新阶段的运势。",
            conversation_prompts=[
                "我最近换了工作，想看看这个决定对我好不好",
                "我刚刚结婚了，想算算我们的婚姻运势",
                "我搬到了新城市，不知道这里对我的运势有什么影响",
                "我刚买了房子，这是个好时机吗？"
            ],
            expected_info_types=["major_changes", "timing_questions", "future_implications", "relationship_impacts"],
            complexity_level=3,
            requires_memory=True
        )
        
        # 5. 情感支持咨询模板
        self.templates["emotional_support"] = InputTemplate(
            template_id="emotional_support",
            scenario_type=ScenarioType.EMOTIONAL_SUPPORT,
            user_personality=UserPersonality.EMOTIONAL,
            communication_style=CommunicationStyle.INTERACTIVE,
            context_setup="用户正在经历情感困扰，寻求心理慰藉和人生指导。",
            conversation_prompts=[
                "我最近心情很低落，感觉什么都不顺",
                "我和男/女朋友分手了，很痛苦",
                "工作压力太大，我快撑不住了",
                "家里有矛盾，我不知道该怎么办"
            ],
            expected_info_types=["emotional_state", "relationship_issues", "stress_sources", "support_needs"],
            complexity_level=4,
            requires_memory=True
        )
        
        # 6. 详细分析型咨询模板
        self.templates["detailed_analysis"] = InputTemplate(
            template_id="detailed_analysis",
            scenario_type=ScenarioType.DIVINATION_CONSULTATION,
            user_personality=UserPersonality.ANALYTICAL,
            communication_style=CommunicationStyle.FORMAL,
            context_setup="用户希望得到深入、详细的分析，对八字、风水等有一定了解。",
            conversation_prompts=[
                "请帮我详细分析一下我的八字命盘",
                "我想了解我的五行缺什么，如何补运",
                "请看看我的流年运势，重点分析事业和财运",
                "我对玄学有些了解，希望得到专业的分析"
            ],
            expected_info_types=["detailed_birth_info", "specific_analysis_requests", "knowledge_level", "focus_areas"],
            complexity_level=5,
            requires_memory=False
        )
        
        # 7. 实用型咨询模板
        self.templates["practical_guidance"] = InputTemplate(
            template_id="practical_guidance",
            scenario_type=ScenarioType.DIVINATION_CONSULTATION,
            user_personality=UserPersonality.PRACTICAL,
            communication_style=CommunicationStyle.DIRECT,
            context_setup="用户重视实用性，希望得到具体的建议和指导，而不是抽象的描述。",
            conversation_prompts=[
                "我想知道什么时候换工作比较好",
                "请告诉我如何改善我的财运",
                "我应该投资什么项目？",
                "什么时候结婚对我最有利？"
            ],
            expected_info_types=["specific_questions", "timeline_requests", "actionable_advice", "decision_making"],
            complexity_level=3,
            requires_memory=False
        )
        
        # 8. 反馈讨论模板
        self.templates["feedback_discussion"] = InputTemplate(
            template_id="feedback_discussion",
            scenario_type=ScenarioType.FEEDBACK_DISCUSSION,
            user_personality=UserPersonality.ANALYTICAL,
            communication_style=CommunicationStyle.DETAILED,
            context_setup="用户对之前的预测进行验证和讨论，提供详细的反馈信息。",
            conversation_prompts=[
                "上次您说我会有贵人相助，确实遇到了好心人",
                "您预测的时间有点偏差，实际发生得更早一些",
                "有些预测很准，但有些完全没发生",
                "我想详细讨论一下预测的准确性"
            ],
            expected_info_types=["accuracy_feedback", "timing_verification", "detailed_outcomes", "improvement_suggestions"],
            complexity_level=4,
            requires_memory=True
        )
    
    def get_template(self, template_id: str) -> Optional[InputTemplate]:
        """获取指定模板"""
        return self.templates.get(template_id)
    
    def get_templates_by_type(self, scenario_type: ScenarioType) -> List[InputTemplate]:
        """根据场景类型获取模板"""
        return [template for template in self.templates.values() 
                if template.scenario_type == scenario_type]
    
    def get_templates_by_complexity(self, min_level: int = 1, max_level: int = 5) -> List[InputTemplate]:
        """根据复杂度获取模板"""
        return [template for template in self.templates.values()
                if min_level <= template.complexity_level <= max_level]
    
    def get_templates_requiring_memory(self) -> List[InputTemplate]:
        """获取需要记忆的模板"""
        return [template for template in self.templates.values() if template.requires_memory]
    
    def get_all_template_ids(self) -> List[str]:
        """获取所有模板ID"""
        return list(self.templates.keys())
    
    def get_template_summary(self) -> Dict[str, Any]:
        """获取模板库概要信息"""
        return {
            "total_templates": len(self.templates),
            "scenario_types": list(set(t.scenario_type.value for t in self.templates.values())),
            "personality_types": list(set(t.user_personality.value for t in self.templates.values())),
            "communication_styles": list(set(t.communication_style.value for t in self.templates.values())),
            "complexity_distribution": {
                level: len([t for t in self.templates.values() if t.complexity_level == level])
                for level in range(1, 6)
            },
            "memory_required": len(self.get_templates_requiring_memory())
        }