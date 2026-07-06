"""Mobile-first look and feel: a single-hue (indigo) palette + slate neutrals,
rectangular modern tabs, elevated controls, and a footer."""
import base64
import os

import streamlit as st

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_LOGO_PATH = os.path.join(_ROOT, "chehab-lab-logo.png")


def _logo_data_uri():
    try:
        with open(_LOGO_PATH, "rb") as fh:
            return "data:image/png;base64," + base64.b64encode(fh.read()).decode("ascii")
    except OSError:
        return ""


_LOGO_URI = _logo_data_uri()

_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Roboto:ital,wght@0,400;0,500;0,700;0,900;1,400&display=swap');

:root {
    --bm-primary: #4F46E5;      /* indigo 600 — the single brand hue */
    --bm-primary-700: #4338CA;
    --bm-primary-50: #EEF2FF;
    --bm-primary-100: #E0E7FF;
    --bm-bg: #FFFFFF;
    --bm-surface: #FFFFFF;
    --bm-text: #1F2333;
    --bm-muted: #6B7280;
    --bm-border: #E6E8F1;
    --bm-danger: #EF4444;
    --bm-ink: #0B0B10;
    --bm-font: 'Roboto', -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
}

html, body { -webkit-font-smoothing: antialiased; -moz-osx-font-smoothing: grayscale; }
[data-testid="stAppViewContainer"], [data-testid="stHeader"] { background: var(--bm-bg); }
html, body, [data-testid="stAppViewContainer"], [data-testid="stSidebar"],
[data-testid="stMarkdownContainer"], [data-testid="stWidgetLabel"],
.stTextInput input, .stNumberInput input, .stTextArea textarea,
.stButton button, .stFormSubmitButton button, .stDownloadButton button {
    font-family: var(--bm-font);
}

/* ----- Layout: tight, phone-width ----- */
.block-container {
    padding: 1.1rem 1rem 2rem;
    max-width: 680px;
}
h1, h2, h3 { letter-spacing: -0.01em; color: var(--bm-text); }
h1 { font-size: 1.6rem; }

/* ----- Rectangular modern tabs (sticky, scrollable) ----- */
div[data-testid="stTabs"] div[data-baseweb="tab-list"] {
    position: sticky;
    top: 0;
    z-index: 6;
    gap: 0.3rem;
    padding: 0.3rem;
    margin-bottom: 1rem;
    overflow-x: auto;
    flex-wrap: nowrap;
    -webkit-overflow-scrolling: touch;
    background: var(--bm-surface);
    border: 1px solid var(--bm-border);
    border-radius: 12px;
    box-shadow: 0 1px 3px rgba(20, 25, 60, 0.05);
}
div[data-testid="stTabs"] div[data-baseweb="tab-list"]::-webkit-scrollbar { display: none; }
div[data-testid="stTabs"] button[data-baseweb="tab"] {
    flex: 0 0 auto;
    white-space: nowrap;
    border: none;
    border-radius: 8px;
    padding: 0.5rem 1rem;
    min-height: 42px;
    font-weight: 600;
    color: var(--bm-muted);
}
div[data-testid="stTabs"] button[data-baseweb="tab"]:hover {
    color: var(--bm-primary);
    background: var(--bm-primary-50);
}
div[data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"] {
    background: var(--bm-primary);
    color: #fff;
}
div[data-testid="stTabs"] div[data-baseweb="tab-highlight"],
div[data-testid="stTabs"] div[data-baseweb="tab-border"] { display: none; }

/* ----- Buttons: full-width, rounded, elevated, touch-friendly ----- */
.stButton > button, .stFormSubmitButton > button, .stDownloadButton > button {
    width: 100%;
    min-height: 48px;
    border-radius: 10px;
    font-weight: 600;
    border: 1px solid var(--bm-border);
    transition: transform 0.05s ease, box-shadow 0.15s ease, filter 0.15s ease;
}
.stButton > button:active, .stFormSubmitButton > button:active { transform: translateY(1px); }
.stButton > button[kind="primary"], .stFormSubmitButton > button[kind="primaryFormSubmit"] {
    border: none;
    box-shadow: 0 4px 12px rgba(79, 70, 229, 0.32);
}

