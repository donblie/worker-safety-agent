"""
全局配置管理
读取 .env 文件中的环境变量，提供统一的配置入口
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ── DeepSeek API 配置（纯文本：问答/培训/应急）─────
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
DEEPSEEK_CHAT_MODEL = os.getenv("DEEPSEEK_CHAT_MODEL", "deepseek-chat")
API_TIMEOUT = int(os.getenv("API_TIMEOUT", "30"))

# ── Qwen-VL API 配置（视觉：工地隐患识别）────────
QWEN_API_KEY = os.getenv("QWEN_API_KEY", "")
QWEN_BASE_URL = os.getenv("QWEN_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
QWEN_VISION_MODEL = os.getenv("QWEN_VISION_MODEL", "qwen-vl-max")

# ── 知识库配置 ─────────────────────────────────
REGULATIONS_DIR = os.getenv("REGULATIONS_DIR", "./data/regulations")
EMERGENCY_DIR = os.getenv("EMERGENCY_DIR", "./data/emergency")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "500"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))
RETRIEVAL_TOP_K = int(os.getenv("RETRIEVAL_TOP_K", "3"))
KB_CACHE_DIR = os.getenv("KB_CACHE_DIR", "./data/kb_cache")

# ── 应用配置 ───────────────────────────────────
APP_TITLE = "工友安全守护Agent"
APP_ICON = "🛡️"
APP_DESCRIPTION = "建筑工地安全智能助手 —— 安全知识问答 · 隐患识别 · 安全培训 · 应急指导"

# ── 安全热线（演示用占位，可替换为真实号码）────
SAFETY_HOTLINE = "XXX-XXXX-XXXX"
