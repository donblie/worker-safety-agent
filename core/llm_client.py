"""
LLM API 封装模块
- LLMClient: DeepSeek文本对话（问答/培训/应急）
- VisionClient: Qwen-VL视觉分析（工地隐患识别）
- 内置超时、异常处理和兜底
"""
import os
import time
import threading
from openai import OpenAI
from utils.config import (
    DEEPSEEK_BASE_URL,
    DEEPSEEK_CHAT_MODEL,
    QWEN_BASE_URL,
    QWEN_VISION_MODEL,
    API_TIMEOUT,
)
from utils.safety_guard import safe_api_call
from utils.cache import _qa_cache, _vision_cache
from utils.logger import log_api_call


def _read_api_key(key_name: str) -> str:
    """运行时读取API密钥（支持环境变量和Streamlit Secrets）"""
    # 1. 环境变量（本地.env文件 或 Streamlit Cloud注入）
    val = os.environ.get(key_name, "")
    if val:
        return val
    # 2. Streamlit Cloud Secrets
    try:
        import streamlit as st
        if hasattr(st, "secrets"):
            val = st.secrets.get(key_name, "")
            if val:
                return val
    except Exception:
        pass
    return ""


class LLMClient:
    """DeepSeek文本对话客户端"""

    def __init__(self):
        api_key = _read_api_key("DEEPSEEK_API_KEY")
        if not api_key:
            raise ValueError(
                "DEEPSEEK_API_KEY not configured. "
                "Add it to .env: DEEPSEEK_API_KEY=sk-your-key"
            )
        self.client = OpenAI(
            api_key=api_key,
            base_url=DEEPSEEK_BASE_URL,
        )
        self.chat_model = DEEPSEEK_CHAT_MODEL
        self.timeout = API_TIMEOUT

    @safe_api_call(fallback_key="unknown_error")
    def chat(
        self,
        system_prompt: str,
        user_message: str,
        model: str = None,
        temperature: float = 0.3,
        max_tokens: int = 2000,
    ) -> str:
        """文本对话调用（带缓存）"""
        # 检查缓存
        model_name = model or self.chat_model
        cached = _qa_cache.get(system_prompt, user_message, model_name, temperature)
        if cached is not None:
            return cached

        start = time.perf_counter()
        response = self.client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=self.timeout,
        )
        elapsed = (time.perf_counter() - start) * 1000
        result = response.choices[0].message.content
        tokens = response.usage.total_tokens if hasattr(response, 'usage') and response.usage else 0
        log_api_call("DeepSeek", model_name, elapsed, True, tokens_used=tokens)
        _qa_cache.set(result, system_prompt, user_message, model_name, temperature)
        return result

    def chat_stream(
        self,
        system_prompt: str,
        user_message: str,
        model: str = None,
        temperature: float = 0.3,
        max_tokens: int = 2000,
    ):
        """
        流式文本对话（Generator）。
        使用 stream=True，yield 每个文本 delta。
        Streamlit 中用 st.write_stream() 消费。
        """
        import time as _time
        model_name = model or self.chat_model

        try:
            start = _time.perf_counter()
            stream = self.client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=self.timeout,
                stream=True,
            )
            total_text = ""
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    delta = chunk.choices[0].delta.content
                    total_text += delta
                    yield delta

            elapsed = (_time.perf_counter() - start) * 1000
            log_api_call("DeepSeek", model_name, elapsed, True,
                        tokens_used=len(total_text) // 2)  # 粗略估算
            _qa_cache.set(total_text, system_prompt, user_message, model_name, temperature)

        except Exception as e:
            log("ERROR", f"Stream chat failed [{type(e).__name__}]: {str(e)[:200]}")
            from utils.safety_guard import FALLBACK_MESSAGES
            yield FALLBACK_MESSAGES.get("unknown_error", "😞 系统遇到了技术问题。")

    def chat_with_context_stream(
        self,
        system_prompt: str,
        user_message: str,
        context: str,
        history: str = "",
        model: str = None,
        temperature: float = 0.3,
        max_tokens: int = 2000,
    ):
        """带检索上下文和历史对话的流式RAG对话"""
        parts = []
        if history:
            parts.append(history)
        if context:
            parts.append(f"【参考资料（来自建筑安全规范）】\n{context}")
        parts.append(f"【工友的问题】\n{user_message}")
        parts.append(
            "请基于参考资料回答问题。如果参考资料不足以回答，如实说明并用你的知识补充"
            "（标注'仅供参考'）。回答时请结合对话历史中的上下文，理解用户的追问意图。"
        )
        full_user_message = "\n\n".join(parts)
        yield from self.chat_stream(
            system_prompt=system_prompt,
            user_message=full_user_message,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    @safe_api_call(fallback_key="unknown_error")
    def chat_with_context(
        self,
        system_prompt: str,
        user_message: str,
        context: str,
        history: str = "",
        model: str = None,
        temperature: float = 0.3,
        max_tokens: int = 2000,
    ) -> str:
        """带检索上下文和历史对话的RAG对话"""
        parts = []
        if history:
            parts.append(history)
        if context:
            parts.append(f"【参考资料（来自建筑安全规范）】\n{context}")
        parts.append(f"【工友的问题】\n{user_message}")
        parts.append(
            "请基于参考资料回答问题。如果参考资料不足以回答，如实说明并用你的知识补充"
            "（标注'仅供参考'）。回答时请结合对话历史中的上下文，理解用户的追问意图。"
        )
        full_user_message = "\n\n".join(parts)
        return self.chat(
            system_prompt=system_prompt,
            user_message=full_user_message,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )


class VisionClient:
    """Qwen-VL 视觉分析客户端"""

    def __init__(self):
        api_key = _read_api_key("QWEN_API_KEY")
        if not api_key:
            raise ValueError(
                "QWEN_API_KEY not configured. "
                "Get your API key from Alibaba Cloud DashScope (dashscope.aliyun.com), "
                "then add to .env: QWEN_API_KEY=sk-your-key"
            )
        self.client = OpenAI(
            api_key=api_key,
            base_url=QWEN_BASE_URL,
        )
        self.model = QWEN_VISION_MODEL
        self.timeout = 45  # 视觉模型响应较慢，给更多超时时间

    @safe_api_call(fallback_key="unknown_error")
    def analyze_image(
        self,
        system_prompt: str,
        image_base64: str,
        image_type: str = "image/jpeg",
        user_message: str = "",
        max_tokens: int = 2000,
    ) -> str:
        """
        视觉分析：上传图片 + 文字提示 → 分析结果（带缓存）
        Qwen-VL 支持 OpenAI Vision 格式的图片输入
        """
        # 用完整base64的MD5做缓存键（防止不同照片因前200字符相同而碰撞）
        import hashlib as _hashlib
        img_hash = _hashlib.md5(image_base64.encode()).hexdigest() if image_base64 else ""
        cached = _vision_cache.get(system_prompt, img_hash, user_message)
        if cached is not None:
            return cached

        user_content = [
            {
                "type": "image_url",
                "image_url": {"url": f"data:{image_type};base64,{image_base64}"},
            },
            {
                "type": "text",
                "text": user_message or "请仔细分析这张工地照片，识别所有安全隐患。",
            },
        ]

        start = time.perf_counter()
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
            max_tokens=max_tokens,
            timeout=self.timeout,
        )
        elapsed = (time.perf_counter() - start) * 1000
        result = response.choices[0].message.content
        tokens = response.usage.total_tokens if hasattr(response, 'usage') and response.usage else 0
        log_api_call("Qwen-VL", self.model, elapsed, True, tokens_used=tokens)
        _vision_cache.set(result, system_prompt, img_hash, user_message)
        return result


# ── 全局单例（线程安全）───────────────────────

_llm_client: LLMClient = None
_vision_client: VisionClient = None
_lock = threading.Lock()


def get_llm_client() -> LLMClient:
    global _llm_client
    if _llm_client is None:
        with _lock:
            if _llm_client is None:  # 双重检查
                _llm_client = LLMClient()
    return _llm_client


def get_vision_client() -> VisionClient:
    global _vision_client
    if _vision_client is None:
        with _lock:
            if _vision_client is None:
                _vision_client = VisionClient()
    return _vision_client
