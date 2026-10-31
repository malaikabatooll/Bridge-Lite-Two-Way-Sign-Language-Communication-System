#  Bridge Lite — Two Way Sign Language Communication System

Communication can become challenging when sign language users interact with people who do not understand sign language. This creates barriers in everyday conversations and can make it difficult to communicate urgent needs.

**Bridge Lite** is a Python-based AI project designed to make communication more accessible through real-time sign recognition and voice assistance.

## 1. Key Features

- **Real-Time Sign Recognition:** Recognizes supported hand gestures through a camera.
- **Sign-to-Text:** Converts recognized signs into readable text.
- **Text-to-Speech:** Converts recognized words into spoken audio.
- **Text-to-Sign Reference:** Displays corresponding sign images for supported words.
- **Emergency Alerts:** Triggers an alert when specified emergency signs are recognized.
- **Confidence Score:** Displays the model's confidence for its predictions.
- **Graphical User Interface:** Provides a visual interface for camera input and translated output.

## 2. How It Works

Bridge Lite combines computer vision, hand-landmark detection, and machine learning to recognize hand gestures.

1. **Camera Input:** The camera captures the user's hand gestures.
2. **Hand Detection:** MediaPipe detects the hand and extracts its landmarks.
3. **Preprocessing:** The extracted landmark coordinates are normalized and prepared as model input.
4. **Gesture Classification:** A custom-trained Random Forest classifier predicts the corresponding sign.
5. **Output Generation:** The recognized word is displayed as text and can be converted into speech.
6. **Emergency Detection:** Specified emergency signs trigger an alert.

## 3. Machine Learning Model

Bridge Lite uses a **Random Forest Classifier** trained on prepared hand-landmark data.

- 21 landmarks per hand.
- 3 coordinates (X, Y, Z) per landmark.
- Supports two-hand landmark input.
- 126 features when both hand landmark sets are included.
- 80/20 training and testing split.

## 4. Technologies Used

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| OpenCV | Camera access and image processing |
| MediaPipe | Hand detection and landmark extraction |
| NumPy | Numerical operations |
| Pandas | Dataset handling |
| Scikit-learn | Machine learning model |
| Joblib | Saving and loading the trained model |
| CustomTkinter | Graphical user interface |
| Pillow | Image processing and display |
| pyttsx3 | Text-to-speech functionality |

## 5. Supported Signs

Bridge Lite currently supports 20 hand gestures.

| No. | Sign | Gesture Description |
|---:|---|---|
| 1 | HELP | Close your hand into a fist by curling all four fingers inward and tucking your thumb beneath them. |
| 2 | HELLO | Raise an open hand with the palm facing forward, keeping all five fingers extended and spread apart. |
| 3 | BYE | Raise an open hand with the palm facing forward, keeping all five fingers extended and held close together. |
| 4 | YES | Form a closed fist with four fingers curled inward while keeping the thumb extended upward. |
| 5 | NO | Form a closed fist with four fingers curled inward while keeping the thumb extended downward. |
| 6 | THANK YOU | Hold an upright, flat hand with all five fingers extended and together, keeping the palm facing toward yourself. |
| 7 | HOSPITAL | Extend the index and middle fingers together while keeping the thumb, ring finger, and little finger curled inward, forming an H-like hand shape. |
| 8 | WATER | Extend the index, middle, and ring fingers together while keeping the thumb and little finger curled inward, forming a W shape. |
| 9 | PAIN | Point the index finger upward while keeping the remaining four fingers curled inward. |
| 10 | STOP | Touch the thumb and index fingertips together to form a circle while extending and spreading the remaining three fingers. |
| 11 | MOTHER | Bring the fingertips of your right hand together and touch them to your chin while slightly tilting your head to the side. |
| 12 | FATHER | Extend the thumb, index finger, and little finger while folding the middle and ring fingers inward. Position the hand near the temple. |
| 13 | THINK | Extend the index finger outward, keep the middle, ring, and little fingers curled inward, and position the hand beside the temple with the thumb extended outward. |
| 14 | SICK | Place your left hand flat against your forehead in a fever-checking gesture, with the back of the hand facing forward. |
| 15 | EAT | Bring the fingertips of all five fingers together and position them in front of the mouth, similar to the MOTHER gesture but near the mouth instead of the chin. |
| 16 | FAMILY | Form closed fists with both hands and bring them together side by side, keeping both forearms vertically aligned beneath the chin. |
| 17 | FRIEND | Hold both hands horizontally facing each other, with the index fingertips touching and the remaining fingers curled into fists. |
| 18 | MORE | Bring the fingertips of all five fingers together on both hands, then face the hands toward each other and touch the joined fingertips together. |
| 19 | SAME | Form a closed fist with both hands, extend the index fingers toward the camera, and bring the hands together so their sides touch. |
| 20 | WORK | Form closed fists with both hands and position the right fist above the left fist in a crossed arrangement. |

## 6. Installation and Setup

### Prerequisites

- Python installed on your computer.
- A working camera.

### Create a Virtual Environment

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run the Application

```bash
python code/main.py
```

**Note:** Ensure that the trained model, MediaPipe hand-landmarker task file, sign images, and other required project assets are present in their expected locations. The emergency sound feature currently uses Windows' built-in `winsound` module.
