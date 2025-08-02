# gui_main.py - Advanced GUI for AayushAGI
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import queue
import time
import json
import os
from datetime import datetime
import sys

# Import our AI components
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import brain and utils
try:
    from brain import AayushAGI
    from utils.helper import speak
    from utils.encryption import verify_password, set_password
except ImportError as e:
    print(f"Import error: {e}")
    AayushAGI = None

class ModernAayushAGI:
    def __init__(self, root):
        self.root = root
        self.setup_window()
        self.setup_variables()
        self.setup_styles()
        self.create_widgets()
        self.setup_ai()
        self.start_background_tasks()
        
    def setup_window(self):
        """Configure the main window"""
        self.root.title("🤖 AayushAGI - The World's Most Advanced Personal AI Assistant")
        self.root.geometry("1200x800")
        self.root.minsize(900, 600)
        
        # Set window icon (if available)
        try:
            self.root.iconbitmap("assets/icon.ico")
        except:
            pass
            
        # Configure grid weights for responsive design
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Set color scheme
        self.colors = {
            'bg_primary': '#1e1e1e',
            'bg_secondary': '#2d2d2d',
            'bg_tertiary': '#3d3d3d',
            'accent': '#00d4ff',
            'text_primary': '#ffffff',
            'text_secondary': '#cccccc',
            'success': '#4caf50',
            'warning': '#ff9800',
            'error': '#f44336'
        }
        
        self.root.configure(bg=self.colors['bg_primary'])
    
    def setup_variables(self):
        """Initialize variables"""
        self.ai_instance = None
        self.voice_mode = tk.BooleanVar(value=False)
        self.auto_scroll = tk.BooleanVar(value=True)
        self.message_queue = queue.Queue()
        self.is_processing = False
        
    def setup_styles(self):
        """Configure ttk styles"""
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configure styles for dark theme
        self.style.configure('Modern.TFrame', background=self.colors['bg_secondary'])
        self.style.configure('Sidebar.TFrame', background=self.colors['bg_tertiary'])
        self.style.configure('Modern.TLabel', background=self.colors['bg_secondary'], 
                           foreground=self.colors['text_primary'], font=('Segoe UI', 10))
        self.style.configure('Title.TLabel', background=self.colors['bg_secondary'], 
                           foreground=self.colors['accent'], font=('Segoe UI', 14, 'bold'))
        self.style.configure('Modern.TButton', font=('Segoe UI', 10))
        self.style.configure('Accent.TButton', font=('Segoe UI', 10, 'bold'))
        
    def create_widgets(self):
        """Create and arrange all GUI widgets"""
        # Main container
        main_frame = ttk.Frame(self.root, style='Modern.TFrame')
        main_frame.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
        
        # Header
        self.create_header(main_frame)
        
        # Sidebar
        self.create_sidebar(main_frame)
        
        # Main content area
        self.create_main_content(main_frame)
        
        # Status bar
        self.create_status_bar(main_frame)
        
    def create_header(self, parent):
        """Create the header section"""
        header_frame = ttk.Frame(parent, style='Modern.TFrame', padding=10)
        header_frame.grid(row=0, column=0, columnspan=2, sticky='ew')
        
        # Title
        title_label = ttk.Label(header_frame, text="🤖 AayushAGI", style='Title.TLabel')
        title_label.grid(row=0, column=0, sticky='w')
        
        subtitle_label = ttk.Label(header_frame, text="The World's Most Advanced Personal AI Assistant", 
                                 style='Modern.TLabel')
        subtitle_label.grid(row=1, column=0, sticky='w')
        
        # Voice mode toggle
        voice_frame = ttk.Frame(header_frame, style='Modern.TFrame')
        voice_frame.grid(row=0, column=1, sticky='e')
        
        ttk.Label(voice_frame, text="Voice Mode:", style='Modern.TLabel').pack(side='left', padx=(0, 5))
        
        self.voice_toggle = ttk.Checkbutton(voice_frame, text="🎤", variable=self.voice_mode,
                                          command=self.toggle_voice_mode)
        self.voice_toggle.pack(side='left')
        
    def create_sidebar(self, parent):
        """Create the sidebar with quick actions"""
        sidebar_frame = ttk.Frame(parent, style='Sidebar.TFrame', padding=10)
        sidebar_frame.grid(row=1, column=0, sticky='nsew', padx=(0, 5))
        
        # Quick Actions
        ttk.Label(sidebar_frame, text="⚡ Quick Actions", style='Title.TLabel').pack(pady=(0, 10))
        
        quick_actions = [
            ("📊 System Status", self.show_system_status),
            ("🧠 Memory Stats", self.show_memory_stats),
            ("🧹 Clean System", self.clean_system),
            ("📁 Organize Files", self.organize_files),
            ("🔒 Security Scan", self.security_scan),
            ("🌐 Network Check", self.network_check),
            ("⚡ Optimize System", self.optimize_system),
        ]
        
        for text, command in quick_actions:
            btn = ttk.Button(sidebar_frame, text=text, command=command, 
                           style='Modern.TButton', width=20)
            btn.pack(pady=2, fill='x')
        
        # Separator
        ttk.Separator(sidebar_frame, orient='horizontal').pack(fill='x', pady=10)
        
        # System Info
        ttk.Label(sidebar_frame, text="💻 System Info", style='Title.TLabel').pack(pady=(0, 10))
        
        self.system_info_frame = ttk.Frame(sidebar_frame, style='Sidebar.TFrame')
        self.system_info_frame.pack(fill='x')
        
        self.cpu_label = ttk.Label(self.system_info_frame, text="CPU: ---%", style='Modern.TLabel')
        self.cpu_label.pack(anchor='w')
        
        self.memory_label = ttk.Label(self.system_info_frame, text="Memory: ---%", style='Modern.TLabel')
        self.memory_label.pack(anchor='w')
        
        self.disk_label = ttk.Label(self.system_info_frame, text="Disk: ---%", style='Modern.TLabel')
        self.disk_label.pack(anchor='w')
        
    def create_main_content(self, parent):
        """Create the main content area"""
        content_frame = ttk.Frame(parent, style='Modern.TFrame', padding=10)
        content_frame.grid(row=1, column=1, sticky='nsew')
        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_columnconfigure(0, weight=1)
        
        # Chat area
        self.create_chat_area(content_frame)
        
        # Input area
        self.create_input_area(content_frame)
        
    def create_chat_area(self, parent):
        """Create the chat/conversation area"""
        chat_frame = ttk.Frame(parent, style='Modern.TFrame')
        chat_frame.grid(row=0, column=0, sticky='nsew', pady=(0, 10))
        chat_frame.grid_rowconfigure(0, weight=1)
        chat_frame.grid_columnconfigure(0, weight=1)
        
        # Chat display
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame, 
            wrap=tk.WORD,
            bg=self.colors['bg_primary'],
            fg=self.colors['text_primary'],
            font=('Consolas', 11),
            selectbackground=self.colors['accent'],
            insertbackground=self.colors['accent'],
            borderwidth=1,
            relief='solid'
        )
        self.chat_display.grid(row=0, column=0, sticky='nsew')
        
        # Configure text tags for different message types
        self.chat_display.tag_configure('user', foreground=self.colors['accent'], font=('Consolas', 11, 'bold'))
        self.chat_display.tag_configure('ai', foreground=self.colors['success'], font=('Consolas', 11, 'bold'))
        self.chat_display.tag_configure('system', foreground=self.colors['warning'], font=('Consolas', 10, 'italic'))
        self.chat_display.tag_configure('error', foreground=self.colors['error'], font=('Consolas', 10, 'bold'))
        self.chat_display.tag_configure('timestamp', foreground=self.colors['text_secondary'], font=('Consolas', 9))
        
        # Welcome message
        self.add_chat_message("🤖 AayushAGI initialized successfully!", "system")
        self.add_chat_message("Welcome to the world's most advanced personal AI assistant!", "ai")
        self.add_chat_message("Type 'help' to see available commands or use the quick actions on the left.", "ai")
        
    def create_input_area(self, parent):
        """Create the input area"""
        input_frame = ttk.Frame(parent, style='Modern.TFrame')
        input_frame.grid(row=1, column=0, sticky='ew')
        input_frame.grid_columnconfigure(0, weight=1)
        
        # Input field
        self.input_var = tk.StringVar()
        self.input_entry = tk.Entry(
            input_frame,
            textvariable=self.input_var,
            bg=self.colors['bg_tertiary'],
            fg=self.colors['text_primary'],
            font=('Segoe UI', 12),
            relief='flat',
            borderwidth=2,
            insertbackground=self.colors['accent']
        )
        self.input_entry.grid(row=0, column=0, sticky='ew', padx=(0, 10))
        self.input_entry.bind('<Return>', self.process_input)
        self.input_entry.bind('<Up>', self.input_history_up)
        self.input_entry.bind('<Down>', self.input_history_down)
        
        # Send button
        self.send_button = ttk.Button(
            input_frame,
            text="Send 📤",
            command=self.process_input,
            style='Accent.TButton'
        )
        self.send_button.grid(row=0, column=1)
        
        # Voice button
        self.voice_button = ttk.Button(
            input_frame,
            text="🎤 Voice",
            command=self.toggle_voice_input,
            style='Modern.TButton'
        )
        self.voice_button.grid(row=0, column=2, padx=(5, 0))
        
        # Input history
        self.input_history = []
        self.history_index = -1
        
    def create_status_bar(self, parent):
        """Create the status bar"""
        status_frame = ttk.Frame(parent, style='Modern.TFrame', padding=5)
        status_frame.grid(row=2, column=0, columnspan=2, sticky='ew')
        
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(status_frame, textvariable=self.status_var, style='Modern.TLabel')
        self.status_label.pack(side='left')
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(status_frame, variable=self.progress_var, mode='indeterminate')
        self.progress_bar.pack(side='right', padx=(10, 0))
        
    def setup_ai(self):
        """Initialize the AI system"""
        try:
            self.add_chat_message("Initializing AI systems...", "system")
            self.ai_instance = AayushAGI()
            self.add_chat_message("✅ AI systems online!", "system")
        except Exception as e:
            self.add_chat_message(f"❌ Error initializing AI: {str(e)}", "error")
    
    def start_background_tasks(self):
        """Start background monitoring tasks"""
        self.update_system_info()
        self.process_message_queue()
        
    def add_chat_message(self, message, msg_type="ai", show_timestamp=True):
        """Add a message to the chat display"""
        self.chat_display.config(state='normal')
        
        if show_timestamp:
            timestamp = datetime.now().strftime("[%H:%M:%S] ")
            self.chat_display.insert(tk.END, timestamp, 'timestamp')
        
        if msg_type == "user":
            self.chat_display.insert(tk.END, "👤 You: ", 'user')
        elif msg_type == "ai":
            self.chat_display.insert(tk.END, "🤖 AayushAGI: ", 'ai')
        elif msg_type == "system":
            self.chat_display.insert(tk.END, "⚙️ System: ", 'system')
        elif msg_type == "error":
            self.chat_display.insert(tk.END, "❌ Error: ", 'error')
        
        self.chat_display.insert(tk.END, message + "\n", msg_type)
        
        if self.auto_scroll.get():
            self.chat_display.see(tk.END)
        
        self.chat_display.config(state='disabled')
        
    def process_input(self, event=None):
        """Process user input"""
        if self.is_processing:
            return
            
        user_input = self.input_var.get().strip()
        if not user_input:
            return
            
        # Add to history
        self.input_history.append(user_input)
        self.history_index = len(self.input_history)
        
        # Clear input
        self.input_var.set("")
        
        # Add to chat
        self.add_chat_message(user_input, "user")
        
        # Process in background thread
        threading.Thread(target=self._process_ai_input, args=(user_input,), daemon=True).start()
        
    def _process_ai_input(self, user_input):
        """Process input with AI (runs in background thread)"""
        self.is_processing = True
        self.root.after(0, lambda: self.status_var.set("Processing..."))
        self.root.after(0, self.progress_bar.start)
        
        try:
            if self.ai_instance:
                # Handle special GUI commands
                if user_input.lower() in ['clear', 'cls']:
                    self.root.after(0, self.clear_chat)
                elif user_input.lower() == 'exit':
                    self.root.after(0, self.root.quit)
                else:
                    # Process with AI
                    response = self.ai_instance.process_input(user_input)
                    if response is not False:  # If AI doesn't want to exit
                        self.root.after(0, lambda: self.add_chat_message("Command processed successfully.", "ai"))
            else:
                self.root.after(0, lambda: self.add_chat_message("AI system not initialized.", "error"))
                
        except Exception as e:
            self.root.after(0, lambda: self.add_chat_message(f"Error processing command: {str(e)}", "error"))
        finally:
            self.is_processing = False
            self.root.after(0, self.progress_bar.stop)
            self.root.after(0, lambda: self.status_var.set("Ready"))
    
    def input_history_up(self, event):
        """Navigate input history up"""
        if self.input_history and self.history_index > 0:
            self.history_index -= 1
            self.input_var.set(self.input_history[self.history_index])
    
    def input_history_down(self, event):
        """Navigate input history down"""
        if self.input_history and self.history_index < len(self.input_history) - 1:
            self.history_index += 1
            self.input_var.set(self.input_history[self.history_index])
        elif self.history_index >= len(self.input_history) - 1:
            self.history_index = len(self.input_history)
            self.input_var.set("")
    
    def clear_chat(self):
        """Clear the chat display"""
        self.chat_display.config(state='normal')
        self.chat_display.delete('1.0', tk.END)
        self.chat_display.config(state='disabled')
        self.add_chat_message("Chat cleared.", "system")
    
    def toggle_voice_mode(self):
        """Toggle voice mode"""
        if self.voice_mode.get():
            self.add_chat_message("Voice mode activated! 🎤", "system")
        else:
            self.add_chat_message("Voice mode deactivated.", "system")
    
    def toggle_voice_input(self):
        """Handle voice input button"""
        self.add_chat_message("Voice input feature coming soon! 🎤", "system")
    
    def show_system_status(self):
        """Show system status"""
        if self.ai_instance:
            threading.Thread(target=lambda: self._process_ai_input("system status"), daemon=True).start()
    
    def show_memory_stats(self):
        """Show memory statistics"""
        if self.ai_instance:
            threading.Thread(target=lambda: self._process_ai_input("memory stats"), daemon=True).start()
    
    def clean_system(self):
        """Trigger system cleanup"""
        if self.ai_instance:
            threading.Thread(target=lambda: self._process_ai_input("clean system"), daemon=True).start()
    
    def organize_files(self):
        """Trigger file organization"""
        if self.ai_instance:
            threading.Thread(target=lambda: self._process_ai_input("organize files"), daemon=True).start()
    
    def security_scan(self):
        """Trigger security scan"""
        if self.ai_instance:
            threading.Thread(target=lambda: self._process_ai_input("security scan"), daemon=True).start()
    
    def network_check(self):
        """Trigger network diagnostics"""
        if self.ai_instance:
            threading.Thread(target=lambda: self._process_ai_input("network diagnostics"), daemon=True).start()
    
    def optimize_system(self):
        """Trigger system optimization"""
        if self.ai_instance:
            threading.Thread(target=lambda: self._process_ai_input("optimize performance"), daemon=True).start()
    
    def update_system_info(self):
        """Update system information display"""
        try:
            import psutil
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory_percent = psutil.virtual_memory().percent
            disk_percent = psutil.disk_usage('/').percent
            
            self.cpu_label.config(text=f"CPU: {cpu_percent:.1f}%")
            self.memory_label.config(text=f"Memory: {memory_percent:.1f}%")
            self.disk_label.config(text=f"Disk: {disk_percent:.1f}%")
            
        except ImportError:
            self.cpu_label.config(text="CPU: N/A")
            self.memory_label.config(text="Memory: N/A")
            self.disk_label.config(text="Disk: N/A")
        except:
            pass
        
        # Schedule next update
        self.root.after(5000, self.update_system_info)  # Update every 5 seconds
    
    def process_message_queue(self):
        """Process messages from background threads"""
        try:
            while True:
                message, msg_type = self.message_queue.get_nowait()
                self.add_chat_message(message, msg_type)
        except queue.Empty:
            pass
        
        # Schedule next check
        self.root.after(100, self.process_message_queue)

def main():
    """Main function to start the GUI"""
    # Verify dependencies
    try:
        import psutil
    except ImportError:
        print("Installing required packages...")
        os.system("pip install psutil")
    
    # Create and run the GUI
    root = tk.Tk()
    app = ModernAayushAGI(root)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\nShutting down AayushAGI GUI...")
    except Exception as e:
        print(f"Error running GUI: {e}")

if __name__ == "__main__":
    main()
