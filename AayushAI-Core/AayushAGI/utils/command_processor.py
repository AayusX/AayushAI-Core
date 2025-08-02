# utils/command_processor.py
import os
import re
import subprocess
import json
import requests
from datetime import datetime, timedelta
import webbrowser
import random
from utils.helper import speak, save_json, load_json

class CommandProcessor:
    def __init__(self):
        self.load_command_patterns()
        self.system_commands = {
            "linux": {
                "open_file_manager": "nautilus",
                "open_terminal": "gnome-terminal",
                "system_info": "neofetch",
                "process_list": "ps aux",
                "disk_usage": "df -h",
                "memory_usage": "free -h"
            }
        }
    
    def load_command_patterns(self):
        """Load command patterns for better recognition"""
        self.patterns = {
            "calculator": [
                r"calculate (.+)",
                r"compute (.+)",
                r"solve (.+)",
                r"what is (.+)",
                r"math (.+)"
            ],
            "system_info": [
                r"system info",
                r"computer info",
                r"specs",
                r"hardware info"
            ],
            "file_operations": [
                r"open (.+)",
                r"create file (.+)",
                r"delete file (.+)",
                r"list files",
                r"show directory"
            ],
            "web_search": [
                r"search for (.+)",
                r"google (.+)",
                r"look up (.+)",
                r"find information about (.+)"
            ],
            "entertainment": [
                r"play music",
                r"play (.+) on youtube",
                r"open youtube",
                r"random joke",
                r"tell me a joke"
            ],
            "productivity": [
                r"take note (.+)",
                r"create reminder (.+)",
                r"set timer for (\d+) (minutes|seconds|hours)",
                r"what's my schedule",
                r"add to calendar (.+)"
            ],
            "weather": [
                r"weather",
                r"temperature",
                r"forecast",
                r"weather in (.+)"
            ]
        }
    
    def calculate_expression(self, expression):
        """Safely calculate mathematical expressions"""
        try:
            # Clean the expression
            expression = expression.lower()
            expression = expression.replace("plus", "+").replace("minus", "-")
            expression = expression.replace("times", "*").replace("multiply", "*")
            expression = expression.replace("divided by", "/").replace("divide", "/")
            
            # Remove non-mathematical characters except basic operators
            safe_expr = re.sub(r'[^0-9+\-*/().\s]', '', expression)
            
            if safe_expr.strip():
                result = eval(safe_expr)
                return f"The result is: {result}"
            else:
                return "I couldn't understand the mathematical expression."
        except Exception as e:
            return "Sorry, I couldn't calculate that expression."
    
    def get_system_info(self):
        """Get system information"""
        try:
            result = subprocess.run(["neofetch", "--stdout"], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                return result.stdout
            else:
                # Fallback system info
                import platform
                info = f"""
System Information:
- OS: {platform.system()} {platform.release()}
- Machine: {platform.machine()}
- Processor: {platform.processor()}
- Python Version: {platform.python_version()}
                """
                return info.strip()
        except subprocess.TimeoutExpired:
            return "System information request timed out."
        except Exception as e:
            return f"Could not retrieve system information: {str(e)}"
    
    def handle_file_operations(self, command, filename=None):
        """Handle file operations"""
        try:
            if "open" in command and filename:
                # Try to open the file with default application
                if os.path.exists(filename):
                    subprocess.run(["xdg-open", filename])
                    return f"Opening {filename}"
                else:
                    return f"File {filename} not found."
            
            elif "list files" in command or "show directory" in command:
                files = os.listdir(".")
                file_list = "\\n".join(files[:20])  # Limit to first 20 files
                return f"Files in current directory:\\n{file_list}"
            
            elif "create file" in command and filename:
                with open(filename, 'w') as f:
                    f.write(f"# Created by AayushAGI on {datetime.now()}\\n")
                return f"Created file: {filename}"
            
            else:
                return "File operation not recognized or filename missing."
                
        except Exception as e:
            return f"Error with file operation: {str(e)}"
    
    def get_random_joke(self):
        """Get a random joke"""
        jokes = [
            "Why don't scientists trust atoms? Because they make up everything!",
            "Why did the scarecrow win an award? He was outstanding in his field!",
            "Why don't eggs tell jokes? They'd crack each other up!",
            "What do you call a fake noodle? An impasta!",
            "Why did the math book look so sad? Because it had too many problems!",
            "What do you call a bear with no teeth? A gummy bear!",
            "Why don't programmers like nature? It has too many bugs!",
            "What's a computer's favorite snack? Microchips!"
        ]
        return random.choice(jokes)
    
    def get_weather_info(self, location=""):
        """Get weather information (placeholder - would need API key)"""
        if not location:
            return "I'd love to help with weather information! However, I need an API key to access real-time weather data. You can ask me to search for weather information instead."
        else:
            return f"I'd show you the weather for {location}, but I need proper API access for real-time data."
    
    def process_productivity_command(self, command):
        """Handle productivity-related commands"""
        if "take note" in command:
            match = re.search(r"take note (.+)", command)
            if match:
                note = match.group(1)
                notes_file = "data/notes.json"
                notes = load_json(notes_file) or []
                notes.append({
                    "timestamp": datetime.now().isoformat(),
                    "note": note
                })
                save_json(notes_file, notes)
                return f"Note saved: {note}"
        
        elif "set timer" in command:
            match = re.search(r"set timer for (\\d+) (minutes|seconds|hours)", command)
            if match:
                amount, unit = match.groups()
                return f"Timer functionality would be implemented here for {amount} {unit}"
        
        return "Productivity command not fully implemented yet."
    
    def process_command(self, command):
        """Main command processing function"""
        command = command.lower().strip()
        
        # Check each pattern category
        for category, patterns in self.patterns.items():
            for pattern in patterns:
                match = re.search(pattern, command)
                if match:
                    if category == "calculator":
                        expression = match.group(1) if match.groups() else command
                        return self.calculate_expression(expression)
                    
                    elif category == "system_info":
                        return self.get_system_info()
                    
                    elif category == "file_operations":
                        filename = match.group(1) if match.groups() else None
                        return self.handle_file_operations(command, filename)
                    
                    elif category == "web_search":
                        query = match.group(1) if match.groups() else command.replace("search", "").strip()
                        if query:
                            search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
                            webbrowser.open(search_url)
                            return f"Searching for: {query}"
                        return "What would you like to search for?"
                    
                    elif category == "entertainment":
                        if "joke" in command:
                            return self.get_random_joke()
                        elif "youtube" in command:
                            if match.groups():
                                query = match.group(1)
                                search_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
                                webbrowser.open(search_url)
                                return f"Searching YouTube for: {query}"
                            else:
                                webbrowser.open("https://www.youtube.com")
                                return "Opening YouTube"
                        elif "music" in command:
                            webbrowser.open("https://www.youtube.com/results?search_query=music")
                            return "Opening music on YouTube"
                    
                    elif category == "productivity":
                        return self.process_productivity_command(command)
                    
                    elif category == "weather":
                        location = match.group(1) if match.groups() else ""
                        return self.get_weather_info(location)
        
        # If no pattern matches, return None to let other handlers try
        return None
    
    def get_help_text(self):
        """Get comprehensive help text"""
        help_text = """
🤖 AayushAGI - Available Commands:

📊 CALCULATIONS:
  - calculate 2+2*5
  - what is 15% of 200
  - solve 10*5+3

💻 SYSTEM:
  - system info
  - computer specs
  - list files
  - open filename.txt

🔍 SEARCH & WEB:
  - search for artificial intelligence
  - google latest news
  - play music on youtube
  - open youtube

😄 ENTERTAINMENT:
  - tell me a joke
  - random joke
  - play [song name] on youtube

📝 PRODUCTIVITY:
  - take note remember to buy milk
  - set timer for 5 minutes
  - remind me to call mom in 2 hours

🌤️ WEATHER:
  - weather (for local weather)
  - weather in New York

🎵 VOICE COMMANDS:
  - Say "start voice mode" for hands-free interaction
  - Say "Hey Aayush" or "Jarvis" to activate voice commands
        """
        return help_text
