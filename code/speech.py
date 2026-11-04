
# speech.py

def init_speech():
    """
    Speech output is handled by the browser,
    not by the Python backend.
    """
    print("Browser-based speech system ready.")


def speak_text(text):
    """
    Speech synthesis is handled by the website
    using the browser's SpeechSynthesis API.

    This function is retained for compatibility
    with the existing Python project.
    """
    if not text:
        return

    print(f"Speech request: {text}")
    print("Send this text to the frontend for speech output.")


def close_speech():
    """
    No Python speech engine needs to be closed.
    """
    print("Speech system closed.")
