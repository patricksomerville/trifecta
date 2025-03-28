"""
PyWrite Roadmap Planning System

A Streamlit-based interface for creating and managing project roadmaps,
planning before coding, and generating code scaffolding based on plans.

Author: PyWrite
Date: 2025-03-28
"""

import streamlit as st
import os
import json
import datetime
import tempfile
import uuid
import re
from typing import Dict, List, Any, Optional, Tuple

# Import PyWrite modules
from project_roadmap import (
    ProjectRoadmap, RoadmapPhase, get_roadmap_manager
)
try:
    from database_helper import get_db_instance
    from continuous_coding import get_continuous_coding_engine
    has_enhanced_features = True
except ImportError:
    has_enhanced_features = False

# Set page configuration
st.set_page_config(
    page_title="PyWrite Roadmap Planning",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
    }
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    .roadmap-title {
        font-weight: bold;
        margin-bottom: 5px;
    }
    .roadmap-description {
        color: #6c757d;
        font-size: 0.9em;
        margin-bottom: 10px;
    }
    .phase-card {
        background-color: #ffffff;
        border-radius: 8px;
        padding: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 15px;
    }
    .phase-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 10px;
    }
    .phase-title {
        font-weight: bold;
        font-size: 1.1em;
    }
    .phase-description {
        color: #6c757d;
        font-size: 0.9em;
        margin-bottom: 10px;
    }
    .status-planned {
        background-color: #e9ecef;
        color: #495057;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 0.8em;
    }
    .status-in_progress {
        background-color: #cff4fc;
        color: #055160;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 0.8em;
    }
    .status-completed {
        background-color: #d1e7dd;
        color: #0f5132;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 0.8em;
    }
    .status-blocked {
        background-color: #f8d7da;
        color: #842029;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 0.8em;
    }
    .item-card {
        background-color: #f8f9fa;
        border-left: 3px solid #6c757d;
        padding: 8px 12px;
        margin: 5px 0;
        border-radius: 0 4px 4px 0;
    }
    .item-card.requirement {
        border-left-color: #0d6efd;
    }
    .item-card.component {
        border-left-color: #6610f2;
    }
    .item-card.task {
        border-left-color: #fd7e14;
    }
    .priority-high {
        color: #dc3545;
        font-weight: bold;
    }
    .priority-medium {
        color: #fd7e14;
    }
    .priority-low {
        color: #6c757d;
    }
    .code-template {
        background-color: #f1f3f5;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        cursor: pointer;
    }
    .code-template:hover {
        background-color: #e9ecef;
    }
    .section-title {
        font-weight: bold;
        margin: 15px 0 10px 0;
        padding-bottom: 5px;
        border-bottom: 1px solid #dee2e6;
    }
    .template-preview {
        font-family: monospace;
        background-color: #f8f9fa;
        padding: 10px;
        border-radius: 4px;
        margin-top: 5px;
        white-space: pre-wrap;
        font-size: 0.9em;
    }
    .drag-indicator {
        color: #adb5bd;
        cursor: move;
        padding-right: 10px;
    }
    .tags-container {
        display: flex;
        flex-wrap: wrap;
        gap: 5px;
        margin: 5px 0;
    }
    .tag {
        background-color: #e9ecef;
        color: #495057;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.8em;
    }
    .generate-button {
        background-color: #0d6efd;
        color: white;
        padding: 10px 15px;
        border-radius: 4px;
        font-weight: bold;
        text-align: center;
        margin: 15px 0;
        cursor: pointer;
    }
    .generate-button:hover {
        background-color: #0b5ed7;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'user_id' not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())
if 'current_roadmap' not in st.session_state:
    st.session_state.current_roadmap = None
if 'roadmap_list' not in st.session_state:
    st.session_state.roadmap_list = []
if 'current_phase_id' not in st.session_state:
    st.session_state.current_phase_id = None
if 'code_templates' not in st.session_state:
    st.session_state.code_templates = []
if 'generated_code' not in st.session_state:
    st.session_state.generated_code = {}
if 'has_unsaved_changes' not in st.session_state:
    st.session_state.has_unsaved_changes = False

# Initialize the roadmap manager
roadmap_manager = get_roadmap_manager()

# Initialize continuous coding engine if available
if has_enhanced_features:
    try:
        api_key = os.environ.get("OPENAI_API_KEY")
        continuous_coding_engine = get_continuous_coding_engine(api_key)
        has_ai = continuous_coding_engine.has_openai
    except Exception as e:
        st.error(f"Error initializing continuous coding engine: {str(e)}")
        has_ai = False
else:
    has_ai = False

# Function to load roadmap list
def load_roadmap_list():
    """Load list of roadmaps."""
    roadmaps = roadmap_manager.list_roadmaps(user_id=st.session_state.user_id)
    st.session_state.roadmap_list = roadmaps

# Function to load a roadmap
def load_roadmap(roadmap_id):
    """Load a roadmap by ID."""
    roadmap = roadmap_manager.get_roadmap(roadmap_id)
    if roadmap:
        st.session_state.current_roadmap = roadmap
        update_code_templates()
        st.success(f"Loaded roadmap: {roadmap.name}")
        st.session_state.has_unsaved_changes = False
    else:
        st.error("Failed to load roadmap")

# Function to save current roadmap
def save_current_roadmap():
    """Save the current roadmap."""
    if not st.session_state.current_roadmap:
        st.warning("No roadmap to save")
        return
        
    success = roadmap_manager.save_roadmap(
        st.session_state.current_roadmap,
        user_id=st.session_state.user_id
    )
    
    if success:
        st.success("Roadmap saved successfully")
        st.session_state.has_unsaved_changes = False
        load_roadmap_list()
    else:
        st.error("Failed to save roadmap")

# Function to update code templates
def update_code_templates():
    """Update code templates based on current roadmap."""
    if not st.session_state.current_roadmap:
        st.session_state.code_templates = []
        return
        
    templates = st.session_state.current_roadmap.get_suggested_templates()
    st.session_state.code_templates = templates

# Function to generate code from a template
def generate_code_from_template(template, template_name, file_type):
    """Generate code from a template using AI if available."""
    # Store the template content in the session state
    template_key = f"{template_name}_{str(uuid.uuid4())[:8]}"
    
    if has_ai and continuous_coding_engine.has_openai:
        # Get context from the roadmap
        context = st.session_state.current_roadmap.generate_code_context()
        
        # Extract placeholders from template (format: {Placeholder})
        placeholders = re.findall(r'\{([^}]+)\}', template)
        
        # If there are placeholders, we should fill them using AI
        if placeholders:
            try:
                # Build a prompt for generating values for the placeholders
                prompt = f"""
                I'm building a {context['project_type']} project called "{context['project_name']}".
                Project description: {context['description']}
                
                I need to fill in the following placeholders in a code template for {template_name}:
                {', '.join(placeholders)}
                
                The code template is:
                ```
                {template}
                ```
                
                Based on the project context, provide appropriate values for these placeholders.
                Return your response in JSON format, with keys matching the placeholder names
                and values containing the suggested replacements.
                """
                
                # Generate suggestions for the placeholders
                suggestion_json = continuous_coding_engine.openai_client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    response_format={"type": "json_object"}
                )
                
                # Parse the JSON response
                suggestions = json.loads(suggestion_json.choices[0].message.content)
                
                # Replace placeholders in the template
                filled_template = template
                for placeholder, value in suggestions.items():
                    filled_template = filled_template.replace(f"{{{placeholder}}}", value)
                
                # Store the filled template
                st.session_state.generated_code[template_key] = {
                    "name": template_name,
                    "content": filled_template,
                    "file_type": file_type
                }
                
                st.success(f"Generated code for {template_name}")
                return template_key
                
            except Exception as e:
                st.error(f"Error generating code: {str(e)}")
                st.session_state.generated_code[template_key] = {
                    "name": template_name,
                    "content": template,
                    "file_type": file_type
                }
                return template_key
        else:
            # No placeholders, just store the template as is
            st.session_state.generated_code[template_key] = {
                "name": template_name,
                "content": template,
                "file_type": file_type
            }
            return template_key
    else:
        # No AI, just store the template as is
        st.session_state.generated_code[template_key] = {
            "name": template_name,
            "content": template,
            "file_type": file_type
        }
        return template_key

