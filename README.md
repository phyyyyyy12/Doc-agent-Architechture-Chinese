# 🏢 Doc-Agent Architecture
> 基于 Markdown 文档深度解析的企业级问答 Agent 架构演进实录


## 🗺️ 技术矩阵 (Architecture Navigation)

| 核心组件 | 💡 当前架构方案 (Status Quo) | 🔄 架构演进思考 (ADR/Deep Dive) |
| :--- | :--- | :--- |
| **1. 记忆管理 (Memory)** | [动态 Token 窗口与语义压缩](./docs/memory/index.md) | [从“全都要”到“算 Token”](./docs/memory/evolution.md) |
| **2. 文档解析 (Parser)** | [Markdown 结构感知智能分块](./docs/parser/index.md) | [从“暴力切分”到“结构化感知”](./docs/parser/evolution.md) |

---

## 🎯 项目核心实现
1. **结构化认知**：不只是简单的 RAG，而是通过识别 Markdown 的 `#` 标题层级建立深层知识索引，确保检索不丢失背景信息。
2. **决策可追溯**：采用“演进日志”模式，记录在吸纳豆包 Agent 等前沿设计思想后，如何优化自身的 Token 管理与记忆系统。
3. **工业级落地**：重点解决长文档场景下的 Context Overflow（上下文溢出）问题。

---

## 📂 快速访问核心实现 (Source Code)
* `src/memory_manager.py`: 实现动态 Token 权重裁剪算法。
* `src/md_parser.py`: 基于标题路径（Breadcrumb）的结构化切片逻辑。
