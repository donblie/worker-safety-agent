"""
工友安全守护Agent — 主入口
建筑工地安全智能助手
"""
import streamlit as st

st.set_page_config(
    page_title="工友安全守护Agent",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── 全局样式 ─────────────────────────────────
st.markdown("""
<style>
    /* ── Google Fonts ── */
    @import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@400;500;600;700&family=Nunito:wght@400;500;600;700;800&display=swap');

    /* ── 基础 ── */
    .stApp {
        font-family: 'Nunito', 'PingFang SC', 'Microsoft YaHei', sans-serif;
        background: #F8FAFC;
    }
    #MainMenu, footer, header[data-testid="stHeader"] {
        display: none;
    }

    /* ── Hero ── */
    .hero {
        text-align: center;
        padding: 3rem 1.5rem 2.5rem 1.5rem;
        margin-bottom: 2rem;
    }
    .hero-badge {
        display: inline-block;
        background: #FFF7ED;
        color: #F97316;
        font-family: 'Fredoka', 'PingFang SC', sans-serif;
        font-weight: 600;
        font-size: 0.8rem;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        padding: 0.35rem 1rem;
        border-radius: 999px;
        margin-bottom: 1rem;
    }
    .hero h1 {
        font-family: 'Fredoka', 'PingFang SC', sans-serif;
        font-weight: 700;
        font-size: 2.5rem;
        color: #1E293B;
        margin: 0 0 0.6rem 0;
        letter-spacing: -0.03em;
        line-height: 1.2;
    }
    .hero .subtitle {
        font-size: 1.05rem;
        color: #64748B;
        line-height: 1.7;
        max-width: 580px;
        margin: 0 auto;
    }

    /* ── 安全提醒 ── */
    .alert-bar {
        background: #FFF7ED;
        border: 1px solid #FED7AA;
        border-radius: 16px;
        padding: 0.9rem 1.3rem;
        margin: 0 auto 2.5rem auto;
        max-width: 720px;
        font-size: 0.9rem;
        color: #9A3412;
        font-weight: 500;
    }

    /* ── 节标题 ── */
    .section-label {
        font-family: 'Fredoka', 'PingFang SC', sans-serif;
        font-weight: 600;
        font-size: 0.75rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: #94A3B8;
        margin-bottom: 1rem;
        text-align: center;
    }

    /* ── 卡片网格 ── */
    .card-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1.2rem;
        max-width: 800px;
        margin: 0 auto 2.5rem auto;
    }
    @media (max-width: 640px) {
        .card-grid { grid-template-columns: 1fr; }
        .hero { padding: 2rem 1rem 1.5rem 1rem; }
        .hero h1 { font-size: 1.8rem; }
        .hero .subtitle { font-size: 0.95rem; }
    }

    /* ── 卡片 ── */
    a.card-link {
        text-decoration: none;
        display: block;
    }
    .feature-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 20px;
        padding: 1.6rem 1.5rem;
        cursor: pointer;
        transition: all 0.25s ease;
        position: relative;
        height: 100%;
    }
    .feature-card:hover {
        border-color: #F97316;
        box-shadow: 0 8px 30px rgba(249, 115, 22, 0.10),
                    0 2px 6px rgba(0,0,0,0.04);
        transform: translateY(-3px);
    }
    .card-icon-box {
        width: 52px;
        height: 52px;
        border-radius: 16px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.6rem;
        margin-bottom: 1rem;
    }
    .card-icon-box.slate  { background: #F1F5F9; }
    .card-icon-box.orange { background: #FFF7ED; }
    .card-icon-box.sky    { background: #F0F9FF; }
    .card-icon-box.rose   { background: #FFF1F2; }
    .card-title {
        font-family: 'Fredoka', 'PingFang SC', sans-serif;
        font-weight: 600;
        font-size: 1.1rem;
        color: #1E293B;
        margin-bottom: 0.35rem;
    }
    .card-desc {
        font-size: 0.9rem;
        color: #64748B;
        line-height: 1.6;
    }
    .card-chevron {
        position: absolute;
        top: 1.5rem;
        right: 1.3rem;
        width: 28px;
        height: 28px;
        border-radius: 50%;
        background: #F1F5F9;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.75rem;
        color: #94A3B8;
        transition: all 0.25s;
    }
    .feature-card:hover .card-chevron {
        background: #F97316;
        color: #FFFFFF;
    }

    /* ── 底部 ── */
    .page-footer {
        text-align: center;
        color: #CBD5E1;
        font-size: 0.8rem;
        padding: 1.5rem 0 0.5rem;
    }

    /* ── 侧边栏 ── */
    section[data-testid="stSidebar"] {
        background: #FFFFFF;
        border-right: 1px solid #E2E8F0;
    }
</style>
""", unsafe_allow_html=True)

# ── Hero ────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-badge">AI SAFETY GUARDIAN</div>
    <h1>工友安全守护</h1>
    <p class="subtitle">
        安全知识随时问 &nbsp;·&nbsp; 隐患拍照能识别 &nbsp;·&nbsp; 培训内容自动生成 &nbsp;·&nbsp; 紧急情况有指导
    </p>
</div>
""", unsafe_allow_html=True)

# ── 安全提醒 ────────────────────────────────
st.markdown("""
<div class="alert-bar">
    ⚠️ &nbsp;本AI助手提供安全参考信息，不可替代现场安全员的专业判断。紧急情况请立即拨打 <strong>120</strong>。
</div>
""", unsafe_allow_html=True)

# ── 功能卡片 ────────────────────────────────
st.markdown('<p class="section-label">功能模块</p>', unsafe_allow_html=True)

st.markdown("""
<div class="card-grid">
    <a href="/01_安全知识问答" target="_self" class="card-link">
        <div class="feature-card">
            <div class="card-chevron">→</div>
            <div class="card-icon-box slate">💬</div>
            <div class="card-title">安全知识问答</div>
            <div class="card-desc">输入问题，立即得到基于规范的回答，支持追问</div>
        </div>
    </a>
    <a href="/02_工地隐患识别" target="_self" class="card-link">
        <div class="feature-card">
            <div class="card-chevron">→</div>
            <div class="card-icon-box orange">📷</div>
            <div class="card-title">工地隐患识别</div>
            <div class="card-desc">拍张照片，AI自动识别安全隐患并给出整改建议</div>
        </div>
    </a>
    <a href="/03_安全培训助手" target="_self" class="card-link">
        <div class="feature-card">
            <div class="card-chevron">→</div>
            <div class="card-icon-box sky">📚</div>
            <div class="card-title">安全培训助手</div>
            <div class="card-desc">选工种定主题，自动生成培训内容 + 随堂测验</div>
        </div>
    </a>
    <a href="/04_应急处理指导" target="_self" class="card-link">
        <div class="feature-card">
            <div class="card-chevron">→</div>
            <div class="card-icon-box rose">🆘</div>
            <div class="card-title">应急处理指导</div>
            <div class="card-desc">遇到紧急情况不要慌，跟着步骤一步步来</div>
        </div>
    </a>
</div>
""", unsafe_allow_html=True)

# ── 底部 ────────────────────────────────────
st.markdown('<div class="page-footer">🛡️ 安全第一 · 生命至上</div>', unsafe_allow_html=True)

# ── 侧边栏 ──────────────────────────────────
with st.sidebar:
    st.markdown("### 🛡️ 安全小海")
    st.markdown("*安全第一，生命至上*")
    st.markdown("---")

    st.markdown("**📱 功能模块**")
    st.page_link("pages/01_安全知识问答.py", label="💬 安全知识问答")
    st.page_link("pages/02_工地隐患识别.py", label="📷 工地隐患识别")
    st.page_link("pages/03_安全培训助手.py", label="📚 安全培训助手")
    st.page_link("pages/04_应急处理指导.py", label="🆘 应急处理指导")

    st.markdown("---")

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