# Function to generate a complete component
def generate_component_code(component_name, component_purpose):
    """Generate code for a component using AI."""
    if not has_ai or not continuous_coding_engine.has_openai:
        st.warning("AI-powered code generation is not available")
        # Return a simple template anyway
        template = f"""
class {component_name}:
    \"\"\"
    {component_purpose}
    \"\"\"
    
    def __init__(self):
        \"\"\"Initialize the component.\"\"\"
        pass
        
    def process(self, data):
        \"\"\"Process data.\"\"\"
        # TODO: Implement processing
        return data
"""
        template_key = f"{component_name}_{str(uuid.uuid4())[:8]}"
        st.session_state.generated_code[template_key] = {
            "name": component_name,
            "content": template,
            "file_type": "python"
        }
        return template_key
        
    # Get context from the roadmap
    context = st.session_state.current_roadmap.generate_code_context()
    
    try:
        # Build a prompt for generating the component
        prompt = f"""
        I'm building a {context['project_type']} project called "{context['project_name']}".
        Project description: {context['project_description']}
        
        I need to implement a component named "{component_name}" with this purpose:
        "{component_purpose}"
        
        Current project phase: {context['current_phase']['name'] if context['current_phase'] else 'Unknown'}
        
        Please generate a Python class for this component with appropriate methods and documentation.
        The code should follow best practices and include detailed docstrings.
        Don't include any imports unless they're absolutely essential.
        """
        
        # Generate code for the component
        response = continuous_coding_engine.openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1000
        )
        
        # Extract the code from the response
        code = response.choices[0].message.content
        
        # If the response contains code blocks, extract the first one
        if "```" in code:
            code_blocks = re.findall(r"```(?:python)?\n(.*?)\n```", code, re.DOTALL)
            if code_blocks:
                code = code_blocks[0]
        
        # Store the generated code
        template_key = f"{component_name}_{str(uuid.uuid4())[:8]}"
        st.session_state.generated_code[template_key] = {
            "name": component_name,
            "content": code,
            "file_type": "python"
        }
        
        st.success(f"Generated code for {component_name}")
        return template_key
        
    except Exception as e:
        st.error(f"Error generating code: {str(e)}")
        # Return a simple template as fallback
        template = f"""
class {component_name}:
    \"\"\"
    {component_purpose}
    \"\"\"
    
    def __init__(self):
        \"\"\"Initialize the component.\"\"\"
        pass
        
    def process(self, data):
        \"\"\"Process data.\"\"\"
        # TODO: Implement processing
        return data
"""
        template_key = f"{component_name}_{str(uuid.uuid4())[:8]}"
        st.session_state.generated_code[template_key] = {
            "name": component_name,
            "content": template,
            "file_type": "python"
        }
        return template_key

