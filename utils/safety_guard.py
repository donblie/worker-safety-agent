"""
全局兜底逻辑模块 (Safety Guard)
确保每个异常路径都有退路，演示现场不翻车
"""
import time
import functools
from typing import Any, Callable, Optional
from openai import (
    AuthenticationError,
    RateLimitError,
    APITimeoutError,
    APIConnectionError,
    APIError,
)
from utils.logger import log


# ── 降级话术模板 ──────────────────────────────

FALLBACK_MESSAGES = {
    "timeout": (
        "⏱️ AI服务响应较慢，请稍候...\n\n"
        "如果30秒后仍无响应，请点击重试按钮。"
    ),
    "auth_error": (
        "🔑 API密钥配置异常。\n\n"
        "请联系系统管理员检查DeepSeek API Key配置。"
    ),
    "network_error": (
        "🌐 网络连接失败，AI服务暂时不可用。\n\n"
        "请检查网络连接后重试。\n\n"
        "如紧急需要安全指导，请拨打安全热线或联系现场安全员。"
    ),
    "rate_limit": (
        "⏳ 使用太频繁啦，请稍等几秒后再试。"
    ),
    "unknown_error": (
        "😞 系统遇到了技术问题，请尝试：\n"
        "1. 刷新页面重试\n"
        "2. 联系现场安全员\n"
        "3. 拨打安全热线"
    ),
    "rag_no_results": (
        "⚠️ 未在规范库中找到相关内容。\n\n"
        "以下回答基于通用建筑安全知识，**建议咨询现场安全员核实**。\n\n"
    ),
    "image_not_construction": (
        "📷 无法识别图片中的工地场景。\n\n"
        "请确保：\n"
        "• 光线充足\n"
        "• 拍摄对象清晰\n"
        "• 画面中包含建筑物或施工场景\n\n"
        "如不是工地照片，暂不支持分析。"
    ),
    "image_too_large": (
        "📷 图片文件过大。\n\n"
        "请压缩后重新上传（建议不超过10MB），或降低相机分辨率后重新拍摄。"
    ),
    "not_safety_related": (
        "🛡️ 我是施工安全助手，暂时只能回答工地安全相关的问题。\n\n"
        "您可以问我这些方面的问题：\n"
        "• 安全规范和操作规程\n"
        "• 安全隐患排查\n"
        "• 安全培训学习\n"
        "• 应急处置指导\n"
        "• 个人防护装备使用"
    ),
    "empty_input": (
        "😊 请输入您的安全问题，或者点击下方示例问题快速开始。"
    ),
}


# ── 高风险触发条件 ────────────────────────────

HIGH_RISK_EMERGENCY_TYPES = {"坍塌", "触电", "火灾", "爆炸", "有限空间窒息", "基坑进水"}

HIGH_RISK_DISCLAIMER = (
    "\n\n---\n"
    "🚨 **此情况属于高风险，AI分析不可替代专业人员判断。**\n"
    "请在采取行动前，务必报告现场安全员或项目经理进行人工确认。"
)


def get_high_risk_disclaimer() -> str:
    """获取高风险免责声明"""
    return HIGH_RISK_DISCLAIMER


def is_high_risk_emergency(emergency_type: str) -> bool:
    """判断是否为高风险紧急情况"""
    return emergency_type in HIGH_RISK_EMERGENCY_TYPES


def should_add_disclaimer(severity: str = None, requires_immediate: bool = False,
                          emergency_type: str = None) -> bool:
    """判断是否需要追加高风险审核提示"""
    if severity == "高":
        return True
    if requires_immediate:
        return True
    if emergency_type and is_high_risk_emergency(emergency_type):
        return True
    return False


# ── API调用兜底装饰器 ─────────────────────────

