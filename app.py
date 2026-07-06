"""BeautifulMind — Streamlit application entry point.

Single-page, role-based app: login routes to the doctor, patient or admin
experience. A signed-in session is remembered in a browser cookie backed by a
server-side sessions table, so reopening the link (e.g. on a phone) keeps the
user logged in until the session expires.
"""
import datetime
import os
import sys

import extra_streamlit_components as stx
import streamlit as st

# Make the ``bm`` package importable when Streamlit runs this file directly.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bm import auth, db, repository  # noqa: E402
from bm.ui import admin as admin_ui  # noqa: E402
from bm.ui import common  # noqa: E402
from bm.ui import doctor as doctor_ui  # noqa: E402
from bm.ui import patient as patient_ui  # noqa: E402
from bm.ui import theme  # noqa: E402

st.set_page_config(page_title="Beautiful Mind", layout="centered")

theme.inject()
db.init_db()

COOKIE_NAME = "bm_auth"
REMEMBER_DAYS = 60

# One CookieManager per run reads/writes the browser's cookies.
cookie_manager = stx.CookieManager(key="bm_cookie_manager")


def _write_pending_cookie():
    """Persist the login cookie on a run of its own.

    The cookie is written here rather than right after authentication so that
    no ``st.rerun()`` races the browser's cookie write (a common reason cookies
    don't stick with Streamlit cookie components).
    """
    token = st.session_state.pop("_pending_cookie", None)
    if token:
        cookie_manager.set(
            COOKIE_NAME,
            token,
            expires_at=datetime.datetime.now() + datetime.timedelta(days=REMEMBER_DAYS),
        )


def _boot_splash():
    """Loading screen shown while the browser reports the auth cookie."""
    st.markdown(
        """
<style>
@keyframes bmSpin { to { transform: rotate(360deg); } }
.bm-splash {
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    min-height: 60vh; gap: 16px;
}
.bm-splash .ring {
    width: 40px; height: 40px; border-radius: 50%;
    border: 3px solid #E6E8F1; border-top-color: #4F46E5;
    animation: bmSpin 0.8s linear infinite;
}
.bm-splash .cap { color: #5a6072; font-size: 1.05rem; letter-spacing: 0.03em; }
</style>
<div class="bm-splash">
    <div class="ring"></div>
    <div class="cap">loading …</div>
</div>
""",
        unsafe_allow_html=True,
    )


def _restore_or_wait():
    """Restore the user from the cookie, or show the splash for one boot cycle.

    The cookie component reports ``{}`` both before it has loaded and when there
    is genuinely no cookie, so we wait exactly one run: on the first boot run we
    show the splash; by the next run the browser has reported the real cookie.
    """
    if st.session_state.get("user"):
        return
    token = cookie_manager.get(cookie=COOKIE_NAME)
    if token:
        user = repository.get_session_user(token)
        if user:
            st.session_state["user"] = user
            st.session_state["_auth_token"] = token
        return
    if not st.session_state.get("_boot_waited"):
        st.session_state["_boot_waited"] = True
        _boot_splash()
        st.stop()


def _do_login(username, password):
    user = auth.authenticate(username, password)
    if user is None:
        st.error("Invalid username or password.")
        return
    token = repository.create_session(user["id"], days=REMEMBER_DAYS)
    st.session_state["user"] = user
    st.session_state["_auth_token"] = token
    # Deferred to the next run so the cookie write isn't cut off by rerun.
    st.session_state["_pending_cookie"] = token
    st.rerun()


def _go_to(page):
    st.session_state["_page"] = page
    st.rerun()


def _nav_bar():
    """Nav bar with a plain (non-link) wordmark and an About/Home toggle.

    The toggle is a real Streamlit button so switching pages reruns the app
    in place — no full page navigation, no new tab.
    """
    with st.container(key="bm_nav"):
        left, right = st.columns([3, 1])
        with left:
            st.markdown('<div class="bm-nav-logo">Beautiful Mind</div>', unsafe_allow_html=True)
        with right:
            if st.session_state.get("_page") == "about":
                if st.button("Home", key="nav_home"):
                    _go_to("login")
            else:
                if st.button("About", key="nav_about"):
                    _go_to("about")


