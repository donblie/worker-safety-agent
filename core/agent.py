"""
单Agent调度器 —— Function Calling 统一入口
- 定义4个Tool（搜索规范/分析图片/生成培训/应急指导）
- AgentLoop: 自动判断意图 → 调度工具 → 合成回答
- 支持流式输出和多轮对话
"""
import json
import time
from typing import Generator, Dict, Any, List, Optional

from core.llm_client import get_llm_client, get_vision_client
from core.knowledge_base import get_knowledge_base
from core.vision_analyzer import encode_image, analyze_image
from core.emergency_guide import generate_emergency_guide, EMERGENCY_TYPES
from core.training_generator import generate_training, WORKER_TYPES, TRAINING_TOPICS
from utils.prompts import QA_SYSTEM_PROMPT
from utils.logger import log

# ═══════════════════════════════════════════════════════════
# 待处理图片（页面设置，Tool执行器读取）
# ═══════════════════════════════════════════════════════════

_pending_image_b64: str = None
_pending_image_type: str = None


def set_pending_image(b64: str, mime_type: str = "image/jpeg"):
    """存入待分析图片（由页面在调用 agent_chat_stream 之前设置）"""
    global _pending_image_b64, _pending_image_type
    _pending_image_b64 = b64
    _pending_image_type = mime_type


def clear_pending_image():
    """清除已分析图片"""
    global _pending_image_b64, _pending_image_type
    _pending_image_b64 = None
    _pending_image_type = None

# ═══════════════════════════════════════════════════════════
# Agent 系统提示词
# ═══════════════════════════════════════════════════════════

AGENT_SYSTEM_PROMPT = """你是"安全小海"，一个建筑工地安全助手Agent。你服务一线工友，回答必须通俗易懂。

## 你的能力
你可以通过调用工具来完成以下任务：
1. **搜索安全规范** — 当工友问安全知识问题时，先搜索规范库
2. **分析工地隐患** — 当工友上传工地照片时，调用 analyze_construction_image 工具进行视觉分析
3. **生成培训材料** — 当工友需要安全培训内容时
4. **应急指导** — 当工友描述紧急情况时

## 核心原则
1. **先说人话**：用大白话回答，300字以内，方便手机阅读
2. **回答问题前先想**：这个问题需要查规范吗？需要就调 search_regulations
3. **不确定就诚实说**：如果工具返回的信息不够，告诉工友"这个我不太确定，建议问现场安全员"
4. **紧急情况优先**：如果工友描述的情况像紧急事故，先给应急指导
5. **不要编造规范条文**：只引用工具返回的实际规范内容
6. **工友上传了照片**：如果用户消息包含"上传了工地照片"或"📷"标记，说明工友需要分析这张照片——必须调用 analyze_construction_image 工具

## 可用工种
架子工、电工、焊工、起重工、信号工、模板工、钢筋工、混凝土工、砌筑工、抹灰工、油漆工、防水工、管道工、挖掘机司机、塔吊司机"""

# ═══════════════════════════════════════════════════════════
# Tool Definitions (OpenAI Function Calling 格式)
# ═══════════════════════════════════════════════════════════

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_regulations",
            "description": "搜索建筑安全规范知识库，获取相关规范条文。当工友问'怎么做''什么要求''规范是什么'等知识性问题时调用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "搜索关键词或自然语言问题，如'高处作业安全带挂点要求'"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_training_material",
            "description": "为指定工种和主题生成安全培训内容（包含大纲、知识点讲解和测验题）。",
            "parameters": {
                "type": "object",
                "properties": {
                    "worker_type": {
                        "type": "string",
                        "description": f"工种，如：{'、'.join(WORKER_TYPES[:8])}等"
                    },
                    "topic": {
                        "type": "string",
                        "description": f"培训主题，如：{'、'.join(TRAINING_TOPICS[:6])}等"
                    },
                    "difficulty": {
                        "type": "string",
                        "enum": ["基础", "进阶", "班组长"],
                        "description": "难度级别"
                    }
                },
                "required": ["worker_type", "topic", "difficulty"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_emergency_guide",
            "description": "获取紧急情况的应急处理指导。当工友描述事故、伤害、危险情况时调用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "emergency_type": {
                        "type": "string",
                        "description": f"紧急情况类型，如：{'、'.join(EMERGENCY_TYPES[:8])}等"
                    },
                    "description": {
                        "type": "string",
                        "description": "工友描述的现场情况（可选）"
                    }
                },
                "required": ["emergency_type"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_construction_image",
            "description": "分析工友上传的工地照片，识别安全隐患（7大类检查：人员防护、高处作业、临时用电、机械设备、物料堆放、基坑边坡、消防安全）。当用户上传了工地照片并请AI看时，必须调用此工具。",
            "parameters": {
                "type": "object",
                "properties": {
                    "description": {
                        "type": "string",
                        "description": "工友对照片的补充描述，如拍摄位置、关注的区域等（可选）"
                    }
                },
                "required": []
            }
        }
    },
]

