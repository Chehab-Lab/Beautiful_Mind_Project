"""Patient view: record voice notes, review anonymized history, change password."""
import base64
import datetime

import streamlit as st

from bm import ai, audio, repository
from bm.ui import common, recorder

# GitHub-style contribution palette (empty -> most).
_HEAT_COLORS = ["#ebedf0", "#9be9a8", "#40c463", "#30a14e", "#216e39"]
_HEAT_WEEKS = 26

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


def _fmt_dt(value):
    """Format a note timestamp without fractional seconds or timezone offset."""
    if isinstance(value, datetime.datetime):
        return value.replace(microsecond=0, tzinfo=None).strftime("%Y-%m-%d %H:%M:%S")
    text = str(value)
    return text.split(".")[0].split("+")[0].strip()


def render(user):
    patient = repository.get_patient_by_user(user["id"])
    if patient is None:
        st.error("No patient profile is linked to this account.")
        return

    st.subheader(patient["alias"] or "My records")
    st.caption("Your voice notes are transcribed and anonymized before they are stored.")

    tab_record, tab_history, tab_usage, tab_account = st.tabs(
        ["Record voice note", "My notes", "Usage", "Account"]
    )

    with tab_record:
        _record(patient)
    with tab_history:
        _history(patient)
    with tab_usage:
        _usage(patient)
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
        st.markdown(f"**{_fmt_dt(note['created_at'])}**")
        st.write(note["anonymized_text"])
        st.divider()


def _heat_level(value, max_value):
    if value <= 0 or max_value <= 0:
        return 0
    ratio = value / max_value
    if ratio < 0.25:
        return 1
    if ratio < 0.5:
        return 2
    if ratio < 0.75:
        return 3
    return 4


def _usage(patient):
    st.markdown("#### Usage")
    by_day = repository.usage_tokens_by_day(patient["id"])
    total = sum(by_day.values())
    st.metric("Total transcribed tokens", f"{total:,}")

    today = datetime.date.today()
    # Start on the Sunday that begins the window of the last _HEAT_WEEKS weeks.
    start = today - datetime.timedelta(days=_HEAT_WEEKS * 7 - 1)
    start -= datetime.timedelta(days=(start.weekday() + 1) % 7)
    max_tokens = max(by_day.values(), default=0)
    num_weeks = (today - start).days // 7 + 1

    columns = []
    for week in range(num_weeks):
        cells = []
        for weekday in range(7):
            day = start + datetime.timedelta(days=week * 7 + weekday)
            if day > today:
                cells.append('<div class="hm-cell hm-empty"></div>')
                continue
            value = by_day.get(day, 0)
            color = _HEAT_COLORS[_heat_level(value, max_tokens)]
            title = f"{value:,} tokens on {day.isoformat()}"
            cells.append(f'<div class="hm-cell" style="background:{color}" title="{title}"></div>')
        columns.append(f'<div class="hm-col">{"".join(cells)}</div>')

    legend = "".join(f'<div class="hm-cell" style="background:{c}"></div>' for c in _HEAT_COLORS)
    html = f"""
<style>
.hm-wrap {{ overflow-x: auto; -webkit-overflow-scrolling: touch; padding: 4px 0; }}
.hm-grid {{ display: flex; gap: 3px; min-width: max-content; }}
.hm-col {{ display: flex; flex-direction: column; gap: 3px; }}
.hm-cell {{ width: 13px; height: 13px; border-radius: 3px; background: #ebedf0; }}
.hm-empty {{ background: transparent; }}
.hm-legend {{ display: flex; align-items: center; gap: 4px; margin-top: 10px;
    font-size: 0.8rem; color: #5a6072; }}
</style>
<div class="hm-wrap"><div class="hm-grid">{"".join(columns)}</div></div>
<div class="hm-legend">Less {legend} More</div>
"""
    st.markdown(html, unsafe_allow_html=True)
    st.caption(f"Total transcribed tokens per day over the last {_HEAT_WEEKS} weeks. "
               "Hover a square to see the daily count.")


def _account(user):
    common.change_password_form(user["id"], must_change=bool(user.get("must_change_password")))