# Function to save generated code to file
def save_code_to_file(template_key, filename):
    """Save generated code to a file."""
    if template_key not in st.session_state.generated_code:
        st.error("Code template not found")
        return False
        
    template = st.session_state.generated_code[template_key]
    content = template["content"]
    
    try:
        # Create directories if needed
        directory = os.path.dirname(filename)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
            
        # Write the file
        with open(filename, "w") as f:
            f.write(content)
            
        st.success(f"Saved code to {filename}")
        return True
        
    except Exception as e:
        st.error(f"Error saving file: {str(e)}")
        return False

# Function to create a new roadmap
def create_new_roadmap(name, description, project_type):
    """Create a new roadmap."""
    roadmap = ProjectRoadmap(
        name=name,
        description=description,
        project_type=project_type
    )
    
    st.session_state.current_roadmap = roadmap
    st.session_state.has_unsaved_changes = True
    
    # Save immediately
    save_current_roadmap()
    
    # Update templates
    update_code_templates()
    
    return roadmap

# Function to add a phase to the current roadmap
def add_phase_to_roadmap(name, description, status="planned"):
    """Add a phase to the current roadmap."""
    if not st.session_state.current_roadmap:
        st.error("No roadmap loaded")
        return None
        
    # Get the next order value
    order = len(st.session_state.current_roadmap.phases)
    
    # Add the phase
    phase_id = st.session_state.current_roadmap.add_phase(
        name=name,
        description=description,
        status=status,
        order=order
    )
    
    st.session_state.has_unsaved_changes = True
    
    return phase_id

