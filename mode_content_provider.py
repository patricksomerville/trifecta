#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyWrite Mode Content Provider

A module that provides mode-specific content templates and functionality
for each of the three PyWrite modes: Fiction, Screenwriting, and Code.

Author: PyWrite
Date: 2025-03-28
"""

import os
import datetime
from mode_switcher import MODE_FICTION, MODE_SCREENWRITING, MODE_CODE

class ModeContentProvider:
    """
    Base class for mode-specific content providers.
    
    This class handles functionality common to all modes and defines
    the interface that mode-specific providers must implement.
    """
    
    def __init__(self):
        """Initialize the content provider."""
        self.mode_name = "Base"
        self.file_extension = ".txt"
        
    def get_new_file_template(self):
        """
        Get a template for a new file in this mode.
        
        Returns:
            str: The template content
        """
        return ""
    
    def get_file_extension(self):
        """
        Get the default file extension for this mode.
        
        Returns:
            str: The file extension including the leading dot
        """
        return self.file_extension
    
    def get_toolbar_items(self):
        """
        Get mode-specific toolbar items.
        
        Returns:
            list: List of dictionaries with toolbar item definitions
        """
        return []
    
    def get_menu_items(self):
        """
        Get mode-specific menu items.
        
        Returns:
            list: List of dictionaries with menu item definitions
        """
        return []
    
    def get_mode_name(self):
        """
        Get the name of this mode.
        
        Returns:
            str: The mode name
        """
        return self.mode_name
    
    def get_sidebar_components(self):
        """
        Get components for the mode-specific sidebar.
        
        Returns:
            dict: A dictionary of sidebar component definitions
        """
        return {}
    
    def get_sidecar_prompts(self):
        """
        Get Sidecar AI prompts specific to this mode.
        
        Returns:
            list: List of strings with example prompts for the Sidecar AI
        """
        return [
            "How can I improve my writing?",
            "What should I focus on next?"
        ]


class FictionContentProvider(ModeContentProvider):
    """Content provider for Fiction mode."""
    
    def __init__(self):
        """Initialize the fiction content provider."""
        super().__init__()
        self.mode_name = "Fiction"
        self.file_extension = ".txt"
    
    def get_new_file_template(self):
        """Get a template for a new fiction document."""
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        
        return f"""# Untitled Fiction

By: Author Name
Date: {today}

---

## Chapter 1

[Your story begins here...]

"""
    
    def get_toolbar_items(self):
        """Get fiction-specific toolbar items."""
        return [
            {
                "id": "character",
                "label": "Character",
                "icon": "person",
                "tooltip": "Create/manage characters"
            },
            {
                "id": "plot",
                "label": "Plot",
                "icon": "timeline",
                "tooltip": "Plot structure and outline"
            },
            {
                "id": "settings",
                "label": "Settings",
                "icon": "map",
                "tooltip": "Manage story settings and locations"
            },
            {
                "id": "notes",
                "label": "Notes",
                "icon": "note",
                "tooltip": "Story notes and ideas"
            }
        ]
    
    def get_menu_items(self):
        """Get fiction-specific menu items."""
        return [
            {
                "label": "Fiction",
                "submenu": [
                    {"label": "New Chapter", "command": "new_chapter"},
                    {"label": "Character List", "command": "character_list"},
                    {"label": "Plot Outline", "command": "plot_outline"},
                    {"label": "Word Count", "command": "word_count"},
                    {"label": "Export Novel", "command": "export_novel"}
                ]
            }
        ]
    
    def get_sidebar_components(self):
        """Get components for the fiction sidebar."""
        return {
            "character_list": {
                "title": "Characters",
                "icon": "person",
                "type": "list",
                "empty_text": "No characters created yet."
            },
            "plot_points": {
                "title": "Plot Points",
                "icon": "timeline",
                "type": "tree",
                "empty_text": "No plot points created yet."
            },
            "settings": {
                "title": "Settings",
                "icon": "map",
                "type": "list",
                "empty_text": "No settings created yet."
            }
        }
    
    def get_sidecar_prompts(self):
        """Get Sidecar AI prompts for fiction writing."""
        return [
            "Help me develop this character further",
            "Can you suggest some plot twists?",
            "What's a good way to introduce my main character?",
            "How can I make this dialogue more realistic?",
            "Can you help me describe this setting?",
            "What's a good way to transition between these scenes?",
            "How can I raise the stakes in this chapter?",
            "Can you help me flesh out my antagonist's motivation?"
        ]


class ScreenwritingContentProvider(ModeContentProvider):
    """Content provider for Screenwriting mode."""
    
    def __init__(self):
        """Initialize the screenwriting content provider."""
        super().__init__()
        self.mode_name = "Screenwriting"
        self.file_extension = ".fountain"  # Fountain format for screenplays
    
    def get_new_file_template(self):
        """Get a template for a new screenplay document."""
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        
        return f"""Title: UNTITLED SCREENPLAY
