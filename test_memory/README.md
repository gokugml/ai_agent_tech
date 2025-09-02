# 增强版记忆系统评测框架

这是一个用于评测不同记忆系统（MemoBase 和 Memu）性能的完整测试框架，支持深度分析和多维度对比。

## 📁 项目结构

```
test_memory/
├── chats.py                           # 测试聊天数据（7个不同记忆场景）
├── test_case.py                      # 测试用例和预期结果
├── test_memobase/
│   └── memory_evaluator.py          # MemoBase记忆系统评测器（4种方法）
├── test_memu/
│   └── memu_evaluator.py            # Memu记忆系统评测器（2种方法）
├── comparative_evaluation.py         # 基础对比评测程序
├── enhanced_comparative_evaluation.py # 增强版对比评测程序
└── README.md                         # 本文档
```

## 🧠 测试的记忆能力维度

1. **时间序列偏好变化** - 测试时间关联 + 偏好追踪能力
2. **个人信息碎片化** - 测试零散信息整合能力  
3. **复杂关系网络** - 测试人际关联记忆能力
4. **算命场景专门测试** - 测试算命核心信息记忆
5. **聊天习惯分析** - 测试用户行为模式记忆
6. **情境化行为模式** - 测试场景-行为关联记忆
7. **长期人生轨迹** - 测试时间轴-事件关联记忆

## 🚀 使用方法

### 单独运行MemoBase评测（4种方法）

```bash
cd test_memory/test_memobase
uv run python memory_evaluator.py
```

### 单独运行Memu评测（2种方法）

```bash
cd test_memory/test_memu  
uv run python memu_evaluator.py
```

### 运行基础对比评测

```bash
cd test_memory
uv run python comparative_evaluation.py
```

### 运行增强版对比评测（推荐）

```bash
cd test_memory
uv run python enhanced_comparative_evaluation.py
```

## 📊 评测机制

### 检索方式对比

**MemoBase（4种方法）**:
- **Context检索**：综合性检索（通用核心方法，包含profile+event）
- **Profile检索**：专门的用户属性跟踪和更新
- **Search Event检索**：事件时间线检索，创建时间顺序记录
- **Search Event Gist检索**：精确事实检索，无需上下文

**Memu（2种方法）**:
- **Memory Items检索**：检索具体记忆内容（通用核心方法）
- **Clustered Categories检索**：基于语义相似性的自动聚类分类

### AI评分系统

使用Claude-3.5-Sonnet模型进行语义相似度评分：

- **10分**：检索内容完全匹配预期，包含所有关键信息且准确
- **8-9分**：检索内容基本匹配预期，包含大部分关键信息
- **6-7分**：检索内容部分匹配预期，包含主要信息
- **4-5分**：检索内容与预期有一定关联，但信息不完整
- **2-3分**：检索内容与预期关联度较低
- **0-1分**：检索内容与预期完全不匹配或为空

## 📈 结果输出

### 基础评测报告

1. **整体性能评分** - 各维度平均分和综合得分
2. **场景级详细结果** - 每个记忆场景的表现分析
3. **最佳/最差用例** - 识别系统优势和改进点
4. **性能评级** - A+/A/B/C/D级别评定

### 增强版评测报告（四层分析）

1. **第一层：核心方法对比** - Context vs Memory Items通用召回能力
2. **第二层：专用方法评估** - 各独有方法的场景适配度分析
3. **第三层：场景-方法矩阵** - 6种方法×7个场景的详细适配分析
4. **第四层：综合框架对比** - 整体架构优势和使用建议

### 输出文件

- `memory_evaluation_detailed.json` - MemoBase详细评测数据（4种方法）
- `memu_evaluation_detailed.json` - Memu详细评测数据（2种方法）
- `comparative_evaluation_results.json` - 基础对比评测汇总
- `enhanced_comparative_results.json` - 增强版对比评测完整数据

## ⚙️ 配置要求

