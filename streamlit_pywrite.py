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
                                output += "\n\nErrors:\n" + result.stderr
                                
                            st.session_state.output = output
                        except subprocess.TimeoutExpired:
                            st.session_state.output = "Error: Code execution timed out after 10 seconds."
                        
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

# Footer
st.markdown("---")
st.markdown("PyWrite Code Editor - Created with Streamlit")