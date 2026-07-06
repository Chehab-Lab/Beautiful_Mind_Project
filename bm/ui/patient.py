"""Patient view: record voice notes, review anonymized history, change password."""
import base64
import datetime
import html

import streamlit as st

from bm import ai, audio, repository
from bm.ui import common, recorder

# Monochrome grayscale-to-black intensity palette (empty -> at/over target).
_HEAT_COLORS = ["#EDEEF1", "#CFD2D8", "#9AA0AB", "#565C68", "#0A0A0A"]
_USAGE_DAYS = 14  # show the last two weeks

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

    st.subheader("My records")
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

    # Transient confirmation after a save — keeps the record tab uncluttered
    # instead of stacking a banner above a fresh recorder.
    if st.session_state.pop("note_saved", False):
        st.toast("Note saved.", icon="✅")
    err = st.session_state.pop("_record_error", None)
    if err:
        st.error(err)

    # The recorder and the "transcribing…" status share ONE slot, so the
    # recorder can never render a second time while transcription blocks
    # (which is what made the UI look duplicated).
    slot = st.empty()

    # A queued recording is kept in session_state until it is actually saved,
    # so a long one whose run gets interrupted is retried rather than lost.
    pending = st.session_state.get("_pending_recording")
    if pending is None:
        with slot.container():
            result = recorder.record_button(key="voice_recorder")
        if not result or not result.get("audio"):
            return
        # Ignore reruns that replay the same recording.
        if result.get("id") == st.session_state.get("last_record_id"):
            return
        st.session_state["last_record_id"] = result.get("id")
        st.session_state["_pending_recording"] = result
        pending = result

    with slot.container():
        with st.spinner("Transcribing and anonymizing…"):
            ok, error = _transcribe_and_save(patient, pending)

    # Only clear the queued recording once processing finished (ok or a real
    # error). An interrupted run leaves it in place to retry next time.
    st.session_state.pop("_pending_recording", None)
    if ok:
        st.session_state["note_saved"] = True
    elif error:
        st.session_state["_record_error"] = error
    st.rerun()


def _transcribe_and_save(patient, result):
    """Transcribe, anonymize and store one recording. Returns (ok, error)."""
    try:
        audio_bytes = base64.b64decode(result["audio"])
        duration = float(result.get("duration") or 0)
        suffix = _suffix_for(result.get("mime"))
        transcript = ai.transcribe(audio_bytes, suffix=suffix)
        anonymized = ai.anonymize(transcript)
    except (ai.AIServiceError, ai.AIConfigError) as exc:
        return False, str(exc)
    tokens = audio.count_tokens(transcript)
    repository.add_note_with_usage(
        patient_id=patient["id"],
        anonymized_text=anonymized,
        duration_seconds=duration,
        transcribed_tokens=tokens,
    )
    return True, None


def _history(patient):
    notes = repository.list_notes(patient["id"])
    if not notes:
        st.info("You have no saved notes yet.")
        return
    for note in notes:
        body = html.escape(note["anonymized_text"]).replace("\n", "<br>")
        st.markdown(
            f'<div dir="rtl" style="text-align:right">'
            f'<div style="font-weight:600;color:#5a6072">{_fmt_dt(note["created_at"])}</div>'
            f'<div style="margin-top:4px">{body}</div></div>',
            unsafe_allow_html=True,
        )
        st.divider()


def _heat_color(value, target):
    """Intensity color for a day's tokens relative to the reference target."""
    if value <= 0:
        return _HEAT_COLORS[0]
    if target <= 0:
        return _HEAT_COLORS[4]
    ratio = value / target
    if ratio < 0.25:
        return _HEAT_COLORS[1]
    if ratio < 0.5:
        return _HEAT_COLORS[2]
    if ratio < 1.0:
        return _HEAT_COLORS[3]
    return _HEAT_COLORS[4]


def _usage(patient):
    st.markdown("#### Usage")
    by_day = repository.usage_tokens_by_day(patient["id"])
    today = datetime.date.today()
    target = repository.get_daily_token_target()
    today_stats = repository.usage_today(patient["id"])

    c1, c2, c3 = st.columns(3)
    c1.metric("Notes today", today_stats["notes"])
    c2.metric("Tokens today", f"{today_stats['tokens']:,}")
    c3.metric("Daily target", f"{target:,}")

    if target > 0:
        pct = min(today_stats["tokens"] / target, 1.0)
        st.progress(
            pct,
            text=f"{today_stats['tokens']:,} / {target:,} tokens today · reference only",
        )

    # Vertical two-week activity: one row per day, most recent first. Each bar
    # is filled relative to the daily target, coloured by intensity.
    rows = []
    for offset in range(_USAGE_DAYS):
        day = today - datetime.timedelta(days=offset)
        value = by_day.get(day, 0)
        width = 0 if target <= 0 else min(value / target, 1.0) * 100
        over = target > 0 and value > target
        rows.append(
            '<div class="bm-u-row">'
            f'<div class="bm-u-day">{day.strftime("%a %d %b")}</div>'
            '<div class="bm-u-track">'
            f'<div class="bm-u-fill" style="width:{width:.0f}%;'
            f'background:{_heat_color(value, target)}"></div></div>'
            f'<div class="bm-u-val">{value:,}{" &#9873;" if over else ""}</div>'
            "</div>"
        )
    st.markdown(
        "<style>"
        ".bm-u-row{display:flex;align-items:center;gap:.6rem;padding:.16rem 0;}"
        ".bm-u-day{flex:0 0 84px;font-size:.8rem;color:#6B7280;}"
        ".bm-u-track{flex:1;height:14px;background:#F1F2F5;border-radius:3px;overflow:hidden;}"
        ".bm-u-fill{height:100%;border-radius:3px;}"
        ".bm-u-val{flex:0 0 62px;text-align:right;font-size:.8rem;font-weight:600;color:#1F2333;}"
        "</style>"
        '<div class="bm-u">' + "".join(rows) + "</div>",
        unsafe_allow_html=True,
    )
    st.caption(
        f"Daily tokens over the last {_USAGE_DAYS} days. Bars are relative to the "
        f"{target:,}-token daily target (&#9873; marks days above it)."
    )


def _account(user):
    common.change_password_form(user["id"], must_change=bool(user.get("must_change_password")))
