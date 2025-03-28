#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyWrite Guide - Demonstration of PyWrite Utilities
A script to explain how to use the PyWrite tools from the command line
"""

def main():
    """Main function to display PyWrite usage information."""
    print("====================================")
    print("  PyWrite Command-Line Guide")
    print("====================================\n")
    
    print("PyWrite is a powerful code editor and file management utility")
    print("that can be used directly from the command line.\n")
    
    print("Core Utilities (enhanced_editor.py):")
    print("------------------------------------")
    print("python enhanced_editor.py view <filename> [line-range]")
    print("    View a file with line numbers and optional line range")
    print("    Example: python enhanced_editor.py view example_code.py")
    print("    Example: python enhanced_editor.py view example_code.py 5-10\n")
    
    print("python enhanced_editor.py list [directory] [pattern]")
    print("    List files matching a pattern in a directory")
    print("    Example: python enhanced_editor.py list . *.py\n")
    
    print("python enhanced_editor.py run <filename.py>")
    print("    Execute a Python file")
    print("    Example: python enhanced_editor.py run example_code.py\n")
    
    print("python enhanced_editor.py create <filename> [template]")
    print("    Create a new file from a template (python, html, css, javascript, json, markdown)")
    print("    Example: python enhanced_editor.py create new_script.py python\n")
    
    print("python enhanced_editor.py copy <source> <destination>")
    print("    Copy a file from source to destination")
    print("    Example: python enhanced_editor.py copy original.py backup.py\n")
    
    print("python enhanced_editor.py cat <output> <input1> [input2 ...]")
    print("    Concatenate multiple files into one output file")
    print("    Example: python enhanced_editor.py cat combined.py part1.py part2.py\n")
    
    print("python enhanced_editor.py search <pattern> [directory] [file-pattern]")
    print("    Search for a pattern in files matching a pattern")
    print("    Example: python enhanced_editor.py search \"function\" . \"*.py\"\n")
    
    print("python enhanced_editor.py compare <file1> <file2>")
    print("    Compare two files and show differences")
    print("    Example: python enhanced_editor.py compare original.py modified.py\n")
    
    print("Comment Assistant (comment_assistant.py):")
    print("----------------------------------------")
    print("python comment_assistant.py analyze <filename>")
    print("    Analyze a file for missing comments and documentation")
    print("    Example: python comment_assistant.py analyze example_code.py\n")
    
    print("python comment_assistant.py improve <filename> --output <output_file>")
    print("    Generate an improved version of a file with proper documentation")
    print("    Example: python comment_assistant.py improve example_code.py --output improved_code.py\n")
    
    print("Sidecar AI Assistant (sidecar.py):")
    print("----------------------------------------")
    print("python sidecar.py")
    print("    Start the AI assistant with voice chat and screen observation")
    print("    Example: python sidecar.py\n")
    print("    Note: Requires OpenAI API key set as environment variable OPENAI_API_KEY")
    print("          Without the API key, Sidecar runs in demo mode.\n")
    
    print("Sidecar Features:")
    print("  - Observes your screen to understand what you're working on")
    print("  - Provides contextual assistance based on the code you're writing")
    print("  - Suggests improvements for documentation and coding style")
    print("  - Answers programming questions with context-aware responses")
    print("  - Helps with code organization and best practices\n")
    
    print("Example Sidecar Commands:")
    print("  - \"Can you help me improve my code documentation?\"")
    print("  - \"How do I structure a good README file?\"")
    print("  - \"What's the best way to organize my Python project?\"")
    print("  - \"Can you suggest a better name for this function?\"")
    print("  - \"How can I write more readable code?\"\n")
    
    print("Additional Resources:")
    print("-------------------")
    print("- For a demo of these features, run: python pywrite_example.py")
    print("- Explore the template files in the template_examples directory")
    print("- Check README.md for complete documentation\n")
    
    print("Happy coding with PyWrite!")

if __name__ == "__main__":
    main()