"""Doctor view: manage the doctor's own patients."""
import streamlit as st

from bm import repository
from bm.ui import common


def render(user):
    doctor = repository.get_doctor_by_user(user["id"])
    if doctor is None:
        st.error("No doctor profile is linked to this account.")
        return

    st.subheader(f"Dr. {doctor['first_name']} {doctor['last_name']}")
    st.caption("Manage your patients")

    tab_list, tab_add, tab_account = st.tabs(["My patients", "Add patient", "Account"])

    with tab_add:
        _add_patient(doctor)

    with tab_list:
        _list_patients(doctor)

    with tab_account:
        st.markdown("#### Change password")
        common.change_password_form(user["id"])


def _add_patient(doctor):
    # After a patient is created, show their one-time credentials.
    creds = st.session_state.get("last_created_credentials")
    if creds:
        common.show_new_credentials(*creds)
        if st.button("Done", key="dismiss_creds"):
            del st.session_state["last_created_credentials"]
            st.rerun()
        return

    # The form stays hidden until the doctor chooses to add a patient.
    if not st.session_state.get("doc_show_add_patient"):
        if st.button("Add patient", type="primary", key="doc_add_open"):
            st.session_state["doc_show_add_patient"] = True
            st.rerun()
        return

    st.markdown("#### New patient")
    values = common.patient_form("doc_add")
    b1, b2 = st.columns(2)
    if b1.button("Create patient", type="primary", key="doc_add_create"):
        patient, username, one_time_password = repository.create_patient(
            doctor_id=doctor["id"], **values
        )
        st.session_state["last_created_credentials"] = (username, one_time_password)
        st.session_state["doc_show_add_patient"] = False
        st.rerun()
    if b2.button("Cancel", key="doc_add_cancel"):
        st.session_state["doc_show_add_patient"] = False
        st.rerun()


def _list_patients(doctor):
    patients = repository.list_patients(doctor_id=doctor["id"])
    if not patients:
        st.info("You have no patients yet. Use the 'Add patient' tab to create one.")
        return

    for p in patients:
        label = p["alias"] or p["username"]
        with st.expander(f"{label}  ·  {p['username']}"):
            _edit_patient(p)


def _edit_patient(p):
    values = common.patient_form(f"edit_{p['id']}", defaults=p)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("Save changes", key=f"save_{p['id']}", type="primary"):
            repository.update_patient(p["id"], **values)
            st.success("Patient updated.")
    with col2:
        if st.button("Reset password", key=f"reset_{p['id']}"):
            new_pw = repository.reset_patient_password(p["user_id"])
            st.session_state[f"reset_pw_{p['id']}"] = new_pw
    with col3:
        if st.button("Remove patient", key=f"del_{p['id']}"):
            repository.delete_user_cascade(p["user_id"])
            st.success("Patient removed.")
            st.rerun()

    reset_pw = st.session_state.get(f"reset_pw_{p['id']}")
    if reset_pw:
        st.info("New one-time password (shown once):")
        st.code(f"Username: {p['username']}\nOne-time password: {reset_pw}", language="text")
