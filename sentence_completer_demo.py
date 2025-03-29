#!/usr/bin/env python3
"""
PyWrite Sentence Completer Demo

This script provides a simplified demonstration of the PyWrite Sentence Completer.
It shows a series of examples in fiction, screenplay, and code formats,
displaying the possible completions for partial sentences.

Author: PyWrite
Date: 2025-03-29
"""

import os
import sys
import time
from typing import List, Dict

# Add current directory to path to ensure imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sentence_completer import SentenceCompleter

def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(text)
    print("=" * 60)

def print_completion(text, comp, index):
    """Print a formatted completion option."""
    print(f"  [{index}] {text}{comp['display_text']}")
    print(f"      Type: {comp['type']}, Score: {comp['score']}")

def demonstrate_fiction_mode():
    """Demonstrate the fiction writing mode of the sentence completer."""
    print_header("Fiction Writing Mode")
    
    completer = SentenceCompleter(use_openai=False)
    
    # Add some document context to improve suggestions
    context = """
    The old house creaked as Sarah made her way through the dimly lit hallway.
    She paused, listening intently. Was that a voice she heard? John had been gone
    for hours, and she was supposed to be alone.
    
    The storm outside intensified, rain pounding against the windows. A flash of
    lightning illuminated the room momentarily, casting strange shadows on the walls.
    """
    completer.load_document_context(context)
    
    examples = [
        "She looked",
        "The door opened and",
        "His eyes widened as he",
        "\"I don't think",
        "In the distance, they could see"
    ]
    
    for example in examples:
        print(f"\nInput: '{example}'")
        print("Thinking...", end="\r")
        time.sleep(0.5)  # Simulate processing time
        
        completions = completer.get_sentence_completions(
            example, len(example), project_type="fiction", num_options=3
        )
        
        print(" " * 20, end="\r")  # Clear the "Thinking..." text
        
        if not completions:
            print("  No completions available, using examples:")
            # Fallback to hard-coded examples
            if "She looked" in example:
                print("  [1] She looked at him with curiosity")
                print("      Type: pattern_completion, Score: 70")
                print("  [2] She looked around the room nervously")
                print("      Type: pattern_completion, Score: 69") 
                print("  [3] She looked down at her hands")
                print("      Type: pattern_completion, Score: 68")
            elif "door opened" in example:
                print("  [1] The door opened and a tall figure stepped inside")
                print("      Type: pattern_completion, Score: 70")
                print("  [2] The door opened and revealed a dimly lit corridor")
                print("      Type: pattern_completion, Score: 69")
                print("  [3] The door opened and slammed against the wall")
                print("      Type: pattern_completion, Score: 68")
            elif "eyes widened" in example:
                print("  [1] His eyes widened as he realized the truth")
                print("      Type: pattern_completion, Score: 70")
                print("  [2] His eyes widened as he saw the figure approaching")
                print("      Type: pattern_completion, Score: 69")
                print("  [3] His eyes widened as he noticed the small detail")
                print("      Type: pattern_completion, Score: 68")
            elif "don't think" in example:
                print('  [1] "I don\'t think this is a good idea"')
                print("      Type: dialog_completion, Score: 70")
                print('  [2] "I don\'t think we should be here"')
                print("      Type: dialog_completion, Score: 69")
                print('  [3] "I don\'t think you understand what\'s happening"')
                print("      Type: dialog_completion, Score: 68")
            elif "distance" in example:
                print("  [1] In the distance, they could see the approaching storm")
                print("      Type: pattern_completion, Score: 70")
                print("  [2] In the distance, they could see the outline of mountains")
                print("      Type: pattern_completion, Score: 69")
                print("  [3] In the distance, they could see lights flickering")
                print("      Type: pattern_completion, Score: 68")
        else:
            for i, comp in enumerate(completions):
                print_completion(example, comp, i+1)
    
    print("\nIn a real writing session, these completions would appear")
    print("as you type and can be accepted with Tab+Enter.")

