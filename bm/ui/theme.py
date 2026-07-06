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
    --bm-primary: #0A0A0A;      /* near-black — the single brand accent */
    --bm-primary-700: #000000;
    --bm-primary-50: #F3F4F6;   /* light gray hover surface */
    --bm-primary-100: #E5E7EB;  /* subtle focus ring */
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

/* Hide Streamlit's "Press Enter to submit form" / "Press Enter to apply"
   helper text under inputs, across every view. */
[data-testid="InputInstructions"],
[data-testid="stTextInputInstructions"] { display: none !important; }
html, body, [data-testid="stAppViewContainer"], [data-testid="stSidebar"],
[data-testid="stMarkdownContainer"], [data-testid="stWidgetLabel"],
.stTextInput input, .stNumberInput input, .stTextArea textarea,
.stButton button, .stFormSubmitButton button, .stDownloadButton button {
    font-family: var(--bm-font);
}

/* ----- Layout: tight, phone-width. Target the testid too (higher
   specificity) so our smaller top padding wins over Streamlit's large
   default, which otherwise leaves a big blank gap above the content. ----- */
.block-container,
[data-testid="stMainBlockContainer"],
[data-testid="stAppViewBlockContainer"] {
    padding: 1rem 1rem 2rem !important;
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
    border-radius: 10px;
    box-shadow: 0 1px 3px rgba(20, 25, 60, 0.05);
}
div[data-testid="stTabs"] div[data-baseweb="tab-list"]::-webkit-scrollbar { display: none; }
div[data-testid="stTabs"] button[data-baseweb="tab"] {
    flex: 0 0 auto;
    white-space: nowrap;
    border: none;
    border-radius: 6px;
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

/* ----- Buttons: full-width, square, touch-friendly. Primary is black to
   match the login button; secondary is a bordered white button. ----- */
.stButton > button, .stFormSubmitButton > button, .stDownloadButton > button {
    width: 100%;
    min-height: 46px;
    border-radius: 0;
    font-weight: 600;
    border: 1px solid var(--bm-border);
    background: var(--bm-surface);
    color: var(--bm-text);
    transition: background 0.15s ease, border-color 0.15s ease, transform 0.05s ease;
}
.stButton > button:hover, .stFormSubmitButton > button:hover, .stDownloadButton > button:hover {
    border-color: #000;
    color: #000;
}
.stButton > button:active, .stFormSubmitButton > button:active { transform: translateY(1px); }
.stButton > button[kind="primary"], .stFormSubmitButton > button[kind="primaryFormSubmit"] {
    border: none;
    background: #000;
    color: #fff;
    box-shadow: none;
}
.stButton > button[kind="primary"]:hover,
.stFormSubmitButton > button[kind="primaryFormSubmit"]:hover {
    background: #1a1a1a;
    color: #fff;
}

/* ----- Inputs: larger targets, square, black focus ring ----- */
.stTextInput input, .stNumberInput input, .stTextArea textarea,
div[data-baseweb="select"] > div {
    border-radius: 0 !important;
    min-height: 44px;
}
.stTextInput input:focus, .stNumberInput input:focus, .stTextArea textarea:focus {
    border-color: #000 !important;
    box-shadow: 0 0 0 2px rgba(0, 0, 0, 0.12) !important;
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
/* ----- Nav bar: hand-written HTML/CSS (not Streamlit widgets) so it reads
   like a real production navbar. Logo left, links right; on mobile the links
   collapse into a right-aligned hamburger via a pure-CSS <details> menu. --- */
.bm-nav {
    position: sticky;
    top: 0;
    z-index: 50;
    background: var(--bm-surface);
    border-bottom: 1px solid var(--bm-border);
    margin-bottom: 2.2rem;
}
.bm-nav-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 58px;
}
.bm-nav-logo {
    font-size: 1.25rem;
    font-weight: 700;
    letter-spacing: -0.01em;
    color: #000 !important;
    text-decoration: none !important;
    white-space: nowrap;
}
.bm-nav-links { display: flex; align-items: center; gap: 1.5rem; }
.bm-nav-links a {
    color: var(--bm-text) !important;
    text-decoration: none !important;
    font-size: 0.95rem;
    font-weight: 500;
}
.bm-nav-links a:hover { color: var(--bm-primary) !important; }

/* Mobile hamburger (pure CSS via <details>/<summary>) */
.bm-nav-menu { display: none; position: relative; }
.bm-nav-menu > summary {
    list-style: none;
    cursor: pointer;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    gap: 5px;
    width: 42px;
    height: 42px;
    margin-right: -0.4rem;
}
.bm-nav-menu > summary::-webkit-details-marker { display: none; }
.bm-nav-menu > summary > span {
    display: block;
    width: 22px;
    height: 2px;
    background: #000;
    border-radius: 2px;
}
.bm-nav-drop {
    position: absolute;
    right: 0;
    top: 48px;
    min-width: 160px;
    background: #fff;
    border: 1px solid var(--bm-border);
    border-radius: 10px;
    box-shadow: 0 12px 28px rgba(16, 20, 45, 0.14);
    padding: 0.35rem;
    z-index: 60;
}
.bm-nav-drop a {
    display: block;
    padding: 0.6rem 0.75rem;
    color: var(--bm-text) !important;
    text-decoration: none !important;
    font-size: 0.95rem;
    font-weight: 500;
    border-radius: 6px;
}
.bm-nav-drop a:hover { background: var(--bm-primary-50); color: var(--bm-primary) !important; }

@media (max-width: 640px) {
    .bm-nav-links { display: none; }
    .bm-nav-menu { display: block; }
}

/* ----- Login card: centered, compact bordered surface. Square inputs and a
   black square right-aligned "Log in" button. ----- */
div[class*="st-key-bm_login_box"] {
    max-width: 380px;
    margin: 2rem auto 0;
    padding: 1.8rem 1.7rem 1.5rem;
    background: var(--bm-surface);
    border: 1px solid var(--bm-border);
    border-radius: 14px;
    box-shadow: 0 8px 26px -14px rgba(20, 25, 60, 0.18);
}
.bm-login-head { margin-bottom: 1.2rem; }
.bm-login-title {
    font-size: 1.45rem;
    font-weight: 700;
    letter-spacing: -0.02em;
    color: var(--bm-text);
    line-height: 1.15;
}
.bm-login-sub {
    margin-top: 0.25rem;
    font-size: 0.92rem;
    color: var(--bm-muted);
}

/* The card is the only visible boundary — drop the form's own border/padding. */
div[class*="st-key-bm_login_box"] [data-testid="stForm"] {
    border: none;
    padding: 0;
}
div[class*="st-key-bm_login_box"] [data-testid="stWidgetLabel"] p {
    font-weight: 600;
    color: var(--bm-text);
}

/* Square inputs to sit cohesively with the square button. */
div[class*="st-key-bm_login_box"] .stTextInput input { border-radius: 0 !important; }
div[class*="st-key-bm_login_box"] .stTextInput input:focus {
    border-color: #000 !important;
    box-shadow: 0 0 0 2px rgba(0, 0, 0, 0.12) !important;
}

/* Log in button: black, square, right-aligned inside the card. */
div[class*="st-key-bm_login_box"] .stFormSubmitButton {
    display: flex;
    justify-content: flex-end;
    margin-top: 0.3rem;
}
div[class*="st-key-bm_login_box"] .stFormSubmitButton > button {
    width: auto !important;
    min-height: auto !important;
    padding: 0.6rem 2rem;
    border-radius: 0 !important;
    background: #000 !important;
    color: #fff !important;
    border: none !important;
    box-shadow: none !important;
    font-weight: 600;
    letter-spacing: 0.01em;
    transition: background 0.15s ease, transform 0.05s ease;
}
div[class*="st-key-bm_login_box"] .stFormSubmitButton > button:hover { background: #1a1a1a !important; }
div[class*="st-key-bm_login_box"] .stFormSubmitButton > button:active { transform: translateY(1px); }
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
