import winsound

EMERGENCY_WORDS = {"help", "hospital", "pain", "sick"}

def is_emergency(word):
    return word in EMERGENCY_WORDS

def play_alarm():
    # Three sharp beeps — deliberately harsher/more urgent than the calm spoken voice
    for _ in range(3):
        winsound.Beep(1000, 200)   # 1000 Hz tone, 200 ms each
