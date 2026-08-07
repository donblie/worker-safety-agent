"""
模块二：工地隐患识别
- 快速拍照：摄像头拍照 → 自动分析（拍完即出报告）
- 上传照片：相册选择 → 补充描述 → 点击分析
"""
import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.vision_analyzer import encode_image, analyze_image
from utils.safety_guard import validate_image
from utils.ui_components import inject_shared_styles, page_header, page_footer

st.set_page_config(page_title="工地隐患识别 - 工友安全守护", page_icon="📷", layout="wide")

inject_shared_styles()

page_header("📷 工地隐患识别", "拍张现场照片，AI自动识别安全隐患，给出整改建议")

# ── 选择分析模式 ─────────────────────────────
analysis_mode = st.radio(
    "选择分析方式",
    ["📸 快速拍照（拍完即分析）", "📤 上传照片（可补充描述）"],
    horizontal=True,
    help=(
        "快速拍照：打开摄像头对准隐患位置拍照，拍完自动分析，无需额外操作。适合快速巡检。\n\n"
        "上传照片：从相册选择已有照片，可以添加文字描述帮助AI更准确判断。适合事后分析。"
    ),
)

st.markdown("---")

# ═══════════════════════════════════════════════
# 模式一：快速拍照 → 拍完即自动分析
# ═══════════════════════════════════════════════
if analysis_mode == "📸 快速拍照（拍完即分析）":
    st.markdown("#### 📸 对准隐患位置，点击下方拍照")
    st.caption("拍照后AI自动分析，无需额外操作。适合现场快速巡检。")

    # ── 开关：点击后才打开摄像头 ──────────
    camera_on = st.checkbox(
        "📸 点击开启摄像头",
        value=False,
        help="勾选后打开摄像头，不拍照时请取消勾选以关闭摄像头",
    )

    if not camera_on:
        st.info("👆 勾选上方开关即可打开摄像头，对准工地隐患位置拍照")
        st.session_state._camera_analyzed = False
    else:
        camera_img = st.camera_input(
            "拍照",
            label_visibility="collapsed",
            help="对准工地隐患位置拍照，系统将自动分析生成报告",
        )

        # ── 自动分析逻辑 ──────────────────
        if camera_img and not st.session_state.get("_camera_analyzed"):
            error = validate_image(camera_img.size, camera_img.type)
            if error:
                st.error(error)
            else:
                with st.status("📸 正在分析照片...", expanded=True) as status:
                    status.write("🖼️ 编码图片...")
                    img_b64, img_type = encode_image(camera_img)

                    if img_b64 is None:
                        st.error(img_type)
                        status.update(label="❌ 分析失败", state="error")
                    else:
                        status.write("✅ 图片编码完成")
                        status.write("👁️ Qwen-VL 正在逐项检查...")
                        status.write("  · 人员防护（安全帽/安全带/反光背心）")
                        status.write("  · 高处作业（临边/洞口/防护栏杆）")
                        status.write("  · 临时用电（电线/配电箱/接地）")
                        status.write("  · 机械设备安全装置")
                        status.write("  · 物料堆放与消防通道")
                        status.write("  · 基坑/边坡状态")
                        status.write("  · 消防安全设施")
                        result = analyze_image(
                            image_base64=img_b64,
                            image_type=img_type,
                            user_description="",
                        )

                        if result.get("success"):
                            status.update(label="✅ 分析完成！", state="complete")
                            st.session_state.hazard_result = result
                            st.session_state._camera_analyzed = True
                            st.rerun()
                        else:
                            st.error(result.get("error", "分析失败，请重试"))
                            status.update(label="❌ 分析失败", state="error")

        # 用户点了"清除拍照"后，重置标记
        if camera_img is None:
            st.session_state._camera_analyzed = False

