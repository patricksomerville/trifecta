#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyWrite Simple File Editor with no interactive input
This version reads from files and writes to files without requiring interactive input.
"""

import os
import sys
import argparse
import time
import glob

def print_banner():
    """Print the PyWrite banner."""
    print("\n====================================")
    print("  PyWrite File Utilities")
    print("====================================\n")

def view_file(filename, line_range=None):
    """Display the contents of a file with line numbers."""
    if not os.path.exists(filename):
        print(f"Error: File '{filename}' does not exist.")
        return False
    
    try:
        with open(filename, 'r') as file:
            lines = file.readlines()
        
        print(f"\nFile: {filename}\n")
        print("=" * 50)
        
        # Handle line range if specified
        start_line = 0
        end_line = len(lines)
        
        if line_range:
            parts = line_range.split('-')
            if len(parts) == 2:
                try:
                    start_line = max(0, int(parts[0]) - 1)  # Convert to 0-based indexing
                    end_line = min(len(lines), int(parts[1]))
                except ValueError:
                    print(f"Invalid line range: {line_range}")
            
        # Display the lines
        for i, line in enumerate(lines[start_line:end_line], start_line + 1):
            print(f"{i:4d} | {line}", end='')
        
        if lines and not lines[-1].endswith('\n'):
            print()  # Add a newline if the last line doesn't have one
        
        print("=" * 50)
        print(f"\nTotal lines: {len(lines)}")
        return True
    except Exception as e:
        print(f"Error reading file: {str(e)}")
        return False

def list_files(directory='.', pattern='*'):
    """List files in the given directory with optional glob pattern."""
    print(f"\nFiles matching '{pattern}' in {os.path.abspath(directory)}:\n")
    print("=" * 50)
    
    try:
        # Combine directory and pattern
        search_pattern = os.path.join(directory, pattern)
        matching_files = glob.glob(search_pattern)
        matching_files.sort()
        
        # Print directories first
        directories = [f for f in matching_files if os.path.isdir(f)]
        for dir_path in directories:
            print(f"/ {os.path.basename(dir_path)}/")
        
        # Then print files
        files = [f for f in matching_files if os.path.isfile(f)]
        for file_path in files:
            print(f"- {os.path.basename(file_path)}")
        
        print("=" * 50)
        print(f"\nFound {len(files)} files and {len(directories)} directories")
    except Exception as e:
        print(f"Error listing files: {str(e)}")

def run_python_file(filename):
    """Run a Python file."""
    if not os.path.exists(filename):
        print(f"Error: File '{filename}' does not exist.")
        return
    
    try:
        print(f"\nRunning {filename}...\n")
        print("=" * 50)
        
        # Use subprocess to run the Python file
        import subprocess
        result = subprocess.run([sys.executable, filename], 
                               capture_output=True, 
                               text=True)
        
        # Print stdout
        if result.stdout:
            print(result.stdout)
        
        # Print stderr if there was an error
        if result.returncode != 0:
            print(f"Error (exit code {result.returncode}):")
            if result.stderr:
                print(result.stderr)
        
        print("=" * 50)
        print(f"Execution of {filename} {'completed successfully' if result.returncode == 0 else 'failed'}.")
    except Exception as e:
        print(f"\nError: {str(e)}")

def create_from_template(filename, template_type='python'):
    """Create a new file from a template."""
    if os.path.exists(filename):
        print(f"Warning: File '{filename}' already exists and will be overwritten.")
    
    if template_type.lower() == 'python':
        content = f"""#!/usr/bin/env python3
# -*- coding: utf-8 -*-
\"\"\"
Description: A Python script
Author: PyWrite
Date: {time.strftime("%Y-%m-%d")}
\"\"\"

def main():
    \"\"\"Main function.\"\"\"
    print("Hello, World!")
    
    # Your code here

if __name__ == "__main__":
    main()