# ═══════════════════════════════════════════════════════════
# Tool 执行器
# ═══════════════════════════════════════════════════════════

def execute_tool(tool_name: str, tool_args: dict) -> str:
    """执行指定的工具并返回结果字符串"""
    log("INFO", f"Agent tool call: {tool_name}({json.dumps(tool_args, ensure_ascii=False)[:200]})")

    if tool_name == "search_regulations":
        kb = get_knowledge_base()
        if not kb.is_ready():
            return "⚠️ 知识库当前不可用，请基于通用知识回答，并告知工友'规范库暂未就绪，以下回答基于通用知识，建议核实'。"
        results = kb.search_formatted(tool_args["query"])
        if not results:
            return "未在规范库中找到直接匹配的内容。请基于通用建筑安全知识回答，并告知工友'建议咨询现场安全员核实'。"
        return f"以下是从建筑安全规范库中检索到的相关内容：\n\n{results}"

    elif tool_name == "generate_training_material":
        result = generate_training(
            worker_type=tool_args["worker_type"],
            topic=tool_args["topic"],
            difficulty=tool_args.get("difficulty", "基础"),
        )
        if not result.get("success"):
            return f"培训内容生成失败：{result.get('error', '未知错误')}"
        return json.dumps(result, ensure_ascii=False, indent=2)

    elif tool_name == "get_emergency_guide":
        result = generate_emergency_guide(
            emergency_type=tool_args["emergency_type"],
            description=tool_args.get("description", ""),
        )
        if not result.get("success"):
            return f"应急指导生成失败：{result.get('error', '未知错误')}"
        return json.dumps(result, ensure_ascii=False, indent=2)

    elif tool_name == "analyze_construction_image":
        if not _pending_image_b64:
            return (
                "⚠️ 未检测到上传的图片。"
                "请告知工友：请先在页面左侧上传工地照片，再描述需要分析的内容。"
            )
        result = analyze_image(
            image_base64=_pending_image_b64,
            image_type=_pending_image_type or "image/jpeg",
            user_description=tool_args.get("description", ""),
        )
        clear_pending_image()
        if not result.get("success"):
            return f"图片分析失败：{result.get('error', '未知错误')}"
        # 提取关键信息返回
        summary_text = {
            "分析结论": result.get("summary", ""),
            "发现隐患数": len(result.get("hazards", [])),
            "隐患详情": result.get("hazards", []),
            "符合规范": result.get("positive_findings", []),
            "是否紧急": result.get("requires_immediate_action", False),
        }
        return json.dumps(summary_text, ensure_ascii=False, indent=2)

    else:
        return f"未知工具: {tool_name}"


# ═══════════════════════════════════════════════════════════
# Agent 调度循环（流式输出）
# ═══════════════════════════════════════════════════════════

