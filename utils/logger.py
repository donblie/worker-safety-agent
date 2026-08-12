"""
结构化日志 —— 记录API调用耗时、检索结果、异常详情
- 同时输出到 stdout（Streamlit Cloud 可见）和日志文件（持久化）
- 日志文件自动轮转，保留最近5个文件，每个最大2MB
"""
import os
import time
import functools
import logging
from logging.handlers import RotatingFileHandler
from typing import Callable, Any
from datetime import datetime

# ── 日志文件路径 ──────────────────────────────
_LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
_LOG_FILE = os.path.join(_LOG_DIR, "worker_safety.log")

# ── 初始化文件 Logger ─────────────────────────
_file_logger: logging.Logger = None


def _get_file_logger() -> logging.Logger:
    """延迟初始化文件 logger（确保目录在运行时创建）"""
    global _file_logger
    if _file_logger is not None:
        return _file_logger

    os.makedirs(_LOG_DIR, exist_ok=True)
    _file_logger = logging.getLogger("worker-safety-agent")
    _file_logger.setLevel(logging.DEBUG)

    # 避免重复添加 handler
    if not _file_logger.handlers:
        handler = RotatingFileHandler(
            _LOG_FILE,
            maxBytes=2 * 1024 * 1024,   # 2MB
            backupCount=5,               # 保留最近5个
            encoding="utf-8",
        )
        handler.setFormatter(logging.Formatter(
            "[%(asctime)s] [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        ))
        _file_logger.addHandler(handler)

    return _file_logger


def _ts() -> str:
    """当前时间戳字符串"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def log(level: str, message: str):
    """统一日志输出。同时输出到 stdout 和日志文件。"""
    line = f"[{_ts()}] [{level}] {message}"
    print(line, flush=True)

    # 持久化到文件
    try:
        fl = _get_file_logger()
        level_map = {"DEBUG": logging.DEBUG, "INFO": logging.INFO,
                     "WARN": logging.WARNING, "ERROR": logging.ERROR}
        fl.log(level_map.get(level, logging.INFO), message)
    except Exception as e:
        # 不吞错误：至少打印到 stdout，方便排查
        print(f"[{_ts()}] [WARN] Log file write failed: {e}", flush=True)


def log_api_call(provider: str, model: str, duration_ms: float, success: bool,
                 tokens_used: int = 0, error: str = ""):
    """记录 API 调用"""
    status = "OK" if success else "FAIL"
    msg = f"{provider}/{model} | {duration_ms:.0f}ms | {status}"
    if tokens_used:
        msg += f" | tokens={tokens_used}"
    if error:
        msg += f" | {error[:100]}"
    log("API", msg)


def log_retrieval(query: str, result_count: int, top_score: float, duration_ms: float):
    """记录知识库检索"""
    query_preview = query[:40].replace("\n", " ")
    log("RETRIEVE",
        f"\"{query_preview}\" → {result_count} results, "
        f"top={top_score:.3f}, {duration_ms:.0f}ms")


def trace_api(func: Callable) -> Callable:
    """装饰器：记录函数调用耗时"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = (time.perf_counter() - start) * 1000
        # 只记录耗时，具体日志由调用方输出
        if not hasattr(wrapper, '_last_elapsed'):
            wrapper._last_elapsed = 0.0
        wrapper._last_elapsed = elapsed
        return result
    return wrapper