/* ----- Inputs: larger targets, focus ring in brand hue ----- */
.stTextInput input, .stNumberInput input, .stTextArea textarea,
div[data-baseweb="select"] > div {
    border-radius: 10px !important;
    min-height: 44px;
}
.stTextInput input:focus, .stNumberInput input:focus, .stTextArea textarea:focus {
    border-color: var(--bm-primary) !important;
    box-shadow: 0 0 0 3px var(--bm-primary-100) !important;
}

/* ----- Cards: metrics & expanders ----- */
div[data-testid="stMetric"] {
    background: var(--bm-surface);
    border: 1px solid var(--bm-border);
    border-radius: 14px;
    padding: 0.9rem 1rem;
    box-shadow: 0 1px 4px rgba(20, 25, 60, 0.05);
}
div[data-testid="stExpander"] {
    border-radius: 14px;
    border: 1px solid var(--bm-border);
    box-shadow: 0 1px 4px rgba(20, 25, 60, 0.05);
    overflow: hidden;
}

section[data-testid="stSidebar"] { border-right: 1px solid var(--bm-border); }
iframe[title="bm_voice_recorder"] { width: 100%; }

/* ----- Footer ----- */
.bm-footer {
    text-align: center;
    color: var(--bm-muted);
    font-size: 0.85rem;
    margin-top: 2.5rem;
    padding-top: 1rem;
    border-top: 1px solid var(--bm-border);
}
.bm-footer a { text-decoration: none; vertical-align: middle; }
.bm-footer .bm-heart { color: var(--bm-danger); }
.bm-footer img { height: 22px; vertical-align: middle; margin-left: 5px; }
</style>
"""


_LANDING_CSS = """
<style>
/* ----- Nav bar: plain black wordmark (not a link) + an About/Home toggle
   button. The toggle is a real Streamlit button so switching pages reruns
   the app in place instead of doing a browser navigation. ----- */
div[class*="st-key-bm_nav"] {
    position: sticky;
    top: 0;
    z-index: 50;
    background: var(--bm-surface);
    border-bottom: 1px solid var(--bm-border);
    padding: 0.9rem 0 0.7rem;
    margin-bottom: 2.2rem;
}
.bm-nav-logo {
    font-size: 1.32rem;
    font-weight: 700;
    letter-spacing: -0.01em;
    color: #000;
}
div[class*="st-key-bm_nav"] .stButton { display: flex; justify-content: flex-end; }
div[class*="st-key-bm_nav"] .stButton > button {
    width: auto !important;
    min-height: auto !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    color: var(--bm-text) !important;
    font-weight: 500;
    font-size: 0.95rem;
    padding: 0.3rem 0.2rem !important;
}
div[class*="st-key-bm_nav"] .stButton > button:hover { color: var(--bm-primary) !important; }

/* ----- Login box: black, square, right-aligned "Sign in" button ----- */
div[class*="st-key-bm_login_box"] .stFormSubmitButton { display: flex; justify-content: flex-end; }
div[class*="st-key-bm_login_box"] .stFormSubmitButton > button {
    width: auto !important;
    min-height: auto !important;
    padding: 0.65rem 1.7rem;
    border-radius: 0 !important;
    background: #000 !important;
    color: #fff !important;
    border: none !important;
    box-shadow: none !important;
}
div[class*="st-key-bm_login_box"] .stFormSubmitButton > button:hover { background: #1a1a1a !important; }
</style>
"""


def inject() -> None:
    """Inject the global mobile-first stylesheet. Call once per run."""
    st.markdown(_CSS, unsafe_allow_html=True)


def inject_landing() -> None:
    """Inject the extra stylesheet used only by the signed-out landing page."""
    st.markdown(_LANDING_CSS, unsafe_allow_html=True)


def footer() -> None:
    """Render the 'Made with love by Chehab Lab' footer."""
    logo = (f'<img src="{_LOGO_URI}" alt="Chehab Lab" />' if _LOGO_URI else "Chehab Lab")
    st.markdown(
        f'<div class="bm-footer">Made with <span class="bm-heart">&#10084;</span> by '
        f'<a href="https://chehablab.com" target="_blank" rel="noopener">{logo}</a></div>',
        unsafe_allow_html=True,
    )
