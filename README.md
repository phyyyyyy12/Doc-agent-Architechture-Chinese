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
3. **ReAct 架构**构建 Thought-Action-Observation 闭环推理，通过双轨规划机制（规则+LLM），在规避外部搜索噪声的同时，实现针对私有技术文档的高精度深度推理

---

## 📂 快速访问核心实现 (Source Code)
* `src/memory_manager.py`: 实现动态 Token 权重裁剪算法。
* `src/md_parser.py`: 基于标题路径（Breadcrumb）的结构化切片逻辑。
