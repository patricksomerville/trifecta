#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyWrite Autocomplete Engine

This module provides intelligent code autocomplete features:
- Context-aware code suggestions
- Pattern-based completion
- Database-backed memory of coding patterns
- Integration with AI models for advanced completion

Author: PyWrite
Date: 2025-03-28
"""

import re
import os
import json
import ast
import time
from typing import Dict, List, Tuple, Any, Optional, Union
from database_helper import get_db_instance


class AutocompleteEngine:
    """Provides intelligent code completion functionalities."""
    
    def __init__(self):
        """Initialize the autocomplete engine."""
        self.db = get_db_instance()
        self.language_patterns = {
            'python': {
                'function': r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\((.*?)\)',
                'class': r'class\s+([a-zA-Z_][a-zA-Z0-9_]*)',
                'import': r'(from|import)\s+([a-zA-Z_][a-zA-Z0-9_.]*)$',
                'variable': r'([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*',
                'method_call': r'([a-zA-Z_][a-zA-Z0-9_]*)\.',
                'decorator': r'@([a-zA-Z_][a-zA-Z0-9_]*)'
            },
            'javascript': {
                'function': r'function\s+([a-zA-Z_][a-zA-Z0-9_]*)',
                'arrow_function': r'(const|let|var)?\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*\(.*?\)\s*=>\s*',
                'class': r'class\s+([a-zA-Z_][a-zA-Z0-9_]*)',
                'import': r'import\s+{?\s*([a-zA-Z_][a-zA-Z0-9_]*)?',
                'variable': r'(const|let|var)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*',
                'method_call': r'([a-zA-Z_][a-zA-Z0-9_]*)\.',
                'jsx_component': r'<([A-Z][a-zA-Z0-9_]*)$'
            }
        }
        self.language_keywords = {
            'python': [
                'and', 'as', 'assert', 'async', 'await', 'break', 'class', 'continue', 
                'def', 'del', 'elif', 'else', 'except', 'False', 'finally', 'for', 
                'from', 'global', 'if', 'import', 'in', 'is', 'lambda', 'None', 
                'nonlocal', 'not', 'or', 'pass', 'raise', 'return', 'True', 'try', 
                'while', 'with', 'yield'
            ],
            'javascript': [
                'break', 'case', 'catch', 'class', 'const', 'continue', 'debugger', 
                'default', 'delete', 'do', 'else', 'export', 'extends', 'false', 
                'finally', 'for', 'function', 'if', 'import', 'in', 'instanceof', 
                'new', 'null', 'return', 'super', 'switch', 'this', 'throw', 'true', 
                'try', 'typeof', 'var', 'void', 'while', 'with', 'yield', 'let', 'static',
                'async', 'await', 'of'
            ]
        }
        
        # Common code constructs for different languages
        self.code_constructs = {
            'python': {
                'if': 'if condition:\n    ',
                'for': 'for item in iterable:\n    ',
                'while': 'while condition:\n    ',
                'function': 'def function_name(parameters):\n    """Docstring"""\n    ',
                'class': 'class ClassName:\n    """Docstring"""\n    \n    def __init__(self):\n        ',
                'try': 'try:\n    \nexcept Exception as e:\n    ',
                'with': 'with open("filename", "r") as file:\n    ',
                'lambda': 'lambda x: x',
                'list_comp': '[x for x in iterable]',
                'dict_comp': '{key: value for item in iterable}'
            },
            'javascript': {
                'if': 'if (condition) {\n    \n}',
                'for': 'for (let i = 0; i < array.length; i++) {\n    \n}',
                'forin': 'for (const key in object) {\n    \n}',
                'forof': 'for (const item of array) {\n    \n}',
                'while': 'while (condition) {\n    \n}',
                'function': 'function functionName(parameters) {\n    \n}',
                'arrow': 'const functionName = (parameters) => {\n    \n}',
                'class': 'class ClassName {\n    constructor() {\n        \n    }\n}',
                'try': 'try {\n    \n} catch (error) {\n    \n}',
                'promise': 'new Promise((resolve, reject) => {\n    \n})',
                'import': 'import { module } from "package";',
                'export': 'export default className;'
            }
        }
        
        # Map snippets as ready-to-insert code blocks
        self.snippets = {}
        self._load_snippets()
    
    def _load_snippets(self):
        """Load snippets from the database."""
        try:
            python_snippets = self.db.search_snippets(language="python", limit=100)
            javascript_snippets = self.db.search_snippets(language="javascript", limit=100)
            
            for snippet in python_snippets:
                self.snippets[f"py_{snippet['name']}"] = snippet['code']
            
            for snippet in javascript_snippets:
                self.snippets[f"js_{snippet['name']}"] = snippet['code']
        except Exception as e:
            print(f"Warning: Failed to load snippets: {str(e)}")
    
    def get_completions(self, 
                       language: str, 
                       current_code: str, 
                       cursor_position: int,
                       file_content: str = "",
                       filename: str = None) -> List[Dict]:
        """
        Get autocomplete suggestions based on current code.
        
        Args:
            language: Programming language
            current_code: Current code being written
            cursor_position: Current cursor position in the code
            file_content: Full content of the file (for context)
            filename: Name of the file being edited
            
        Returns:
            List of completion suggestions
        """
        # Extract the context before the cursor
        code_before_cursor = current_code[:cursor_position]
        
        # Get language-specific completions
        completions = []
        
        # Only process if we have a valid language and code
        if not language or not code_before_cursor:
            return completions
        
        # 1. Get database-learned completions
        db_completions = self._get_db_completions(language, code_before_cursor)
        completions.extend(db_completions)
        
        # 2. Get keyword completions
        keyword_completions = self._get_keyword_completions(language, code_before_cursor)
        completions.extend(keyword_completions)
        
        # 3. Get snippet completions
        snippet_completions = self._get_snippet_completions(language, code_before_cursor)
        completions.extend(snippet_completions)
        
        # 4. Get context-aware completions
        context_completions = self._get_context_completions(
            language, code_before_cursor, file_content
        )
        completions.extend(context_completions)
        
        # 5. Get code construct completions
        construct_completions = self._get_construct_completions(
            language, code_before_cursor
        )
        completions.extend(construct_completions)
        
        # Sort by score and remove duplicates
        return self._deduplicate_and_rank_completions(completions)
    
    def _get_db_completions(self, language: str, code_before_cursor: str) -> List[Dict]:
        """Get completions from the database."""
        try:
            db_results = self.db.get_completions(language, code_before_cursor)
            return [
                {
                    'text': result['completion'],
                    'display_text': result['completion'],
                    'type': 'database',
                    'description': f"Used {result['frequency']} times",
                    'score': min(result['frequency'] * 10, 100),
                    'prefix_match': self._get_prefix_match(code_before_cursor, result['completion'])
                }
                for result in db_results
            ]
        except Exception as e:
            print(f"Warning: Failed to get database completions: {str(e)}")
            return []
    
    def _get_keyword_completions(self, language: str, code_before_cursor: str) -> List[Dict]:
        """Get language keyword completions."""
        completions = []
        
        # Extract the last word being typed
        match = re.search(r'[a-zA-Z0-9_]*$', code_before_cursor)
        if not match:
            return completions
            
        current_word = match.group(0)
        if not current_word:
            return completions
        
        # Add matching keywords
        if language in self.language_keywords:
            for keyword in self.language_keywords[language]:
                if keyword.startswith(current_word):
                    completions.append({
                        'text': keyword,
                        'display_text': keyword,
                        'type': 'keyword',
                        'description': f"{language} keyword",
                        'score': 80,  # Keywords are highly relevant
                        'prefix_match': len(current_word)
                    })
        
        return completions
    
    def _get_snippet_completions(self, language: str, code_before_cursor: str) -> List[Dict]:
        """Get snippet-based completions."""
        completions = []
        
        # Extract the last word being typed
        match = re.search(r'[a-zA-Z0-9_]*$', code_before_cursor)
        if not match:
            return completions
            
        current_word = match.group(0)
        if not current_word or len(current_word) < 2:
            return completions
        
        # Get language prefix for snippets
        lang_prefix = ''
        if language == 'python':
            lang_prefix = 'py_'
        elif language == 'javascript':
            lang_prefix = 'js_'
        
        # Check for matching snippets
        for name, code in self.snippets.items():
            if name.startswith(lang_prefix) and name[3:].startswith(current_word):
                display_name = name[3:]  # Remove language prefix for display
                completions.append({
                    'text': code,
                    'display_text': display_name,
                    'type': 'snippet',
                    'description': f"{display_name} snippet",
                    'score': 85,  # Snippets are very relevant
                    'prefix_match': len(current_word)
                })
        
        return completions
    
    def _get_context_completions(self, 
                                language: str, 
                                code_before_cursor: str,
                                file_content: str) -> List[Dict]:
        """Get completions based on current context."""
        completions = []
        
        # Parse the file to extract identifiers for intelligent completion
        # If we have Python and can parse the file
        if language == 'python' and file_content:
            try:
                imports, functions, classes, variables = self._parse_python_file(file_content)
                
                # Check for import completions
                import_match = re.search(r'(from|import)\s+([a-zA-Z_][a-zA-Z0-9_.]*)$', code_before_cursor)
                if import_match:
                    # Add matching imports
                    imported_module = import_match.group(2)
                    for module in imports:
                        if module.startswith(imported_module):
                            completions.append({
                                'text': module,
                                'display_text': module,
                                'type': 'import',
                                'description': "Import statement",
                                'score': 90,
                                'prefix_match': len(imported_module)
                            })
                
                # Check for function/method completions
                func_match = re.search(r'([a-zA-Z_][a-zA-Z0-9_]*)\.$', code_before_cursor)
                if func_match:
                    # Object method completion
                    obj_name = func_match.group(1)
                    # Find if obj_name is an instance of a class
                    obj_class = None
                    for var_name, var_info in variables.items():
                        if var_name == obj_name and 'class' in var_info:
                            obj_class = var_info['class']
                            break
                    
                    if obj_class and obj_class in classes:
                        # Add class methods
                        for method_name in classes[obj_class]['methods']:
                            completions.append({
                                'text': f"{method_name}()",
                                'display_text': method_name,
                                'type': 'method',
                                'description': f"Method of {obj_class}",
                                'score': 95,
                                'prefix_match': 0  # Full match with the dot
                            })
                
                # Variable name completions
                var_match = re.search(r'([a-zA-Z_][a-zA-Z0-9_]*)$', code_before_cursor)
                if var_match:
                    current_var = var_match.group(1)
                    # Add matching variables
                    for var_name in variables:
                        if var_name.startswith(current_var):
                            completions.append({
                                'text': var_name,
                                'display_text': var_name,
                                'type': 'variable',
                                'description': "Variable",
                                'score': 85,
                                'prefix_match': len(current_var)
                            })
                    
                    # Add matching functions
                    for func_name in functions:
                        if func_name.startswith(current_var):
                            completions.append({
                                'text': f"{func_name}()",
                                'display_text': func_name,
                                'type': 'function',
                                'description': "Function",
                                'score': 85,
                                'prefix_match': len(current_var)
                            })
                    
                    # Add matching classes
                    for class_name in classes:
                        if class_name.startswith(current_var):
                            completions.append({
                                'text': class_name,
                                'display_text': class_name,
                                'type': 'class',
                                'description': "Class",
                                'score': 85,
                                'prefix_match': len(current_var)
                            })
            
            except Exception as e:
                print(f"Warning: Failed to parse Python file for context: {str(e)}")
        
        # Add JavaScript context parsing here if needed
        
        return completions
    
    def _get_construct_completions(self, language: str, code_before_cursor: str) -> List[Dict]:
        """Get code construct completions."""
        completions = []
        
        # Match partial constructs
        if language in self.code_constructs:
            # Extract the last word or partial command
            match = re.search(r'[a-zA-Z0-9_]*$', code_before_cursor)
            if not match:
                return completions
                
            current_word = match.group(0)
            if not current_word or len(current_word) < 2:
                return completions
            
            # Check for matching constructs
            for name, template in self.code_constructs[language].items():
                if name.startswith(current_word):
                    completions.append({
                        'text': template,
                        'display_text': name,
                        'type': 'construct',
                        'description': f"{name} template",
                        'score': 80,
                        'prefix_match': len(current_word)
                    })
        
        return completions
    
    def _parse_python_file(self, file_content: str) -> Tuple[List[str], Dict, Dict, Dict]:
        """
        Parse a Python file to extract imports, functions, classes, and variables.
        
        Returns:
            Tuple containing:
            - List of imported modules
            - Dict of functions with details
            - Dict of classes with methods and details
            - Dict of variables with types
        """
        imports = []
        functions = {}
        classes = {}
        variables = {}
        
        try:
            tree = ast.parse(file_content)
            
            for node in ast.walk(tree):
                # Extract imports
                if isinstance(node, ast.Import):
                    for name in node.names:
                        imports.append(name.name)
                elif isinstance(node, ast.ImportFrom):
                    imports.append(node.module)
                
                # Extract function definitions
                elif isinstance(node, ast.FunctionDef):
                    functions[node.name] = {
                        'args': [arg.arg for arg in node.args.args],
                        'line': node.lineno
                    }
                
                # Extract class definitions
                elif isinstance(node, ast.ClassDef):
                    methods = []
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            methods.append(item.name)
                    
                    classes[node.name] = {
                        'methods': methods,
                        'bases': [base.id for base in node.bases if isinstance(base, ast.Name)],
                        'line': node.lineno
                    }
                
                # Extract variable assignments
                elif isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            # Try to determine variable type from the value
                            var_type = 'unknown'
                            if isinstance(node.value, ast.Num):
                                var_type = 'number'
                            elif isinstance(node.value, ast.Str):
                                var_type = 'string'
                            elif isinstance(node.value, ast.List):
                                var_type = 'list'
                            elif isinstance(node.value, ast.Dict):
                                var_type = 'dict'
                            elif isinstance(node.value, ast.Call):
                                if isinstance(node.value.func, ast.Name):
                                    var_type = node.value.func.id
                                    # This might be a class instantiation
                                    if var_type in classes:
                                        variables[target.id] = {
                                            'type': var_type,
                                            'class': var_type
                                        }
                                        continue
                            
                            variables[target.id] = {'type': var_type}
        
        except Exception as e:
            print(f"Warning: AST parsing error: {str(e)}")
        
        return imports, functions, classes, variables
    
    def _get_prefix_match(self, prefix: str, completion: str) -> int:
        """
        Calculate the length of matching prefix between input and completion.
        
        Args:
            prefix: The input prefix text
            completion: The suggested completion text
            
        Returns:
            Length of matching characters
        """
        match = re.search(r'[a-zA-Z0-9_]*$', prefix)
        if not match:
            return 0
            
        current_word = match.group(0)
        if not current_word:
            return 0
        
        # Calculate matching prefix
        match_len = 0
        for i, char in enumerate(current_word):
            if i < len(completion) and char == completion[i]:
                match_len += 1
            else:
                break
        
        return match_len
    
    def _deduplicate_and_rank_completions(self, completions: List[Dict]) -> List[Dict]:
        """
        Remove duplicates and rank completions by score.
        
        Args:
            completions: List of completion dictionaries
            
        Returns:
            Deduplicated and ranked completions
        """
        seen = set()
        unique_completions = []
        
        for completion in completions:
            text = completion['text']
            display = completion['display_text']
            
            # Use text + display_text as a unique key
            key = f"{text}|{display}"
            if key not in seen:
                seen.add(key)
                unique_completions.append(completion)
        
        # Sort by score (descending) and prefix match length (descending)
        return sorted(
            unique_completions, 
            key=lambda x: (x['score'], x['prefix_match']), 
            reverse=True
        )
    
    def learn_from_file(self, file_path: str, language: str = None) -> int:
        """
        Learn patterns from an existing file to improve autocomplete.
        
        Args:
            file_path: Path to the file
            language: Optional language override
            
        Returns:
            Number of patterns learned
        """
        if not os.path.exists(file_path):
            return 0
        
        # Determine language from file extension if not provided
        if not language:
            _, ext = os.path.splitext(file_path)
            if ext == '.py':
                language = 'python'
            elif ext in ['.js', '.jsx']:
                language = 'javascript'
            else:
                return 0  # Unsupported language
        
        # Read file content
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Learn patterns from the content
            return self.db.learn_from_code(language, content)
        except Exception as e:
            print(f"Warning: Failed to learn from file {file_path}: {str(e)}")
            return 0
    
    def add_snippet(self, name: str, language: str, code: str, description: str = "") -> int:
        """
        Add a code snippet for autocomplete suggestions.
        
        Args:
            name: Name of the snippet
            language: Programming language
            code: The actual code
            description: Optional description
            
        Returns:
            Snippet ID
        """
        try:
            snippet_id = self.db.add_snippet(
                name=name,
                language=language,
                code=code,
                description=description
            )
            
            # Update in-memory snippets
            lang_prefix = 'py_' if language == 'python' else 'js_' if language == 'javascript' else ''
            if lang_prefix:
                self.snippets[f"{lang_prefix}{name}"] = code
            
            return snippet_id
        except Exception as e:
            print(f"Warning: Failed to add snippet: {str(e)}")
            return 0


# Demo code if run directly
if __name__ == "__main__":
    print("Initializing PyWrite Autocomplete Engine...")
    engine = AutocompleteEngine()
    
    # Test Python completions
    python_code = """import os
import sys

def calculate_sum(a, b):
    return a + b

class Calculator:
    def __init__(self):
        self.history = []
    
    def add(self, a, b):
        result = a + b
        self.history.append(f"Added {a} + {b} = {result}")
        return result

# Test cursor position here
calc = Calculator()
calc."""

    cursor_pos = len(python_code)
    completions = engine.get_completions(
        language='python',
        current_code=python_code,
        cursor_position=cursor_pos,
        file_content=python_code
    )
    
    print("Python completions:")
    for i, completion in enumerate(completions[:5]):
        print(f"{i+1}. {completion['display_text']} ({completion['type']}) - {completion['description']}")
    
    # Learn from file
    engine.learn_from_file('database_helper.py')
    
    # Test completions after learning
    test_code = "def get_"
    completions = engine.get_completions(
        language='python',
        current_code=test_code,
        cursor_position=len(test_code)
    )
    
    print("\nAfter learning:")
    for i, completion in enumerate(completions[:5]):
        print(f"{i+1}. {completion['display_text']} ({completion['type']}) - {completion['description']}")
    
    print("\nAutocomplete engine initialized and tested.")