# Function to delete a phase from the current roadmap
def delete_phase_from_roadmap(phase_id):
    """Delete a phase from the current roadmap."""
    if not st.session_state.current_roadmap:
        st.error("No roadmap loaded")
        return False
        
    # Find the phase
    phase_index = None
    for i, phase in enumerate(st.session_state.current_roadmap.phases):
        if phase.id == phase_id:
            phase_index = i
            break
            
    if phase_index is not None:
        # Remove the phase
        st.session_state.current_roadmap.phases.pop(phase_index)
        
        # Update order values
        for i, phase in enumerate(st.session_state.current_roadmap.phases):
            phase.order = i
            
        st.session_state.has_unsaved_changes = True
        return True
    
    return False

# Function to add a requirement to a phase
def add_requirement_to_phase(phase_id, title, description, req_type, priority):
    """Add a requirement to a phase."""
    if not st.session_state.current_roadmap:
        st.error("No roadmap loaded")
        return None
        
    # Find the phase
    phase = st.session_state.current_roadmap.get_phase(phase_id)
    if not phase:
        st.error("Phase not found")
        return None
        
    # Add the requirement
    req_id = phase.add_requirement(
        title=title,
        description=description,
        requirement_type=req_type,
        priority=priority
    )
    
    st.session_state.has_unsaved_changes = True
    
    return req_id

# Function to add a component to a phase
def add_component_to_phase(phase_id, name, purpose, details, dependencies):
    """Add a component to a phase."""
    if not st.session_state.current_roadmap:
        st.error("No roadmap loaded")
        return None
        
    # Find the phase
    phase = st.session_state.current_roadmap.get_phase(phase_id)
    if not phase:
        st.error("Phase not found")
        return None
        
    # Add the component
    component_id = phase.add_component(
        name=name,
        purpose=purpose,
        implementation_details=details,
        dependencies=dependencies
    )
    
    st.session_state.has_unsaved_changes = True
    
    return component_id

# Function to add a task to a phase
def add_task_to_phase(phase_id, title, description, priority, hours):
    """Add a task to a phase."""
    if not st.session_state.current_roadmap:
        st.error("No roadmap loaded")
        return None
        
    # Find the phase
    phase = st.session_state.current_roadmap.get_phase(phase_id)
    if not phase:
        st.error("Phase not found")
        return None
        
    # Add the task
    task_id = phase.add_task(
        title=title,
        description=description,
        priority=priority,
        estimated_hours=hours
    )
    
    st.session_state.has_unsaved_changes = True
    
    return task_id

# Function to update phase status
def update_phase_status(phase_id, status):
    """Update the status of a phase."""
    if not st.session_state.current_roadmap:
        st.error("No roadmap loaded")
        return False
        
    # Find the phase
    phase = st.session_state.current_roadmap.get_phase(phase_id)
    if not phase:
        st.error("Phase not found")
        return False
        
    # Update the status
    phase.update_status(status)
    
    st.session_state.has_unsaved_changes = True
    
    return True

# Function to reorder phases
def reorder_phases(phase_ids):
    """Reorder phases in the roadmap."""
    if not st.session_state.current_roadmap:
        st.error("No roadmap loaded")
        return False
        
    # Reorder the phases
    success = st.session_state.current_roadmap.reorder_phases(phase_ids)
    
    if success:
        st.session_state.has_unsaved_changes = True
        
    return success

# Function to add a tag to the roadmap
def add_tag_to_roadmap(tag):
    """Add a tag to the roadmap."""
    if not st.session_state.current_roadmap:
        st.error("No roadmap loaded")
        return False
        
    # Add the tag
    st.session_state.current_roadmap.add_tag(tag)
    
    st.session_state.has_unsaved_changes = True
    
    return True

# Initialize by loading roadmap list
if roadmap_manager:
    load_roadmap_list()

# Layout the application
title_col1, title_col2 = st.columns([3, 1])

with title_col1:
    st.title("🗺️ PyWrite Roadmap Planning")
    st.markdown("Plan your project before coding to improve autocomplete and AI assistance.")

with title_col2:
    st.write("")
    st.write("")
    if st.session_state.has_unsaved_changes:
        st.warning("You have unsaved changes")
        if st.button("Save Changes"):
            save_current_roadmap()

