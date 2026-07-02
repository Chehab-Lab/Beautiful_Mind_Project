"""Patient view: record voice notes, review anonymized history, change password."""
import base64
import datetime
import html

import streamlit as st
import streamlit.components.v1 as components

from bm import ai, audio, repository
from bm.ui import common, recorder

# Monochromatic indigo contribution palette (empty -> most).
_HEAT_COLORS = ["#E9EAF2", "#C7C9F4", "#9A9DEC", "#6E6FE4", "#4F46E5"]
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
        body = html.escape(note["anonymized_text"]).replace("\n", "<br>")
        st.markdown(
            f'<div dir="rtl" style="text-align:right">'
            f'<div style="font-weight:600;color:#5a6072">{_fmt_dt(note["created_at"])}</div>'
            f'<div style="margin-top:4px">{body}</div></div>',
            unsafe_allow_html=True,
        )
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
                cells.append('<div class="c e"></div>')
                continue
            value = by_day.get(day, 0)
            color = _HEAT_COLORS[_heat_level(value, max_tokens)]
            cells.append(
                f'<div class="c" style="background:{color}" '
                f'data-d="{day.isoformat()}" data-t="{value}"></div>'
            )
        columns.append(f'<div class="col">{"".join(cells)}</div>')

    legend = "".join(f'<span class="c" style="background:{c}"></span>' for c in _HEAT_COLORS)
    grid = "".join(columns)
    # Rendered in a component iframe so tapping a day works on mobile (no hover).
    doc = f"""<!doctype html><html><head><meta charset="utf-8"><style>
* {{ box-sizing: border-box; }}
body {{ margin: 0; background: transparent; color: #1F2333;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }}
.wrap {{ overflow-x: auto; -webkit-overflow-scrolling: touch; padding: 2px 0; }}
.grid {{ display: flex; gap: 3px; min-width: max-content; }}
.col {{ display: flex; flex-direction: column; gap: 3px; }}
.c {{ width: 15px; height: 15px; border-radius: 3px; background: #E9EAF2; }}
.c.e {{ background: transparent; }}
.grid .c {{ cursor: pointer; }}
.grid .c.sel {{ outline: 2px solid #1F2333; outline-offset: 1px; }}
.readout {{ margin-top: 12px; font-size: 0.92rem; color: #374151; min-height: 1.2em; }}
.readout b {{ color: #1F2333; }}
.legend {{ display: flex; align-items: center; gap: 5px; margin-top: 10px;
    font-size: 0.78rem; color: #6B7280; }}
.legend .c {{ width: 13px; height: 13px; }}
</style></head><body>
<div class="wrap"><div class="grid" id="g">{grid}</div></div>
<div class="readout" id="r">Tap a day to see its tokens.</div>
<div class="legend">Less {legend} More</div>
<script>
var g = document.getElementById('g'), r = document.getElementById('r'), sel = null;
g.addEventListener('click', function (e) {{
  var c = e.target.closest('.c');
  if (!c || !c.dataset.d) return;
  if (sel) sel.classList.remove('sel');
  c.classList.add('sel'); sel = c;
  var t = parseInt(c.dataset.t || '0', 10);
  r.innerHTML = '<b>' + t.toLocaleString() + '</b> token' + (t === 1 ? '' : 's') + ' on ' + c.dataset.d;
}});
</script></body></html>"""
    components.html(doc, height=215)
    st.caption(f"Total transcribed tokens per day over the last {_HEAT_WEEKS} weeks. "
               "Tap a square to see its count.")


def _account(user):
    common.change_password_form(user["id"], must_change=bool(user.get("must_change_password")))
