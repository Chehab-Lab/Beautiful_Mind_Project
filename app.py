"""BeautifulMind — Streamlit application entry point.

Single-page, role-based app that replaces the previous microservice stack:
login routes to the doctor, patient or admin experience.
"""
import os
import sys

import streamlit as st

# Make the ``bm`` package importable when Streamlit runs this file directly.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bm import auth, db  # noqa: E402
from bm.ui import admin as admin_ui  # noqa: E402
from bm.ui import common  # noqa: E402
from bm.ui import doctor as doctor_ui  # noqa: E402
from bm.ui import patient as patient_ui  # noqa: E402

st.set_page_config(page_title="BeautifulMind", page_icon="🧠", layout="centered")

db.init_db()


def login_view():
    st.title("🧠 BeautifulMind")
    st.caption("Sign in to continue")
    with st.form("login"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Sign in", type="primary")
    if submitted:
        user = auth.authenticate(username, password)
        if user is None:
            st.error("Invalid username or password.")
        else:
            st.session_state["user"] = user
            st.rerun()


def logout():
    st.session_state.pop("user", None)
    st.rerun()


def main():
    user = st.session_state.get("user")
    if user is None:
        login_view()
        return

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