# Layout with tabs for different functions
tab1, tab2, tab3, tab4 = st.tabs(["Project Overview", "Phase Details", "Code Generation", "Settings"])

with tab1:
    # Project Overview tab
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Project Selection")
        
        # Create new project section
        with st.expander("Create New Project", expanded=True if not st.session_state.roadmap_list else False):
            new_project_name = st.text_input("Project Name", value="My New Project")
            new_project_description = st.text_area("Project Description", value="A brief description of the project")
            new_project_type = st.selectbox(
                "Project Type",
                ["software", "data", "web", "mobile", "research", "other"]
            )
            
            if st.button("Create Project"):
                roadmap = create_new_roadmap(
                    name=new_project_name,
                    description=new_project_description,
                    project_type=new_project_type
                )
                st.success(f"Created project: {roadmap.name}")
                st.rerun()
        
        # Existing projects list
        st.subheader("Existing Projects")
        if not st.session_state.roadmap_list:
            st.info("No projects found. Create a new one to get started.")
        else:
            for roadmap in st.session_state.roadmap_list:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**{roadmap['name']}**")
                    st.caption(roadmap['description'][:100] + "..." if len(roadmap['description']) > 100 else roadmap['description'])
                with col2:
                    if st.button("Load", key=f"load_{roadmap['id']}"):
                        load_roadmap(roadmap['id'])
                        st.rerun()
    
    with col2:
        # Current project details
        if st.session_state.current_roadmap:
            roadmap = st.session_state.current_roadmap
            
            st.subheader("Current Project")
            
            # Project header
            st.markdown(f"## {roadmap.name}")
            st.markdown(f"*{roadmap.description}*")
            st.markdown(f"**Type:** {roadmap.project_type}")
            
            # Tags
            if roadmap.tags:
                st.markdown("**Tags:**")
                tags_html = '<div class="tags-container">'
                for tag in roadmap.tags:
                    tags_html += f'<span class="tag">{tag}</span>'
                tags_html += '</div>'
                st.markdown(tags_html, unsafe_allow_html=True)
            
            # Add tag
            new_tag = st.text_input("Add Tag")
            if new_tag and st.button("Add Tag"):
                add_tag_to_roadmap(new_tag)
                st.success(f"Added tag: {new_tag}")
                st.rerun()
            
            # Phases overview
            st.subheader("Project Phases")
            
            phases_container = st.container()
            
            with phases_container:
                for phase in roadmap.phases:
                    with st.container():
                        col1, col2, col3 = st.columns([3, 1, 1])
                        
                        with col1:
                            st.markdown(f"**{phase.name}**")
                            st.caption(phase.description[:100] + "..." if len(phase.description) > 100 else phase.description)
                        
                        with col2:
                            status_class = f"status-{phase.status}"
                            st.markdown(f'<span class="{status_class}">{phase.status.replace("_", " ").title()}</span>', unsafe_allow_html=True)
                        
                        with col3:
                            st.button("Details", key=f"details_{phase.id}", on_click=lambda phase_id=phase.id: setattr(st.session_state, 'current_phase_id', phase_id))
            
            # Add new phase
            with st.expander("Add New Phase"):
                phase_name = st.text_input("Phase Name")
                phase_description = st.text_area("Phase Description")
                phase_status = st.selectbox(
                    "Initial Status",
                    ["planned", "in_progress", "completed", "blocked"]
                )
                
                if st.button("Add Phase"):
                    phase_id = add_phase_to_roadmap(
                        name=phase_name,
                        description=phase_description,
                        status=phase_status
                    )
                    st.success(f"Added phase: {phase_name}")
                    save_current_roadmap()
                    st.rerun()
        else:
            st.info("No project loaded. Please create or load a project.")