### 环境依赖

```bash
# 主要依赖包
langchain>=0.3.27
langchain-anthropic>=0.3.19
memobase>=0.0.24
memu  # Memu客户端库
```

### API密钥配置

需要在环境变量或`.env`文件中配置：

```bash
ANTHROPIC_API_KEY=your_claude_api_key
MEMU_API_KEY=your_memu_api_key  
```

### MemoBase配置

```python
# 在memory_evaluator.py中配置
MEMOBASE_PROJECT_URL = "https://api.memobase.dev"
MEMOBASE_API_KEY = "your_memobase_api_key"
```

## 🔧 自定义测试

### 添加新的测试场景

1. 在`chats.py`中添加新的对话数据
2. 在`test_case.py`中添加对应的测试用例和预期结果
3. 重新运行评测程序

### 修改评分标准

在各评测器的`evaluate_similarity`方法中修改系统提示词以调整评分标准。

## 🐛 故障排除

### 常见问题

1. **导入错误** - 确保项目路径正确，所有依赖已安装
2. **API密钥错误** - 检查环境变量配置
3. **网络连接问题** - 确保能访问MemoBase和Memu的API服务
4. **内存不足** - 大量测试数据可能需要足够的内存空间

### 调试模式

在评测器代码中设置详细的日志输出来诊断问题：

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📝 评测示例

### 基础对比评测报告示例

```
🧠 记忆系统对比评测报告
================================================================================
评测时间: 2024-09-01T15:30:00
MemoBase测试用例: 21 | Memu测试用例: 21

📊 整体性能对比
------------------------------------------------------------
记忆系统        综合得分    Context/聚类  Profile/记忆项目
------------------------------------------------------------
MemoBase       7.85       8.20         7.50      
Memu          7.20       7.10         7.30      

🏆 综合性能优胜: MemoBase
📊 性能优势: 0.65 分 (6.5%)
```

### 增强版对比评测报告示例

```
🧠 增强版记忆系统对比评测报告
============================================================================
🎯 第一层分析：核心通用方法对比
MemoBase Context得分: 8.20/10
Memu Memory Items得分: 7.30/10
🏆 核心通用方法优胜: MemoBase Context

🔧 第二层分析：专用方法性能评估
1. MemoBase Search Event: 8.50/10
2. MemoBase Profile: 7.80/10  
3. MemoBase Search Event Gist: 7.20/10
4. Memu Clustered Categories: 6.90/10

🎲 第三层分析：场景-方法适配分析
场景适配度矩阵 (6种方法×7个场景)
最佳方法推荐：
• 时间序列偏好变化: MemoBase Search Event (8.9分)
• 个人信息碎片化: MemoBase Profile (8.5分)
• 复杂关系网络: MemoBase Context (8.7分)

🏗️ 第四层分析：综合框架对比
MemoBase综合得分: 7.93/10
Memu综合得分: 7.10/10
🏆 综合性能优胜: MemoBase
```

## 🎯 应用场景

这个评测框架适用于：

- **记忆系统选型** - 基于6种检索方法的深度性能对比
- **算法优化** - 评估记忆检索算法在不同场景下的改进效果  
- **产品验证** - 验证特定场景下最适合的记忆检索方法
- **性能监控** - 定期评估记忆系统各维度的服务质量
- **架构决策** - 为不同业务场景选择最优的记忆框架和方法组合

## 🔬 技术创新点

1. **多维度深度评测** - 首个支持6种不同记忆检索方法的对比框架
2. **场景-方法适配分析** - 基于理论适配度和实际表现的双重分析
3. **四层递进式分析** - 从核心对比到综合框架的全方位评估
4. **AI驱动评分** - 使用Claude-3.5-Sonnet进行语义相似度精准评估
5. **实时适应性推荐** - 为具体场景智能推荐最佳记忆检索方法

---

*最后更新: 2025-09-01 - 增强版深度对比评测系统*