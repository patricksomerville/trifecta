import streamlit as st
import os
import tempfile
import utils
import styles

# Page configuration
st.set_page_config(
    page_title="PyWrite Editor",
    page_icon="🐍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS
st.markdown(styles.get_css(), unsafe_allow_html=True)

# Initialize session state
if 'content' not in st.session_state:
    st.session_state.content = "# Enter your Python code here\n\ndef hello_world():\n    print('Hello, World!')\n\n# Write your code here"
if 'current_file' not in st.session_state:
    st.session_state.current_file = None
if 'app_theme' not in st.session_state:
    st.session_state.app_theme = "light"  # Default app theme

def toggle_app_theme():
    if st.session_state.app_theme == "light":
        st.session_state.app_theme = "dark"
    else:
        st.session_state.app_theme = "light"

# Display the header with logo
col1, col2 = st.columns([1, 5])
with col1:
    st.markdown(styles.get_logo_svg(), unsafe_allow_html=True)
with col2:
    st.title("PyWrite Editor")

# Sidebar for file operations and settings
with st.sidebar:
    st.markdown("## File Operations")
    
    # New file button
    if st.button("New File", key="new_file"):
        st.session_state.content = ""
        st.session_state.current_file = None
        st.success("Created new file")
    
    # Open file
    uploaded_file = st.file_uploader("Open File", type=["py", "txt", "md"])
    if uploaded_file is not None:
        st.session_state.content = uploaded_file.getvalue().decode("utf-8")
        st.session_state.current_file = uploaded_file.name
        st.success(f"Opened {uploaded_file.name}")
    
    # Save file functionality
    st.markdown("### Save File")
    file_name = st.text_input("File Name", value=st.session_state.current_file if st.session_state.current_file else "untitled.py")
    
    if st.button("Save", key="save_file"):
        if st.session_state.content:
            utils.save_file(file_name, st.session_state.content)
            st.session_state.current_file = file_name
            st.success(f"Saved as {file_name}")
        else:
            st.error("Nothing to save")
    
    # Settings
    st.markdown("## Settings")
    
    # App theme toggle
    theme_label = "🌙 Dark Mode" if st.session_state.app_theme == "light" else "☀️ Light Mode"
    if st.button(theme_label):
        toggle_app_theme()
        st.experimental_rerun()
    
    # Display keyboard shortcuts
    st.markdown("## Keyboard Shortcuts")
    st.markdown("""
    - `Tab`: Indent
    - `Shift+Tab`: Outdent
    - Use the provided buttons for other operations
    """)

# Main editor area
st.markdown(f"### {'Untitled' if not st.session_state.current_file else st.session_state.current_file}")

# Apply dark theme CSS if needed
if st.session_state.app_theme == "dark":
    st.markdown(styles.get_dark_mode_css(), unsafe_allow_html=True)

# Create a simple editor with a text area
content = st.text_area(
    "Edit your code here",
    value=st.session_state.content,
    height=400,
    key="text_editor"
)

# Add some basic editor features
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("Format Code"):
        try:
            import autopep8
            st.session_state.content = autopep8.fix_code(content)
            st.experimental_rerun()
        except ImportError:
            st.session_state.content = content
            st.warning("Code formatting requires autopep8 package")

with col2:
    if st.button("Clear Editor"):
        st.session_state.content = ""
        st.experimental_rerun()
        
with col3:
    language = utils.get_extension_language(st.session_state.current_file)
    st.write(f"Language: {language}")

# Update session state with current content
st.session_state.content = content

# Basic Python linting and error highlighting
if content:
    linting_result = utils.lint_python_code(content)
    if linting_result:
        with st.expander("Code Issues"):
            for issue in linting_result:
                st.markdown(f"**Line {issue['line']}:** {issue['message']}")

# Execute code section
with st.expander("Run Code"):
    if st.button("Execute Code"):
        output = utils.execute_python_code(st.session_state.content)
        st.code(output, language="bash")

# Footer
st.markdown("""
<div class="footer">
    <p>PyWrite Editor - A Streamlit-powered Python code editor</p>
</div>
""", unsafe_allow_html=True)