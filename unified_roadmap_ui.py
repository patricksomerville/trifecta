"""
PyWrite Unified Roadmap Planning System

A versatile Streamlit-based interface for managing both technical and creative projects:
- Software development planning
- Fiction writing structure and character development
- Screenplay development with proper formatting

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
from project_roadmap import ProjectRoadmap, RoadmapPhase, get_roadmap_manager
from creative_roadmap import CreativeRoadmap, get_creative_roadmap_manager
from creative_roadmap import STORY_TEMPLATES, SCREENPLAY_TEMPLATES

try:
    from database_helper import get_db_instance
    from continuous_coding import get_continuous_coding_engine
    from creative_autocomplete_bridge import get_creative_autocomplete_bridge
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
    .item-card.character {
        border-left-color: #20c997;
    }
    .item-card.location {
        border-left-color: #0dcaf0;
    }
    .item-card.theme {
        border-left-color: #6f42c1;
    }
    .item-card.scene {
        border-left-color: #d63384;
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
    .role-protagonist {
        color: #0d6efd;
        font-weight: bold;
    }
    .role-antagonist {
        color: #dc3545;
        font-weight: bold;
    }
    .role-supporting {
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
    .mode-tabs {
        margin-bottom: 20px;
    }
    .feature-box {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 15px;
        margin: 15px 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .feature-box:hover {
        background-color: #e9ecef;
    }
    .feature-title {
        font-weight: bold;
        margin-bottom: 5px;
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
if 'current_project_type' not in st.session_state:
    st.session_state.current_project_type = "software"  # Default to software
if 'current_story_structure' not in st.session_state:
    st.session_state.current_story_structure = "three_act"  # Default to three act

# Initialize the managers
roadmap_manager = get_roadmap_manager()
creative_manager = get_creative_roadmap_manager()

# Initialize continuous coding engine and creative bridge if available
if has_enhanced_features:
    try:
        api_key = os.environ.get("OPENAI_API_KEY")
        continuous_coding_engine = get_continuous_coding_engine(api_key)
        creative_bridge = get_creative_autocomplete_bridge()
        has_ai = continuous_coding_engine.has_openai
    except Exception as e:
        st.error(f"Error initializing enhanced features: {str(e)}")
        has_ai = False
else:
    has_ai = False

# Function to load roadmap list
def load_roadmap_list():
    """Load list of roadmaps."""
    # Get software roadmaps
    software_roadmaps = roadmap_manager.list_roadmaps(user_id=st.session_state.user_id)
    software_roadmaps = [r for r in software_roadmaps 
                         if r["project_type"] not in ["fiction", "screenplay"]]
    
    # Get creative roadmaps
    creative_roadmaps = creative_manager.list_roadmaps(user_id=st.session_state.user_id)
    
    # Combine and update
    st.session_state.roadmap_list = software_roadmaps + creative_roadmaps

# Function to load a roadmap
def load_roadmap(roadmap_id):
    """Load a roadmap by ID."""
    # Try loading as creative roadmap first
    roadmap = creative_manager.get_roadmap(roadmap_id)
    
    # If not found, try standard roadmap
    if not roadmap:
        roadmap = roadmap_manager.get_roadmap(roadmap_id)
    
    if roadmap:
        st.session_state.current_roadmap = roadmap
        st.session_state.current_project_type = roadmap.project_type
        
        if hasattr(roadmap, 'characters'):  # It's a creative roadmap
            # Set creative specific attributes if available
            if hasattr(roadmap, 'story_structure'):
                st.session_state.current_story_structure = roadmap.story_structure
        
        update_templates()
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
    
    # Determine which manager to use
    if st.session_state.current_project_type in ["fiction", "screenplay"]:
        # Creative roadmap
        success = creative_manager.save_roadmap(
            st.session_state.current_roadmap,
            user_id=st.session_state.user_id
        )
    else:
        # Software roadmap
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

# Function to update templates based on roadmap type
def update_templates():
    """Update templates based on current roadmap."""
    if not st.session_state.current_roadmap:
        st.session_state.code_templates = []
        return
        
    templates = st.session_state.current_roadmap.get_suggested_templates()
    st.session_state.code_templates = templates

# Function to generate content from a template
def generate_from_template(template, template_name, file_type):
    """Generate content from a template using AI if available."""
    # Store the template content in the session state
    template_key = f"{template_name}_{str(uuid.uuid4())[:8]}"
    
    if has_ai and (continuous_coding_engine.has_openai or 
                  (hasattr(creative_bridge, 'has_openai') and creative_bridge.has_openai)):
        # Get context from the roadmap
        if st.session_state.current_project_type in ["fiction", "screenplay"]:
            context = st.session_state.current_roadmap.generate_writing_context()
        else:
            context = st.session_state.current_roadmap.generate_code_context()
        
        # Extract placeholders from template (format: {Placeholder})
        placeholders = re.findall(r'\{([^}]+)\}', template)
        
        # If there are placeholders, we should fill them using AI
        if placeholders:
            try:
                # Build a prompt for generating values for the placeholders
                if st.session_state.current_project_type in ["fiction", "screenplay"]:
                    prompt = f"""
                    I'm working on a {st.session_state.current_project_type} project called "{context['project_name']}".
                    Project description: {context['project_description']}
                    
                    I need to fill in the following placeholders in a content template for {template_name}:
                    {', '.join(placeholders)}
                    
                    The template is:
                    ```
                    {template}
                    ```
                    
                    Based on the project context, provide appropriate values for these placeholders.
                    Return your response in JSON format, with keys matching the placeholder names
                    and values containing the suggested replacements.
                    """
                else:
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
                
                st.success(f"Generated content for {template_name}")
                return template_key
                
            except Exception as e:
                st.error(f"Error generating content: {str(e)}")
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

# Function to generate a complete component, character, or scene
def generate_custom_content(content_type, name, purpose=None, details=None, context=None):
    """Generate code or text content using AI."""
    if not has_ai:
        st.warning("AI-powered content generation is not available")
        # Return a simple template anyway
        if st.session_state.current_project_type in ["fiction", "screenplay"]:
            if content_type == "character":
                template = f"""# Character Profile: {name}

## Basic Information
- **Full Name:** {name}
- **Age:** 
- **Occupation:** 
- **Physical Description:** 

## Background
[Character background here]

## Personality
[Character personality traits here]

## Goals and Motivations
[Character motivations here]

## Conflicts
[Character conflicts here]

## Notes
This is a placeholder template. For a complete character profile, provide OpenAI API key.
"""
            elif content_type == "scene":
                template = f"""# Scene: {name}

## Setting
- **Location:** 
- **Time:** 
- **Weather/Atmosphere:** 

## Characters Present
- 

## Scene Goal
{purpose or ""}

## Outcome
[Scene outcome here]

## Notes
This is a placeholder template. For a complete scene, provide OpenAI API key.
"""
            else:
                template = f"""# {content_type.title()}: {name}

## Description
{purpose or ""}

## Notes
This is a placeholder template. For complete content, provide OpenAI API key.
"""
        else:
            # Software component
            template = f"""
class {name}:
    \"\"\"
    {purpose or name} component.
    
    This is a placeholder implementation. For a complete implementation,
    provide OpenAI API key.
    \"\"\"
    
    def __init__(self):
        \"\"\"Initialize the component.\"\"\"
        pass
        
    def process(self, data):
        \"\"\"Process data.\"\"\"
        # TODO: Implement processing
        return data
