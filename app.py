import os
import sys
import argparse
import time

def print_banner():
    """Print the PyWrite banner."""
    print("\n====================================")
    print("  PyWrite Simple File Editor")
    print("====================================\n")

def view_file(filename):
    """Display the contents of a file with line numbers."""
    if not os.path.exists(filename):
        print(f"Error: File '{filename}' does not exist.")
        return False
    
    try:
        with open(filename, 'r') as file:
            content = file.readlines()
        
        print(f"\nFile: {filename}\n")
        print("=" * 50)
        for i, line in enumerate(content, 1):
            print(f"{i:4d} | {line}", end='')
        if content and not content[-1].endswith('\n'):
            print()  # Add a newline if the last line doesn't have one
        print("=" * 50)
        print(f"\nTotal lines: {len(content)}")
        return True
    except Exception as e:
        print(f"Error reading file: {str(e)}")
        return False

def list_files(directory='.', extension=None):
    """List files in the given directory, optionally filtering by extension."""
    print(f"\nFiles in {os.path.abspath(directory)}:\n")
    print("=" * 50)
    
    try:
        files = os.listdir(directory)
        files.sort()
        
        count = 0
        for filename in files:
            if filename.startswith('.'):
                continue  # Skip hidden files
                
            filepath = os.path.join(directory, filename)
            if os.path.isfile(filepath):
                if extension and not filename.endswith(extension):
                    continue
                
                print(f"- {filename}")
                count += 1
            elif os.path.isdir(filepath):
                print(f"/ {filename}/")
        
        print("=" * 50)
        if extension:
            print(f"\nFound {count} {extension} files")
        else:
            print(f"\nFound {count} files")
    except Exception as e:
        print(f"Error listing files: {str(e)}")

def run_python_file(filename):
    """Run a Python file."""
    if not os.path.exists(filename):
        print(f"Error: File '{filename}' does not exist.")
        return
    
    if not filename.endswith('.py'):
        print("Warning: This doesn't look like a Python file.")
    
    try:
        print(f"\nRunning {filename}...\n")
        print("=" * 50)
        
        # Using exec for simplicity
        with open(filename, 'r') as file:
            code = file.read()
            
        # Create a global namespace for execution
        namespace = {'__file__': filename}
        exec(code, namespace)
        
        print("\n" + "=" * 50)
        print(f"Execution of {filename} complete.")
    except Exception as e:
        print(f"\nError: {str(e)}")

def create_or_edit_file(filename, append=False):
    """Create a new file or append to an existing one using a simple approach."""
    mode = 'a' if append else 'w'
    
    if os.path.exists(filename) and not append:
        print(f"Warning: File '{filename}' already exists and will be overwritten.")
    
    print(f"\n{'Appending to' if append else 'Creating'} {filename}")
    print("Enter your text below. Each line will be saved to the file.")
    print("Enter a line with just '.' (period) to save and exit.")
    print("=" * 50)
    
    with open(filename, mode) as file:
        while True:
            line = input()
            if line == '.':
                break
            file.write(line + '\n')
    
    print(f"File '{filename}' saved successfully!")

def create_simple_python_file(filename):
    """Create a simple Python file with boilerplate code."""
    if os.path.exists(filename):
        print(f"Warning: File '{filename}' already exists and will be overwritten.")
    
    basic_code = """#!/usr/bin/env python3
# -*- coding: utf-8 -*-
\"\"\"
Description: A simple Python script
Author: PyWrite
Date: {date}
\"\"\"

def main():
    \"\"\"Main function.\"\"\"
    print("Hello, World!")
    
    # Your code here

if __name__ == "__main__":
    main()
""".format(date=time.strftime("%Y-%m-%d"))
    
    with open(filename, 'w') as file:
        file.write(basic_code)
    
    print(f"Created Python file: {filename}")
    return True

def print_usage():
    """Display program usage information."""
    print("\nUsage:")
    print("  python app.py view <filename>     - View a file")
    print("  python app.py list [directory]    - List files in a directory")
    print("  python app.py new <filename>      - Create a new file")
    print("  python app.py append <filename>   - Append to an existing file")
    print("  python app.py run <filename.py>   - Run a Python file")
    print("  python app.py newpy <filename.py> - Create a new Python file with template")
    print("\nExamples:")
    print("  python app.py view sample.txt")
    print("  python app.py list")
    print("  python app.py list sample_novel")
    print("  python app.py new my_file.txt")
    print("  python app.py run my_script.py")

def main():
    """Main function to parse arguments and call appropriate handlers."""
    print_banner()
    
    parser = argparse.ArgumentParser(description='PyWrite Simple File Editor', add_help=False)
    parser.add_argument('command', nargs='?', default='help')
    parser.add_argument('filename', nargs='?', default=None)
    
    try:
        args = parser.parse_args()
        command = args.command.lower()
        filename = args.filename
        
        if command == 'view' and filename:
            view_file(filename)
        elif command == 'list':
            list_files(filename or '.')
        elif command == 'run' and filename:
            run_python_file(filename)
        elif command == 'new' and filename:
            create_or_edit_file(filename, append=False)
        elif command == 'append' and filename:
            create_or_edit_file(filename, append=True)
        elif command == 'newpy' and filename:
            create_simple_python_file(filename)
        else:
            print_usage()
    except Exception as e:
        print(f"Error: {str(e)}")
        print_usage()

if __name__ == "__main__":
    main()