# utils/nlp_engine.py
import re
import random
from datetime import datetime, timedelta
import json
import requests

class NLPEngine:
    def __init__(self):
        self.conversation_history = []
        self.user_preferences = {}
        self.load_responses()
    
    def load_responses(self):
        """Load pre-defined intelligent responses"""
        self.responses = {
            "greetings": [
                "Hello! How can I assist you today?",
                "Hi there! What would you like to do?",
                "Good to see you! How may I help?",
                "Welcome back! What's on your mind?"
            ],
            "compliments": [
                "Thank you! I'm here to help you achieve great things.",
                "That's very kind of you! I'm always learning to serve you better.",
                "I appreciate that! Let's accomplish something amazing together."
            ],
            "thinking": [
                "Let me process that for you...",
                "Analyzing your request...",
                "Computing the best response...",
                "Processing your query..."
            ],
            "unknown": [
                "I'm not sure about that yet, but I'm always learning. Could you rephrase?",
                "That's interesting! I don't have enough data on that topic yet.",
                "I'm still expanding my knowledge base. Can you help me understand better?",
                "That's beyond my current capabilities, but I'm constantly improving!"
            ]
        }
    
    def analyze_intent(self, text):
        """Analyze user intent from text"""
        text = text.lower().strip()
        
        # Greeting patterns
        greeting_patterns = [
            r'\b(hi|hello|hey|good morning|good afternoon|good evening)\b',
            r'\b(what\'s up|how are you|howdy)\b'
        ]
        
        # Question patterns
        question_patterns = [
            r'\b(what|who|when|where|why|how)\b.*\?',
            r'\b(can you|could you|would you|will you)\b',
            r'\b(do you know|tell me about|explain)\b'
        ]
        
        # Command patterns
        command_patterns = [
            r'\b(play|open|start|run|execute)\b',
            r'\b(remind me|set reminder|alert me)\b',
            r'\b(search|find|look up|google)\b',
            r'\b(calculate|compute|solve)\b'
        ]
        
        # Emotional patterns
        positive_patterns = [
            r'\b(love|like|awesome|great|amazing|wonderful|excellent)\b'
        ]
        
        negative_patterns = [
            r'\b(hate|dislike|awful|terrible|bad|horrible|worst)\b'
        ]
        
        if any(re.search(pattern, text) for pattern in greeting_patterns):
            return "greeting"
        elif any(re.search(pattern, text) for pattern in question_patterns):
            return "question"
        elif any(re.search(pattern, text) for pattern in command_patterns):
            return "command"
        elif any(re.search(pattern, text) for pattern in positive_patterns):
            return "positive"
        elif any(re.search(pattern, text) for pattern in negative_patterns):
            return "negative"
        else:
            return "unknown"
    
    def extract_entities(self, text):
        """Extract entities like time, dates, numbers, etc."""
        entities = {}
        
        # Time patterns
        time_patterns = [
            r'(\d{1,2}):(\d{2})\s*(am|pm)?',
            r'(\d{1,2})\s*(am|pm)',
            r'(morning|afternoon|evening|night|midnight|noon)'
        ]
        
        # Date patterns
        date_patterns = [
            r'(today|tomorrow|yesterday)',
            r'(monday|tuesday|wednesday|thursday|friday|saturday|sunday)',
            r'(\d{1,2})/(\d{1,2})/(\d{4})',
            r'(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{1,2})'
        ]
        
        # Number patterns
        number_patterns = [
            r'\b(\d+)\s*(minutes?|hours?|seconds?|days?|weeks?|months?|years?)\b',
            r'\b(\d+(?:\.\d+)?)\b'
        ]
        
        # Extract time entities
        for pattern in time_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                entities['time'] = matches
        
        # Extract date entities
        for pattern in date_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                entities['date'] = matches
        
        # Extract number entities
        for pattern in number_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                entities['numbers'] = matches
        
        return entities
    
    def generate_smart_response(self, text, intent, entities):
        """Generate intelligent responses based on context"""
        if intent == "greeting":
            response = random.choice(self.responses["greetings"])
            current_hour = datetime.now().hour
            if 5 <= current_hour < 12:
                response += " Good morning!"
            elif 12 <= current_hour < 17:
                response += " Good afternoon!"
            elif 17 <= current_hour < 21:
                response += " Good evening!"
            else:
                response += " Good night!"
            return response
        
        elif intent == "positive":
            return random.choice(self.responses["compliments"])
        
        elif intent == "question":
            if "weather" in text:
                return "I'd love to help with weather info, but I need internet access for real-time data. Try asking me to search for weather information!"
            elif "time" in text:
                return f"The current time is {datetime.now().strftime('%I:%M %p')}"
            elif "date" in text:
                return f"Today is {datetime.now().strftime('%A, %B %d, %Y')}"
            elif any(word in text for word in ["your", "you", "yourself"]):
                return "I'm AayushAGI, your personal AI assistant created by Aayush Bhandari. I'm here to help you with various tasks!"
            else:
                return random.choice(self.responses["unknown"])
        
        elif intent == "command":
            return random.choice(self.responses["thinking"])
        
        else:
            return random.choice(self.responses["unknown"])
    
    def calculate_basic_math(self, expression):
        """Calculate basic mathematical expressions safely"""
        try:
            # Remove any non-mathematical characters
            safe_expression = re.sub(r'[^0-9+\-*/().\s]', '', expression)
            # Evaluate the expression safely
            result = eval(safe_expression)
            return f"The result is: {result}"
        except:
            return "I couldn't calculate that. Please check your expression."
    
    def process_natural_language(self, text):
        """Main processing function"""
        intent = self.analyze_intent(text)
        entities = self.extract_entities(text)
        
        # Store conversation history
        self.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "input": text,
            "intent": intent,
            "entities": entities
        })
        
        # Limit history to last 10 conversations
        if len(self.conversation_history) > 10:
            self.conversation_history.pop(0)
        
        # Generate response
        response = self.generate_smart_response(text, intent, entities)
        
        return {
            "response": response,
            "intent": intent,
            "entities": entities,
            "context": self.conversation_history[-3:] if len(self.conversation_history) >= 3 else self.conversation_history
        }
