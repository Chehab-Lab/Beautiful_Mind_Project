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
html { scroll-behavior: smooth; }

/* The landing page is a real marketing/article page, so it gets more room
   than the mobile-first dashboards (which keep the 680px block-container). */
.block-container:has(.bm-nav) {
    max-width: 940px !important;
    padding-top: 0 !important;
}

/* ----- Nav bar ----- */
.bm-nav {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.75rem;
    padding: 1.15rem 0.1rem;
    margin-bottom: 2.4rem;
    border-bottom: 1px solid var(--bm-border);
    position: sticky;
    top: 0;
    z-index: 50;
    background: var(--bm-surface);
}
.bm-nav-logo {
    font-size: 1.32rem;
    font-weight: 700;
    letter-spacing: -0.01em;
    color: var(--bm-text);
}

/* Desktop nav links */
.bm-nav-links { display: flex; align-items: center; gap: 1.75rem; }
.bm-nav-links a {
    color: var(--bm-text);
    font-weight: 500;
    font-size: 0.95rem;
    text-decoration: none;
}
.bm-nav-links a:hover { color: var(--bm-primary); }

/* Mobile hamburger + dropdown (pure CSS via <details>/<summary>) */
.bm-nav-burger { display: none; position: relative; }
.bm-nav-burger summary { list-style: none; cursor: pointer; }
.bm-nav-burger summary::-webkit-details-marker { display: none; }
.bm-burger-icon { display: flex; flex-direction: column; gap: 4px; padding: 8px; }
.bm-burger-icon span { width: 22px; height: 2px; background: var(--bm-text); display: block; }
.bm-burger-menu {
    position: absolute;
    right: 0;
    top: calc(100% + 6px);
    min-width: 150px;
    background: #fff;
    border: 1px solid var(--bm-border);
    box-shadow: 0 12px 24px rgba(0, 0, 0, 0.12);
    padding: 0.35rem;
    z-index: 60;
}
.bm-burger-menu a {
    display: block;
    padding: 0.6rem 0.7rem;
    color: var(--bm-text);
    text-decoration: none;
    font-weight: 500;
    font-size: 0.95rem;
}
.bm-burger-menu a:hover { background: var(--bm-primary-50); color: var(--bm-primary); }

@media (max-width: 640px) {
    .bm-nav-links { display: none; }
    .bm-nav-burger { display: block; }
}

/* ----- Hero ----- */
.bm-eyebrow {
    text-transform: uppercase;
    letter-spacing: 0.14em;
    font-size: 0.72rem;
    font-weight: 700;
    color: var(--bm-primary);
    margin-bottom: 0.9rem;
}
.bm-hero-title {
    font-size: 2.6rem;
    line-height: 1.1;
    font-weight: 800;
    letter-spacing: -0.02em;
    color: var(--bm-text);
    margin: 0 0 1.1rem;
}
.bm-hero-sub {
    font-size: 1.06rem;
    line-height: 1.65;
    color: var(--bm-muted);
    max-width: 46ch;
}
@media (max-width: 640px) { .bm-hero-title { font-size: 2rem; } }

/* ----- Login card: a flat black sleek rectangle, square-cornered ----- */
div[class*="st-key-bm_login_card"] {
    background: #0a0a0a;
    border: none;
    border-radius: 0;
    padding: 1.6rem 1.5rem;
    box-shadow: 0 24px 48px -16px rgba(0, 0, 0, 0.45), 0 2px 10px rgba(0, 0, 0, 0.2);
}
div[class*="st-key-bm_login_card"] input {
    background: rgba(255, 255, 255, 0.06) !important;
    border: 1px solid rgba(255, 255, 255, 0.16) !important;
    border-radius: 0 !important;
    color: #fff !important;
}
div[class*="st-key-bm_login_card"] input::placeholder { color: rgba(255, 255, 255, 0.4); }
div[class*="st-key-bm_login_card"] input:focus {
    border-color: #fff !important;
    box-shadow: 0 0 0 1px #fff !important;
}
div[class*="st-key-bm_login_card"] [data-testid="stForm"] { border: none; padding: 0; }
div[class*="st-key-bm_login_card"] .stFormSubmitButton > button {
    background: #000;
    color: #fff;
    border: 1px solid rgba(255, 255, 255, 0.25);
    border-radius: 0 !important;
    font-weight: 700;
    box-shadow: none;
}
div[class*="st-key-bm_login_card"] .stFormSubmitButton > button:hover { background: #1a1a1a; }
div[class*="st-key-bm_login_card"] div[data-testid="stAlert"] {
    background: rgba(239, 68, 68, 0.15);
    color: #FCA5A5;
    border: 1px solid rgba(239, 68, 68, 0.3);
}

/* ----- About: Medium-style journalistic article, set in Roboto ----- */
.bm-about { max-width: 680px; margin: 4rem auto 0; scroll-margin-top: 90px; }
.bm-kicker {
    font-style: italic;
    color: var(--bm-muted);
    font-size: 0.98rem;
    margin-bottom: 0.6rem;
}
.bm-about-title {
    font-size: 2.05rem;
    line-height: 1.28;
    font-weight: 700;
    color: var(--bm-text);
    letter-spacing: -0.01em;
    margin: 0 0 1.5rem;
}
.bm-lede {
    font-size: 1.2rem;
    line-height: 1.85;
    color: #2b2f3a;
}
.bm-lede.bm-dropcap:first-letter {
    float: left;
    font-size: 3.7em;
    line-height: 0.78;
    padding: 0.07em 0.12em 0 0;
    font-weight: 700;
    color: var(--bm-text);
}
.bm-section h3 {
    font-size: 1.34rem;
    font-weight: 700;
    color: var(--bm-text);
    margin: 2.3rem 0 0.6rem;
}
.bm-section p {
    font-size: 1.09rem;
    line-height: 1.8;
    color: #333743;
    margin: 0;
}
.bm-callout {
    background: var(--bm-primary-50);
    border: 1px solid var(--bm-primary-100);
    border-radius: 16px;
    padding: 1.6rem 1.7rem;
    margin: 2.8rem 0;
}
.bm-callout h3 { margin-top: 0; }
.bm-contact { border-top: 1px solid var(--bm-border); margin-top: 2.8rem; padding-top: 1.9rem; }
.bm-contact a { color: var(--bm-primary); font-weight: 700; text-decoration: none; }
.bm-legal-heading {
    font-size: 1.15rem;
    font-weight: 700;
    color: var(--bm-text);
    margin: 2.6rem 0 0.9rem;
}
div[class*="st-key-bm_legal"] { max-width: 680px; margin: 0 auto; }
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
