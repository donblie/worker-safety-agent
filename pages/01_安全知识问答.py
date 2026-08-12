"""
模块一：安全知识问答
工友输入问题 → RAG检索知识库 → LLM基于规范回答
"""
import streamlit as st
import sys
import os

# 确保core模块路径可访问
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.llm_client import get_llm_client
from core.knowledge_base import get_knowledge_base
from utils.prompts import QA_SYSTEM_PROMPT
from utils.safety_guard import (
    validate_input,
    FALLBACK_MESSAGES,
    SubmitGuard,
)
from utils.ui_components import inject_shared_styles, page_header, page_footer
from utils.json_parser import is_api_error_response

# ── 页面配置 ─────────────────────────────────
st.set_page_config(
    page_title="安全知识问答 - 工友安全守护",
    page_icon="💬",
    layout="wide",
)

inject_shared_styles()

# ── 初始化 ───────────────────────────────────
if "qa_history" not in st.session_state:
    st.session_state.qa_history = []  # 对话历史

if "qa_submit_guard" not in st.session_state:
    st.session_state.qa_submit_guard = SubmitGuard(cooldown_seconds=1.5)

# ── 页面标题 ─────────────────────────────────
page_header("💬 安全知识问答", "问你想问的安全问题，AI帮你在规范中找答案")

# ── 知识库状态检查 ───────────────────────────
try:
    kb = get_knowledge_base()
    kb_ready = kb.is_ready()
except Exception:
    kb_ready = False

if not kb_ready:
    st.warning("""
    ⚠️ **知识库尚未初始化**

    当前使用纯AI模式回答（基于DeepSeek通用知识，不检索规范库）。
    答案可能不够精准。建议先加载安全规范文档到知识库。

    点击侧边栏返回首页查看更多信息。
    """)

# ── 示例问题 ─────────────────────────────────
with st.expander("💡 试试这些问题（点击展开）"):
    examples = [
        "高处作业安全带应该怎么系？",
        "脚手架剪刀撑有什么要求？",
        "临时用电三级配电是什么意思？",
        "安全帽多久需要更换一次？",
        "电焊作业需要注意哪些安全事项？",
        "基坑边多少距离内不能堆载？",
    ]
    cols = st.columns(3)
    for i, example in enumerate(examples):
        with cols[i % 3]:
            if st.button(example, key=f"ex_{i}", use_container_width=True):
                st.session_state.current_question = example
                st.rerun()

# ── 对话显示区域 ────────────────────────────
chat_container = st.container()

with chat_container:
    for msg in st.session_state.qa_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# ── 输入区域 ─────────────────────────────────
st.markdown("---")

# 合并两个来源的问题：chat_input输入 或 示例按钮点击
user_question = st.chat_input(
    placeholder="输入您的安全问题，比如：高处作业安全带怎么挂？",
)

# 如果chat_input没有输入但有点击示例问题，使用示例问题
clicked_question = st.session_state.pop("current_question", None)
if not user_question and clicked_question:
    user_question = clicked_question

# ── 处理用户输入 ────────────────────────────
if user_question:
    # 兜底校验
    error_msg = validate_input(user_question)
    if error_msg:
        st.error(error_msg)
    else:
        guard = st.session_state.qa_submit_guard
        if not guard.can_submit():
            st.warning(f"⏳ 请稍等 {guard.get_remaining_cooldown():.0f} 秒后再提问")
        else:
            guard.mark_submitted()

            # 显示用户问题，初始化LLM客户端
            st.session_state.qa_history.append({"role": "user", "content": user_question})
            llm = get_llm_client()

            with st.status("🔍 正在处理您的问题...", expanded=True) as status:
                try:
                    # 步骤1：RAG检索
                    context = ""
                    search_results = []
                    if kb_ready:
                        status.write("📚 检索知识库...")
                        search_results = kb.search(user_question)
                        if search_results:
                            context = kb.search_formatted(user_question)
                            status.write(f"✅ 找到 {len(search_results)} 条相关规范段落")
                        else:
                            status.write("⚠️ 未在知识库中找到直接匹配，使用通用知识回答")

                    # 步骤1.5：注入对话历史（近3轮，支持追问）
                    history_context = ""
                    if len(st.session_state.qa_history) >= 3:
                        recent = st.session_state.qa_history[-7:]  # 最近3轮+当前问题
                        history_context = "【对话历史】\n" + "\n".join(
                            f"{'👷工友' if m['role']=='user' else '🤖助手'}: {m['content'][:300]}"
                            for m in recent
                        ) + "\n\n"

                    # 步骤2：构建消息并通知
                    status.write("🤖 DeepSeek 正在组织回答...")
                    status.update(label="💬 AI正在回答...", state="running")

                except Exception as e:
                    status.update(label=f"❌ 检索失败: {str(e)[:50]}", state="error")
                    context = ""
                    history_context = ""

            # 步骤3：流式输出（在status外，实时显示）
            with st.chat_message("assistant"):
                if context:
                    stream = llm.chat_with_context_stream(
                        system_prompt=QA_SYSTEM_PROMPT,
                        user_message=user_question,
                        context=context,
                        history=history_context,
                    )
                else:
                    fallback_prompt = (
                        QA_SYSTEM_PROMPT +
                        "\n\n注意：当前知识库中未找到该问题的相关规范，请基于你的建筑安全知识回答，"
                        "并在回答末尾标注'⚠️ 未在规范库中找到直接相关条文，以上内容基于通用建筑安全知识，建议咨询现场安全员核实。'"
                    )
                    msg_with_history = user_question
                    if history_context:
                        msg_with_history = history_context + "\n【工友的问题】\n" + user_question
                    stream = llm.chat_stream(
                        system_prompt=fallback_prompt,
                        user_message=msg_with_history,
                    )

                full_answer = st.write_stream(stream)

            # 保存到历史
            st.session_state.qa_history.append({
                "role": "assistant",
                "content": full_answer or ""
            })

            # 重新运行以刷新UI（显示完整对话和status完成状态）
            st.rerun()

# ── 底部操作 ─────────────────────────────────
st.markdown("---")
col1, col2 = st.columns([1, 1])
with col1:
    if st.button("🗑️ 清除对话", use_container_width=True):
        st.session_state.qa_history = []
        st.rerun()
with col2:
    page_footer(show_home=False)
