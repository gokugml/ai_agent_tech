"""
记忆框架对比测试配置文件

使用 pydantic-settings 管理配置，支持从环境变量和 .env 文件加载配置
"""

from typing import Optional
from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class MemoryTestSettings(BaseSettings):
    """记忆框架对比测试配置"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
        case_sensitive=True
    )
    
    # =============================================================================
    # 框架模式选择
    # =============================================================================
    
    MEMU_MODE: str = Field(default="selfhost", description="MemU 框架模式: cloud 或 selfhost")
    MEMOBASE_MODE: str = Field(default="selfhost", description="Memobase 框架模式: selfhost")
    
    # =============================================================================
    # MemU 配置
    # =============================================================================
    
    # MemU 云版本配置
    MEMU_CLOUD_API_KEY: Optional[str] = Field(default=None, description="MemU 云版本 API Key")
    MEMU_CLOUD_BASE_URL: str = Field(default="https://api.memu.so", description="MemU 云版本 API 地址")
    
    # MemU 自托管配置
    MEMU_SELFHOST_URL: str = Field(default="http://localhost:31010", description="MemU 自托管服务地址")
    MEMU_SELFHOST_API_KEY: str = Field(default="memu_selfhost_key", description="MemU 自托管 API Key")
    
    # OpenAI API Key（MemU 需要）
    OPENAI_API_KEY: Optional[str] = Field(default=None, description="OpenAI API Key")
    
    # =============================================================================
    # Memobase 配置
    # =============================================================================
    
    # Memobase 服务器配置
    MEMOBASE_URL: str = Field(default="http://localhost:31000", description="Memobase 服务地址")
    MEMOBASE_API_KEY: str = Field(default="secret", description="Memobase API Key")
    
    # Memobase 数据库配置（自托管时使用）
    POSTGRES_DB: str = Field(default="memobase", description="PostgreSQL 数据库名")
    POSTGRES_USER: str = Field(default="memobase", description="PostgreSQL 用户名")
    POSTGRES_PASSWORD: str = Field(default="memobase_password", description="PostgreSQL 密码")
    POSTGRES_HOST: str = Field(default="localhost", description="PostgreSQL 主机")
    POSTGRES_PORT: int = Field(default=5432, description="PostgreSQL 端口")
    
    # Memobase Redis 配置
    REDIS_HOST: str = Field(default="localhost", description="Redis 主机")
    REDIS_PORT: int = Field(default=6379, description="Redis 端口")
    REDIS_DB: int = Field(default=0, description="Redis 数据库")
    
    # =============================================================================
    # 测试配置
    # =============================================================================
    
    # 测试用户ID前缀
    TEST_USER_PREFIX: str = Field(default="test_user", description="测试用户ID前缀")
    
    # 测试并发设置
    MAX_CONCURRENT_TESTS: int = Field(default=3, description="最大并发测试数")
    
    # 测试超时设置（秒）
    TEST_TIMEOUT: int = Field(default=300, description="测试超时时间")
    
    # 是否保留测试数据（用于调试）
    KEEP_TEST_DATA: bool = Field(default=False, description="是否保留测试数据")
    
    # =============================================================================
    # 日志配置
    # =============================================================================
    
    # 日志级别
    LOG_LEVEL: str = Field(default="INFO", description="日志级别")
    
    # 日志文件路径
    LOG_FILE_PATH: str = Field(default="./logs/memory_comparison_test.log", description="日志文件路径")
    
    # =============================================================================
    # Docker 配置
    # =============================================================================
    
    # Docker 网络名称
    DOCKER_NETWORK_NAME: str = Field(default="memory_test_network", description="Docker 网络名称")
    
    # 数据卷前缀
    VOLUME_PREFIX: str = Field(default="memory_test", description="数据卷前缀")
    
    # =============================================================================
    # 计算属性
    # =============================================================================
    
    @computed_field
    @property
    def postgres_url(self) -> str:
        """PostgreSQL 连接 URL"""
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    @computed_field
    @property
    def redis_url(self) -> str:
        """Redis 连接 URL"""
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    @computed_field
    @property
    def memu_base_url(self) -> str:
        """根据模式返回 MemU 基础 URL"""
        if self.MEMU_MODE == "cloud":
            return self.MEMU_CLOUD_BASE_URL
        else:
            return self.MEMU_SELFHOST_URL
    
    @computed_field
    @property
    def memu_api_key(self) -> Optional[str]:
        """根据模式返回 MemU API Key"""
        if self.MEMU_MODE == "cloud":
            return self.MEMU_CLOUD_API_KEY
        else:
            return self.MEMU_SELFHOST_API_KEY
    
    def validate_config(self) -> bool:
        """验证配置有效性"""
        errors = []
        
        # 验证 MemU 配置
        if self.MEMU_MODE == "cloud" and not self.MEMU_CLOUD_API_KEY:
            errors.append("云模式下需要 MEMU_CLOUD_API_KEY")
        
        # 验证 OpenAI API Key
        if not self.OPENAI_API_KEY:
            errors.append("需要 OPENAI_API_KEY")
        
        # 验证模式选择
        if self.MEMU_MODE not in ["cloud", "selfhost"]:
            errors.append("MEMU_MODE 必须是 'cloud' 或 'selfhost'")
        
        if self.MEMOBASE_MODE not in ["selfhost"]:
            errors.append("MEMOBASE_MODE 目前仅支持 'selfhost'")
        
        if errors:
            raise ValueError("配置验证失败:\n" + "\n".join(f"- {error}" for error in errors))
        
        return True


# 全局配置实例
settings = MemoryTestSettings()