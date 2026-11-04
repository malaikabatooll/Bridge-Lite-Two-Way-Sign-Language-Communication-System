
import cv2
import numpy as np
import threading

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

import recognizer

app = FastAPI(title="Bridge Lite API")

# Temporary CORS configuration.
# Restrict this to your Vercel domain before public launch.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prevent simultaneous requests from interfering
# with the shared MediaPipe recognizer and timestamps.
recognition_lock = threading.Lock()


@app.on_event("startup")
def startup():
    recognizer.init_recognizer()
    print("Bridge Lite recognition engine ready.")


@app.on_event("shutdown")
def shutdown():
    recognizer.close_recognizer()


@app.get("/")
def home():
    return {
        "message": "Bridge Lite API is running",
        "status": "online"
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/recognize")
async def recognize(file: UploadFile = File(...)):

    if file.content_type not in [
        "image/jpeg",
        "image/png",
        "image/webp"
    ]:
        raise HTTPException(
            status_code=415,
            detail="Unsupported image format"
        )

    try:
        image_bytes = await file.read()

        if not image_bytes:
            raise HTTPException(
                status_code=400,
                detail="Empty image"
            )

        # Decode the uploaded image into an OpenCV frame.
        image_array = np.frombuffer(
            image_bytes,
            dtype=np.uint8
        )

        frame = cv2.imdecode(
            image_array,
            cv2.IMREAD_COLOR
        )

        if frame is None:
            raise HTTPException(
                status_code=400,
                detail="Invalid image"
            )

        # Process one frame using the existing recognizer.
        with recognition_lock:
            word, confidence = recognizer.recognize_frame(frame)

        if not word:
            return {
                "word": None,
                "confidence": 0.0,
                "emergency": False
            }

        return {
            "word": str(word),
            "confidence": round(float(confidence), 2),
            "emergency": str(word).lower() in {
                "help", "hospital", "pain", "stop"
            }
        }

    except HTTPException:
        raise

    except Exception as error:
        print("Recognition error:", error)

        raise HTTPException(
            status_code=500,
            detail="Recognition failed"
        )
