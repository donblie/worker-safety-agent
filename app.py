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

# ── 全局样式：浅色简洁 + 现代感 ──────────────
st.markdown("""
<style>
    /* ── 基础 ── */
    .stApp {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
        background: #f5f6fa;
    }

    /* 隐藏Streamlit默认元素 */
    #MainMenu, footer, header[data-testid="stHeader"] {
        display: none;
    }

    /* ── 顶部Hero区域 ── */
    .hero {
        background: linear-gradient(160deg, #ffffff 0%, #f0f4ff 100%);
        border: 1px solid rgba(27, 94, 155, 0.08);
        border-radius: 24px;
        padding: 2.5rem 2rem 2rem 2rem;
        text-align: center;
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
    }
    .hero::before {
        content: '';
        position: absolute;
        top: -60px;
        right: -60px;
        width: 200px;
        height: 200px;
        background: radial-gradient(circle, rgba(255,184,0,0.12) 0%, transparent 70%);
        border-radius: 50%;
    }
    .hero::after {
        content: '';
        position: absolute;
        bottom: -40px;
        left: -40px;
        width: 160px;
        height: 160px;
        background: radial-gradient(circle, rgba(27,94,155,0.06) 0%, transparent 70%);
        border-radius: 50%;
    }
    .hero-logo {
        font-size: 3.2rem;
        margin-bottom: 0.5rem;
        position: relative;
        z-index: 1;
    }
    .hero h1 {
        font-size: 2rem;
        font-weight: 700;
        color: #1a1a2e;
        margin: 0 0 0.4rem 0;
        letter-spacing: -0.02em;
        position: relative;
        z-index: 1;
    }
    .hero .subtitle {
        font-size: 0.95rem;
        color: #5a6170;
        line-height: 1.6;
        position: relative;
        z-index: 1;
        max-width: 560px;
        margin: 0 auto;
    }
    .hero .accent-dot {
        display: inline-block;
        width: 6px;
        height: 6px;
        background: #FFB800;
        border-radius: 50%;
        margin: 0 0.5rem;
        vertical-align: middle;
        opacity: 0.6;
    }

    /* ── 安全提醒条 ── */
    .alert-bar {
        background: #fffbeb;
        border: 1px solid #fde68a;
        border-radius: 14px;
        padding: 0.8rem 1.2rem;
        margin-bottom: 2rem;
        display: flex;
        align-items: center;
        gap: 0.6rem;
        font-size: 0.88rem;
        color: #92400e;
    }
    .alert-bar .alert-icon {
        font-size: 1.2rem;
        flex-shrink: 0;
    }

    /* ── 功能卡片网格 ── */
    .section-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #1a1a2e;
        margin-bottom: 1rem;
        letter-spacing: -0.01em;
    }

    .card-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1rem;
        margin-bottom: 2rem;
    }
    @media (max-width: 640px) {
        .card-grid {
            grid-template-columns: 1fr;
        }
        .hero {
            padding: 1.8rem 1.2rem 1.5rem 1.2rem;
            border-radius: 18px;
        }
        .hero h1 {
            font-size: 1.5rem;
        }
        .hero-logo {
            font-size: 2.4rem;
        }
    }

    /* ── 单张卡片 ── */
    .card-link {
        text-decoration: none;
        display: block;
    }
    .feature-card {
        background: #ffffff;
        border: 1px solid #eef0f5;
        border-radius: 18px;
        padding: 1.6rem 1.4rem;
        cursor: pointer;
        transition: all 0.25s cubic-bezier(0.25, 0.1, 0.25, 1);
        position: relative;
        overflow: hidden;
    }
    .feature-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 32px rgba(27, 94, 155, 0.10), 0 2px 8px rgba(0,0,0,0.04);
        border-color: rgba(27, 94, 155, 0.15);
    }
    .feature-card:active {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(27, 94, 155, 0.08);
    }
    .card-icon-wrap {
        width: 48px;
        height: 48px;
        border-radius: 14px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        margin-bottom: 1rem;
    }
    .card-icon-wrap.blue   { background: #eff6ff; }
    .card-icon-wrap.amber  { background: #fffbeb; }
    .card-icon-wrap.green  { background: #ecfdf5; }
    .card-icon-wrap.red    { background: #fef2f2; }
    .card-title {
        font-size: 1.05rem;
        font-weight: 650;
        color: #1a1a2e;
        margin-bottom: 0.35rem;
        letter-spacing: -0.01em;
    }
    .card-desc {
        font-size: 0.85rem;
        color: #6b7280;
        line-height: 1.5;
    }
    .card-arrow {
        position: absolute;
        top: 1.2rem;
        right: 1.2rem;
        color: #c5cad3;
        font-size: 1rem;
        transition: all 0.25s;
    }
    .feature-card:hover .card-arrow {
        color: #1B5E9B;
        right: 0.9rem;
    }

    /* ── 底部 ── */
    .footer-bar {
        text-align: center;
        color: #adb1ba;
        font-size: 0.8rem;
        padding: 1.5rem 0 0.5rem 0;
    }

    /* ── 侧边栏细化 ── */
    section[data-testid="stSidebar"] {
        background: #fafbfc;
    }
</style>
""", unsafe_allow_html=True)

