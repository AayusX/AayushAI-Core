# utils/advanced_memory.py
import json
import os
import time
from datetime import datetime, timedelta
from collections import defaultdict, deque
import hashlib
import pickle
import threading
from typing import Dict, List, Any, Optional
import math

class AdvancedMemorySystem:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.memory_file = os.path.join(data_dir, "advanced_memory.json")
        self.patterns_file = os.path.join(data_dir, "learned_patterns.pkl")
        self.neural_weights_file = os.path.join(data_dir, "neural_weights.json")
        
        # Memory components
        self.short_term_memory = deque(maxlen=50)  # Last 50 interactions
        self.long_term_memory = {}
        self.episodic_memory = {}  # Events with timestamps
        self.semantic_memory = {}  # Facts and knowledge
        self.procedural_memory = {}  # How to do things
        
        # Learning components
        self.user_preferences = defaultdict(float)
        self.command_frequency = defaultdict(int)
        self.response_effectiveness = defaultdict(list)
        self.context_patterns = defaultdict(list)
        
        # Neural-like weights for decision making
        self.neural_weights = {
            "greeting_importance": 0.7,
            "task_completion": 0.9,
            "emotional_support": 0.8,
            "information_accuracy": 0.95,
            "response_speed": 0.6
        }
        
        self.load_memory()
        self.learning_thread = threading.Thread(target=self._continuous_learning, daemon=True)
        self.learning_thread.start()
    
    def load_memory(self):
        """Load all memory components from files"""
        try:
            if os.path.exists(self.memory_file):
                with open(self.memory_file, 'r') as f:
                    data = json.load(f)
                    self.long_term_memory = data.get('long_term', {})
                    self.episodic_memory = data.get('episodic', {})
                    self.semantic_memory = data.get('semantic', {})
                    self.procedural_memory = data.get('procedural', {})
                    self.user_preferences = defaultdict(float, data.get('preferences', {}))
                    self.command_frequency = defaultdict(int, data.get('frequency', {}))
            
            if os.path.exists(self.neural_weights_file):
                with open(self.neural_weights_file, 'r') as f:
                    self.neural_weights.update(json.load(f))
                    
        except Exception as e:
            print(f"[Memory] Error loading memory: {e}")
    
    def save_memory(self):
        """Save all memory components to files"""
        try:
            os.makedirs(self.data_dir, exist_ok=True)
            
            memory_data = {
                'long_term': dict(self.long_term_memory),
                'episodic': dict(self.episodic_memory),
                'semantic': dict(self.semantic_memory),
                'procedural': dict(self.procedural_memory),
                'preferences': dict(self.user_preferences),
                'frequency': dict(self.command_frequency)
            }
            
            with open(self.memory_file, 'w') as f:
                json.dump(memory_data, f, indent=2)
            
            with open(self.neural_weights_file, 'w') as f:
                json.dump(self.neural_weights, f, indent=2)
                
        except Exception as e:
            print(f"[Memory] Error saving memory: {e}")
    
    def store_interaction(self, user_input: str, ai_response: str, context: Dict[str, Any]):
        """Store a complete interaction in memory"""
        timestamp = datetime.now().isoformat()
        interaction_id = hashlib.md5(f"{timestamp}{user_input}".encode()).hexdigest()[:12]
        
        interaction = {
            'id': interaction_id,
            'timestamp': timestamp,
            'user_input': user_input,
            'ai_response': ai_response,
            'context': context,
            'effectiveness_score': 0.5  # Will be updated based on user feedback
        }
        
        # Store in short-term memory
        self.short_term_memory.append(interaction)
        
        # Store in episodic memory
        self.episodic_memory[interaction_id] = interaction
        
        # Update command frequency
        self.command_frequency[user_input.lower()] += 1
        
        # Extract and store semantic information
        self._extract_semantic_info(user_input, ai_response)
        
    def _extract_semantic_info(self, user_input: str, ai_response: str):
        """Extract semantic information from interactions"""
        # Extract entities and facts
        words = user_input.lower().split()
        
        # Store facts about user preferences
        if any(word in user_input.lower() for word in ['like', 'love', 'prefer', 'enjoy']):
            for word in words:
                if word not in ['i', 'like', 'love', 'prefer', 'enjoy', 'the', 'a', 'an']:
                    self.user_preferences[word] += 0.1
        
        # Store negative preferences
        if any(word in user_input.lower() for word in ['hate', 'dislike', 'dont like', "don't like"]):
            for word in words:
                if word not in ['i', 'hate', 'dislike', 'dont', "don't", 'like', 'the', 'a', 'an']:
                    self.user_preferences[word] -= 0.1
    
    def get_context_aware_response(self, current_input: str) -> Dict[str, Any]:
        """Generate context-aware information for response generation"""
        context = {
            'recent_interactions': list(self.short_term_memory)[-5:],
            'user_preferences': dict(self.user_preferences),
            'similar_past_queries': self._find_similar_queries(current_input),
            'emotional_state': self._detect_emotional_context(),
            'time_context': self._get_time_context(),
            'frequency_score': self.command_frequency.get(current_input.lower(), 0)
        }
        
        return context
    
    def _find_similar_queries(self, query: str, limit: int = 3) -> List[Dict]:
        """Find similar past queries using simple similarity"""
        query_words = set(query.lower().split())
        similar_queries = []
        
        for interaction in self.episodic_memory.values():
            past_query = interaction['user_input']
            past_words = set(past_query.lower().split())
            
            # Calculate Jaccard similarity
            intersection = len(query_words.intersection(past_words))
            union = len(query_words.union(past_words))
            
            if union > 0 and intersection > 0:
                similarity = intersection / union
                if similarity > 0.3:  # Threshold for similarity
                    similar_queries.append({
                        'query': past_query,
                        'response': interaction['ai_response'],
                        'similarity': similarity,
                        'timestamp': interaction['timestamp']
                    })
        
        return sorted(similar_queries, key=lambda x: x['similarity'], reverse=True)[:limit]
    
    def _detect_emotional_context(self) -> str:
        """Detect emotional context from recent interactions"""
        if not self.short_term_memory:
            return "neutral"
        
        recent_interactions = list(self.short_term_memory)[-3:]
        emotional_indicators = {
            'positive': ['good', 'great', 'excellent', 'amazing', 'wonderful', 'happy', 'love'],
            'negative': ['bad', 'terrible', 'awful', 'hate', 'sad', 'angry', 'frustrated'],
            'excited': ['excited', 'thrilled', 'awesome', 'fantastic', 'incredible'],
            'confused': ['confused', 'dont understand', "don't understand", 'help', 'unclear']
        }
        
        emotion_scores = defaultdict(int)
        
        for interaction in recent_interactions:
            user_input = interaction['user_input'].lower()
            for emotion, indicators in emotional_indicators.items():
                for indicator in indicators:
                    if indicator in user_input:
                        emotion_scores[emotion] += 1
        
        if emotion_scores:
            return max(emotion_scores, key=emotion_scores.get)
        return "neutral"
    
    def _get_time_context(self) -> Dict[str, Any]:
        """Get contextual information based on time"""
        now = datetime.now()
        return {
            'hour': now.hour,
            'day_of_week': now.strftime('%A'),
            'month': now.strftime('%B'),
            'is_weekend': now.weekday() >= 5,
            'time_of_day': self._get_time_of_day(now.hour)
        }
    
    def _get_time_of_day(self, hour: int) -> str:
        """Get time of day classification"""
        if 5 <= hour < 12:
            return "morning"
        elif 12 <= hour < 17:
            return "afternoon"
        elif 17 <= hour < 21:
            return "evening"
        else:
            return "night"
    
    def learn_from_feedback(self, interaction_id: str, feedback_score: float):
        """Learn from user feedback on responses"""
        if interaction_id in self.episodic_memory:
            self.episodic_memory[interaction_id]['effectiveness_score'] = feedback_score
            
            # Update neural weights based on feedback
            if feedback_score > 0.7:
                # Positive feedback - reinforce patterns
                interaction = self.episodic_memory[interaction_id]
                context = interaction.get('context', {})
                
                # Increase weights for successful patterns
                for key, weight in self.neural_weights.items():
                    if key in context:
                        self.neural_weights[key] = min(1.0, weight + 0.01)
    
    def _continuous_learning(self):
        """Background learning process"""
        while True:
            time.sleep(300)  # Learn every 5 minutes
            self._analyze_patterns()
            self.save_memory()
    
    def _analyze_patterns(self):
        """Analyze interaction patterns for learning"""
        if len(self.episodic_memory) < 10:
            return
        
        # Analyze successful interaction patterns
        successful_interactions = [
            interaction for interaction in self.episodic_memory.values()
            if interaction.get('effectiveness_score', 0.5) > 0.7
        ]
        
        # Extract common patterns from successful interactions
        for interaction in successful_interactions:
            user_input = interaction['user_input'].lower()
            
            # Learn greeting patterns
            if any(word in user_input for word in ['hi', 'hello', 'hey', 'good morning']):
                self.neural_weights['greeting_importance'] = min(1.0, 
                    self.neural_weights['greeting_importance'] + 0.005)
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get statistics about memory usage"""
        return {
            'short_term_count': len(self.short_term_memory),
            'long_term_count': len(self.long_term_memory),
            'episodic_count': len(self.episodic_memory),
            'semantic_count': len(self.semantic_memory),
            'top_preferences': dict(sorted(self.user_preferences.items(), 
                                         key=lambda x: x[1], reverse=True)[:10]),
            'most_used_commands': dict(sorted(self.command_frequency.items(),
                                            key=lambda x: x[1], reverse=True)[:10]),
            'neural_weights': self.neural_weights
        }
    
    def cleanup_old_memories(self, days_threshold: int = 30):
        """Clean up old, less important memories"""
        cutoff_date = datetime.now() - timedelta(days=days_threshold)
        
        # Remove old episodic memories with low effectiveness scores
        to_remove = []
        for interaction_id, interaction in self.episodic_memory.items():
            try:
                interaction_date = datetime.fromisoformat(interaction['timestamp'])
                if (interaction_date < cutoff_date and 
                    interaction.get('effectiveness_score', 0.5) < 0.4):
                    to_remove.append(interaction_id)
            except:
                continue
        
        for interaction_id in to_remove:
            del self.episodic_memory[interaction_id]
        
        print(f"[Memory] Cleaned up {len(to_remove)} old memories")
