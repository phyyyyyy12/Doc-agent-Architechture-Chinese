# 🏢 Doc-Agent Architecture
> 基于 Markdown 文档深度解析的企业级问答 Agent 架构演进实录


## 🗺️ 技术矩阵 (Architecture Navigation)

| 核心组件 | 💡 当前架构方案 (Status Quo) | 🔄 架构演进思考 (ADR/Deep Dive) |
| :--- | :--- | :--- |
| **1. 记忆管理 (Memory)** | [动态 Token 窗口与语义压缩](./docs/memory/index.md) | [从“全都要”到“算 Token”](./docs/memory/evolution.md) |
| **2. 文档解析 (Parser)** | [Markdown 结构感知智能分块](./docs/parser/index.md) | [从“暴力切分”到“结构化感知”](./docs/parser/evolution.md) |
| **3. 推理引擎 (ReAct)** | [多模态 ReAct 推理引擎与双轨规划](./docs/react/index.md) | [从“泛用搜索”到“高度闭环”](./docs/react/evolution.md) |
---

## 🎯 项目核心实现
| 核心模块 | 技术特性 (Key Features) | 源码位置 (Source) |
| --- | --- | --- |
| **ReAct 引擎** | **推理闭环**：Thought-Action-Observation 循环，支持工具自动解析与流式终止判断。 | `react_core.py` |
| **动态 Memory** | **Token 精算**：实时窗口管理，采用 **System 锚点保护** 与 **远场语义压缩** 策略。 | `memory_core.py` |
| **结构化分块** | **语法感知**：基于标题层级的智能切分，支持 **面包屑路径继承** 与代码块边界保护。 | `chunker_core.py` |
| **任务执行器** | **安全调度**：整合简单规划器（关键词匹配），内置工具权限检查与 LLM 容错重试。 | `executor_core.py` |
