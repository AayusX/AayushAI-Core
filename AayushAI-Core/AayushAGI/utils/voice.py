# utils/voice.py
import pyttsx3
import os
import platform
import subprocess

engine = pyttsx3.init()
engine.setProperty('rate', 170)
engine.setProperty('volume', 1.0)

def speak(text):
    print(f"\n[🧠 Brain AI]: {text}")
    engine.say(text)
    engine.runAndWait()

def play_reminder_sound():
    sound_path = os.path.join("assets", "reminder_sound.mp3")
    if os.path.exists(sound_path):
        if platform.system() == "Windows":
            import winsound
            winsound.PlaySound(sound_path, winsound.SND_FILENAME)
        elif platform.system() == "Darwin":  # macOS
            subprocess.call(["afplay", sound_path])
        else:  # Linux
            subprocess.call(["mpg123", sound_path])
    else:
        print("[!] Reminder sound file missing.")
