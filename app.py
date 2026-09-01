"""
Niko Persian TTS API

Run locally:
    uvicorn app:app --host 0.0.0.0 --port 8000

Run on ParsPack PaaS:
    uvicorn app:app --host 0.0.0.0 --port $PORT
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import Response
import edge_tts

app = FastAPI(
    title="Niko TTS",
    description="Persian TTS API using Microsoft Edge voice Farid",
    version="1.0.0",
)

DEFAULT_VOICE = "fa-IR-FaridNeural"
DEFAULT_RATE = "-8%"
DEFAULT_PITCH = "-4Hz"


@app.get("/")
def root():
    return {
        "status": "ok",
        "service": "niko-tts",
        "voice": DEFAULT_VOICE,
        "endpoints": ["/health", "/tts"],
    }


@app.get("/health")
def health():
    # این مسیر نباید TTS اجرا کند؛ فقط برای بررسی آماده‌بودن سرویس است.
    return {"status": "ok", "service": "niko-tts"}


@app.get("/tts")
async def tts(
    text: str = Query(
        ...,
        min_length=1,
        max_length=2000,
        description="متنی که باید خوانده شود",
    ),
    voice: str = Query(
        DEFAULT_VOICE,
        description="نام صدای Edge TTS",
    ),
    rate: str = Query(
        DEFAULT_RATE,
        description="سرعت گفتار؛ مانند -8% یا +5%",
    ),
    pitch: str = Query(
        DEFAULT_PITCH,
        description="زیر و بمی صدا؛ مانند -4Hz یا +5Hz",
    ),
):
    text = text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="text نباید خالی باشد")

    # برای اینکه کلاینت نتواند ناخواسته صدای دیگری انتخاب کند،
    # صدای پیش‌فرض و مجاز پروژه را روی فرید نگه می‌داریم.
    if voice != DEFAULT_VOICE:
        voice = DEFAULT_VOICE

    audio_chunks = bytearray()

    try:
        communicate = edge_tts.Communicate(
            text,
            voice,
            rate=rate,
            pitch=pitch,
        )

        async for chunk in communicate.stream():
            if chunk.get("type") == "audio":
                audio_chunks.extend(chunk.get("data", b""))

    except Exception as exc:
        # جزئیات خطا را به کاربر عمومی نشان نمی‌دهیم.
        raise HTTPException(
            status_code=502,
            detail="تولید صدای Edge TTS ناموفق بود",
        ) from exc

    if not audio_chunks:
        raise HTTPException(
            status_code=502,
            detail="فایل صوتی از Edge TTS دریافت نشد",
        )

    return Response(
        content=bytes(audio_chunks),
        media_type="audio/mpeg",
        headers={
            "Cache-Control": "public, max-age=3600",
            "Content-Disposition": "inline; filename=niko-tts.mp3",
        },
    )
