import os

class TerminalUI:
    """Professional terminal UI utility class for AayushAGI"""
    
    # Color codes
    COLORS = {
        'reset': '\033[0m',
        'bold': '\033[1m',
        'dim': '\033[2m',
        'underline': '\033[4m',
        'blink': '\033[5m',
        'reverse': '\033[7m',
        'black': '\033[30m',
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'magenta': '\033[95m',
        'cyan': '\033[96m',
        'white': '\033[97m'
    }
    
    @staticmethod
    def blue(text):
        return f"\033[94m{text}\033[0m"

    @staticmethod
    def green(text):
        return f"\033[92m{text}\033[0m"

    @staticmethod
    def yellow(text):
        return f"\033[93m{text}\033[0m"

    @staticmethod
    def red(text):
        return f"\033[91m{text}\033[0m"
    
    @staticmethod
    def cyan(text):
        return f"\033[96m{text}\033[0m"
    
    @staticmethod
    def magenta(text):
        return f"\033[95m{text}\033[0m"

    @staticmethod
    def bold(text):
        return f"\033[1m{text}\033[0m"
    
    @staticmethod
    def dim(text):
        return f"\033[2m{text}\033[0m"
    
    @staticmethod
    def underline(text):
        return f"\033[4m{text}\033[0m"

    @staticmethod
    def clear_screen():
        os.system("clear" if os.name == "posix" else "cls")
    
    @staticmethod
    def print_separator(char="─", length=70, color="blue"):
        """Print a styled separator line"""
        color_func = getattr(TerminalUI, color, TerminalUI.blue)
        print(color_func(char * length))
    
    @staticmethod
    def print_centered(text, width=70, color="white"):
        """Print centered text"""
        color_func = getattr(TerminalUI, color, lambda x: x)
        padding = (width - len(text)) // 2
        centered_text = "" * padding + text
        print(color_func(centered_text))
    
    @staticmethod
    def format_status(icon, label, value, label_color="blue", value_color="white"):
        """Format status information consistently"""
        label_func = getattr(TerminalUI, label_color, TerminalUI.blue)
        value_func = getattr(TerminalUI, value_color, lambda x: x)
        return f"{icon} {label_func(label)} {value_func(value)}"
