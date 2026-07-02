"""Admin view: manage doctors & patients, usage stats, application secrets."""
import streamlit as st

from bm import auth, repository
from bm.ui import common


def render(user):
    st.subheader("Administration")
    tab_doctors, tab_patients, tab_stats, tab_secrets = st.tabs(
        ["Doctors", "Patients", "Usage statistics", "Application secrets"]
    )
    with tab_doctors:
        _doctors()
    with tab_patients:
        _patients()
    with tab_stats:
        _stats()
    with tab_secrets:
        _secrets()


# ---------------------------------------------------------------------------
# Doctors
# ---------------------------------------------------------------------------
def _doctors():
    st.markdown("#### Add a doctor")
    with st.form("add_doctor"):
        c1, c2 = st.columns(2)
        username = c1.text_input("Username")
        phone = c2.text_input("Phone number")
        first = c1.text_input("First name")
        last = c2.text_input("Last name")
        password = st.text_input("Initial password", type="password")
        force_change = st.checkbox("Require password change on first login", value=True)
        submitted = st.form_submit_button("Create doctor", type="primary")
    if submitted:
        if not (username and first and last and password):
            st.error("Username, first name, last name and password are required.")
        else:
            try:
                repository.create_doctor(
                    username, password, first, last, phone,
                    must_change_password=force_change,
                )
                st.success(f"Doctor '{username.lower()}' created.")
                st.rerun()
            except Exception as exc:  # noqa: BLE001 - e.g. duplicate username
                st.error(f"Could not create doctor: {exc}")

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


# ---------------------------------------------------------------------------
# Patients
# ---------------------------------------------------------------------------
def _patients():
    doctors = repository.list_doctors()
    doctor_options = {None: "— Unassigned —"}
    doctor_options.update(
        {d["id"]: f"Dr. {d['first_name']} {d['last_name']}" for d in doctors}
    )

    st.markdown("#### Add a patient")
    assigned = st.selectbox(
        "Assign to doctor", list(doctor_options.keys()),
        format_func=lambda k: doctor_options[k], key="admin_add_doctor",
    )
    values = common.patient_form("admin_add")
    if st.button("Create patient", type="primary"):
        _, username, otp = repository.create_patient(doctor_id=assigned, **values)
        st.session_state["admin_new_creds"] = (username, otp)
        st.rerun()
    creds = st.session_state.get("admin_new_creds")
    if creds:
        common.show_new_credentials(*creds)
        if st.button("Dismiss", key="admin_dismiss_creds"):
            del st.session_state["admin_new_creds"]
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
# Secrets
# ---------------------------------------------------------------------------
def _secrets():
    st.markdown("#### Application secrets")
    st.caption(
        "Stored secrets are used by the app at runtime (e.g. OPENAI_API_KEY, "
        "OPENAI_CHAT_MODEL, OPENAI_STT_MODEL for voice transcription)."
    )
    with st.form("add_secret"):
        key = st.text_input("Key", placeholder="OPENAI_API_KEY")
        value = st.text_input("Value", type="password")
        submitted = st.form_submit_button("Save secret", type="primary")
    if submitted:
        if not key or not value:
            st.error("Both key and value are required.")
        else:
            repository.set_secret(key, value)
            st.success(f"Secret '{key.strip()}' saved.")
            st.rerun()

    st.divider()
    secrets_rows = repository.list_secrets()
    if not secrets_rows:
        st.info("No secrets stored yet.")
        return
    for s in secrets_rows:
        c1, c2, c3 = st.columns([3, 3, 1])
        c1.text(s["key"])
        masked = (s["value"][:2] + "•" * max(len(s["value"]) - 2, 0)) if s["value"] else ""
        c2.text(masked)
        if c3.button("Delete", key=f"sdel_{s['key']}"):
            repository.delete_secret(s["key"])
            st.rerun()
