# Fortune Telling Memory Test Framework

基于 LangGraph 的算命师记忆框架测试系统，支持 MemU 和 Memobase 两种记忆框架的动态切换测试。

## 功能特性

- 🔮 **专业算命师 AI**: 具备传统易学知识的算命师人设
- 🧠 **智能记忆系统**: 支持 MemU 和 Memobase 记忆框架
- 🛠️ **工具调用**: AI 智能决策何时检索历史记忆
- 📝 **自动存储**: 对话结束后自动存储到记忆框架
- 🌐 **LangGraph Studio**: 支持网页界面交互测试

## 快速开始

### 1. 环境准备

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑环境变量，填入你的 API 密钥
vim .env
```

### 2. 配置环境变量

在 `.env` 文件中设置：

```bash
# AI Provider (至少需要一个)
ANTHROPIC_API_KEY=your_anthropic_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# Memory Frameworks (可选，不设置则使用模拟模式)
MEMU_API_KEY=your_memu_api_key_here
MEMU_BASE_URL=https://api.memu.so

MEMOBASE_PROJECT_URL=your_memobase_project_url_here
MEMOBASE_API_KEY=your_memobase_api_key_here

# LangGraph (可选)
LANGSMITH_API_KEY=your_langsmith_api_key_here
LANGSMITH_TRACING=true
```

### 3. 启动 LangGraph Dev

```bash
# 确保在项目目录中
cd /path/to/fortunetelling_memory_test

# 启动 LangGraph 开发服务器
langgraph dev
```

### 4. 访问 Web 界面

访问 `http://localhost:8123`，在界面中：

1. 选择 Graph: `fortuneteller`
2. 设置初始状态：
   ```json
   {
     "session_id": "test_001",
     "memory_framework": "memu",
     "messages": [],
     "user_profile": {
       "birth_info": {
         "date": "1990-05-15",
         "time": "14:30",
         "location": "北京"
       },
       "gender": "女",
       "age": 33,
       "concerns": ["事业发展", "感情关系"]
     }
   }
   ```
3. 开始对话测试

## 架构设计

### State 结构

```python
class MemoryTestState(TypedDict):
    session_id: str                    # 会话ID
    memory_framework: Literal["memu", "memobase"]  # 记忆框架
    messages: Annotated[Sequence[AnyMessage], add_messages]  # 对话历史
    user_profile: Dict[str, Any]       # 用户档案
```

### 节点流程

```
START → AI对话代理 → 记忆存储 → END
```

### 记忆工具

- `retrieve_memory`: 通用记忆检索
- `search_conversation_history`: 搜索特定话题的对话历史
- `get_user_interaction_pattern`: 分析用户交互模式
- `check_prediction_accuracy`: 检查历史预测准确性

## 测试场景

### 基础测试

1. **首次咨询**: 测试新用户的初始对话
2. **历史回顾**: 测试记忆检索功能
3. **话题连贯**: 测试多轮对话的连贯性
4. **框架切换**: 测试不同记忆框架的效果

### 示例对话

```
用户: 你好，我想了解一下我的运势
AI: 欢迎来到易学咨询！根据您的出生信息...

用户: 我最近在考虑换工作，这个决定合适吗？
AI: [调用记忆工具] 结合您之前关注的事业发展...

用户: 你之前提到我有贵人相助，能具体说说吗？
AI: [检索历史预测] 根据之前的分析...
```

## 记忆框架对比

| 特性 | MemU | Memobase |
|------|------|----------|
| 存储方式 | 对话字符串 + 分析记录 | ChatBlob 消息数组 |
| 检索能力 | 语义搜索 + 类型过滤 | 向量相似度搜索 |
| 特色功能 | 自动对话分析 | 结构化消息存储 |

## 开发说明

### 项目结构

```
fortunetelling_memory_test/
├── main.py                    # 主 Graph 定义
├── state.py                   # State 类型定义
├── nodes/                     # 节点实现
│   ├── ai_agent.py           # AI 对话代理
│   └── memory_store.py       # 记忆存储
├── tools/                     # 工具定义
│   └── memory_tools.py       # 记忆检索工具
├── memory/                    # 记忆框架适配器
│   ├── memu_adapter.py       # MemU 适配器
│   ├── memobase_adapter.py   # Memobase 适配器
│   └── message_utils.py      # 消息处理工具
└── prompts/                   # 提示模板
    └── system_prompts.py     # 算命师系统提示
```

### 添加新记忆框架

1. 在 `memory/` 目录创建新的适配器
2. 实现 `store_conversation` 和 `retrieve_memories` 方法
3. 在 `state.py` 中添加新的框架类型
4. 更新 `tools/memory_tools.py` 中的工厂函数

## 故障排除

### 常见问题

1. **API 密钥错误**: 检查 `.env` 文件中的密钥设置
2. **记忆工具调用失败**: 确保状态信息正确传递
3. **记忆存储失败**: 检查记忆框架的连接配置

### 调试模式

启用详细日志：

```python
from loguru import logger
logger.add("debug.log", level="DEBUG")
```

## 许可证

MIT License