"""
    elif template_type.lower() == 'html':
        content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
        }
    </style>
</head>
<body>
    <h1>Hello, World!</h1>
    <p>This is a sample HTML page.</p>
    
    <script>
        // JavaScript code here
        console.log('Page loaded');
    </script>
</body>
</html>
"""
    elif template_type.lower() == 'javascript' or template_type.lower() == 'js':
        content = f"""/**
 * JavaScript module
 * Author: PyWrite
 * Date: {time.strftime("%Y-%m-%d")}
 */

// Main function
function main() {
    console.log("Hello, World!");
    
    // Your code here
}

// Event listener for DOM loading
document.addEventListener('DOMContentLoaded', function() {
    main();
});

// Export functions if using modules
export { main };
"""
    elif template_type.lower() == 'css':
        content = f"""/**
 * CSS Stylesheet
 * Author: PyWrite
 * Date: {time.strftime("%Y-%m-%d")}
 */

/* Reset some default styles */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Arial', sans-serif;
    line-height: 1.6;
    color: #333;
    background-color: #f4f4f4;
    padding: 20px;
}

/* Container */
.container {
    width: 80%;
    max-width: 1200px;
    margin: 0 auto;
    overflow: hidden;
}

/* Typography */
h1, h2, h3 {
    margin-bottom: 15px;
    color: #333;
}

p {
    margin-bottom: 15px;
}

/* Buttons */
.btn {
    display: inline-block;
    padding: 10px 20px;
    background: #333;
    color: #fff;
    border: none;

def search_in_files(search_pattern, directory='.', file_pattern='*.*'):
    """Search for a pattern in files matching the given file pattern."""
    import re
    
    print(f"\nSearching for '{search_pattern}' in files matching '{file_pattern}' in {os.path.abspath(directory)}:\n")
    print("=" * 50)
    
    try:
        # Get all matching files
        search_path = os.path.join(directory, file_pattern)
        matching_files = glob.glob(search_path, recursive=True)
        matching_files.sort()
        
        # Compile the search pattern
        try:
            regex = re.compile(search_pattern, re.IGNORECASE)
        except re.error:
            # If the pattern is not a valid regex, search for it as a literal string
            regex = re.compile(re.escape(search_pattern), re.IGNORECASE)
        
        results_count = 0
        for file_path in matching_files:
            if os.path.isfile(file_path):
                try:
                    with open(file_path, 'r', errors='replace') as file:
                        lines = file.readlines()
                    
                    file_results = []
                    for i, line in enumerate(lines, 1):
                        matches = regex.finditer(line)
                        for match in matches:
                            file_results.append((i, line.strip(), match.span()))
                    
                    if file_results:
                        print(f"\nFile: {file_path}")
                        print("-" * 40)
                        for line_num, line_text, span in file_results:
                            start, end = span
                            print(f"Line {line_num}: {line_text[:start]}\033[1;31m{line_text[start:end]}\033[0m{line_text[end:]}")
                        
                        results_count += len(file_results)
                except Exception as e:
                    print(f"Error reading {file_path}: {str(e)}")
        
        print("=" * 50)
        if results_count > 0:
            print(f"\nFound {results_count} occurrences in {len(matching_files)} files.")
        else:
            print(f"\nNo matches found in {len(matching_files)} files.")
        
        return results_count > 0
    except Exception as e:
        print(f"Error searching files: {str(e)}")
        return False

def compare_files(file1, file2):
    """Compare two files and show the differences."""
    if not os.path.exists(file1):
        print(f"Error: File '{file1}' does not exist.")
        return False
        
    if not os.path.exists(file2):
        print(f"Error: File '{file2}' does not exist.")
        return False
    
    try:
        import difflib
        
        print(f"\nComparing '{file1}' and '{file2}':\n")
        print("=" * 50)
        
        with open(file1, 'r', errors='replace') as f1, open(file2, 'r', errors='replace') as f2:
            file1_lines = f1.readlines()
            file2_lines = f2.readlines()
        
        # Create a differ object
        differ = difflib.Differ()
        diff = list(differ.compare(file1_lines, file2_lines))
        
        # Print the diff
        for line in diff:
            if line.startswith('+ '):
                print(f"\033[1;32m{line}\033[0m", end='')  # Green for additions
            elif line.startswith('- '):
                print(f"\033[1;31m{line}\033[0m", end='')  # Red for removals
            elif line.startswith('? '):
                print(f"\033[1;36m{line}\033[0m", end='')  # Cyan for information
            else:
                print(line, end='')
        
        print("\n" + "=" * 50)
        print(f"\nComparison complete.")
        return True
    except Exception as e:
        print(f"Error comparing files: {str(e)}")
        return False


    cursor: pointer;
    border-radius: 5px;
    text-decoration: none;
}

.btn:hover {
    background: #555;
}
"""
    elif template_type.lower() == 'json':
        content = """{
    "name": "Project Name",
    "version": "1.0.0",
    "description": "Project description",
    "author": "Your Name",
    "created": "CURRENT_DATE",
    "main": "index.js",
    "properties": {
        "property1": "value1",
        "property2": "value2"
    },
    "items": [
        "item1", 
        "item2", 
        "item3"
    ]
}""".replace("CURRENT_DATE", time.strftime("%Y-%m-%d"))
    elif template_type.lower() == 'markdown' or template_type.lower() == 'md':
        content = f"""# Title

Created: {time.strftime("%Y-%m-%d")}

## Introduction

Write your introduction here.

## Main Content

- Point 1
- Point 2
- Point 3

## Conclusion

Write your conclusion here.
"""
    else:
        content = f"# New file created by PyWrite\n# Date: {time.strftime('%Y-%m-%d')}\n\n"
    
    try:
        with open(filename, 'w') as file:
            file.write(content)
        print(f"Created file: {filename}")
        return True
    except Exception as e:
        print(f"Error creating file: {str(e)}")
        return False

