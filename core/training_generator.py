"""
安全培训助手模块
- 根据工种+主题 → 检索规范 → 生成培训大纲、内容和测验
- 输出: 结构化培训材料（大纲 + 知识点 + 测验题）
"""
import json

from core.llm_client import get_llm_client
from core.knowledge_base import get_knowledge_base
from utils.prompts import TRAINING_SYSTEM_PROMPT


# 工种列表（建筑工地常见工种）
WORKER_TYPES = [
    "架子工", "电工", "焊工", "起重工", "信号工",
    "模板工", "钢筋工", "混凝土工", "砌筑工", "抹灰工",
    "油漆工", "防水工", "管道工", "挖掘机司机", "塔吊司机",
]

# 培训主题
TRAINING_TOPICS = [
    "个人防护装备使用", "高处作业安全", "临时用电安全",
    "脚手架搭设安全", "消防安全", "机械设备操作安全",
    "基坑支护安全", "模板工程安全", "焊接与切割安全",
    "起重吊装安全", "有限空间作业安全", "夏季防暑降温",
    "冬季施工安全", "应急处理知识", "安全法律法规",
]

# 难度级别
DIFFICULTY_LEVELS = ["基础", "进阶", "班组长"]


def generate_training(
    worker_type: str,
    topic: str,
    difficulty: str = "基础",
) -> dict:
    """
    生成安全培训内容

    返回格式:
    {
        "success": True/False,
        "error": "错误信息（如果失败）",
        "title": "培训标题",
        "target_audience": "适用工种",
        "duration": "建议时长",
        "outline": [...],
        "content": [...],
        "quiz": [...],
        "references": [...]  # 引用的规范
    }
    """
    kb = get_knowledge_base()
    llm = get_llm_client()

    # 步骤1: 检索相关规范
    search_query = f"{worker_type} {topic} 安全规范"
    context = ""
    if kb.is_ready():
        context = kb.search_formatted(search_query)

    # 步骤2: 构建用户消息
    user_message = f"""请为以下培训需求生成安全培训内容：

【工种】{worker_type}
【培训主题】{topic}
【难度级别】{difficulty}

【培训要求】
1. 内容要通俗易懂（工友多为初中文化水平）
2. 每个知识点都要包含"常见错误做法"
3. 关键数据引用安全规范标准
4. 测验题要实用，考"碰到这种情况你怎么办"而非死记硬背"""

    if context:
        user_message += f"\n\n【参考规范】\n{context}"
    else:
        user_message += "\n\n注意：当前知识库未检索到相关规范，请基于通用建筑安全知识生成培训内容。"

    try:
        response = llm.chat(
            system_prompt=TRAINING_SYSTEM_PROMPT,
            user_message=user_message,
            max_tokens=3000,
        )

        # 检查兜底错误
        if any(keyword in str(response) for keyword in
               ["⏱️", "🔑", "🌐", "⏳", "😞", "服务繁忙", "API密钥"]):
            return {
                "success": False,
                "error": str(response),
            }

        # 解析JSON
        json_str = str(response).strip()
        if json_str.startswith("```"):
            start = json_str.find("{")
            end = json_str.rfind("}") + 1
            if start >= 0 and end > start:
                json_str = json_str[start:end]

        result = json.loads(json_str)
        result["success"] = True
        return result

    except json.JSONDecodeError:
        return {
            "success": True,
            "title": f"{worker_type} - {topic}安全培训",
            "target_audience": worker_type,
            "duration": "约30分钟",
            "raw_content": str(response),
            "parse_error": True,
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"生成培训内容时出错: {str(e)}",
        }
