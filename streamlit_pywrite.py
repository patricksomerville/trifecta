"""
PyWrite Code Editor with Streamlit
A Streamlit-based code editor with integrated file management and commenting features
"""

import streamlit as st
import os
import glob
import json
import time
import re
import difflib
import subprocess
import traceback
import requests
from streamlit_ace import st_ace
from comment_assistant import analyze_code_file, generate_improved_file

# Set page configuration
st.set_page_config(
    page_title="PyWrite Code Editor",
    page_icon="✏️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        background-color: #f5f5f5;
    }
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    .file-list {
        max-height: 400px;
        overflow-y: auto;
        border: 1px solid #ddd;
        border-radius: 5px;
        padding: 10px;
    }
    .output-area {
        background-color: #f0f0f0;
        border-radius: 5px;
        padding: 10px;
        font-family: monospace;
        min-height: 100px;
        max-height: 400px;
        overflow-y: auto;
    }
    .comment-area {
        background-color: #f8f8f8;
        border-radius: 5px;
        padding: 10px;
        border: 1px solid #ddd;
    }
    .header-area {
        background-color: #4A6572;
        padding: 20px;
        color: white;
        border-radius: 5px;
        margin-bottom: 20px;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #F0F2F6;
        border-radius: 4px 4px 0px 0px;
        gap: 1px;
        padding: 10px 16px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #4A6572;
        color: white;
    }
    .button-container {
        display: flex;
        gap: 10px;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'file_content' not in st.session_state:
    st.session_state.file_content = ""
if 'current_file' not in st.session_state:
    st.session_state.current_file = None
if 'output' not in st.session_state:
    st.session_state.output = ""
if 'directory' not in st.session_state:
    st.session_state.directory = "."
if 'file_pattern' not in st.session_state:
    st.session_state.file_pattern = "*.*"
if 'search_results' not in st.session_state:
    st.session_state.search_results = ""
if 'diff_results' not in st.session_state:
    st.session_state.diff_results = ""
if 'template_type' not in st.session_state:
    st.session_state.template_type = "python"
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None
if 'improved_content' not in st.session_state:
    st.session_state.improved_content = ""
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False
if 'has_error' not in st.session_state:
    st.session_state.has_error = False
if 'error_text' not in st.session_state:
    st.session_state.error_text = ""
if 'debug_suggestions' not in st.session_state:
    st.session_state.debug_suggestions = ""
if 'learning_mode' not in st.session_state:
    st.session_state.learning_mode = False
if 'pattern_explanation' not in st.session_state:
    st.session_state.pattern_explanation = ""
if 'last_analyzed_code' not in st.session_state:
    st.session_state.last_analyzed_code = ""

# Header
with st.container():
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("""
        <div class="header-area">
            <h1>PyWrite Code Editor</h1>
            <p>A powerful code editor with file management and AI-powered commenting</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        dark_mode = st.toggle("Dark Mode", value=st.session_state.dark_mode)
        if dark_mode != st.session_state.dark_mode:
            st.session_state.dark_mode = dark_mode
            st.rerun()
        
        learning_mode = st.toggle("Learning Mode 🧠", value=st.session_state.learning_mode)
        if learning_mode != st.session_state.learning_mode:
            st.session_state.learning_mode = learning_mode
            st.rerun()

# Main layout
col1, col2 = st.columns([1, 2])

# File management sidebar
with col1:
    st.subheader("File Management")
    
    # Directory and file pattern selection
    dir_col, pattern_col = st.columns(2)
    with dir_col:
        directory = st.text_input("Directory", value=st.session_state.directory)
    with pattern_col:
        file_pattern = st.text_input("Pattern", value=st.session_state.file_pattern)
    
    if directory != st.session_state.directory or file_pattern != st.session_state.file_pattern:
        st.session_state.directory = directory
        st.session_state.file_pattern = file_pattern
    
    # File list
    st.markdown("### Files")
    try:
        search_path = os.path.join(directory, file_pattern)
        files = glob.glob(search_path, recursive=True)
        files = [f for f in files if os.path.isfile(f)]
        files.sort()
        
        if files:
            selected_file = st.selectbox("Select a file", files)
            
            if selected_file != st.session_state.current_file:
                try:
                    with open(selected_file, 'r', encoding='utf-8', errors='replace') as file:
                        st.session_state.file_content = file.read()
                    st.session_state.current_file = selected_file
                except Exception as e:
                    st.error(f"Error reading file: {str(e)}")
        else:
            st.info(f"No files found matching '{file_pattern}' in '{directory}'")
    except Exception as e:
        st.error(f"Error accessing files: {str(e)}")
    
    # File operations
    st.markdown("### Operations")
    
    # New file creation
    new_file_name = st.text_input("New file name")
    template_types = ["python", "html", "css", "javascript", "json", "markdown", "yaml"]
    template_type = st.selectbox("Template type", template_types, index=template_types.index(st.session_state.template_type))
    
    if template_type != st.session_state.template_type:
        st.session_state.template_type = template_type
    
    if st.button("Create New File") and new_file_name:
        try:
            # Generate template content based on type
            current_date = time.strftime("%Y-%m-%d")
            
            if template_type == "python":
                content = f'''"""
Description: A Python script
Author: PyWrite
Date: {current_date}
"""

def main():
    """Main function."""
    print("Hello, World!")

if __name__ == "__main__":
    main()
'''
            elif template_type == "html":
                content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <header>
        <h1>My Website</h1>
    </header>
    
    <main>
        <p>Welcome to my website!</p>
    </main>
    
    <footer>
        <p>&copy; {time.strftime("%Y")} PyWrite</p>
    </footer>
    
    <script src="script.js"></script>
</body>
</html>
'''
            elif template_type == "css":
                content = f'''/**
 * CSS Stylesheet
 * Author: PyWrite
 * Date: {current_date}
 */

/* Reset some default styles */
* {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}}

body {{
    font-family: 'Arial', sans-serif;
    line-height: 1.6;
    color: #333;
    background-color: #f4f4f4;
    padding: 20px;
}}

/* Container */
.container {{
    width: 80%;
    max-width: 1200px;
    margin: 0 auto;
    overflow: hidden;
}}

/* Typography */
h1, h2, h3 {{
    margin-bottom: 15px;
    color: #333;
}}

p {{
    margin-bottom: 15px;
}}

/* Buttons */
.btn {{
    display: inline-block;
    padding: 10px 20px;
    background: #333;
    color: #fff;
    border: none;
    cursor: pointer;
    border-radius: 5px;
    text-decoration: none;
}}

.btn:hover {{
    background: #555;
}}
'''
            elif template_type == "javascript":
                content = f'''/**
 * JavaScript module
 * Author: PyWrite
 * Date: {current_date}
 */

// Main function
function main() {{
    console.log("Hello, World!");
    
    // Your code here
}}

// Event listener for DOM loading
document.addEventListener('DOMContentLoaded', function() {{
    main();
}});

// Export functions if using modules
export {{ main }};
'''
            elif template_type == "json":
                content = f'''{{
    "name": "Project Name",
    "version": "1.0.0",
    "description": "Project description",
    "author": "Your Name",
    "created": "{current_date}",
    "main": "index.js",
    "properties": {{
        "property1": "value1",
        "property2": "value2"
    }},
    "items": [
        "item1", 
        "item2", 
        "item3"
    ]
}}'''
            elif template_type == "markdown":
                content = f'''# Title

Created: {current_date}

## Introduction

Write your introduction here.

## Main Content

- Point 1
- Point 2
- Point 3

## Conclusion

Write your conclusion here.

## References

* [Reference 1](https://example.com)
* [Reference 2](https://example.com)
'''
            elif template_type == "yaml":
                content = f'''# YAML Configuration File
# Created: {current_date}

version: '1.0'

application:
  name: ApplicationName
  description: Application description
  environment: development

database:
  host: localhost
  port: 5432
  username: user
  password: password
  database: dbname

server:
  port: 8080
  timeout: 30
  max_connections: 100
  
logging:
  level: info
  file: logs/app.log
  max_size: 10MB
  backup_count: 5
'''
            else:
                content = f"# New file created by PyWrite\n# Date: {current_date}\n\n"
                
            # Write the file
            with open(new_file_name, 'w', encoding='utf-8') as file:
                file.write(content)
                
            st.success(f"Created new file: {new_file_name}")
            
            # Update the file list and select the new file
            st.session_state.file_content = content
            st.session_state.current_file = new_file_name
            st.rerun()
        except Exception as e:
            st.error(f"Error creating file: {str(e)}")
    
    # File search
    st.markdown("### Search in Files")
    search_term = st.text_input("Search term")
    search_col1, search_col2 = st.columns(2)
    with search_col1:
        search_dir = st.text_input("Search directory", value=".")
    with search_col2:
        search_pattern = st.text_input("Search file pattern", value="*.*")
    
    if st.button("Search") and search_term:
        try:
            st.session_state.search_results = ""
            search_path = os.path.join(search_dir, search_pattern)
            matching_files = glob.glob(search_path, recursive=True)
            matching_files = [f for f in matching_files if os.path.isfile(f)]
            matching_files.sort()
            
            # Compile the search pattern
            try:
                regex = re.compile(search_term, re.IGNORECASE)
            except re.error:
                # If the pattern is not a valid regex, search for it as a literal string
                regex = re.compile(re.escape(search_term), re.IGNORECASE)
            
            results = []
            for file_path in matching_files:
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='replace') as file:
                        lines = file.readlines()
                    
                    file_results = []
                    for i, line in enumerate(lines, 1):
                        if regex.search(line):
                            file_results.append((i, line.strip()))
                    
                    if file_results:
                        results.append((file_path, file_results))
                except Exception as e:
                    st.session_state.search_results += f"Error reading {file_path}: {str(e)}\n"
            
            # Format results
            if results:
                for file_path, file_results in results:
                    st.session_state.search_results += f"\nFile: {file_path}\n"
                    st.session_state.search_results += "-" * 40 + "\n"
                    for line_num, line_text in file_results:
                        st.session_state.search_results += f"Line {line_num}: {line_text}\n"
                
                st.session_state.search_results += f"\nFound matches in {len(results)} files."
            else:
                st.session_state.search_results = f"No matches found for '{search_term}' in {len(matching_files)} files."
        except Exception as e:
            st.session_state.search_results = f"Error searching files: {str(e)}"
    
    # File comparison
    st.markdown("### Compare Files")
    comp_col1, comp_col2 = st.columns(2)
    with comp_col1:
        file1 = st.text_input("File 1")
    with comp_col2:
        file2 = st.text_input("File 2")
    
    if st.button("Compare") and file1 and file2:
        try:
            if not os.path.exists(file1):
                st.session_state.diff_results = f"Error: File '{file1}' does not exist."
            elif not os.path.exists(file2):
                st.session_state.diff_results = f"Error: File '{file2}' does not exist."
            else:
                with open(file1, 'r', encoding='utf-8', errors='replace') as f1, open(file2, 'r', encoding='utf-8', errors='replace') as f2:
                    file1_lines = f1.readlines()
                    file2_lines = f2.readlines()
                
                differ = difflib.Differ()
                diff = list(differ.compare(file1_lines, file2_lines))
                
                st.session_state.diff_results = f"Comparing '{file1}' and '{file2}':\n\n"
                st.session_state.diff_results += "".join(diff)
        except Exception as e:
            st.session_state.diff_results = f"Error comparing files: {str(e)}"

# Editor and output area
with col2:
    tabs = st.tabs(["Editor", "Run Output", "Search Results", "Compare Results", "Comment Analysis"])
    
    # Tab 1: Editor
    with tabs[0]:
        st.markdown("### Code Editor")
        
        # Language detection based on file extension
        language = "python"
        if st.session_state.current_file:
            ext = os.path.splitext(st.session_state.current_file)[1].lower()
            if ext == ".py":
                language = "python"
            elif ext == ".js":
                language = "javascript"
            elif ext == ".html":
                language = "html"
            elif ext == ".css":
                language = "css"
            elif ext == ".json":
                language = "json"
            elif ext in [".md", ".markdown"]:
                language = "markdown"
            elif ext in [".yml", ".yaml"]:
                language = "yaml"
        
        # Editor theme based on dark mode
        theme = "twilight" if st.session_state.dark_mode else "github"
        
        # Code editor
        editor_content = st_ace(
            value=st.session_state.file_content,
            language=language,
            theme=theme,
            height=500,
            key="editor"
        )
        
        # Only update if content changed
        if editor_content != st.session_state.file_content:
            st.session_state.file_content = editor_content
            
            # Learning Mode - analyze code patterns when content changes
            if st.session_state.learning_mode and language == "python":
                # Check if code has changed significantly (at least 10 characters)
                if (not st.session_state.last_analyzed_code or 
                    abs(len(editor_content) - len(st.session_state.last_analyzed_code)) > 10):
                    
                    # In a production app, this would call an AI API
                    # Here we'll use pattern matching for demonstration
                    
                    # Reset explanation
                    st.session_state.pattern_explanation = ""
                    
                    # Look for common Python patterns to explain
                    patterns_to_detect = [
                        {
                            "pattern": r"with\s+\w+\([^)]*\)\s+as\s+\w+:",
                            "name": "Context Manager (with statement)",
                            "explanation": """
### Context Manager Pattern

The `with` statement creates a context manager that automatically handles setup and cleanup actions.

#### Benefits:
- Automatically manages resources (like file handles)
- Ensures proper cleanup even if exceptions occur
- Makes code cleaner and more readable

#### Common uses:
- File operations
- Database connections
- Network connections
- Thread locks

#### Example:
```python
# Instead of:
f = open('file.txt', 'r')
content = f.read()
f.close()  # Must remember to close!

# Better approach:
with open('file.txt', 'r') as f:
    content = f.read()
# File is automatically closed when the block exits
```
"""
                        },
                        {
                            "pattern": r"if\s+__name__\s*==\s*['\"]__main__['\"]:",
                            "name": "Main Function Pattern",
                            "explanation": """
### Main Function Pattern

The `if __name__ == "__main__":` pattern allows a Python file to be both imported as a module and run as a script.

#### Benefits:
- Code only runs when directly executed, not when imported
- Encourages modular design
- Makes testing easier

#### Best practices:
- Place all executable code inside functions or classes
- Use this pattern to call a `main()` function
- Keep the script-specific code separate from reusable logic

#### Example:
```python
def main():
    # Main program logic here
    print("Running as script")

if __name__ == "__main__":
    main()
```
"""
                        },
                        {
                            "pattern": r"try\s*:.+?except(\s+\w+)?(\s+as\s+\w+)?:",
                            "name": "Exception Handling",
                            "explanation": """
### Exception Handling Pattern

The `try/except` block handles errors gracefully, preventing program crashes.

#### Benefits:
- Prevents program termination due to errors
- Allows graceful degradation
- Enables custom error handling

#### Best practices:
- Catch specific exceptions, not all exceptions
- Keep the try block as small as possible
- Always include error reporting or logging
- Use `finally` for cleanup that must always happen

#### Example:
```python
try:
    result = risky_operation()
except ValueError as e:
    print(f"Invalid value: {e}")
except FileNotFoundError:
    print("The required file was not found")
except Exception as e:
    print(f"Unexpected error: {e}")
    raise  # Re-raise unexpected errors
finally:
    # This always runs
    cleanup_resources()
```
"""
                        },
                        {
                            "pattern": r"def\s+\w+\s*\(\s*self\s*,",
                            "name": "Class Method",
                            "explanation": """
### Class Method Pattern

Methods with `self` as the first parameter are instance methods in a class.

#### Key concepts:
- `self` refers to the instance of the class
- Each instance has its own set of instance variables
- Instance methods can access and modify instance state

#### Best practices:
- Always use `self` as the first parameter name (convention)
- Use descriptive method names (verb phrases)
- Follow the single responsibility principle

#### Example:
```python
class User:
    def __init__(self, name, email):
        self.name = name
        self.email = email
        
    def send_message(self, message):
        print(f"Sending '{message}' to {self.name} at {self.email}")
        
    def update_email(self, new_email):
        self.email = new_email
```
"""
                        },
                        {
                            "pattern": r"@\w+",
                            "name": "Decorator Pattern",
                            "explanation": """
### Decorator Pattern

Decorators (@symbol) modify or enhance functions without changing their code.

#### Benefits:
- Adds functionality to functions or methods
- Keeps the code DRY (Don't Repeat Yourself)
- Separates cross-cutting concerns

#### Common uses:
- Authentication/authorization
- Logging and timing
- Caching
- Input validation
- Rate limiting

#### Example:
```python
# Timing decorator example
import time

def timer(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"{func.__name__} ran in {end_time - start_time:.4f} seconds")
        return result
    return wrapper

@timer
def slow_function():
    time.sleep(1)
    return "Function complete"
```
"""
                        },
                        {
                            "pattern": r"for\s+\w+\s+in\s+\w+:",
                            "name": "Iteration Pattern",
                            "explanation": """
### Iteration Pattern

The `for` loop in Python is used to iterate over sequences (lists, tuples, strings, etc.)

#### Key concepts:
- Iterates over any iterable object
- More Pythonic than traditional counting loops
- Can be combined with enumerate() for index tracking

#### Best practices:
- Use meaningful variable names in the loop
- Consider list comprehensions for simple transformations
- Use `enumerate()` when you need indices
- Use `zip()` to iterate over multiple sequences in parallel

#### Example:
```python
# Simple iteration
for item in my_list:
    print(item)

# With index
for i, item in enumerate(my_list):
    print(f"Item {i}: {item}")
    
# Parallel iteration
for name, age in zip(names, ages):
    print(f"{name} is {age} years old")
    
# List comprehension (alternative to for loop)
squares = [x**2 for x in numbers]
```
"""
                        },
                        {
                            "pattern": r"lambda\s+\w+(\s*,\s*\w+)*\s*:",
                            "name": "Lambda Function",
                            "explanation": """
### Lambda Function Pattern

Lambda functions are small anonymous functions defined with the `lambda` keyword.

#### Benefits:
- Create simple functions without formal definition
- Useful for short operations
- Common in functional programming patterns

#### Best practices:
- Keep lambda functions simple and short
- Use named functions for complex operations
- Commonly used with `map()`, `filter()`, and `sorted()`

#### Example:
```python
# Sort by second element in tuples
data = [(1, 5), (3, 2), (2, 8)]
sorted_data = sorted(data, key=lambda x: x[1])
# Result: [(3, 2), (1, 5), (2, 8)]

# Filter even numbers
numbers = [1, 2, 3, 4, 5, 6]
even = list(filter(lambda x: x % 2 == 0, numbers))
# Result: [2, 4, 6]

# Map to squares
squares = list(map(lambda x: x**2, numbers))
# Result: [1, 4, 9, 16, 25, 36]
```
"""
                        },
                    ]
                    
                    # Check if any patterns match
                    for pattern_info in patterns_to_detect:
                        if re.search(pattern_info["pattern"], editor_content, re.DOTALL):
                            st.session_state.pattern_explanation = {
                                "name": pattern_info["name"],
                                "explanation": pattern_info["explanation"]
                            }
                            break
                    
                    # Update last analyzed code
                    st.session_state.last_analyzed_code = editor_content
        
        # Action buttons
        save_col, run_col, comment_col = st.columns(3)
        
        with save_col:
            if st.button("Save File") and st.session_state.current_file:
                try:
                    with open(st.session_state.current_file, 'w', encoding='utf-8') as file:
                        file.write(editor_content)
                    st.success(f"Saved to {st.session_state.current_file}")
                except Exception as e:
                    st.error(f"Error saving file: {str(e)}")
        
        with run_col:
            if st.button("Run Code") and st.session_state.current_file:
                try:
                    # Only run Python files
                    if language == "python":
                        # Create a temporary file to ensure we run the latest code
                        temp_filename = f"temp_{int(time.time())}.py"
                        with open(temp_filename, 'w', encoding='utf-8') as temp_file:
                            temp_file.write(editor_content)
                        
                        # Run the code and capture output
                        try:
                            result = subprocess.run(
                                ["python", temp_filename],
                                capture_output=True,
                                text=True,
                                timeout=10  # Timeout after 10 seconds
                            )
                            
                            output = result.stdout
                            if result.stderr:
                                error_text = result.stderr
                                output += "\n\nErrors:\n" + error_text
                                
                                # Add Smart Debugging button if error detected
                                st.session_state.has_error = True
                                st.session_state.error_text = error_text
                            else:
                                st.session_state.has_error = False
                                
                            st.session_state.output = output
                        except subprocess.TimeoutExpired:
                            st.session_state.output = "Error: Code execution timed out after 10 seconds."
                            st.session_state.has_error = True
                            st.session_state.error_text = "Code execution timed out after 10 seconds."
                        
                        # Clean up the temporary file
                        try:
                            os.remove(temp_filename)
                        except:
                            pass
                    else:
                        st.session_state.output = "Only Python files can be executed."
                except Exception as e:
                    st.session_state.output = f"Error running code: {str(e)}"
        
        with comment_col:
            analyze_comment_col, improve_comment_col = st.columns(2)
            
            with analyze_comment_col:
                if st.button("Analyze Comments") and st.session_state.current_file:
                    try:
                        # Save current content to a temporary file
                        temp_filename = f"temp_{int(time.time())}.py"
                        with open(temp_filename, 'w', encoding='utf-8') as temp_file:
                            temp_file.write(editor_content)
                        
                        # Analyze the file
                        st.session_state.analysis_results = analyze_code_file(temp_filename)
                        
                        # Clean up the temporary file
                        try:
                            os.remove(temp_filename)
                        except:
                            pass
                    except Exception as e:
                        st.error(f"Error analyzing file: {str(e)}")
            
            with improve_comment_col:
                if st.button("Improve Comments") and st.session_state.current_file:
                    try:
                        # Save current content to a temporary file
                        temp_filename = f"temp_{int(time.time())}.py"
                        with open(temp_filename, 'w', encoding='utf-8') as temp_file:
                            temp_file.write(editor_content)
                        
                        # Generate improved content
                        st.session_state.improved_content = generate_improved_file(temp_filename)
                        
                        # Clean up the temporary file
                        try:
                            os.remove(temp_filename)
                        except:
                            pass
                        
                        # Show the results in the Comment Analysis tab
                        st.success("Comments improved! View in the Comment Analysis tab.")
                    except Exception as e:
                        st.error(f"Error improving file: {str(e)}")
        
    # Tab 2: Run Output
    with tabs[1]:
        st.markdown("### Execution Output")
        st.code(st.session_state.output, language="text")
        
        # Smart Debugging Feature
        if st.session_state.has_error:
            st.markdown("### 🔍 Smart Debugging")
            
            if st.button("Analyze Error and Suggest Fix"):
                with st.spinner("Analyzing error and generating suggestions..."):
                    try:
                        # In a production app, you would use the OpenAI API
                        # import openai
                        # client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
                        
                        prompt = f"""
                        You are an expert Python developer. Analyze this error and code to provide debugging help:
                        
                        CODE:
                        ```python
                        {st.session_state.file_content}
                        ```
                        
                        ERROR:
                        ```
                        {st.session_state.error_text}
                        ```
                        
                        Provide a clear explanation of:
                        1. What the error means
                        2. Why it's occurring
                        3. How to fix it with specific code suggestions
                        4. Best practices to avoid this issue in the future
                        """
                        
                        # In a production app with API:
                        # response = client.chat.completions.create(
                        #     model="gpt-4",
                        #     messages=[{"role": "user", "content": prompt}],
                        #     temperature=0.3,
                        # )
                        # debug_suggestions = response.choices[0].message.content
                        
                        # Simulated response for demonstration
                        debug_suggestions = f"""## Error Analysis

Based on the error message, it appears you're encountering a **{st.session_state.error_text.split(':')[0] if ':' in st.session_state.error_text else 'Python Error'}**.

### What's happening:
The Python interpreter found an issue in your code that prevented it from executing.

### Likely causes:
1. Syntax error (missing colons, brackets, etc.)
2. Undefined variable or function
3. Type mismatch in operations
4. Indentation issues

### Suggested fixes:
```python
# Look for these patterns in your code:
# 1. Check variable definitions before use
if variable_name is not None:
    # use variable_name

# 2. Verify function parameters
def function_name(required_param):
    # function body

# 3. Ensure proper exception handling
try:
    # risky code
except Exception as e:
    print(f"Error: {e}")
```

### Best practices:
- Use a linter like flake8 or pylint
- Implement type hints
- Write tests for your functions
- Use a debugger to step through code
"""
                        
                        st.session_state.debug_suggestions = debug_suggestions
                        
                    except Exception as e:
                        st.error(f"Error analyzing code: {str(e)}")
            
            if st.session_state.debug_suggestions:
                st.markdown(st.session_state.debug_suggestions)
    
    # Tab 3: Search Results
    with tabs[2]:
        st.markdown("### Search Results")
        st.code(st.session_state.search_results, language="text")
    
    # Tab 4: Compare Results
    with tabs[3]:
        st.markdown("### File Comparison")
        st.code(st.session_state.diff_results, language="text")
    
    # Tab 5: Comment Analysis
    with tabs[4]:
        st.markdown("### Comment Analysis")
        
        if st.session_state.analysis_results:
            with st.expander("Analysis Results", expanded=True):
                # Display analysis results
                analysis = st.session_state.analysis_results
                
                if "error" in analysis:
                    st.error(f"Error: {analysis['error']}")
                else:
                    st.markdown(f"**File type:** {analysis['type']}")
                    st.markdown(f"**Summary:** {analysis['file_summary']}")
                    
                    if "missing_docstrings" in analysis:
                        st.markdown(f"**Missing docstrings:** {len(analysis['missing_docstrings'])}")
                        for item in analysis['missing_docstrings']:
                            st.markdown(f"- {item['type'].capitalize()} '{item['name']}' at line {item['line']}")
                    
                    if "complex_functions" in analysis:
                        st.markdown(f"**Complex functions:** {len(analysis['complex_functions'])}")
                        for func in analysis['complex_functions']:
                            st.markdown(f"- Function '{func['name']}' at line {func['line']} (complexity: {func['complexity']})")
                    
                    suggested_comments = analysis.get("suggested_comments", {})
                    if suggested_comments:
                        st.markdown(f"**Suggested inline comments:** {len(suggested_comments)}")
                        for line, comment in suggested_comments.items():
                            st.markdown(f"- Line {line}: {comment}")
        
        if st.session_state.improved_content:
            with st.expander("Improved Code with Comments", expanded=True):
                # Display improved content
                st.code(st.session_state.improved_content, language="python")
                
                if st.button("Apply Improved Comments"):
                    # Update editor content with improved version
                    st.session_state.file_content = st.session_state.improved_content
                    
                    # Save the improved version
                    try:
                        with open(st.session_state.current_file, 'w', encoding='utf-8') as file:
                            file.write(st.session_state.improved_content)
                        st.success(f"Updated {st.session_state.current_file} with improved comments!")
                    except Exception as e:
                        st.error(f"Error saving improved file: {str(e)}")
                    
                    # Refresh to show updated content in editor
                    st.rerun()
                    
    # Tab 6: Four Horsemen (Orchestration Engine)
    with tabs[5:]:
        st.markdown("### 🏇 The Four Horsemen")
        st.markdown("""
        <div style="background-color: #2E4057; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
            <h3 style="color: white;">Parallel AI Agent Orchestration</h3>
            <p style="color: white;">Unleash the power of multiple AI systems working in parallel on different aspects of your code</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Initialize orchestration session state if not exist
        if 'orchestration_tasks' not in st.session_state:
            st.session_state.orchestration_tasks = []
            
        if 'orchestration_results' not in st.session_state:
            st.session_state.orchestration_results = {}
            
        # Display orchestration panel
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("### Assign Tasks")
            
            # File selection for orchestration
            orchestration_file = st.text_input("Target File", value=st.session_state.current_file if st.session_state.current_file else "")
            
            # Task selection for each agent
            st.markdown("#### Agent Assignments")
            
            # The Four Horsemen and their specialties
            horsemen = {
                "Conquest (OpenAI)": ["Optimize Algorithm", "Refactor Code", "Add Type Hints", "Extend Functionality"],
                "War (Replit Assistant)": ["Debug Code", "Fix Bugs", "Add Error Handling", "Improve Security"],
                "Famine (Replit Agent)": ["Optimize Performance", "Reduce Resource Usage", "Improve Efficiency", "Memory Optimization"],
                "Death (Code Reviewer)": ["Identify Code Smells", "Check Best Practices", "Review Logic", "Ensure Standards"]
            }
            
            selected_tasks = {}
            for horseman, tasks in horsemen.items():
                st.markdown(f"**{horseman}**")
                selected_tasks[horseman] = st.selectbox(
                    f"Task for {horseman}", 
                    ["Not Assigned"] + tasks,
                    key=f"task_{horseman}"
                )
            
            # Priority settings
            priority_mode = st.radio(
                "Orchestration Mode",
                ["Sequential", "Parallel", "Prioritized"],
                index=1
            )
            
            # Launch orchestration
            if st.button("🚀 Launch Orchestration"):
                if orchestration_file and any(task != "Not Assigned" for task in selected_tasks.values()):
                    # Clear previous results
                    st.session_state.orchestration_tasks = []
                    st.session_state.orchestration_results = {}
                    
                    # Add selected tasks
                    for horseman, task in selected_tasks.items():
                        if task != "Not Assigned":
                            st.session_state.orchestration_tasks.append({
                                "agent": horseman,
                                "task": task,
                                "file": orchestration_file,
                                "status": "pending",
                                "start_time": time.time()
                            })
                    
                    # Simulate orchestration process (in real implementation, this would trigger actual API calls)
                    for i, task in enumerate(st.session_state.orchestration_tasks):
                        task["status"] = "running"
                        
                        # Add a simulated result after a delay (in real implementation this would be the actual result)
                        # Simply updating the session state here since we're just demonstrating the concept
                        st.session_state.orchestration_results[f"{task['agent']}_{task['task']}"] = {
                            "summary": f"Completed {task['task']} on {task['file']}",
                            "changes": [
                                f"Improvement 1 related to {task['task']}",
                                f"Improvement 2 related to {task['task']}",
                                f"Improvement 3 related to {task['task']}",
                            ],
                            "completion_time": time.time() + (i * 2) # Simulating different completion times
                        }
                        
                        task["status"] = "completed"
                    
                    st.success("Orchestration launched successfully!")
                    st.rerun()
                else:
                    st.error("Please select a file and at least one task to proceed")
        
        with col2:
            st.markdown("### Orchestration Dashboard")
            
            # Display tasks and their status
            if st.session_state.orchestration_tasks:
                for task in st.session_state.orchestration_tasks:
                    status_color = {
                        "pending": "🟡",
                        "running": "🔵",
                        "completed": "🟢",
                        "failed": "🔴"
                    }.get(task["status"], "⚪")
                    
                    st.markdown(f"{status_color} **{task['agent']}**: {task['task']} - *{task['status']}*")
                
                # Display results of completed tasks
                st.markdown("### Results")
                
                for task in st.session_state.orchestration_tasks:
                    if task["status"] == "completed":
                        result_key = f"{task['agent']}_{task['task']}"
                        if result_key in st.session_state.orchestration_results:
                            result = st.session_state.orchestration_results[result_key]
                            
                            with st.expander(f"{task['agent']}: {task['task']}"):
                                st.markdown(f"**Summary**: {result['summary']}")
                                st.markdown("**Changes**:")
                                for change in result['changes']:
                                    st.markdown(f"- {change}")
                                
                                # Add apply button (in a real implementation, this would apply the changes)
                                if st.button(f"Apply changes from {task['agent']}", key=f"apply_{result_key}"):
                                    st.success(f"Applied changes from {task['agent']} - {task['task']}")
            else:
                st.info("No orchestration tasks have been launched yet")
        
        # Documentation of the orchestration system
        with st.expander("About The Four Horsemen"):
            st.markdown("""
            ### The Four Horsemen Orchestration System
            
            This system allows you to leverage multiple AI agents simultaneously, each specialized in different aspects of code improvement:
            
            1. **Conquest (OpenAI)** - Focuses on code structure and features
            2. **War (Replit Assistant)** - Specializes in debugging and fixing issues
            3. **Famine (Replit Agent)** - Optimizes performance and resource usage
            4. **Death (Code Reviewer)** - Ensures code quality and best practices
            
            #### How to use:
            1. Select a target file
            2. Assign specific tasks to each agent
            3. Choose orchestration mode (Sequential, Parallel, or Prioritized)
            4. Launch the orchestration
            5. Review and apply the changes from each agent
            
            This parallel processing approach significantly improves efficiency when working on complex codebases.
            """)

# Footer
st.markdown("---")
st.markdown("PyWrite Code Editor - Created with Streamlit")