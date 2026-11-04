EMERGENCY_WORDS = {
    "help",
    "hospital",
    "pain",
    "sick"
}

def is_emergency(word):
    if not word:
        return False

    return word.lower().strip() in EMERGENCY_WORDS