"""
        
        template_key = f"{name}_{str(uuid.uuid4())[:8]}"
        st.session_state.generated_code[template_key] = {
            "name": name,
            "content": template,
            "file_type": "markdown" if st.session_state.current_project_type in ["fiction", "screenplay"] else "python"
        }
        return template_key
    
    # Get roadmap context
    if st.session_state.current_project_type in ["fiction", "screenplay"]:
        # Creative content generation
        
        if content_type == "character":
            # Generate a character profile
            try:
                content = creative_bridge.generate_creative_content(
                    content_type="character",
                    character_name=name,
                    prompt=purpose
                )
            except:
                st.error("Error connecting to creative bridge. Check OpenAI API key.")
                return None
                
        elif content_type == "scene":
            # Generate a scene
            try:
                content = creative_bridge.generate_creative_content(
                    content_type="scene",
                    character_name=context,  # Main character
                    setting_name=name,  # Location
                    scene_goal=purpose,
                    prompt=details
                )
            except:
                st.error("Error connecting to creative bridge. Check OpenAI API key.")
                return None
                
        elif content_type == "setting":
            # Generate a setting description
            try:
                content = creative_bridge.generate_creative_content(
                    content_type="description",
                    setting_name=name,
                    prompt=purpose
                )
            except:
                st.error("Error connecting to creative bridge. Check OpenAI API key.")
                return None
        
        if content:
            template_key = f"{name}_{str(uuid.uuid4())[:8]}"
            st.session_state.generated_code[template_key] = {
                "name": name,
                "content": content,
                "file_type": "markdown"
            }
            
            st.success(f"Generated {content_type} content for {name}")
            return template_key
            
    else:
        # Software component generation
        roadmap_context = st.session_state.current_roadmap.generate_code_context()
        
        try:
            # Build a prompt for generating the component
            prompt = f"""
            I'm building a {roadmap_context['project_type']} project called "{roadmap_context['project_name']}".
            Project description: {roadmap_context['project_description']}
            
            I need to implement a component named "{name}" with this purpose:
            "{purpose or 'No purpose specified'}"
            
            Additional details: {details or 'None provided'}
            
            Current project phase: {roadmap_context['current_phase']['name'] if roadmap_context.get('current_phase') else 'Unknown'}
            
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
            template_key = f"{name}_{str(uuid.uuid4())[:8]}"
            st.session_state.generated_code[template_key] = {
                "name": name,
                "content": code,
                "file_type": "python"
            }
            
            st.success(f"Generated code for {name}")
            return template_key
            
        except Exception as e:
            st.error(f"Error generating code: {str(e)}")
            return None
    
    st.error("Content generation failed")
    return None

# Function to save generated content to file
def save_content_to_file(template_key, filename):
    """Save generated content to a file."""
    if template_key not in st.session_state.generated_code:
        st.error("Content template not found")
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
            
        st.success(f"Saved content to {filename}")
        return True
        
    except Exception as e:
        st.error(f"Error saving file: {str(e)}")
        return False

# Function to create a new roadmap
def create_new_roadmap(name, description, project_type, story_structure=None):
    """Create a new roadmap."""
    if project_type in ["fiction", "screenplay"]:
        # Create creative roadmap
        roadmap = creative_manager.create_roadmap(
            name=name,
            description=description,
            project_type=project_type,
            structure_template=story_structure
        )
    else:
        # Create software roadmap
        roadmap = ProjectRoadmap(
            name=name,
            description=description,
            project_type=project_type
        )
    
    st.session_state.current_roadmap = roadmap
    st.session_state.current_project_type = project_type
    st.session_state.has_unsaved_changes = True
    
    if story_structure:
        st.session_state.current_story_structure = story_structure
    
    # Save immediately
    save_current_roadmap()
    
    # Update templates
    update_templates()
    
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

# Function to add a requirement to a phase (technical roadmap)
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

# Function to add a component to a phase (technical roadmap)
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

# Function to add a task to a phase (common to all roadmaps)
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

# Function to add a character (creative roadmap)
def add_character_to_roadmap(name, role, description, motivation, arc):
    """Add a character to the creative roadmap."""
    if not st.session_state.current_roadmap or not hasattr(st.session_state.current_roadmap, 'add_character'):
        st.error("No creative roadmap loaded")
        return None
        
    # Add the character
    character_id = st.session_state.current_roadmap.add_character(
        name=name,
        role=role,
        description=description,
        motivation=motivation,
        arc=arc
    )
    
    st.session_state.has_unsaved_changes = True
    
    return character_id

# Function to add a location (creative roadmap)
def add_location_to_roadmap(name, description):
    """Add a location to the creative roadmap."""
    if not st.session_state.current_roadmap or not hasattr(st.session_state.current_roadmap, 'add_location'):
        st.error("No creative roadmap loaded")
        return None
        
    # Add the location
    location_id = st.session_state.current_roadmap.add_location(
        name=name,
        description=description
    )
    
    st.session_state.has_unsaved_changes = True
    
    return location_id

# Function to add a theme (creative roadmap)
def add_theme_to_roadmap(name, description):
    """Add a theme to the creative roadmap."""
    if not st.session_state.current_roadmap or not hasattr(st.session_state.current_roadmap, 'add_theme'):
        st.error("No creative roadmap loaded")
        return None
        
    # Add the theme
    theme_id = st.session_state.current_roadmap.add_theme(
        name=name,
        description=description
    )
    
    st.session_state.has_unsaved_changes = True
    
    return theme_id

# Function to add a scene to a phase (creative roadmap)
def add_scene_to_phase(phase_id, title, description, characters, location, goal):
    """Add a scene to a phase."""
    if not st.session_state.current_roadmap or not hasattr(st.session_state.current_roadmap, 'add_scene'):
        st.error("No creative roadmap loaded")
        return None
        
    # Add the scene
    scene_id = st.session_state.current_roadmap.add_scene(
        phase_id=phase_id,
        title=title,
        description=description,
        characters=characters,
        location=location,
        goal=goal
    )
    
    st.session_state.has_unsaved_changes = True
    
    return scene_id

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

# Function to change the story structure for creative roadmaps
def change_story_structure(structure_template):
    """Change the story structure for a creative roadmap."""
    if not st.session_state.current_roadmap or not hasattr(st.session_state.current_roadmap, 'change_story_structure'):
        st.error("No creative roadmap loaded")
        return False
        
    # Change the structure
    success = st.session_state.current_roadmap.change_story_structure(structure_template)
    
    if success:
        st.session_state.current_story_structure = structure_template
        st.session_state.has_unsaved_changes = True
        
    return success

# Initialize by loading roadmap list
if roadmap_manager:
    load_roadmap_list()

# Layout the application
title_col1, title_col2 = st.columns([3, 1])

with title_col1:
    st.title("🗺️ PyWrite Unified Roadmap Planning")
    st.markdown("Plan technical and creative projects to enhance autocomplete and AI assistance.")

with title_col2:
    st.write("")
    st.write("")
    if st.session_state.has_unsaved_changes:
        st.warning("You have unsaved changes")
        if st.button("Save Changes"):
            save_current_roadmap()

