#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyWrite Continuous Coding Module

This module provides AI-powered continuous coding capabilities:
- Automated code completion
- Smart refactoring suggestions
- Real-time error detection and fixing
- Context-aware code generation
- Continuous improvement features

Author: PyWrite
Date: 2025-03-28
"""

import os
import re
import ast
import time
import json
import logging
import threading
import traceback
import openai
from typing import Dict, List, Tuple, Any, Optional, Union, Callable
from database_helper import get_db_instance
from autocomplete_engine import AutocompleteEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('continuous_coding.log')
    ]
)

logger = logging.getLogger('PyWrite.ContinuousCoding')


class ContinuousCodingEngine:
    """Provides AI-powered continuous coding capabilities."""
    
    def __init__(self, api_key=None):
        """
        Initialize the continuous coding engine.
        
        Args:
            api_key: OpenAI API key (optional, can be loaded from environment)
        """
        self.db = get_db_instance()
        self.autocomplete = AutocompleteEngine()
        
        # Initialize OpenAI
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if self.api_key:
            openai.api_key = self.api_key
            self.openai_client = openai.OpenAI(api_key=self.api_key)
            self.has_openai = True
        else:
            logger.warning("OpenAI API key not provided. Advanced AI features will be disabled.")
            self.has_openai = False
        
        # Thread for background processing
        self.processing_thread = None
        self.should_stop = threading.Event()
        
        # Smart improvement history
        self.improvement_history = {}
        
        # Number of tokens consumed for tracking
        self.tokens_consumed = 0
    
    def start(self):
        """Start the continuous coding engine."""
        if self.processing_thread and self.processing_thread.is_alive():
            logger.warning("Continuous coding engine already running")
            return
        
        self.should_stop.clear()
        self.processing_thread = threading.Thread(target=self._background_processing, daemon=True)
        self.processing_thread.start()
        logger.info("Continuous coding engine started")
    
    def stop(self):
        """Stop the continuous coding engine."""
        if not self.processing_thread or not self.processing_thread.is_alive():
            logger.warning("Continuous coding engine not running")
            return
        
        self.should_stop.set()
        self.processing_thread.join(timeout=5.0)
        logger.info("Continuous coding engine stopped")
    
    def _background_processing(self):
        """Background thread for processing files."""
        while not self.should_stop.is_set():
            try:
                # Process recent files from database
                self._process_recent_files()
                
                # Sleep for a while before next check
                self.should_stop.wait(60.0)  # Check every minute
            except Exception as e:
                logger.error(f"Error in background processing: {str(e)}")
                self.should_stop.wait(10.0)  # Wait a bit on error
    
    def _process_recent_files(self):
        """Process recently accessed files for improvements."""
        try:
            # Get recent file activity from the database
            recent_activity = self.db.get_activity_history(
                action_type='file_saved',
                limit=10
            )
            
            for activity in recent_activity:
                if self.should_stop.is_set():
                    break
                
                data = activity.get('action_data', {})
                file_path = data.get('file_path', '')
                
                # Skip if file doesn't exist or we've already processed it recently
                if not file_path or not os.path.exists(file_path):
                    continue
                
                # Skip if we've processed this file in the last hour
                last_processed = self.improvement_history.get(file_path, 0)
                if time.time() - last_processed < 3600:  # 1 hour
                    continue
                
                # Process the file
                self._process_file(file_path)
                
                # Record processing time
                self.improvement_history[file_path] = time.time()
                
                # Small delay between files to avoid overwhelming system
                self.should_stop.wait(5.0)
        
        except Exception as e:
            logger.error(f"Error processing recent files: {str(e)}")
    
    def _process_file(self, file_path):
        """
        Process a file for improvements.
        
        Args:
            file_path: Path to the file to process
        """
        # Determine file type
        _, ext = os.path.splitext(file_path)
        
        if ext == '.py':
            self._process_python_file(file_path)
        elif ext in ['.js', '.jsx']:
            self._process_javascript_file(file_path)
        # Add other file types as needed
    
    def _process_python_file(self, file_path):
        """
        Process a Python file for improvements.
        
        Args:
            file_path: Path to the Python file
        """
        try:
            # Read the file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Basic improvements
            issues = self._check_python_issues(content, file_path)
            
            # Only proceed with AI improvements if we have OpenAI access
            if self.has_openai:
                # Get AI suggestions for the file
                suggestions = self._get_ai_code_suggestions(content, 'python', file_path)
                
                # Apply selected suggestions if they seem valuable
                if suggestions:
                    improved_content = self._apply_ai_suggestions(content, suggestions, file_path)
                    
                    # If we have substantial improvements, save them
                    if improved_content and improved_content != content:
                        # Create a backup
                        backup_path = f"{file_path}.bak"
                        with open(backup_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        
                        # Write the improved version
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(improved_content)
                        
                        logger.info(f"Applied AI improvements to {file_path}")
            
            # Learn patterns for autocomplete
            self.autocomplete.learn_from_file(file_path, 'python')
            
        except Exception as e:
            logger.error(f"Error processing Python file {file_path}: {str(e)}")
    
    def _process_javascript_file(self, file_path):
        """
        Process a JavaScript file for improvements.
        
        Args:
            file_path: Path to the JavaScript file
        """
        try:
            # Read the file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Only proceed with AI improvements if we have OpenAI access
            if self.has_openai:
                # Get AI suggestions for the file
                suggestions = self._get_ai_code_suggestions(content, 'javascript', file_path)
                
                # Apply selected suggestions if they seem valuable
                if suggestions:
                    improved_content = self._apply_ai_suggestions(content, suggestions, file_path)
                    
                    # If we have substantial improvements, save them
                    if improved_content and improved_content != content:
                        # Create a backup
                        backup_path = f"{file_path}.bak"
                        with open(backup_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        
                        # Write the improved version
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(improved_content)
                        
                        logger.info(f"Applied AI improvements to {file_path}")
            
            # Learn patterns for autocomplete
            self.autocomplete.learn_from_file(file_path, 'javascript')
            
        except Exception as e:
            logger.error(f"Error processing JavaScript file {file_path}: {str(e)}")
    
    def _check_python_issues(self, content, file_path):
        """
        Check for common issues in Python code.
        
        Args:
            content: Python code content
            file_path: Path to the file
            
        Returns:
            List of identified issues
        """
        issues = []
        
        try:
            # Parse the AST
            tree = ast.parse(content)
            
            # Check for unused imports
            imported_names = set()
            used_names = set()
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for name in node.names:
                        imported_names.add(name.name)
                elif isinstance(node, ast.ImportFrom):
                    for name in node.names:
                        imported_names.add(name.name)
                elif isinstance(node, ast.Name):
                    used_names.add(node.id)
            
            for name in imported_names:
                if name not in used_names:
                    issues.append({
                        'type': 'unused_import',
                        'message': f"Unused import: '{name}'",
                        'severity': 'warning'
                    })
            
            # Check for functions without docstrings
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    has_docstring = False
                    if (node.body and isinstance(node.body[0], ast.Expr) and 
                        isinstance(node.body[0].value, ast.Str)):
                        has_docstring = True
                    
                    if not has_docstring:
                        issues.append({
                            'type': 'missing_docstring',
                            'message': f"Function '{node.name}' is missing a docstring",
                            'line': node.lineno,
                            'severity': 'info'
                        })
            
        except SyntaxError as e:
            issues.append({
                'type': 'syntax_error',
                'message': f"Syntax error: {str(e)}",
                'line': e.lineno,
                'severity': 'error'
            })
        except Exception as e:
            issues.append({
                'type': 'analysis_error',
                'message': f"Error during analysis: {str(e)}",
                'severity': 'error'
            })
        
        return issues
    
    def _get_ai_code_suggestions(self, content, language, file_path):
        """
        Get AI-powered suggestions for the code.
        
        Args:
            content: Code content
            language: Programming language
            file_path: Path to the file
            
        Returns:
            List of improvement suggestions
        """
        if not self.has_openai:
            return []
        
        try:
            file_name = os.path.basename(file_path)
            
            # Construct prompt
            prompt = (
                f"You are a software engineer reviewing the following {language} code "
                f"from a file named {file_name}. Please analyze it carefully and suggest "
                "improvements that could make the code more efficient, readable, maintainable, "
                "or correct. Focus on important issues rather than style preferences. "
                "Identify logic issues, potential bugs, performance problems, and provide "
                "specific, actionable improvements. Respond in JSON format.\n\n"
                "Code to analyze:\n```\n" + content + "\n```\n\n"
                "Provide your response in this JSON format:\n"
                "{\n"
                "  \"suggestions\": [\n"
                "    {\n"
                "      \"type\": \"improvement_type\",\n"
                "      \"severity\": \"high|medium|low\",\n"
                "      \"description\": \"Description of the issue\",\n"
                "      \"line_numbers\": [line_numbers],\n"
                "      \"original_code\": \"original code snippet\",\n"
                "      \"improved_code\": \"improved code snippet\",\n"
                "      \"explanation\": \"Why this improvement matters\"\n"
                "    }\n"
                "  ],\n"
                "  \"summary\": \"Brief overall assessment\"\n"
                "}\n"
            )
            
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Track token usage
            self.tokens_consumed += response.usage.total_tokens
            
            return result.get('suggestions', [])
            
        except Exception as e:
            logger.error(f"Error getting AI suggestions: {str(e)}")
            return []
    
    def _apply_ai_suggestions(self, content, suggestions, file_path):
        """
        Apply AI suggestions to the code.
        
        Args:
            content: Original code content
            suggestions: List of improvement suggestions
            file_path: Path to the file
            
        Returns:
            Improved code content or None if no improvements were applied
        """
        if not suggestions:
            return None
        
        # Sort suggestions by line number (descending) to avoid position shifts
        sorted_suggestions = sorted(
            suggestions, 
            key=lambda x: x.get('line_numbers', [0])[0] if x.get('line_numbers') else 0,
            reverse=True
        )
        
        # Apply only high and medium severity suggestions
        applied_changes = 0
        original_content = content
        
        for suggestion in sorted_suggestions:
            severity = suggestion.get('severity', '').lower()
            if severity not in ('high', 'medium'):
                continue
                
            original_code = suggestion.get('original_code', '')
            improved_code = suggestion.get('improved_code', '')
            
            if not original_code or not improved_code or original_code == improved_code:
                continue
            
            # Simple direct replacement for exact matches
            if original_code in content:
                content = content.replace(original_code, improved_code)
                applied_changes += 1
                logger.info(f"Applied {severity} suggestion to {file_path}")
            else:
                # Try fuzzy matching for near matches
                try:
                    # If we have line numbers, use them for more precise replacement
                    line_numbers = suggestion.get('line_numbers', [])
                    if line_numbers:
                        lines = content.splitlines()
                        original_lines = original_code.splitlines()
                        
                        # Check if we have enough lines and the right range
                        if (len(lines) >= max(line_numbers) and 
                            len(original_lines) <= len(line_numbers)):
                            
                            # Extract the actual lines from the file
                            actual_lines = [lines[line-1] for line in line_numbers]
                            actual_block = '\n'.join(actual_lines)
                            
                            # If the actual block is similar enough to the original code, replace it
                            similarity = self._similarity(actual_block, original_code)
                            if similarity > 0.7:  # 70% similarity threshold
                                # Replace those specific lines
                                for i, line_num in enumerate(line_numbers):
                                    if i < len(improved_code.splitlines()):
                                        lines[line_num-1] = improved_code.splitlines()[i]
                                
                                content = '\n'.join(lines)
                                applied_changes += 1
                                logger.info(f"Applied {severity} suggestion to {file_path} (line-based)")
                except Exception as e:
                    logger.error(f"Error applying line-based suggestion: {str(e)}")
        
        return content if applied_changes > 0 else None
    
    def _similarity(self, str1, str2):
        """
        Calculate simple similarity between two strings (0.0 to 1.0).
        
        Args:
            str1: First string
            str2: Second string
            
        Returns:
            Similarity score between 0.0 and 1.0
        """
        # Use Python's difflib to calculate sequence similarity
        import difflib
        return difflib.SequenceMatcher(None, str1, str2).ratio()
    
    def generate_code_completion(self, code_context, language, max_tokens=500):
        """
        Generate code completion based on context.
        
        Args:
            code_context: Current code context
            language: Programming language
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated code completion
        """
        if not self.has_openai:
            return None
        
        try:
            # Construct prompt
            prompt = (
                f"Complete the following {language} code snippet. "
                "Continue in a logical way that follows best practices:\n\n"
                "```\n" + code_context + "\n```"
            )
            
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=max_tokens
            )
            
            completion = response.choices[0].message.content
            
            # Extract only the code part if it contains markdown code blocks
            if "```" in completion:
                code_blocks = re.findall(r"```(?:\w+)?\n(.*?)\n```", completion, re.DOTALL)
                if code_blocks:
                    completion = code_blocks[0]
            
            # Track token usage
            self.tokens_consumed += response.usage.total_tokens
            
            return completion
            
        except Exception as e:
            logger.error(f"Error generating code completion: {str(e)}")
            return None
    
    def explain_code(self, code, language):
        """
        Generate an explanation for the provided code.
        
        Args:
            code: Code to explain
            language: Programming language
            
        Returns:
            Explanation of the code
        """
        if not self.has_openai:
            return "OpenAI API not available. Cannot explain code."
        
        try:
            # Construct prompt
            prompt = (
                f"Explain what the following {language} code does in clear, "
                "simple terms. Break down the explanation by logical sections:\n\n"
                "```\n" + code + "\n```"
            )
            
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=800
            )
            
            explanation = response.choices[0].message.content
            
            # Track token usage
            self.tokens_consumed += response.usage.total_tokens
            
            return explanation
            
        except Exception as e:
            logger.error(f"Error explaining code: {str(e)}")
            return f"Error explaining code: {str(e)}"
    
    def generate_unit_tests(self, code, language):
        """
        Generate unit tests for the provided code.
        
        Args:
            code: Code to generate tests for
            language: Programming language
            
        Returns:
            Generated unit tests
        """
        if not self.has_openai:
            return "OpenAI API not available. Cannot generate unit tests."
        
        try:
            # Construct prompt
            prompt = (
                f"Generate comprehensive unit tests for the following {language} code. "
                "Include tests for normal cases, edge cases, and error handling. "
                "Use appropriate testing framework and style for the language:\n\n"
                "```\n" + code + "\n```"
            )
            
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=1000
            )
            
            tests = response.choices[0].message.content
            
            # Extract only the code part if it contains markdown code blocks
            if "```" in tests:
                code_blocks = re.findall(r"```(?:\w+)?\n(.*?)\n```", tests, re.DOTALL)
                if code_blocks:
                    tests = code_blocks[0]
            
            # Track token usage
            self.tokens_consumed += response.usage.total_tokens
            
            return tests
            
        except Exception as e:
            logger.error(f"Error generating unit tests: {str(e)}")
            return f"Error generating unit tests: {str(e)}"
    
    def get_tokens_consumed(self):
        """
        Get the number of tokens consumed by the AI model.
        
        Returns:
            Number of tokens consumed
        """
        return self.tokens_consumed


# Singleton instance
_continuous_coding_engine = None

def get_continuous_coding_engine(api_key=None):
    """
    Get a singleton instance of the continuous coding engine.
    
    Args:
        api_key: OpenAI API key (optional)
    
    Returns:
        ContinuousCodingEngine: Continuous coding engine instance
    """
    global _continuous_coding_engine
    if _continuous_coding_engine is None:
        _continuous_coding_engine = ContinuousCodingEngine(api_key)
    return _continuous_coding_engine


# Example usage
if __name__ == "__main__":
    print("Initializing PyWrite Continuous Coding Engine...")
    
    # Get API key from environment variable
    api_key = os.environ.get("OPENAI_API_KEY")
    
    if not api_key:
        print("Warning: OPENAI_API_KEY environment variable not set.")
        print("Advanced AI features will be disabled.")
    
    # Get the engine instance
    engine = get_continuous_coding_engine(api_key)
    
    # Demo code completion
    if engine.has_openai:
        python_code = """
def calculate_fibonacci(n):
    '''Calculate the nth Fibonacci number.'''
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)
"""
        
        completion = engine.generate_code_completion(python_code, 'python')
        print("\nCode Completion:")
        print(completion)
        
        # Demo code explanation
        explanation = engine.explain_code(python_code + completion, 'python')
        print("\nCode Explanation:")
        print(explanation)
        
        # Demo unit test generation
        tests = engine.generate_unit_tests(python_code + completion, 'python')
        print("\nGenerated Unit Tests:")
        print(tests)
    
    # Start the engine
    print("\nStarting continuous coding engine...")
    engine.start()
    
    print("Continuous coding engine running. Press Ctrl+C to stop.")
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping continuous coding engine...")
        engine.stop()
        print("Continuous coding engine stopped.")