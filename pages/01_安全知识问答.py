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

# 如果有示例问题点击，填入输入框
default_question = st.session_state.get("current_question", "")
if default_question:
    st.session_state.pop("current_question")

user_question = st.chat_input(
    placeholder="输入您的安全问题，比如：高处作业安全带怎么挂？",
)

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

            # 显示用户问题
            st.session_state.qa_history.append({"role": "user", "content": user_question})

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

                    # 步骤2：LLM生成
                    llm = get_llm_client()
                    status.write("🤖 DeepSeek 正在组织回答...")

                    if context:
                        answer = llm.chat_with_context(
                            system_prompt=QA_SYSTEM_PROMPT,
                            user_message=user_question,
                            context=context,
                        )
                    else:
                        fallback_prompt = (
                            QA_SYSTEM_PROMPT +
                            "\n\n注意：当前知识库中未找到该问题的相关规范，请基于你的建筑安全知识回答，"
                            "并在回答末尾标注'⚠️ 未在规范库中找到直接相关条文，以上内容基于通用建筑安全知识，建议咨询现场安全员核实。'"
                        )
                        answer = llm.chat(
                            system_prompt=fallback_prompt,
                            user_message=user_question,
                        )

                    status.update(label="✅ 回答完成!", state="complete")

                    # 步骤3：检查返回结果（兜底：如果LLM返回了错误信息）
                    if any(err_keyword in str(answer) for err_keyword in
                           ["⏱️", "🔑", "🌐", "⏳", "😞"]):
                        st.session_state.qa_history.append({
                            "role": "assistant",
                            "content": str(answer)
                        })
                    else:
                        st.session_state.qa_history.append({
                            "role": "assistant",
                            "content": str(answer)
                        })

                except Exception as e:
                    error_response = FALLBACK_MESSAGES["unknown_error"]
                    st.session_state.qa_history.append({
                        "role": "assistant",
                        "content": f"{error_response}\n\n> 错误详情：{str(e)}"
                    })

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