# Project type tabs
project_type_tab1, project_type_tab2, project_type_tab3 = st.tabs(["Software Projects", "Fiction Projects", "Screenplay Projects"])

# Determine which tab to switch to based on current project type
if st.session_state.current_roadmap:
    if st.session_state.current_project_type == "fiction":
        project_type_tab2.write("Fiction writing project active")
    elif st.session_state.current_project_type == "screenplay":
        project_type_tab3.write("Screenplay project active")
    else:
        project_type_tab1.write("Software project active")

# Software Projects Tab
with project_type_tab1:
    st.header("Software Project Planning")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Software Project Selection")
        
        # Create new project section
        with st.expander("Create New Software Project", expanded=True if not st.session_state.roadmap_list else False):
            new_project_name = st.text_input("Project Name", value="My New Software Project", key="sw_name")
            new_project_description = st.text_area("Project Description", value="A description of the software project", key="sw_desc")
            new_project_type = st.selectbox(
                "Project Type",
                ["software", "web", "mobile", "api", "data", "research", "other"],
                key="sw_type"
            )
            
            if st.button("Create Software Project"):
                roadmap = create_new_roadmap(
                    name=new_project_name,
                    description=new_project_description,
                    project_type=new_project_type
                )
                st.success(f"Created project: {roadmap.name}")
                st.rerun()
        
        # Existing software projects list
        st.subheader("Existing Software Projects")
        software_roadmaps = [r for r in st.session_state.roadmap_list 
                           if r["project_type"] not in ["fiction", "screenplay"]]
        
        if not software_roadmaps:
            st.info("No software projects found. Create a new one to get started.")
        else:
            for roadmap in software_roadmaps:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**{roadmap['name']}**")
                    st.caption(roadmap['description'][:100] + "..." if len(roadmap['description']) > 100 else roadmap['description'])
                with col2:
                    if st.button("Load", key=f"load_sw_{roadmap['id']}"):
                        load_roadmap(roadmap['id'])
                        st.rerun()
    
    with col2:
        # Current project details
        if st.session_state.current_roadmap and st.session_state.current_project_type not in ["fiction", "screenplay"]:
            roadmap = st.session_state.current_roadmap
            
            st.subheader("Current Software Project")
            
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
                            if st.button("Details", key=f"details_sw_{phase.id}"):
                                st.session_state.current_phase_id = phase.id
                                st.rerun()
            
            # Add new phase
            with st.expander("Add New Phase"):
                phase_name = st.text_input("Phase Name", key="sw_phase_name")
                phase_description = st.text_area("Phase Description", key="sw_phase_desc")
                phase_status = st.selectbox(
                    "Initial Status",
                    ["planned", "in_progress", "completed", "blocked"],
                    key="sw_phase_status"
                )
                
                if st.button("Add Phase", key="add_sw_phase"):
                    phase_id = add_phase_to_roadmap(
                        name=phase_name,
                        description=phase_description,
                        status=phase_status
                    )
                    st.success(f"Added phase: {phase_name}")
                    save_current_roadmap()
                    st.rerun()
        else:
            st.info("No software project loaded. Please create or load a project.")

# Fiction Projects Tab
with project_type_tab2:
    st.header("Fiction Writing Projects")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Fiction Project Selection")
        
        # Create new project section
        with st.expander("Create New Fiction Project", expanded=True if not st.session_state.roadmap_list else False):
            new_project_name = st.text_input("Book/Story Title", value="My Novel", key="fiction_name")
            new_project_description = st.text_area("Story Concept/Logline", value="A brief description of the story", key="fiction_desc")
            
            # Story structure selection
            story_structure = st.selectbox(
                "Story Structure",
                list(STORY_TEMPLATES.keys()),
                format_func=lambda x: x.replace("_", " ").title(),
                key="fiction_structure"
            )
            
            if st.button("Create Fiction Project"):
                roadmap = create_new_roadmap(
                    name=new_project_name,
                    description=new_project_description,
                    project_type="fiction",
                    story_structure=story_structure
                )
                st.success(f"Created fiction project: {roadmap.name}")
                st.rerun()
        
        # Existing fiction projects list
        st.subheader("Existing Fiction Projects")
        fiction_roadmaps = [r for r in st.session_state.roadmap_list 
                          if r["project_type"] == "fiction"]
        
        if not fiction_roadmaps:
            st.info("No fiction projects found. Create a new one to get started.")
        else:
            for roadmap in fiction_roadmaps:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**{roadmap['name']}**")
                    st.caption(roadmap['description'][:100] + "..." if len(roadmap['description']) > 100 else roadmap['description'])
                with col2:
                    if st.button("Load", key=f"load_fiction_{roadmap['id']}"):
                        load_roadmap(roadmap['id'])
                        st.rerun()
    
    with col2:
        # Current project details
        if st.session_state.current_roadmap and st.session_state.current_project_type == "fiction":
            roadmap = st.session_state.current_roadmap
            
            st.subheader("Current Fiction Project")
            
            # Project header
            st.markdown(f"## {roadmap.name}")
            st.markdown(f"*{roadmap.description}*")
            
            # Story structure
            structure_options = list(STORY_TEMPLATES.keys())
            structure_names = [s.replace("_", " ").title() for s in structure_options]
            
            col1, col2 = st.columns([3, 1])
            with col1:
                structure_index = structure_options.index(st.session_state.current_story_structure) if st.session_state.current_story_structure in structure_options else 0
                new_structure = st.selectbox(
                    "Story Structure",
                    structure_options,
                    index=structure_index,
                    format_func=lambda x: x.replace("_", " ").title(),
                    key="fiction_change_structure"
                )
            with col2:
                if new_structure != st.session_state.current_story_structure and st.button("Update Structure"):
                    change_story_structure(new_structure)
                    st.success(f"Updated story structure to: {new_structure.replace('_', ' ').title()}")
                    save_current_roadmap()
                    st.rerun()
            
            # Tags
            if roadmap.tags:
                st.markdown("**Tags:**")
                tags_html = '<div class="tags-container">'
                for tag in roadmap.tags:
                    tags_html += f'<span class="tag">{tag}</span>'
                tags_html += '</div>'
                st.markdown(tags_html, unsafe_allow_html=True)
            
            # Add tag
            new_tag = st.text_input("Add Tag", key="fiction_tag")
            if new_tag and st.button("Add Tag", key="fiction_add_tag"):
                add_tag_to_roadmap(new_tag)
                st.success(f"Added tag: {new_tag}")
                st.rerun()
            
            # Writing stats
            st.subheader("Writing Stats")
            col1, col2 = st.columns(2)
            with col1:
                word_count = st.number_input("Target Word Count", 
                                            min_value=0, 
                                            value=roadmap.word_count_goal or 50000,
                                            step=1000)
                if word_count != roadmap.word_count_goal:
                    roadmap.word_count_goal = word_count
                    st.session_state.has_unsaved_changes = True
                    
            with col2:
                st.metric("Characters", len(roadmap.characters))
                st.metric("Locations", len(roadmap.locations))
            
            # Quick access tabs
            story_tab1, story_tab2, story_tab3 = st.tabs(["Structure", "Characters", "Settings"])
            
            with story_tab1:
                # Story structure phases
                st.subheader("Story Structure")
                
                phases_container = st.container()
                
                with phases_container:
                    structure_phases = [p for p in roadmap.phases 
                                      if p.name in [name for name, _ in STORY_TEMPLATES[st.session_state.current_story_structure]]]
                    
                    for phase in structure_phases:
                        with st.container():
                            col1, col2, col3 = st.columns([3, 1, 1])
                            
                            with col1:
                                st.markdown(f"**{phase.name}**")
                                st.caption(phase.description[:100] + "..." if len(phase.description) > 100 else phase.description)
                            
                            with col2:
                                status_class = f"status-{phase.status}"
                                st.markdown(f'<span class="{status_class}">{phase.status.replace("_", " ").title()}</span>', unsafe_allow_html=True)
                            
                            with col3:
                                if st.button("Details", key=f"details_fiction_{phase.id}"):
                                    st.session_state.current_phase_id = phase.id
                                    st.rerun()
            
            with story_tab2:
                # Characters
                st.subheader("Characters")
                
                for character in roadmap.characters:
                    with st.container():
                        role_class = f"role-{character['role']}"
                        st.markdown(f"<div class='item-card character'><strong>{character['name']}</strong> - <span class='{role_class}'>{character['role'].title()}</span></div>", unsafe_allow_html=True)
                        with st.expander("Details"):
                            st.write(f"**Description:** {character['description']}")
                            st.write(f"**Motivation:** {character['motivation']}")
                            st.write(f"**Character Arc:** {character['arc']}")
                
                # Add new character
                with st.expander("Add Character"):
                    char_name = st.text_input("Character Name", key="fiction_char_name")
                    char_role = st.selectbox(
                        "Role",
                        ["protagonist", "antagonist", "supporting"],
                        key="fiction_char_role"
                    )
                    char_desc = st.text_area("Description", key="fiction_char_desc")
                    char_motivation = st.text_area("Motivation/Goals", key="fiction_char_motivation")
                    char_arc = st.text_area("Character Arc", key="fiction_char_arc")
                    
                    if st.button("Add Character", key="fiction_add_char"):
                        char_id = add_character_to_roadmap(
                            name=char_name,
                            role=char_role,
                            description=char_desc,
                            motivation=char_motivation,
                            arc=char_arc
                        )
                        st.success(f"Added character: {char_name}")
                        save_current_roadmap()
                        st.rerun()
            
            with story_tab3:
                # Locations
                st.subheader("Locations")
                
                for location in roadmap.locations:
                    with st.container():
                        st.markdown(f"<div class='item-card location'><strong>{location['name']}</strong></div>", unsafe_allow_html=True)
                        with st.expander("Details"):
                            st.write(f"**Description:** {location['description']}")
                
                # Add new location
                with st.expander("Add Location"):
                    loc_name = st.text_input("Location Name", key="fiction_loc_name")
                    loc_desc = st.text_area("Description", key="fiction_loc_desc")
                    
                    if st.button("Add Location", key="fiction_add_loc"):
                        loc_id = add_location_to_roadmap(
                            name=loc_name,
                            description=loc_desc
                        )
                        st.success(f"Added location: {loc_name}")
                        save_current_roadmap()
                        st.rerun()
                
                # Themes
                st.subheader("Themes")
                
                for theme in roadmap.themes:
                    with st.container():
                        st.markdown(f"<div class='item-card theme'><strong>{theme['name']}</strong></div>", unsafe_allow_html=True)
                        with st.expander("Details"):
                            st.write(f"**Description:** {theme['description']}")
                
                # Add new theme
                with st.expander("Add Theme"):
                    theme_name = st.text_input("Theme Name", key="fiction_theme_name")
                    theme_desc = st.text_area("Description", key="fiction_theme_desc")
                    
                    if st.button("Add Theme", key="fiction_add_theme"):
                        theme_id = add_theme_to_roadmap(
                            name=theme_name,
                            description=theme_desc
                        )
                        st.success(f"Added theme: {theme_name}")
                        save_current_roadmap()
                        st.rerun()
        else:
            st.info("No fiction project loaded. Please create or load a project.")

