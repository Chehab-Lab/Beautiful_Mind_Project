"""Admin view: manage doctors and patients, and view usage statistics."""
import streamlit as st

from bm import db, repository
from bm.ui import common


def render(user):
    st.subheader("Administration")
    tab_doctors, tab_patients, tab_stats, tab_danger = st.tabs(
        ["Doctors", "Patients", "Usage statistics", "Danger zone"]
    )
    with tab_doctors:
        _doctors()
    with tab_patients:
        _patients()
    with tab_stats:
        _stats()
    with tab_danger:
        _danger_zone()


# ---------------------------------------------------------------------------
# Doctors
# ---------------------------------------------------------------------------
def _doctors():
    if st.session_state.get("admin_show_add_doctor"):
        _add_doctor_form()
    elif st.button("Add doctor", type="primary", key="admin_add_doctor_open"):
        st.session_state["admin_show_add_doctor"] = True
        st.rerun()

    st.divider()
    st.markdown("#### Existing doctors")
    doctors = repository.list_doctors()
    if not doctors:
        st.info("No doctors yet.")
        return
    for d in doctors:
        with st.expander(f"Dr. {d['first_name']} {d['last_name']}  ·  {d['username']}"):
            c1, c2 = st.columns(2)
            first = c1.text_input("First name", d["first_name"], key=f"df_{d['id']}")
            last = c2.text_input("Last name", d["last_name"], key=f"dl_{d['id']}")
            phone = st.text_input("Phone", d["phone_number"] or "", key=f"dp_{d['id']}")
            b1, b2 = st.columns(2)
            if b1.button("Save", key=f"dsave_{d['id']}", type="primary"):
                repository.update_doctor(d["id"], first, last, phone)
                st.success("Saved.")
            if b2.button("Delete", key=f"ddel_{d['id']}"):
                repository.delete_user_cascade(d["user_id"])
                st.success("Doctor deleted.")
                st.rerun()


def _add_doctor_form():
    st.markdown("#### Add a doctor")
    with st.form("add_doctor"):
        c1, c2 = st.columns(2)
        username = c1.text_input("Username")
        phone = c2.text_input("Phone number")
        first = c1.text_input("First name")
        last = c2.text_input("Last name")
        password = st.text_input("Initial password", type="password")
        force_change = st.checkbox("Require password change on first login", value=True)
        b1, b2 = st.columns(2)
        submitted = b1.form_submit_button("Create doctor", type="primary")
        cancelled = b2.form_submit_button("Cancel")
    if cancelled:
        st.session_state["admin_show_add_doctor"] = False
        st.rerun()
    if submitted:
        if not (username and first and last and password):
            st.error("Username, first name, last name and password are required.")
        else:
            try:
                repository.create_doctor(
                    username, password, first, last, phone,
                    must_change_password=force_change,
                )
                st.session_state["admin_show_add_doctor"] = False
                st.success(f"Doctor '{username.lower()}' created.")
                st.rerun()
            except Exception as exc:  # noqa: BLE001 - e.g. duplicate username
                st.error(f"Could not create doctor: {exc}")


