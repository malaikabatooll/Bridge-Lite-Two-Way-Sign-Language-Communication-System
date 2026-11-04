# api.py

import threading
from contextlib import asynccontextmanager

import cv2
import numpy as np
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.concurrency import run_in_threadpool

import recognizer
from emergency import is_emergency

ALLOWED_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/webp"}
MAX_UPLOAD_BYTES = 5 * 1024 * 1024  # 5 MB

# TODO before public launch: replace "*" with your Vercel URL,
# e.g. ["https://your-site.vercel.app"]
ALLOWED_ORIGINS = ["*"]

# Only one request may use the shared MediaPipe recognizer at a time.
recognition_lock = threading.Lock()


@asynccontextmanager
async def lifespan(app):
    recognizer.init_recognizer()
    print("Bridge Lite recognition engine ready.")
    yield
    recognizer.close_recognizer()


app = FastAPI(title="Bridge Lite API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {"message": "Bridge Lite API is running", "status": "online"}


@app.get("/health")
def health():
    return {"status": "healthy"}


def _recognize_bytes(image_bytes):
    """Decode and recognize one image. Runs in a worker thread."""
    image_array = np.frombuffer(image_bytes, dtype=np.uint8)
    frame = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    if frame is None:
        return "invalid"

    with recognition_lock:
        return recognizer.recognize_frame(frame)


@app.post("/recognize")
async def recognize(file: UploadFile = File(...)):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=415, detail="Unsupported image format")

    image_bytes = await file.read()

    if not image_bytes:
        raise HTTPException(status_code=400, detail="Empty image")
    if len(image_bytes) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="Image too large")

    try:
        result = await run_in_threadpool(_recognize_bytes, image_bytes)
    except Exception as error:
        print("Recognition error:", error)
        raise HTTPException(status_code=500, detail="Recognition failed")

    if result == "invalid":
        raise HTTPException(status_code=400, detail="Invalid image")

    word, confidence = result
    if not word:
        return {"word": None, "confidence": 0.0, "emergency": False}

    return {
        "word": word,
        "confidence": round(confidence, 2),
        "emergency": is_emergency(word),
    }