Credit: Written by
Author: Your Name
Draft date: {today}

/*
    This screenplay follows the Fountain syntax.
    For more information, visit fountain.io
*/

# Act 1

== Opening Scene ==

EXT. LOCATION - DAY

[Description of the scene goes here.]

CHARACTER
(action)
Dialogue goes here.

"""
    
    def get_toolbar_items(self):
        """Get screenwriting-specific toolbar items."""
        return [
            {
                "id": "scene",
                "label": "Scene",
                "icon": "movie",
                "tooltip": "Insert new scene"
            },
            {
                "id": "character",
                "label": "Character",
                "icon": "person",
                "tooltip": "Insert character and dialogue"
            },
            {
                "id": "action",
                "label": "Action",
                "icon": "directions_run",
                "tooltip": "Insert action block"
            },
            {
                "id": "transition",
                "label": "Transition",
                "icon": "compare_arrows",
                "tooltip": "Insert transition"
            }
        ]
    
    def get_menu_items(self):
        """Get screenwriting-specific menu items."""
        return [
            {
                "label": "Screenplay",
                "submenu": [
                    {"label": "New Scene", "command": "new_scene"},
                    {"label": "Character List", "command": "character_list"},
                    {"label": "Scene Breakdown", "command": "scene_breakdown"},
                    {"label": "Export PDF", "command": "export_pdf"},
                    {"label": "Export Fountain", "command": "export_fountain"}
                ]
            }
        ]
    
    def get_sidebar_components(self):
        """Get components for the screenwriting sidebar."""
        return {
            "scene_list": {
                "title": "Scenes",
                "icon": "movie",
                "type": "list",
                "empty_text": "No scenes created yet."
            },
            "characters": {
                "title": "Characters",
                "icon": "person",
                "type": "list",
                "empty_text": "No characters created yet."
            },
            "beat_sheet": {
                "title": "Beat Sheet",
                "icon": "list",
                "type": "list",
                "empty_text": "No beats created yet."
            }
        }
    
    def get_sidecar_prompts(self):
        """Get Sidecar AI prompts for screenwriting."""
        return [
            "How do I format a montage?",
            "Can you suggest a good establishing shot?",
            "Help me make this dialogue more concise",
            "How can I describe this action sequence?",
            "Can you help me structure this scene?",
            "What's a good transition between these scenes?",
            "How can I convey this character's emotion without dialogue?",
            "Can you help me write a better scene heading?"
        ]


class CodeContentProvider(ModeContentProvider):
    """Content provider for Code mode."""
    
    def __init__(self):
        """Initialize the code content provider."""
        super().__init__()
        self.mode_name = "Code"
        self.file_extension = ".py"  # Default to Python
    
    def get_new_file_template(self):
        """Get a template for a new Python code file."""
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        
        return f"""#!/usr/bin/env python3
