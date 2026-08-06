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

# ── 风格选择 ─────────────────────────────────
if "theme" not in st.session_state:
    st.session_state.theme = "warm"

# ── 主题定义 ─────────────────────────────────
THEMES = {
    "light": {
        "name": "浅色简洁",
        "bg": "#F8FAFC",
        "card_bg": "#FFFFFF",
        "card_border": "#E2E8F0",
        "text_heading": "#0F172A",
        "text_body": "#334155",
        "text_muted": "#64748B",
        "accent": "#F97316",
        "accent_light": "#FFF7ED",
        "hero_bg": "#FFFFFF",
    },
    "warm": {
        "name": "暖橙亲和",
        "bg": "#FFFBEB",
        "card_bg": "#FFFFFF",
        "card_border": "#FDE68A",
        "text_heading": "#451A03",
        "text_body": "#78350F",
        "text_muted": "#A16207",
        "accent": "#EA580C",
        "accent_light": "#FFF7ED",
        "hero_bg": "#FFFBEB",
    },
    "dark": {
        "name": "深色科技",
        "bg": "#0F172A",
        "card_bg": "#1E293B",
        "card_border": "#334155",
        "text_heading": "#F1F5F9",
        "text_body": "#CBD5E1",
        "text_muted": "#94A3B8",
        "accent": "#F97316",
        "accent_light": "#1E293B",
        "hero_bg": "#0F172A",
    },
}

t = THEMES[st.session_state.theme]

# ── CSS（使用内插变量）───────────────────────
st.markdown(f"""
<style>
    .stApp {{
        background: {t['bg']};
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
    }}
    #MainMenu, footer, header[data-testid="stHeader"] {{
        display: none;
    }}

    /* ── Hero ── */
    .hero {{
        text-align: center;
        padding: 3rem 1.5rem 2.5rem 1.5rem;
        margin-bottom: 2rem;
    }}
    .hero-badge {{
        display: inline-block;
        background: {t['accent_light']};
        color: {t['accent']};
        font-weight: 700;
        font-size: 0.75rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        padding: 0.35rem 1rem;
        border-radius: 999px;
        margin-bottom: 1rem;
    }}
    .hero h1 {{
        font-weight: 800;
        font-size: 2.5rem;
        color: {t['text_heading']};
        margin: 0 0 0.6rem 0;
        letter-spacing: -0.03em;
        line-height: 1.2;
    }}
    .hero h1 span {{
        color: {t['accent']};
    }}
    .hero .subtitle {{
        font-size: 1.05rem;
        color: {t['text_muted']};
        line-height: 1.7;
        max-width: 560px;
        margin: 0 auto;
    }}

    /* ── 安全提醒 ── */
    .alert-bar {{
        background: {t['accent_light']};
        border: 1px solid {t['accent']}22;
        border-radius: 16px;
        padding: 0.9rem 1.3rem;
        margin: 0 auto 2.5rem auto;
        max-width: 740px;
        font-size: 0.9rem;
        color: {t['accent']};
        font-weight: 600;
    }}

    /* ── 节标题 ── */
    .section-label {{
        font-weight: 700;
        font-size: 0.75rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: {t['text_muted']};
        margin-bottom: 1rem;
        text-align: center;
    }}

    /* ── 卡片网格 ── */
    .card-grid {{
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1.2rem;
        max-width: 800px;
        margin: 0 auto 2.5rem auto;
    }}
    @media (max-width: 640px) {{
        .card-grid {{ grid-template-columns: 1fr; }}
        .hero {{ padding: 2rem 1rem 1.5rem 1rem; }}
        .hero h1 {{ font-size: 1.8rem; }}
    }}

    /* ── 卡片 ── */
    a.card-link {{
        text-decoration: none;
        display: block;
    }}
    .feature-card {{
        background: {t['card_bg']};
        border: 1px solid {t['card_border']};
        border-radius: 20px;
        padding: 1.6rem 1.5rem;
        cursor: pointer;
        transition: all 0.25s ease;
        position: relative;
        height: 100%;
    }}
    .feature-card:hover {{
        border-color: {t['accent']};
        box-shadow: 0 8px 30px {t['accent']}15, 0 2px 6px rgba(0,0,0,0.05);
        transform: translateY(-3px);
    }}
    .card-icon-box {{
        width: 52px;
        height: 52px;
        border-radius: 16px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.6rem;
        margin-bottom: 1rem;
        background: {t['accent_light']};
    }}
    .card-title {{
        font-weight: 700;
        font-size: 1.1rem;
        color: {t['text_heading']};
        margin-bottom: 0.35rem;
    }}
    .card-desc {{
        font-size: 0.9rem;
        color: {t['text_body']};
        line-height: 1.6;
    }}
    .card-chevron {{
        position: absolute;
        top: 1.5rem;
        right: 1.3rem;
        width: 28px;
        height: 28px;
        border-radius: 50%;
        background: {t['card_border']};
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.75rem;
        color: {t['text_muted']};
        transition: all 0.25s;
    }}
    .feature-card:hover .card-chevron {{
        background: {t['accent']};
        color: #FFFFFF;
    }}

    /* ── 底部 ── */
    .page-footer {{
        text-align: center;
        color: {t['text_muted']};
        font-size: 0.8rem;
        padding: 1.5rem 0 0.5rem;
        opacity: 0.5;
    }}

    /* ── 侧边栏 ── */
    section[data-testid="stSidebar"] {{
        background: {t['card_bg']};
        border-right: 1px solid {t['card_border']};
    }}
</style>
""", unsafe_allow_html=True)

# ── Hero ────────────────────────────────────
st.markdown(f"""
<div class="hero">
    <div class="hero-badge">AI SAFETY GUARDIAN</div>
    <h1>工友安全<span>守护</span></h1>
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
            <div class="card-icon-box">💬</div>
            <div class="card-title">安全知识问答</div>
            <div class="card-desc">输入问题，立即得到基于规范的回答，支持追问</div>
        </div>
    </a>
    <a href="/02_工地隐患识别" target="_self" class="card-link">
        <div class="feature-card">
            <div class="card-chevron">→</div>
            <div class="card-icon-box">📷</div>
            <div class="card-title">工地隐患识别</div>
            <div class="card-desc">拍张照片，AI自动识别安全隐患并给出整改建议</div>
        </div>
    </a>
    <a href="/03_安全培训助手" target="_self" class="card-link">
        <div class="feature-card">
            <div class="card-chevron">→</div>
            <div class="card-icon-box">📚</div>
            <div class="card-title">安全培训助手</div>
            <div class="card-desc">选工种定主题，自动生成培训内容 + 随堂测验</div>
        </div>
    </a>
    <a href="/04_应急处理指导" target="_self" class="card-link">
        <div class="feature-card">
            <div class="card-chevron">→</div>
            <div class="card-icon-box">🆘</div>
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

    # 风格切换
    st.markdown("**🎨 切换风格**")
    theme_choice = st.selectbox(
        "选择配色方案",
        options=list(THEMES.keys()),
        format_func=lambda k: THEMES[k]["name"],
        index=list(THEMES.keys()).index(st.session_state.theme),
        label_visibility="collapsed",
    )
    if theme_choice != st.session_state.theme:
        st.session_state.theme = theme_choice
        st.rerun()

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
