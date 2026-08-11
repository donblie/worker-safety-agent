"""
LLM JSON 解析工具
从 LLM 返回文本中提取 JSON，处理常见格式异常
"""
import json
import re
from typing import Any


def extract_json(raw_response: str) -> dict:
    """
    从 LLM 原始返回中提取 JSON 对象。

    处理以下情况：
    - 纯 JSON 字符串
    - ```json ... ``` 包裹的代码块
    - 前后有额外文字说明
    - 嵌套花括号

    返回: 解析后的 dict
    抛出: ValueError 当无法提取有效 JSON 时
    """
    if not raw_response or not isinstance(raw_response, str):
        raise ValueError("Response is empty or not a string")

    text = raw_response.strip()

    # 情况1: 移除代码块包裹
    if text.startswith("```"):
        # 去掉开头的 ```json 或 ```
        text = re.sub(r"^```(?:json)?\s*\n?", "", text)
        # 去掉结尾的 ```
        text = re.sub(r"\n?```\s*$", "", text)

    # 情况2: 尝试找到最外层 JSON 对象
    text = text.strip()

    # 直接尝试解析
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # 情况3: 从文本中提取第一个完整的 JSON 对象
    # 使用花括号计数匹配
    start = text.find("{")
    if start == -1:
        raise ValueError("No JSON object found in response")

    depth = 0
    in_string = False
    escaped = False

    for i in range(start, len(text)):
        char = text[i]

        if escaped:
            escaped = False
            continue

        if char == "\\" and in_string:
            escaped = True
            continue

        if char == '"' and not escaped:
            in_string = not in_string
            continue

        if in_string:
            continue

        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                json_str = text[start:i + 1]
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    # 找到的片段无效，继续找下一个
                    start = text.find("{", i + 1)
                    if start == -1:
                        raise ValueError("No valid JSON object found in response")
                    depth = 0
                    continue

    raise ValueError("Unterminated JSON object in response")


def is_api_error_response(response: Any) -> bool:
    """
    判断 LLM 返回是否为 API 层面的错误降级消息。
    与 safety_guard.py 中的 FALLBACK_MESSAGES 配合使用。
    """
    if not isinstance(response, str):
        return False

    # 错误降级消息的特征：以特定 emoji 开头
    error_prefixes = ("⏱️", "🔑", "🌐", "⏳", "😞")
    for prefix in error_prefixes:
        if response.startswith(prefix):
            return True
    return False
