"""ReAct 核心实现：Thought-Action-Observation 循环

核心流程：
1. Thought: LLM思考下一步行动
2. Action: 执行工具调用或生成回答
3. Observation: 观察工具执行结果
4. 循环直到完成任务
"""
from typing import List, Dict, Any, Optional, Iterator, Callable
import json
import re
import logging

logger = logging.getLogger(__name__)


class ReActCore:
    """ReAct 核心循环实现"""
    
    def __init__(self, llm, tools: Dict[str, Callable], max_iterations: int = 10):
        self.llm = llm
        self.tools = tools
        self.max_iterations = max_iterations
    
    def run(self, query: str, allowed_tools: Optional[List[str]] = None) -> str:
        """执行 ReAct 循环"""
        history = []
        
        for i in range(self.max_iterations):
            # Thought 阶段
            thought = self._think(query, history)
            
            # 判断是否应该结束
            if self._should_finish(thought):
                final_answer = self._extract_final_answer(thought)
                if final_answer:
                    return final_answer
            
            # Action 阶段
            action_result = self._act(thought, allowed_tools)
            
            # Observation 阶段
            observation = self._observe(action_result)
            history.append(observation)
        
        # 达到最大迭代次数
        return self._generate_final_answer(query, history) if history else "无法完成任务"
    
    def _think(self, query: str, history: List[str]) -> str:
        """生成 Thought"""
        prompt = self._build_react_prompt(query, history)
        try:
            return self.llm.generate(prompt, temperature=0.3)
        except Exception as e:
            logger.error(f"生成Thought失败: {e}")
            return f"思考: 遇到错误，无法继续思考。错误: {str(e)}"
    
    def _build_react_prompt(self, query: str, history: List[str]) -> str:
        """构建 ReAct 格式的 prompt"""
        # 构建工具描述
        tool_descriptions = []
        for name, func in self.tools.items():
            doc = func.__doc__ or "无描述"
            doc_first_line = doc.strip().split('\n')[0]
            tool_descriptions.append(f"- {name}: {doc_first_line}")
        
        tools_info = "\n".join(tool_descriptions) if tool_descriptions else "无可用工具"
        
        # 构建历史观察
        history_text = ""
        if history:
            history_text = "\n\n" + "\n\n".join([
                f"Observation {i+1}: {obs}" 
                for i, obs in enumerate(history)
            ])
        
        return f"""你是一个智能助手，使用ReAct模式解决问题。

可用工具：
{tools_info}

请按照以下格式思考和行动：
1. Thought: [分析当前情况，思考下一步应该做什么]
2. Action: [如果需要使用工具，格式为: tool_name({{"参数名": "参数值"}})]
   或者 Action: FINISH [如果可以直接给出最终答案]

用户查询: {query}{history_text}

请开始思考："""
    
    def _should_finish(self, thought: str) -> bool:
        """判断是否应该结束循环"""
        finish_patterns = [
            r'Final Answer:',
            r'最终答案:',
            r'Action:\s*FINISH',
        ]
        return any(re.search(pattern, thought, re.IGNORECASE) for pattern in finish_patterns)
    
    def _extract_final_answer(self, thought: str) -> Optional[str]:
        """从 Thought 中提取最终答案"""
        patterns = [
            r'Final Answer:\s*(.+?)(?:\n|$)',
            r'最终答案:\s*(.+?)(?:\n|$)',
        ]
        for pattern in patterns:
            match = re.search(pattern, thought, re.IGNORECASE | re.DOTALL)
            if match:
                answer = match.group(1).strip()
                if answer:
                    return answer
        return thought.strip()
    
    def _act(self, thought: str, allowed_tools: Optional[List[str]] = None) -> Dict[str, Any]:
        """执行 Action"""
        # 解析 Action
        action_match = re.search(
            r'Action:\s*(\w+)\s*\((.+?)\)',
            thought,
            re.IGNORECASE | re.DOTALL
        )
        
        if not action_match:
            if re.search(r'Action:\s*FINISH', thought, re.IGNORECASE):
                return {'type': 'finish', 'action': 'FINISH'}
            return {'type': 'no_action', 'error': '未找到有效的Action'}
        
        tool_name = action_match.group(1).strip()
        args_str = action_match.group(2).strip()
        
        # 检查工具权限
        if allowed_tools is not None and tool_name not in allowed_tools:
            return {'type': 'error', 'error': f'工具 {tool_name} 未被允许'}
        
        # 获取工具函数
        tool_func = self.tools.get(tool_name)
        if not tool_func:
            return {'type': 'error', 'error': f'未知工具: {tool_name}'}
        
        # 解析参数
        try:
            args = json.loads(args_str)
        except json.JSONDecodeError:
            # 尝试简单键值对解析
            args = {}
            kv_pattern = r'(\w+)\s*[:=]\s*"([^"]+)"'
            for match in re.finditer(kv_pattern, args_str):
                args[match.group(1)] = match.group(2)
            
            if not args:
                return {'type': 'error', 'error': f'无法解析Action参数: {args_str}'}
        
        # 执行工具
        try:
            result = tool_func(args)
            return {'type': 'tool', 'tool_name': tool_name, 'args': args, 'result': result}
        except Exception as e:
            logger.error(f"工具 {tool_name} 执行失败: {e}")
            return {'type': 'error', 'error': str(e), 'tool_name': tool_name}
    
    def _observe(self, action_result: Dict[str, Any]) -> str:
        """生成 Observation 文本"""
        if action_result.get('type') == 'finish':
            return "任务完成"
        
        if action_result.get('type') == 'error':
            error = action_result.get('error', '未知错误')
            tool_name = action_result.get('tool_name', '')
            return f"错误: {error}" + (f" (工具: {tool_name})" if tool_name else "")
        
        if action_result.get('type') == 'tool':
            tool_name = action_result.get('tool_name', '')
            result = action_result.get('result', {})
            result_text = json.dumps(result, ensure_ascii=False) if isinstance(result, dict) else str(result)
            return f"[工具 {tool_name}] {result_text}"
        
        return f"未知的Action结果: {action_result}"
    
    def _generate_final_answer(self, query: str, history: List[str]) -> str:
        """生成最终答案"""
        history_text = "\n\n".join([
            f"Observation {i+1}: {obs}" 
            for i, obs in enumerate(history)
        ])
        
        prompt = f"""基于以下观察结果，回答用户的问题。

用户查询: {query}

观察结果:
{history_text}

请给出简洁、准确的最终答案："""
        
        try:
            return self.llm.generate(prompt, temperature=0.3).strip()
        except Exception as e:
            logger.error(f"生成最终答案失败: {e}")
            return "抱歉，无法生成最终答案。"