with tab2:
    # Phase Details tab
    if st.session_state.current_roadmap:
        roadmap = st.session_state.current_roadmap
        
        # Phase selection
        st.subheader("Phase Selection")
        phase_options = [(phase.id, phase.name) for phase in roadmap.phases]
        selected_phase_index = 0  # Default to first phase
        
        # If we have a current phase ID, use it
        if st.session_state.current_phase_id:
            for i, (phase_id, _) in enumerate(phase_options):
                if phase_id == st.session_state.current_phase_id:
                    selected_phase_index = i
                    break
        
        # Only show the selector if we have phases
        if phase_options:
            selected_phase_id = st.selectbox(
                "Select Phase",
                options=[phase_id for phase_id, _ in phase_options],
                format_func=lambda x: next((name for pid, name in phase_options if pid == x), ""),
                index=selected_phase_index
            )
            
            # Update current phase ID
            st.session_state.current_phase_id = selected_phase_id
            
            # Get the phase object
            phase = roadmap.get_phase(selected_phase_id)
            
            if phase:
                # Phase details
                st.subheader(phase.name)
                st.write(phase.description)
                
                # Status update
                col1, col2 = st.columns([3, 1])
                with col1:
                    status = st.selectbox(
                        "Status",
                        ["planned", "in_progress", "completed", "blocked"],
                        index=["planned", "in_progress", "completed", "blocked"].index(phase.status)
                    )
                with col2:
                    if status != phase.status and st.button("Update Status"):
                        update_phase_status(phase.id, status)
                        st.success(f"Updated status to: {status}")
                        save_current_roadmap()
                        st.rerun()
                
                # Requirements, Components, and Tasks
                req_tab, comp_tab, task_tab = st.tabs(["Requirements", "Components", "Tasks"])
                
                with req_tab:
                    # Requirements
                    st.subheader("Requirements")
                    
                    # Show existing requirements
                    if not phase.requirements:
                        st.info("No requirements defined yet.")
                    else:
                        for i, req in enumerate(phase.requirements):
                            with st.container():
                                st.markdown(f"<div class='item-card requirement'><strong>{req['title']}</strong> - <span class='priority-{req['priority']}'>{req['priority']}</span></div>", unsafe_allow_html=True)
                                with st.expander("Details"):
                                    st.write(f"**Description:** {req['description']}")
                                    st.write(f"**Type:** {req['type']}")
                                    st.write(f"**Status:** {req['status']}")
                    
                    # Add new requirement
                    with st.expander("Add Requirement"):
                        req_title = st.text_input("Requirement Title", key="new_req_title")
                        req_description = st.text_area("Description", key="new_req_desc")
                        req_type = st.selectbox(
                            "Type",
                            ["functional", "non_functional", "technical"],
                            key="new_req_type"
                        )
                        req_priority = st.selectbox(
                            "Priority",
                            ["low", "medium", "high"],
                            index=1,  # Default to medium
                            key="new_req_priority"
                        )
                        
                        if st.button("Add Requirement"):
                            req_id = add_requirement_to_phase(
                                phase_id=phase.id,
                                title=req_title,
                                description=req_description,
                                req_type=req_type,
                                priority=req_priority
                            )
                            st.success(f"Added requirement: {req_title}")
                            save_current_roadmap()
                            st.rerun()
                
                with comp_tab:
                    # Components
                    st.subheader("Components")
                    
                    # Show existing components
                    if not phase.components:
                        st.info("No components defined yet.")
                    else:
                        for i, comp in enumerate(phase.components):
                            with st.container():
                                st.markdown(f"<div class='item-card component'><strong>{comp['name']}</strong></div>", unsafe_allow_html=True)
                                with st.expander("Details"):
                                    st.write(f"**Purpose:** {comp['purpose']}")
                                    st.write(f"**Implementation Details:** {comp['implementation_details']}")
                                    if comp['dependencies']:
                                        st.write(f"**Dependencies:** {', '.join(comp['dependencies'])}")
                                    
                                    # Generate code button
                                    if has_ai:
                                        if st.button("Generate Code", key=f"gen_code_{comp['id']}"):
                                            template_key = generate_component_code(
                                                component_name=comp['name'],
                                                component_purpose=comp['purpose']
                                            )
                                            
                                            if template_key:
                                                st.session_state.current_template = template_key
                                                st.success("Code generated! Check the Code Generation tab.")
                    
                    # Add new component
                    with st.expander("Add Component"):
                        comp_name = st.text_input("Component Name", key="new_comp_name")
                        comp_purpose = st.text_area("Purpose", key="new_comp_purpose")
                        comp_details = st.text_area("Implementation Details", key="new_comp_details")
                        
                        # Get all component names for dependencies
                        comp_names = [comp['name'] for comp in phase.components]
                        comp_dependencies = st.multiselect(
                            "Dependencies",
                            options=comp_names,
                            key="new_comp_deps"
                        )
                        
                        if st.button("Add Component"):
                            comp_id = add_component_to_phase(
                                phase_id=phase.id,
                                name=comp_name,
                                purpose=comp_purpose,
                                details=comp_details,
                                dependencies=comp_dependencies
                            )
                            st.success(f"Added component: {comp_name}")
                            save_current_roadmap()
                            st.rerun()
                
                with task_tab:
                    # Tasks
                    st.subheader("Tasks")
                    
                    # Show existing tasks
                    if not phase.tasks:
                        st.info("No tasks defined yet.")
                    else:
                        for i, task in enumerate(phase.tasks):
                            with st.container():
                                st.markdown(f"<div class='item-card task'><strong>{task['title']}</strong> - <span class='priority-{task['priority']}'>{task['priority']}</span> ({task['estimated_hours']} hrs)</div>", unsafe_allow_html=True)
                                with st.expander("Details"):
                                    st.write(f"**Description:** {task['description']}")
                                    st.write(f"**Status:** {task['status']}")
                    
                    # Add new task
                    with st.expander("Add Task"):
                        task_title = st.text_input("Task Title", key="new_task_title")
                        task_description = st.text_area("Description", key="new_task_desc")
                        task_priority = st.selectbox(
                            "Priority",
                            ["low", "medium", "high"],
                            index=1,  # Default to medium
                            key="new_task_priority"
                        )
                        task_hours = st.number_input(
                            "Estimated Hours",
                            min_value=0.5,
                            max_value=100.0,
                            value=2.0,
                            step=0.5,
                            key="new_task_hours"
                        )
                        
                        if st.button("Add Task"):
                            task_id = add_task_to_phase(
                                phase_id=phase.id,
                                title=task_title,
                                description=task_description,
                                priority=task_priority,
                                hours=task_hours
                            )
                            st.success(f"Added task: {task_title}")
                            save_current_roadmap()
                            st.rerun()
            else:
                st.error("Selected phase not found. Please select another phase.")
        else:
            st.info("No phases in this project yet. Please add a phase first.")
    else:
        st.info("No project loaded. Please create or load a project in the Project Overview tab.")