def copy_file(source, destination):
    """Copy a file from source to destination."""
    if not os.path.exists(source):
        print(f"Error: Source file '{source}' does not exist.")
        return False
    
    try:
        with open(source, 'r') as src_file:
            content = src_file.read()
        
        with open(destination, 'w') as dest_file:
            dest_file.write(content)
        
        print(f"Copied '{source}' to '{destination}'")
        return True
    except Exception as e:
        print(f"Error copying file: {str(e)}")
        return False

def concatenate_files(input_files, output_file, separator="\n\n"):
    """Concatenate multiple files into one output file."""
    if not input_files:
        print("Error: No input files specified.")
        return False
    
    try:
        combined_content = ""
        
        for filename in input_files:
            if not os.path.exists(filename):
                print(f"Warning: File '{filename}' does not exist and will be skipped.")
                continue
                
            with open(filename, 'r') as file:
                file_content = file.read()
                combined_content += file_content
                
                # Add separator if this isn't the last file
                if filename != input_files[-1]:
                    combined_content += separator
        
        with open(output_file, 'w') as out_file:
            out_file.write(combined_content)
            
        print(f"Successfully concatenated {len(input_files)} files into '{output_file}'")
        return True
    except Exception as e:
        print(f"Error concatenating files: {str(e)}")
        return False

def append_content(filename, content):
    """Append content to a file."""
    try:
        with open(filename, 'a') as file:
            file.write(content + "\n")
        print(f"Content appended to '{filename}'")
        return True
    except Exception as e:
        print(f"Error appending to file: {str(e)}")
        return False

def print_usage():
    """Display program usage information."""
    print("\nUsage:")
    print("  python simple_editor.py view <filename> [line-range]  - View a file with optional line range")
    print("  python simple_editor.py list [directory] [pattern]    - List files matching pattern")
    print("  python simple_editor.py run <filename.py>             - Run a Python file")
    print("  python simple_editor.py create <filename> [template]  - Create file from template")
    print("  python simple_editor.py copy <source> <destination>   - Copy a file")
    print("  python simple_editor.py cat <output> <input1> [input2 ...]  - Concatenate files")
    print("  python simple_editor.py search <pattern> [directory]  - Search for text in files")
    print("  python simple_editor.py compare <file1> <file2>       - Compare two files")
    print("\nExamples:")
    print("  python simple_editor.py view sample.txt 10-20")
    print("  python simple_editor.py list sample_novel *.txt")
    print("  python simple_editor.py create script.py python")
    print("  python simple_editor.py create page.html html")
    print("  python simple_editor.py create style.css css")
    print("  python simple_editor.py create app.js javascript")
    print("  python simple_editor.py create data.json json")
    print("  python simple_editor.py copy file1.txt file2.txt")
    print("  python simple_editor.py cat combined.txt file1.txt file2.txt file3.txt")
    print("  python simple_editor.py search \"function\" *.js")
    print("  python simple_editor.py compare file1.txt file2.txt")

def main():
    """Main function to parse arguments and execute commands."""
    print_banner()
    
    parser = argparse.ArgumentParser(description='PyWrite Simple File Editor', add_help=False)
    parser.add_argument('command', nargs='?', default='help')
    parser.add_argument('args', nargs='*', help='Command arguments')
    
    args = parser.parse_args()
    command = args.command.lower()
    arguments = args.args
    
    try:
        if command == 'view' and len(arguments) >= 1:
            if len(arguments) > 1:
                view_file(arguments[0], arguments[1])
            else:
                view_file(arguments[0])
                
        elif command == 'list':
            if len(arguments) >= 2:
                list_files(arguments[0], arguments[1])
            elif len(arguments) == 1:
                list_files(arguments[0])
            else:
                list_files()
                
        elif command == 'run' and len(arguments) >= 1:
            run_python_file(arguments[0])
            
        elif command == 'create' and len(arguments) >= 1:
            template = arguments[1] if len(arguments) > 1 else 'python'
            create_from_template(arguments[0], template)
            
        elif command == 'copy' and len(arguments) >= 2:
            copy_file(arguments[0], arguments[1])
            
        elif command == 'cat' and len(arguments) >= 2:
            output_file = arguments[0]
            input_files = arguments[1:]
            concatenate_files(input_files, output_file)
            
        elif command == 'search' and len(arguments) >= 1:
            pattern = arguments[0]
            if len(arguments) >= 2:
                search_in_files(pattern, '.', arguments[1])
            else:
                search_in_files(pattern)
                
        elif command == 'compare' and len(arguments) >= 2:
            compare_files(arguments[0], arguments[1])
            
        else:
            print_usage()
            
    except Exception as e:
        print(f"Error: {str(e)}")
        print_usage()

if __name__ == "__main__":
    main()