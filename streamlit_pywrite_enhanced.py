"""
PyWrite Enhanced Code Editor with Streamlit
A Streamlit-based code editor with integrated autocomplete, file management, and automation features

Author: PyWrite
Date: 2025-03-28
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
import uuid
import threading
import tempfile
from datetime import datetime
from streamlit_ace import st_ace
from typing import Dict, List, Any, Optional

# Import PyWrite modules
from database_helper import get_db_instance
from autocomplete_engine import AutocompleteEngine
from automation_manager import get_automation_manager
try:
    from comment_assistant import analyze_code_file, generate_improved_file
except ImportError:
    def analyze_code_file(file_path):
        st.warning("Comment assistant module not available")
        return {"missing_docstrings": 0, "summary": ""}
    
    def generate_improved_file(file_path):
        st.warning("Comment assistant module not available")
        return ""

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
    .code-suggestion {
        background-color: #e8f4ff;
        border-left: 3px solid #2196F3;
        padding: 8px;
        margin: 5px 0;
        font-family: monospace;
        border-radius: 3px;
    }
    .automation-card {
        background-color: #f9f9f9;
        border: 1px solid #ddd;
        border-radius: 5px;
        padding: 10px;
        margin-bottom: 10px;
    }
    .automation-active {
        border-left: 4px solid #4CAF50;
    }
    .automation-inactive {
        border-left: 4px solid #FF5722;
    }
    .suggestion-card {
        background-color: #e1f5fe;
        border-radius: 5px;
        padding: 10px;
        margin-bottom: 10px;
        cursor: pointer;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'file_content' not in st.session_state:
    st.session_state.file_content = ""
if 'current_file' not in st.session_state:
    st.session_state.current_file = None
if 'editor_language' not in st.session_state:
    st.session_state.editor_language = "python"
if 'cursor_position' not in st.session_state:
    st.session_state.cursor_position = 0
if 'suggestions' not in st.session_state:
    st.session_state.suggestions = []
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if 'automation_status' not in st.session_state:
    st.session_state.automation_status = "stopped"
if 'last_saved_content' not in st.session_state:
    st.session_state.last_saved_content = ""
if 'db_initialized' not in st.session_state:
    st.session_state.db_initialized = False
if 'auto_save_enabled' not in st.session_state:
    st.session_state.auto_save_enabled = True
if 'auto_complete_enabled' not in st.session_state:
    st.session_state.auto_complete_enabled = True
if 'auto_improve_enabled' not in st.session_state:
    st.session_state.auto_improve_enabled = False
if 'output_content' not in st.session_state:
    st.session_state.output_content = ""
if 'recent_files' not in st.session_state:
    st.session_state.recent_files = []
if 'snippets' not in st.session_state:
    st.session_state.snippets = []
if 'continuous_coding_active' not in st.session_state:
    st.session_state.continuous_coding_active = False

# Initialize database and services
@st.cache_resource
def initialize_services():
    """Initialize database and related services."""
    try:
        # Initialize database
        db = get_db_instance()
        
        # Initialize autocomplete engine
        autocomplete = AutocompleteEngine()
        
        # Initialize automation manager
        automation = get_automation_manager()
        
        # Set up automation event handlers
        def file_saved_handler(data):
            # Log activity
            file_path = data.get('file_path', '')
            db.log_activity(
                st.session_state.session_id,
                'file_saved',
                {'file_path': file_path}
            )
            
            # Learn patterns from the saved file
            if file_path.endswith('.py'):
                autocomplete.learn_from_file(file_path, 'python')
        
        # Register event handlers
        automation.register_event_handler('file_saved', file_saved_handler)
        
        return {
            "db": db,
            "autocomplete": autocomplete,
            "automation": automation,
            "initialized": True
        }
    except Exception as e:
        st.error(f"Error initializing services: {str(e)}")
        return {
            "db": None,
            "autocomplete": None,
            "automation": None,
            "initialized": False
        }

# Initialize services
services = initialize_services()

# Start automation manager if needed
if services["initialized"] and st.session_state.automation_status == "stopped":
    try:
        services["automation"].start()
        st.session_state.automation_status = "running"
    except Exception as e:
        st.error(f"Error starting automation: {str(e)}")


# Utility Functions

def get_file_language(filename):
    """Determine the language based on file extension."""
    _, ext = os.path.splitext(filename)
    if ext == '.py':
        return 'python'
    elif ext in ['.js', '.jsx']:
        return 'javascript'
    elif ext == '.html':
        return 'html'
    elif ext == '.css':
        return 'css'
    elif ext in ['.json', '.jsonl']:
        return 'json'
    elif ext == '.md':
        return 'markdown'
    elif ext in ['.sh', '.bash']:
        return 'sh'
    elif ext in ['.yml', '.yaml']:
        return 'yaml'
    else:
        return 'text'

def load_file(filepath):
    """Load a file into the editor."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        st.session_state.file_content = content
        st.session_state.current_file = filepath
        st.session_state.editor_language = get_file_language(filepath)
        st.session_state.last_saved_content = content
        
        # Add to recent files
        if filepath not in st.session_state.recent_files:
            st.session_state.recent_files.insert(0, filepath)
            # Keep only the 10 most recent files
            st.session_state.recent_files = st.session_state.recent_files[:10]
        
        # Log activity
        if services["db"]:
            services["db"].log_activity(
                st.session_state.session_id,
                'file_opened',
                {'file_path': filepath}
            )
        
        return True
    except Exception as e:
        st.error(f"Error loading file: {str(e)}")
        return False

