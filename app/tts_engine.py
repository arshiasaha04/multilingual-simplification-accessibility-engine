from pathlib import Path
from uuid import uuid4

from app.config import get_settings


def synthesize_speech(text: str, language: str, speaker_wav: str | Path | None = None) -> Path:
    """Generate an audio file with a Coqui multilingual voice model."""
    if not text.strip():
        raise ValueError("text must not be empty")

    from TTS.api import TTS

    settings = get_settings()
    output_dir = Path(settings.audio_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{uuid4().hex}.wav"
    engine = TTS(settings.tts_model)
    engine.tts_to_file(
        text=text,
        language=language,
        speaker_wav=str(speaker_wav) if speaker_wav else None,
        file_path=str(output_path),
    )
    return output_path