# -*- coding: utf-8 -*-
\"\"\"
Description: A Python script
Author: PyWrite
Date: {today}
\"\"\"

def main():
    \"\"\"Main function.\"\"\"
    print("Hello, World!")

if __name__ == "__main__":
    main()
"""
    
    def get_toolbar_items(self):
        """Get code-specific toolbar items."""
        return [
            {
                "id": "run",
                "label": "Run",
                "icon": "play_arrow",
                "tooltip": "Run the current script"
            },
            {
                "id": "debug",
                "label": "Debug",
                "icon": "bug_report",
                "tooltip": "Debug the current script"
            },
            {
                "id": "format",
                "label": "Format",
                "icon": "format_align_left",
                "tooltip": "Format the code"
            },
            {
                "id": "comments",
                "label": "Comments",
                "icon": "comment",
                "tooltip": "Generate/improve comments"
            }
        ]
    
    def get_menu_items(self):
        """Get code-specific menu items."""
        return [
            {
                "label": "Code",
                "submenu": [
                    {"label": "Run Script", "command": "run_script"},
                    {"label": "Check Syntax", "command": "check_syntax"},
                    {"label": "Generate Comments", "command": "generate_comments"},
                    {"label": "Format Code", "command": "format_code"},
                    {"label": "Toggle Console", "command": "toggle_console"}
                ]
            }
        ]
    
    def get_sidebar_components(self):
        """Get components for the code sidebar."""
        return {
            "file_browser": {
                "title": "Files",
                "icon": "folder",
                "type": "tree",
                "empty_text": "No files in the current directory."
            },
            "outline": {
                "title": "Outline",
                "icon": "account_tree",
                "type": "tree",
                "empty_text": "No symbols found in the current file."
            },
            "console": {
                "title": "Console",
                "icon": "terminal",
                "type": "console",
                "empty_text": "Run your code to see output here."
            }
        }
    
    def get_sidecar_prompts(self):
        """Get Sidecar AI prompts for coding."""
        return [
            "Can you explain what this code does?",
            "How can I optimize this function?",
            "Help me debug this error",
            "What's a better way to implement this?",
            "Can you suggest comments for this code?",
            "How can I make this code more readable?",
            "What design pattern would work here?",
            "Can you help me write a test for this function?"
        ]


class ModeContentFactory:
    """Factory for creating the appropriate content provider for each mode."""
    
    @staticmethod
    def create_provider(mode):
        """
        Create a content provider for the specified mode.
        
        Args:
            mode: One of the MODE_* constants from mode_switcher
            
        Returns:
            ModeContentProvider: The appropriate content provider
        """
        if mode == MODE_FICTION:
            return FictionContentProvider()
        elif mode == MODE_SCREENWRITING:
            return ScreenwritingContentProvider()
        else:  # Default to CODE mode
            return CodeContentProvider()


# Demo functionality
if __name__ == "__main__":
    import json
    
    def print_mode_info(mode):
        """Print information about a mode."""
        provider = ModeContentFactory.create_provider(mode)
        
        print(f"\n{'=' * 40}")
        print(f"  {provider.get_mode_name()} Mode")
        print(f"{'=' * 40}")
        
        print(f"\nDefault File Extension: {provider.get_file_extension()}")
        
        print("\nNew File Template:")
        print(f"```\n{provider.get_new_file_template()}\n```")
        
        print("\nToolbar Items:")
        print(json.dumps(provider.get_toolbar_items(), indent=2))
        
        print("\nMenu Items:")
        print(json.dumps(provider.get_menu_items(), indent=2))
        
        print("\nSidebar Components:")
        print(json.dumps(provider.get_sidebar_components(), indent=2))
        
        print("\nSidecar Prompts:")
        for prompt in provider.get_sidecar_prompts():
            print(f"- {prompt}")
    
    # Print info for all modes
    print_mode_info(MODE_FICTION)
    print_mode_info(MODE_SCREENWRITING)
    print_mode_info(MODE_CODE)