"""Shared UI widgets used across roles."""
import streamlit as st

from bm import auth

GENDER_LABELS = {"M": "Male", "F": "Female", "O": "Other"}
GENDER_VALUES = list(GENDER_LABELS.keys())


def patient_form(prefix, defaults=None):
    """Render patient demographic/clinical inputs. Returns a dict of values."""
    defaults = defaults or {}
    col1, col2 = st.columns(2)
    with col1:
        alias = st.text_input("Alias", value=defaults.get("alias", ""), key=f"{prefix}_alias")
        gender = st.selectbox(
            "Gender",
            GENDER_VALUES,
            index=GENDER_VALUES.index(defaults.get("gender", "O")),
            format_func=lambda g: GENDER_LABELS[g],
            key=f"{prefix}_gender",
        )
        age = st.number_input(
            "Age", min_value=0, max_value=120,
            value=int(defaults.get("age") or 0), key=f"{prefix}_age",
        )
        married = st.checkbox(
            "Married", value=bool(defaults.get("married")), key=f"{prefix}_married"
        )
        smoke = st.checkbox(
            "Smokes", value=bool(defaults.get("smoke")), key=f"{prefix}_smoke"
        )
    with col2:
        occupation = st.text_input(
            "Occupation", value=defaults.get("occupation", ""), key=f"{prefix}_occupation"
        )
        weekly_sport_activity = st.text_input(
            "Weekly sport activity",
            value=defaults.get("weekly_sport_activity", ""),
            key=f"{prefix}_sport",
        )
    diagnostic = st.text_area(
        "Mental illness diagnostic",
        value=defaults.get("mental_illness_diagnostic", ""),
        key=f"{prefix}_diag",
    )
    medications = st.text_area(
        "Medications", value=defaults.get("medications", ""), key=f"{prefix}_meds"
    )
    return {
        "alias": alias,
        "gender": gender,
        "age": int(age),
        "married": married,
        "smoke": smoke,
        "occupation": occupation,
        "weekly_sport_activity": weekly_sport_activity,
        "mental_illness_diagnostic": diagnostic,
        "medications": medications,
    }


def show_new_credentials(username, password):
    """Display freshly generated credentials with a clear one-time warning."""
    st.success("Patient account created. Share these credentials securely — "
               "the password is shown only once.")
    st.code(f"Username: {username}\nOne-time password: {password}", language="text")


def change_password_form(user_id, must_change=False):
    """Render a change-password form. Returns True if the password was changed."""
    if must_change:
        st.warning("You are using a one-time password. Please set a new password to continue.")
    with st.form("change_password_form"):
        new1 = st.text_input("New password", type="password")
        new2 = st.text_input("Confirm new password", type="password")
        submitted = st.form_submit_button("Update password")
    if submitted:
        if len(new1) < 6:
            st.error("Password must be at least 6 characters.")
        elif new1 != new2:
            st.error("Passwords do not match.")
        else:
            auth.set_password(user_id, new1, clear_must_change=True)
            st.success("Password updated.")
            return True
    return False