with tab3:
    # Code Generation tab
    if st.session_state.current_roadmap:
        st.subheader("Code Generation")
        st.write("Generate code scaffolding based on your project plan.")
        
        # Suggested templates
        st.markdown("### Suggested Templates")
        
        # Update templates
        update_code_templates()
        
        if not st.session_state.code_templates:
            st.info("No templates available for the current project phase.")
        else:
            for i, template in enumerate(st.session_state.code_templates):
                with st.container():
                    st.markdown(f"<div class='code-template'><strong>{template['name']}</strong> ({template['file_type']})<br/>{template['description']}</div>", unsafe_allow_html=True)
                    with st.expander("Preview"):
                        st.markdown(f"<div class='template-preview'>{template['template']}</div>", unsafe_allow_html=True)
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            template_name = st.text_input("Output File Name", value=f"{template['name'].lower().replace(' ', '_')}.{template['file_type']}", key=f"filename_{i}")
                        with col2:
                            if st.button("Generate", key=f"generate_{i}"):
                                template_key = generate_code_from_template(
                                    template=template['template'],
                                    template_name=template['name'],
                                    file_type=template['file_type']
                                )
                                
                                if template_key:
                                    st.session_state.current_template = template_key
                                    
                                    # Save to file if filename is provided
                                    if template_name:
                                        save_code_to_file(template_key, template_name)
                                    
                                    st.success("Code generated!")
        
        # Custom code generation
        st.markdown("### Custom Component Generation")
        
        col1, col2 = st.columns(2)
        with col1:
            component_name = st.text_input("Component Name", value="CustomComponent")
            component_purpose = st.text_area("Component Purpose", value="Describe what this component does")
        with col2:
            output_filename = st.text_input("Output File Name", value=f"{component_name.lower()}.py")
            
            if st.button("Generate Component"):
                if component_name and component_purpose:
                    template_key = generate_component_code(
                        component_name=component_name,
                        component_purpose=component_purpose
                    )
                    
                    if template_key:
                        st.session_state.current_template = template_key
                        
                        # Save to file if filename is provided
                        if output_filename:
                            save_code_to_file(template_key, output_filename)
                        
                        st.success("Component generated!")
                else:
                    st.warning("Please provide a component name and purpose")
        
        # Generated code
        if st.session_state.generated_code:
            st.markdown("### Generated Code")
            
            # Use a selectbox for the generated code
            template_keys = list(st.session_state.generated_code.keys())
            template_names = [f"{st.session_state.generated_code[k]['name']}" for k in template_keys]
            
            selected_index = 0
            if hasattr(st.session_state, 'current_template'):
                if st.session_state.current_template in template_keys:
                    selected_index = template_keys.index(st.session_state.current_template)
            
            selected_template = st.selectbox(
                "Select Generated Code",
                options=template_keys,
                format_func=lambda x: st.session_state.generated_code[x]['name'],
                index=selected_index
            )
            
            if selected_template:
                template = st.session_state.generated_code[selected_template]
                st.code(template['content'], language=template['file_type'])
                
                # File output options
                col1, col2 = st.columns(2)
                with col1:
                    save_filename = st.text_input("Save to File", value=f"{template['name'].lower().replace(' ', '_')}.{template['file_type']}")
                with col2:
                    if st.button("Save to File"):
                        if save_filename:
                            save_code_to_file(selected_template, save_filename)
                        else:
                            st.warning("Please provide a filename")
    else:
        st.info("No project loaded. Please create or load a project in the Project Overview tab.")

