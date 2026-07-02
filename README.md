# Beautiful Mind

A privacy-first Streamlit app for recording and reviewing anonymized voice notes.

## Overview
Beautiful Mind is a research application from Chehab Lab at the American University of Beirut. Patients record short voice notes that are automatically transcribed and anonymized before storage, so notes can be reviewed without exposing identities. The app has three roles: doctor, patient, and admin.

## Run
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Configuration
Provide the following as application secrets or environment variables:

- `OPENAI_API_KEY` (required for transcription)
- `OPENAI_CHAT_MODEL` (default `gpt-4o-mini`)
- `OPENAI_STT_MODEL` (default `whisper-1`)

---
© 2026 Chehab Lab.
