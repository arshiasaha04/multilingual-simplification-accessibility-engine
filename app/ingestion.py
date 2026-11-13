from pathlib import Path

from app.config import get_settings


async def scrape_page(url: str) -> str:
    """Fetch visible page text using a headless Chromium browser."""
    from playwright.async_api import async_playwright

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch()
        try:
            page = await browser.new_page()
            response = await page.goto(url, wait_until="domcontentloaded", timeout=30_000)
            if response is None or not response.ok:
                status = response.status if response is not None else "no response"
                raise RuntimeError(f"Unable to load page ({status}): {url}")
            return await page.locator("body").inner_text()
        finally:
            await browser.close()


def transcribe_audio(audio_path: str | Path, language: str | None = None) -> dict:
    """Transcribe an audio file with OpenAI Whisper."""
    import whisper

    path = Path(audio_path)
    if not path.is_file():
        raise FileNotFoundError(f"Audio file does not exist: {path}")

    model = whisper.load_model(get_settings().whisper_model)
    result = model.transcribe(str(path), language=language, fp16=False)
    return {
        "text": result["text"].strip(),
        "language": result.get("language"),
        "segments": result.get("segments", []),
    }
