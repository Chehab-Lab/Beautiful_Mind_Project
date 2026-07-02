"""Utilities for measuring recorded audio and counting transcribed tokens."""
import contextlib
import io
import wave


def wav_duration_seconds(audio_bytes: bytes) -> float:
    """Return the duration of a WAV clip in seconds, 0.0 if it can't be read.

    ``st.audio_input`` yields WAV data, so the stdlib ``wave`` module is enough
    and keeps the dependency footprint small.
    """
    try:
        with contextlib.closing(wave.open(io.BytesIO(audio_bytes), "rb")) as wf:
            frames = wf.getnframes()
            rate = wf.getframerate()
            if rate:
                return round(frames / float(rate), 2)
    except (wave.Error, EOFError, OSError):
        pass
    return 0.0


def count_tokens(text: str) -> int:
    """Count transcribed tokens.

    Uses ``tiktoken`` when available for an accurate model-aligned count and
    falls back to a whitespace word count otherwise.
    """
    if not text:
        return 0
    try:
        import tiktoken

        enc = tiktoken.get_encoding("cl100k_base")
        return len(enc.encode(text))
    except Exception:  # noqa: BLE001 - tiktoken optional
        return len(text.split())
