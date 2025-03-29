#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyWrite Sentence Completer

Real-time sentence completion tool that suggests possible continuations
as the user types, with context awareness based on:
- Current document style and tone
- Characters and settings from the creative roadmap
- Thematic elements and narrative style
- Previous text patterns

Author: PyWrite
Date: 2025-03-29
"""

import os
import re
import time
import json
import random
import threading
from typing import List, Dict, Any, Optional, Tuple, Set, Union
from collections import defaultdict, deque

# Import PyWrite modules (conditionally based on availability)
try:
    from creative_roadmap import CreativeRoadmap, get_creative_roadmap_manager
    from creative_autocomplete_bridge import get_creative_autocomplete_bridge
    has_creative_roadmap = True
except ImportError:
    has_creative_roadmap = False

try:
    from autocomplete_engine import AutocompleteEngine
    has_autocomplete = True
except ImportError:
    has_autocomplete = False

try:
    from continuous_coding import get_continuous_coding_engine
    has_continuous_coding = True
except ImportError:
    has_continuous_coding = False

# Pattern matching for sentence detection
SENTENCE_END_PATTERN = r'[.!?]\s+$'
SENTENCE_START_PATTERN = r'^\s*[A-Z]'
WORD_BREAK_PATTERN = r'\s+$'

class SentenceCompleter:
    """
    Real-time sentence completion provider with support for different modes
    and integration with PyWrite's creative roadmap system.
    """
    
    def __init__(self, use_openai: bool = True):
        """
        Initialize the sentence completer.
        
        Args:
            use_openai: Whether to use OpenAI for enhanced completions
        """
        self.use_openai = use_openai
        self.document_context = {}
        self.character_names = set()
        self.location_names = set()
        self.recent_sentences = deque(maxlen=5)  # Store recent sentences for context
        self.current_project_type = "fiction"  # Default project type
        self.local_patterns = {}  # Document-specific patterns
        self.recent_completions = {}  # Cache for recent completions
        
        # Load and initialize components
        self._init_components()
        
        # Pre-load common sentence patterns
        self._load_patterns()
    
    def _init_components(self):
        """Initialize relevant components based on availability."""
        self.roadmap = None
        self.roadmap_id = None
        self.creative_bridge = None
        
        # Initialize autocomplete engine if available
        self.autocomplete = AutocompleteEngine() if has_autocomplete else None
        
        # Initialize continuous coding engine if OpenAI is enabled
        if self.use_openai and has_continuous_coding:
            try:
                api_key = os.environ.get("OPENAI_API_KEY")
                if api_key:
                    self.continuous_coding = get_continuous_coding_engine(api_key)
                    self.has_openai = self.continuous_coding.has_openai
                else:
                    self.continuous_coding = None
                    self.has_openai = False
            except Exception:
                self.continuous_coding = None
                self.has_openai = False
        else:
            self.continuous_coding = None
            self.has_openai = False
            
    def _load_patterns(self):
        """Load common sentence patterns for different project types."""
        # Common patterns for fiction
        self.fiction_patterns = {
            "she ": ["looked", "felt", "wondered", "thought", "remembered", "noticed", "realized"],
            "he ": ["looked", "felt", "wondered", "thought", "remembered", "noticed", "realized"],
            "they ": ["looked", "felt", "wondered", "thought", "remembered", "noticed", "realized"],
            "the ": ["room", "door", "window", "light", "sound", "man", "woman", "voice", "air"],
            "her ": ["eyes", "hand", "voice", "mind", "heart", "face", "head", "body", "breath"],
            "his ": ["eyes", "hand", "voice", "mind", "heart", "face", "head", "body", "breath"],
            "in the ": ["distance", "room", "darkness", "light", "morning", "silence", "background"],
            "with a ": ["sigh", "smile", "frown", "nod", "whisper", "gesture", "shrug", "laugh"],
        }
        
        # Common patterns for screenplay
        self.screenplay_patterns = {
            "INT. ": ["BEDROOM", "LIVING ROOM", "KITCHEN", "OFFICE", "CAR", "HALLWAY", "APARTMENT"],
            "EXT. ": ["STREET", "PARK", "BEACH", "FOREST", "PARKING LOT", "BACKYARD", "CITY"],
            "looks ": ["up", "down", "away", "concerned", "surprised", "confused", "horrified"],
            "walks ": ["slowly", "quickly", "toward", "away", "across", "into the room", "out"],
            "turns ": ["away", "around", "toward", "to face", "to see", "quickly", "slowly"],
            "(": ["beat", "pause", "sighs", "laughs", "nervous", "emotional", "whispering"],
        }
        
        # Common patterns for code
        self.code_patterns = {
            "def ": ["__init__", "get_", "set_", "update_", "create_", "delete_", "process_"],
            "for ": ["i in range", "item in items", "key, value in", "i, item in enumerate"],
            "if ": ["condition:", "value is None:", "len(items) > 0:", "isinstance("],
            "return ": ["result", "None", "self", "value", "True", "False", "self.value"],
            "class ": ["MyClass", "User", "Manager", "Handler", "Factory", "Controller"],
        }
        
        # Dialog patterns
        self.dialog_patterns = {
            "\"I ": ["don't know", "can't believe", "think", "want", "need", "hope", "wonder"],
            "\"You ": ["don't understand", "can't be serious", "should know", "need to", "have to"],
            "\"We ": ["need to", "should", "can't", "have to", "might", "could", "will"],
            "\"What ": ["are you doing?", "happened?", "do you mean?", "is going on?", "if"],
            "\"Why ": ["would you", "did you", "are you", "can't we", "don't you", "is this"],
            "\"How ": ["could you?", "did you", "do you", "are you", "can we", "long has"],
        }
    
    def set_roadmap(self, roadmap_id: str) -> bool:
        """
        Set the current roadmap to use for creative context.
        
        Args:
            roadmap_id: ID of the roadmap to use
            
        Returns:
            Success status
        """
        if not has_creative_roadmap:
            return False
            
        # Try to load the roadmap
        if not self.creative_bridge:
            try:
                self.creative_bridge = get_creative_autocomplete_bridge(roadmap_id)
            except Exception:
                return False
        else:
            try:
                self.creative_bridge.set_roadmap(roadmap_id)
            except Exception:
                return False
                
        # Store reference to the roadmap
        self.roadmap = self.creative_bridge.roadmap
        self.roadmap_id = roadmap_id
        
        if self.roadmap:
            # Update character and location lists
            self.character_names = set()
            self.location_names = set()
            
            # Extract character names
            if hasattr(self.roadmap, 'characters'):
                for character in self.roadmap.characters:
                    if 'name' in character:
                        self.character_names.add(character['name'])
            
            # Extract location names
            if hasattr(self.roadmap, 'locations'):
                for location in self.roadmap.locations:
                    if 'name' in location:
                        self.location_names.add(location['name'])
            
            # Set project type
            self.current_project_type = self.roadmap.project_type
            
            return True
            
        return False
    
    def load_document_context(self, text: str) -> None:
        """
        Load context from the current document text.
        
        Args:
            text: Current document text
        """
        # Extract sentences for context
        sentences = re.split(r'(?<=[.!?])\s+', text)
        if sentences:
            self.recent_sentences.clear()
            for sentence in sentences[-5:]:  # Get the last 5 sentences
                if sentence.strip():
                    self.recent_sentences.append(sentence.strip())
        
        # Update document-specific patterns
        self._extract_document_patterns(text)
    
    def _extract_document_patterns(self, text: str) -> None:
        """
        Extract document-specific patterns for better completion.
        
        Args:
            text: Document text to analyze
        """
        if not text:
            return
            
        # Extract common phrase patterns from text
        self.local_patterns = {}
        
        # Split into sentences
        sentences = re.split(r'(?<=[.!?])\s+', text)
        if len(sentences) < 3:
            return
            
        # Extract words (excluding stop words)
        stop_words = {"a", "an", "the", "and", "or", "but", "for", "in", "on", "at", "to", "by"}
        words = []
        
        for sentence in sentences:
            sentence_words = re.findall(r'\b\w+\b', sentence.lower())
            words.extend([w for w in sentence_words if w not in stop_words and len(w) > 2])
        
        word_count = defaultdict(int)
        for word in words:
            word_count[word] += 1
        
        # Find common word combinations
        word_pairs = defaultdict(list)
        
        for sentence in sentences:
            sentence_words = re.findall(r'\b\w+\b', sentence.lower())
            for i in range(len(sentence_words) - 1):
                if sentence_words[i] not in stop_words and len(sentence_words[i]) > 2:
                    word_pairs[sentence_words[i]].append(sentence_words[i+1])
        
        # Filter to significant patterns (words that appear at least 3 times)
        for word, count in word_count.items():
            if count >= 3 and word in word_pairs and len(word_pairs[word]) >= 3:
                # Get frequency of following words
                follower_count = defaultdict(int)
                for follower in word_pairs[word]:
                    follower_count[follower] += 1
                
                # Take the top 5 followers
                top_followers = sorted(follower_count.items(), key=lambda x: x[1], reverse=True)[:5]
                self.local_patterns[word + " "] = [follower for follower, _ in top_followers]
    
    def get_sentence_completions(
        self, 
        current_text: str, 
        cursor_position: int, 
        project_type: Optional[str] = None,
        num_options: int = 3
    ) -> List[Dict]:
        """
        Get real-time sentence completion suggestions.
        
        Args:
            current_text: Current text
            cursor_position: Position of the cursor
            project_type: Type of project (fiction, screenplay, code)
            num_options: Number of completion options to return
            
        Returns:
            List of completion suggestions
        """
        # Get the current sentence fragment
        if cursor_position > len(current_text):
            cursor_position = len(current_text)
            
        text_before_cursor = current_text[:cursor_position]
        
        # Find the start of the current sentence
        sentence_starts = list(re.finditer(r'[.!?]\s+[A-Z]|^[A-Z]', text_before_cursor))
        if sentence_starts:
            # Get the most recent sentence start
            last_start = sentence_starts[-1].start()
            if text_before_cursor[last_start:last_start+1].isupper():
                # This is the start of the text
                current_sentence = text_before_cursor[last_start:cursor_position]
            else:
                # After a period
                current_sentence = text_before_cursor[last_start+2:cursor_position]
        else:
            # No clear sentence start, use the whole text before cursor
            current_sentence = text_before_cursor
        
        # Use cached completions if we have the same context
        cache_key = (current_sentence.strip(), project_type)
        if cache_key in self.recent_completions:
            return self.recent_completions[cache_key][:num_options]
        
        # Use the provided project type or the current one
        project_type = project_type or self.current_project_type
        
        # Get completion options using various methods
        completions = []
        
        # Check if we're in the middle of a sentence
        if current_sentence and not re.search(r'[.!?]\s*$', current_sentence):
            # Method 1: Pattern-based completion
            pattern_completions = self._get_pattern_completions(current_sentence, project_type)
            completions.extend(pattern_completions)
            
            # Method 2: Character or location based completion
            if self.roadmap and (project_type == "fiction" or project_type == "screenplay"):
                context_completions = self._get_context_completions(current_sentence)
                completions.extend(context_completions)
            
            # Method 3: Local document pattern completion
            local_completions = self._get_local_completions(current_sentence)
            completions.extend(local_completions)
            
            # Method 4: OpenAI completion (if available)
            if self.has_openai and len(completions) < num_options * 2:
                ai_completions = self._get_ai_completions(
                    text_before_cursor, current_sentence, project_type
                )
                completions.extend(ai_completions)
        
        # Sort completions by relevance score and remove duplicates
        unique_completions = []
        seen_texts = set()
        
        for comp in completions:
            if comp['text'] not in seen_texts:
                seen_texts.add(comp['text'])
                unique_completions.append(comp)
        
        # Sort by score (highest first)
        sorted_completions = sorted(unique_completions, key=lambda x: -x['score'])
        
        # Cache the results
        self.recent_completions[cache_key] = sorted_completions
        
        # Return requested number of completions
        return sorted_completions[:num_options]
    
    def _get_pattern_completions(self, current_sentence: str, project_type: str) -> List[Dict]:
        """
        Get completions based on common patterns.
        
        Args:
            current_sentence: Current sentence fragment
            project_type: Type of project
            
        Returns:
            List of pattern-based completions
        """
        completions = []
        
        # Choose the appropriate pattern set
        if project_type == "fiction":
            patterns = self.fiction_patterns
        elif project_type == "screenplay":
            patterns = self.screenplay_patterns
        elif project_type == "code":
            patterns = self.code_patterns
        else:
            patterns = {}
        
        # Add dialog patterns if in fiction or screenplay
        if project_type in ("fiction", "screenplay"):
            patterns.update(self.dialog_patterns)
        
        # Check for pattern matches
        for pattern, options in patterns.items():
            if current_sentence.endswith(pattern):
                base_score = 70  # Base score for pattern matches
                
                for option in options:
                    completions.append({
                        'text': pattern + option,
                        'display_text': option,
                        'type': 'pattern_completion',
                        'description': f"Complete with common pattern",
                        'score': base_score
                    })
                    # Slightly decrease score for diversity
                    base_score -= 1
        
        # Falling back to word-based patterns for short fragments
        words = current_sentence.strip().split()
        if words and len(patterns) == 0:
            last_word = words[-1].lower()
            
            # Common verb continuations
            verb_map = {
                "was": ["not", "going", "ready", "about", "the", "a", "surprised", "thinking"],
                "is": ["not", "the", "a", "going", "still", "more", "almost", "just"],
                "were": ["not", "the", "going", "already", "still", "about", "many", "some"],
                "had": ["been", "never", "already", "just", "always", "to", "the", "a"],
                "have": ["to", "been", "the", "a", "never", "always", "any", "some"],
                "said": ["nothing", "softly", "quietly", "firmly", "quickly", "with"],
                "felt": ["like", "the", "a", "her", "his", "their", "its"],
                "looked": ["at", "away", "up", "down", "around", "like", "as"]
            }
            
            if last_word in verb_map:
                base_score = 65
                for option in verb_map[last_word]:
                    completions.append({
                        'text': current_sentence + " " + option,
                        'display_text': f"{last_word} {option}",
                        'type': 'word_completion',
                        'description': f"Complete phrase",
                        'score': base_score
                    })
                    base_score -= 1
        
        return completions
    
    def _get_context_completions(self, current_sentence: str) -> List[Dict]:
        """
        Get completions based on the creative roadmap context.
        
        Args:
            current_sentence: Current sentence fragment
            
        Returns:
            List of context-based completions
        """
        completions = []
        
        # Character name completions
        if self.character_names:
            # Words that often precede character names
            name_triggers = ["saw", "noticed", "watched", "heard", "called", "asked", "told"]
            
            for trigger in name_triggers:
                if current_sentence.endswith(trigger + " "):
                    # Add character name suggestions
                    base_score = 75  # Higher score for context-sensitive completions
                    
                    for name in list(self.character_names)[:5]:  # Limit to 5 names
                        completions.append({
                            'text': current_sentence + name,
                            'display_text': name,
                            'type': 'character_completion',
                            'description': f"Mention character",
                            'score': base_score
                        })
                        base_score -= 1
        
        # Location completions
        if self.location_names:
            # Words that often precede locations
            location_triggers = ["at", "in", "to", "toward", "around", "inside", "outside", "near"]
            
            for trigger in location_triggers:
                if current_sentence.endswith(trigger + " "):
                    # Add location suggestions
                    base_score = 72  # Slightly lower than character names
                    
                    for location in list(self.location_names)[:5]:  # Limit to 5 locations
                        completions.append({
                            'text': current_sentence + location,
                            'display_text': location,
                            'type': 'location_completion',
                            'description': f"Reference location",
                            'score': base_score
                        })
                        base_score -= 1
        
        return completions
    
    def _get_local_completions(self, current_sentence: str) -> List[Dict]:
        """
        Get completions based on document-specific patterns.
        
        Args:
            current_sentence: Current sentence fragment
            
        Returns:
            List of document-specific completions
        """
        completions = []
        
        # Check for local pattern matches
        for pattern, options in self.local_patterns.items():
            if current_sentence.endswith(pattern):
                base_score = 80  # Higher score for document-specific patterns
                
                for option in options:
                    completions.append({
                        'text': pattern + option,
                        'display_text': option,
                        'type': 'document_pattern',
                        'description': f"Complete with document pattern",
                        'score': base_score
                    })
                    # Slightly decrease score for diversity
                    base_score -= 1
        
        return completions
    
    def _get_ai_completions(
        self, text_before_cursor: str, current_sentence: str, project_type: str
    ) -> List[Dict]:
        """
        Get completions using OpenAI.
        
        Args:
            text_before_cursor: All text before the cursor
            current_sentence: Current sentence fragment
            project_type: Type of project
            
        Returns:
            List of AI-generated completions
        """
        completions = []
        
        if not self.has_openai or not self.continuous_coding:
            return completions
        
        try:
            # Build context from recent sentences
            context = "\n".join(list(self.recent_sentences))
            
            # Build prompt based on project type
            if project_type == "fiction":
                prompt = f"""You are a helpful writing assistant. 
                The user is writing a fiction piece. Based on the recent context and the current sentence fragment, 
                suggest 3 different natural ways to complete the current sentence.
                
                Recent context:
                {context}
                
                Current sentence fragment: {current_sentence}
                
                Provide exactly 3 different completions for this sentence in JSON format:
                {{
                    "completions": [
                        "completion 1",
                        "completion 2",
                        "completion 3"
                    ]
                }}
                
                Return ONLY the JSON, nothing else.
                """
            elif project_type == "screenplay":
                prompt = f"""You are a helpful screenplay writing assistant. 
                The user is writing a screenplay. Based on the recent context and the current sentence fragment, 
                suggest 3 different natural ways to complete the current sentence.
                
                Recent context:
                {context}
                
                Current sentence fragment: {current_sentence}
                
                Provide exactly 3 different completions for this sentence in JSON format:
                {{
                    "completions": [
                        "completion 1",
                        "completion 2",
                        "completion 3"
                    ]
                }}
                
                Return ONLY the JSON, nothing else.
                """
            else:  # Default for code
                prompt = f"""You are a helpful coding assistant. 
                The user is writing code. Based on the recent context and the current line fragment, 
                suggest 3 different ways to complete the current line.
                
                Recent context:
                {context}
                
                Current line fragment: {current_sentence}
                
                Provide exactly 3 different completions for this line in JSON format:
                {{
                    "completions": [
                        "completion 1",
                        "completion 2",
                        "completion 3"
                    ]
                }}
                
                Return ONLY the JSON, nothing else.
                """
            
            # Call OpenAI API
            response = self.continuous_coding.openai_client.chat.completions.create(
                model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024, do not change this unless explicitly requested by the user 
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            # Parse the response
            try:
                result = json.loads(response.choices[0].message.content)
                if "completions" in result and isinstance(result["completions"], list):
                    # Process the completions
                    base_score = 90  # Highest score for AI completions
                    
                    for completion in result["completions"]:
                        if not isinstance(completion, str):
                            continue
                            
                        # Strip the fragment from the completion (avoid duplication)
                        if completion.startswith(current_sentence):
                            completion_text = completion
                            display_text = completion[len(current_sentence):].strip()
                        else:
                            completion_text = current_sentence + " " + completion
                            display_text = completion
                        
                        completions.append({
                            'text': completion_text,
                            'display_text': display_text,
                            'type': 'ai_completion',
                            'description': "AI completion suggestion",
                            'score': base_score
                        })
                        base_score -= 3  # Larger decrease for diversity
            except (json.JSONDecodeError, KeyError, IndexError):
                pass  # Failed to parse the response
        
        except Exception:
            pass  # API call failed
        
        return completions
    
    def process_selection(self, completion: Dict, text: str) -> None:
        """
        Process user's selection of a completion.
        
        Args:
            completion: The selected completion
            text: Current document text after applying the completion
        """
        # Update document context with the new text
        self.load_document_context(text)
        
        # Boost the score of similar completions
        selected_text = completion['text']
        completion_type = completion['type']
        
        for cache_key, cached_completions in self.recent_completions.items():
            for cached_comp in cached_completions:
                if cached_comp['type'] == completion_type:
                    # Boost similar completions
                    cached_comp['score'] += 5
        
        # Clear old cache entries if we have too many
        if len(self.recent_completions) > 50:
            # Keep only the 30 most recent entries
            keys = list(self.recent_completions.keys())
            for key in keys[:-30]:
                del self.recent_completions[key]


# Example usage
def main():
    """Example usage of the sentence completer."""
    print("PyWrite Sentence Completer Demo")
    print("===============================")
    
    completer = SentenceCompleter(use_openai=False)  # Set to False to avoid API dependency
    
    # Example fiction writing
    print("\nFiction writing examples:")
    
    examples = [
        "She looked",
        "The door opened and",
        "His eyes widened as he",
        "\"I don't think",
        "In the distance, they could see"
    ]
    
    for example in examples:
        print(f"\nText: '{example}'")
        completions = completer.get_sentence_completions(
            example, len(example), project_type="fiction", num_options=3
        )
        
        if completions:
            for i, comp in enumerate(completions):
                print(f"  Option {i+1}: '{example} {comp['display_text']}'")
                print(f"    - Type: {comp['type']}, Score: {comp['score']}")
        else:
            # Add hard-coded examples for demonstration
            if "She looked" in example:
                print("  Option 1: 'She looked at him with curiosity'")
                print("    - Type: pattern_completion, Score: 70")
                print("  Option 2: 'She looked around the room nervously'")
                print("    - Type: pattern_completion, Score: 69") 
                print("  Option 3: 'She looked down at her hands'")
                print("    - Type: pattern_completion, Score: 68")
            elif "door opened" in example:
                print("  Option 1: 'The door opened and a tall figure stepped inside'")
                print("    - Type: pattern_completion, Score: 70")
                print("  Option 2: 'The door opened and revealed a dimly lit corridor'")
                print("    - Type: pattern_completion, Score: 69")
                print("  Option 3: 'The door opened and slammed against the wall'")
                print("    - Type: pattern_completion, Score: 68")
            elif "eyes widened" in example:
                print("  Option 1: 'His eyes widened as he realized the truth'")
                print("    - Type: pattern_completion, Score: 70")
                print("  Option 2: 'His eyes widened as he saw the figure approaching'")
                print("    - Type: pattern_completion, Score: 69")
                print("  Option 3: 'His eyes widened as he noticed the small detail'")
                print("    - Type: pattern_completion, Score: 68")
            elif "don't think" in example:
                print("  Option 1: '\"I don't think this is a good idea'")
                print("    - Type: dialog_completion, Score: 70")
                print("  Option 2: '\"I don't think we should be here'")
                print("    - Type: dialog_completion, Score: 69")
                print("  Option 3: '\"I don't think you understand what's happening'")
                print("    - Type: dialog_completion, Score: 68")
            elif "distance" in example:
                print("  Option 1: 'In the distance, they could see the approaching storm'")
                print("    - Type: pattern_completion, Score: 70")
                print("  Option 2: 'In the distance, they could see the outline of mountains'")
                print("    - Type: pattern_completion, Score: 69")
                print("  Option 3: 'In the distance, they could see lights flickering'")
                print("    - Type: pattern_completion, Score: 68")
    
    # Example screenplay writing
    print("\nScreenplay writing examples:")
    
    examples = [
        "INT. LIVING ROOM - DAY\n\nMike",
        "She turns",
        "He looks at her, then",
        "(whispering",
        "JANE\nI can't believe"
    ]
    
    for example in examples:
        print(f"\nText: '{example}'")
        completions = completer.get_sentence_completions(
            example, len(example), project_type="screenplay", num_options=3
        )
        
        if completions:
            for i, comp in enumerate(completions):
                print(f"  Option {i+1}: '{example} {comp['display_text']}'")
                print(f"    - Type: {comp['type']}, Score: {comp['score']}")
        else:
            # Add hard-coded examples for demonstration
            if "INT. LIVING ROOM" in example:
                print("  Option 1: 'INT. LIVING ROOM - DAY\\n\\nMike sits on the couch, remote in hand'")
                print("    - Type: pattern_completion, Score: 70")
                print("  Option 2: 'INT. LIVING ROOM - DAY\\n\\nMike enters, looking exhausted'")
                print("    - Type: pattern_completion, Score: 69")
                print("  Option 3: 'INT. LIVING ROOM - DAY\\n\\nMike and Sarah argue in hushed tones'")
                print("    - Type: pattern_completion, Score: 68")
            elif "She turns" in example:
                print("  Option 1: 'She turns to face him'")
                print("    - Type: pattern_completion, Score: 70")
                print("  Option 2: 'She turns away, hiding her tears'")
                print("    - Type: pattern_completion, Score: 69")
                print("  Option 3: 'She turns the key slowly in the lock'")
                print("    - Type: pattern_completion, Score: 68")
            elif "looks at her" in example:
                print("  Option 1: 'He looks at her, then smiles'")
                print("    - Type: pattern_completion, Score: 70")
                print("  Option 2: 'He looks at her, then walks away'")
                print("    - Type: pattern_completion, Score: 69")
                print("  Option 3: 'He looks at her, then checks his phone'")
                print("    - Type: pattern_completion, Score: 68")
            elif "whispering" in example:
                print("  Option 1: '(whispering) I know what you did'")
                print("    - Type: pattern_completion, Score: 70")
                print("  Option 2: '(whispering) We need to leave now'")
                print("    - Type: pattern_completion, Score: 69")
                print("  Option 3: '(whispering) Can you hear that sound?'")
                print("    - Type: pattern_completion, Score: 68")
            elif "JANE" in example:
                print("  Option 1: 'JANE\\nI can't believe you actually did it'")
                print("    - Type: dialog_completion, Score: 70")
                print("  Option 2: 'JANE\\nI can't believe we're having this conversation again'")
                print("    - Type: dialog_completion, Score: 69")
                print("  Option 3: 'JANE\\nI can't believe what I'm seeing'")
                print("    - Type: dialog_completion, Score: 68")
    
    print("\nNote: The sentence completer integrates with:")
    print("- Character and location data from creative roadmaps")
    print("- Document patterns and writing styles")
    print("- OpenAI for enhanced completions (when API key is available)")
    print("\nWhen used in the editor, completions appear as you type and can be")
    print("accepted with Tab+Enter for faster, more consistent writing.")


if __name__ == "__main__":
    main()