#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyWrite Roadmap Demo

This script demonstrates the PyWrite Roadmap Planning System functionality 
with some sample roadmaps and shows how it can be used with the autocomplete system.

Author: PyWrite
Date: 2025-03-28
"""

import os
import json
import uuid
import datetime
from typing import Dict, List, Any, Optional, Union

from project_roadmap import ProjectRoadmap, RoadmapPhase, get_roadmap_manager
from roadmap_autocomplete_bridge import RoadmapAutocompleteBridge

# Print banner
def print_banner():
    """Print the demo banner."""
    print("=" * 80)
    print("                   PyWrite Roadmap Planning System Demo")
    print("=" * 80)
    print("This demo will showcase the roadmap planning system and its integration with autocomplete.")
    print("=" * 80)
    print()

# Create a sample roadmap
def create_sample_roadmap() -> str:
    """
    Create a sample roadmap and save it to the database.
    
    Returns:
        Roadmap ID
    """
    print("Creating a sample roadmap...")
    
    # Create a web application roadmap
    roadmap = ProjectRoadmap(
        name="PyWrite Web Application",
        description="A web-based code editor with AI-powered features",
        project_type="software"
    )
    
    # Access the first phase (Requirements)
    if roadmap.phases:
        req_phase = roadmap.phases[0]
        
        # Add requirements
        req_phase.add_requirement(
            title="User Authentication",
            description="Users should be able to register, log in, and log out. Support for OAuth providers.",
            requirement_type="functional",
            priority="high"
        )
        
        req_phase.add_requirement(
            title="Code Editor Interface",
            description="A web-based editor with syntax highlighting, autocomplete, and error checking",
            requirement_type="functional",
            priority="high"
        )
        
        req_phase.add_requirement(
            title="AI Assistance",
            description="AI-powered code suggestions, error fixing, and documentation generation",
            requirement_type="functional",
            priority="medium"
        )
        
        req_phase.add_requirement(
            title="Responsive Design",
            description="The application should work well on desktop and tablet devices",
            requirement_type="non_functional",
            priority="medium"
        )
        
        # Mark phase as completed
        req_phase.update_status("completed")
    
    # Access the design phase
    if len(roadmap.phases) > 1:
        design_phase = roadmap.phases[1]
        
        # Add components
        design_phase.add_component(
            name="AuthService",
            purpose="Manage user authentication and session handling",
            implementation_details="Use JWT tokens for authentication, with refresh token mechanism"
        )
        
        design_phase.add_component(
            name="CodeEditorComponent",
            purpose="Handle code editing, highlighting, and user input",
            implementation_details="Use CodeMirror or Monaco Editor as the base, with custom extensions"
        )
        
        design_phase.add_component(
            name="AIAssistant",
            purpose="Provide AI-powered code assistance",
            implementation_details="Integrate with OpenAI API for code suggestions and improvements",
            dependencies=["CodeEditorComponent"]
        )
        
        design_phase.add_component(
            name="ProjectManager",
            purpose="Manage user projects and files",
            implementation_details="Handle file operations, project structure, and versioning",
            dependencies=["AuthService"]
        )
        
        # Mark phase as in progress
        design_phase.update_status("in_progress")
    
    # Access the implementation phase
    if len(roadmap.phases) > 2:
        impl_phase = roadmap.phases[2]
        
        # Add tasks
        impl_phase.add_task(
            title="Set up project structure",
            description="Initialize the project with proper directory structure and base files",
            priority="high",
            estimated_hours=2.0
        )
        
        impl_phase.add_task(
            title="Implement AuthService",
            description="Create the authentication service with login, registration, and token handling",
            priority="high",
            estimated_hours=8.0
        )
        
        impl_phase.add_task(
            title="Integrate code editor library",
            description="Add the code editor library and configure basic features",
            priority="high",
            estimated_hours=6.0
        )
        
        impl_phase.add_task(
            title="Create AI assistant integration",
            description="Connect to OpenAI API and implement basic code assistance",
            priority="medium",
            estimated_hours=10.0
        )
    
    # Add tags to the roadmap
    roadmap.add_tag("web")
    roadmap.add_tag("editor")
    roadmap.add_tag("ai")
    
    # Save roadmap
    manager = get_roadmap_manager()
    success = manager.save_roadmap(roadmap)
    
    if success:
        print(f"✓ Created sample roadmap: '{roadmap.name}' with ID: {roadmap.id}")
        print(f"✓ The roadmap has {len(roadmap.phases)} phases")
        return roadmap.id
    else:
        print("✗ Failed to create sample roadmap")
        return None

# Demo the roadmap-autocomplete bridge
def demo_autocomplete_bridge(roadmap_id: str):
    """
    Demonstrate the roadmap-autocomplete bridge functionality.
    
    Args:
        roadmap_id: ID of the roadmap to use
    """
    print("\nDemonstrating roadmap-autocomplete integration...")
    
    # Create the bridge
    bridge = RoadmapAutocompleteBridge(roadmap_id)
    
    if not bridge.roadmap:
        print("✗ Failed to load roadmap")
        return
    
    print(f"✓ Loaded roadmap: {bridge.roadmap.name}")
    print(f"✓ Extracted {len(bridge.component_hierarchy)} components")
    print(f"✓ Extracted {len(bridge.function_signatures)} function signatures")
    
    # Show component hierarchy
    print("\nComponent Hierarchy:")
    print("-----------------")
    for component, info in bridge.component_hierarchy.items():
        children = ", ".join(info["children"]) if info["children"] else "None"
        print(f"• {component} (Level: {info['level']}, Children: {children})")
    
    # Demonstrate code suggestions
    print("\nCode Suggestion Examples:")
    print("-----------------------")
    
    # Example 1: Class definition
    code1 = "class "
    completions1 = bridge.get_roadmap_completions("python", code1, len(code1))
    print("\nWhen typing 'class ':")
    for comp in completions1[:3]:
        print(f"• {comp['display_text']} - {comp['description']}")
    
    # Example 2: Inside a class
    code2 = "class MyClass:\n    def __init__(self):\n        self."
    completions2 = bridge.get_roadmap_completions("python", code2, len(code2))
    print("\nWhen typing 'self.' inside a class:")
    for comp in completions2[:3]:
        print(f"• {comp['display_text']} - {comp['description']}")
    
    # Example 3: Function call
    code3 = "def main():\n    "
    completions3 = bridge.get_roadmap_completions("python", code3, len(code3))
    print("\nWhen typing in a new function:")
    for comp in completions3[:3]:
        print(f"• {comp['display_text']} - {comp['description']}")
    
    # Generate component code example
    if bridge.component_hierarchy:
        component_name = next(iter(bridge.component_hierarchy.keys()))
        print(f"\nGenerating code for component: {component_name}")
        print("------------------------------------")
        
        if not bridge.has_openai:
            print("✗ OpenAI API key not available. Component code generation requires OpenAI.")
            print("  To enable this feature, set the OPENAI_API_KEY environment variable.")
            
            # Generate a simple component template instead
            template = f"""class {component_name}:
    \"\"\"
    {component_name} component from the PyWrite Web Application roadmap.
    
    This is a placeholder implementation. For a complete implementation,
    run the demo with an OpenAI API key.
    \"\"\"
    
    def __init__(self):
        \"\"\"Initialize the component.\"\"\"
        pass
        
    def authenticate(self, username, password):
        \"\"\"Example authentication method.\"\"\"
        return True
