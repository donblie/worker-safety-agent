"""
应急处理指导模块
- 根据紧急情况类型 → 匹配应急预案 → 生成分步骤指导
- 输出: 结构化应急步骤 + 禁止事项 + 后续处理
"""
import json

from core.llm_client import get_llm_client
from core.knowledge_base import get_knowledge_base
from utils.prompts import EMERGENCY_SYSTEM_PROMPT
from utils.safety_guard import is_high_risk_emergency, get_high_risk_disclaimer
from utils.json_parser import extract_json, is_api_error_response


# 预定义的紧急情况类型
EMERGENCY_TYPES = [
    "触电", "高处坠落", "物体打击", "坍塌",
    "火灾", "中暑", "机械伤害", "化学品伤害",
    "有限空间窒息", "基坑进水", "管涌",
    "脚手架倒塌", "塔吊倾覆", "爆炸",
]

# 每种紧急情况的简短描述模板（供用户快速选择）
EMERGENCY_DESCRIPTIONS = {
    "触电": "人员触电，可能倒地或粘在电源上",
    "高处坠落": "人员从高处跌落，可能骨折或内伤",
    "物体打击": "被坠落物或飞溅物击中",
    "坍塌": "脚手架/模板/基坑/墙体坍塌，可能有人被埋",
    "火灾": "现场起火，可能蔓延",
    "中暑": "高温环境下头晕、恶心、意识模糊",
    "机械伤害": "肢体被机械卷入、切割或挤压",
    "化学品伤害": "皮肤或眼睛接触化学品，或吸入有毒气体",
    "有限空间窒息": "在地下室/管沟/罐体内昏迷",
    "基坑进水": "基坑大量进水，可能塌方",
    "管涌": "基坑底部冒水冒沙",
    "脚手架倒塌": "脚手架部分或全部倒塌",
    "塔吊倾覆": "塔式起重机倾斜或倒塌",
    "爆炸": "气瓶/压力容器/粉尘爆炸",
}


def generate_emergency_guide(
    emergency_type: str,
    description: str = "",
    people_count: int = 1,
) -> dict:
    """
    生成应急处理指导

    返回格式:
    {
        "success": True/False,
        "error": "错误信息",
        "emergency": "紧急情况类型",
        "first_thing": "第一件要做的事",
        "steps": [{"step": N, "action": "", "detail": "", "why": "", "warning": ""}],
        "donts": [...],
        "when_to_call_120": "",
        "after_emergency": "",
        "disclaimer": "高风险免责声明（高风险时自动追加）"
    }
    """
    kb = get_knowledge_base()
    llm = get_llm_client()

    # 步骤1: 检索相关应急预案
    context = ""
    if kb.is_ready():
        context = kb.search_formatted(f"{emergency_type} 应急处理")

    # 步骤2: 构建用户消息
    user_message = f"""请为以下紧急情况生成应急处理指导：

【紧急类型】{emergency_type}
"""

    if description:
        user_message += f"【现场描述】{description}\n"
    if people_count > 1:
        user_message += f"【受伤人数】{people_count}人\n"

    user_message += """
【重要要求】
1. 步骤要简短、清晰——紧急情况下必须一眼看懂
2. 第一步必须是最关键的事
3. "绝对不能做的事"要和"该做的事"一样重要
4. 明确什么情况下必须打120
5. 语气冷静坚定"""

    if context:
        user_message += f"\n\n【参考应急预案】\n{context}"

    try:
        response = llm.chat(
            system_prompt=EMERGENCY_SYSTEM_PROMPT,
            user_message=user_message,
            max_tokens=2000,
        )

        # 检查兜底错误
        if is_api_error_response(response):
            return {
                "success": False,
                "error": str(response),
            }

        result = extract_json(str(response))

        # 高风险紧急情况自动追加免责声明
        if is_high_risk_emergency(emergency_type):
            result["disclaimer"] = get_high_risk_disclaimer()
        else:
            result["disclaimer"] = (
                "\n\n---\n⚠️ 应急指导由AI生成，紧急情况下请以现场安全员和急救人员指令为准。"
            )

        result["success"] = True
        return result

    except json.JSONDecodeError:
        return {
            "success": True,
            "emergency": emergency_type,
            "raw_content": str(response),
            "parse_error": True,
            "disclaimer": get_high_risk_disclaimer() if is_high_risk_emergency(emergency_type) else "",
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"生成应急指导时出错: {str(e)}",
        }