def agent_chat_stream(
    user_message: str,
    history: List[Dict] = None,
    max_tool_rounds: int = 3,
) -> Generator[Dict, None, None]:
    """
    Agent 流式对话。

    Yields:
        {"type": "thinking", "content": "正在分析..."}
        {"type": "tool_call", "tool": "search_regulations", "args": {...}}
        {"type": "tool_result", "tool": "...", "content": "..."}
        {"type": "delta", "content": "回答文本片段"}
        {"type": "done", "full_text": "完整回答"}
        {"type": "error", "content": "错误信息"}
    """
    llm = get_llm_client()
    history = history or []

    # 构建消息列表
    messages = [{"role": "system", "content": AGENT_SYSTEM_PROMPT}]
    # 注入最近对话历史
    for msg in history[-10:]:
        messages.append(msg)
    messages.append({"role": "user", "content": user_message})

    try:
        yield {"type": "thinking", "content": "正在分析您的问题..."}

        tool_rounds = 0
        while True:
            # 流式调用（stream=True），同时返回文本增量与工具调用
            stream = llm.client.chat.completions.create(
                model=llm.chat_model,
                messages=messages,
                tools=TOOLS,
                tool_choice="auto",
                temperature=0.3,
                max_tokens=2000,
                timeout=llm.timeout,
                stream=True,
            )

            content_parts = []
            tool_calls_map = {}  # index -> {id, name, arguments}

            for chunk in stream:
                if not chunk.choices:
                    continue
                delta = chunk.choices[0].delta
                if delta is None:
                    continue

                # 文本增量 → 逐字流式输出
                if delta.content:
                    content_parts.append(delta.content)
                    yield {"type": "delta", "content": delta.content}

                # 工具调用增量（分片累积）
                if delta.tool_calls:
                    for tcd in delta.tool_calls:
                        idx = tcd.index if tcd.index is not None else 0
                        entry = tool_calls_map.setdefault(
                            idx, {"id": "", "name": "", "arguments": ""}
                        )
                        if tcd.id:
                            entry["id"] = tcd.id
                        if tcd.function:
                            if tcd.function.name:
                                entry["name"] += tcd.function.name
                            if tcd.function.arguments:
                                entry["arguments"] += tcd.function.arguments

            content = "".join(content_parts)
            calls = [tool_calls_map[i] for i in sorted(tool_calls_map.keys())]

            # 无工具调用 → 最终回答（文本已流式输出，这里收尾）
            if not calls:
                full_text = content or (
                    "抱歉，我暂时无法回答这个问题，请换个方式描述或联系现场安全员。"
                )
                yield {"type": "done", "full_text": full_text}
                return

            # 达到最大轮次仍要求工具 → 停止调度，直接输出已有内容
            if tool_rounds >= max_tool_rounds:
                full_text = content or (
                    "抱歉，这个任务有点复杂，我暂时处理不了，建议联系现场安全员。"
                )
                yield {"type": "done", "full_text": full_text}
                return

            tool_rounds += 1

            # 追加 assistant 的工具调用消息（dict格式，兼容DeepSeek）
            messages.append({
                "role": "assistant",
                "content": content or None,
                "tool_calls": [
                    {
                        "id": c["id"] or f"call_{i}",
                        "type": "function",
                        "function": {"name": c["name"], "arguments": c["arguments"]},
                    }
                    for i, c in enumerate(calls)
                ],
            })

            # 逐个执行工具
            for i, c in enumerate(calls):
                tool_name = c["name"]
                try:
                    tool_args = json.loads(c["arguments"]) if c["arguments"] else {}
                except json.JSONDecodeError:
                    tool_args = {}

                yield {"type": "tool_call", "tool": tool_name, "args": tool_args}

                tool_result = execute_tool(tool_name, tool_args)

                yield {
                    "type": "tool_result",
                    "tool": tool_name,
                    "content": tool_result[:500] + ("..." if len(tool_result) > 500 else ""),
                }

                messages.append({
                    "role": "tool",
                    "tool_call_id": c["id"] or f"call_{i}",
                    "content": tool_result,
                })

    except Exception as e:
        log("ERROR", f"Agent chat failed [{type(e).__name__}]: {str(e)[:200]}")
        from utils.safety_guard import FALLBACK_MESSAGES
        yield {"type": "error", "content": FALLBACK_MESSAGES.get("unknown_error", str(e))}
    finally:
        # 无论本轮是否调用视觉工具，结束后都清空待分析图片，防止残留到下一轮/其他用户
        clear_pending_image()


# 便捷方法：返回完整文本（非流式）
def agent_chat(
    user_message: str,
    history: List[Dict] = None,
) -> str:
    """Agent 非流式对话，返回完整回答文本"""
    full_text = ""
    for event in agent_chat_stream(user_message, history):
        if event["type"] == "done":
            full_text = event["full_text"]
            break
        elif event["type"] == "error":
            return event["content"]
    return full_text
