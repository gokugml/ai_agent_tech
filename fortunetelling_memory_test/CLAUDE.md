# Fortune Telling Memory Test - Claude 开发记录

## 项目概述

这是一个基于 LangGraph 的算命师记忆框架测试系统，支持 MemU 和 Memobase 两种记忆框架的动态切换测试。

## 🎯 项目完成状态

**✅ 已完成的功能**：
1. 完整的 LangGraph StateGraph 架构
2. MemU 和 Memobase 记忆框架适配器
3. AI 工具调用系统（4个记忆检索工具）
4. 算命师专业人设和提示模板
5. 消息提取和对话管理系统
6. 完整的项目结构和依赖配置
7. LangGraph dev 服务器成功启动验证

## 🏗️ 架构设计要点

### State 结构（最简化设计）
```python
class MemoryTestState(TypedDict):
    session_id: str                    # 会话ID
    memory_framework: Literal["memu", "memobase"]  # 记忆框架选择
    messages: Annotated[Sequence[AnyMessage], add_messages]  # 对话历史
    user_profile: Dict[str, Any]       # 用户档案（生辰八字等）
```

### 节点流程
```
START → AI对话代理 → 记忆存储 → END
```

### 关键技术决策
1. **单Graph设计**：动态记忆框架选择，而非两个独立Graph
2. **Tool-Calling模式**：AI智能决策何时检索记忆，而非预定义输入
3. **消息提取**：从messages序列中提取最新对话对进行存储
4. **相对导入修复**：使用以项目根目录为PYTHONPATH的导入方式

## 🔧 技术实现细节

### 关键文件说明
- `main.py`: 主Graph定义，整合所有节点
- `state.py`: 状态类型定义，注意 `add_messages` 从 `langgraph.graph.message` 导入
- `nodes/ai_agent.py`: AI对话代理，绑定记忆工具
- `nodes/memory_store.py`: 记忆存储节点，自动提取对话对
- `tools/memory_tools.py`: 4个记忆检索工具供AI调用
- `memory/`: MemU和Memobase适配器实现
- `prompts/system_prompts.py`: 算命师专业提示模板

### 记忆框架API对接
**MemU**:
```python
memu_client.memorize_conversation(conversation=f"user: {user_input}\n\nassistant: {ai_response}")
```

**Memobase**:
```python
ChatBlob(messages=[
    {"role": "user", "content": user_input}, 
    {"role": "assistant", "content": ai_response}
])
```

## 🚀 启动和使用

### 启动服务器
```bash
cd /home/colsrch/programs/PixClip/ai_agent_tech/fortunetelling_memory_test
uv run langgraph dev --port 8123
```

### 访问地址
- **Studio UI**: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:8123
- **API文档**: http://127.0.0.1:8123/docs
- **Graph名称**: `fortuneteller`

### 测试初始状态
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

## 🔄 工作流程

1. **对话开始**: 用户输入问题
2. **AI处理**: 算命师AI可能调用记忆工具检索历史
3. **生成回复**: 基于记忆和专业知识回复
4. **自动存储**: 对话结束后自动存储到选定的记忆框架

## 📝 重要提醒

### 导入注意事项
- 项目使用以 `fortunetelling_memory_test` 为根目录的导入方式
- `add_messages` 必须从 `langgraph.graph.message` 导入
- 所有模块导入都是相对于项目根目录的绝对导入

### 环境配置
- 使用 `uv` 进行依赖管理
- 需要安装 `langgraph-cli[inmem]` 支持本地开发
- 环境变量配置参考 `.env.example`

### 测试验证
- 主模块导入测试: `uv run python -c "from main import graph; print('✅ 主图模块导入成功')"`
- LangGraph服务器已验证可正常启动并注册 `fortuneteller` graph

## 🎯 下一步工作

如需继续开发或测试，主要关注：
1. 在LangGraph Studio中进行实际对话测试
2. 验证记忆工具调用功能
3. 测试MemU和Memobase记忆存储功能
4. 根据测试结果优化提示模板和工具逻辑

## 🐛 已知问题

- 有一个虚拟环境警告（不影响功能）: `VIRTUAL_ENV=/home/colsrch/programs/PixClip/ai_agent_tech/memory_test/.venv` 不匹配当前项目环境
- LangGraph API版本提示有更新可用 (0.3.4 → 0.4.0)，但当前版本运行正常

---
*最后更新: 2025-08-26 - 项目构建完成，LangGraph dev服务器验证成功*