def save_file(filepath, content):
    """Save content to a file."""
    try:
        # Create directories if they don't exist
        directory = os.path.dirname(filepath)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        st.session_state.last_saved_content = content
        
        # Trigger saved event
        if services["automation"]:
            services["automation"].trigger_event(
                'file_saved', 
                {'file_path': filepath}
            )
        
        return True
    except Exception as e:
        st.error(f"Error saving file: {str(e)}")
        return False

def run_python_file(filepath):
    """Run a Python file and capture the output."""
    try:
        result = subprocess.run(
            ['python', filepath],
            capture_output=True,
            text=True,
            timeout=10  # 10 second timeout
        )
        
        output = f"Exit code: {result.returncode}\n\n"
        
        if result.stdout:
            output += f"=== STDOUT ===\n{result.stdout}\n"
        
        if result.stderr:
            output += f"=== STDERR ===\n{result.stderr}\n"
        
        st.session_state.output_content = output
        
        # Log activity
        if services["db"]:
            services["db"].log_activity(
                st.session_state.session_id,
                'file_executed',
                {'file_path': filepath, 'exit_code': result.returncode}
            )
        
        return output
    except subprocess.TimeoutExpired:
        return "Error: Execution timed out (> 10 seconds)"
    except Exception as e:
        return f"Error executing file: {str(e)}"

def get_autocomplete_suggestions(code, language, cursor_position):
    """Get autocomplete suggestions for the current code position."""
    if not services["autocomplete"]:
        return []
    
    try:
        # Get file content if available
        file_content = ""
        if st.session_state.current_file and os.path.exists(st.session_state.current_file):
            with open(st.session_state.current_file, 'r', encoding='utf-8') as f:
                file_content = f.read()
        
        # Get completion suggestions
        suggestions = services["autocomplete"].get_completions(
            language=language,
            current_code=code,
            cursor_position=cursor_position,
            file_content=file_content,
            filename=st.session_state.current_file
        )
        
        return suggestions
    except Exception as e:
        st.error(f"Error getting suggestions: {str(e)}")
        return []

def create_snippet_from_selection(name, code, language):
    """Create a new code snippet from selected text."""
    if not services["autocomplete"]:
        return False
    
    try:
        # Add the snippet
        snippet_id = services["autocomplete"].add_snippet(
            name=name,
            language=language,
            code=code,
            description=f"Created from editor selection"
        )
        
        # Refresh snippets
        load_snippets()
        
        return bool(snippet_id)
    except Exception as e:
        st.error(f"Error creating snippet: {str(e)}")
        return False

def load_snippets():
    """Load code snippets from the database."""
    if not services["db"]:
        return []
    
    try:
        # Get snippets for the current language
        language = st.session_state.editor_language
        snippets = services["db"].search_snippets(language=language, limit=20)
        
        st.session_state.snippets = snippets
        return snippets
    except Exception as e:
        st.error(f"Error loading snippets: {str(e)}")
        return []

