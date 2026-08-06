"""
共享UI样式和页面装饰
浅色简洁风格，与首页保持一致
"""
import streamlit as st


# ── 色系 ──────────────────────────────────────
SAFETY_YELLOW = "#FFB800"
SAFETY_BLUE   = "#1B5E9B"
DANGER_RED    = "#D32F2F"
SUCCESS_GREEN = "#2E7D32"
BG_LIGHT      = "#f5f6fa"
TEXT_MUTED    = "#6b7280"


def inject_shared_styles():
    """在所有页面注入统一的浅色简洁CSS"""
    st.markdown("""
    <style>
        /* ── 基础 ── */
        .stApp {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
            background: #f5f6fa;
        }
        #MainMenu, footer, header[data-testid="stHeader"] {
            display: none;
        }

        /* ── 页面顶栏（浅色）── */
        .page-header {
            background: #ffffff;
            border: 1px solid #eef0f5;
            border-radius: 20px;
            padding: 1.4rem 1.8rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.03);
        }
        .page-header h2 {
            color: #1a1a2e !important;
            margin: 0 0 0.25rem 0;
            font-size: 1.35rem;
            font-weight: 700;
            letter-spacing: -0.02em;
        }
        .page-header .subtitle {
            color: #6b7280;
            font-size: 0.88rem;
        }

        /* ── 安全提醒条 ── */
        .safety-notice {
            background: #fffbeb;
            border: 1px solid #fde68a;
            border-radius: 14px;
            padding: 0.8rem 1.2rem;
            font-size: 0.85rem;
            color: #92400e;
            margin: 1rem 0;
        }

        /* ── 信息卡片 ── */
        .info-card {
            background: #ffffff;
            border: 1px solid #eef0f5;
            border-radius: 14px;
            padding: 1.2rem 1.4rem;
            margin: 0.5rem 0;
            box-shadow: 0 1px 2px rgba(0,0,0,0.02);
        }

        /* ── 高风险脉冲 ── */
        @keyframes pulse-warning {
            0%, 100% { box-shadow: 0 0 0 0 rgba(211, 47, 47, 0.3); }
            50%      { box-shadow: 0 0 0 8px rgba(211, 47, 47, 0); }
        }
        .high-risk-alert {
            border: 2px solid #D32F2F;
            border-radius: 16px;
            padding: 1.2rem;
            background: #fef2f2;
            animation: pulse-warning 2s infinite;
        }

        /* ── 移动端 ── */
        @media (max-width: 768px) {
            .page-header {
                padding: 1rem 1.2rem;
                border-radius: 16px;
            }
            .page-header h2 {
                font-size: 1.15rem;
            }
            section[data-testid="stSidebar"] {
                display: none;
            }
        }
    </style>
    """, unsafe_allow_html=True)


def page_header(title: str, subtitle: str):
    """统一页面标题"""
    st.markdown(f"""
    <div class="page-header">
        <h2>{title}</h2>
        <div class="subtitle">{subtitle}</div>
    </div>
    """, unsafe_allow_html=True)


def safety_notice():
    """统一安全提醒条"""
    st.markdown("""
    <div class="safety-notice">
        ⚠️ <strong>安全提醒：</strong>本AI助手提供安全参考信息，不可替代现场安全员的专业判断。
    </div>
    """, unsafe_allow_html=True)


def page_footer(show_home: bool = True):
    """统一页脚"""
    cols = st.columns([1, 1, 1])
    with cols[1]:
        if show_home:
            if st.button("🏠 返回首页", use_container_width=True, key="_footer_home"):
                st.switch_page("app.py")
