"""
سرور کوچک TTS برای نیکو — با استفاده از صداهای رایگان Microsoft Edge
(کتابخونه‌ی متن‌باز edge-tts)

نصب:
    pip install edge-tts fastapi uvicorn

اجرا:
    uvicorn server:app --host 0.0.0.0 --port 8000

بعد از اجرا، از روی گوشیت (وقتی به همون وای‌فای وصله) می‌تونی تستش کنی:
    http://<آی‌پی-محلی-پی‌سی>:8000/tts?text=سلام

صداهای فارسی موجود:
    fa-IR-FaridNeural   (مرد)
    fa-IR-DilaraNeural  (زن)

تنظیمات صمیمی‌تر (پیش‌فرض): سرعت کمی کندتر و زیر و بمی کمی بم‌تر
از حالت عادی صدا، که معمولاً گرم‌تر و کمتر رسمی شنیده می‌شه.
اگه دوست نداشتی، مقادیر DEFAULT_RATE و DEFAULT_PITCH پایین رو
دستکاری کن یا موقع درخواست با پارامتر rate/pitch عوضش کن.
"""

from fastapi import FastAPI, Query
from fastapi.responses import Response
import edge_tts

app = FastAPI()

# صدای کمی کندتر و بم‌تر از حالت عادی = صمیمی‌تر
# فرمت rate/pitch باید با علامت + یا - شروع بشه
DEFAULT_RATE = "-8%"
DEFAULT_PITCH = "-4Hz"


@app.get("/tts")
async def tts(
    text: str = Query(..., description="متنی که باید خونده بشه"),
    voice: str = Query("fa-IR-FaridNeural", description="اسم صدا"),
    rate: str = Query(DEFAULT_RATE, description="سرعت گفتار، مثلاً -10% یا +5%"),
    pitch: str = Query(DEFAULT_PITCH, description="زیر و بمی صدا، مثلاً -5Hz یا +10Hz")
):
    communicate = edge_tts.Communicate(
        text,
        voice,
        rate=rate,
        pitch=pitch
    )

    audio_chunks = bytearray()

    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_chunks.extend(chunk["data"])

    return Response(
        content=bytes(audio_chunks),
        media_type="audio/mpeg"
    )


@app.get("/")
async def health_check():
    return {"status": "نیکو TTS سرور در حال اجراست ✅"}