# ---------------------------------------------------------------------------
# Patients
# ---------------------------------------------------------------------------
def _patients():
    doctors = repository.list_doctors()
    doctor_options = {None: "— Unassigned —"}
    doctor_options.update(
        {d["id"]: f"Dr. {d['first_name']} {d['last_name']}" for d in doctors}
    )

    creds = st.session_state.get("admin_new_creds")
    if creds:
        common.show_new_credentials(*creds)
        if st.button("Done", key="admin_dismiss_creds"):
            del st.session_state["admin_new_creds"]
            st.rerun()
    elif st.session_state.get("admin_show_add_patient"):
        _add_patient_form(doctor_options)
    elif st.button("Add patient", type="primary", key="admin_add_patient_open"):
        st.session_state["admin_show_add_patient"] = True
        st.rerun()

    st.divider()
    st.markdown("#### Existing patients")
    patients = repository.list_patients()
    if not patients:
        st.info("No patients yet.")
        return
    for p in patients:
        label = p["alias"] or p["username"]
        with st.expander(f"{label}  ·  {p['username']}"):
            values = common.patient_form(f"admin_edit_{p['id']}", defaults=p)
            current_doctor = p["doctor_id"]
            new_doctor = st.selectbox(
                "Assigned doctor", list(doctor_options.keys()),
                index=list(doctor_options.keys()).index(current_doctor)
                if current_doctor in doctor_options else 0,
                format_func=lambda k: doctor_options[k],
                key=f"admin_pd_{p['id']}",
            )
            b1, b2, b3 = st.columns(3)
            if b1.button("Save", key=f"psave_{p['id']}", type="primary"):
                repository.update_patient(p["id"], doctor_id=new_doctor, **values)
                st.success("Saved.")
            if b2.button("Reset password", key=f"preset_{p['id']}"):
                st.session_state[f"admin_reset_{p['id']}"] = (
                    repository.reset_patient_password(p["user_id"])
                )
            if b3.button("Delete", key=f"pdel_{p['id']}"):
                repository.delete_user_cascade(p["user_id"])
                st.success("Patient deleted.")
                st.rerun()
            reset_pw = st.session_state.get(f"admin_reset_{p['id']}")
            if reset_pw:
                st.code(f"Username: {p['username']}\nOne-time password: {reset_pw}",
                        language="text")


def _add_patient_form(doctor_options):
    st.markdown("#### Add a patient")
    assigned = st.selectbox(
        "Assign to doctor", list(doctor_options.keys()),
        format_func=lambda k: doctor_options[k], key="admin_add_doctor",
    )
    values = common.patient_form("admin_add")
    b1, b2 = st.columns(2)
    if b1.button("Create patient", type="primary", key="admin_add_create"):
        _, username, otp = repository.create_patient(doctor_id=assigned, **values)
        st.session_state["admin_new_creds"] = (username, otp)
        st.session_state["admin_show_add_patient"] = False
        st.rerun()
    if b2.button("Cancel", key="admin_add_cancel"):
        st.session_state["admin_show_add_patient"] = False
        st.rerun()


# ---------------------------------------------------------------------------
# Usage statistics
# ---------------------------------------------------------------------------
def _stats():
    totals = repository.usage_totals()
    st.markdown("#### Aggregated usage")
    c1, c2, c3 = st.columns(3)
    c1.metric("Voice requests", int(totals["voice_requests"]))
    c2.metric("Voice duration", f"{totals['total_duration']:.0f} s")
    c3.metric("Transcribed tokens", int(totals["total_tokens"]))

    st.markdown("#### Per-patient usage")
    rows = repository.usage_per_patient()
    if not rows:
        st.info("No patients yet.")
        return
    table = [
        {
            "Patient": r["alias"] or r["username"],
            "Username": r["username"],
            "Voice requests": int(r["voice_requests"]),
            "Voice duration (s)": round(r["total_duration"], 1),
            "Transcribed tokens": int(r["total_tokens"]),
        }
        for r in rows
    ]
    st.dataframe(table, use_container_width=True, hide_index=True)


# ---------------------------------------------------------------------------
# Danger zone
# ---------------------------------------------------------------------------
_RESET_PHRASE = "RESET"


@st.dialog("Reset the database?")
def _confirm_reset_dialog():
    st.error(
        "This permanently deletes **all** doctors, patients, notes and usage "
        "data. Only the default `admin` / `admin` account will remain, and you "
        "will be signed out. This cannot be undone."
    )
    phrase = st.text_input(f"Type {_RESET_PHRASE} to confirm", key="reset_phrase")
    c1, c2 = st.columns(2)
    if c1.button("Cancel", use_container_width=True, key="reset_cancel"):
        st.rerun()
    if c2.button(
        "Reset database",
        type="primary",
        use_container_width=True,
        disabled=phrase.strip().upper() != _RESET_PHRASE,
        key="reset_confirm",
    ):
        db.reset_db()
        # The current session row is gone; drop the in-memory user so the next
        # run lands on the login screen.
        st.session_state.pop("user", None)
        st.session_state.pop("_auth_token", None)
        st.rerun()


def _danger_zone():
    st.markdown("#### Reset database")
    st.caption(
        "Wipe all doctors, patients, notes and usage data and restore the "
        "default admin account. This is irreversible."
    )
    if st.button("Reset database", key="danger_reset_open"):
        _confirm_reset_dialog()
