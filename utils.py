import os
import sys
import tempfile
import base64
import subprocess
import streamlit as st
import ast
import traceback
from io import StringIO

def save_file(file_name, content):
    """
    Save content to a file and provide it as a download
    """
    with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.py') as tmp:
        tmp.write(content)
    
    with open(tmp.name, 'rb') as f:
        bytes_data = f.read()
    
    # Create a download button for the file
    st.download_button(
        label=f"Download {file_name}",
        data=bytes_data,
        file_name=file_name,
        mime="text/plain"
    )

def lint_python_code(code):
    """
    Basic Python linting to identify syntax errors
    """
    issues = []
    
    # Check for syntax errors
    try:
        ast.parse(code)
    except SyntaxError as e:
        issues.append({
            'line': e.lineno,
            'col': e.offset,
            'message': f"Syntax error: {str(e)}"
        })
        return issues
    
    # More advanced linting could be added here
    
    return issues

def execute_python_code(code):
    """
    Execute the Python code and return the output
    """
    # Capture stdout and stderr
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    redirected_output = sys.stdout = StringIO()
    redirected_error = sys.stderr = StringIO()
    
    result = ""
    
    try:
        # Create a temporary file to execute
        with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.py') as tmp:
            tmp.write(code)
            tmp_name = tmp.name
        
        # Run the code in a subprocess for safety
        process = subprocess.run(
            [sys.executable, tmp_name],
            capture_output=True,
            text=True,
            timeout=10  # Timeout after 10 seconds
        )
        
        # Get output
        result = process.stdout
        if process.stderr:
            result += "\n" + process.stderr
            
        # Clean up
        os.unlink(tmp_name)
            
    except subprocess.TimeoutExpired:
        result = "Execution timed out after 10 seconds."
    except Exception as e:
        result = f"Error: {str(e)}"
        traceback.print_exc()
    finally:
        # Restore stdout and stderr
        sys.stdout = old_stdout
        sys.stderr = old_stderr
        
        # Get any output from the StringIO objects
        if redirected_output.getvalue() or redirected_error.getvalue():
            additional_output = redirected_output.getvalue() + redirected_error.getvalue()
            if additional_output and not result:
                result = additional_output
    
    return result

def get_extension_language(file_name):
    """
    Determine the language based on file extension
    """
    if not file_name:
        return "python"
        
    extension = file_name.split('.')[-1].lower()
    extension_map = {
        'py': 'python',
        'js': 'javascript',
        'html': 'html',
        'css': 'css',
        'json': 'json',
        'md': 'markdown',
        'txt': 'text'
    }
    
    return extension_map.get(extension, 'python')
