"""
共享UI样式 — 支持主题切换，与首页设计系统一致
"""
import streamlit as st


_THEME_KEYS = ("light", "warm", "dark")


def _resolve_theme():
    """解析当前主题：URL查询参数优先（跨页面/刷新持久），其次 session_state，默认 warm"""
    name = st.session_state.get("theme", "warm")
    try:
        qp = st.query_params.get("theme")
        if isinstance(qp, (list, tuple)):
            qp = qp[0] if qp else None
        if qp in _THEME_KEYS:
            name = qp
            st.session_state.theme = name  # 同步，让侧边栏下拉框等显示正确
    except Exception:
        pass
    return name


def theme_href_param():
    """生成内部链接查询参数（如 ?theme=dark），保证 <a href> 全页面导航主题不丢"""
    return f"?theme={_resolve_theme()}"


def _theme():
    """读取当前主题配色"""
    name = _resolve_theme()
    themes = {
        "light": {
            "bg": "#F8FAFC", "card_bg": "#FFFFFF", "card_border": "#E2E8F0",
            "text_heading": "#0F172A", "text_body": "#334155", "text_muted": "#64748B",
            "accent": "#F97316", "accent_light": "#FFF7ED",
        },
        "warm": {
            "bg": "#FFFBEB", "card_bg": "#FFFFFF", "card_border": "#FDE68A",
            "text_heading": "#451A03", "text_body": "#78350F", "text_muted": "#A16207",
            "accent": "#EA580C", "accent_light": "#FFF7ED",
        },
        "dark": {
            "bg": "#0F172A", "card_bg": "#1E293B", "card_border": "#334155",
            "text_heading": "#F1F5F9", "text_body": "#CBD5E1", "text_muted": "#94A3B8",
            "accent": "#F97316", "accent_light": "#1E293B",
        },
    }
    return themes.get(name, themes["light"])


