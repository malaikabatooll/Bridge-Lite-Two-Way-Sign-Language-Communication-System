# recognizer.py

import os
import cv2
import numpy as np
import joblib
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HAND_MODEL_PATH = os.path.join(BASE_DIR, "hand_landmarker.task")
CLASSIFIER_PATH = os.path.join(BASE_DIR, "models", "word_classifier.pkl")

landmarker = None
model = None


def init_recognizer():
    global landmarker, model

    base_options = python.BaseOptions(model_asset_path=HAND_MODEL_PATH)
    options = vision.HandLandmarkerOptions(
        base_options=base_options,
        num_hands=2,
        running_mode=vision.RunningMode.IMAGE,
    )
    landmarker = vision.HandLandmarker.create_from_options(options)
    model = joblib.load(CLASSIFIER_PATH)
    print("Recognizer initialized (IMAGE mode, two-hand).")


def normalize_landmarks(hand_landmarks):
    """One hand's 21 points -> 63 normalized numbers."""
    wrist = hand_landmarks[0]
    ref = hand_landmarks[9]
    scale = ((ref.x - wrist.x) ** 2 + (ref.y - wrist.y) ** 2) ** 0.5
    if scale == 0:
        scale = 1e-6

    features = []
    for lm in hand_landmarks:
        features.append((lm.x - wrist.x) / scale)
        features.append((lm.y - wrist.y) / scale)
        features.append((lm.z - wrist.z) / scale)
    return features


def build_feature_vector(hands_landmarks):
    """
    Turn 0, 1, or 2 detected hands into a consistent 126-number vector.
    Two hands are ordered left-to-right by x-position in the frame.
    """
    if len(hands_landmarks) == 0:
        return [0.0] * 126
    if len(hands_landmarks) == 1:
        return normalize_landmarks(hands_landmarks[0]) + [0.0] * 63

    sorted_hands = sorted(hands_landmarks[:2], key=lambda h: h[0].x)
    return normalize_landmarks(sorted_hands[0]) + normalize_landmarks(sorted_hands[1])


def recognize_frame(frame):
    """
    Recognize one BGR frame (OpenCV format).
    Returns (word, confidence_percent) or (None, 0.0) if no hand is found.
    """
    if landmarker is None or model is None:
        raise RuntimeError("Recognizer is not initialized. Call init_recognizer() first.")

    img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_rgb)
    result = landmarker.detect(mp_image)

    if not result.hand_landmarks:
        return None, 0.0

    features = build_feature_vector(result.hand_landmarks)
    probs = model.predict_proba([features])[0]
    best_idx = int(np.argmax(probs))

    word = str(model.classes_[best_idx])
    confidence = float(probs[best_idx]) * 100
    return word, confidence


def close_recognizer():
    global landmarker
    if landmarker is not None:
        landmarker.close()
        landmarker = None
    print("Recognizer closed.")


# Desktop test loop. Requires camera.py in the same folder.
if __name__ == "__main__":
    import camera

    camera.start_camera()
    init_recognizer()

    while True:
        frame = camera.read_frame()
        if frame is None:
            break

        word, confidence = recognize_frame(frame)
        if word:
            text = f"{word.upper()} ({confidence:.1f}%)"
        else:
            text = "No hand detected"

        cv2.putText(frame, text, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        cv2.imshow("Recognizer Test", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    camera.release_camera()
    close_recognizer()
    cv2.destroyAllWindows()