# Screenplay Projects Tab
with project_type_tab3:
    st.header("Screenplay Projects")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Screenplay Project Selection")
        
        # Create new project section
        with st.expander("Create New Screenplay Project", expanded=True if not st.session_state.roadmap_list else False):
            new_project_name = st.text_input("Screenplay Title", value="My Screenplay", key="screenplay_name")
            new_project_description = st.text_area("Logline", value="A brief description of the screenplay", key="screenplay_desc")
            
            # Screenplay structure selection
            screenplay_structure = st.selectbox(
                "Screenplay Structure",
                list(SCREENPLAY_TEMPLATES.keys()),
                format_func=lambda x: x.replace("_", " ").title(),
                key="screenplay_structure"
            )
            
            if st.button("Create Screenplay Project"):
                roadmap = create_new_roadmap(
                    name=new_project_name,
                    description=new_project_description,
                    project_type="screenplay",
                    story_structure=screenplay_structure
                )
                st.success(f"Created screenplay project: {roadmap.name}")
                st.rerun()
        
        # Existing screenplay projects list
        st.subheader("Existing Screenplay Projects")
        screenplay_roadmaps = [r for r in st.session_state.roadmap_list 
                             if r["project_type"] == "screenplay"]
        
        if not screenplay_roadmaps:
            st.info("No screenplay projects found. Create a new one to get started.")
        else:
            for roadmap in screenplay_roadmaps:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**{roadmap['name']}**")
                    st.caption(roadmap['description'][:100] + "..." if len(roadmap['description']) > 100 else roadmap['description'])
                with col2:
                    if st.button("Load", key=f"load_screenplay_{roadmap['id']}"):
                        load_roadmap(roadmap['id'])
                        st.rerun()
    
    with col2:
        # Current project details
        if st.session_state.current_roadmap and st.session_state.current_project_type == "screenplay":
            roadmap = st.session_state.current_roadmap
            
            st.subheader("Current Screenplay Project")
            
            # Project header
            st.markdown(f"## {roadmap.name}")
            st.markdown(f"*{roadmap.description}*")
            
            # Screenplay structure
            structure_options = list(SCREENPLAY_TEMPLATES.keys())
            structure_names = [s.replace("_", " ").title() for s in structure_options]
            
            col1, col2 = st.columns([3, 1])
            with col1:
                structure_index = structure_options.index(st.session_state.current_story_structure) if st.session_state.current_story_structure in structure_options else 0
                new_structure = st.selectbox(
                    "Screenplay Structure",
                    structure_options,
                    index=structure_index,
                    format_func=lambda x: x.replace("_", " ").title(),
                    key="screenplay_change_structure"
                )
            with col2:
                if new_structure != st.session_state.current_story_structure and st.button("Update Structure"):
                    change_story_structure(new_structure)
                    st.success(f"Updated screenplay structure to: {new_structure.replace('_', ' ').title()}")
                    save_current_roadmap()
                    st.rerun()
            
            # Tags
            if roadmap.tags:
                st.markdown("**Tags:**")
                tags_html = '<div class="tags-container">'
                for tag in roadmap.tags:
                    tags_html += f'<span class="tag">{tag}</span>'
                tags_html += '</div>'
                st.markdown(tags_html, unsafe_allow_html=True)
            
            # Add tag
            new_tag = st.text_input("Add Tag", key="screenplay_tag")
            if new_tag and st.button("Add Tag", key="screenplay_add_tag"):
                add_tag_to_roadmap(new_tag)
                st.success(f"Added tag: {new_tag}")
                st.rerun()
            
            # Writing stats
            st.subheader("Screenplay Stats")
            col1, col2 = st.columns(2)
            with col1:
                page_count = st.number_input("Target Page Count", 
                                            min_value=0, 
                                            value=roadmap.page_count_goal or 120,
                                            step=5)
                if page_count != roadmap.page_count_goal:
                    roadmap.page_count_goal = page_count
                    st.session_state.has_unsaved_changes = True
                    
            with col2:
                st.metric("Characters", len(roadmap.characters))
                st.metric("Locations", len(roadmap.locations))
            
            # Quick access tabs
            screenplay_tab1, screenplay_tab2, screenplay_tab3 = st.tabs(["Structure", "Characters", "Settings"])
            
            with screenplay_tab1:
                # Screenplay structure
                st.subheader("Screenplay Structure")
                
                phases_container = st.container()
                
                with phases_container:
                    structure_phases = [p for p in roadmap.phases 
                                      if p.name in [name for name, _ in SCREENPLAY_TEMPLATES[st.session_state.current_story_structure]]]
                    
                    for phase in structure_phases:
                        with st.container():
                            col1, col2, col3 = st.columns([3, 1, 1])
                            
                            with col1:
                                st.markdown(f"**{phase.name}**")
                                st.caption(phase.description[:100] + "..." if len(phase.description) > 100 else phase.description)
                            
                            with col2:
                                status_class = f"status-{phase.status}"
                                st.markdown(f'<span class="{status_class}">{phase.status.replace("_", " ").title()}</span>', unsafe_allow_html=True)
                            
                            with col3:
                                if st.button("Details", key=f"details_screenplay_{phase.id}"):
                                    st.session_state.current_phase_id = phase.id
                                    st.rerun()
            
            with screenplay_tab2:
                # Characters
                st.subheader("Characters")
                
                for character in roadmap.characters:
                    with st.container():
                        role_class = f"role-{character['role']}"
                        st.markdown(f"<div class='item-card character'><strong>{character['name']}</strong> - <span class='{role_class}'>{character['role'].title()}</span></div>", unsafe_allow_html=True)
                        with st.expander("Details"):
                            st.write(f"**Description:** {character['description']}")
                            st.write(f"**Motivation:** {character['motivation']}")
                            st.write(f"**Character Arc:** {character['arc']}")
                
                # Add new character
                with st.expander("Add Character"):
                    char_name = st.text_input("Character Name", key="screenplay_char_name")
                    char_role = st.selectbox(
                        "Role",
                        ["protagonist", "antagonist", "supporting"],
                        key="screenplay_char_role"
                    )
                    char_desc = st.text_area("Description", key="screenplay_char_desc")
                    char_motivation = st.text_area("Motivation/Goals", key="screenplay_char_motivation")
                    char_arc = st.text_area("Character Arc", key="screenplay_char_arc")
                    
                    if st.button("Add Character", key="screenplay_add_char"):
                        char_id = add_character_to_roadmap(
                            name=char_name,
                            role=char_role,
                            description=char_desc,
                            motivation=char_motivation,
                            arc=char_arc
                        )
                        st.success(f"Added character: {char_name}")
                        save_current_roadmap()
                        st.rerun()
            
            with screenplay_tab3:
                # Locations
                st.subheader("Locations")
                
                for location in roadmap.locations:
                    with st.container():
                        st.markdown(f"<div class='item-card location'><strong>{location['name']}</strong></div>", unsafe_allow_html=True)
                        with st.expander("Details"):
                            st.write(f"**Description:** {location['description']}")
                
                # Add new location
                with st.expander("Add Location"):
                    loc_name = st.text_input("Location Name", key="screenplay_loc_name")
                    loc_desc = st.text_area("Description", key="screenplay_loc_desc")
                    
                    if st.button("Add Location", key="screenplay_add_loc"):
                        loc_id = add_location_to_roadmap(
                            name=loc_name,
                            description=loc_desc
                        )
                        st.success(f"Added location: {loc_name}")
                        save_current_roadmap()
                        st.rerun()
                
                # Themes
                st.subheader("Themes")
                
                for theme in roadmap.themes:
                    with st.container():
                        st.markdown(f"<div class='item-card theme'><strong>{theme['name']}</strong></div>", unsafe_allow_html=True)
                        with st.expander("Details"):
                            st.write(f"**Description:** {theme['description']}")
                
                # Add new theme
                with st.expander("Add Theme"):
                    theme_name = st.text_input("Theme Name", key="screenplay_theme_name")
                    theme_desc = st.text_area("Description", key="screenplay_theme_desc")
                    
                    if st.button("Add Theme", key="screenplay_add_theme"):
                        theme_id = add_theme_to_roadmap(
                            name=theme_name,
                            description=theme_desc
                        )
                        st.success(f"Added theme: {theme_name}")
                        save_current_roadmap()
                        st.rerun()
        else:
            st.info("No screenplay project loaded. Please create or load a project.")

