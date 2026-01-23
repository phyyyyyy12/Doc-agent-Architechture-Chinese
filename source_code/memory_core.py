"""动态 Memory 核心实现：Token 窗口管理与语义压缩

核心特性：
1. Token 计数与窗口管理
2. 近场全量保留，远场压缩
3. System Prompt 锚点保护
"""
import os
import logging
from typing import List, Dict, Any, Optional, Tuple

try:
    import tiktoken
    HAS_TIKTOKEN = True
except ImportError:
    HAS_TIKTOKEN = False


class TokenCounter:
    """Token 计数器"""
    
    def __init__(self, model: str = "deepseek-chat"):
        self.model = model
        self.encoding = None
        
        if HAS_TIKTOKEN:
            try:
                if "deepseek" in model.lower() or "gpt" in model.lower():
                    self.encoding = tiktoken.get_encoding("cl100k_base")
                else:
                    self.encoding = tiktoken.get_encoding("cl100k_base")
            except Exception:
                self.encoding = None
    
    def count(self, text: str) -> int:
        """计算文本的 Token 数量"""
        if not text:
            return 0
        
        if self.encoding:
            try:
                return len(self.encoding.encode(text))
            except Exception:
                pass
        
        # 回退方案：字符数估算
        return int(len(text) / 2.5)
    
    def count_messages(self, messages: List[Dict[str, Any]]) -> int:
        """计算消息列表的总 Token 数"""
        total = 0
        for msg in messages:
            total += 6  # 基础开销
            total += self.count(str(msg.get("content", "")))
        return total


class DynamicMemoryCore:
    """动态 Memory 核心：Token 窗口管理"""
    
    def __init__(
        self,
        max_context_tokens: int = 32768,
        system_prompt: str = "",
        model: str = "deepseek-chat",
        near_field_turns: int = 2,
        llm=None,
    ):
        self.token_counter = TokenCounter(model=model)
        self.system_prompt = system_prompt
        self.near_field_turns = near_field_turns
        self.llm = llm
        
        self.max_context_tokens = max_context_tokens
        self.system_prompt_tokens = self.token_counter.count(system_prompt)
        # 预留 20% 的安全边距 + System Prompt
        self.reserved_tokens = int(self.max_context_tokens * 0.2) + self.system_prompt_tokens
        self.available_tokens = self.max_context_tokens - self.reserved_tokens
        
        self.logger = logging.getLogger(__name__)
    
    def build_context_prompt(
        self,
        user_input: str,
        messages: List[Dict[str, Any]],
    ) -> Tuple[str, Dict[str, Any]]:
        """
        构建上下文 prompt，进行 Token 窗口管理
        
        Returns:
            (context_text, metadata): 上下文文本和元数据
        """
        # 计算当前用户输入的 Token 数
        current_input_tokens = self.token_counter.count(user_input)
        remaining_tokens = self.available_tokens - current_input_tokens
        
        if remaining_tokens <= 0:
            return "", {
                'strategy': 'input_too_large',
                'messages_tokens': 0,
                'remaining_tokens': remaining_tokens
            }
        
        # 按轮次分组消息
        message_pairs = self._group_messages_by_turns(messages)
        
        # 策略：近场全量，远场压缩
        near_field_pairs = message_pairs[-self.near_field_turns:] if len(message_pairs) > self.near_field_turns else message_pairs
        far_field_pairs = message_pairs[:-self.near_field_turns] if len(message_pairs) > self.near_field_turns else []
        
        # 计算近场消息 Token
        near_field_messages = [msg for pair in near_field_pairs for msg in pair]
        near_field_tokens = self.token_counter.count_messages(near_field_messages)
        
        # 如果近场消息超过限制，只保留最近的几轮
        if near_field_tokens > remaining_tokens:
            selected_pairs = []
            selected_tokens = 0
            for pair in reversed(near_field_pairs):
                pair_tokens = self.token_counter.count_messages(pair)
                if selected_tokens + pair_tokens <= remaining_tokens:
                    selected_pairs.insert(0, pair)
                    selected_tokens += pair_tokens
                else:
                    break
            
            filtered_messages = [msg for pair in selected_pairs for msg in pair]
            context_text = self._format_messages(filtered_messages)
            
            return context_text, {
                'strategy': 'near_field_partial',
                'messages_tokens': selected_tokens,
                'remaining_tokens': remaining_tokens - selected_tokens
            }
        
        # 近场消息可以全部保留，尝试压缩远场
        remaining_after_near = remaining_tokens - near_field_tokens
        
        if remaining_after_near > 0 and far_field_pairs and self.llm:
            # 压缩远场消息
            compressed_summary = self._compress_far_field(far_field_pairs, remaining_after_near)
            
            if compressed_summary:
                summary_tokens = self.token_counter.count(compressed_summary)
                if summary_tokens <= remaining_after_near:
                    all_messages = near_field_messages + [
                        {'role': 'system', 'content': compressed_summary}
                    ]
                    context_text = self._format_messages(all_messages)
                    
                    return context_text, {
                        'strategy': 'near_field_full_with_far_field_compressed',
                        'messages_tokens': near_field_tokens + summary_tokens,
                        'remaining_tokens': remaining_tokens - near_field_tokens - summary_tokens
                    }
        
        # 只保留近场消息
        context_text = self._format_messages(near_field_messages)
        
        return context_text, {
            'strategy': 'near_field_only',
            'messages_tokens': near_field_tokens,
            'remaining_tokens': remaining_tokens - near_field_tokens
        }
    
    def _group_messages_by_turns(self, messages: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        """将消息按轮次分组（每轮 = user + assistant）"""
        pairs = []
        current_pair = []
        
        for msg in messages:
            role = msg.get("role", "")
            if role == "user":
                if current_pair:
                    pairs.append(current_pair)
                current_pair = [msg]
            elif role == "assistant" and current_pair:
                current_pair.append(msg)
                pairs.append(current_pair)
                current_pair = []
        
        if current_pair:
            pairs.append(current_pair)
        
        return pairs
    
    def _compress_far_field(
        self,
        far_field_pairs: List[List[Dict[str, Any]]],
        max_tokens: int,
    ) -> Optional[str]:
        """压缩远场消息，生成语义摘要"""
        if not self.llm or not far_field_pairs:
            return None
        
        # 提取远场消息内容
        far_field_text = []
        for pair in far_field_pairs:
            for msg in pair:
                role = msg.get("role", "")
                content = msg.get("content", "")
                if role == "user":
                    far_field_text.append(f"用户: {content}")
                elif role == "assistant":
                    far_field_text.append(f"助手: {content}")
        
        far_field_content = "\n".join(far_field_text)
        
        # 使用 LLM 生成摘要
        prompt = f"""请将以下历史对话压缩为简洁的摘要，保留关键信息：

{far_field_content}

摘要："""
        
        try:
            summary = self.llm.generate(prompt, temperature=0.3)
            return f"[历史对话摘要] {summary}"
        except Exception as e:
            self.logger.error(f"压缩远场消息失败: {e}")
            return None
    
    def _format_messages(self, messages: List[Dict[str, Any]]) -> str:
        """格式化消息为文本"""
        formatted = []
        for msg in messages:
            role = msg.get("role", "")
            content = msg.get("content", "")
            if role == "user":
                formatted.append(f"用户: {content}")
            elif role == "assistant":
                formatted.append(f"AI: {content}")
            elif role == "system":
                formatted.append(f"[系统] {content}")
        
        return "\n".join(formatted)

