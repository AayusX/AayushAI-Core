import os
import time
import json
import threading
import datetime
import re
from utils.helper import (
    extract_keywords,
    update_emotions,
    load_json,
    save_json,
    speak,
    get_current_time,
    get_current_date,
)
from utils.web_tools import youtube_second_video_url, google_search
from utils.nlp_engine import NLPEngine
from utils.command_processor import CommandProcessor
from utils.advanced_memory import AdvancedMemorySystem
from utils.task_automation import TaskAutomationEngine
from utils.terminal_ui import TerminalUI

# Voice input disabled - Text input only, Voice output enabled
VOICE_INPUT_AVAILABLE = False
print("[📝] Text input mode enabled - Voice responses active")

class AayushAGI:
    def __init__(self):
        # Initialize core components
        self.nlp_engine = NLPEngine()
        self.command_processor = CommandProcessor()
        self.task_engine = TaskAutomationEngine()
        self.memory_system = AdvancedMemorySystem()
        
        # Voice input disabled for this configuration
        # self.voice_recognition = None
        
        # Start system monitoring
        self.task_engine.system_monitor.start_monitoring()
        
        # Initialize data paths
        self.memory_path = "data/brain_memory.json"
        self.reminder_path = "data/brain_reminders.json"
        self.journal_path = "data/brain_journal.json"
        self.profile_path = "data/brain_profile.json"
        
        # Create data directory if it doesn't exist
        os.makedirs("data", exist_ok=True)
        
        # Load data with proper defaults
        self.memory = load_json(self.memory_path)
        if not self.memory or not isinstance(self.memory, dict):
            self.memory = {"conversations": [], "learned_patterns": {}}
        
        # Ensure required keys exist
        if "conversations" not in self.memory:
            self.memory["conversations"] = []
        if "learned_patterns" not in self.memory:
            self.memory["learned_patterns"] = {}
        
        self.reminders = load_json(self.reminder_path) or []
        self.journal = load_json(self.journal_path) or []
        self.profile = load_json(self.profile_path) or {"name": "User", "preferences": {}}
        
        # Voice mode flag
        self.voice_mode = False
        
        print("[🧠] AayushAGI Core initialized successfully!")
    
    def setup_user_profile(self):
        """Complete user profile setup with --Next-option feature"""
        if not self.profile.get("name") or self.profile["name"] == "User":
            speak("Welcome to AayushAGI! Let me get to know you better.")
            
            # Get user's name
            user_name = input("\n💬 What should I call you? ").strip()
            if user_name:
                self.profile["name"] = user_name
                speak(f"Nice to meet you, {user_name}!")
            
            # Get user's profession
            profession = input(f"\n💬 What do you do for work, {user_name}? ").strip()
            if profession:
                self.profile["profession"] = profession
                speak(f"Interesting! So you're involved in {profession}.")
            
            # Ask about interests
            interests = input("\n💬 What are your main interests or hobbies? ").strip()
            if interests:
                self.profile["interests"] = interests
                speak("Great! I'll remember that for our future conversations.")
            
            # Ask about preferred interaction style
            print("\n🎯 How would you like me to interact with you?")
            print("1. Professional and formal")
            print("2. Friendly and casual")
            print("3. Technical and detailed")
            print("4. Creative and inspiring")
            
            style_choice = input("\n💬 Choose (1-4): ").strip()
            style_map = {
                "1": "professional",
                "2": "friendly", 
                "3": "technical",
                "4": "creative"
            }
            
            if style_choice in style_map:
                self.profile["interaction_style"] = style_map[style_choice]
                speak(f"Perfect! I'll adopt a {style_map[style_choice]} approach in our conversations.")
            
            self.save_all_data()
            speak("Your profile is now set up! I'm ready to assist you with personalized responses.")
    
    def get_personalized_greeting(self):
        """Generate personalized greeting based on user profile"""
        name = self.profile.get("name", "there")
        profession = self.profile.get("profession", "")
        style = self.profile.get("interaction_style", "friendly")
        
        import random
        
        if style == "professional":
            greetings = [
                f"Good day, {name}. How may I assist you today?",
                f"Hello {name}, I'm ready to help with your requests.",
                f"Welcome back, {name}. What can I help you accomplish?"
            ]
        elif style == "technical":
            greetings = [
                f"System ready, {name}. Awaiting your command input.",
                f"Hello {name}, all systems operational. How can I process your request?",
                f"Greetings {name}, AayushAGI core is online and ready."
            ]
        elif style == "creative":
            greetings = [
                f"Hey {name}! Ready to create something amazing today?",
                f"Hello creative soul {name}! What inspiring project shall we work on?",
                f"Greetings {name}! Let's bring some innovative ideas to life!"
            ]
        else:  # friendly
            greetings = [
                f"Hey {name}! Great to see you again! How can I help?",
                f"Hi there {name}! What's on your mind today?",
                f"Hello {name}! Ready for another productive conversation?"
            ]
        
        if profession:
            profession_greetings = [
                f"Hope your work in {profession} is going well, {name}!",
                f"How are things in the {profession} world today, {name}?"
            ]
            greetings.extend(profession_greetings)
        
        return random.choice(greetings)

    def save_all_data(self):
        """Save all data to files"""
        save_json(self.memory_path, self.memory)
        save_json(self.reminder_path, self.reminders)
        save_json(self.journal_path, self.journal)
        save_json(self.profile_path, self.profile)
    
    def check_reminders(self):
        """Check and trigger active reminders"""
        now = datetime.datetime.now().astimezone()
        triggered_reminders = []
        
        for reminder in self.reminders[:]:
            try:
                reminder_time = datetime.datetime.fromisoformat(reminder["time"])
                if abs((now - reminder_time).total_seconds()) <= 60:
                    message = f"⏰ Reminder: {reminder['text']}"
                    speak(message)
                    print(f"[🔔 Reminder]: {reminder['text']} at {reminder['time']}")
                    triggered_reminders.append(reminder)
            except Exception as e:
                print(f"[Error] Invalid reminder format: {e}")
                triggered_reminders.append(reminder)  # Remove invalid reminders
        
        # Remove triggered reminders
        for reminder in triggered_reminders:
            if reminder in self.reminders:
                self.reminders.remove(reminder)
        
        if triggered_reminders:
            self.save_all_data()
    
    def handle_reminder(self, command):
        """Handle reminder creation with improved parsing"""
        try:
            import re
            from datetime import timedelta
            
            patterns = [
                r"remind me to (.+) in (\d+) (seconds?|minutes?|hours?|days?)",
                r"set reminder (.+) in (\d+) (seconds?|minutes?|hours?|days?)",
                r"alert me to (.+) in (\d+) (seconds?|minutes?|hours?|days?)"
            ]
            
            for pattern in patterns:
                match = re.search(pattern, command)
                if match:
                    action, amount, unit = match.groups()
                    amount = int(amount)
                    
                    # Handle different time units
                    unit = unit.rstrip('s').lower()  # Remove plural 's'
                    if unit == "second":
                        delta = timedelta(seconds=amount)
                    elif unit == "minute":
                        delta = timedelta(minutes=amount)
                    elif unit == "hour":
                        delta = timedelta(hours=amount)
                    elif unit == "day":
                        delta = timedelta(days=amount)
                    else:
                        raise ValueError(f"Invalid time unit: {unit}")
                    
                    reminder_time = datetime.datetime.now().astimezone() + delta
                    reminder = {
                        "text": action.strip(),
                        "time": reminder_time.isoformat(),
                        "created": datetime.datetime.now().isoformat()
                    }
                    
                    self.reminders.append(reminder)
                    self.save_all_data()
                    
                    formatted_time = reminder_time.strftime('%Y-%m-%d %H:%M')
                    response = f"Reminder set: '{action}' for {formatted_time}"
                    speak(response)
                    print(f"[🧠 Brain AI]: {response}")
                    return True
                    
        except Exception as e:
            speak("Sorry, I couldn't set that reminder. Please check the format.")
            print(f"[Error in reminder setup]: {e}")
        
        return False
    
    def handle_youtube(self, command):
        """Enhanced YouTube handling"""
        patterns = [
            r"play (.+) on youtube",
            r"youtube (.+)",
            r"play youtube (.+)",
            r"search youtube for (.+)"
        ]
        
        query = None
        for pattern in patterns:
            match = re.search(pattern, command)
            if match:
                query = match.group(1).strip()
                break
        
        if query:
            url = youtube_second_video_url(query)
            if url:
                speak(f"Playing '{query}' on YouTube.")
                os.system(f"xdg-open '{url}'")
                return True
            else:
                speak("Sorry, couldn't find that video on YouTube.")
                return True
        
        return False
    
    def handle_journal(self, command):
        """Enhanced journal handling"""
        patterns = [
            r"add journal (.+)",
            r"journal (.+)",
            r"note in journal (.+)",
            r"write in journal (.+)"
        ]
        
        entry_text = None
        for pattern in patterns:
            match = re.search(pattern, command)
            if match:
                entry_text = match.group(1).strip()
                break
        
        if entry_text:
            entry = {
                "date": get_current_date(),
                "time": get_current_time(),
                "entry": entry_text,
                "emotion": update_emotions(entry_text)
            }
            
            self.journal.append(entry)
            self.save_all_data()
            
            speak("Journal entry added successfully.")
            print(f"[📝 Journal]: Entry added - {entry_text[:50]}...")
            return True
        
        return False
    
    def show_enhanced_help(self):
        """Show comprehensive help information"""
        help_text = self.command_processor.get_help_text()
        additional_help = """

🚀 ADVANCED FEATURES:
  - system status (comprehensive system overview)
  - memory stats (AI memory and learning statistics)
  - clean system (automated system cleanup)
  - organize files (smart file organization)
  - network diagnostics (network health check)
  - optimize performance (system optimization)
  - security scan (basic security assessment)
        """
        print(help_text + additional_help)
        speak("I've displayed all available commands. I can help with calculations, system info, web searches, entertainment, and much more!")
    
    def display_system_status(self, sys_overview):
        """Display a detailed system status report"""
        print("\n[⚙️ SYSTEM OVERVIEW]:")
        print(f"CPU Usage: {sys_overview['cpu']['percent']}% (Cores: {sys_overview['cpu']['count']})")
        print(f"Memory Usage: {sys_overview['memory']['percent']}% used")
        print(f"Disk Usage: {sys_overview['disk']['percent']}% used")
        print(f"Network: {sys_overview['network']['bytes_sent']} bytes sent | {sys_overview['network']['bytes_recv']} bytes received")
        print(f"System Boot Time: {sys_overview['boot_time']}")
        print(f"Active Tasks: {sys_overview['active_tasks']} | Queued Tasks: {sys_overview['queued_tasks']}")
        speak("Here is your system overview.")

    def display_memory_stats(self, mem_stats):
        """Display memory stats and insights"""
        print("\n[🧠 MEMORY STATISTICS]:")
        print(f"Short-term memory slots used: {mem_stats['short_term_count']}")
        print(f"Long-term memory entries: {mem_stats['long_term_count']}")
        print(f"Episodic memory events: {mem_stats['episodic_count']}")
        print(f"Semantic memory facts: {mem_stats['semantic_count']}")

        if mem_stats['top_preferences']:
            print("\nTop User Preferences:")
            for item, score in list(mem_stats['top_preferences'].items())[:5]:
                print(f" - {item}: {score:.2f}")

        if mem_stats['most_used_commands']:
            print("\nMost Used Commands:")
            for cmd, freq in list(mem_stats['most_used_commands'].items())[:5]:
                print(f" - {cmd}: {freq} times")

        print("\nNeural Weights:")
        for weight, value in mem_stats['neural_weights'].items():
            print(f" - {weight}: {value:.2f}")
        speak("Memory statistics have been displayed.")
    
    def display_task_result(self, task):
        """Display the result of a task execution"""
        print(f"\n[🔧 TASK RESULT]: {task['type']}")
        print(f"Status: {task['status']}")
        print(f"Started: {task['created_at']}")
        
        if task['status'] == 'completed':
            print(f"Completed: {task['completed_at']}")
            result = task['result']
            
            if 'error' in result:
                print(f"Error: {result['error']}")
                speak(f"Task failed: {result['error']}")
            else:
                # Display specific results based on task type
                if task['type'] == 'system_cleanup':
                    if 'cleaned' in result:
                        print(f"Files cleaned: {len(result['cleaned'])}")
                        if result['errors']:
                            print(f"Errors encountered: {len(result['errors'])}")
                    speak("System cleanup completed successfully.")
                
                elif task['type'] == 'file_organization':
                    if 'organized' in result:
                        print(f"Files organized: {len(result['organized'])}")
                        print(f"Folders created: {len(result['created_folders'])}")
                        for org in result['organized'][:10]:  # Show first 10
                            print(f" - {org}")
                    speak("File organization completed successfully.")
                
                elif task['type'] == 'network_diagnostics':
                    print(f"Internet Status: {result.get('internet_status', 'Unknown')}")
                    if 'ping_avg' in result:
                        print(f"Ping Average: {result['ping_avg']}")
                    speak("Network diagnostics completed.")
                
                elif task['type'] == 'performance_optimization':
                    if 'optimizations' in result:
                        print(f"Optimizations applied: {len(result['optimizations'])}")
                        for opt in result['optimizations']:
                            print(f" - {opt}")
                    if 'warnings' in result and result['warnings']:
                        print("Warnings:")
                        for warning in result['warnings']:
                            print(f" - {warning}")
                    speak("Performance optimization completed.")
                
                elif task['type'] == 'security_scan':
                    print(f"Security checks passed: {len(result.get('checks', []))}")
                    if result.get('warnings'):
                        print(f"Security warnings: {len(result['warnings'])}")
                        for warning in result['warnings'][:3]:  # Show first 3
                            print(f" - {warning}")
                    speak("Security scan completed.")
                
                else:
                    print(f"Result: {result}")
                    speak("Task completed successfully.")
        else:
            print(f"Task failed: {task['result']}")
            speak("Task failed to complete.")
    
    def get_user_input(self):
        """Get input from user (text input only) with enhanced prompt"""
        # Voice input disabled - text input only
        prompt = f"\n{TerminalUI.green('┌─')} {TerminalUI.yellow('💬 You')} {TerminalUI.green('─────────────────────────────────────────────────────')}"
        print(prompt)
        user_input = input(f"{TerminalUI.green('└─▶')} ").strip()
        if user_input:
            print(f"{TerminalUI.blue('   ✓ Processing:')} {TerminalUI.bold(user_input)}")
        return user_input
    
    def process_input(self, user_input):
        """Process user input with enhanced intelligence"""
        if not user_input:
            return True  # Continue loop
        
        # Convert to lowercase for processing
        processed_input = user_input.lower()
        original_input = user_input
        
        # Store in memory with context
        self.memory["conversations"].append({
            "timestamp": get_current_time(),
            "user_input": original_input,
            "processed_input": processed_input
        })
        
        # Limit memory size
        if len(self.memory["conversations"]) > 100:
            self.memory["conversations"] = self.memory["conversations"][-50:]
        
        # Process with NLP engine first
        nlp_result = self.nlp_engine.process_natural_language(processed_input)
        
        # Handle special commands first
        if processed_input in ["exit", "quit", "goodbye", "bye"]:
            speak("Goodbye! It was great talking with you.")
            return False  # Exit loop
        
        elif processed_input in ["help", "commands", "what can you do"]:
            self.show_enhanced_help()
            return True
        
        elif "voice mode" in processed_input or "start voice" in processed_input:
            speak("Voice input is disabled in this configuration. Text input only mode is active with voice responses.")
            print("[📝] Voice input disabled - Using text input with voice responses")
            return True
        
        elif "text mode" in processed_input or "stop voice" in processed_input:
            speak("Already in text input mode with voice responses enabled.")
            print("[📝] Text input mode is active with voice responses")
            return True
        
        elif "system status" in processed_input or "system overview" in processed_input:
            sys_overview = self.task_engine.get_system_overview()
            self.display_system_status(sys_overview)
            return True
        
        elif "memory stats" in processed_input or "memory status" in processed_input:
            mem_stats = self.memory_system.get_memory_stats()
            self.display_memory_stats(mem_stats)
            return True
        
        elif "clean system" in processed_input or "cleanup" in processed_input:
            speak("Starting system cleanup. This may take a moment.")
            result = self.task_engine.execute_task("system_cleanup")
            self.display_task_result(result)
            return True
        
        elif "organize files" in processed_input:
            speak("Organizing your files. Please wait.")
            result = self.task_engine.execute_task("file_organization")
            self.display_task_result(result)
            return True
        
        elif "network diagnostics" in processed_input or "check network" in processed_input:
            speak("Running network diagnostics.")
            result = self.task_engine.execute_task("network_diagnostics")
            self.display_task_result(result)
            return True
        
        elif "optimize performance" in processed_input or "optimize system" in processed_input:
            speak("Optimizing system performance.")
            result = self.task_engine.execute_task("performance_optimization")
            self.display_task_result(result)
            return True
        
        elif "security scan" in processed_input:
            speak("Performing security scan.")
            result = self.task_engine.execute_task("security_scan")
            self.display_task_result(result)
            return True
        
        # Try specialized handlers
        if self.handle_reminder(processed_input):
            return True
        elif self.handle_youtube(processed_input):
            return True
        elif self.handle_journal(processed_input):
            return True
        
        # Try advanced command processor
        command_result = self.command_processor.process_command(processed_input)
        if command_result:
            speak(command_result)
            print(f"[🧠 Brain AI]: {command_result}")
            return True
        
        # Use NLP engine for intelligent response
        if nlp_result and nlp_result.get("response"):
            response = nlp_result["response"]
            speak(response)
            print(f"[🧠 Brain AI]: {response}")
        else:
            # Fallback response
            fallback_responses = [
                "That's interesting! I'm still learning about that topic.",
                "I understand you're asking about that, but I need more context to help better.",
                "I'm constantly expanding my knowledge. Could you rephrase that or ask me something else?",
                "That's beyond my current capabilities, but I'm always improving!"
            ]
            import random
            response = random.choice(fallback_responses)
            speak(response)
            print(f"[🧠 Brain AI]: {response}")
        
        # Save updated memory
        self.save_all_data()
        return True
    
    def run(self):
        """Main AI loop with personalized experience"""
        speak("Welcome to AayushCore AGI - the world's most advanced personal AI assistant!")
        print("\n[🧠 Brain AI]: Welcome to AayushCore AGI!")
        
        # Setup user profile if needed
        self.setup_user_profile()
        
        # Give personalized greeting
        greeting = self.get_personalized_greeting()
        speak(greeting)
        
        print("\nType 'help' for commands, 'voice mode' for hands-free interaction, or 'exit' to quit.\n")
        
        # Start reminder check thread
        reminder_thread = threading.Thread(target=self._reminder_loop, daemon=True)
        reminder_thread.start()
        
        try:
            while True:
                # Check reminders
                self.check_reminders()
                
                # Get user input
                user_input = self.get_user_input()
                
                # Process input
                if not self.process_input(user_input):
                    break  # Exit requested
                    
        except KeyboardInterrupt:
            print("\n[🧠] Shutting down AayushAGI...")
            speak("Goodbye!")
        except Exception as e:
            print(f"[Error] Unexpected error: {e}")
            speak("I encountered an error, but I'm shutting down gracefully.")
        finally:
            self.save_all_data()
            print("[💾] All data saved. AayushAGI shutdown complete.")
    
    def _reminder_loop(self):
        """Background thread for checking reminders"""
        while True:
            time.sleep(30)  # Check every 30 seconds
            self.check_reminders()

# Main function to start the AI
def brain_ai():
    """Initialize and start the enhanced AI brain"""
    agi = AayushAGI()
    agi.run()
