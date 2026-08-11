"""
工地隐患识别模块
- 图片上传 → Qwen-VL 视觉分析 → RAG规范对照 → 结构化隐患报告
- 双引擎：视觉识别（找出问题）+ 知识库检索（匹配规范）
"""
import json
import base64
from io import BytesIO
from PIL import Image

from core.llm_client import get_vision_client
from core.knowledge_base import get_knowledge_base
from utils.prompts import VISION_SYSTEM_PROMPT
from utils.safety_guard import get_high_risk_disclaimer
from utils.json_parser import extract_json, is_api_error_response


def encode_image(image_file) -> tuple:
    """
    上传图片 → base64编码（自动压缩大图）
    返回: (base64_string, mime_type) 或 (None, error_message)
    """
    try:
        img = Image.open(image_file)

        # 压缩大图
        max_size = 2000
        if max(img.size) > max_size:
            ratio = max_size / max(img.size)
            new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
            img = img.resize(new_size, Image.LANCZOS)

        # 统一转RGB
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        buffer = BytesIO()
        img.save(buffer, format="JPEG", quality=85)
        img_bytes = buffer.getvalue()

        if len(img_bytes) > 10 * 1024 * 1024:
            return None, "图片过大（超过10MB），请降低分辨率后重试"

        b64_str = base64.b64encode(img_bytes).decode("utf-8")
        return b64_str, "image/jpeg"

    except Exception as e:
        return None, f"图片处理失败: {str(e)}"


def analyze_image(
    image_base64: str,
    image_type: str = "image/jpeg",
    user_description: str = "",
) -> dict:
    """
    工地图片隐患分析

    流程:
    1. Qwen-VL 视觉分析图片 → 识别隐患
    2. RAG 检索相关规范 → 匹配条文
    3. 组装结构化报告

    返回:
    {
        "success": bool,
        "summary": "总体概述",
        "hazards": [{type, severity, description, regulation_ref, fix, deadline}],
        "positive_findings": [...],
        "requires_immediate_action": bool,
        "disclaimer": "免责声明"
    }
    """
    vision = get_vision_client()
    kb = get_knowledge_base()

    # ── 步骤1: Qwen-VL看图分析 ─────────────────
    user_msg = "请严格按照JSON格式输出分析结果。"
    if user_description:
        user_msg = f"工友补充描述：{user_description}\n\n{user_msg}"

    try:
        raw_response = vision.analyze_image(
            system_prompt=VISION_SYSTEM_PROMPT,
            image_base64=image_base64,
            image_type=image_type,
            user_message=user_msg,
            max_tokens=2000,
        )

        # 兜底检查
        if is_api_error_response(raw_response):
            return {"success": False, "error": str(raw_response)}

        # ── 步骤2: 解析视觉分析结果 ─────────────
        result = extract_json(str(raw_response))

        # ── 步骤3: RAG检索相关规范 ──────────────
        if kb.is_ready():
            # 根据识别出的隐患类型检索规范
            hazard_types = [h.get("type", "") for h in result.get("hazards", [])]
            search_query = " ".join(hazard_types[:3]) if hazard_types else "施工现场安全隐患"
            context = kb.search_formatted(search_query, top_k=3)

            if context:
                # 用LLM将检索到的规范匹配到各隐患
                result["regulation_context"] = context

        # ── 步骤4: 组装最终报告 ────────────────
        result["success"] = True

        # 高风险追加免责声明
        has_high_risk = any(
            h.get("severity") == "高" for h in result.get("hazards", [])
        )
        if has_high_risk or result.get("requires_immediate_action"):
            result["disclaimer"] = get_high_risk_disclaimer()
        else:
            result["disclaimer"] = (
                "\n\n---\n"
                "⚠️ 本分析由AI生成，仅供参考。建议由现场安全员进行人工复核。"
            )

        return result

    except json.JSONDecodeError:
        # JSON解析失败，返回原始文本作为分析记录
        return {
            "success": True,
            "summary": "AI视觉分析完成（非结构化输出）",
            "hazards": [],
            "raw_response": str(raw_response),
            "positive_findings": [],
            "requires_immediate_action": False,
            "disclaimer": (
                "\n\n---\n"
                "⚠️ AI返回了非结构化结果，以上分析仅供参考。"
            ),
        }
    except Exception as e:
        return {"success": False, "error": f"分析过程出错: {str(e)}"}