def login_view():
    """Signed-out landing page: nav bar plus a centered login form."""
    theme.inject_landing()
    _nav_bar()

    _, mid, _ = st.columns([1, 1.2, 1])
    with mid:
        with st.container(key="bm_login_box"):
            st.subheader("Sign in")
            with st.form("login"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                submitted = st.form_submit_button("Sign in", type="primary")
            if submitted:
                _do_login(username, password)


def about_view():
    """A plain, generic About page describing the research project."""
    theme.inject_landing()
    _nav_bar()

    st.title("About the Project")
    st.write(
        "The Beautiful Mind project is a pioneering research initiative at Chehab "
        "Lab, American University of Beirut. We collect audio journals to unlock "
        "insights into mental well-being through advanced analysis."
    )

    st.subheader("Audio Journals")
    st.write(
        "Participants share their daily thoughts and emotions through secure, "
        "private voice recordings."
    )
    st.subheader("Insightful Analysis")
    st.write(
        "We use cutting-edge computational methods to analyze transcribed text "
        "and sentiment to better understand mental health."
    )
    st.subheader("Chehab Lab at AUB")
    st.write(
        "A flagship research initiative within the American University of Beirut "
        "(AUB), led by dedicated researchers."
    )

    st.subheader("Your Privacy is Our Priority")
    st.write(
        "The Beautiful Mind project is built on trust. All collected data is "
        "strictly secured and completely anonymized. Your identity is never linked "
        "to your recordings, ensuring your journey remains private while "
        "contributing to vital research."
    )

    st.subheader("Get in Touch")
    st.write("Interested in participating or learning more about our research?")
    st.write("amm90@mail.aub.edu  \nAmerican University of Beirut  \nChehab Lab Research Initiative")

    st.subheader("Legal Information")
    with st.expander("Research Participation"):
        st.write(
            "By participating in the Beautiful Mind Project, you contribute to a "
            "research initiative at AUB's Chehab Lab. Your participation is voluntary "
            "and focused on advancing mental health analytics."
        )
    with st.expander("Data Usage & Security"):
        st.write(
            "All data is processed using state-of-the-art anonymization techniques "
            "to ensure participant privacy and confidentiality. Audio files are "
            "stored securely using industry-standard protection measures and are "
            "accessible only to authorized research personnel. Audio processing is "
            "performed through OpenAI APIs in accordance with applicable data "
            "protection standards. We do not sell, trade, or share any "
            "individual-level data with third parties under any circumstances."
        )
    with st.expander("Medical Disclaimer"):
        st.write(
            "This project is for research purposes only. It does not provide "
            "medical advice, diagnosis, or treatment. It is not a substitute for "
            "professional mental health services or emergency intervention."
        )
    with st.expander("Terms of Service"):
        st.write(
            "Use of this platform constitutes acceptance of our research "
            "protocols. Users must be 18+ or have parental consent. We reserve the "
            "right to terminate access if protocols are violated."
        )


def logout():
    token = st.session_state.get("_auth_token")
    if token:
        repository.delete_session(token)  # server-side invalidation is what matters
    try:
        cookie_manager.delete(COOKIE_NAME)
    except Exception:  # noqa: BLE001 - cookie may already be gone
        pass
    st.session_state.pop("user", None)
    st.session_state.pop("_auth_token", None)
    st.rerun()


def main():
    # Write a just-issued cookie first (no reader on this run to avoid conflicts).
    _write_pending_cookie()
    _restore_or_wait()
    user = st.session_state.get("user")
    if user is None:
        if st.session_state.get("_page") == "about":
            about_view()
        else:
            login_view()
    else:
        _render_authenticated(user)
    theme.footer()


def _render_authenticated(user):
    with st.sidebar:
        st.markdown(f"**{user['username']}**")
        st.caption(user["role"].title())
        if st.button("Sign out"):
            logout()

    # A user on a one-time password must change it before doing anything else.
    if user.get("must_change_password"):
        st.title("Set your password")
        if common.change_password_form(user["id"], must_change=True):
            user["must_change_password"] = 0
            st.session_state["user"] = user
            st.rerun()
        return

    if user["role"] == "DOCTOR":
        doctor_ui.render(user)
    elif user["role"] == "PATIENT":
        patient_ui.render(user)
    elif user["role"] == "ADMIN":
        admin_ui.render(user)
    else:
        st.error("Unknown role.")


main()
