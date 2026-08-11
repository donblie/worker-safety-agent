"""
结构化日志 —— 记录API调用耗时、检索结果、异常详情
"""
import time
import functools
from typing import Callable, Any
from datetime import datetime


def _ts() -> str:
    """当前时间戳字符串"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def log(level: str, message: str):
    """统一日志输出。生产环境可替换为 logging 模块或外部服务。"""
    print(f"[{_ts()}] [{level}] {message}", flush=True)


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
