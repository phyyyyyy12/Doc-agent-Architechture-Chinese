# 🧠 ReAct 推理引擎 (ReAct Engine)

项目实现了标准的 **ReAct (Reasoning + Acting)** 范式，通过 `Thought-Action-Observation` 闭环赋予 Agent 解决复杂问题的能力。

---

## 🛠️ 核心逻辑

### 1. 双轨规划机制 (Hybrid Planner)
针对不同复杂度的任务，系统提供两种调度策略以平衡速度与深度：
* **Simple Planner**：基于规则与关键词触发，适用于高频、确定的工具调用场景（如数学计算、基础索引检索）。
* **LLM Planner**：基于大模型生成动态 JSON 任务列表，支持多步骤逻辑拆解、长链任务编排及动态目标调整。

### 2. 自适应 ReAct 循环 (Adaptive Reasoning Loop)
构建健壮的推理闭环，确保生成过程透明且可控：
* **流式推理 (Streaming)**：通过 `run_stream()` 实时输出 `Thought` 思考过程，消除用户等待焦虑，提升交互体验。
* **迭代熔断 (Safety Guard)**：内置 `Max Iterations` 限制（默认 10 次），防止模型在处理模糊指令时陷入逻辑死循环。
* **终止信号收敛**：兼容 `Final Answer` 关键词与 `Action: FINISH` 强指令，确保 Agent 在完成任务后能够准确收敛。

### 3. 执行器隔离与安全 (Executor Sandbox)
为工具调用提供安全的运行环境与错误容忍机制：
* **权限白名单 (RBAC)**：通过 `allowed_tools` 严格控制 Agent 的操作边界，从底层杜绝敏感工具的非法调用。
* **鲁棒执行机制**：
    * **自动重试**：LLM 调用内置指数退避重试机制（最多 3 次）。
    * **异常捕获**：对工具返回的错误进行语义化包装，将错误信息反馈给模型进行自我修正，而非直接崩溃。
