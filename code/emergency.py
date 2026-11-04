# emergency.py

# Keep in sync with the website's Emergency-flagged signs.
EMERGENCY_WORDS = {
    "help",
    "hospital",
    "pain"
    "sick",
}


def is_emergency(word):
    """
    Return True if the recognized word is an emergency word.
    """
    if not word:
        return False

    return str(word).lower().strip() in EMERGENCY_WORDS
