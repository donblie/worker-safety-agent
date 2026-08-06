"""
工友安全守护Agent — 主入口
建筑工地安全智能助手
"""
import streamlit as st

# ── 页面配置 ─────────────────────────────────
st.set_page_config(
    page_title="工友安全守护Agent",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── 移动端适配CSS ────────────────────────────
st.markdown("""
<style>
    .stApp {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
    }

    /* 标题样式 */
    .main-header {
        text-align: center;
        padding: 2rem 1rem 1rem 1rem;
        background: linear-gradient(135deg, #1B5E9B 0%, #1565C0 100%);
        border-radius: 0 0 20px 20px;
        color: white;
        margin-bottom: 2rem;
    }
    .main-header h1 {
        color: white;
        font-size: 2rem;
        margin-bottom: 0.3rem;
    }
    .main-header p {
        color: rgba(255,255,255,0.85);
        font-size: 1rem;
    }

    /* 功能卡片 */
    .feature-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.5rem 1rem;
        text-align: center;
        height: 100%;
        transition: all 0.2s;
    }
    .feature-card:hover {
        border-color: #FFB800;
        box-shadow: 0 4px 12px rgba(255, 184, 0, 0.15);
        transform: translateY(-2px);
    }
    .feature-card .icon {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }
    .feature-card .title {
        font-weight: 600;
        font-size: 1.1rem;
        color: #1B5E9B;
        margin-bottom: 0.3rem;
    }
    .feature-card .desc {
        font-size: 0.85rem;
        color: #64748b;
    }

    /* 警告条 */
    .safety-notice {
        background: #FFF8E1;
        border-left: 4px solid #FFB800;
        padding: 0.8rem 1rem;
        border-radius: 8px;
        font-size: 0.85rem;
        color: #5D4037;
        margin: 1rem 0;
    }

    /* 移动端适配 */
    @media (max-width: 768px) {
        .main-header h1 { font-size: 1.5rem; }
        .main-header p { font-size: 0.9rem; }
        .feature-card { padding: 1rem 0.8rem; }
        .feature-card .icon { font-size: 2rem; }
    }
</style>
""", unsafe_allow_html=True)

# ── 页面标题 ─────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>🛡️ 工友安全守护Agent</h1>
    <p>建筑工地安全智能助手 —— 安全知识随时问 · 隐患拍照能识别 · 培训内容自动生成 · 紧急情况有指导</p>
</div>
""", unsafe_allow_html=True)

# ── 安全提醒 ─────────────────────────────────
st.markdown("""
<div class="safety-notice">
    ⚠️ <strong>安全提醒：</strong>本AI助手提供安全参考信息，不可替代现场安全员的专业判断。
    高风险作业请务必按照规范流程操作，紧急情况请立即拨打120并报告现场管理人员。
</div>
""", unsafe_allow_html=True)

# ── 功能介绍 ─────────────────────────────────
st.markdown("### 📱 选择功能模块")

col1, col2 = st.columns(2)
col3, col4 = st.columns(2)

with col1:
    st.markdown("""
    <div class="feature-card">
        <div class="icon">💬</div>
        <div class="title">安全知识问答</div>
        <div class="desc">有什么不懂的安全问题？输入问题，立即得到基于规范的准确回答。支持追问!</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-card">
        <div class="icon">📷</div>
        <div class="title">工地隐患识别</div>
        <div class="desc">拍张现场照片 → AI识别安全隐患 → 给出整改建议。拍照巡检像发朋友圈一样简单!</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="feature-card">
        <div class="icon">📚</div>
        <div class="title">安全培训助手</div>
        <div class="desc">选工种、选主题，自动生成培训内容+测验题。安全培训不再流于形式!</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="feature-card">
        <div class="icon">🆘</div>
        <div class="title">应急处理指导</div>
        <div class="desc">遇到紧急情况？选择类型 → 分步骤指导 → 该做什么、不该做什么一目了然!</div>
    </div>
    """, unsafe_allow_html=True)

# ── 导航提示 ─────────────────────────────────
st.markdown("---")
st.markdown("### 👆 使用方法")
st.markdown("在左侧导航栏选择对应的功能模块，或者直接点击上方对应的功能页面。")

# ── 侧边栏 ───────────────────────────────
with st.sidebar:
    st.markdown("### 🛡️ 安全小海")
    st.markdown("*安全第一，生命至上*")
    st.markdown("---")

    # 快速导航
    st.markdown("**📱 功能模块**")
    st.page_link("pages/01_安全知识问答.py", label="💬 安全知识问答")
    st.page_link("pages/02_工地隐患识别.py", label="📷 工地隐患识别")
    st.page_link("pages/03_安全培训助手.py", label="📚 安全培训助手")
    st.page_link("pages/04_应急处理指导.py", label="🆘 应急处理指导")

    st.markdown("---")

    # 知识库状态
    try:
        from core.knowledge_base import get_knowledge_base
        kb = get_knowledge_base()
        if kb.is_ready():
            stats = kb.get_stats()
            st.success(f"📚 知识库就绪 — {stats['total_chunks']}条规范")
        else:
            st.warning("⚠️ 知识库未初始化")
    except Exception:
        st.info("📚 知识库待初始化")

    st.markdown("---")
    st.caption("© 2026 海之子杯AI智能体挑战计划")