with tab4:
    # Settings tab
    st.subheader("Settings")
    
    # Application settings
    st.markdown("### Application Settings")
    
    # AI Settings
    st.markdown("### AI Configuration")
    
    if has_ai:
        st.success("AI features are enabled. You can use code generation and suggestions.")
        
        # API key configuration
        api_key = os.environ.get("OPENAI_API_KEY")
        if api_key:
            st.write("OpenAI API key is configured.")
        else:
            st.warning("No OpenAI API key found. Some features will be disabled.")
            st.write("Set the OPENAI_API_KEY environment variable to enable all AI features.")
    else:
        st.warning("AI features are not available. Install the required packages to enable them.")
        
    # Database information
    st.markdown("### Database Information")
    
    if get_db_instance():
        st.success("Database connection is established.")
        st.write("Your roadmaps are being saved to the database.")
    else:
        st.error("Database connection is not established.")
        st.write("Your roadmaps may not be saved correctly.")
    
    # Export/Import features
    st.markdown("### Export/Import")
    
    # Export current roadmap
    if st.session_state.current_roadmap:
        if st.button("Export Current Roadmap"):
            # Convert the roadmap to JSON
            roadmap_json = json.dumps(st.session_state.current_roadmap.to_dict(), indent=2)
            
            # Create a download link
            st.download_button(
                label="Download Roadmap JSON",
                data=roadmap_json,
                file_name=f"{st.session_state.current_roadmap.name.lower().replace(' ', '_')}_roadmap.json",
                mime="application/json"
            )
    
    # Import roadmap
    uploaded_file = st.file_uploader("Import Roadmap", type="json")
    if uploaded_file is not None:
        try:
            # Load the JSON
            roadmap_dict = json.loads(uploaded_file.getvalue().decode("utf-8"))
            
            # Create a roadmap from the dict
            roadmap = ProjectRoadmap.from_dict(roadmap_dict)
            
            # Set as current roadmap
            st.session_state.current_roadmap = roadmap
            st.session_state.has_unsaved_changes = True
            
            st.success(f"Imported roadmap: {roadmap.name}")
            
            # Save the roadmap
            save_current_roadmap()
            
            # Update templates
            update_code_templates()
            
            # Refresh
            st.rerun()
        except Exception as e:
            st.error(f"Error importing roadmap: {str(e)}")

# Footer
st.markdown("---")
st.markdown("PyWrite Roadmap Planning System | Built with Streamlit")

# Main function when run directly
if __name__ == "__main__":
    pass