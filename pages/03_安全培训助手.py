"""
模块三：安全培训助手
选择工种+主题 → 自动生成培训内容 + 随堂测验
"""
import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.training_generator import (
    generate_training,
    WORKER_TYPES,
    TRAINING_TOPICS,
    DIFFICULTY_LEVELS,
)
from utils.ui_components import inject_shared_styles, page_header, page_footer


st.set_page_config(page_title="安全培训助手 - 工友安全守护", page_icon="📚", layout="wide")

inject_shared_styles()

page_header("📚 安全培训助手", "选工种、定主题，AI自动生成培训内容+测验题")

# ── 参数选择 ─────────────────────────────────
col1, col2, col3 = st.columns(3)

with col1:
    worker_type = st.selectbox(
        "选择工种",
        WORKER_TYPES,
        index=0,
    )

with col2:
    topic = st.selectbox(
        "培训主题",
        TRAINING_TOPICS,
        index=0,
    )

with col3:
    difficulty = st.selectbox(
        "难度级别",
        DIFFICULTY_LEVELS,
        index=0,
    )

# ── 生成按钮 ─────────────────────────────────
gen_btn = st.button("🎓 生成培训内容", type="primary", use_container_width=True)

if gen_btn:
    with st.spinner("🔄 正在生成培训内容..."):
        result = generate_training(
            worker_type=worker_type,
            topic=topic,
            difficulty=difficulty,
        )

        if result.get("success"):
            st.session_state.training_result = result
        else:
            st.error(result.get("error", "生成失败，请重试"))

# ── 显示结果 ─────────────────────────────────
if "training_result" in st.session_state:
    result = st.session_state.training_result

    st.markdown("---")

    # 标题信息
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("培训标题", result.get("title", "未命名"))
    with col2:
        st.metric("适用对象", result.get("target_audience", worker_type))
    with col3:
        st.metric("建议时长", result.get("duration", "约30分钟"))

    st.markdown("---")

    # 培训大纲
    outline = result.get("outline", [])
    if outline:
        st.markdown("### 📋 培训大纲")
        for item in outline:
            st.markdown(f"- {item}")

    st.markdown("---")

    # 详细内容
    content = result.get("content", [])
    if content:
        st.markdown("### 📖 培训内容")
        for section in content:
            with st.expander(
                f"📌 {section.get('section', '未命名章节')}",
                expanded=(len(content) <= 3),
            ):
                st.markdown(section.get("body", ""))

                key_points = section.get("key_points", [])
                if key_points:
                    st.markdown("**🔑 关键要点：**")
                    for kp in key_points:
                        st.markdown(f"- {kp}")

                mistakes = section.get("common_mistakes", [])
                if mistakes:
                    st.markdown("**⚠️ 常见错误：**")
                    for m in mistakes:
                        st.markdown(f"- ❌ {m}")

    st.markdown("---")

    # 测验题
    quiz = result.get("quiz", [])
    if quiz:
        st.markdown("### 📝 随堂测验")
        st.markdown("*选择答案后点击空白处查看对错*")

        for i, q in enumerate(quiz, 1):
            st.markdown(f"**{i}. {q.get('question', '')}**")
            options = q.get("options", [])
            answer = q.get("answer", "")
            explanation = q.get("explanation", "")

            # 用radio展示选项
            user_choice = st.radio(
                f"第{i}题答案",
                options,
                key=f"quiz_{i}",
                index=None,
                label_visibility="collapsed",
            )

            if user_choice:
                if user_choice.startswith(answer):
                    st.success(f"✅ 正确！{explanation}")
                else:
                    st.error(f"❌ 不对。正确答案是 {answer}。{explanation}")

            st.markdown("---")

    # 非结构化处理
    if result.get("parse_error"):
        st.info("⚠️ AI返回了非结构化内容，以下是原文：")
        st.markdown(result.get("raw_content", ""))

# ── 底部操作 ─────────────────────────────────
st.markdown("---")
col1, col2 = st.columns(2)
with col1:
    if st.button("🗑️ 清除内容", use_container_width=True):
        st.session_state.pop("training_result", None)
        st.rerun()
with col2:
    page_footer(show_home=False)
