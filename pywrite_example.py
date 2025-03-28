#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyWrite Example Script
Shows how to use the enhanced editor, comment assistant, and Sidecar together
"""

import os
import sys
import subprocess
import time

def main():
    """Main function to demonstrate PyWrite functionality."""
    print("====================================")
    print("  PyWrite Demo Script")
    print("====================================\n")
    
    # Step 1: Create a new Python file from template
    print("Step 1: Creating a new Python file from template...\n")
    template_file = "example_code.py"
    subprocess.run(["python", "enhanced_editor.py", "create", template_file, "python"])
    time.sleep(1)
    
    # Step 2: View the file
    print("\nStep 2: Viewing the created file...\n")
    subprocess.run(["python", "enhanced_editor.py", "view", template_file])
    time.sleep(1)
    
    # Step 3: Analyze the file for missing comments
    print("\nStep 3: Analyzing file for missing comments...\n")
    subprocess.run(["python", "comment_assistant.py", "analyze", template_file])
    time.sleep(1)
    
    # Step 4: Create a more complex file for testing
    print("\nStep 4: Creating a more complex file for testing...\n")
    with open("complex_example.py", "w") as f:
        f.write('''
class DataProcessor:
    def __init__(self, input_file, output_file):
        self.input_file = input_file
        self.output_file = output_file
        self.data = []
        self.processed_data = []
        
    def process_data(self):
        for item in self.data:
            if item and "key" in item and item["key"] > 10:
                self.processed_data.append(item["value"])
        return len(self.processed_data)
    
    def save_results(self):
        with open(self.output_file, "w") as f:
            for item in self.processed_data:
                f.write(f"{item}\\n")
                
def validate_inputs(input_path, output_path):
    if not os.path.exists(input_path):
        print(f"Error: Input file {input_path} does not exist")
        return False
    return True

def main():
    processor = DataProcessor("input.json", "output.txt")
    processor.process_data()
    processor.save_results()
''')
    print("Created complex_example.py")
    time.sleep(1)
    
    # Step 5: Analyze the complex file
    print("\nStep 5: Analyzing the complex file...\n")
    subprocess.run(["python", "comment_assistant.py", "analyze", "complex_example.py"])
    time.sleep(1)
    
    # Step 6: Improve the file
    print("\nStep 6: Improving the complex file with comments...\n")
    subprocess.run(["python", "comment_assistant.py", "improve", "complex_example.py", "--output", "complex_example_improved.py"])
    time.sleep(1)
    
    # Step 7: Compare the files
    print("\nStep 7: Comparing original and improved files...\n")
    subprocess.run(["python", "enhanced_editor.py", "compare", "complex_example.py", "complex_example_improved.py"])
    
    # Step 8: Demonstrate Sidecar feature
    print("\nStep 8: Demonstrating the Sidecar AI Assistant feature...\n")
    print("The Sidecar assistant can provide real-time help with your code.")
    print("It observes your screen and provides contextual assistance.")
    print("To start Sidecar in another terminal, run: ./pywrite.sh sidecar")
    
    # Create a simulated conversation for demo purposes
    print("\nExample Sidecar conversation:")
    print("\nYou: Can you help me improve my code documentation?")
    time.sleep(1)
    print("\nSidecar: Absolutely! Good documentation makes code more maintainable and")
    print("         easier to understand. Here are tips for better documentation:")
    print("         1. Use clear docstrings for functions, classes, and modules")
    print("         2. Explain 'why' not just 'what' the code does")
    print("         3. Keep comments up-to-date as code changes")
    print("         4. Document parameters and return values")
    print("         5. Include examples for complex functions")
    
    time.sleep(1)
    print("\nYou: How do I structure a good README file?")
    time.sleep(1)
    print("\nSidecar: A well-structured README should include:")
    print("         1. Project name and description")
    print("         2. Installation instructions")
    print("         3. Usage examples with code snippets")
    print("         4. Features and capabilities")
    print("         5. Dependencies and requirements")
    print("         6. Configuration options")
    print("         7. License information")
    print("         Keep it concise but informative with clear formatting.")
    
    print("\nDemo completed! You can now explore the following files:")
    print("- example_code.py: Simple Python template file")
    print("- complex_example.py: More complex Python file without proper comments")
    print("- complex_example_improved.py: The same file with improved comments")
    print("\nTo try the Sidecar feature, run: ./pywrite.sh sidecar")

if __name__ == "__main__":
    main()