def safe_api_call(fallback_key: str = "unknown_error"):
    """
    API调用的安全包裹函数
    捕获所有OpenAI SDK可能抛出的异常，返回降级话术
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)
            except APITimeoutError:
                return FALLBACK_MESSAGES["timeout"]
            except AuthenticationError:
                return FALLBACK_MESSAGES["auth_error"]
            except APIConnectionError:
                return FALLBACK_MESSAGES["network_error"]
            except RateLimitError:
                return FALLBACK_MESSAGES["rate_limit"]
            except APIError as e:
                log("ERROR", f"APIError [{type(e).__name__}]: {str(e)[:200]}")
                return FALLBACK_MESSAGES.get(fallback_key, FALLBACK_MESSAGES["unknown_error"])
            except Exception as e:
                log("ERROR", f"Unexpected [{type(e).__name__}]: {str(e)[:200]}")
                return FALLBACK_MESSAGES.get(fallback_key, FALLBACK_MESSAGES["unknown_error"])
        return wrapper
    return decorator


# ── 输入校验 ──────────────────────────────────

def validate_image(file_size: int, file_type: str) -> Optional[str]:
    """
    校验上传图片
    返回 None 表示通过；返回 str 表示错误提示
    """
    MAX_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/webp"}

    if file_type.lower() not in ALLOWED_TYPES and not file_type.lower().startswith("image/"):
        return "请上传JPG、PNG或WEBP格式的图片。"
    if file_size > MAX_SIZE:
        return FALLBACK_MESSAGES["image_too_large"]
    return None


def validate_input(text: str) -> Optional[str]:
    """
    校验文本输入
    返回 None 表示通过；返回 str 表示错误提示
    """
    if not text or not text.strip():
        return FALLBACK_MESSAGES["empty_input"]
    if len(text.strip()) < 2:
        return "请至少输入2个字描述您的问题。"
    # 检查是否与安全相关（关键词快速过滤）
    if not _is_safety_related(text.strip()):
        return FALLBACK_MESSAGES["not_safety_related"]
    return None


# ── 安全相关性关键词过滤 ──────────────────────

_SAFETY_KEYWORDS = {
    # 安全对象
    "安全帽", "安全带", "安全网", "安全绳", "安全鞋", "防护", "反光背心", "手套",
    "脚手架", "扣件", "立杆", "横杆", "剪刀撑", "连墙件",
    "配电箱", "电线", "电缆", "漏电", "接地", "触电", "电压", "开关箱",
    "临时用电", "三级配电", "配电", "用电",
    "高处", "临边", "洞口", "基坑", "边坡", "模板", "支架", "支撑",
    "塔吊", "起重机", "施工电梯", "电焊", "气瓶", "切割", "焊接", "吊装",
    "消防", "灭火器", "通道", "逃生", "火灾", "爆炸",
    # 安全动作
    "安全", "隐患", "危险", "整改", "规范", "标准", "检查", "巡检",
    "培训", "应急", "急救", "救援", "事故", "伤害", "坠落",
    "坍塌", "塌方", "中毒", "窒息", "堆载",
    # 工种/场景
    "架子工", "电工", "焊工", "钢筋工", "模板工", "混凝土", "塔吊司机",
    "施工", "工地", "建筑", "现场",
    # 规范相关
    "JGJ", "GB", "条文", "规定",
}


def _is_safety_related(text: str) -> bool:
    """快速关键词匹配判断是否与工地安全相关"""
    # 太短的输入放宽判断（可能是"安全吗""咋整"等口语简问）
    if len(text) < 6:
        return True
    for kw in _SAFETY_KEYWORDS:
        if kw in text:
            return True
    # 无任何安全关键词命中 → 判定为不相关
    return False


# ── 防重复提交 ────────────────────────────────

class SubmitGuard:
    """
    防止用户快速重复点击导致重复提交
    """
    def __init__(self, cooldown_seconds: float = 2.0):
        self.cooldown = cooldown_seconds
        self._last_submit_time = 0.0

    def can_submit(self) -> bool:
        now = time.time()
        if now - self._last_submit_time < self.cooldown:
            return False
        return True

    def mark_submitted(self):
        self._last_submit_time = time.time()

    def get_remaining_cooldown(self) -> float:
        remaining = self.cooldown - (time.time() - self._last_submit_time)
        return max(0, remaining)