def demonstrate_screenplay_mode():
    """Demonstrate the screenplay writing mode of the sentence completer."""
    print_header("Screenplay Writing Mode")
    
    completer = SentenceCompleter(use_openai=False)
    
    # Add some document context to improve suggestions
    context = """
    INT. ABANDONED WAREHOUSE - NIGHT
    
    Rain pounds on the metal roof. Water drips through in several places.
    
    DETECTIVE MILLER (45, weathered, seen too much) moves cautiously through
    the space, gun drawn. Each step echoes.
    
    MILLER
    (quietly)
    Police. Anyone here?
    
    A CRASH from somewhere deeper in the building. Miller spins toward the sound.
    """
    completer.load_document_context(context)
    
    examples = [
        "INT. LIVING ROOM - DAY\n\nMike",
        "She turns",
        "He looks at her, then",
        "(whispering",
        "JANE\nI can't believe"
    ]
    
    for example in examples:
        print(f"\nInput: '{example}'")
        print("Thinking...", end="\r")
        time.sleep(0.5)  # Simulate processing time
        
        completions = completer.get_sentence_completions(
            example, len(example), project_type="screenplay", num_options=3
        )
        
        print(" " * 20, end="\r")  # Clear the "Thinking..." text
        
        if not completions:
            # Fallback to hard-coded examples
            print("  No completions available, using examples:")
            if "INT. LIVING ROOM" in example:
                print("  [1] INT. LIVING ROOM - DAY\n\n      Mike sits on the couch, remote in hand")
                print("      Type: pattern_completion, Score: 70")
                print("  [2] INT. LIVING ROOM - DAY\n\n      Mike enters, looking exhausted")
                print("      Type: pattern_completion, Score: 69")
                print("  [3] INT. LIVING ROOM - DAY\n\n      Mike and Sarah argue in hushed tones")
                print("      Type: pattern_completion, Score: 68")
            elif "She turns" in example:
                print("  [1] She turns to face him")
                print("      Type: pattern_completion, Score: 70")
                print("  [2] She turns away, hiding her tears")
                print("      Type: pattern_completion, Score: 69")
                print("  [3] She turns the key slowly in the lock")
                print("      Type: pattern_completion, Score: 68")
            elif "looks at her" in example:
                print("  [1] He looks at her, then smiles")
                print("      Type: pattern_completion, Score: 70")
                print("  [2] He looks at her, then walks away")
                print("      Type: pattern_completion, Score: 69")
                print("  [3] He looks at her, then checks his phone")
                print("      Type: pattern_completion, Score: 68")
            elif "whispering" in example:
                print("  [1] (whispering) I know what you did")
                print("      Type: pattern_completion, Score: 70")
                print("  [2] (whispering) We need to leave now")
                print("      Type: pattern_completion, Score: 69")
                print("  [3] (whispering) Can you hear that sound?")
                print("      Type: pattern_completion, Score: 68")
            elif "JANE" in example:
                print("  [1] JANE\n      I can't believe you actually did it")
                print("      Type: dialog_completion, Score: 70")
                print("  [2] JANE\n      I can't believe we're having this conversation again")
                print("      Type: dialog_completion, Score: 69")
                print("  [3] JANE\n      I can't believe what I'm seeing")
                print("      Type: dialog_completion, Score: 68")
        else:
            for i, comp in enumerate(completions):
                print_completion(example, comp, i+1)
    
    print("\nScreenplay format follows industry standards with specific")
    print("patterns for scene headings, action, character cues, and dialog.")

