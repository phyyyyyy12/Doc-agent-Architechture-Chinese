多模态 ReAct 推理引擎 (Multi-modal ReAct Engine)
项目实现了标准的 ReAct (Reasoning + Acting) 范式，通过 Thought-Action-Observation 闭环赋予 Agent 解决复杂问题的能力。

核心逻辑如下：
1.双轨规划机制 (Hybrid Planner)：

Simple Planner：基于规则与关键词触发，适用于高频、确定的工具调用场景（如计算、基础检索），响应极快。

LLM Planner：基于 LLM 生成动态 JSON 任务列表，支持多步骤逻辑拆解与长链任务编排。

2.自适应 ReAct 循环 (Adaptive Reasoning Loop)：

流式推理：通过 run_stream() 实时输出 Thought 过程，提升用户交互体验。

迭代熔断：设置最大迭代次数（Max Iterations）限制，防止模型进入逻辑死循环。

终止信号：支持 Final Answer 关键词与 Action: FINISH 强指令的双重收敛逻辑。

3.执行器隔离与安全 (Executor Sandbox)：

权限白名单：通过 allowed_tools 严格控制 Agent 的操作边界，确保敏感工具不被非法调用。

鲁棒执行：内置 LLM 调用重试机制（自动指数退避）与工具异常捕获，确保单点故障不中断任务流。
