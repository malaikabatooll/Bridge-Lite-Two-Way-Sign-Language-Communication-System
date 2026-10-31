import os
import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

import camera

WORDS = ["mother", "father", "think", "sick", "eat", "family", "friend", "more", "same", "work"]
OUTPUT_DIR = "assets/sign_photos"
os.makedirs(OUTPUT_DIR, exist_ok=True)

HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),
    (0, 5), (5, 6), (6, 7), (7, 8),
    (0, 9), (9, 10), (10, 11), (11, 12),
    (0, 13), (13, 14), (14, 15), (15, 16),
    (0, 17), (17, 18), (18, 19), (19, 20),
    (5, 9), (9, 13), (13, 17)
]

base_options = python.BaseOptions(model_asset_path="hand_landmarker.task")
options = vision.HandLandmarkerOptions(
    base_options=base_options, num_hands=2, running_mode=vision.RunningMode.VIDEO
)
landmarker = vision.HandLandmarker.create_from_options(options)

camera.start_camera()
frame_timestamp = 0
word_idx = 0

print("For each word: hold the sign (both hands if needed), press SPACE to capture.")
print("'n' to skip, 'q' to quit.")

while word_idx < len(WORDS):
    word = WORDS[word_idx]
    frame = camera.read_frame()
    if frame is None:
        continue

    display = frame.copy()
    cv2.putText(display, f"Sign: {word.upper()}  (SPACE=capture, n=skip, q=quit)",
                (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
    cv2.imshow("Capture New Sign Photos", display)

    key = cv2.waitKey(1) & 0xFF

    if key == ord(' '):
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_rgb)
        result = landmarker.detect_for_video(mp_image, frame_timestamp)
        frame_timestamp += 1

        if result.hand_landmarks:
            h, w = frame.shape[:2]
            # loop over EVERY detected hand (1 for face-touching signs, 2 for two-hand signs)
            for hand_landmarks in result.hand_landmarks:
                pts = [(int(lm.x * w), int(lm.y * h)) for lm in hand_landmarks]
                for a, b in HAND_CONNECTIONS:
                    cv2.line(frame, pts[a], pts[b], (198, 229, 41), 3)   # signal cyan, BGR
                for x, y in pts:
                    cv2.circle(frame, (x, y), 6, (244, 245, 242), -1)   # off-white fill
                    cv2.circle(frame, (x, y), 6, (198, 229, 41), 2)     # cyan ring

            out_path = os.path.join(OUTPUT_DIR, f"{word}.png")
            cv2.imwrite(out_path, frame)
            print(f"Saved {out_path} ({len(result.hand_landmarks)} hand(s) detected)")
            word_idx += 1
        else:
            print("No hand detected — try again.")
    elif key == ord('n'):
        print(f"Skipped {word}")
        word_idx += 1
    elif key == ord('q'):
        break

camera.release_camera()
cv2.destroyAllWindows()
print("Done.")
