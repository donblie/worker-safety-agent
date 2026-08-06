"""
共享UI样式 — 与首页设计系统一致
"""
import streamlit as st

SAFETY_ORANGE = "#F97316"
SLATE_700     = "#334155"
SLATE_500     = "#64748B"
SLATE_100     = "#F1F5F9"
BG_COLOR      = "#F8FAFC"


def inject_shared_styles():
    """在所有子页面注入统一的浅色简洁CSS"""
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@400;500;600;700&family=Nunito:wght@400;500;600;700;800&display=swap');

        .stApp {
            font-family: 'Nunito', 'PingFang SC', 'Microsoft YaHei', sans-serif;
            background: #F8FAFC;
        }
        #MainMenu, footer, header[data-testid="stHeader"] {
            display: none;
        }

        /* ── 页面顶栏 ── */
        .page-header {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 20px;
            padding: 1.5rem 1.8rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        }
        .page-header h2 {
            font-family: 'Fredoka', 'PingFang SC', sans-serif;
            font-weight: 700;
            font-size: 1.35rem;
            color: #1E293B !important;
            margin: 0 0 0.3rem 0;
            letter-spacing: -0.02em;
        }
        .page-header .subtitle {
            color: #64748B;
            font-size: 0.9rem;
            font-weight: 500;
        }

        /* ── 安全提醒条 ── */
        .safety-notice {
            background: #FFF7ED;
            border: 1px solid #FED7AA;
            border-radius: 16px;
            padding: 0.9rem 1.3rem;
            font-size: 0.88rem;
            color: #9A3412;
            margin: 1rem 0;
            font-weight: 500;
        }

        /* ── 信息卡片 ── */
        .info-card {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 16px;
            padding: 1.3rem 1.5rem;
            margin: 0.5rem 0;
        }

        /* ── 高风险脉冲 ── */
        @keyframes pulse-warning {
            0%, 100% { box-shadow: 0 0 0 0 rgba(249, 115, 22, 0.35); }
            50%      { box-shadow: 0 0 0 10px rgba(249, 115, 22, 0); }
        }
        .high-risk-alert {
            border: 2px solid #F97316;
            border-radius: 16px;
            padding: 1.2rem;
            background: #FFF7ED;
            animation: pulse-warning 2s infinite;
        }

        @media (max-width: 640px) {
            .page-header {
                padding: 1.1rem 1.2rem;
                border-radius: 16px;
            }
            .page-header h2 { font-size: 1.15rem; }
        }
    </style>
    """, unsafe_allow_html=True)


def page_header(title: str, subtitle: str):
    st.markdown(f"""
    <div class="page-header">
        <h2>{title}</h2>
        <div class="subtitle">{subtitle}</div>
    </div>
    """, unsafe_allow_html=True)


def safety_notice():
    st.markdown("""
    <div class="safety-notice">
        ⚠️ <strong>安全提醒：</strong>本AI助手提供安全参考信息，不可替代现场安全员的专业判断。
    </div>
    """, unsafe_allow_html=True)


def page_footer(show_home: bool = True):
    cols = st.columns([1, 1, 1])
    with cols[1]:
        if show_home:
            if st.button("🏠 返回首页", use_container_width=True, key="_footer_home"):
                st.switch_page("app.py")