def toggle_automation_task(task_id, is_active):
    """Toggle an automation task on or off."""
    if not services["automation"]:
        return False
    
    try:
        success = services["automation"].toggle_task(task_id, is_active)
        return success
    except Exception as e:
        st.error(f"Error toggling automation: {str(e)}")
        return False

def add_automation_task(task_name, task_type, trigger, action):
    """Add a new automation task."""
    if not services["automation"]:
        return None
    
    try:
        task_id = services["automation"].add_automation_task(
            task_name=task_name,
            task_type=task_type,
            trigger=trigger,
            action=action
        )
        return task_id
    except Exception as e:
        st.error(f"Error adding automation: {str(e)}")
        return None

def trigger_continuous_coding():
    """Start or stop continuous coding mode."""
    st.session_state.continuous_coding_active = not st.session_state.continuous_coding_active
    
    # Enable or disable related automation tasks
    if services["automation"]:
        if st.session_state.continuous_coding_active:
            # Enable auto-improve task if it exists
            if "Auto-improve Code" in services["automation"].tasks:
                services["automation"].toggle_task("Auto-improve Code", True)
        else:
            # Disable auto-improve task if it exists
            if "Auto-improve Code" in services["automation"].tasks:
                services["automation"].toggle_task("Auto-improve Code", False)


# UI Layout

# Define the top menu
menu_col1, menu_col2, menu_col3 = st.columns([1, 3, 1])

with menu_col1:
    st.image("assets/logo.svg", width=80)

with menu_col2:
    st.title("PyWrite Code Editor")

with menu_col3:
    st.write("")
    enable_mode = st.checkbox("Continuous Coding Mode", value=st.session_state.continuous_coding_active, on_change=trigger_continuous_coding)

# Layout with sidebar and main content
col1, col2 = st.columns([1, 3])

