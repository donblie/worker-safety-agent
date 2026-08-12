"""
全局配置管理
优先级: Streamlit Cloud Secrets > 环境变量 > .env 文件 > 默认值
"""
import os
from dotenv import load_dotenv

load_dotenv()


def _get(key: str, default: str = "") -> str:
    """
    读取配置。
    Streamlit Cloud 上 st.secrets 和 os.environ 都会被注入，
    这里优先从 os.environ 读（最可靠），st.secrets 兜底。
    """
    # 方式1: 环境变量（.env 文件本地生效，Streamlit Cloud 也注入）
    val = os.environ.get(key)
    if val:
        return val

    # 方式2: st.secrets（Streamlit Cloud Dashboard 配置）
    try:
        import streamlit as st
        if hasattr(st, "secrets"):
            val = st.secrets.get(key) or st.secrets[key] if key in st.secrets else None
            if val:
                return val
    except Exception:
        pass

    return default


def _get_int(key: str, default: int = 0) -> int:
    """读取整数配置"""
    try:
        return int(_get(key, str(default)))
    except (ValueError, TypeError):
        return default


# ── DeepSeek API 配置（纯文本：问答/培训/应急）─────
DEEPSEEK_API_KEY = _get("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = _get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
DEEPSEEK_CHAT_MODEL = _get("DEEPSEEK_CHAT_MODEL", "deepseek-chat")
API_TIMEOUT = _get_int("API_TIMEOUT", 30)

# ── Qwen-VL API 配置（视觉：工地隐患识别）────────
QWEN_API_KEY = _get("QWEN_API_KEY", "")
QWEN_BASE_URL = _get("QWEN_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
QWEN_VISION_MODEL = _get("QWEN_VISION_MODEL", "qwen-vl-max")

# ── 知识库配置 ─────────────────────────────────
REGULATIONS_DIR = _get("REGULATIONS_DIR", "./data/regulations")
EMERGENCY_DIR = _get("EMERGENCY_DIR", "./data/emergency")
CHUNK_SIZE = _get_int("CHUNK_SIZE", 500)
CHUNK_OVERLAP = _get_int("CHUNK_OVERLAP", 50)
RETRIEVAL_TOP_K = _get_int("RETRIEVAL_TOP_K", 3)
RETRIEVAL_MIN_SCORE = 0.08  # 相似度阈值，低于此值视为噪音（TF-IDF/BGE共用）
KB_EMBEDDING_MODEL = _get("KB_EMBEDDING_MODEL", "BAAI/bge-small-zh-v1.5")
KB_CACHE_DIR = _get("KB_CACHE_DIR", "./data/kb_cache")

# ── 应用配置 ───────────────────────────────────
APP_TITLE = "工友安全守护Agent"
APP_ICON = "🛡️"
APP_DESCRIPTION = "建筑工地安全智能助手 —— 安全知识问答 · 隐患识别 · 安全培训 · 应急指导"

# ── 安全热线（演示用占位，可替换为真实号码）────
SAFETY_HOTLINE = "XXX-XXXX-XXXX"
