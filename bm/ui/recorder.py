"""Custom press-to-record voice button (bidirectional Streamlit component).

The frontend (``recorder_component/index.html``) records audio with the browser
MediaRecorder API, animates a central button with the microphone level, and
returns ``{id, audio(base64), mime, duration}`` to Python when recording stops.
"""
import os

import streamlit.components.v1 as components

_DIR = os.path.join(os.path.dirname(__file__), "recorder_component")
_component = components.declare_component("bm_voice_recorder", path=_DIR)


def record_button(key: str = "voice_recorder"):
    """Render the recorder. Returns the latest recording dict, or None."""
    return _component(key=key, default=None)