# Sidebar for file management and settings
with col1:
    st.header("File Management")
    
    # File operations tab
    tab1, tab2, tab3 = st.tabs(["Files", "Settings", "Automation"])
    
    with tab1:
        # File actions
        file_action = st.selectbox(
            "Action",
            ["Open File", "New File", "Recent Files"]
        )
        
        if file_action == "Open File":
            # File pattern filter
            file_pattern = st.text_input("Filter", "*.py", help="Glob pattern for filtering files")
            
            # List files
            files = sorted(glob.glob(file_pattern))
            if not files:
                st.info("No files match the pattern")
            else:
                st.write(f"Found {len(files)} files:")
                file_list = st.container(height=300)
                with file_list:
                    for f in files:
                        if st.button(f, key=f"open_{f}"):
                            load_file(f)
                            st.rerun()
        
        elif file_action == "New File":
            file_options = st.columns([3, 2])
            with file_options[0]:
                new_filename = st.text_input("Filename", "new_file.py")
            with file_options[1]:
                file_type = st.selectbox(
                    "Type",
                    ["Python", "JavaScript", "HTML", "CSS", "JSON", "Text"]
                )
            
            # Templates
            templates = {
                "Python": """#!/usr/bin/env python3
# -*- coding: utf-8 -*-
\"\"\"
Description: A Python script
Author: PyWrite
Date: {date}
\"\"\"

def main():
    \"\"\"Main function.\"\"\"
    print("Hello, World!")
    
    # Your code here

if __name__ == "__main__":
    main()
""",
                "JavaScript": """/**
 * Description: A JavaScript file
 * Author: PyWrite
 * Date: {date}
 */

function main() {
    console.log("Hello, World!");
    
    // Your code here
}

main();
""",
                "HTML": """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>New Document</title>
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
    <!-- Your content here -->
    
    <script>
        // Your JavaScript here
    </script>
</body>
</html>
""",
                "CSS": """/**
 * Description: CSS Stylesheet
 * Author: PyWrite
 * Date: {date}
 */

body {
    font-family: Arial, sans-serif;
    margin: 0;
    padding: 0;
    background-color: #f5f5f5;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

/* Your styles here */
""",
                "JSON": """{
    "name": "PyWrite Project",
    "version": "1.0.0",
    "description": "A project created with PyWrite",
    "created_at": "{date}",
    "author": "PyWrite",
    "settings": {
        "theme": "light",
        "auto_save": true
    },
    "data": [
        {
            "id": 1,
            "value": "Sample data"
        }
    ]
}
""",
                "Text": """PyWrite Document
Created: {date}

Your text content here.
"""
            }
            
            # Calculate template content
            template_type = file_type.lower()
            template = templates.get(file_type, "").format(date=datetime.now().strftime("%Y-%m-%d"))
            
            if st.button("Create File"):
                if os.path.exists(new_filename):
                    st.warning(f"File '{new_filename}' already exists. Choose a different name.")
                else:
                    if save_file(new_filename, template):
                        st.success(f"Created file: {new_filename}")
                        load_file(new_filename)
                        st.rerun()
        
        elif file_action == "Recent Files":
            if not st.session_state.recent_files:
                st.info("No recent files")
            else:
                st.write("Recent files:")
                file_list = st.container(height=300)
                with file_list:
                    for f in st.session_state.recent_files:
                        if st.button(f, key=f"recent_{f}"):
                            load_file(f)
                            st.rerun()
        
        # Show save button if a file is loaded
        if st.session_state.current_file:
            if st.button("Save", key="save_button"):
                if save_file(st.session_state.current_file, st.session_state.file_content):
                    st.success(f"Saved: {st.session_state.current_file}")
    
    with tab2:
        # Settings
        st.subheader("Editor Settings")
        
        st.session_state.auto_save_enabled = st.checkbox(
            "Auto-save",
            value=st.session_state.auto_save_enabled,
            help="Automatically save changes when code is modified"
        )
        
        st.session_state.auto_complete_enabled = st.checkbox(
            "Auto-complete",
            value=st.session_state.auto_complete_enabled,
            help="Show code completion suggestions"
        )
        
        st.session_state.auto_improve_enabled = st.checkbox(
            "Auto-improve",
            value=st.session_state.auto_improve_enabled,
            help="Automatically improve code with documentation"
        )
        
        # Theme selection
        theme = st.selectbox(
            "Editor Theme",
            ["github", "monokai", "tomorrow", "kuroir", "twilight", "xcode", "solarized_dark", "terminal"],
            index=0
        )
        
        # Font size
        font_size = st.slider("Font Size", min_value=12, max_value=24, value=14, step=1)
        
        # Tab size
        tab_size = st.slider("Tab Size", min_value=2, max_value=8, value=4, step=1)
    
    with tab3:
        # Automation
        st.subheader("Automation Tasks")
        
        # Add a new automation task
        with st.expander("Add New Task"):
            task_name = st.text_input("Task Name", "New Task")
            task_type = st.selectbox(
                "Task Type",
                ["file_watcher", "timer", "continuous_processor"]
            )
            
            # Different options based on task type
            if task_type == "file_watcher":
                directory = st.text_input("Directory", ".")
                patterns = st.text_input("File Patterns", "*.py")
                action_type = st.selectbox(
                    "Action",
                    ["learn_patterns", "analyze_code"]
                )
                
                if st.button("Add File Watcher"):
                    task_id = add_automation_task(
                        task_name=task_name,
                        task_type="file_watcher",
                        trigger="file_modified",
                        action={
                            "directory": directory,
                            "patterns": patterns.split(','),
                            "action_type": action_type
                        }
                    )
                    if task_id:
                        st.success(f"Added file watcher: {task_name}")
            
            elif task_type == "timer":
                interval = st.number_input("Interval (seconds)", min_value=10, value=60)
                module = st.text_input("Module Name", "comment_assistant")
                function = st.text_input("Function Name", "analyze_code_file")
                
                if st.button("Add Timer Task"):
                    task_id = add_automation_task(
                        task_name=task_name,
                        task_type="timer",
                        trigger="timer",
                        action={
                            "interval": interval,
                            "action_type": "run_function",
                            "module": module,
                            "function": function
                        }
                    )
                    if task_id:
                        st.success(f"Added timer task: {task_name}")
            
            elif task_type == "continuous_processor":
                processor_type = st.selectbox(
                    "Processor Type",
                    ["code_improver", "snippet_collector"]
                )
                directory = st.text_input("Directory", ".")
                patterns = st.text_input("File Patterns", "*.py")
                interval = st.number_input("Interval (seconds)", min_value=30, value=300)
                
                if st.button("Add Processor"):
                    task_id = add_automation_task(
                        task_name=task_name,
                        task_type="continuous_processor",
                        trigger="interval",
                        action={
                            "processor_type": processor_type,
                            "directory": directory,
                            "patterns": patterns.split(','),
                            "interval": interval,
                            "max_files": 5
                        }
                    )
                    if task_id:
                        st.success(f"Added processor: {task_name}")
        
        # List existing tasks
        st.subheader("Active Tasks")
        if services["automation"]:
            tasks = services["automation"].tasks
            if not tasks:
                st.info("No automation tasks configured")
            else:
                for task_name, task in tasks.items():
                    is_active = task.get('is_active', False)
                    task_type = task.get('type', 'unknown')
                    
                    with st.container():
                        cols = st.columns([3, 1, 1])
                        with cols[0]:
                            st.markdown(f"**{task_name}** ({task_type})")
                        with cols[1]:
                            status = "Active" if is_active else "Inactive"
                            status_color = "green" if is_active else "red"
                            st.markdown(f"<span style='color:{status_color};'>{status}</span>", unsafe_allow_html=True)
                        with cols[2]:
                            if is_active:
                                if st.button("Stop", key=f"stop_{task_name}"):
                                    toggle_automation_task(task_name, False)
                                    st.rerun()
                            else:
                                if st.button("Start", key=f"start_{task_name}"):
                                    toggle_automation_task(task_name, True)
                                    st.rerun()

