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
1. **结构化embedding**：基于标题层级进行语义切分，辅以面包屑路径继承与块边界保护（代码/表格），确保存储单元的高内敛性与语义完整性。
2. **动态memory**：基于 Context Window 实时精算的动态窗口管理：结合 System 锚点保护、远场语义压缩与检索噪声过滤，实现长效、高信息密度的 Agent 记忆调度。
3. **ReAct 架构**：构建 Thought-Action-Observation 闭环推理，通过双轨规划机制（规则+LLM），在规避外部搜索噪声的同时，实现针对私有技术文档的高精度深度推理

---

## 📂 快速访问核心实现 (Source Code)
为了让 GitHub README 更加紧凑、专业，建议将**源码路径**与**核心特性**合并，采用表格（Table）或列表（List）结合加粗关键词的形式。这样读者可以一眼看到“功能”与“代码”的对应关系，无需反复滚动页面。

以下是为您优化后的紧凑版：

---

## 🛠️ 核心架构与实现 (Core Architecture)

我们将复杂的 Agent 逻辑拆解为四个高度解耦的核心模块，确保在有限的上下文内实现最高效的推理。

| 核心模块 | 技术特性 (Key Features) | 源码位置 (Source) |
| --- | --- | --- |
| **ReAct 引擎** | **推理闭环**：Thought-Action-Observation 循环，支持工具自动解析与流式终止判断。 | `react_core.py` |
| **动态 Memory** | **Token 精算**：实时窗口管理，采用 **System 锚点保护** 与 **远场语义压缩** 策略。 | `memory_core.py` |
| **结构化分块** | **语法感知**：基于标题层级的智能切分，支持 **面包屑路径继承** 与代码块边界保护。 | `chunker_core.py` |
| **任务执行器** | **安全调度**：整合简单规划器（关键词匹配），内置工具权限检查与 LLM 容错重试。 | `executor_core.py` |
