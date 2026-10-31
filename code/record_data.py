import cv2
import csv
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

import camera

WORDS = ["mother", "father", "think", "sick", "eat", "family", "friend", "more", "same", "work"]
SAMPLES_PER_WORD = 200
OUTPUT_FILE = "models/new_words_data.csv"   # separate file, kept apart from training_data.csv on purpose

base_options = python.BaseOptions(model_asset_path="hand_landmarker.task")
options = vision.HandLandmarkerOptions(
    base_options=base_options,
    num_hands=2,
    running_mode=vision.RunningMode.VIDEO
)
landmarker = vision.HandLandmarker.create_from_options(options)


def normalize_landmarks(hand_landmarks):
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
    if len(hands_landmarks) == 0:
        return None
    elif len(hands_landmarks) == 1:
        return normalize_landmarks(hands_landmarks[0]) + [0.0] * 63
    else:
        sorted_hands = sorted(hands_landmarks[:2], key=lambda h: h[0].x)
        return normalize_landmarks(sorted_hands[0]) + normalize_landmarks(sorted_hands[1])


camera.start_camera()
frame_timestamp = 0

with open(OUTPUT_FILE, "w", newline="") as f:
    writer = csv.writer(f)
    header = ["label"]
    for i in range(21):
        header += [f"h1_x{i}", f"h1_y{i}", f"h1_z{i}"]
    for i in range(21):
        header += [f"h2_x{i}", f"h2_y{i}", f"h2_z{i}"]
    writer.writerow(header)

    for word in WORDS:
        while True:
            frame = camera.read_frame()
            if frame is None:
                continue
            display = frame.copy()
            cv2.putText(display, f"Ready? Sign: {word.upper()}  (SPACE=start, q=quit)",
                        (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            cv2.imshow("Recording", display)
            key = cv2.waitKey(1) & 0xFF
            if key == ord(' '):
                break
            if key == ord('q'):
                camera.release_camera(); cv2.destroyAllWindows(); exit()

        collected = 0
        while collected < SAMPLES_PER_WORD:
            frame = camera.read_frame()
            if frame is None:
                continue

            img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_rgb)
            result = landmarker.detect_for_video(mp_image, frame_timestamp)
            frame_timestamp += 1

            display = frame.copy()
            if result.hand_landmarks:
                features = build_feature_vector(result.hand_landmarks)
                if features is not None:
                    writer.writerow([word] + features)
                    collected += 1
                for hand_landmarks in result.hand_landmarks:
                    for lm in hand_landmarks:
                        x, y = int(lm.x * frame.shape[1]), int(lm.y * frame.shape[0])
                        cv2.circle(display, (x, y), 4, (0, 255, 0), -1)

            cv2.putText(display, f"{word.upper()}: {collected}/{SAMPLES_PER_WORD}",
                        (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.imshow("Recording", display)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                camera.release_camera(); cv2.destroyAllWindows(); exit()

        print(f"Done: {word} ({collected} samples)")

camera.release_camera()
cv2.destroyAllWindows()
print(f"\nAll done! Saved to {OUTPUT_FILE}")
