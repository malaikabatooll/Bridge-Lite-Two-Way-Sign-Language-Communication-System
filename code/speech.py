import pyttsx3

def init_speech():
    print("Speech engine ready.")

def speak_text(text):
    engine = pyttsx3.init()   # fresh engine instance every time — avoids the "only speaks once" bug
    engine.say(text)
    engine.runAndWait()
    engine.stop()

def close_speech():
    print("Speech engine closed.")