# Main content tabs (common to all project types)
if st.session_state.current_roadmap:
    # Phase details, templates, and settings tabs
    tab1, tab2, tab3, tab4 = st.tabs(["Phase Details", "Content Generation", "Analysis", "Settings"])
    
    with tab1:
        # Phase Details tab
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
                
                # Tab groups based on project type
                if st.session_state.current_project_type in ["fiction", "screenplay"]:
                    # Creative project tabs
                    creative_tabs = st.tabs(["Scenes", "Notes", "Tasks"])
                    
                    with creative_tabs[0]:
                        # Scenes
                        st.subheader("Scenes")
                        
                        # Show existing scenes
                        scene_count = 0
                        for task in phase.tasks:
                            if "scene_data" in task:
                                scene_count += 1
                                scene = task["scene_data"]
                                st.markdown(f"<div class='item-card scene'><strong>{scene['title']}</strong></div>", unsafe_allow_html=True)
                                with st.expander("Details"):
                                    st.write(f"**Description:** {scene['description']}")
                                    st.write(f"**Location:** {scene['location']}")
                                    st.write(f"**Characters:** {', '.join(scene['characters'])}")
                                    st.write(f"**Goal:** {scene['goal']}")
                        
                        if scene_count == 0:
                            st.info("No scenes defined yet.")
                        
                        # Add new scene
                        with st.expander("Add Scene"):
                            scene_title = st.text_input("Scene Title")
                            scene_desc = st.text_area("Description")
                            
                            # Character selection from existing characters
                            character_options = [char["name"] for char in roadmap.characters]
                            scene_characters = st.multiselect(
                                "Characters in Scene",
                                options=character_options
                            )
                            
                            # Location selection from existing locations
                            location_options = [loc["name"] for loc in roadmap.locations]
                            scene_location = st.selectbox(
                                "Location",
                                options=[""] + location_options
                            )
                            
                            scene_goal = st.text_area("Scene Goal/Purpose")
                            
                            if st.button("Add Scene"):
                                scene_id = add_scene_to_phase(
                                    phase_id=phase.id,
                                    title=scene_title,
                                    description=scene_desc,
                                    characters=scene_characters,
                                    location=scene_location,
                                    goal=scene_goal
                                )
                                st.success(f"Added scene: {scene_title}")
                                save_current_roadmap()
                                st.rerun()
                    
                    with creative_tabs[1]:
                        # Notes
                        st.subheader("Notes")
                        
                        # Show existing notes (stored as requirements)
                        note_count = 0
                        for req in phase.requirements:
                            note_count += 1
                            st.markdown(f"<div class='item-card requirement'><strong>{req['title']}</strong></div>", unsafe_allow_html=True)
                            with st.expander("Details"):
                                st.write(req['description'])
                        
                        if note_count == 0:
                            st.info("No notes added yet.")
                        
                        # Add new note
                        with st.expander("Add Note"):
                            note_title = st.text_input("Note Title")
                            note_content = st.text_area("Note Content")
                            
                            if st.button("Add Note"):
                                note_id = add_requirement_to_phase(
                                    phase_id=phase.id,
                                    title=note_title,
                                    description=note_content,
                                    req_type="note",
                                    priority="medium"
                                )
                                st.success(f"Added note: {note_title}")
                                save_current_roadmap()
                                st.rerun()
                    
                    with creative_tabs[2]:
                        # Tasks
                        st.subheader("Tasks")
                        
                        # Show existing tasks that are not scenes
                        task_count = 0
                        for task in phase.tasks:
                            if "scene_data" not in task:
                                task_count += 1
                                st.markdown(f"<div class='item-card task'><strong>{task['title']}</strong> - <span class='priority-{task['priority']}'>{task['priority']}</span> ({task['estimated_hours']} hrs)</div>", unsafe_allow_html=True)
                                with st.expander("Details"):
                                    st.write(f"**Description:** {task['description']}")
                                    st.write(f"**Status:** {task['status']}")
                        
                        if task_count == 0:
                            st.info("No tasks defined yet.")
                        
                        # Add new task
                        with st.expander("Add Task"):
                            task_title = st.text_input("Task Title")
                            task_description = st.text_area("Description")
                            task_priority = st.selectbox(
                                "Priority",
                                ["low", "medium", "high"],
                                index=1  # Default to medium
                            )
                            task_hours = st.number_input(
                                "Estimated Hours",
                                min_value=0.5,
                                max_value=100.0,
                                value=2.0,
                                step=0.5
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
                    # Software project tabs
                    sw_tabs = st.tabs(["Requirements", "Components", "Tasks"])
                    
                    with sw_tabs[0]:
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
                            req_title = st.text_input("Requirement Title")
                            req_description = st.text_area("Description")
                            req_type = st.selectbox(
                                "Type",
                                ["functional", "non_functional", "technical"]
                            )
                            req_priority = st.selectbox(
                                "Priority",
                                ["low", "medium", "high"],
                                index=1  # Default to medium
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
                    
                    with sw_tabs[1]:
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
                                                template_key = generate_custom_content(
                                                    content_type="component",
                                                    name=comp['name'],
                                                    purpose=comp['purpose'],
                                                    details=comp['implementation_details']
                                                )
                                                
                                                if template_key:
                                                    st.session_state.current_template = template_key
                                                    st.success("Code generated! Check the Code Generation tab.")
                        
                        # Add new component
                        with st.expander("Add Component"):
                            comp_name = st.text_input("Component Name")
                            comp_purpose = st.text_area("Purpose")
                            comp_details = st.text_area("Implementation Details")
                            
                            # Get all component names for dependencies
                            comp_names = []
                            for p in roadmap.phases:
                                comp_names.extend([c['name'] for c in p.components])
                            comp_dependencies = st.multiselect(
                                "Dependencies",
                                options=comp_names
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
                    
                    with sw_tabs[2]:
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
                            task_title = st.text_input("Task Title")
                            task_description = st.text_area("Description")
                            task_priority = st.selectbox(
                                "Priority",
                                ["low", "medium", "high"],
                                index=1  # Default to medium
                            )
                            task_hours = st.number_input(
                                "Estimated Hours",
                                min_value=0.5,
                                max_value=100.0,
                                value=2.0,
                                step=0.5
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
    
    with tab2:
        # Content Generation tab
        st.subheader("Content Generation")
        
        if st.session_state.current_project_type in ["fiction", "screenplay"]:
            st.write("Generate creative content based on your project plan.")
        else:
            st.write("Generate code scaffolding based on your project plan.")
        
        # Suggested templates
        st.markdown("### Suggested Templates")
        
        # Update templates
        update_templates()
        
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
                                template_key = generate_from_template(
                                    template=template['template'],
                                    template_name=template['name'],
                                    file_type=template['file_type']
                                )
                                
                                if template_key:
                                    st.session_state.current_template = template_key
                                    
                                    # Save to file if filename is provided
                                    if template_name:
                                        save_content_to_file(template_key, template_name)
                                    
                                    st.success("Content generated!")
        
        # Custom content generation based on project type
        if st.session_state.current_project_type in ["fiction", "screenplay"]:
            # Creative content generation
            st.markdown("### Custom Content Generation")
            
            content_type = st.selectbox(
                "Content Type",
                ["character", "scene", "setting"]
            )
            
            if content_type == "character":
                col1, col2 = st.columns(2)
                with col1:
                    character_name = st.text_input("Character Name", value="New Character")
                    character_desc = st.text_area("Character Description/Prompt", value="Describe this character")
                with col2:
                    output_filename = st.text_input("Output File Name", value=f"{character_name.lower().replace(' ', '_')}.md")
                    
                    if st.button("Generate Character"):
                        if character_name:
                            template_key = generate_custom_content(
                                content_type="character",
                                name=character_name,
                                purpose=character_desc
                            )
                            
                            if template_key:
                                st.session_state.current_template = template_key
                                
                                # Save to file if filename is provided
                                if output_filename:
                                    save_content_to_file(template_key, output_filename)
                                
                                st.success("Character generated!")
                        else:
                            st.warning("Please provide a character name")
            
            elif content_type == "scene":
                col1, col2 = st.columns(2)
                with col1:
                    # Settings and characters
                    location_options = [""] + [loc["name"] for loc in roadmap.locations]
                    scene_location = st.selectbox("Location", options=location_options)
                    
                    character_options = [char["name"] for char in roadmap.characters]
                    main_character = st.selectbox("Main Character", options=[""] + character_options)
                    
                    scene_goal = st.text_area("Scene Goal/Purpose")
                    scene_details = st.text_area("Additional Details")
                
                with col2:
                    output_filename = st.text_input("Output File Name", value=f"scene_{scene_location.lower().replace(' ', '_')}.md")
                    
                    if st.button("Generate Scene"):
                        if scene_location:
                            template_key = generate_custom_content(
                                content_type="scene",
                                name=scene_location,  # Location
                                purpose=scene_goal,
                                details=scene_details,
                                context=main_character  # Character
                            )
                            
                            if template_key:
                                st.session_state.current_template = template_key
                                
                                # Save to file if filename is provided
                                if output_filename:
                                    save_content_to_file(template_key, output_filename)
                                
                                st.success("Scene generated!")
                        else:
                            st.warning("Please select a location")
            
            elif content_type == "setting":
                col1, col2 = st.columns(2)
                with col1:
                    setting_name = st.text_input("Setting Name", value="New Location")
                    setting_desc = st.text_area("Setting Description/Prompt", value="Describe this location")
                with col2:
                    output_filename = st.text_input("Output File Name", value=f"{setting_name.lower().replace(' ', '_')}.md")
                    
                    if st.button("Generate Setting"):
                        if setting_name:
                            template_key = generate_custom_content(
                                content_type="setting",
                                name=setting_name,
                                purpose=setting_desc
                            )
                            
                            if template_key:
                                st.session_state.current_template = template_key
                                
                                # Save to file if filename is provided
                                if output_filename:
                                    save_content_to_file(template_key, output_filename)
                                
                                st.success("Setting description generated!")
                        else:
                            st.warning("Please provide a setting name")
        
        else:
            # Code component generation
            st.markdown("### Custom Component Generation")
            
            col1, col2 = st.columns(2)
            with col1:
                component_name = st.text_input("Component Name", value="CustomComponent")
                component_purpose = st.text_area("Component Purpose", value="Describe what this component does")
                component_details = st.text_area("Implementation Details", value="")
            with col2:
                output_filename = st.text_input("Output File Name", value=f"{component_name.lower()}.py")
                
                if st.button("Generate Component"):
                    if component_name and component_purpose:
                        template_key = generate_custom_content(
                            content_type="component",
                            name=component_name,
                            purpose=component_purpose,
                            details=component_details
                        )
                        
                        if template_key:
                            st.session_state.current_template = template_key
                            
                            # Save to file if filename is provided
                            if output_filename:
                                save_content_to_file(template_key, output_filename)
                            
                            st.success("Component generated!")
                    else:
                        st.warning("Please provide a component name and purpose")
        
        # Generated content
        if st.session_state.generated_code:
            st.markdown("### Generated Content")
            
            # Use a selectbox for the generated content
            template_keys = list(st.session_state.generated_code.keys())
            template_names = [f"{st.session_state.generated_code[k]['name']}" for k in template_keys]
            
            selected_index = 0
            if hasattr(st.session_state, 'current_template'):
                if st.session_state.current_template in template_keys:
                    selected_index = template_keys.index(st.session_state.current_template)
            
            selected_template = st.selectbox(
                "Select Generated Content",
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
                            save_content_to_file(selected_template, save_filename)
                        else:
                            st.warning("Please provide a filename")
    
    with tab3:
        # Analysis tab
        st.subheader("Project Analysis")
        
        if st.session_state.current_project_type in ["fiction", "screenplay"]:
            # Creative project analysis
            st.write("Analyze your creative project for consistency and completeness.")
            
            # Project stats
            st.markdown("### Project Statistics")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Characters", len(roadmap.characters))
                char_with_arcs = sum(1 for char in roadmap.characters if char.get('arc'))
                st.metric("Characters with Arcs", f"{char_with_arcs}/{len(roadmap.characters)}")
            
            with col2:
                st.metric("Locations", len(roadmap.locations))
                st.metric("Themes", len(roadmap.themes))
            
            with col3:
                # Count scenes across all phases
                scene_count = 0
                for phase in roadmap.phases:
                    for task in phase.tasks:
                        if "scene_data" in task:
                            scene_count += 1
                
                st.metric("Total Scenes", scene_count)
                
                # Count phases with scenes
                phases_with_scenes = 0
                for phase in roadmap.phases:
                    has_scene = False
                    for task in phase.tasks:
                        if "scene_data" in task:
                            has_scene = True
                            break
                    if has_scene:
                        phases_with_scenes += 1
                
                st.metric("Phases with Scenes", f"{phases_with_scenes}/{len(roadmap.phases)}")
            
            # Character usage
            st.markdown("### Character Usage Analysis")
            
            character_scene_counts = {}
            for phase in roadmap.phases:
                for task in phase.tasks:
                    if "scene_data" in task:
                        for char_name in task["scene_data"].get("characters", []):
                            if char_name in character_scene_counts:
                                character_scene_counts[char_name] += 1
                            else:
                                character_scene_counts[char_name] = 1
            
            if character_scene_counts:
                char_data = []
                for char in roadmap.characters:
                    name = char["name"]
                    char_data.append({
                        "name": name,
                        "role": char["role"],
                        "scenes": character_scene_counts.get(name, 0)
                    })
                
                # Sort by scene count
                char_data.sort(key=lambda x: x["scenes"], reverse=True)
                
                # Create a bar chart
                char_names = [c["name"] for c in char_data]
                scene_counts = [c["scenes"] for c in char_data]
                
                # Display as a table
                st.write("Character scene appearances:")
                for char in char_data:
                    role_class = f"role-{char['role']}"
                    st.markdown(f"<span class='{role_class}'>{char['name']}</span>: {char['scenes']} scenes", unsafe_allow_html=True)
                
                # Recommendations
                st.markdown("### Recommendations")
                
                recommendations = []
                
                # Check for characters without arcs
                chars_no_arc = [char["name"] for char in roadmap.characters if not char.get('arc')]
                if chars_no_arc:
                    recommendations.append({
                        "title": "Add character arcs",
                        "details": f"Characters without defined arcs: {', '.join(chars_no_arc)}"
                    })
                
                # Check for characters not used in scenes
                chars_no_scenes = [char["name"] for char in roadmap.characters if char["name"] not in character_scene_counts]
                if chars_no_scenes:
                    recommendations.append({
                        "title": "Use all characters in scenes",
                        "details": f"Characters not appearing in any scenes: {', '.join(chars_no_scenes)}"
                    })
                
                # Check for phases without scenes
                phases_no_scenes = []
                structure_phases = [p for p in roadmap.phases 
                                  if p.name in [name for name, _ in STORY_TEMPLATES[st.session_state.current_story_structure]]]
                
                for phase in structure_phases:
                    has_scene = False
                    for task in phase.tasks:
                        if "scene_data" in task:
                            has_scene = True
                            break
                    if not has_scene:
                        phases_no_scenes.append(phase.name)
                
                if phases_no_scenes:
                    recommendations.append({
                        "title": "Add scenes to all story phases",
                        "details": f"Story phases without scenes: {', '.join(phases_no_scenes)}"
                    })
                
                # Display recommendations
                if recommendations:
                    for rec in recommendations:
                        st.markdown(f"**{rec['title']}**")
                        st.markdown(f"{rec['details']}")
                else:
                    st.success("No critical issues found in your project structure.")
                
                # AI analysis button
                if has_ai:
                    st.markdown("### AI-Powered Analysis")
                    
                    if st.button("Generate Detailed Analysis"):
                        st.info("AI analysis would go here. This would analyze your project for structure, pacing, character development, and theme consistency.")
                        
                        # This would normally call the creative bridge for analysis
                        if False:  # Placeholder for actual implementation
                            analysis = creative_bridge.analyze_writing_with_roadmap("sample_file.txt")
                            for suggestion in analysis.get("suggestions", []):
                                st.markdown(f"**{suggestion['title']}**")
                                st.markdown(f"{suggestion['details']}")
                
        else:
            # Software project analysis
            st.write("Analyze your software project for architectural consistency and completeness.")
            
            # Project stats
            st.markdown("### Project Statistics")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # Count components across all phases
                component_count = 0
                for phase in roadmap.phases:
                    component_count += len(phase.components)
                
                st.metric("Components", component_count)
                
                # Count components with dependencies
                components_with_deps = 0
                for phase in roadmap.phases:
                    for comp in phase.components:
                        if comp.get('dependencies'):
                            components_with_deps += 1
                
                st.metric("Components with Dependencies", components_with_deps)
            
            with col2:
                # Count requirements
                requirement_count = 0
                for phase in roadmap.phases:
                    requirement_count += len(phase.requirements)
                
                st.metric("Requirements", requirement_count)
                
                # Count requirements by type
                functional_reqs = 0
                non_functional_reqs = 0
                technical_reqs = 0
                
                for phase in roadmap.phases:
                    for req in phase.requirements:
                        if req.get('type') == 'functional':
                            functional_reqs += 1
                        elif req.get('type') == 'non_functional':
                            non_functional_reqs += 1
                        elif req.get('type') == 'technical':
                            technical_reqs += 1
                
                st.metric("Functional Requirements", functional_reqs)
                st.metric("Non-Functional Requirements", non_functional_reqs)
            
            with col3:
                # Count tasks
                task_count = 0
                for phase in roadmap.phases:
                    task_count += len(phase.tasks)
                
                st.metric("Tasks", task_count)
                
                # Calculate estimated hours
                total_hours = 0
                for phase in roadmap.phases:
                    for task in phase.tasks:
                        total_hours += task.get('estimated_hours', 0)
                
                st.metric("Estimated Hours", f"{total_hours:.1f}")
            
            # Dependency graph analysis
            st.markdown("### Component Dependency Analysis")
            
            # Create component dependency map
            components = {}
            for phase in roadmap.phases:
                for comp in phase.components:
                    name = comp.get('name', '')
                    if name:
                        components[name] = {
                            "dependencies": comp.get('dependencies', []),
                            "phase": phase.name
                        }
            
            if components:
                # Create an adjacency matrix
                component_names = list(components.keys())
                
                # Check for missing dependencies
                missing_deps = []
                for comp_name, comp_data in components.items():
                    for dep in comp_data["dependencies"]:
                        if dep not in components:
                            missing_deps.append((comp_name, dep))
                
                # Display dependencies
                st.write("Component dependencies:")
                for comp_name, comp_data in components.items():
                    if comp_data["dependencies"]:
                        st.markdown(f"**{comp_name}** depends on: {', '.join(comp_data['dependencies'])}")
                    else:
                        st.markdown(f"**{comp_name}** has no dependencies")
                
                # Recommendations
                st.markdown("### Recommendations")
                
                recommendations = []
                
                # Check for missing dependencies
                if missing_deps:
                    dep_list = [f"{comp} → {dep}" for comp, dep in missing_deps]
                    recommendations.append({
                        "title": "Fix missing dependencies",
                        "details": f"The following dependencies are referenced but not defined: {', '.join(dep_list)}"
                    })
                
                # Check for phases without components
                phases_no_components = []
                for phase in roadmap.phases:
                    if not phase.components and "Design" in phase.name or "Implementation" in phase.name:
                        phases_no_components.append(phase.name)
                
                if phases_no_components:
                    recommendations.append({
                        "title": "Add components to design/implementation phases",
                        "details": f"Phases without components: {', '.join(phases_no_components)}"
                    })
                
                # Check for phases without requirements
                phases_no_requirements = []
                for phase in roadmap.phases:
                    if not phase.requirements and "Requirements" in phase.name:
                        phases_no_requirements.append(phase.name)
                
                if phases_no_requirements:
                    recommendations.append({
                        "title": "Add requirements to requirements phase",
                        "details": f"Requirements phases without defined requirements: {', '.join(phases_no_requirements)}"
                    })
                
                # Display recommendations
                if recommendations:
                    for rec in recommendations:
                        st.markdown(f"**{rec['title']}**")
                        st.markdown(f"{rec['details']}")
                else:
                    st.success("No critical issues found in your project structure.")
                
                # AI analysis button
                if has_ai:
                    st.markdown("### AI-Powered Code Analysis")
                    
                    if st.button("Analyze Code Against Roadmap"):
                        st.info("AI analysis would go here. This would analyze your actual code against the roadmap to find inconsistencies and improvement opportunities.")
    
    with tab4:
        # Settings tab
        st.subheader("Settings")
        
        # Application settings
        st.markdown("### Application Settings")
        
        # Project type
        st.write(f"Current project type: **{st.session_state.current_project_type}**")
        
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
                
                # Determine the type of roadmap based on project_type
                project_type = roadmap_dict.get("project_type", "software")
                
                if project_type in ["fiction", "screenplay"]:
                    # Create a creative roadmap from the dict
                    roadmap = CreativeRoadmap.from_dict(roadmap_dict)
                else:
                    # Create a standard roadmap from the dict
                    roadmap = ProjectRoadmap.from_dict(roadmap_dict)
                
                # Set as current roadmap
                st.session_state.current_roadmap = roadmap
                st.session_state.current_project_type = project_type
                st.session_state.has_unsaved_changes = True
                
                # Set story structure if available
                if hasattr(roadmap, 'story_structure'):
                    st.session_state.current_story_structure = roadmap.story_structure
                
                st.success(f"Imported roadmap: {roadmap.name}")
                
                # Save the roadmap
                save_current_roadmap()
                
                # Update templates
                update_templates()
                
                # Refresh
                st.rerun()
            except Exception as e:
                st.error(f"Error importing roadmap: {str(e)}")
else:
    # Welcome page if no roadmap is loaded
    st.markdown("## Welcome to PyWrite Unified Roadmap Planning!")
    st.markdown("""
    This tool helps you plan your projects before starting to code or write, enhancing your productivity with:
    
    - 🧩 **Structured planning** for software, fiction, and screenplay projects
    - 🤖 **AI-powered content generation** based on your project plan
    - 📝 **Context-aware suggestions** via integration with autocomplete
    - 📊 **Project analysis** to identify gaps and opportunities
    
    To get started, select a project type above and create a new project or load an existing one.
    """)
    
    st.markdown("### Project Types")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-box">
            <div class="feature-title">Software Projects</div>
            <ul>
                <li>Requirements management</li>
                <li>Component architecture</li>
                <li>Task tracking</li>
                <li>Code generation</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-box">
            <div class="feature-title">Fiction Projects</div>
            <ul>
                <li>Story structure templates</li>
                <li>Character development</li>
                <li>Scene planning</li>
                <li>Theme integration</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-box">
            <div class="feature-title">Screenplay Projects</div>
            <ul>
                <li>Script structure templates</li>
                <li>Character & dialogue</li>
                <li>Scene breakdown</li>
                <li>Format-aware generation</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("### Integrated with PyWrite Features")
    st.markdown("""
    The Roadmap Planning System integrates with other PyWrite features:
    
    - **Autocomplete**: Get project-aware code and text suggestions
    - **Sidecar AI Assistant**: Contextual help based on your project plan
    - **Multi-Modal Interface**: Voice commands for roadmap navigation
    """)

# Footer
st.markdown("---")
st.markdown("PyWrite Unified Roadmap Planning System | Built with Streamlit")

# Main function when run directly
if __name__ == "__main__":
    pass