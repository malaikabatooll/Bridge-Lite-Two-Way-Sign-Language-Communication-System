
# emergency.py

# Words that should trigger an emergency alert.
EMERGENCY_WORDS = {
    "help",
    "hospital",
    "pain",
    "sick"
}


def is_emergency(word):
    """
    Check whether a recognized word is an emergency word.

    Returns:
        bool: True if the word is an emergency word,
              otherwise False.
    """

    if not word:
        return False

    normalized_word = str(word).lower().strip()

    return normalized_word in EMERGENCY_WORDS
