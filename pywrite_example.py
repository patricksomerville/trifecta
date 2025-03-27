#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyWrite Example Script
Shows how to use the enhanced editor and comment assistant together
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
    
    print("\nDemo completed! You can now explore the following files:")
    print("- example_code.py: Simple Python template file")
    print("- complex_example.py: More complex Python file without proper comments")
    print("- complex_example_improved.py: The same file with improved comments")

if __name__ == "__main__":
    main()