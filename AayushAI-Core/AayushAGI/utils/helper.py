import os
import json
import pyttsx3
from datetime import datetime
import re

# ========== File Management ==========
def load_json(path):
    """Load JSON file safely, return list or dict based on extension."""
    if not os.path.exists(path):
        return [] if path.endswith(".json") else {}
    with open(path, "r") as f:
        return json.load(f)

def save_json(path, data):
    """Save JSON data safely."""
    with open(path, "w") as f:
        json.dump(data, f, indent=4)

# ========== Keyword Extraction ==========
def extract_keywords(text):
    """Extract meaningful keywords from text by removing stopwords."""
    stopwords = {
        "what", "is", "the", "in", "on", "a", "an", "who", "where",
        "when", "how", "to", "of", "and", "or", "i", "you", "me", "we", "are"
    }
    words = re.findall(r'\b\w+\b', text.lower())
    return list({word for word in words if word not in stopwords})

# ========== Emotion Engine ==========
def update_emotions(text):
    """Detect emotion from keywords (basic simulation)."""
    happy_keywords = ["happy", "great", "excited", "joy", "good"]
    sad_keywords = ["sad", "bad", "depressed", "angry", "tired"]
    text = text.lower()

    for word in happy_keywords:
        if word in text:
            return "😊 Positive"
    for word in sad_keywords:
        if word in text:
            return "😔 Negative"
    return "😐 Neutral"

# ========== Edge Sound Effects (Disabled) ==========
def play_edge_sound(sound_type="start"):
    """Edge sound effects - currently disabled to avoid annoying beeps"""
    # Sounds disabled to prevent annoying beeps
    pass

# ========== Text-to-Speech ==========
def speak(text):
    """Safe text-to-speech function with edge sounds."""
    # TTS Configuration - Set to True to enable actual voice output
    USE_TTS = os.getenv('AAYUSH_TTS_ENABLED', 'False').lower() == 'true'
    USE_EDGE_SOUNDS = os.getenv('AAYUSH_EDGE_SOUNDS', 'True').lower() == 'true'
    
    # You can also enable TTS by setting environment variable:
    # export AAYUSH_TTS_ENABLED=true
    # export AAYUSH_EDGE_SOUNDS=true
    
    if USE_TTS:
        try:
            # Add edge sound - start
            if USE_EDGE_SOUNDS:
                play_edge_sound("start")
            
            # Try system TTS first (more stable than pyttsx3)
            import subprocess
            # Try espeak (lightweight and stable)
            result = subprocess.run(["espeak", "-s", "180", text], 
                                   check=False, capture_output=True, timeout=5)
            
            # Add edge sound - end
            if USE_EDGE_SOUNDS:
                play_edge_sound("end")
            
            if result.returncode == 0:
                return
        except:
            pass
        
        try:
            # Fallback to pyttsx3 with timeout
            import pyttsx3
            import threading
            import time
            
            def tts_worker():
                # Add start sound for pyttsx3 path
                if USE_EDGE_SOUNDS:
                    play_edge_sound("start")
                
                engine = pyttsx3.init()
                engine.setProperty("rate", 180)
                engine.setProperty("volume", 1.0)
                engine.say(text)
                engine.runAndWait()
                engine.stop()
                
                # Add end sound for pyttsx3 path
                if USE_EDGE_SOUNDS:
                    play_edge_sound("end")
            
            # Run TTS in separate thread with timeout
            tts_thread = threading.Thread(target=tts_worker, daemon=True)
            tts_thread.start()
            tts_thread.join(timeout=10)  # 10 second timeout
            
        except Exception as e:
            print(f"[TTS Error] {e}")
    
    # Always print the text as clean visual feedback
    print(f"[🤖 AI]: {text}")

# ========== Time Formatter ==========
def get_current_time():
    """Get the current time as a readable string."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_current_date():
    """Get the current date as a readable string."""
    return datetime.now().strftime("%Y-%m-%d")
