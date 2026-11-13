# Multilingual Simplification Accessibility Engine

A starter service for collecting text and audio, measuring readability, and preparing accessible multilingual content. It includes a FastAPI API, a LangGraph simplification/evaluation workflow, Indic-script-aware text metrics, Whisper transcription, Coqui text-to-speech, evaluation charts, and an accessible browser dashboard.

> **Prototype status:** The simplification endpoint is intentionally disabled until a language-model simplifier is connected. The workflow accepts a simplifier callback rather than returning unchanged text as though it had been simplified. Speech models may require substantial downloads and platform-specific setup.

## Features

- Language codes for English and major Indic languages (`GET /api/languages`).
- Playwright page-text ingestion (`POST /api/scrape`).
- Whisper audio transcription (`POST /api/transcribe`).
- Unicode-based Indic character counts, sentence length, and TF-IDF back-translation similarity.
- A LangGraph validation, simplification, evaluation, and self-correction workflow.
- Coqui multilingual speech synthesis and Pandas/Seaborn evaluation reports.
- SQLite telemetry by default and an accessible static dashboard.

## Setup

Use Python 3.10 or 3.11 (the Coqui TTS dependency has narrower Python support). Install dependencies in a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m playwright install chromium
```

Coqui TTS and Whisper have additional system/model requirements. Review their upstream installation guidance for your operating system and available hardware before installing them.

Start the API from the project directory:

```powershell
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/static/index.html` for the dashboard or `http://127.0.0.1:8000/docs` for the API documentation.

## Configuration

Settings can be provided in a `.env` file or as environment variables:

| Variable | Default | Description |
| --- | --- | --- |
| `DATABASE_URL` | `sqlite:///./data/engine.db` | SQLAlchemy database URL |
| `AUDIO_DIR` | `static/audio` | Upload and generated audio directory |
| `PLOTS_DIR` | `static/plots` | Evaluation chart directory |
| `WHISPER_MODEL` | `small` | Whisper model size |
| `TTS_MODEL` | `tts_models/multilingual/multi-dataset/xtts_v2` | Coqui model identifier |
| `MAX_PIPELINE_ATTEMPTS` | `2` | Simplification/self-correction attempts |

## Connecting a simplifier

Provide a callback that calls your selected model and returns simplified text. Its arguments are the source text, language code, and optional evaluation feedback:

```python
from app.pipeline_graph import create_pipeline

def simplify_with_your_model(text: str, language: str, feedback: str | None) -> str:
    # Call an approved model/provider and return its text response.
    ...

pipeline = create_pipeline(simplify_with_your_model)
result = pipeline.invoke({"source_text": "Input text", "language": "hi"})
```

The callback is deliberately injected so model credentials and provider-specific choices are not embedded in this repository. Connect the selected callback to `POST /api/simplify` before enabling that endpoint.

## API examples

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
Invoke-RestMethod http://127.0.0.1:8000/api/languages
```

The transcription endpoint accepts multipart form data with an `audio` file and optional `language` field. The scrape endpoint accepts a URL. Only submit content you are authorized to process; scraped pages and uploads should be handled in accordance with applicable privacy and copyright requirements.

## Privacy and telemetry

Telemetry records operation type, language, and limited error detail; it does not store submitted text by default. Audio uploads are written temporarily to the configured audio directory and removed after transcription. Configure access controls, retention, network restrictions, and model-data handling before deploying with real user content.
