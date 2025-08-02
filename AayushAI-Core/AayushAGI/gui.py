# gui.py
import tkinter as tk
from tkinter import messagebox, scrolledtext
from main import AayushAGI
import threading

class AayushAGIGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("AayushAGI - The World's Most Advanced Personal AI Assistant")
        self.master.geometry("800x600")

        self.agi = AayushAGI()

        self.create_widgets()
        
        # Run AI in a separate thread
        self.ai_thread = threading.Thread(target=self.run_ai, daemon=True)
        self.ai_thread.start()

    def create_widgets(self):
        # Create text area for output
        self.text_area = scrolledtext.ScrolledText(self.master, wrap=tk.WORD)
        self.text_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Create command entry
        self.command_label = tk.Label(self.master, text="Enter Command:")
        self.command_label.pack(padx=10, pady=5)
        self.command_entry = tk.Entry(self.master, width=50)
        self.command_entry.pack(padx=10, pady=5)

        # Create buttons
        self.command_button = tk.Button(self.master, text="Execute", command=self.execute_command)
        self.command_button.pack(pady=5)

        self.clear_button = tk.Button(self.master, text="Clear Output", command=self.clear_output)
        self.clear_button.pack(pady=5)

    def run_ai(self):
        # Start the AI processing loop
        self.agi.run()

    def display_text(self, text):
        self.text_area.insert(tk.END, text + "\n")
        self.text_area.yview(tk.END)

    def execute_command(self):
        command = self.command_entry.get()
        self.display_text("You: " + command)
        self.command_entry.delete(0, tk.END)
        
        # Process command in AGI
        output = self.agi.process_input(command)
        if output:
            self.display_text("AayushAGI: " + output)

    def clear_output(self):
        self.text_area.delete('1.0', tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = AayushAGIGUI(root)
    root.mainloop()

