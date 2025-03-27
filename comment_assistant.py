#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI-powered Comment Assistant for PyWrite
This module provides functionality to analyze code and generate appropriate comments.
"""

import re
import ast
import os
from typing import Dict, List, Tuple, Optional


class CommentAssistant:
    """AI-powered assistant for generating code comments."""
    
    def __init__(self):
        """Initialize the comment assistant."""
        self.language_handlers = {
            'python': self.analyze_python,
            'javascript': self.analyze_javascript,
            'html': self.analyze_html,
            'css': self.analyze_css,
        }
        
    def analyze_file(self, file_path: str) -> Dict:
        """
        Analyze a file and generate comments.
        
        Args:
            file_path: Path to the file to analyze
            
        Returns:
            Dictionary with analysis results
        """
        if not os.path.exists(file_path):
            return {"error": f"File not found: {file_path}"}
            
        # Determine file type
        extension = file_path.split('.')[-1].lower()
        language_map = {
            'py': 'python',
            'js': 'javascript',
            'html': 'html',
            'css': 'css'
        }
        
        language = language_map.get(extension)
        if not language:
            return {"error": f"Unsupported file type: .{extension}"}
            
        # Read file content
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return {"error": f"Error reading file: {str(e)}"}
            
        # Analyze content
        handler = self.language_handlers.get(language)
        if handler:
            return handler(content, file_path)
        else:
            return {"error": f"No handler for language: {language}"}
    
    def analyze_python(self, content: str, file_path: str) -> Dict:
        """
        Analyze Python code and generate comments.
        
        Args:
            content: Python code content
            file_path: Path to the Python file
            
        Returns:
            Dictionary with analysis results
        """
        result = {
            "type": "python",
            "file_path": file_path,
            "missing_docstrings": [],
            "complex_functions": [],
            "suggested_comments": {},
            "file_summary": self._generate_file_summary(content, "python")
        }
        
        try:
            # Parse the AST
            tree = ast.parse(content)
            
            # Analyze classes and functions
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    # Check for missing docstrings
                    if not ast.get_docstring(node):
                        line_num = node.lineno
                        result["missing_docstrings"].append({
                            "name": node.name,
                            "line": line_num,
                            "type": "class" if isinstance(node, ast.ClassDef) else "function",
                            "suggested_docstring": self._generate_docstring(node, content)
                        })
                    
                    # Check for complex functions (those with many lines or conditions)
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        complexity = self._calculate_complexity(node)
                        if complexity > 5:  # Arbitrary threshold
                            result["complex_functions"].append({
                                "name": node.name,
                                "line": node.lineno,
                                "complexity": complexity
                            })
            
            # Find code blocks without inline comments
            result["suggested_comments"] = self._find_missing_comments(content)
            
        except SyntaxError as e:
            result["error"] = f"Syntax error in Python file: {str(e)}"
            
        return result
    
    def analyze_javascript(self, content: str, file_path: str) -> Dict:
        """
        Analyze JavaScript code and generate comments.
        
        Args:
            content: JavaScript code content
            file_path: Path to the JavaScript file
            
        Returns:
            Dictionary with analysis results
        """
        result = {
            "type": "javascript",
            "file_path": file_path,
            "functions": [],
            "classes": [],
            "suggested_comments": {},
            "file_summary": self._generate_file_summary(content, "javascript")
        }
        
        # Find functions
        function_pattern = r'(function\s+(\w+)\s*\([^)]*\)|const\s+(\w+)\s*=\s*function\s*\([^)]*\)|const\s+(\w+)\s*=\s*\([^)]*\)\s*=>)'
        for match in re.finditer(function_pattern, content):
            line_num = content[:match.start()].count('\n') + 1
            func_name = match.group(2) or match.group(3) or match.group(4)
            if func_name:
                # Check if function has JSDoc comment
                prev_lines = content[:match.start()].split('\n')
                has_comment = False
                if prev_lines and '/**' in prev_lines[-1]:
                    has_comment = True
                
                result["functions"].append({
                    "name": func_name,
                    "line": line_num,
                    "has_comment": has_comment,
                    "suggested_comment": "" if has_comment else self._generate_js_comment(match.group(0), content)
                })
        
        # Find classes
        class_pattern = r'class\s+(\w+)'
        for match in re.finditer(class_pattern, content):
            line_num = content[:match.start()].count('\n') + 1
            class_name = match.group(1)
            
            # Check if class has JSDoc comment
            prev_lines = content[:match.start()].split('\n')
            has_comment = False
            if prev_lines and '/**' in prev_lines[-1]:
                has_comment = True
            
            result["classes"].append({
                "name": class_name,
                "line": line_num,
                "has_comment": has_comment,
                "suggested_comment": "" if has_comment else self._generate_js_class_comment(class_name, content)
            })
            
        # Find missing inline comments
        result["suggested_comments"] = self._find_missing_comments(content, language="javascript")
        
        return result
    
    def analyze_html(self, content: str, file_path: str) -> Dict:
        """
        Analyze HTML code and suggest comments.
        
        Args:
            content: HTML content
            file_path: Path to the HTML file
            
        Returns:
            Dictionary with analysis results
        """
        result = {
            "type": "html",
            "file_path": file_path,
            "sections": [],
            "suggested_comments": {},
            "file_summary": self._generate_file_summary(content, "html")
        }
        
        # Find major sections (divs with ids or sections)
        section_pattern = r'<(div|section|header|footer|nav|main|article|aside)([^>]*id=["\']([^"\']+)["\']|[^>]*class=["\']([^"\']+)["\'])'
        for match in re.finditer(section_pattern, content):
            line_num = content[:match.start()].count('\n') + 1
            tag = match.group(1)
            section_id = match.group(3) or match.group(4) or "unnamed"
            
            # Check if section has a comment
            prev_content = content[:match.start()]
            prev_lines = prev_content.split('\n')
            has_comment = False
            for i in range(len(prev_lines) - 1, max(0, len(prev_lines) - 3), -1):
                if '<!--' in prev_lines[i]:
                    has_comment = True
                    break
            
            result["sections"].append({
                "tag": tag,
                "id": section_id,
                "line": line_num,
                "has_comment": has_comment,
                "suggested_comment": "" if has_comment else f"<!-- {tag.upper()} section: {section_id} -->"
            })
        
        return result
    
    def analyze_css(self, content: str, file_path: str) -> Dict:
        """
        Analyze CSS code and suggest comments.
        
        Args:
            content: CSS content
            file_path: Path to the CSS file
            
        Returns:
            Dictionary with analysis results
        """
        result = {
            "type": "css",
            "file_path": file_path,
            "selectors": [],
            "suggested_comments": {},
            "file_summary": self._generate_file_summary(content, "css")
        }
        
        # Find CSS selectors
        selector_pattern = r'([.#]?\w+(?:[.#]\w+)*)\s*\{'
        current_section = ""
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            # Check for section comments
            if '/*' in line and '*/' in line and line.strip().startswith('/*'):
                current_section = line.strip()[2:-2].strip()
            
            # Find selectors
            for match in re.finditer(selector_pattern, line):
                selector = match.group(1)
                
                # Check if selector has a comment
                has_comment = False
                if i > 0 and '/*' in lines[i-1]:
                    has_comment = True
                
                result["selectors"].append({
                    "selector": selector,
                    "line": i + 1,
                    "section": current_section,
                    "has_comment": has_comment,
                    "suggested_comment": "" if has_comment else f"/* Styles for {selector} */"
                })
        
        return result
    
    def generate_improved_file(self, analysis_result: Dict) -> str:
        """
        Generate an improved version of the file with added comments.
        
        Args:
            analysis_result: Result from analyze_file
            
        Returns:
            String with the improved file content
        """
        if "error" in analysis_result:
            return f"# Error: {analysis_result['error']}"
            
        file_path = analysis_result["file_path"]
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return f"# Error reading file: {str(e)}"
            
        # Create a new version with improved comments
        file_type = analysis_result["type"]
        
        if file_type == "python":
            return self._improve_python_file(content, analysis_result)
        elif file_type == "javascript":
            return self._improve_javascript_file(content, analysis_result)
        elif file_type == "html":
            return self._improve_html_file(content, analysis_result)
        elif file_type == "css":
            return self._improve_css_file(content, analysis_result)
        else:
            return f"# Unsupported file type: {file_type}"
    
    def _improve_python_file(self, content: str, analysis: Dict) -> str:
        """Improve a Python file by adding missing docstrings and comments."""
        lines = content.split('\n')
        new_lines = lines.copy()
        offset = 0  # Offset due to added lines
        
        # Add file header if missing
        if not content.startswith('"""') and not content.startswith('#'):
            header = f'"""\n{analysis["file_summary"]}\n"""\n\n'
            new_lines.insert(0, header)
            offset += 4
        
        # Add missing docstrings
        for item in sorted(analysis["missing_docstrings"], key=lambda x: x["line"], reverse=True):
            line_idx = item["line"] + offset - 1
            indent = len(lines[item["line"] - 1]) - len(lines[item["line"] - 1].lstrip())
            spaces = ' ' * indent
            docstring_lines = item["suggested_docstring"].split('\n')
            formatted_docstring = f'{spaces}"""\n'
            for ds_line in docstring_lines:
                formatted_docstring += f'{spaces}{ds_line}\n'
            formatted_docstring += f'{spaces}"""\n'
            
            # Find the position right after the function/class declaration
            insert_idx = line_idx + 1
            next_line_indent = 999  # Default to a large number
            
            # Check if there's a body to the function/class
            if insert_idx < len(new_lines):
                next_line = new_lines[insert_idx].rstrip()
                if next_line:  # If the next line is not empty
                    next_line_indent = len(next_line) - len(next_line.lstrip())
                    
                    # If the next line is less indented, this is an empty function/class
                    if next_line_indent <= indent:
                        # This is an empty function/class
                        formatted_docstring = f'{spaces}"""{item["suggested_docstring"]}"""\n'
                        
            # Insert the docstring
            new_lines.insert(insert_idx, formatted_docstring)
            offset += len(formatted_docstring.split('\n'))
        
        # Add inline comments
        for line_num, comment in sorted(analysis["suggested_comments"].items(), key=lambda x: int(x[0]), reverse=True):
            line_idx = int(line_num) + offset - 1
            if line_idx < len(new_lines):
                new_lines[line_idx] = f"{new_lines[line_idx]}  # {comment}"
        
        return '\n'.join(new_lines)
    
    def _improve_javascript_file(self, content: str, analysis: Dict) -> str:
        """Improve a JavaScript file by adding JSDoc comments."""
        lines = content.split('\n')
        new_lines = lines.copy()
        offset = 0  # Offset due to added lines
        
        # Add file header if missing
        if not content.startswith('/**') and not content.startswith('//'):
            header = f'/**\n * {analysis["file_summary"]}\n */\n\n'
            new_lines.insert(0, header)
            offset += 4
        
        # Add missing function comments
        for func in analysis["functions"]:
            if not func["has_comment"] and func["suggested_comment"]:
                line_idx = func["line"] + offset - 1
                new_lines.insert(line_idx, func["suggested_comment"])
                offset += len(func["suggested_comment"].split('\n'))
        
        # Add missing class comments
        for cls in analysis["classes"]:
            if not cls["has_comment"] and cls["suggested_comment"]:
                line_idx = cls["line"] + offset - 1
                new_lines.insert(line_idx, cls["suggested_comment"])
                offset += len(cls["suggested_comment"].split('\n'))
        
        # Add inline comments
        for line_num, comment in analysis["suggested_comments"].items():
            line_idx = int(line_num) + offset - 1
            if line_idx < len(new_lines):
                new_lines[line_idx] = f"{new_lines[line_idx]} // {comment}"
        
        return '\n'.join(new_lines)
    
    def _improve_html_file(self, content: str, analysis: Dict) -> str:
        """Improve an HTML file by adding section comments."""
        lines = content.split('\n')
        new_lines = lines.copy()
        offset = 0  # Offset due to added lines
        
        # Add file header if missing
        if not content.startswith('<!--') and not '<!DOCTYPE' in content[:100]:
            header = f'<!--\n  {analysis["file_summary"]}\n-->\n\n'
            new_lines.insert(0, header)
            offset += 4
        
        # Add missing section comments
        for section in analysis["sections"]:
            if not section["has_comment"] and section["suggested_comment"]:
                line_idx = section["line"] + offset - 1
                new_lines.insert(line_idx, section["suggested_comment"])
                offset += 1
        
        return '\n'.join(new_lines)
    
    def _improve_css_file(self, content: str, analysis: Dict) -> str:
        """Improve a CSS file by adding selector comments."""
        lines = content.split('\n')
        new_lines = lines.copy()
        offset = 0  # Offset due to added lines
        
        # Add file header if missing
        if not content.startswith('/*'):
            header = f'/*\n * {analysis["file_summary"]}\n */\n\n'
            new_lines.insert(0, header)
            offset += 4
        
        # Add missing selector comments
        current_section = ""
        for selector in analysis["selectors"]:
            if not selector["has_comment"]:
                line_idx = selector["line"] + offset - 1
                
                # Add section comment if needed
                if selector["section"] != current_section and selector["section"]:
                    section_comment = f"\n/* {selector['section']} Section */\n"
                    new_lines.insert(line_idx, section_comment)
                    offset += 2
                    line_idx += 2
                    current_section = selector["section"]
                
                new_lines.insert(line_idx, selector["suggested_comment"])
                offset += 1
        
        return '\n'.join(new_lines)
    
    def _calculate_complexity(self, node: ast.AST) -> int:
        """Calculate the complexity of a function."""
        complexity = 1  # Base complexity
        
        # Count if statements, loops, and exception handlers
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.Try)):
                complexity += 1
        
        return complexity
    
    def _generate_docstring(self, node: ast.AST, content: str) -> str:
        """Generate a docstring for a Python function or class."""
        if isinstance(node, ast.ClassDef):
            # Analyze class to generate a better description
            class_desc = f"Class for {node.name.replace('_', ' ').lower()}."
            methods = []
            
            # Find methods in the class
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    methods.append(item.name)
            
            # Add methods information if available
            if methods:
                class_desc += f"\n\nThis class provides the following methods:\n"
                for method in methods:
                    class_desc += f"    - {method}\n"
                    
            return class_desc
            
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            # Get function signature
            args = []
            returns_value = False
            
            # Handle arguments
            for arg in node.args.args:
                if arg.arg != 'self' and arg.arg != 'cls':
                    args.append(arg.arg)
            
            # Check if function has a return statement
            for child in ast.walk(node):
                if isinstance(child, ast.Return) and child.value is not None:
                    returns_value = True
                    break
            
            # Generate a more descriptive summary based on function name
            func_name = node.name
            
            # Common function name patterns
            if func_name.startswith('get_'):
                summary = f"Get the {func_name[4:].replace('_', ' ')}."
            elif func_name.startswith('set_'):
                summary = f"Set the {func_name[4:].replace('_', ' ')}."
            elif func_name.startswith('is_'):
                summary = f"Check if {func_name[3:].replace('_', ' ')}."
            elif func_name.startswith('has_'):
                summary = f"Check if has {func_name[4:].replace('_', ' ')}."
            elif func_name.startswith('calculate_') or func_name.startswith('calc_'):
                summary = f"Calculate the {func_name.split('_', 1)[1].replace('_', ' ')}."
            elif func_name.startswith('validate_'):
                summary = f"Validate the {func_name[9:].replace('_', ' ')}."
            elif func_name.startswith('create_'):
                summary = f"Create a new {func_name[7:].replace('_', ' ')}."
            elif func_name.startswith('update_'):
                summary = f"Update the {func_name[7:].replace('_', ' ')}."
            elif func_name.startswith('delete_') or func_name.startswith('remove_'):
                summary = f"Delete the {func_name.split('_', 1)[1].replace('_', ' ')}."
            elif func_name == 'main':
                summary = "Entry point of the program."
            elif func_name == '__init__':
                summary = "Initialize the object."
            else:
                summary = f"{func_name.replace('_', ' ').capitalize()}."
            
            # Build complete docstring
            docstring = summary
            
            if args:
                docstring += "\n\nArgs:\n"
                for arg in args:
                    docstring += f"    {arg}: Description of {arg}\n"
            
            if returns_value:
                docstring += "\nReturns:\n    Description of return value"
                
            return docstring
        return ""
    
    def _generate_js_comment(self, function_code: str, content: str) -> str:
        """Generate a JSDoc comment for a JavaScript function."""
        # Extract function name and parameters
        params = []
        if '(' in function_code and ')' in function_code:
            param_str = function_code.split('(')[1].split(')')[0]
            params = [p.strip() for p in param_str.split(',') if p.strip()]
        
        # Build JSDoc comment
        comment = "/**\n"
        comment += f" * Function description\n"
        
        for param in params:
            param = param.replace('{', '').replace('}', '').strip()
            if '=' in param:
                param = param.split('=')[0].strip()
            comment += f" * @param {{{param.split(':')[0] if ':' in param else 'any'}}} {param.split(':')[0] if ':' in param else param} - Parameter description\n"
        
        comment += " * @returns {void} Return description\n"
        comment += " */\n"
        
        return comment
    
    def _generate_js_class_comment(self, class_name: str, content: str) -> str:
        """Generate a JSDoc comment for a JavaScript class."""
        # Build JSDoc comment
        comment = "/**\n"
        comment += f" * Class representing a {class_name}\n"
        comment += " */\n"
        
        return comment
    
    def _find_missing_comments(self, content: str, language: str = "python") -> Dict:
        """Find code blocks that could benefit from comments."""
        suggested_comments = {}
        lines = content.split('\n')
        
        # Different patterns based on language
        complex_patterns = {}
        if language == "python":
            complex_patterns = {
                r'for\s+\w+\s+in': "Loop through items",
                r'if\s+.+\s+and\s+.+:': "Check multiple conditions",
                r'try\s*:': "Handle potential errors",
                r'except\s+(\w+)?(\s+as\s+\w+)?:': "Catch specific exception",
                r'with\s+.+\s+as\s+\w+:': "Manage context",
                r'while\s+.+:': "Continue until condition is met"
            }
        elif language == "javascript":
            complex_patterns = {
                r'for\s*\(.+;.+;.+\)': "Loop with counter",
                r'for\s*\(.+\s+of\s+.+\)': "Loop through items",
                r'if\s*\(.+&&.+\)': "Check multiple conditions",
                r'try\s*\{': "Handle potential errors",
                r'catch\s*\(.+\)': "Catch exceptions",
                r'while\s*\(.+\)': "Continue until condition is met"
            }
        
        # Check each line for complex patterns
        for i, line in enumerate(lines):
            line_num = i + 1
            
            # Skip lines that already have comments
            if (language == "python" and '#' in line) or \
               (language == "javascript" and ('//' in line or '/*' in line)):
                continue
            
            # Check for complex patterns
            for pattern, comment in complex_patterns.items():
                if re.search(pattern, line):
                    suggested_comments[line_num] = comment
                    break
        
        return suggested_comments
    
    def _generate_file_summary(self, content: str, language: str) -> str:
        """Generate a summary for the file based on its content."""
        if language == "python":
            return "Python module for handling code functionality."
        elif language == "javascript":
            return "JavaScript module providing client-side functionality."
        elif language == "html":
            return "HTML template for webpage structure."
        elif language == "css":
            return "CSS stylesheet for styling the application."
        else:
            return f"File containing {language} code."


