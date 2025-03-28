#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyWrite Roadmap-Autocomplete Integration Bridge

This module integrates the roadmap planning system with the autocomplete engine:
- Extracts coding patterns and context from roadmap
- Provides roadmap-aware code suggestions
- Enables component-based completion
- Informs AI generation with project requirements

Author: PyWrite
Date: 2025-03-28
"""

import os
import re
import ast
import json
import logging
from typing import Dict, List, Tuple, Any, Optional, Union, Set

# Import PyWrite modules
from project_roadmap import ProjectRoadmap, RoadmapPhase, get_roadmap_manager
from database_helper import get_db_instance
from autocomplete_engine import AutocompleteEngine
try:
    from continuous_coding import get_continuous_coding_engine
    has_ai = True
except ImportError:
    has_ai = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('roadmap_bridge.log')
    ]
)

logger = logging.getLogger('PyWrite.RoadmapBridge')


class RoadmapAutocompleteBridge:
    """Integrates roadmap planning with code autocomplete."""
    
    def __init__(self, roadmap_id: Optional[str] = None):
        """
        Initialize the bridge.
        
        Args:
            roadmap_id: Optional ID of a specific roadmap to use
        """
        self.db = get_db_instance()
        self.roadmap_manager = get_roadmap_manager()
        self.autocomplete = AutocompleteEngine()
        
        # Initialize OpenAI if available
        if has_ai:
            api_key = os.environ.get("OPENAI_API_KEY")
            self.continuous_coding = get_continuous_coding_engine(api_key)
            self.has_openai = self.continuous_coding.has_openai
        else:
            self.continuous_coding = None
            self.has_openai = False
        
        # Set the current roadmap if provided
        self.roadmap_id = roadmap_id
        self.roadmap = None
        if roadmap_id:
            self.set_roadmap(roadmap_id)
        
        # Track completions extracted from the roadmap
        self.roadmap_completions = {}
        self.component_hierarchy = {}
        self.function_signatures = {}
        self.variable_types = {}
        
        # Extract patterns from roadmap if available
        if self.roadmap:
            self._extract_patterns_from_roadmap()
    
    def set_roadmap(self, roadmap_id: str) -> bool:
        """
        Set the current roadmap.
        
        Args:
            roadmap_id: ID of the roadmap to use
            
        Returns:
            Success status
        """
        roadmap = self.roadmap_manager.get_roadmap(roadmap_id)
        if roadmap:
            self.roadmap = roadmap
            self.roadmap_id = roadmap_id
            self._extract_patterns_from_roadmap()
            return True
        return False
    
    def _extract_patterns_from_roadmap(self) -> None:
        """Extract coding patterns from the roadmap."""
        if not self.roadmap:
            return
        
        logger.info(f"Extracting patterns from roadmap: {self.roadmap.name}")
        
        # Extract components first
        self._extract_components()
        
        # Extract function signatures based on requirements
        self._extract_function_signatures()
        
        # Convert the extracted patterns to completions
        self._convert_to_completions()
    
    def _extract_components(self) -> None:
        """Extract component definitions from the roadmap."""
        component_map = {}  # name -> definition
        dependency_map = {}  # name -> list of dependencies
        
        # Go through all phases to collect components
        for phase in self.roadmap.phases:
            for component in phase.components:
                name = component.get('name', '')
                if not name:
                    continue
                
                # Store the component definition
                component_map[name] = component
                
                # Store dependencies
                dependencies = component.get('dependencies', [])
                if dependencies:
                    dependency_map[name] = dependencies
        
        # Build component hierarchy from dependencies
        hierarchy = {}
        
        # Start with components that have no dependencies
        for name, component in component_map.items():
            if name not in dependency_map or not dependency_map[name]:
                hierarchy[name] = {"level": 0, "children": []}
        
        # Now propagate through the dependencies
        max_iterations = len(component_map)  # Avoid infinite loops
        iteration = 0
        while iteration < max_iterations:
            made_progress = False
            
            for name, dependencies in dependency_map.items():
                # Skip if already in hierarchy
                if name in hierarchy:
                    continue
                
                # Check if all dependencies are in hierarchy
                all_deps_in_hierarchy = all(dep in hierarchy for dep in dependencies)
                
                if all_deps_in_hierarchy:
                    # Calculate the level (max dependency level + 1)
                    level = max(hierarchy[dep]["level"] for dep in dependencies) + 1
                    
                    # Add to hierarchy
                    hierarchy[name] = {"level": level, "children": []}
                    
                    # Add as child to each parent
                    for dep in dependencies:
                        hierarchy[dep]["children"].append(name)
                    
                    made_progress = True
            
            if not made_progress:
                # Handle any circular dependencies
                for name, dependencies in dependency_map.items():
                    if name not in hierarchy:
                        # Add with an arbitrary level
                        hierarchy[name] = {"level": 100, "children": []}
                        logger.warning(f"Possible circular dependency for component: {name}")
            
            iteration += 1
        
        # Store the results
        self.component_hierarchy = hierarchy
    
    def _extract_function_signatures(self) -> None:
        """Extract function signatures from requirements."""
        signatures = {}
        
        # Go through all phases to collect requirements
        for phase in self.roadmap.phases:
            for req in phase.requirements:
                # Only process functional requirements
                if req.get('type') != 'functional':
                    continue
                
                title = req.get('title', '')
                description = req.get('description', '')
                
                # Generate function signature from the requirement
                if self.has_openai:
                    try:
                        func_sig = self._generate_function_signature(title, description)
                        if func_sig:
                            signatures[func_sig['name']] = func_sig
                    except Exception as e:
                        logger.error(f"Error generating function signature: {str(e)}")
        
        # Store the results
        self.function_signatures = signatures
    
    def _generate_function_signature(self, title: str, description: str) -> Optional[Dict]:
        """
        Generate a function signature from a requirement.
        
        Args:
            title: Requirement title
            description: Requirement description
            
        Returns:
            Dictionary with function signature details or None
        """
        if not self.has_openai:
            return None
        
        try:
            # Prepare prompt for function signature generation
            prompt = (
                f"Based on the following requirement, generate a Python function signature "
                f"including parameter types and return type. The function should implement "
                f"the requirement as efficiently as possible.\n\n"
                f"Requirement title: {title}\n"
                f"Requirement description: {description}\n\n"
                f"Respond with a JSON object containing:\n"
                f"1. The function name (name)\n"
                f"2. The function parameters with types (parameters)\n"
                f"3. The return type (return_type)\n"
                f"4. A brief docstring (docstring)\n"
                f"5. The full function signature as it would appear in code (signature)\n"
                f"\nMake the function name clear and descriptive, using snake_case."
            )
            
            # Call OpenAI API
            response = self.continuous_coding.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            # Parse the response
            result = json.loads(response.choices[0].message.content)
            
            # Make sure it has all required fields
            if not all(key in result for key in ["name", "parameters", "return_type", "docstring", "signature"]):
                logger.warning(f"Incomplete function signature generated for: {title}")
                return None
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating function signature: {str(e)}")
            return None
    
    def _convert_to_completions(self) -> None:
        """Convert extracted patterns to completion suggestions."""
        completions = {}
        
        # Generate completions from component hierarchy
        for name, info in self.component_hierarchy.items():
            # Class definition
            class_template = f"class {name}:\n    \"\"\"Component from {self.roadmap.name} roadmap.\"\"\"\n    \n    def __init__(self):\n        pass"
            completions[f"class {name}"] = {
                "text": class_template,
                "display_text": f"class {name}",
                "type": "roadmap_component",
                "description": f"Component from project roadmap",
                "score": 95,
                "prefix_match": len(f"class {name}")
            }
            
            # Instance creation
            instance_template = f"{name.lower()} = {name}()"
            completions[f"{name.lower()} = "] = {
                "text": instance_template,
                "display_text": instance_template,
                "type": "roadmap_component",
                "description": f"Create instance of {name}",
                "score": 90,
                "prefix_match": len(f"{name.lower()} = ")
            }
        
        # Generate completions from function signatures
        for name, func in self.function_signatures.items():
            # Full function definition
            completions[f"def {name}"] = {
                "text": func["signature"],
                "display_text": f"def {name}(...)",
                "type": "roadmap_function",
                "description": func["docstring"],
                "score": 95,
                "prefix_match": len(f"def {name}")
            }
            
            # Function call
            params = ", ".join(func["parameters"].keys())
            completions[f"{name}("] = {
                "text": f"{name}({params})",
                "display_text": f"{name}({params})",
                "type": "roadmap_function",
                "description": func["docstring"],
                "score": 90,
                "prefix_match": len(f"{name}(")
            }
        
        # Store the completions
        self.roadmap_completions = completions
    
    def get_roadmap_completions(self, 
                               language: str, 
                               current_code: str, 
                               cursor_position: int) -> List[Dict]:
        """
        Get code completions based on the roadmap.
        
        Args:
            language: Programming language
            current_code: Current code text
            cursor_position: Position of the cursor
            
        Returns:
            List of completion suggestions
        """
        if not self.roadmap or language != "python":
            return []
        
        # Get the text up to the cursor position
        code_context = current_code[:cursor_position]
        
        # Extract the last line and the last "word" being typed
        last_line = code_context.split('\n')[-1] if '\n' in code_context else code_context
        last_word_match = re.search(r'[\w.]+$', last_line)
        last_word = last_word_match.group(0) if last_word_match else ""
        
        completions = []
        
        # Look for completions in our roadmap patterns
        for pattern, comp in self.roadmap_completions.items():
            if pattern.startswith(last_word):
                completions.append(comp)
        
        return sorted(completions, key=lambda x: (-x['score'], -x['prefix_match']))
    
    def enhance_autocomplete(self, 
                            language: str, 
                            current_code: str, 
                            cursor_position: int,
                            file_content: str = "",
                            filename: str = None) -> List[Dict]:
        """
        Enhance autocomplete suggestions with roadmap information.
        
        Args:
            language: Programming language
            current_code: Current code text
            cursor_position: Position of the cursor
            file_content: Full content of the file (for context)
            filename: Name of the file being edited
            
        Returns:
            Enhanced list of completion suggestions
        """
        # Get normal autocomplete suggestions
        standard_completions = self.autocomplete.get_completions(
            language=language,
            current_code=current_code,
            cursor_position=cursor_position,
            file_content=file_content,
            filename=filename
        )
        
        # Get roadmap-based completions
        roadmap_completions = self.get_roadmap_completions(
            language=language,
            current_code=current_code,
            cursor_position=cursor_position
        )
        
        # Combine the two sets of completions, prioritizing roadmap ones
        all_completions = roadmap_completions + standard_completions
        
        # Deduplicate (keep the first occurrence, which will be from roadmap if present)
        seen_displays = set()
        unique_completions = []
        
        for comp in all_completions:
            display = comp['display_text']
            if display not in seen_displays:
                seen_displays.add(display)
                unique_completions.append(comp)
        
        # Return the deduplicated, combined list
        return unique_completions
    
    def analyze_file_with_roadmap(self, file_path: str) -> Dict:
        """
        Analyze a file using the roadmap context.
        
        Args:
            file_path: Path to the file to analyze
            
        Returns:
            Analysis results
        """
        if not self.roadmap:
            return {"error": "No roadmap loaded"}
        
        try:
            # Read the file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Get roadmap context
            context = self.roadmap.generate_code_context()
            
            results = {
                "file_path": file_path,
                "roadmap_name": self.roadmap.name,
                "components": [],
                "functions": [],
                "imports": [],
                "inconsistencies": [],
                "suggestions": []
            }
            
            # If Python file, parse it for deeper analysis
            if file_path.endswith('.py'):
                try:
                    # Parse the file
                    tree = ast.parse(content)
                    
                    # Extract classes
                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef):
                            # Check if this class matches a roadmap component
                            class_name = node.name
                            if class_name in self.component_hierarchy:
                                results["components"].append({
                                    "name": class_name,
                                    "line": node.lineno,
                                    "in_roadmap": True
                                })
                                
                                # Check for missing dependencies
                                if class_name in self.component_hierarchy:
                                    # Check dependencies based on class attributes/imports
                                    dependencies = self._extract_dependencies(node)
                                    roadmap_deps = self._get_component_dependencies(class_name)
                                    
                                    # Find missing dependencies
                                    missing_deps = set(roadmap_deps) - set(dependencies)
                                    if missing_deps:
                                        results["inconsistencies"].append({
                                            "type": "missing_dependencies",
                                            "component": class_name,
                                            "missing": list(missing_deps),
                                            "line": node.lineno
                                        })
                            else:
                                # Class exists in code but not in roadmap
                                results["components"].append({
                                    "name": class_name,
                                    "line": node.lineno,
                                    "in_roadmap": False
                                })
                    
                    # Extract functions and compare with roadmap signatures
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            func_name = node.name
                            results["functions"].append({
                                "name": func_name,
                                "line": node.lineno,
                                "in_roadmap": func_name in self.function_signatures
                            })
                    
                    # Generate suggestions based on analysis
                    if self.has_openai:
                        suggestions = self._generate_improvement_suggestions(
                            content, results, context
                        )
                        if suggestions:
                            results["suggestions"] = suggestions
                
                except SyntaxError as e:
                    results["error"] = f"Syntax error in file: {str(e)}"
                except Exception as e:
                    results["error"] = f"Error analyzing file: {str(e)}"
            
            return results
            
        except Exception as e:
            logger.error(f"Error analyzing file with roadmap: {str(e)}")
            return {"error": str(e)}
    
    def _extract_dependencies(self, class_node) -> List[str]:
        """
        Extract dependencies from a class definition.
        
        Args:
            class_node: AST class definition node
            
        Returns:
            List of dependency names
        """
        dependencies = []
        
        # Check class attributes
        for node in ast.walk(class_node):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        # Check if the value is an instance of a roadmap component
                        if isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name):
                            instance_type = node.value.func.id
                            if instance_type in self.component_hierarchy:
                                dependencies.append(instance_type)
        
        return dependencies
    
    def _get_component_dependencies(self, component_name: str) -> List[str]:
        """
        Get the dependencies of a component from the roadmap.
        
        Args:
            component_name: Name of the component
            
        Returns:
            List of dependency names
        """
        # Go through all phases to find the component
        for phase in self.roadmap.phases:
            for component in phase.components:
                if component.get('name') == component_name:
                    return component.get('dependencies', [])
        
        return []
    
    def _generate_improvement_suggestions(self, 
                                         content: str, 
                                         analysis: Dict, 
                                         context: Dict) -> List[Dict]:
        """
        Generate improvement suggestions based on analysis and roadmap.
        
        Args:
            content: File content
            analysis: Analysis results
            context: Roadmap context
            
        Returns:
            List of suggestions
        """
        if not self.has_openai:
            return []
        
        try:
            # Prepare prompt for suggestions
            prompt = (
                f"You are analyzing a Python file for a project called '{context['project_name']}'. "
                f"Project description: {context['project_description']}\n\n"
                f"Here is the current code:\n```python\n{content}\n```\n\n"
                f"Based on the project roadmap, I've analyzed the code and found these components "
                f"and functions:\n\n"
            )
            
            # Add components info
            prompt += "Components in code:\n"
            for comp in analysis["components"]:
                prompt += f"- {comp['name']} (line {comp['line']}) - "
                prompt += "Defined in roadmap" if comp['in_roadmap'] else "Not in roadmap"
                prompt += "\n"
            
            # Add functions info
            prompt += "\nFunctions in code:\n"
            for func in analysis["functions"]:
                prompt += f"- {func['name']} (line {func['line']}) - "
                prompt += "Defined in roadmap" if func['in_roadmap'] else "Not in roadmap"
                prompt += "\n"
            
            # Add inconsistencies
            if analysis["inconsistencies"]:
                prompt += "\nInconsistencies:\n"
                for inconsistency in analysis["inconsistencies"]:
                    if inconsistency["type"] == "missing_dependencies":
                        prompt += f"- Component {inconsistency['component']} is missing dependencies: "
                        prompt += ", ".join(inconsistency["missing"])
                        prompt += f" (line {inconsistency['line']})\n"
            
            # Add roadmap components that should be implemented
            missing_comps = []
            for name in self.component_hierarchy.keys():
                if name not in [c["name"] for c in analysis["components"] if c["in_roadmap"]]:
                    missing_comps.append(name)
            
            if missing_comps:
                prompt += "\nComponents defined in roadmap but missing in code:\n"
                for comp in missing_comps:
                    prompt += f"- {comp}\n"
            
            # Add request for suggestions
            prompt += (
                "\nBased on this analysis, provide concrete suggestions for improving the code "
                "to better align with the roadmap. Focus on architectural improvements, missing "
                "components, and implementation details. Provide 3-5 specific, actionable suggestions."
                "\n\nReturn your response as a JSON array of suggestion objects, each with 'title' and 'details' fields."
            )
            
            # Call OpenAI API
            response = self.continuous_coding.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                response_format={"type": "json_object"}
            )
            
            # Parse the response
            result = json.loads(response.choices[0].message.content)
            
            # Return the suggestions
            return result.get("suggestions", [])
            
        except Exception as e:
            logger.error(f"Error generating improvement suggestions: {str(e)}")
            return []
    
    def generate_component_from_roadmap(self, component_name: str) -> Optional[str]:
        """
        Generate code for a component defined in the roadmap.
        
        Args:
            component_name: Name of the component to generate
            
        Returns:
            Generated code or None if generation failed
        """
        if not self.roadmap or not self.has_openai:
            return None
        
        # Find the component in the roadmap
        component = None
        for phase in self.roadmap.phases:
            for comp in phase.components:
                if comp.get('name') == component_name:
                    component = comp
                    break
            if component:
                break
        
        if not component:
            logger.warning(f"Component {component_name} not found in roadmap")
            return None
        
        try:
            # Get roadmap context
            context = self.roadmap.generate_code_context()
            
            # Prepare prompt for component generation
            prompt = (
                f"You are generating a Python class for a component in a project called '{context['project_name']}'. "
                f"Project description: {context['project_description']}\n\n"
                f"Component name: {component_name}\n"
                f"Component purpose: {component.get('purpose', 'No purpose specified')}\n"
                f"Implementation details: {component.get('implementation_details', 'No details specified')}\n"
            )
            
            # Add dependencies
            dependencies = component.get('dependencies', [])
            if dependencies:
                prompt += f"Dependencies: {', '.join(dependencies)}\n\n"
                
                # Add details about each dependency
                prompt += "Dependency details:\n"
                for dep_name in dependencies:
                    for phase in self.roadmap.phases:
                        for dep in phase.components:
                            if dep.get('name') == dep_name:
                                prompt += f"- {dep_name}: {dep.get('purpose', 'No purpose specified')}\n"
                                break
            
            # Add request for code generation
            prompt += (
                "\nGenerate a complete, well-documented Python class for this component. "
                "Include appropriate methods based on the component's purpose. "
                "Make sure to implement dependency relationships correctly. "
                "Add detailed docstrings for the class and all methods. "
                "Do NOT include any imports or logging setup - just generate the class definition."
            )
            
            # Call OpenAI API
            response = self.continuous_coding.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=2000
            )
            
            # Extract the code from the response
            code = response.choices[0].message.content
            
            # If the response contains code blocks, extract the first one
            if "```" in code:
                code_blocks = re.findall(r"```(?:python)?\n(.*?)\n```", code, re.DOTALL)
                if code_blocks:
                    code = code_blocks[0]
            
            return code
            
        except Exception as e:
            logger.error(f"Error generating component code: {str(e)}")
            return None
    
    def generate_function_from_roadmap(self, function_name: str) -> Optional[str]:
        """
        Generate code for a function defined in the roadmap.
        
        Args:
            function_name: Name of the function to generate
            
        Returns:
            Generated code or None if generation failed
        """
        if not self.roadmap or not self.has_openai:
            return None
        
        # Find the function in the signatures
        if function_name not in self.function_signatures:
            logger.warning(f"Function {function_name} not found in roadmap")
            return None
        
        func_sig = self.function_signatures[function_name]
        
        try:
            # Get roadmap context
            context = self.roadmap.generate_code_context()
            
            # Prepare prompt for function generation
            prompt = (
                f"You are generating a Python function for a project called '{context['project_name']}'. "
                f"Project description: {context['project_description']}\n\n"
                f"Function name: {function_name}\n"
                f"Signature: {func_sig['signature']}\n"
                f"Docstring: {func_sig['docstring']}\n"
                f"Parameters: {json.dumps(func_sig['parameters'])}\n"
                f"Return type: {func_sig['return_type']}\n\n"
            )
            
            # Add requirements related to this function
            related_reqs = []
            for phase in self.roadmap.phases:
                for req in phase.requirements:
                    if req.get('type') == 'functional' and function_name.lower() in req.get('title', '').lower():
                        related_reqs.append(req)
            
            if related_reqs:
                prompt += "Related requirements:\n"
                for req in related_reqs:
                    prompt += f"- {req.get('title')}: {req.get('description')}\n"
            
            # Add request for code generation
            prompt += (
                "\nImplement this function completely, following the provided signature and docstring. "
                "Include proper error handling and comments where appropriate. "
                "Do NOT include any imports - just generate the function definition."
            )
            
            # Call OpenAI API
            response = self.continuous_coding.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=1500
            )
            
            # Extract the code from the response
            code = response.choices[0].message.content
            
            # If the response contains code blocks, extract the first one
            if "```" in code:
                code_blocks = re.findall(r"```(?:python)?\n(.*?)\n```", code, re.DOTALL)
                if code_blocks:
                    code = code_blocks[0]
            
            return code
            
        except Exception as e:
            logger.error(f"Error generating function code: {str(e)}")
            return None
    
    def get_framework_suggestions(self) -> List[Dict]:
        """
        Get suggestions for frameworks and libraries based on the roadmap.
        
        Returns:
            List of framework suggestions
        """
        if not self.roadmap or not self.has_openai:
            return []
        
        try:
            # Get roadmap context
            context = self.roadmap.generate_code_context()
            
            # Prepare prompt for framework suggestions
            prompt = (
                f"You are suggesting Python frameworks and libraries for a project called '{context['project_name']}'. "
                f"Project description: {context['project_description']}\n"
                f"Project type: {context['project_type']}\n\n"
            )
            
            # Add components info
            prompt += "Components defined in the project:\n"
            for comp in context.get('components', []):
                prompt += f"- {comp.get('name')}: {comp.get('purpose', 'No purpose specified')}\n"
            
            # Add requirements info
            prompt += "\nRequirements defined in the project:\n"
            for req in context.get('requirements', []):
                prompt += f"- {req.get('title')}: {req.get('description', 'No description specified')} "
                prompt += f"(Type: {req.get('type')}, Priority: {req.get('priority')})\n"
            
            # Add request for framework suggestions
            prompt += (
                "\nBased on this project information, suggest appropriate Python frameworks and libraries "
                "that would be useful for implementation. For each suggestion, provide:\n"
                "1. The name of the framework/library\n"
                "2. What it would be used for in this specific project\n"
                "3. Why it's a good fit for this project\n"
                "4. A brief example of how it might be used in this project\n\n"
                "Suggest 3-5 frameworks/libraries that would be most valuable for this specific project. "
                "\n\nReturn your response as a JSON array of framework objects, each with 'name', 'purpose', 'rationale', and 'example' fields."
            )
            
            # Call OpenAI API
            response = self.continuous_coding.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                response_format={"type": "json_object"}
            )
            
            # Parse the response
            result = json.loads(response.choices[0].message.content)
            
            # Return the framework suggestions
            return result.get("frameworks", [])
            
        except Exception as e:
            logger.error(f"Error generating framework suggestions: {str(e)}")
            return []


# Example usage
if __name__ == "__main__":
    import sys
    
    print("PyWrite Roadmap-Autocomplete Bridge")
    
    # Get roadmap ID from command line if provided
    roadmap_id = sys.argv[1] if len(sys.argv) > 1 else None
    
    # Initialize the bridge
    bridge = RoadmapAutocompleteBridge(roadmap_id)
    
    if not roadmap_id:
        # List available roadmaps
        roadmap_manager = get_roadmap_manager()
        roadmaps = roadmap_manager.list_roadmaps()
        
        print(f"\nAvailable roadmaps:")
        for i, roadmap in enumerate(roadmaps):
            print(f"{i+1}. {roadmap['name']} (ID: {roadmap['id']})")
        
        if roadmaps:
            # Select a roadmap
            selection = input("\nSelect a roadmap number (or press Enter to skip): ")
            if selection.isdigit() and 1 <= int(selection) <= len(roadmaps):
                selected_roadmap = roadmaps[int(selection) - 1]
                bridge.set_roadmap(selected_roadmap['id'])
                print(f"Using roadmap: {selected_roadmap['name']}")
    elif bridge.roadmap:
        print(f"Using roadmap: {bridge.roadmap.name}")
    else:
        print("Roadmap not found or not specified")
    
    # Show some example completions
    if bridge.roadmap:
        print("\nRoadmap-based completions:")
        sample_code = "class MyClass:\n    def __init__(self):\n        "
        completions = bridge.get_roadmap_completions("python", sample_code, len(sample_code))
        
        for completion in completions[:5]:
            print(f"- {completion['display_text']} ({completion['type']}) - {completion['description']}")
        
        # Test component generation
        if bridge.component_hierarchy:
            component_name = next(iter(bridge.component_hierarchy.keys()))
            print(f"\nGenerating component code for: {component_name}")
            component_code = bridge.generate_component_from_roadmap(component_name)
            
            if component_code:
                print("\nGenerated component code:")
                print("--------------------------")
                print(component_code[:500] + "..." if len(component_code) > 500 else component_code)
                print("--------------------------")
        
        # Get framework suggestions
        print("\nSuggested frameworks/libraries for this project:")
        frameworks = bridge.get_framework_suggestions()
        
        for framework in frameworks:
            print(f"- {framework.get('name')}: {framework.get('purpose')}")
    
    print("\nBridge initialized and ready to use.")