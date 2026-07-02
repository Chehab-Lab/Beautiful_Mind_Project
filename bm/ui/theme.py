"""Mobile-first look and feel for the app (injected CSS + floating actions)."""
import streamlit as st

_CSS = """
<style>
:root { --bm-primary: #4C6FFF; --bm-primary-dark: #3b5bdb; }

/* ----- Layout: tight, phone-width, room for the floating button ----- */
.block-container {
    padding-top: 1.1rem;
    padding-bottom: 6rem;
    padding-left: 1rem;
    padding-right: 1rem;
    max-width: 680px;
}
h1, h2, h3 { letter-spacing: -0.01em; }
h1 { font-size: 1.6rem; }

/* ----- Sticky, scrollable pill tabs ----- */
div[data-testid="stTabs"] div[data-baseweb="tab-list"] {
    position: sticky;
    top: 0;
    z-index: 6;
    gap: 0.35rem;
    padding: 0.3rem;
    margin-bottom: 0.5rem;
    overflow-x: auto;
    flex-wrap: nowrap;
    -webkit-overflow-scrolling: touch;
    background: var(--secondary-background-color, #fff);
    border-radius: 14px;
    box-shadow: 0 1px 4px rgba(20, 30, 70, 0.06);
}
div[data-testid="stTabs"] div[data-baseweb="tab-list"]::-webkit-scrollbar { display: none; }
div[data-testid="stTabs"] button[data-baseweb="tab"] {
    flex: 0 0 auto;
    white-space: nowrap;
    border-radius: 10px;
    padding: 0.45rem 0.9rem;
    min-height: 42px;
    color: #4a5169;
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
    border-radius: 12px;
    font-weight: 600;
    border: 1px solid #e3e6f0;
    box-shadow: 0 2px 6px rgba(20, 30, 70, 0.08);
    transition: transform 0.05s ease, box-shadow 0.15s ease, filter 0.15s ease;
}
.stButton > button:active, .stFormSubmitButton > button:active { transform: translateY(1px); }
.stButton > button[kind="primary"], .stFormSubmitButton > button[kind="primaryFormSubmit"] {
    border: none;
    box-shadow: 0 4px 12px rgba(76, 111, 255, 0.35);
}

/* ----- Inputs: larger tap targets, rounded ----- */
.stTextInput input, .stNumberInput input, .stTextArea textarea,
div[data-baseweb="select"] > div {
    border-radius: 10px !important;
    min-height: 44px;
}

/* ----- Cards: metrics & expanders ----- */
div[data-testid="stMetric"] {
    background: #fff;
    border: 1px solid #eceef5;
    border-radius: 14px;
    padding: 0.9rem 1rem;
    box-shadow: 0 1px 4px rgba(20, 30, 70, 0.05);
}
div[data-testid="stExpander"] {
    border-radius: 14px;
    border: 1px solid #eceef5;
    box-shadow: 0 1px 4px rgba(20, 30, 70, 0.05);
    overflow: hidden;
}

/* ----- Roomier sidebar on mobile drawer ----- */
section[data-testid="stSidebar"] { border-right: 1px solid #eceef5; }

/* ----- Custom recorder component sits flush and centered ----- */
iframe[title="bm_voice_recorder"] { width: 100%; }
</style>
"""


def inject() -> None:
    """Inject the global mobile-first stylesheet. Call once per run."""
    st.markdown(_CSS, unsafe_allow_html=True)