def inject_shared_styles():
    t = _theme()
    st.markdown(f"""
    <style>
        .stApp {{
            background: {t['bg']};
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
        }}
        .stApp, .stMarkdown, [data-testid="stMarkdownContainer"], .stMarkdown p,
        .stMarkdown span, .stMarkdown li, .stMarkdown div, label, .stSelectbox label {{
            color: {t['text_body']} !important;
        }}
        .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4 {{
            color: {t['text_heading']} !important;
        }}
        #MainMenu, footer, header[data-testid="stHeader"] {{
            display: none;
        }}

        .page-header {{
            background: {t['card_bg']};
            border: 1px solid {t['card_border']};
            border-radius: 20px;
            padding: 1.5rem 1.8rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        }}
        .page-header h2 {{
            font-weight: 800;
            font-size: 1.35rem;
            color: {t['text_heading']} !important;
            margin: 0 0 0.3rem 0;
            letter-spacing: -0.02em;
        }}
        .page-header .subtitle {{
            color: {t['text_muted']};
            font-size: 0.9rem;
            font-weight: 500;
        }}

        .safety-notice {{
            background: {t['accent_light']};
            border: 1px solid {t['accent']}22;
            border-radius: 16px;
            padding: 0.9rem 1.3rem;
            font-size: 0.88rem;
            color: {t['accent']};
            margin: 1rem 0;
            font-weight: 600;
        }}

        .info-card {{
            background: {t['card_bg']};
            border: 1px solid {t['card_border']};
            border-radius: 16px;
            padding: 1.3rem 1.5rem;
            margin: 0.5rem 0;
        }}

        @keyframes pulse-warning {{
            0%, 100% {{ box-shadow: 0 0 0 0 {t['accent']}50; }}
            50%      {{ box-shadow: 0 0 0 10px {t['accent']}00; }}
        }}
        .high-risk-alert {{
            border: 2px solid {t['accent']};
            border-radius: 16px;
            padding: 1.2rem;
            background: {t['accent_light']};
            animation: pulse-warning 2s infinite;
        }}

        section[data-testid="stSidebar"] {{
            background: {t['card_bg']};
            border-right: 1px solid {t['card_border']};
        }}

        /* ── Streamlit 按钮 ── */
        .stButton > button, button[kind="secondary"] {{
            background: {t['card_bg']} !important;
            color: {t['text_body']} !important;
            border: 1px solid {t['card_border']} !important;
            border-radius: 10px !important;
            font-weight: 600 !important;
            transition: all 0.2s !important;
        }}
        .stButton > button:hover, button[kind="secondary"]:hover {{
            border-color: {t['accent']} !important;
            color: {t['accent']} !important;
            background: {t['accent_light']} !important;
        }}
        button[kind="primary"] {{
            background: {t['accent']} !important;
            color: #FFFFFF !important;
            border: 1px solid {t['accent']} !important;
        }}
        button[kind="primary"]:hover {{
            background: {t['accent']}DD !important;
        }}

        /* ── Streamlit 输入框/文本域/数字输入 ── */
        .stTextInput input, .stTextArea textarea, .stNumberInput input {{
            background: {t['card_bg']} !important;
            color: {t['text_body']} !important;
            border: 1px solid {t['card_border']} !important;
            border-radius: 10px !important;
        }}
        .stTextInput input:focus, .stTextArea textarea:focus, .stNumberInput input:focus {{
            border-color: {t['accent']} !important;
            box-shadow: 0 0 0 2px {t['accent']}22 !important;
        }}
        .stTextInput label, .stTextArea label, .stNumberInput label {{
            color: {t['text_heading']} !important;
        }}

        /* ── Streamlit radio / checkbox ── */
        .stRadio label, .stCheckbox label {{
            color: {t['text_body']} !important;
        }}

        /* ── Streamlit selectbox ── */
        .stSelectbox [data-baseweb="select"] {{
            background: {t['card_bg']} !important;
        }}
        .stSelectbox [data-baseweb="select"] div {{
            color: {t['text_body']} !important;
        }}

        /* ── Streamlit radio ── */
        .stRadio [data-baseweb="radio"] div:first-child {{
            border-color: {t['card_border']} !important;
            background: {t['card_bg']} !important;
        }}
        .stRadio label p {{
            color: {t['text_body']} !important;
        }}

        /* ── Streamlit checkbox ── */
        .stCheckbox [data-baseweb="checkbox"] div:first-child {{
            border-color: {t['card_border']} !important;
            background: {t['card_bg']} !important;
        }}
        .stCheckbox label p {{
            color: {t['text_body']} !important;
        }}

        /* ── Streamlit expander ── */
        [data-testid="stExpander"] details {{
            border-color: {t['card_border']} !important;
            border-radius: 12px !important;
            overflow: hidden;
        }}
        [data-testid="stExpander"] summary {{
            background: {t['card_bg']} !important;
            color: {t['text_body']} !important;
            border-radius: 12px !important;
        }}
        [data-testid="stExpander"] summary:hover {{
            color: {t['accent']} !important;
        }}
        [data-testid="stExpander"] .stMarkdown {{
            background: {t['bg']} !important;
        }}

        /* ── Streamlit metric ── */
        [data-testid="stMetricValue"] {{
            color: {t['text_heading']} !important;
        }}
        [data-testid="stMetricLabel"] {{
            color: {t['text_muted']} !important;
        }}
        [data-testid="stMetricValue"] + div {{
            color: {t['text_body']} !important;
        }}

        /* ── Streamlit file uploader ── */
        [data-testid="stFileUploader"] section {{
            background: {t['card_bg']} !important;
            border: 1px dashed {t['card_border']} !important;
            border-radius: 12px !important;
        }}
        [data-testid="stFileUploader"] section:hover {{
            border-color: {t['accent']} !important;
        }}
        [data-testid="stFileUploader"] span {{
            color: {t['text_muted']} !important;
        }}
        [data-testid="stFileUploader"] small {{
            color: {t['text_muted']} !important;
        }}

        /* ── Streamlit chat_input ── */
        [data-testid="stChatInput"] textarea {{
            background: {t['card_bg']} !important;
            color: {t['text_body']} !important;
            border: 1px solid {t['card_border']} !important;
            border-radius: 12px !important;
        }}
        [data-testid="stChatInput"] textarea:focus {{
            border-color: {t['accent']} !important;
        }}

        /* ── Streamlit spinner ── */
        .stSpinner {{
            color: {t['text_body']} !important;
        }}

        @media (max-width: 640px) {{
            .page-header {{
                padding: 1.1rem 1.2rem;
                border-radius: 16px;
            }}
            .page-header h2 {{ font-size: 1.15rem; }}
        }}
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


def mobile_bottom_nav():
    """移动端底部导航栏 — 粘性固定在页面底部，方便单手操作"""
    t = _theme()
    tp = theme_href_param()
    st.markdown(f"""
    <style>
        .mobile-nav-spacer {{
            height: 72px;
        }}
        .mobile-bottom-nav {{
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            z-index: 999;
            background: {t['card_bg']};
            border-top: 1px solid {t['card_border']};
            display: flex;
            justify-content: space-around;
            align-items: center;
            padding: 6px 4px max(6px, env(safe-area-inset-bottom)) 4px;
            box-shadow: 0 -2px 12px rgba(0,0,0,0.06);
        }}
        .mobile-bottom-nav a {{
            text-decoration: none;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 2px;
            padding: 4px 6px;
            border-radius: 10px;
            min-width: 52px;
            transition: all 0.15s;
        }}
        .mobile-bottom-nav a:hover {{
            background: {t['accent_light']};
        }}
        .mobile-bottom-nav .nav-icon {{
            font-size: 1.25rem;
            line-height: 1;
        }}
        .mobile-bottom-nav .nav-label {{
            font-size: 0.65rem;
            color: {t['text_muted']};
            font-weight: 500;
            white-space: nowrap;
        }}
        .mobile-bottom-nav a.active .nav-label {{
            color: {t['accent']};
            font-weight: 700;
        }}
        /* 桌面端隐藏底部导航（侧边栏已够用） */
        @media (min-width: 768px) {{
            .mobile-bottom-nav, .mobile-nav-spacer {{
                display: none;
            }}
        }}
    </style>
    <div class="mobile-nav-spacer"></div>
    <div class="mobile-bottom-nav">
        <a href="/{tp}" target="_self">
            <span class="nav-icon">🏠</span>
            <span class="nav-label">首页</span>
        </a>
        <a href="/安全知识问答{tp}" target="_self">
            <span class="nav-icon">💬</span>
            <span class="nav-label">问答</span>
        </a>
        <a href="/工地隐患识别{tp}" target="_self">
            <span class="nav-icon">📷</span>
            <span class="nav-label">隐患</span>
        </a>
        <a href="/安全培训助手{tp}" target="_self">
            <span class="nav-icon">📚</span>
            <span class="nav-label">培训</span>
        </a>
        <a href="/应急处理指导{tp}" target="_self">
            <span class="nav-icon">🆘</span>
            <span class="nav-label">应急</span>
        </a>
    </div>
    """, unsafe_allow_html=True)
