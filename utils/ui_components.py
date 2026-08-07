"""
共享UI样式 — 支持主题切换，与首页设计系统一致
"""
import streamlit as st


def _theme():
    """读取当前主题配色"""
    name = st.session_state.get("theme", "warm")
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