# ── Hero 区域 ───────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-logo">🛡️</div>
    <h1>工友安全守护 Agent</h1>
    <p class="subtitle">
        安全知识随时问<span class="accent-dot"></span>隐患拍照能识别<span class="accent-dot"></span>培训内容自动生成<span class="accent-dot"></span>紧急情况有指导
    </p>
</div>
""", unsafe_allow_html=True)

# ── 安全提醒 ─────────────────────────────────
st.markdown("""
<div class="alert-bar">
    <span class="alert-icon">⚠️</span>
    <span><strong>安全提醒：</strong>本AI助手提供安全参考信息，不可替代现场安全员的专业判断。紧急情况请立即拨打120。</span>
</div>
""", unsafe_allow_html=True)

# ── 功能卡片（可点击跳转）────────────────────
st.markdown('<p class="section-title">📱 选择功能模块</p>', unsafe_allow_html=True)

# 用两列布局 + 可点击卡片
card_data = [
    {
        "icon": "💬", "icon_class": "blue",
        "title": "安全知识问答",
        "desc": "有什么不懂的安全问题？输入问题，立即得到基于规范的准确回答，支持追问。",
        "url": "/01_安全知识问答",
    },
    {
        "icon": "📷", "icon_class": "amber",
        "title": "工地隐患识别",
        "desc": "拍张现场照片 → AI识别安全隐患 → 给出整改建议。快速拍照或上传照片，像发朋友圈一样简单。",
        "url": "/02_工地隐患识别",
    },
    {
        "icon": "📚", "icon_class": "green",
        "title": "安全培训助手",
        "desc": "选工种、定主题、选难度，自动生成培训内容 + 随堂测验。让安全培训不再流于形式。",
        "url": "/03_安全培训助手",
    },
    {
        "icon": "🆘", "icon_class": "red",
        "title": "应急处理指导",
        "desc": "遇到紧急情况不要慌！选择类型 → 分步骤指导 → 该做什么不该做什么一目了然。",
        "url": "/04_应急处理指导",
    },
]

# 渲染两行卡片
for row_start in [0, 2]:
    cols = st.columns(2)
    for i, col in enumerate(cols):
        idx = row_start + i
        if idx < len(card_data):
            c = card_data[idx]
            with col:
                st.markdown(f"""
                <a href="{c['url']}" target="_self" class="card-link">
                    <div class="feature-card">
                        <div class="card-arrow">→</div>
                        <div class="card-icon-wrap {c['icon_class']}">{c['icon']}</div>
                        <div class="card-title">{c['title']}</div>
                        <div class="card-desc">{c['desc']}</div>
                    </div>
                </a>
                """, unsafe_allow_html=True)

# ── 底部 ─────────────────────────────────────
st.markdown('<div class="footer-bar">🛡️ 安全第一 · 生命至上</div>', unsafe_allow_html=True)

# ── 侧边栏 ───────────────────────────────
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
