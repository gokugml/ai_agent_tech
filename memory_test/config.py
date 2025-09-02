"""
配置管理模块

管理AI回复测试框架的各种配置
"""

import os
from typing import Dict, Any, Optional, List
from pydantic_settings import BaseSettings
from pydantic import Field
from pathlib import Path
from dotenv import load_dotenv

# 加载.env文件
load_dotenv()


class OpenAIConfig(BaseSettings):
    """OpenAI配置"""
    model_config = {"extra": "ignore"}
    
    api_key: str = Field(default="", alias="OPENAI_API_KEY")
    model: str = Field(default="gpt-4", alias="OPENAI_MODEL")
    base_url: Optional[str] = Field(default=None, alias="OPENAI_BASE_URL")
    temperature: float = Field(default=0.7, alias="OPENAI_TEMPERATURE")
    max_tokens: int = Field(default=2000, alias="OPENAI_MAX_TOKENS")


class ClaudeConfig(BaseSettings):
    """Claude配置"""
    model_config = {"extra": "ignore"}
    
    api_key: str = Field(default="", alias="ANTHROPIC_API_KEY")
    model: str = Field(default="claude-3-haiku-20240307", alias="CLAUDE_MODEL")
    base_url: Optional[str] = Field(default=None, alias="CLAUDE_BASE_URL")
    max_tokens: int = Field(default=2000, alias="CLAUDE_MAX_TOKENS")
    temperature: float = Field(default=0.7, alias="CLAUDE_TEMPERATURE")


class MemuConfig(BaseSettings):
    """MemU记忆框架配置"""
    model_config = {"extra": "ignore"}
    
    api_key: str = Field(default="", alias="MEMU_API_KEY")
    base_url: str = Field(default="http://localhost:31010", alias="MEMU_BASE_URL")
    user_id: str = Field(default="memory_test_user", alias="MEMU_USER_ID")
    use_simulation: bool = Field(default=True, alias="MEMU_USE_SIMULATION")


class MemobaseConfig(BaseSettings):
    """Memobase记忆框架配置"""
    model_config = {"extra": "ignore"}
    
    project_url: str = Field(default="http://localhost:31000", alias="MEMOBASE_PROJECT_URL")
    project_id: str = Field(default="memory_test_project", alias="MEMOBASE_PROJECT_ID")
    user_id: str = Field(default="memory_test_user", alias="MEMOBASE_USER_ID")
    use_simulation: bool = Field(default=True, alias="MEMOBASE_USE_SIMULATION")


class TestConfig(BaseSettings):
    """测试配置"""
    model_config = {"extra": "ignore"}
    
    # 测试模式配置
    use_real_ai: bool = Field(default=True, alias="USE_REAL_AI")
    preferred_ai_model: str = Field(default="claude", alias="PREFERRED_AI_MODEL")  # claude | openai
    max_concurrent_tests: int = Field(default=3, alias="MAX_CONCURRENT_TESTS")
    
    # 输入生成配置
    input_template_variety: int = Field(default=5, alias="INPUT_TEMPLATE_VARIETY")
    max_conversation_rounds: int = Field(default=10, alias="MAX_CONVERSATION_ROUNDS")
    
    # 评估配置
    response_quality_threshold: float = Field(default=0.7, alias="RESPONSE_QUALITY_THRESHOLD")
    memory_utilization_threshold: float = Field(default=0.6, alias="MEMORY_UTILIZATION_THRESHOLD")
    
    # 输出配置
    save_detailed_logs: bool = Field(default=True, alias="SAVE_DETAILED_LOGS")
    export_conversation_history: bool = Field(default=True, alias="EXPORT_CONVERSATION_HISTORY")


class MemoryTestSettings(BaseSettings):
    """主配置类"""
    model_config = {
        "extra": "ignore",
        "env_file": ".env",
        "env_nested_delimiter": "__",
        "case_sensitive": False
    }
    
    # 子配置
    openai: OpenAIConfig = Field(default_factory=OpenAIConfig)
    claude: ClaudeConfig = Field(default_factory=ClaudeConfig)
    memu: MemuConfig = Field(default_factory=MemuConfig)
    memobase: MemobaseConfig = Field(default_factory=MemobaseConfig)
    test: TestConfig = Field(default_factory=TestConfig)
    
    # 基础配置
    project_name: str = Field(default="AI回复效果真实测试", ali="PROJECT_NAME")
    log_level: str = Field(default="INFO", ali="LOG_LEVEL")
    results_dir: str = Field(default="test_results", ali="RESULTS_DIR")


# 全局配置实例
settings = MemoryTestSettings()


def get_ai_client_config() -> Dict[str, Any]:
    """获取AI客户端配置"""
    if settings.test.preferred_ai_model == "claude":
        return {
            "provider": "claude",
            "api_key": settings.claude.api_key,
            "model": settings.claude.model,
            "base_url": settings.claude.base_url,
            "max_tokens": settings.claude.max_tokens,
            "temperature": settings.claude.temperature
        }
    else:
        return {
            "provider": "openai",
            "api_key": settings.openai.api_key,
            "model": settings.openai.model,
            "base_url": settings.openai.base_url,
            "max_tokens": settings.openai.max_tokens,
            "temperature": settings.openai.temperature
        }


def get_memory_framework_configs() -> Dict[str, Dict[str, Any]]:
    """获取记忆框架配置"""
    return {
        "memu": {
            "api_key": settings.memu.api_key,
            "base_url": settings.memu.base_url,
            "user_id": settings.memu.user_id,
            "use_simulation": settings.memu.use_simulation
        },
        "memobase": {
            "project_url": settings.memobase.project_url,
            "project_id": settings.memobase.project_id,
            "user_id": settings.memobase.user_id,
            "use_simulation": settings.memobase.use_simulation
        }
    }


def ensure_results_directory() -> Path:
    """确保结果目录存在"""
    results_path = Path(settings.results_dir)
    results_path.mkdir(exist_ok=True)
    return results_path