# ═══════════════════════════════════════════════
# 模式二：上传照片 + 补充描述（原有流程）
# ═══════════════════════════════════════════════
else:
    uploaded_file = st.file_uploader(
        "📤 上传工地现场照片",
        type=["jpg", "jpeg", "png", "webp"],
        help="拍摄清晰、光线充足的施工现场照片。支持JPG/PNG/WEBP格式，大小不超过10MB。",
    )

    if uploaded_file:
        error = validate_image(uploaded_file.size, uploaded_file.type)
        if error:
            st.error(error)
        else:
            col_img, col_input = st.columns([1, 1])

            with col_img:
                st.image(uploaded_file, caption="上传的现场照片", use_container_width=True)

            with col_input:
                st.markdown("#### 💬 补充说明（可选）")
                st.caption("添加文字描述能帮助AI更准确地分析，但不是必须的。AI会先看图分析，再参考你的描述。")
                user_desc = st.text_area(
                    "描述您注意到的异常（选填）",
                    placeholder=(
                        "例：这是三楼的脚手架转角处，昨天刚搭好..."
                    ),
                    height=100,
                )

                st.markdown("")

                analyze_btn = st.button(
                    "🔍 开始隐患分析",
                    type="primary",
                    use_container_width=True,
                )

                if analyze_btn:
                    with st.status("📸 正在分析照片...", expanded=True) as status:
                        status.write("🖼️ 编码图片...")
                        img_b64, img_type = encode_image(uploaded_file)

                        if img_b64 is None:
                            st.error(img_type)
                            status.update(label="❌ 分析失败", state="error")
                        else:
                            status.write("✅ 图片编码完成")
                            status.write("👁️ Qwen-VL 正在逐项检查...")
                            status.write("  · 人员防护（安全帽/安全带/反光背心）")
                            status.write("  · 高处作业（临边/洞口/防护栏杆）")
                            status.write("  · 临时用电（电线/配电箱/接地）")
                            status.write("  · 机械设备安全装置")
                            status.write("  · 物料堆放与消防通道")
                            status.write("  · 基坑/边坡状态")
                            status.write("  · 消防安全设施")
                            result = analyze_image(
                                image_base64=img_b64,
                                image_type=img_type,
                                user_description=user_desc or "",
                            )

                            if result.get("success"):
                                status.update(label="✅ 分析完成！", state="complete")
                                st.session_state.hazard_result = result
                                st.rerun()
                            else:
                                st.error(result.get("error", "分析失败，请重试"))
                                status.update(label="❌ 分析失败", state="error")

# ── 显示分析结果（两种模式共用）──────────────
if "hazard_result" in st.session_state:
    result = st.session_state.hazard_result

    st.markdown("---")
    st.markdown("## 📋 隐患分析报告")

    # 概述
    summary = result.get("summary", "")
    if summary:
        st.info(f"**分析结论：** {summary}")

    # 隐患列表
    hazards = result.get("hazards", [])
    if hazards:
        high_count = sum(1 for h in hazards if h.get("severity") == "高")
        mid_count = sum(1 for h in hazards if h.get("severity") == "中")
        low_count = sum(1 for h in hazards if h.get("severity") == "低")

        st.markdown(
            f"### ⚠️ 发现 {len(hazards)} 处隐患  "
            f"（🔴高风险 {high_count}  |  🟡中风险 {mid_count}  |  🟢低风险 {low_count}）"
        )

        for i, h in enumerate(hazards, 1):
            severity = h.get("severity", "未知")
            sev_emoji = {"高": "🔴", "中": "🟡", "低": "🟢"}.get(severity, "⚪")

            with st.expander(
                f"{sev_emoji} **[{severity}风险]** {h.get('type', '未知隐患')}",
                expanded=(severity == "高"),
            ):
                st.markdown(f"**隐患描述：** {h.get('description', '暂无详细描述')}")

                fix = h.get("fix", "")
                if fix:
                    st.markdown(f"**整改建议：** {fix}")

                deadline = h.get("deadline", "")
                if deadline:
                    st.markdown(f"**整改时限：** {deadline}")

                reg = h.get("regulation_ref", "")
                if reg:
                    st.caption(f"📖 {reg}")
    else:
        st.success("✅ 未识别出明显隐患。但AI分析不能替代专业巡检，请保持常规安全检查。")

    # 好的方面
    positives = result.get("positive_findings", [])
    if positives:
        st.markdown("#### ✅ 符合规范的地方")
        for p in positives:
            st.markdown(f"- {p}")

    # 规范检索补充
    reg_context = result.get("regulation_context", "")
    if reg_context:
        with st.expander("📚 相关安全规范条文"):
            st.markdown(reg_context)

    # 紧急行动
    if result.get("requires_immediate_action"):
        st.error("🚨 **需要立即采取行动！请马上报告现场安全员！**")

    # 免责声明
    disclaimer = result.get("disclaimer", "")
    if disclaimer:
        st.warning(disclaimer)

    # 原始分析（兜底输出）
    if result.get("raw_response"):
        with st.expander("📝 AI原始分析记录"):
            st.markdown(result["raw_response"])

# ── 底部 ─────────────────────────────────────
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("🗑️ 清除结果", use_container_width=True):
        st.session_state.pop("hazard_result", None)
        st.session_state.pop("_camera_analyzed", None)
        st.rerun()
with col2:
    st.caption("💡 提示：拍清晰照片，分析更准确")
with col3:
    page_footer(show_home=False)