"""
            # Save the template to a file
            filename = f"{component_name.lower()}.py"
            with open(filename, 'w') as f:
                f.write(template)
            print(f"✓ Created simple template for {component_name} in {filename}")
        else:
            component_code = bridge.generate_component_from_roadmap(component_name)
            if component_code:
                # Show a snippet of the generated code
                code_lines = component_code.split('\n')
                displayed_lines = code_lines[:15]  # Show first 15 lines
                print('\n'.join(displayed_lines))
                
                if len(code_lines) > 15:
                    print("... (truncated)")
                    
                print(f"\n✓ Generated {len(code_lines)} lines of code for {component_name}")
                
                # Save the code to a file
                filename = f"{component_name.lower()}.py"
                with open(filename, 'w') as f:
                    f.write(component_code)
                print(f"✓ Saved generated code to {filename}")
            else:
                print("✗ Failed to generate component code. Check logs for details.")

# Demo file analysis
def demo_file_analysis(roadmap_id: str, file_path: str):
    """
    Demonstrate analyzing a file against the roadmap.
    
    Args:
        roadmap_id: ID of the roadmap to use
        file_path: Path to the file to analyze
    """
    print("\nDemonstrating file analysis...")
    
    # Create the bridge
    bridge = RoadmapAutocompleteBridge(roadmap_id)
    
    if not bridge.roadmap:
        print("✗ Failed to load roadmap")
        return
    
    if not os.path.exists(file_path):
        print(f"✗ File not found: {file_path}")
        return
    
    print(f"✓ Analyzing file: {file_path}")
    
    # Analyze the file
    results = bridge.analyze_file_with_roadmap(file_path)
    
    if 'error' in results:
        print(f"✗ Analysis error: {results['error']}")
        return
    
    # Print analysis results
    print("\nAnalysis Results:")
    print("----------------")
    
    # Components
    print("\nComponents found:")
    if results["components"]:
        for comp in results["components"]:
            status = "In roadmap" if comp["in_roadmap"] else "Not in roadmap"
            print(f"• {comp['name']} (Line {comp['line']}) - {status}")
    else:
        print("• No components found")
    
    # Functions
    print("\nFunctions found:")
    if results["functions"]:
        for func in results["functions"]:
            status = "In roadmap" if func["in_roadmap"] else "Not in roadmap"
            print(f"• {func['name']} (Line {func['line']}) - {status}")
    else:
        print("• No functions found")
    
    # Inconsistencies
    print("\nInconsistencies:")
    if results["inconsistencies"]:
        for inconsistency in results["inconsistencies"]:
            if inconsistency["type"] == "missing_dependencies":
                print(f"• Component {inconsistency['component']} is missing dependencies: {', '.join(inconsistency['missing'])}")
    else:
        print("• No inconsistencies found")
    
    # Suggestions
    print("\nImprovement Suggestions:")
    if results["suggestions"]:
        for i, suggestion in enumerate(results["suggestions"], 1):
            print(f"• {suggestion.get('title', f'Suggestion {i}')}")
            print(f"  {suggestion.get('details', 'No details provided')}")
            print()
    else:
        print("• No suggestions available")

# Main function
def main():
    """Main function to run the demo."""
    print_banner()
    
    # Create a sample roadmap
    roadmap_id = create_sample_roadmap()
    
    if roadmap_id:
        # Demonstrate autocomplete bridge
        demo_autocomplete_bridge(roadmap_id)
        
        # If we generated a component file, analyze it
        component_file = "authservice.py"
        if os.path.exists(component_file):
            demo_file_analysis(roadmap_id, component_file)
        
        print("\nDemo Completed!")
        print("===============")
        print("To explore the roadmap system more in depth:")
        print("1. Run: ./pywrite.sh roadmap")
        print("2. Load the sample roadmap we just created")
        print("3. Create your own roadmaps and see how they integrate with coding")
    else:
        print("\nDemo failed to run properly. Please check the database connection.")

# Run the demo
if __name__ == "__main__":
    main()