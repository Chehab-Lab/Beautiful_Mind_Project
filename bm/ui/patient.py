"""Patient view: record voice notes, review anonymized history, change password."""
import streamlit as st

from bm import ai, audio, repository
from bm.ui import common


def render(user):
    patient = repository.get_patient_by_user(user["id"])
    if patient is None:
        st.error("No patient profile is linked to this account.")
        return

    st.subheader(patient["alias"] or "My records")
    st.caption("Your voice notes are transcribed and anonymized before they are stored.")

    tab_record, tab_history, tab_account = st.tabs(
        ["Record voice note", "My notes", "Account"]
    )

    with tab_record:
        _record(patient)
    with tab_history:
        _history(patient)
    with tab_account:
        _account(user)


def _record(patient):
    if not ai.is_configured():
        st.warning(
            "Voice transcription is unavailable because the OpenAI API key has "
            "not been configured yet. Please contact your administrator."
        )
        return

    st.markdown("#### New voice note")

    # Show a one-off confirmation after a note was just saved.
    if st.session_state.pop("note_saved", False):
        st.success("Your note was saved. You can record another one, or find it "
                   "under 'My notes'.")

    # A changing key gives a fresh, empty recorder after each save.
    round_id = st.session_state.get("recorder_round", 0)
    clip = st.audio_input("Record your note", key=f"recorder_{round_id}")
    if clip is None:
        return

    if st.button("Transcribe & save", type="primary"):
        audio_bytes = clip.getvalue()
        duration = audio.wav_duration_seconds(audio_bytes)
        with st.spinner("Transcribing and anonymizing…"):
            try:
                transcript = ai.transcribe(audio_bytes)
                anonymized = ai.anonymize(transcript)
            except (ai.AIServiceError, ai.AIConfigError) as exc:
                st.error(str(exc))
                return
        tokens = audio.count_tokens(transcript)
        repository.add_note_with_usage(
            patient_id=patient["id"],
            anonymized_text=anonymized,
            duration_seconds=duration,
            transcribed_tokens=tokens,
        )
        # Reset back to a clean recorder without revealing the transcription.
        st.session_state["recorder_round"] = round_id + 1
        st.session_state["note_saved"] = True
        st.rerun()


def _history(patient):
    notes = repository.list_notes(patient["id"])
    if not notes:
        st.info("You have no saved notes yet.")
        return
    for note in notes:
        st.markdown(f"**{note['created_at']}**")
        st.write(note["anonymized_text"])
        st.divider()


def _account(user):
    common.change_password_form(user["id"], must_change=bool(user.get("must_change_password")))
