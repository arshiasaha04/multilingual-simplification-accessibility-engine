from contextlib import asynccontextmanager
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, HttpUrl
from playwright.async_api import Error as PlaywrightError

from app.config import SUPPORTED_LANGUAGES, get_settings
from app.database import init_db, log_event
from app.ingestion import scrape_page, transcribe_audio
from app.pipeline_graph import create_pipeline


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title=get_settings().app_name, lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")


class SimplifyRequest(BaseModel):
    text: str
    language: str


class ScrapeRequest(BaseModel):
    url: HttpUrl


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/languages")
def languages() -> dict[str, str]:
    return SUPPORTED_LANGUAGES


@app.post("/api/simplify")
def simplify(request: SimplifyRequest) -> dict:
    if request.language not in SUPPORTED_LANGUAGES:
        raise HTTPException(status_code=422, detail="Unsupported language code")
    log_event("simplify_requested", request.language)
    raise HTTPException(
        status_code=503,
        detail=(
            "No language-model simplifier is configured. Integrate a model with "
            "app.pipeline_graph.create_pipeline before enabling this endpoint."
        ),
    )


@app.post("/api/scrape")
async def scrape(request: ScrapeRequest) -> dict[str, str]:
    try:
        text = await scrape_page(str(request.url))
    except (PlaywrightError, RuntimeError) as exc:
        log_event("scrape_failed", details=type(exc).__name__)
        raise HTTPException(status_code=502, detail=f"Page ingestion failed: {exc}") from exc
    log_event("page_scraped")
    return {"text": text}


@app.post("/api/transcribe")
async def transcribe(audio: UploadFile = File(...), language: str | None = None) -> dict:
    settings = get_settings()
    audio_dir = Path(settings.audio_dir)
    audio_dir.mkdir(parents=True, exist_ok=True)
    suffix = Path(audio.filename or "").suffix.lower()
    if suffix not in {".aac", ".flac", ".m4a", ".mp3", ".mp4", ".mpeg", ".ogg", ".wav", ".webm"}:
        raise HTTPException(status_code=415, detail="Unsupported audio file type")
    path = audio_dir / f"upload-{uuid4().hex}{suffix}"
    try:
        path.write_bytes(await audio.read())
        result = transcribe_audio(path, language)
    except (OSError, RuntimeError, FileNotFoundError) as exc:
        log_event("transcription_failed", language, type(exc).__name__)
        raise HTTPException(status_code=500, detail=f"Audio transcription failed: {exc}") from exc
    finally:
        path.unlink(missing_ok=True)
    log_event("audio_transcribed", result.get("language"))
    return result