def analyze_code_file(file_path: str) -> Dict:
    """
    Analyze a code file and generate comment suggestions.
    
    Args:
        file_path: Path to the file to analyze
        
    Returns:
        Analysis results
    """
    assistant = CommentAssistant()
    return assistant.analyze_file(file_path)


def generate_improved_file(file_path: str) -> str:
    """
    Generate an improved version of a code file with comments.
    
    Args:
        file_path: Path to the file to improve
        
    Returns:
        Improved file content
    """
    assistant = CommentAssistant()
    analysis = assistant.analyze_file(file_path)
    return assistant.generate_improved_file(analysis)


def main():
    """Process command line arguments and run the comment assistant."""
    import argparse
    
    parser = argparse.ArgumentParser(description='AI-powered Comment Assistant')
    parser.add_argument('command', choices=['analyze', 'improve'],
                        help='Command: analyze or improve')
    parser.add_argument('file_path', help='Path to the file to process')
    parser.add_argument('--output', '-o', help='Output file path (for improve command)')
    
    args = parser.parse_args()
    
    if args.command == 'analyze':
        result = analyze_code_file(args.file_path)
        # Print analysis results
        print("\n====================================")
        print("  PyWrite Comment Assistant")
        print("====================================\n")
        
        if "error" in result:
            print(f"Error: {result['error']}")
            return
            
        print(f"Analysis for: {args.file_path}\n")
        print(f"File type: {result['type']}")
        print(f"Summary: {result['file_summary']}\n")
        
        if "missing_docstrings" in result:
            print(f"Missing docstrings: {len(result['missing_docstrings'])}")
            for item in result['missing_docstrings']:
                print(f"  - {item['type'].capitalize()} '{item['name']}' at line {item['line']}")
            print()
            
        if "complex_functions" in result:
            print(f"Complex functions: {len(result['complex_functions'])}")
            for func in result['complex_functions']:
                print(f"  - Function '{func['name']}' at line {func['line']} (complexity: {func['complexity']})")
            print()
            
        if "functions" in result:
            print(f"Functions: {len(result['functions'])}")
            for func in result['functions']:
                status = "missing comment" if not func['has_comment'] else "has comment"
                print(f"  - Function '{func['name']}' at line {func['line']} ({status})")
            print()
            
        if "classes" in result:
            print(f"Classes: {len(result['classes'])}")
            for cls in result['classes']:
                status = "missing comment" if not cls['has_comment'] else "has comment"
                print(f"  - Class '{cls['name']}' at line {cls['line']} ({status})")
            print()
            
        if "sections" in result:
            print(f"HTML sections: {len(result['sections'])}")
            for section in result['sections']:
                status = "missing comment" if not section['has_comment'] else "has comment"
                print(f"  - {section['tag']} '{section['id']}' at line {section['line']} ({status})")
            print()
            
        if "selectors" in result:
            print(f"CSS selectors: {len(result['selectors'])}")
            for selector in result['selectors']:
                status = "missing comment" if not selector['has_comment'] else "has comment"
                print(f"  - Selector '{selector['selector']}' at line {selector['line']} ({status})")
            print()
            
        suggested_comments = result.get("suggested_comments", {})
        if suggested_comments:
            print(f"Suggested inline comments: {len(suggested_comments)}")
            for line, comment in suggested_comments.items():
                print(f"  - Line {line}: {comment}")
            print()
            
        print("Analysis complete.")
            
    elif args.command == 'improve':
        improved_content = generate_improved_file(args.file_path)
        
        print("\n====================================")
        print("  PyWrite Comment Assistant")
        print("====================================\n")
        
        if improved_content.startswith('# Error'):
            print(improved_content)
            return
            
        output_path = args.output
        if output_path:
            try:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(improved_content)
                print(f"Improved file written to: {output_path}")
            except Exception as e:
                print(f"Error writing to output file: {str(e)}")
        else:
            print("Improved content:\n")
            print(improved_content)
            
        print("\nImprovement complete.")


if __name__ == "__main__":
    main()