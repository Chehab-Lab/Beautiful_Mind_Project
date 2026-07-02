"""Speech-to-text and anonymization.

This is a direct port of the original ``ai`` microservice (``src/stt.py`` and
``src/anonymizer.py``), collapsed into in-process helper functions. Credentials
and model names are read from application secrets (managed by the admin) with a
fallback to environment variables, so no separate service is required.
"""
import hashlib
import json
import os

from bm import repository


class AIConfigError(RuntimeError):
    """Raised when the OpenAI credentials/models have not been configured."""


class AIServiceError(RuntimeError):
    """Raised when a downstream OpenAI call fails."""


def _secret(key, env_default=None):
    return repository.get_secret(key) or os.getenv(key) or env_default


def get_api_key():
    key = _secret("OPENAI_API_KEY")
    if not key:
        raise AIConfigError(
            "OpenAI API key is not configured. Ask an admin to add the "
            "'OPENAI_API_KEY' secret under Application Secrets."
        )
    return key


def _client():
    try:
        from openai import OpenAI
    except ImportError as exc:  # pragma: no cover - dependency guard
        raise AIConfigError("The 'openai' package is not installed.") from exc
    return OpenAI(api_key=get_api_key())


def is_configured() -> bool:
    try:
        get_api_key()
        return True
    except AIConfigError:
        return False


def transcribe(audio_bytes: bytes, suffix: str = ".wav") -> str:
    """Transcribe raw audio bytes to Arabic text using Whisper."""
    import tempfile

    model = _secret("OPENAI_STT_MODEL", "whisper-1")
    client = _client()
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name
        with open(tmp_path, "rb") as fh:
            transcript = client.audio.transcriptions.create(
                model=model, file=fh, language="ar"
            )
        return transcript.text
    except Exception as exc:  # noqa: BLE001 - surface a friendly error
        raise AIServiceError(f"Failed to transcribe audio: {exc}") from exc
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)


def anonymize(text: str) -> str:
    """Replace names of people/places with hashed placeholders (GPT-assisted)."""
    model = _secret("OPENAI_CHAT_MODEL", "gpt-4o-mini")
    client = _client()
    prompt = (
        "You are a helpful assistant that identifies names of people and places "
        "in text for anonymization. Identify all names of people and places in "
        "the text provided below. Return the result ONLY as a JSON object with a "
        "key 'entities' containing a list of objects, each containing 'text' (the "
        "original name) and 'type' for types person and place use the language of "
        "the text. For example if the text is in Arabic return the type in Arabic. "
        'If no entities are found, return {"entities": []}.\n\n'
        "Don't add markdown formatting using ```json or ```"
        f"Text: {text}"
    )
    try:
        response = client.chat.completions.create(
            model=model, messages=[{"role": "user", "content": prompt}]
        )
        content = response.choices[0].message.content
        data = json.loads(content)
        entities = data.get("entities", [])
    except Exception as exc:  # noqa: BLE001
        raise AIServiceError(f"Failed to anonymize text: {exc}") from exc

    anonymized = text
    for entity in entities:
        original = entity["text"]
        entity_type = entity["type"]
        hashed = hashlib.sha256(original.encode()).hexdigest()[:6]
        anonymized = anonymized.replace(original, f"{entity_type} {hashed}")
    return anonymized
