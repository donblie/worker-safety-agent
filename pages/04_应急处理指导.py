"""
模块四：应急处理指导
选择紧急类型 → 分步骤指导 → 该做什么/不该做什么
"""
import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.emergency_guide import (
    generate_emergency_guide,
    EMERGENCY_TYPES,
    EMERGENCY_DESCRIPTIONS,
)
from utils.ui_components import inject_shared_styles, page_header, page_footer


st.set_page_config(page_title="应急处理指导 - 工友安全守护", page_icon="🆘", layout="wide")

inject_shared_styles()

page_header("🆘 应急处理指导", "遇到紧急情况不要慌，跟着步骤一步步来")

# ── 紧急类型选择 ─────────────────────────────
st.markdown("### 🚨 选择紧急情况类型")

# 用卡片式grid展示紧急类型
selected_type = None

# 每行4个
cols_per_row = 4
rows = (len(EMERGENCY_TYPES) + cols_per_row - 1) // cols_per_row

for row in range(rows):
    cols = st.columns(cols_per_row)
    for col_idx in range(cols_per_row):
        idx = row * cols_per_row + col_idx
        if idx < len(EMERGENCY_TYPES):
            etype = EMERGENCY_TYPES[idx]
            desc = EMERGENCY_DESCRIPTIONS.get(etype, "")
            with cols[col_idx]:
                is_high_risk = etype in {"触电", "坍塌", "火灾", "爆炸", "有限空间窒息"}
                style = "border: 2px solid #D32F2F;" if is_high_risk else ""
                btn_label = f"{'🔴' if is_high_risk else '🟡'} {etype}"
                if st.button(btn_label, key=f"emergency_{idx}", use_container_width=True):
                    st.session_state.selected_emergency = etype
                    st.rerun()

# ── 现场描述 ─────────────────────────────────
if "selected_emergency" in st.session_state:
    etype = st.session_state.selected_emergency
    st.markdown("---")
    st.markdown(f"### 🚨 {etype}")

    col1, col2 = st.columns([3, 2])
    with col1:
        description = st.text_area(
            "现场描述（可选）",
            placeholder=f"例：{EMERGENCY_DESCRIPTIONS.get(etype, '请描述现场情况')}",
            height=80,
        )
    with col2:
        people_count = st.number_input("涉及人数", min_value=1, max_value=50, value=1)

    guide_btn = st.button("🆘 获取应急指导", type="primary", use_container_width=True)

    if guide_btn:
        with st.spinner("🔄 正在生成应急指导..."):
            result = generate_emergency_guide(
                emergency_type=etype,
                description=description,
                people_count=people_count,
            )

            if result.get("success"):
                st.session_state.guide_result = result
            else:
                st.error(result.get("error", "生成失败，请重试"))

# ── 显示指导结果 ─────────────────────────────
if "guide_result" in st.session_state:
    result = st.session_state.guide_result

    st.markdown("---")

    # 第一步：最关键
    first_thing = result.get("first_thing", "")
    if first_thing:
        st.info(f"### ⚡ 第一件事\n\n{first_thing}")

    # 分步骤
    steps = result.get("steps", [])
    if steps:
        st.markdown("### 📋 操作步骤")
        for step in steps:
            with st.container():
                step_num = step.get("step", "")
                action = step.get("action", "")
                detail = step.get("detail", "")
                why = step.get("why", "")
                warning = step.get("warning", "")

                st.markdown(f"**{step_num}. {action}**")
                st.markdown(f"> {detail}")
                if why:
                    st.caption(f"💡 {why}")
                if warning:
                    st.warning(warning)

                st.markdown("")

    # 绝对禁止
    donts = result.get("donts", [])
    if donts:
        st.markdown("---")
        st.markdown("### 🚫 绝对禁止")
        for d in donts:
            st.error(f"❌ {d}")

    # 何时打120
    when_call = result.get("when_to_call_120", "")
    if when_call:
        st.markdown("---")
        st.warning(f"### 🚑 何时打120\n\n{when_call}")

    # 后续处理
    after = result.get("after_emergency", "")
    if after:
        st.markdown("---")
        st.markdown(f"### 📌 紧急情况控制后\n\n{after}")

    # 免责声明
    disclaimer = result.get("disclaimer", "")
    if disclaimer:
        st.warning(disclaimer)

    # 非结构化处理
    if result.get("parse_error"):
        st.info("⚠️ AI返回了非结构化内容，以下是原文：")
        st.markdown(result.get("raw_content", ""))

# ── 底部操作 ─────────────────────────────────
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("🗑️ 清除指导", use_container_width=True):
        st.session_state.pop("guide_result", None)
        st.session_state.pop("selected_emergency", None)
        st.rerun()
with col2:
    if st.button("🔄 换一种情况", use_container_width=True):
        st.session_state.pop("guide_result", None)
        st.session_state.pop("selected_emergency", None)
        st.rerun()
with col3:
    page_footer(show_home=False)