# Main content area
with col2:
    # Display current file info
    if st.session_state.current_file:
        st.subheader(f"Editing: {st.session_state.current_file}")
    else:
        st.subheader("No file loaded")
    
    # Code editor
    editor_col, info_col = st.columns([3, 1])
    
    with editor_col:
        # Code editor
        content = st_ace(
            value=st.session_state.file_content,
            language=st.session_state.editor_language,
            theme=theme if 'theme' in locals() else "github",
            font_size=font_size if 'font_size' in locals() else 14,
            tab_size=tab_size if 'tab_size' in locals() else 4,
            show_gutter=True,
            key="ace_editor",
            height=500
        )
        
        # Update file content when code changes
        if content != st.session_state.file_content:
            st.session_state.file_content = content
            
            # Auto-save if enabled
            if st.session_state.auto_save_enabled and st.session_state.current_file:
                if save_file(st.session_state.current_file, content):
                    st.toast(f"Auto-saved: {st.session_state.current_file}")
        
        # File actions
        action_col1, action_col2, action_col3 = st.columns(3)
        
        with action_col1:
            if st.session_state.current_file:
                if st.button("Run File"):
                    if st.session_state.current_file.endswith('.py'):
                        # Save any changes first
                        save_file(st.session_state.current_file, st.session_state.file_content)
                        # Run the file
                        output = run_python_file(st.session_state.current_file)
                        st.session_state.output_content = output
                    else:
                        st.warning("Can only run Python files")
            
                if st.session_state.file_content != st.session_state.last_saved_content:
                    st.info("File has unsaved changes")
        
        with action_col2:
            if st.session_state.current_file:
                # Analyze and improve code
                if st.button("Analyze Code"):
                    # Save any changes first
                    save_file(st.session_state.current_file, st.session_state.file_content)
                    # Analyze the file
                    try:
                        analysis = analyze_code_file(st.session_state.current_file)
                        st.session_state.analysis_result = analysis
                        st.toast(f"Analysis complete: found {analysis.get('missing_docstrings', 0)} missing docstrings")
                    except Exception as e:
                        st.error(f"Error analyzing code: {str(e)}")
        
        with action_col3:
            if st.session_state.current_file and hasattr(st.session_state, 'analysis_result'):
                if st.button("Improve Code"):
                    try:
                        # Generate improved code
                        improved_code = generate_improved_file(st.session_state.current_file)
                        # Create a backup of the original
                        backup_path = f"{st.session_state.current_file}.bak"
                        save_file(backup_path, st.session_state.file_content)
                        # Save the improved version
                        save_file(st.session_state.current_file, improved_code)
                        # Update the editor
                        st.session_state.file_content = improved_code
                        st.session_state.last_saved_content = improved_code
                        st.toast(f"Code improved and saved (backup at {backup_path})")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error improving code: {str(e)}")
        
        # Output display
        if st.session_state.output_content:
            st.subheader("Output")
            st.text_area(
                "Program Output",
                value=st.session_state.output_content,
                height=200,
                disabled=True,
                key="output_area"
            )
    
    with info_col:
        # Autocomplete and suggestions area
        if st.session_state.auto_complete_enabled:
            st.subheader("Code Assistance")
            
            # Get suggestions based on current content
            if st.session_state.file_content:
                suggestions = get_autocomplete_suggestions(
                    st.session_state.file_content,
                    st.session_state.editor_language,
                    len(st.session_state.file_content)  # Use end of content as cursor position
                )
                
                if suggestions:
                    st.write("Suggestions:")
                    for i, suggestion in enumerate(suggestions[:5]):
                        with st.container():
                            st.markdown(f"<div class='code-suggestion'>{suggestion['display_text']}</div>", unsafe_allow_html=True)
                            if st.button("Insert", key=f"insert_{i}"):
                                # In a real implementation, we would insert at cursor position
                                # but streamlit_ace doesn't expose cursor position
                                # Instead, we append to the end as an example
                                st.session_state.file_content += f"\n{suggestion['text']}"
                                st.rerun()
            
            # Create snippet from selection
            with st.expander("Create Snippet"):
                snippet_name = st.text_input("Snippet Name", "my_snippet")
                snippet_code = st.text_area("Code", height=100)
                
                if st.button("Save Snippet"):
                    if snippet_code and snippet_name:
                        language = st.session_state.editor_language
                        if create_snippet_from_selection(snippet_name, snippet_code, language):
                            st.success(f"Created snippet: {snippet_name}")
                            st.rerun()
            
            # Show available snippets
            with st.expander("Code Snippets"):
                # Load snippets if empty
                if not st.session_state.snippets:
                    load_snippets()
                
                if not st.session_state.snippets:
                    st.info("No snippets available for this language")
                else:
                    for snippet in st.session_state.snippets:
                        with st.container():
                            st.markdown(f"<strong>{snippet['name']}</strong>", unsafe_allow_html=True)
                            code_preview = snippet['code'][:100] + "..." if len(snippet['code']) > 100 else snippet['code']
                            st.code(code_preview, language=snippet['language'])
                            if st.button("Insert", key=f"insert_snippet_{snippet['id']}"):
                                # In a real implementation, we would insert at cursor position
                                st.session_state.file_content += f"\n{snippet['code']}"
                                st.rerun()
        
        # Show information about code analysis if available
        if hasattr(st.session_state, 'analysis_result'):
            with st.expander("Code Analysis", expanded=True):
                analysis = st.session_state.analysis_result
                
                st.write(f"File summary: {analysis.get('summary', 'No summary available')}")
                st.write(f"Missing docstrings: {analysis.get('missing_docstrings', 0)}")
                
                if 'complex_functions' in analysis and analysis['complex_functions']:
                    st.write("Complex functions:")
                    for func in analysis['complex_functions']:
                        st.write(f"- {func}")
        
        # Show continuous coding status if active
        if st.session_state.continuous_coding_active:
            with st.container():
                st.markdown("""
                <div style="background-color: #e8f5e9; padding: 10px; border-radius: 5px; border-left: 4px solid #4CAF50;">
                <h4 style="margin: 0; color: #2E7D32;">Continuous Coding Active</h4>
                <p>PyWrite is automatically improving your code</p>
                </div>
                """, unsafe_allow_html=True)

# Add a status bar at the bottom
status_col1, status_col2, status_col3 = st.columns(3)

with status_col1:
    st.write(f"Current mode: {st.session_state.editor_language}")

with status_col2:
    if st.session_state.current_file:
        st.write(f"Current file: {os.path.basename(st.session_state.current_file)}")
    else:
        st.write("No file loaded")

with status_col3:
    automation_status = "Active" if st.session_state.automation_status == "running" else "Inactive"
    st.write(f"Automation: {automation_status}")


# Main function when run directly
if __name__ == "__main__":
    pass