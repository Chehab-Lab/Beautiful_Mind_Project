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
}

html, body { -webkit-font-smoothing: antialiased; -moz-osx-font-smoothing: grayscale; }
[data-testid="stAppViewContainer"], [data-testid="stHeader"] { background: var(--bm-bg); }

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
/* The landing page is a real marketing/article page, so it gets more room
   than the mobile-first dashboards (which keep the 680px block-container). */
.block-container:has(.bm-nav) {
    max-width: 940px !important;
    padding-top: 0 !important;
}

/* ----- Nav bar ----- */
.bm-nav {
    display: flex;
    align-items: baseline;
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
    font-weight: 800;
    letter-spacing: -0.02em;
    color: var(--bm-text);
}
.bm-nav-logo span { color: var(--bm-primary); }
.bm-nav-tag {
    font-size: 0.82rem;
    font-weight: 500;
    color: var(--bm-muted);
    white-space: nowrap;
}
@media (max-width: 640px) { .bm-nav-tag { display: none; } }

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

/* ----- Login card: black, sleek, sits at the top of the page ----- */
div[class*="st-key-bm_login_card"] {
    background: linear-gradient(165deg, #17171f, #0a0a0e);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 18px;
    padding: 1.9rem 1.7rem 1.6rem;
    box-shadow: 0 24px 48px -16px rgba(0, 0, 0, 0.45), 0 2px 10px rgba(0, 0, 0, 0.2);
}
.bm-login-eyebrow {
    color: rgba(255, 255, 255, 0.45);
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    font-weight: 700;
    margin-bottom: 0.35rem;
}
.bm-login-title { color: #fff; font-size: 1.4rem; font-weight: 800; margin: 0 0 0.2rem; }
.bm-login-sub { color: rgba(255, 255, 255, 0.5); font-size: 0.88rem; margin-bottom: 1.2rem; }
div[class*="st-key-bm_login_card"] [data-testid="stWidgetLabel"] p {
    color: rgba(255, 255, 255, 0.7) !important;
    font-weight: 600;
}
div[class*="st-key-bm_login_card"] input {
    background: rgba(255, 255, 255, 0.06) !important;
    border: 1px solid rgba(255, 255, 255, 0.14) !important;
    color: #fff !important;
}
div[class*="st-key-bm_login_card"] input::placeholder { color: rgba(255, 255, 255, 0.32); }
div[class*="st-key-bm_login_card"] input:focus {
    border-color: #818CF8 !important;
    box-shadow: 0 0 0 3px rgba(129, 140, 248, 0.28) !important;
}
div[class*="st-key-bm_login_card"] [data-testid="stForm"] { border: none; padding: 0; }
div[class*="st-key-bm_login_card"] .stFormSubmitButton > button {
    background: #fff;
    color: var(--bm-ink);
    border: none;
    font-weight: 700;
    box-shadow: none;
}
div[class*="st-key-bm_login_card"] .stFormSubmitButton > button:hover { background: #EEF0FF; }
div[class*="st-key-bm_login_card"] div[data-testid="stAlert"] {
    background: rgba(239, 68, 68, 0.15);
    color: #FCA5A5;
    border: 1px solid rgba(239, 68, 68, 0.3);
}

/* ----- About: Medium-style journalistic article ----- */
.bm-about { max-width: 680px; margin: 4rem auto 0; }
.bm-kicker {
    font-family: Georgia, 'Times New Roman', serif;
    font-style: italic;
    color: var(--bm-muted);
    font-size: 0.98rem;
    margin-bottom: 0.6rem;
}
.bm-about-title {
    font-family: Georgia, 'Times New Roman', serif;
    font-size: 2.05rem;
    line-height: 1.28;
    font-weight: 700;
    color: var(--bm-text);
    letter-spacing: -0.01em;
    margin: 0 0 1.5rem;
}
.bm-lede {
    font-family: Georgia, 'Times New Roman', serif;
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
    font-family: Georgia, 'Times New Roman', serif;
    font-size: 1.34rem;
    font-weight: 700;
    color: var(--bm-text);
    margin: 2.3rem 0 0.6rem;
}
.bm-section p {
    font-family: Georgia, 'Times New Roman', serif;
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
    font-family: Georgia, 'Times New Roman', serif;
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