def demonstrate_code_mode():
    """Demonstrate the code writing mode of the sentence completer."""
    print_header("Code Writing Mode")
    
    completer = SentenceCompleter(use_openai=False)
    
    # Add some document context to improve suggestions
    context = """
    def calculate_average(numbers):
        if not numbers:
            return 0
        return sum(numbers) / len(numbers)
        
    class DataProcessor:
        def __init__(self, data_source):
            self.data_source = data_source
            self.results = []
    """
    completer.load_document_context(context)
    
    examples = [
        "def process_data",
        "for item in ",
        "if condition",
        "return ",
        "class User:"
    ]
    
    for example in examples:
        print(f"\nInput: '{example}'")
        print("Thinking...", end="\r")
        time.sleep(0.5)  # Simulate processing time
        
        completions = completer.get_sentence_completions(
            example, len(example), project_type="code", num_options=3
        )
        
        print(" " * 20, end="\r")  # Clear the "Thinking..." text
        
        if not completions:
            # Fallback to hard-coded examples
            print("  No completions available, using examples:")
            if "process_data" in example:
                print("  [1] def process_data(source, options=None):")
                print("      Type: code_completion, Score: 70")
                print("  [2] def process_data(data_list):")
                print("      Type: code_completion, Score: 69")
                print("  [3] def process_data(input_file, output_file=None):")
                print("      Type: code_completion, Score: 68")
            elif "for item in" in example:
                print("  [1] for item in self.data_source:")
                print("      Type: code_completion, Score: 70")
                print("  [2] for item in range(len(data)):")
                print("      Type: code_completion, Score: 69")
                print("  [3] for item in items:")
                print("      Type: code_completion, Score: 68")
            elif "if condition" in example:
                print("  [1] if condition is True:")
                print("      Type: code_completion, Score: 70")
                print("  [2] if condition and value > threshold:")
                print("      Type: code_completion, Score: 69")
                print("  [3] if condition or fallback_condition:")
                print("      Type: code_completion, Score: 68")
            elif "return" in example:
                print("  [1] return self.results")
                print("      Type: code_completion, Score: 70")
                print("  [2] return result if result is not None else default")
                print("      Type: code_completion, Score: 69")
                print("  [3] return {'status': 'success', 'data': processed_data}")
                print("      Type: code_completion, Score: 68")
            elif "class User" in example:
                print("  [1] class User:\n    def __init__(self, username, email):")
                print("      Type: code_completion, Score: 70")
                print("  [2] class User:\n    \"\"\"User class for authentication and profile management\"\"\"")
                print("      Type: code_completion, Score: 69")
                print("  [3] class User:\n    def __init__(self, user_id=None):")
                print("      Type: code_completion, Score: 68")
        else:
            for i, comp in enumerate(completions):
                print_completion(example, comp, i+1)
    
    print("\nCode completions leverage language-specific patterns,")
    print("project context, and common programming structures.")

def show_system_overview():
    """Show an overview of the sentence completion system."""
    print_header("PyWrite Sentence Completer: System Overview")
    
    print("The sentence completer provides real-time suggestions as you type,")
    print("enhancing your writing flow with contextually relevant completions.")
    print("\nKey features:")
    
    features = [
        "• Adaptive to three writing modes: Fiction, Screenplay, and Code",
        "• Context-aware: learns from your current document",
        "• Integrates with your Creative Roadmap for character/setting awareness",
        "• Pattern-based suggestions drawn from common writing structures",
        "• OpenAI integration for enhanced suggestions (when API key is available)",
        "• Selection memory: learns from your preferred completions"
    ]
    
    for feature in features:
        print(feature)
    
    print("\nIntegration points:")
    print("- Connects with creative_roadmap.py for character/setting information")
    print("- Shares pattern data with autocomplete_engine.py for code mode")
    print("- Accessible via the mode_switcher.py across different writing modes")
    
    print("\nAdvanced usage with Creative Roadmap integration:")
    print("When a creative roadmap is active, the sentence completer gains access to:")
    print("- Character names, traits, and dialogue patterns")
    print("- Setting details and descriptive elements")
    print("- Plot points and narrative flow") 
    print("- Thematic elements and stylistic preferences")

def main():
    """Main function."""
    try:
        # Clear terminal
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print("\n" + "=" * 80)
        print(" " * 25 + "PYWRITE SENTENCE COMPLETER DEMO")
        print("=" * 80)
        
        print("\nThis demonstration shows how the sentence completer works")
        print("across different writing modes, providing intelligent continuation")
        print("suggestions as you type.")
        
        # Show all modes automatically without requiring input
        print("\n--- Starting demonstration ---")
        
        # Show system overview
        show_system_overview()
        print("\n--- Fiction mode examples ---")
        
        # Demonstrate fiction mode
        demonstrate_fiction_mode()
        print("\n--- Screenplay mode examples ---")
        
        # Demonstrate screenplay mode
        demonstrate_screenplay_mode()
        print("\n--- Code mode examples ---")
        
        # Demonstrate code mode
        demonstrate_code_mode()
        
        print("\n" + "=" * 80)
        print("Demonstration complete!")
        print("\nIn the full PyWrite environment, the sentence completer is:")
        print("- Integrated into the text editor with real-time suggestions")
        print("- Accessible across all three writing modes")
        print("- Continuously learning from your writing style")
        print("- Connected to your creative roadmap for contextual awareness")
        print("=" * 80)
        
    except KeyboardInterrupt:
        print("\nDemonstration interrupted by user.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")


if __name__ == "__main__":
    main()