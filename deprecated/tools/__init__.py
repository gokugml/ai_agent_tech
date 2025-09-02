"""
兴趣爱好分析工具集
"""

from .sexual_selection import sexual_selection_tool
from .male_tools import man_spots_tool, man_study_tool, analyze_male_interests
from .female_tools import woman_spots_tool, woman_activity_tool, woman_study_tool, analyze_female_interests

__all__ = [
    'sexual_selection_tool',
    'man_spots_tool', 
    'man_study_tool',
    'woman_spots_tool',
    'woman_activity_tool', 
    'woman_study_tool',
    'analyze_male_interests',
    'analyze_female_interests'
]