"""执行器与规划器核心实现

核心功能：
1. 任务执行（工具调用 + LLM 生成）
2. 简单规划器（基于关键词匹配）
"""
from typing import List, Dict, Any, Optional, Callable
import json
import logging

logger = logging.getLogger(__name__)


class ExecutorCore:
    """执行器核心：统一执行工具和 LLM 任务"""
    
    def __init__(self, llm=None, get_tool: Optional[Callable] = None):
        self.llm = llm
        self.get_tool = get_tool
    
    def execute(
        self,
        tasks: List[Dict[str, Any]],
        allowed_tools: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """执行任务序列"""
        outputs = []
        tool_texts = []
        
        for t in tasks:
            if t['type'] == 'tool':
                name = t.get('name')
                
                # 获取工具函数
                if self.get_tool:
                    func = self.get_tool(name)
                else:
                    func = None
                
                if not func:
                    outputs.append({'ok': False, 'error': f'未知工具: {name}'})
                    continue
                
                # 检查工具权限
                if allowed_tools is not None and name not in allowed_tools:
                    outputs.append({'ok': False, 'tool_blocked': True, 'name': name})
                    continue
                
                # 执行工具
                try:
                    res = func(t.get('args', {}))
                    outputs.append({'ok': True, 'tool': name, 'result': res})
                    res_text = json.dumps(res, ensure_ascii=False) if isinstance(res, dict) else str(res)
                    tool_texts.append(f"[工具 {name}] {res_text}")
                except Exception as e:
                    logger.error(f"工具 {name} 执行失败: {e}")
                    outputs.append({'ok': False, 'error': str(e)})
            
            elif t['type'] == 'llm':
                prompt = t['args'].get('prompt', '')
                if tool_texts:
                    full_prompt = '\n\n'.join(tool_texts) + '\n\n' + prompt
                else:
                    full_prompt = prompt
                
                resp = self.llm.generate(full_prompt) if self.llm else ''
                outputs.append({'ok': True, 'llm': True, 'result': resp})
            
            else:
                outputs.append({'ok': False, 'error': '未知任务类型'})
        
        return outputs


class PlannerCore:
    """规划器核心：基于关键词的任务规划"""
    
    @staticmethod
    def simple_plan(user_input: str) -> List[Dict[str, Any]]:
        """简单规划器：基于关键词匹配"""
        tasks = []
        low = user_input.lower()
        
        # 索引建立
        if '建立索引' in low or ('索引' in low and 'http' in low):
            parts = user_input.split()
            repo_url = None
            for p in parts:
                if p.startswith('http'):
                    repo_url = p
                    break
            if repo_url:
                index_name = repo_url.rstrip('/').split('/')[-1].replace('.git', '')
                tasks.append({
                    'type': 'tool',
                    'name': 'index_github_repo',
                    'args': {'repo_url': repo_url, 'index_name': index_name}
                })
                tasks.append({
                    'type': 'llm',
                    'args': {'prompt': f'已为仓库 {repo_url} 建立索引 {index_name}，请给出说明。'}
                })
                return tasks
        
        # 数学计算
        if '计算' in low or (any(ch in low for ch in ['+', '-', '*', '/', '%']) and any(c.isdigit() for c in low)):
            expr = ''.join([c for c in user_input if c in '0123456789+-*/(). %^'])
            tasks.append({'type': 'tool', 'name': 'calculator', 'args': {'expr': expr}})
            tasks.append({'type': 'llm', 'args': {'prompt': '请根据计算结果给出建议。'}})
            return tasks
        
        # 文档检索
        if any(k in low for k in ['检索', '搜索', '查询', '查找', '文档中', '在文档']):
            tasks.append({
                'type': 'tool',
                'name': 'query_index',
                'args': {'query': user_input, 'index_name': 'default', 'top_k': 4}
            })
            tasks.append({
                'type': 'llm',
                'args': {'prompt': '请基于检索结果给出简洁回答。'}
            })
            return tasks
        
        # 默认：直接使用 LLM
        tasks.append({'type': 'llm', 'args': {'prompt': user_input}})
        return tasks

