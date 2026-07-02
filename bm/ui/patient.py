"""Patient view: record voice notes, review anonymized history, change password."""
import base64

import streamlit as st

from bm import ai, audio, repository
from bm.ui import common, recorder

_MIME_SUFFIX = {
    "audio/webm": ".webm",
    "audio/ogg": ".ogg",
    "audio/mp4": ".mp4",
    "audio/aac": ".aac",
    "audio/mpeg": ".mp3",
    "audio/wav": ".wav",
}


def _suffix_for(mime):
    base = (mime or "").split(";")[0].strip()
    return _MIME_SUFFIX.get(base, ".webm")


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

    # Show a one-off confirmation after a note was just saved.
    if st.session_state.pop("note_saved", False):
        st.success("Your note was saved. You can record another one, or find it "
                   "under 'My notes'.")

    result = recorder.record_button(key="voice_recorder")
    if not result or not result.get("audio"):
        return
    # Ignore reruns that replay the same recording.
    if result.get("id") == st.session_state.get("last_record_id"):
        return
    st.session_state["last_record_id"] = result.get("id")

    audio_bytes = base64.b64decode(result["audio"])
    duration = float(result.get("duration") or 0)
    suffix = _suffix_for(result.get("mime"))
    with st.spinner("Transcribing and anonymizing…"):
        try:
            transcript = ai.transcribe(audio_bytes, suffix=suffix)
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
    # Return to a clean recorder without revealing the transcription.
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
