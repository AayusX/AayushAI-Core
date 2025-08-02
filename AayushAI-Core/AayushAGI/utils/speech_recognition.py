# utils/speech_recognition.py
import speech_recognition as sr
import pyaudio
import wave
import threading
import time
from utils.voice import speak

class VoiceRecognition:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.is_listening = False
        self.wake_words = ["jarvis", "aayush", "hey aayush", "computer"]
        
        # Calibrate for ambient noise
        self.calibrate_microphone()
    
    def calibrate_microphone(self):
        """Calibrate microphone for ambient noise"""
        try:
            with self.microphone as source:
                print("[🎤] Calibrating microphone for ambient noise... Please stay quiet.")
                self.recognizer.adjust_for_ambient_noise(source, duration=2)
                print("[🎤] Microphone calibrated!")
        except Exception as e:
            print(f"[🎤 Error] Microphone calibration failed: {e}")
    
    def listen_for_wake_word(self):
        """Listen continuously for wake words"""
        print("[🎤] Listening for wake words... Say 'Hey Aayush' or 'Jarvis' to activate.")
        
        while True:
            try:
                with self.microphone as source:
                    # Listen for audio with timeout
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=3)
                
                try:
                    # Recognize speech
                    text = self.recognizer.recognize_google(audio).lower()
                    
                    # Check for wake words
                    for wake_word in self.wake_words:
                        if wake_word in text:
                            print(f"[🎤] Wake word detected: '{wake_word}'")
                            speak("Yes, I'm listening. What can I do for you?")
                            return True
                            
                except sr.UnknownValueError:
                    # Speech was unintelligible
                    pass
                except sr.RequestError as e:
                    print(f"[🎤 Error] Could not request results: {e}")
                    
            except sr.WaitTimeoutError:
                # No speech detected within timeout
                pass
            except Exception as e:
                print(f"[🎤 Error] Unexpected error: {e}")
                time.sleep(1)
    
    def listen_for_command(self, timeout=10):
        """Listen for a voice command after wake word"""
        try:
            with self.microphone as source:
                print("[🎤] Listening for your command...")
                speak("I'm listening...")
                
                # Listen for the command
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=10)
                
            # Recognize the command
            command = self.recognizer.recognize_google(audio)
            print(f"[🎤] You said: {command}")
            return command.lower()
            
        except sr.WaitTimeoutError:
            print("[🎤] No command received within timeout.")
            speak("I didn't hear anything. Please try again.")
            return None
        except sr.UnknownValueError:
            print("[🎤] Could not understand the command.")
            speak("I couldn't understand that. Could you please repeat?")
            return None
        except sr.RequestError as e:
            print(f"[🎤 Error] Recognition service error: {e}")
            speak("Sorry, I'm having trouble with speech recognition right now.")
            return None
        except Exception as e:
            print(f"[🎤 Error] Unexpected error: {e}")
            return None
    
    def start_voice_mode(self):
        """Start continuous voice interaction mode"""
        print("[🎤] Voice mode activated! Say 'stop listening' to exit voice mode.")
        speak("Voice mode activated. I'm now listening for your commands.")
        
        while True:
            if self.listen_for_wake_word():
                command = self.listen_for_command()
                
                if command:
                    if any(phrase in command for phrase in ["stop listening", "exit voice mode", "quit voice"]):
                        speak("Voice mode deactivated. Returning to text mode.")
                        print("[🎤] Voice mode deactivated.")
                        break
                    else:
                        yield command  # Return the command to the main brain
    
    def quick_listen(self):
        """Quick one-time listen for a command"""
        try:
            with self.microphone as source:
                print("[🎤] Say something...")
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
            
            command = self.recognizer.recognize_google(audio)
            print(f"[🎤] You said: {command}")
            return command.lower()
            
        except sr.WaitTimeoutError:
            print("[🎤] No speech detected.")
            return None
        except sr.UnknownValueError:
            print("[🎤] Could not understand the speech.")
            return None
        except sr.RequestError as e:
            print(f"[🎤 Error] Recognition service error: {e}")
            return None
        except Exception as e:
            print(f"[🎤 Error] Unexpected error: {e}")
            return None

# Test function
def test_voice_recognition():
    """Test the voice recognition system"""
    vr = VoiceRecognition()
    
    print("Testing voice recognition...")
    print("Say something within 5 seconds:")
    
    result = vr.quick_listen()
    if result:
        print(f"Recognition successful: {result}")
    else:
        print("Recognition failed or no speech detected.")

if __name__ == "__main__":
    test_voice_recognition()
