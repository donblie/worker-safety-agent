"""
简单内存缓存 —— 避免短时间内相同请求重复调用 API
"""
import hashlib
import time
from typing import Any, Optional
from collections import OrderedDict


class SimpleCache:
    """LRU 内存缓存，带 TTL 过期"""

    def __init__(self, max_size: int = 100, ttl_seconds: int = 300):
        self._cache: OrderedDict[str, tuple[float, Any]] = OrderedDict()
        self.max_size = max_size
        self.ttl = ttl_seconds

    def _make_key(self, *args, **kwargs) -> str:
        raw = str(args) + str(sorted(kwargs.items()))
        return hashlib.md5(raw.encode()).hexdigest()

    def get(self, *args, **kwargs) -> Optional[Any]:
        key = self._make_key(*args, **kwargs)
        if key in self._cache:
            timestamp, value = self._cache[key]
            if time.time() - timestamp < self.ttl:
                # 移到末尾（最近使用）
                self._cache.move_to_end(key)
                return value
            else:
                # 过期，删除
                del self._cache[key]
        return None

    def set(self, value: Any, *args, **kwargs):
        key = self._make_key(*args, **kwargs)
        if key in self._cache:
            del self._cache[key]
        elif len(self._cache) >= self.max_size:
            # 淘汰最久未使用
            self._cache.popitem(last=False)
        self._cache[key] = (time.time(), value)

    def clear(self):
        self._cache.clear()

    def size(self) -> int:
        return len(self._cache)


# 全局缓存实例
_qa_cache = SimpleCache(max_size=200, ttl_seconds=600)   # 问答缓存10分钟
_vision_cache = SimpleCache(max_size=50, ttl_seconds=1800)  # 图片分析缓存30分钟
