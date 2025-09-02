"""
算命师记忆测试配置文件

使用 pydantic-settings 管理配置，支持从环境变量和 .env 文件加载配置
"""

from typing import Literal

from pydantic import AnyUrl, Field, SecretStr, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class FortunetellingSettings(BaseSettings):
    """算命师记忆测试配置"""

    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True, extra="ignore", case_sensitive=True)

    # =============================================================================
    # AI 服务配置
    # =============================================================================

    ANTHROPIC_API_KEY: SecretStr | None = Field(default=None, description="Anthropic Claude API 密钥")
    ANTHROPIC_BASE_URL: str = Field(default=None, description="Anthropic Claude Base URL")

    OPENAI_API_KEY: SecretStr | None = Field(default=None, description="OpenAI API 密钥")
    OPENAI_BASE_URL: str = Field(None, description="OpenAI Base URL")

    # AI 模型配置
    ANTHROPIC_MODEL: str = Field(default="claude-3-sonnet-20240229", description="Claude 模型名称")

    OPENAI_MODEL: str = Field(default="gpt-4", description="OpenAI 模型名称")

    AI_TEMPERATURE: float = Field(default=0.7, description="AI 模型温度参数")

    AI_MAX_TOKENS: int = Field(default=2000, description="AI 回复最大 token 数")

    # =============================================================================
    # MemU 记忆框架配置
    # =============================================================================

    MEMU_API_KEY: str | None = Field(default=None, description="MemU API 密钥")

    MEMU_BASE_URL: str = Field(default="https://api.memu.so", description="MemU 服务基础 URL")

    MEMU_USE_SIMULATION: bool = Field(default=True, description="是否使用 MemU 模拟模式")

    MEMU_USER_NAME: str = Field(default="Fortune Telling User", description="MemU 用户名")

    MEMU_AGENT_ID: str = Field(default="fortuneteller001", description="MemU 代理 ID")

    MEMU_AGENT_NAME: str = Field(default="AI Fortune Teller", description="MemU 代理名称")

    # =============================================================================
    # Memobase 记忆框架配置
    # =============================================================================

    MEMOBASE_PROJECT_URL: str = Field(default="http://localhost:31000", description="Memobase 项目 URL")

    MEMOBASE_API_KEY: str = Field(default="memobase_test_key", description="Memobase API 密钥")

    MEMOBASE_USE_SIMULATION: bool = Field(default=True, description="是否使用 Memobase 模拟模式")

    # =============================================================================
    # LangGraph 服务器配置
    # =============================================================================

    LANGGRAPH_PORT: int = Field(default=8123, description="LangGraph 开发服务器端口")

    LANGGRAPH_HOST: str = Field(default="127.0.0.1", description="LangGraph 开发服务器主机")

    # =============================================================================
    # 记忆配置
    # =============================================================================

    MEMORY_RETRIEVAL_LIMIT: int = Field(default=5, description="记忆检索结果数量限制")

    MEMORY_RELEVANCE_THRESHOLD: float = Field(default=0.1, description="记忆相关性分数阈值")

    # =============================================================================
    # 日志配置
    # =============================================================================

    LOG_LEVEL: str = Field(default="INFO", description="日志级别")

    LOG_FORMAT: str = Field(
        default="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        description="日志格式",
    )

    # =============================================================================
    # 开发配置
    # =============================================================================

    DEBUG_MODE: bool = Field(default=False, description="是否启用调试模式")

    SAVE_CONVERSATION_HISTORY: bool = Field(default=True, description="是否保存对话历史")
    
    MONGO_DB: str
    MONGO_HOST: str = "127.0.0.1"
    MONGO_PORT: int = 27017
    MONGO_USER: str
    MONGO_PASSWORD: str
    MONGO_AUTH_SOURCE: str = "admin"

    @computed_field
    @property
    def mongo_uri(self) -> AnyUrl:
        return AnyUrl.build(
            scheme="mongodb",
            username=self.MONGO_USER,
            password=self.MONGO_PASSWORD,
            host=self.MONGO_HOST,
            port=self.MONGO_PORT,
            path=self.MONGO_DB,
            query=f"authSource={self.MONGO_AUTH_SOURCE}",
        )

    # =============================================================================
    # 计算属性
    # =============================================================================

    @computed_field
    @property
    def preferred_ai_provider(self) -> Literal["anthropic", "openai", "none"]:
        """根据可用 API 密钥确定首选 AI 提供商"""
        if self.ANTHROPIC_API_KEY:
            return "anthropic"
        elif self.OPENAI_API_KEY:
            return "openai"
        else:
            return "none"

    @computed_field
    @property
    def langgraph_dev_url(self) -> str:
        """LangGraph 开发服务器完整 URL"""
        return f"http://{self.LANGGRAPH_HOST}:{self.LANGGRAPH_PORT}"

    @computed_field
    @property
    def studio_url(self) -> str:
        """LangGraph Studio URL"""
        return f"https://smith.langchain.com/studio/?baseUrl={self.langgraph_dev_url}"

    # =============================================================================
    # 配置验证方法
    # =============================================================================

    def validate_ai_config(self) -> bool:
        """验证 AI 配置有效性"""
        errors = []

        # 检查是否至少有一个 AI API 密钥
        if not self.ANTHROPIC_API_KEY and not self.OPENAI_API_KEY:
            errors.append("需要至少一个 AI API 密钥 (ANTHROPIC_API_KEY 或 OPENAI_API_KEY)")

        # 验证温度参数
        if not (0.0 <= self.AI_TEMPERATURE <= 2.0):
            errors.append("AI_TEMPERATURE 必须在 0.0 到 2.0 之间")

        # 验证最大 token 数
        if self.AI_MAX_TOKENS <= 0:
            errors.append("AI_MAX_TOKENS 必须大于 0")

        if errors:
            raise ValueError("AI 配置验证失败:\n" + "\n".join(f"- {error}" for error in errors))

        return True

    def validate_memory_config(self) -> bool:
        """验证记忆框架配置有效性"""
        errors = []

        # 验证记忆检索限制
        if self.MEMORY_RETRIEVAL_LIMIT <= 0:
            errors.append("MEMORY_RETRIEVAL_LIMIT 必须大于 0")

        # 验证相关性阈值
        if not (0.0 <= self.MEMORY_RELEVANCE_THRESHOLD <= 1.0):
            errors.append("MEMORY_RELEVANCE_THRESHOLD 必须在 0.0 到 1.0 之间")

        if errors:
            raise ValueError("记忆配置验证失败:\n" + "\n".join(f"- {error}" for error in errors))

        return True

    def validate_server_config(self) -> bool:
        """验证服务器配置有效性"""
        errors = []

        # 验证端口号
        if not (1 <= self.LANGGRAPH_PORT <= 65535):
            errors.append("LANGGRAPH_PORT 必须在 1 到 65535 之间")

        # 验证日志级别
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.LOG_LEVEL.upper() not in valid_log_levels:
            errors.append(f"LOG_LEVEL 必须是以下之一: {', '.join(valid_log_levels)}")

        if errors:
            raise ValueError("服务器配置验证失败:\n" + "\n".join(f"- {error}" for error in errors))

        return True

    def validate_all(self) -> bool:
        """验证所有配置"""
        self.validate_ai_config()
        self.validate_memory_config()
        self.validate_server_config()
        return True

    # =============================================================================
    # 辅助方法
    # =============================================================================

    def get_ai_api_key(self) -> str | None:
        """获取可用的 AI API 密钥"""
        if self.preferred_ai_provider == "anthropic" and self.ANTHROPIC_API_KEY:
            return self.ANTHROPIC_API_KEY.get_secret_value()
        elif self.preferred_ai_provider == "openai" and self.OPENAI_API_KEY:
            return self.OPENAI_API_KEY.get_secret_value()
        return None

    def get_ai_model(self) -> str:
        """获取对应的 AI 模型名称"""
        if self.preferred_ai_provider == "anthropic":
            return self.ANTHROPIC_MODEL
        elif self.preferred_ai_provider == "openai":
            return self.OPENAI_MODEL
        else:
            return "unknown"

    def is_memory_simulation_mode(self, framework: Literal["memu", "memobase"]) -> bool:
        """检查指定记忆框架是否为模拟模式"""
        if framework == "memu":
            return self.MEMU_USE_SIMULATION
        elif framework == "memobase":
            return self.MEMOBASE_USE_SIMULATION
        return True


# 全局配置实例
settings = FortunetellingSettings()
