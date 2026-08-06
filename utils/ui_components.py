"""
共享UI样式和页面装饰
每个页面调用 inject_shared_styles() 获得统一的外观
"""
import streamlit as st


# ── 安全色系 ──────────────────────────────────
SAFETY_YELLOW = "#FFB800"
SAFETY_BLUE = "#1B5E9B"
DANGER_RED = "#D32F2F"
SUCCESS_GREEN = "#2E7D32"
BG_LIGHT = "#f8fafc"
TEXT_MUTED = "#64748b"


def inject_shared_styles():
    """在所有页面注入统一的CSS样式"""
    st.markdown("""
    <style>
        /* ── 基础 ── */
        .stApp {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
        }

        /* ── 页面顶栏 ── */
        .page-header {
            background: linear-gradient(135deg, #1B5E9B 0%, #1565C0 100%);
            padding: 1.2rem 1.5rem;
            border-radius: 0 0 16px 16px;
            color: white;
            margin-bottom: 1.5rem;
        }
        .page-header h2 {
            color: white !important;
            margin: 0;
            font-size: 1.4rem;
        }
        .page-header .subtitle {
            color: rgba(255,255,255,0.8);
            font-size: 0.85rem;
            margin-top: 0.3rem;
        }

        /* ── 底部工具栏 ── */
        .page-footer {
            display: flex;
            gap: 0.5rem;
            align-items: center;
            justify-content: center;
            padding: 1rem 0;
            border-top: 1px solid #e2e8f0;
            margin-top: 2rem;
        }

        /* ── 安全提醒条 ── */
        .safety-notice {
            background: #FFF8E1;
            border-left: 4px solid #FFB800;
            padding: 0.7rem 1rem;
            border-radius: 8px;
            font-size: 0.85rem;
            color: #5D4037;
            margin: 1rem 0;
        }

        /* ── 移动端适配 ── */
        @media (max-width: 768px) {
            .page-header {
                padding: 1rem 1.2rem;
                border-radius: 0 0 12px 12px;
            }
            .page-header h2 {
                font-size: 1.2rem;
            }
            section[data-testid="stSidebar"] {
                display: none;
            }
        }

        /* ── 卡片容器 ── */
        .info-card {
            background: #f1f5f9;
            border-radius: 10px;
            padding: 1rem 1.2rem;
            margin: 0.5rem 0;
        }

        /* ── 高风险闪烁 ── */
        @keyframes pulse-warning {
            0%, 100% { border-color: #D32F2F; }
            50% { border-color: #ff6b6b; }
        }
        .high-risk-alert {
            border: 3px solid #D32F2F;
            border-radius: 12px;
            padding: 1rem;
            animation: pulse-warning 2s infinite;
        }
    </style>
    """, unsafe_allow_html=True)


def page_header(title: str, subtitle: str):
    """统一的页面标题"""
    st.markdown(f"""
    <div class="page-header">
        <h2>{title}</h2>
        <div class="subtitle">{subtitle}</div>
    </div>
    """, unsafe_allow_html=True)


def safety_notice():
    """统一的安全提醒条"""
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
