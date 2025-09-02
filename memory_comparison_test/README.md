# 记忆框架对比测试项目

## 项目概述

本项目用于对比测试 **memu** 和 **memobase** 两个记忆框架在算命AI场景下的表现。测试重点关注三个核心能力：

1. **聊天风格学习** - AI学习并适应用户沟通偏好的能力
2. **算命准确性提升** - 基于历史反馈优化预测质量的能力  
3. **再算命信息提取** - 从对话中获取新的算命要素的能力

## 项目结构

```
memory_comparison_test/
├── memu_test/                    # Memu框架测试模块
│   ├── __init__.py
│   └── memu_tester.py           # Memu测试器实现
├── memobase_test/               # Memobase框架测试模块  
│   ├── __init__.py
│   └── memobase_tester.py       # Memobase测试器实现
├── test_scenarios/              # 测试场景定义
│   ├── style_learning/          # 聊天风格学习测试
│   │   └── chat_style_tests.py
│   ├── accuracy_boost/          # 准确性提升测试
│   │   └── divination_accuracy_tests.py
│   └── info_extraction/         # 信息提取测试
│       └── information_extraction_tests.py
├── evaluation_tools/            # 评估工具
│   ├── __init__.py
│   ├── comparison_evaluator.py  # 对比评估器
│   └── run_comparison.py        # 测试执行脚本
├── comparison_results/          # 测试结果输出目录
└── README.md                    # 项目说明文档
```

## 核心功能

### 1. 聊天风格学习测试

测试AI如何学习用户的沟通偏好：

- **简洁偏好型用户**：喜欢直接、简短的回答
- **详细偏好型用户**：希望得到充分解释和背景信息
- **互动偏好型用户**：喜欢问答式的交流过程
- **语言风格适应**：正式vs随意的语言风格

### 2. 算命准确性提升测试

测试AI如何基于用户反馈提升预测质量：

- **反馈学习**：根据用户验证调整预测准确性
- **模式识别**：识别个人命理模式并应用
- **跨领域关联**：关联分析不同生活领域的信息
- **时间预测精度**：提升时间预测的准确度

### 3. 信息提取测试

测试从对话中提取再次算命所需信息的能力：

- **生活变化提取**：识别职业、感情、健康等重大变化
- **时间信息提取**：准确识别和解析时间相关信息
- **情感状态追踪**：跟踪用户情感状态变化
- **复合信息处理**：处理多领域交叉的复杂信息

## 使用方法

### 环境要求

- Python 3.8+
- 无特殊第三方依赖（使用标准库）

### 运行测试

1. **进入项目目录**：
   ```bash
   cd memory_comparison_test
   ```

2. **运行完整对比测试**：
   ```bash
   cd evaluation_tools
   python run_comparison.py
   ```

3. **运行单独的测试模块**：
   ```python
   from evaluation_tools.comparison_evaluator import MemoryFrameworkComparator
   
   # 创建对比器
   comparator = MemoryFrameworkComparator("test_user")
   comparator.initialize_testers()
   
   # 运行特定测试
   style_result = comparator.run_style_learning_test("concise_preference")
   accuracy_result = comparator.run_accuracy_boost_test("feedback_learning") 
   extraction_result = comparator.run_info_extraction_test("life_changes_extraction")
   ```

### 查看测试结果

测试完成后，结果会保存在 `comparison_results/` 目录下：

- **详细结果**：`detailed_comparison_YYYYMMDD_HHMMSS.json`
- **简要报告**：`summary_report_YYYYMMDD_HHMMSS.md`

## 评估指标

### 聊天风格学习指标

- **适应速度**：学习用户偏好所需的对话轮次
- **最终匹配度**：风格适应的准确程度  
- **一致性**：风格保持的稳定性
- **总体评分**：综合评估分数

### 算命准确性提升指标

- **反馈整合**：用户反馈的有效应用程度
- **置信度调整**：基于历史验证的置信度更新
- **特异性改进**：预测细节和针对性的提升
- **模式学习**：个人命理模式的识别能力

### 信息提取指标

- **召回率**：应该提取的信息中实际提取到的比例
- **精确率**：提取信息中正确的比例
- **时间准确性**：时间信息识别的准确度
- **完整性**：信息类别覆盖的全面性

## 测试场景示例

### 风格学习场景示例

```python
# 简洁偏好用户的学习过程
轮次1: 用户说"太长了，简单点说" → AI学习简洁偏好
轮次2: 用户说"还是太复杂" → AI进一步调整
轮次3: 用户说"这样刚好" → AI确认学到的风格
轮次4: 测试AI是否能在新话题上应用学到的简洁风格
```

### 准确性提升场景示例

```python
# 反馈学习过程
初始预测: "你下半年会有职业变动" (置信度0.7)
用户反馈: "确实，我10月换了工作，很准！"
调整后预测: 提高类似预测的置信度，增加具体细节
```

### 信息提取场景示例

```python
# 从对话中提取关键信息
用户输入: "最近换了新工作，从互联网公司跳到了传统制造业，压力比以前大了不少"
提取信息:
- 职业变化：互联网 → 传统制造业
- 时间：最近
- 压力状况：增加
- 变化类型：跨行业跳槽
```

## 扩展开发

### 添加新的测试场景

1. 在相应的测试场景文件中添加新的测试用例
2. 更新评估指标和方法
3. 在对比评估器中集成新场景

### 集成真实的记忆框架

目前的实现是模拟版本，可以替换为：

1. **Memu框架集成**：
   - 替换 `MemuTester` 中的模拟实现
   - 连接真实的 Memu API

2. **Memobase框架集成**：
   - 替换 `MemobaseTester` 中的数据库操作
   - 连接真实的 Memobase 服务

### 添加新的评估指标

在各测试场景类中添加新的评估方法，并在对比评估器中调用。

## 注意事项

1. **测试数据隔离**：每次测试使用独立的用户ID，避免数据污染
2. **结果可重现性**：固定随机种子确保测试结果可重现
3. **资源清理**：测试结束后及时清理数据库连接等资源
4. **性能考虑**：大规模测试时注意内存和存储使用

## 贡献指南

1. Fork 本项目
2. 创建特性分支
3. 添加测试用例
4. 提交 Pull Request

## 许可证

本项目仅用于记忆框架对比研究，请遵循相关框架的使用许可。