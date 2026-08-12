"""
对话助手 —— 单Agent + Function Calling 统一入口
工友在一个对话框中自然描述需求，Agent自动判断并调度工具
"""
import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json

from core.agent import agent_chat_stream
from core.vision_analyzer import encode_image
from utils.safety_guard import validate_input, FALLBACK_MESSAGES, SubmitGuard
from utils.ui_components import inject_shared_styles, page_header, page_footer
from utils.logger import log

# ── 页面配置 ─────────────────────────────────
st.set_page_config(
    page_title="对话助手 - 工友安全守护",
    page_icon="🤖",
    layout="wide",
)

inject_shared_styles()

# ── 初始化 ───────────────────────────────────
if "agent_history" not in st.session_state:
    st.session_state.agent_history = []
if "agent_submit_guard" not in st.session_state:
    st.session_state.agent_submit_guard = SubmitGuard(cooldown_seconds=1.5)
if "agent_has_image" not in st.session_state:
    st.session_state.agent_has_image = False

page_header("🤖 对话助手", "智能识别需求，自动调度工具——问知识、识隐患、生成培训、应急指导一站式搞定")

# ── 侧边栏：图片上传 ──────────────────────────
with st.sidebar:
    st.markdown("### 📷 上传工地照片")
    st.caption("上传照片后描述您的需求，Agent会自动调用视觉分析工具")
    uploaded_file = st.file_uploader(
        "选择图片",
        type=["jpg", "jpeg", "png", "webp"],
        label_visibility="collapsed",
        key="agent_image_uploader",
    )
    current_image_b64 = None
    current_image_type = None
    if uploaded_file:
        image_b64, error = encode_image(uploaded_file)
        if error:
            st.error(error)
        else:
            st.image(uploaded_file, caption="已上传", use_container_width=True)
            current_image_b64 = image_b64
            current_image_type = "image/jpeg"
            st.session_state.agent_has_image = True

    st.markdown("---")

    # 快捷提示
    st.markdown("### 💡 试试这些")
    quick_prompts = [
        "高处作业安全带应该挂在什么地方？",
        "帮架子工生成一份脚手架安全培训",
        "工友触电了怎么办？",
        "电焊作业有什么安全要求？",
    ]
    for qp in quick_prompts:
        if st.button(qp, key=f"agent_qp_{qp[:15]}", use_container_width=True):
            st.session_state.agent_quick_prompt = qp
            st.rerun()

    st.markdown("---")
    st.caption("💬 当前为Agent对话模式。如需使用完整功能页面，请返回首页选择对应模块。")

# ── 对话显示区域 ────────────────────────────
chat_container = st.container()

with chat_container:
    for msg in st.session_state.agent_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# ── 输入区域 ─────────────────────────────────
st.markdown("---")

user_input = st.chat_input(
    placeholder="想做什么？问知识、分析照片、生成培训、应急指导…直接告诉我就行！",
)

# 检查快捷提示
quick_prompt = st.session_state.pop("agent_quick_prompt", None)
if not user_input and quick_prompt:
    user_input = quick_prompt

# ── 处理用户输入 ────────────────────────────
if user_input:
    error_msg = validate_input(user_input)
    if error_msg:
        st.error(error_msg)
    else:
        guard = st.session_state.agent_submit_guard
        if not guard.can_submit():
            st.warning(f"⏳ 请稍等 {guard.get_remaining_cooldown():.0f} 秒")
        else:
            guard.mark_submitted()

            # 构建用户消息（如有图片则附加说明）
            display_msg = user_input
            if st.session_state.agent_has_image and current_image_b64:
                display_msg = f"📷 [已上传工地照片] {user_input}"
                # 实际传给Agent的消息包含图片分析指令
                agent_msg = (
                    f"{user_input}\n\n[系统提示：用户已上传一张工地照片（base64已就绪），"
                    f"如需进行隐患分析，请告知用户当前Agent对话模式暂不支持直接图片分析，"
                    f"建议用户前往'工地隐患识别'页面上传分析。回答时请先回应工友的文字问题。]"
                )
            else:
                agent_msg = user_input

            # 显示用户消息
            st.session_state.agent_history.append({"role": "user", "content": display_msg})
            st.session_state.agent_has_image = False

            # ── Agent 处理 ──
            tool_calls_made = []
            with st.chat_message("assistant"):
                placeholder = st.empty()

                try:
                    events = agent_chat_stream(agent_msg, st.session_state.agent_history[:-1])
                    full_response = ""

                    for event in events:
                        etype = event.get("type", "")

                        if etype == "thinking":
                            placeholder.info(f"🔍 {event['content']}")

                        elif etype == "tool_call":
                            tool_name = event["tool"]
                            tool_calls_made.append(tool_name)
                            tool_labels = {
                                "search_regulations": "📚 搜索安全规范",
                                "generate_training_material": "📝 生成培训内容",
                                "get_emergency_guide": "🆘 应急指导",
                            }
                            label = tool_labels.get(tool_name, f"🔧 {tool_name}")
                            placeholder.info(f"{label}: {json.dumps(event.get('args', {}), ensure_ascii=False)[:120]}")

                        elif etype == "tool_result":
                            placeholder.success(f"✅ {event['tool']} 完成")

                        elif etype == "delta":
                            full_response += event["content"]
                            placeholder.markdown(full_response + "▌")

                        elif etype == "done":
                            full_response = event["full_text"]
                            if tool_calls_made:
                                tools_used = " · ".join(
                                    {"search_regulations": "📚规范检索", "generate_training_material": "📝培训生成",
                                     "get_emergency_guide": "🆘应急指导"}.get(t, t)
                                    for t in tool_calls_made
                                )
                                full_response = f"*（已调用工具：{tools_used}）*\n\n{full_response}"
                            placeholder.markdown(full_response)

                        elif etype == "error":
                            placeholder.error(event["content"])
                            full_response = event["content"]

                    # 保存到历史
                    st.session_state.agent_history.append({
                        "role": "assistant",
                        "content": full_response or "抱歉，我暂时无法回答这个问题。"
                    })

                except Exception as e:
                    import traceback
                    log("ERROR", f"Agent page error: {traceback.format_exc()[:500]}")
                    placeholder.error(FALLBACK_MESSAGES["unknown_error"])
                    st.session_state.agent_history.append({
                        "role": "assistant",
                        "content": FALLBACK_MESSAGES["unknown_error"]
                    })

            st.rerun()

# ── 底部操作 ─────────────────────────────────
st.markdown("---")
col1, col2 = st.columns([1, 1])
with col1:
    if st.button("🗑️ 清除对话", use_container_width=True):
        st.session_state.agent_history = []
        st.session_state.agent_has_image = False
        st.rerun()
with col2:
    page_footer(show_home=False)
