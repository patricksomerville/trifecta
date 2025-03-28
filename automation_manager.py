#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyWrite Automation Manager

This module provides advanced automation capabilities:
- File watching for automated events
- Continuous code improvement
- Scheduled tasks for maintenance
- Event-based triggers for actions
- Code generation continuity

Author: PyWrite
Date: 2025-03-28
"""

import os
import time
import threading
import json
import re
import logging
import queue
import importlib
import inspect
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any, Optional, Union, Callable
from database_helper import get_db_instance
from autocomplete_engine import AutocompleteEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('automation.log')
    ]
)

logger = logging.getLogger('PyWrite.Automation')


class AutomationManager:
    """Manages automated tasks and continuous coding operations."""
    
    def __init__(self):
        """Initialize the automation manager."""
        self.db = get_db_instance()
        self.autocomplete = AutocompleteEngine()
        self.running = False
        self.tasks = {}
        self.event_queue = queue.Queue()
        self.worker_thread = None
        self.file_watchers = {}
        self.scheduled_tasks = {}
        self.last_run_times = {}
        
        # Dictionary of registered event handlers
        self.event_handlers = {
            'file_modified': [],
            'file_created': [],
            'code_generated': [],
            'autocomplete_triggered': [],
            'save_requested': [],
            'run_requested': [],
            'task_completed': [],
            'timer_elapsed': [],
            'voice_command': []
        }
        
        # Load tasks from database
        self._load_tasks()
    
    def start(self):
        """Start the automation manager and all registered tasks."""
        if self.running:
            return
        
        self.running = True
        self.worker_thread = threading.Thread(target=self._event_processor, daemon=True)
        self.worker_thread.start()
        
        # Start all active tasks
        self._start_active_tasks()
        
        logger.info("Automation manager started")
    
    def stop(self):
        """Stop the automation manager and all tasks."""
        if not self.running:
            return
            
        self.running = False
        
        # Stop all tasks
        for task_name in list(self.tasks.keys()):
            self._stop_task(task_name)
        
        # Clear the event queue
        while not self.event_queue.empty():
            try:
                self.event_queue.get_nowait()
            except queue.Empty:
                break
        
        if self.worker_thread and self.worker_thread.is_alive():
            self.worker_thread.join(timeout=5.0)
            
        logger.info("Automation manager stopped")
    
    def _load_tasks(self):
        """Load automation tasks from the database."""
        try:
            tasks = self.db.get_automation_tasks(is_active=True)
            for task in tasks:
                self._register_task(task)
        except Exception as e:
            logger.error(f"Failed to load tasks from database: {str(e)}")
    
    def _start_active_tasks(self):
        """Start all active tasks."""
        for task_name, task in self.tasks.items():
            if task.get('is_active', False):
                self._start_task(task_name)
    
    def _register_task(self, task_data):
        """Register a task from database data."""
        task_name = task_data['task_name']
        task_type = task_data['task_type']
        trigger = task_data['trigger']
        action = task_data['action']
        
        if isinstance(action, str):
            try:
                action = json.loads(action)
            except:
                pass
        
        self.tasks[task_name] = {
            'id': task_data['id'],
            'type': task_type,
            'trigger': trigger,
            'action': action,
            'is_active': task_data.get('is_active', True),
            'thread': None,
            'stop_event': threading.Event(),
            'created_at': task_data.get('created_at', datetime.now()),
            'updated_at': task_data.get('updated_at', datetime.now())
        }
    
    def _start_task(self, task_name):
        """Start a registered task."""
        if task_name not in self.tasks:
            logger.warning(f"Task '{task_name}' not found")
            return False
            
        task = self.tasks[task_name]
        
        if task.get('thread') and task['thread'].is_alive():
            logger.warning(f"Task '{task_name}' is already running")
            return False
        
        # Reset the stop event
        task['stop_event'] = threading.Event()
        
        # Start the task based on its type
        task_type = task['type']
        
        if task_type == 'file_watcher':
            return self._start_file_watcher(task_name)
        elif task_type == 'timer':
            return self._start_timer_task(task_name)
        elif task_type == 'continuous_processor':
            return self._start_continuous_processor(task_name)
        elif task_type == 'code_generator':
            return self._start_code_generator(task_name)
        else:
            logger.warning(f"Unknown task type: {task_type}")
            return False
    
    def _stop_task(self, task_name):
        """Stop a running task."""
        if task_name not in self.tasks:
            logger.warning(f"Task '{task_name}' not found")
            return False
            
        task = self.tasks[task_name]
        
        # Signal the task to stop
        task['stop_event'].set()
        
        # Wait for the task to finish
        if task.get('thread') and task['thread'].is_alive():
            task['thread'].join(timeout=5.0)
            
        # Clear the thread reference
        task['thread'] = None
        
        logger.info(f"Task '{task_name}' stopped")
        return True
    
    def _event_processor(self):
        """Process events from the event queue."""
        while self.running:
            try:
                # Get the next event with a timeout
                try:
                    event = self.event_queue.get(timeout=1.0)
                except queue.Empty:
                    continue
                
                # Process the event
                event_type = event.get('type')
                event_data = event.get('data', {})
                
                # Call registered handlers for this event type
                if event_type in self.event_handlers:
                    for handler in self.event_handlers[event_type]:
                        try:
                            handler(event_data)
                        except Exception as e:
                            logger.error(f"Error in event handler for '{event_type}': {str(e)}")
                
                self.event_queue.task_done()
                
            except Exception as e:
                logger.error(f"Error in event processor: {str(e)}")
                time.sleep(1.0)  # Avoid tight loop on error
    
    def _start_file_watcher(self, task_name):
        """Start a file watcher task."""
        task = self.tasks[task_name]
        action = task['action']
        
        # Get the directory and patterns to watch
        directory = action.get('directory', '.')
        patterns = action.get('patterns', ['*.py'])
        
        # Create a thread function for the watcher
        def watcher_thread():
            try:
                from watchdog.observers import Observer
                from watchdog.events import FileSystemEventHandler, FileModifiedEvent
                
                class EventHandler(FileSystemEventHandler):
                    def on_modified(self, event):
                        if task['stop_event'].is_set():
                            return
                            
                        if not event.is_directory:
                            # Check if the file matches any pattern
                            file_path = event.src_path
                            if not any(re.match(pattern, file_path) for pattern in patterns):
                                return
                                
                            # Queue an event
                            self.event_queue.put({
                                'type': 'file_modified',
                                'data': {
                                    'file_path': file_path,
                                    'task_name': task_name
                                }
                            })
                            
                            # Execute the specified action
                            action_type = action.get('action_type')
                            if action_type == 'analyze_code':
                                self._analyze_code_file(file_path)
                            elif action_type == 'learn_patterns':
                                self._learn_patterns_from_file(file_path)
                            elif action_type == 'run_function':
                                self._run_function(
                                    action.get('module', ''),
                                    action.get('function', ''),
                                    file_path=file_path
                                )
                
                # Create observer
                handler = EventHandler()
                handler.event_queue = self.event_queue
                handler._analyze_code_file = self._analyze_code_file
                handler._learn_patterns_from_file = self._learn_patterns_from_file
                handler._run_function = self._run_function
                
                observer = Observer()
                observer.schedule(handler, directory, recursive=True)
                observer.start()
                
                # Wait until stop event is set
                while not task['stop_event'].is_set():
                    time.sleep(1.0)
                    
                observer.stop()
                observer.join()
                
            except ImportError:
                logger.error(f"watchdog module is required for file watching")
            except Exception as e:
                logger.error(f"Error in file watcher '{task_name}': {str(e)}")
        
        # Create and start the thread
        task['thread'] = threading.Thread(target=watcher_thread, daemon=True)
        task['thread'].start()
        
        logger.info(f"File watcher task '{task_name}' started")
        return True
    
    def _start_timer_task(self, task_name):
        """Start a timer-based task."""
        task = self.tasks[task_name]
        action = task['action']
        
        # Get the interval in seconds
        interval = action.get('interval', 60)  # Default: 1 minute
        
        # Create a thread function for the timer
        def timer_thread():
            try:
                while not task['stop_event'].is_set():
                    # Queue a timer event
                    self.event_queue.put({
                        'type': 'timer_elapsed',
                        'data': {
                            'task_name': task_name,
                            'timestamp': datetime.now().isoformat()
                        }
                    })
                    
                    # Execute the specified action
                    action_type = action.get('action_type')
                    if action_type == 'run_function':
                        self._run_function(
                            action.get('module', ''),
                            action.get('function', ''),
                            task_name=task_name
                        )
                    
                    # Wait for the next interval or until stopped
                    task['stop_event'].wait(interval)
            
            except Exception as e:
                logger.error(f"Error in timer task '{task_name}': {str(e)}")
        
        # Create and start the thread
        task['thread'] = threading.Thread(target=timer_thread, daemon=True)
        task['thread'].start()
        
        logger.info(f"Timer task '{task_name}' started with interval {interval}s")
        return True
    
    def _start_continuous_processor(self, task_name):
        """Start a continuous processor task."""
        task = self.tasks[task_name]
        action = task['action']
        
        # Get the processor details
        processor_type = action.get('processor_type', 'code_improver')
        interval = action.get('interval', 300)  # Default: 5 minutes
        
        # Create a thread function for the processor
        def processor_thread():
            try:
                while not task['stop_event'].is_set():
                    # Execute based on processor type
                    if processor_type == 'code_improver':
                        self._run_code_improver(
                            action.get('directory', '.'),
                            action.get('patterns', ['*.py']),
                            action.get('max_files', 5)
                        )
                    elif processor_type == 'snippet_collector':
                        self._run_snippet_collector(
                            action.get('directory', '.'),
                            action.get('patterns', ['*.py']),
                            action.get('min_lines', 5),
                            action.get('max_files', 10)
                        )
                    
                    # Queue a completion event
                    self.event_queue.put({
                        'type': 'task_completed',
                        'data': {
                            'task_name': task_name,
                            'processor_type': processor_type,
                            'timestamp': datetime.now().isoformat()
                        }
                    })
                    
                    # Wait for the next interval or until stopped
                    task['stop_event'].wait(interval)
            
            except Exception as e:
                logger.error(f"Error in continuous processor '{task_name}': {str(e)}")
        
        # Create and start the thread
        task['thread'] = threading.Thread(target=processor_thread, daemon=True)
        task['thread'].start()
        
        logger.info(f"Continuous processor '{task_name}' started with interval {interval}s")
        return True
    
    def _start_code_generator(self, task_name):
        """Start a code generator task."""
        task = self.tasks[task_name]
        action = task['action']
        
        # Create a thread function for the generator
        def generator_thread():
            try:
                # Execute once immediately
                self._run_code_generator(
                    task_name,
                    action.get('template', ''),
                    action.get('output_file', ''),
                    action.get('params', {})
                )
                
                # If it's a one-time task, we're done
                if action.get('one_time', False):
                    return
                
                # Otherwise, run periodically
                interval = action.get('interval', 3600)  # Default: 1 hour
                
                while not task['stop_event'].is_set():
                    # Wait for the next interval or until stopped
                    task['stop_event'].wait(interval)
                    
                    if task['stop_event'].is_set():
                        break
                    
                    # Run the generator again
                    self._run_code_generator(
                        task_name,
                        action.get('template', ''),
                        action.get('output_file', ''),
                        action.get('params', {})
                    )
            
            except Exception as e:
                logger.error(f"Error in code generator '{task_name}': {str(e)}")
        
        # Create and start the thread
        task['thread'] = threading.Thread(target=generator_thread, daemon=True)
        task['thread'].start()
        
        logger.info(f"Code generator task '{task_name}' started")
        return True
    
    def _analyze_code_file(self, file_path):
        """Analyze a code file for patterns and issues."""
        if not os.path.exists(file_path):
            logger.warning(f"File not found: {file_path}")
            return
        
        # Determine language from file extension
        _, ext = os.path.splitext(file_path)
        language = None
        
        if ext == '.py':
            language = 'python'
        elif ext in ['.js', '.jsx']:
            language = 'javascript'
        else:
            logger.info(f"Unsupported file type for analysis: {ext}")
            return
        
        try:
            # Read the file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Learn patterns for autocomplete
            patterns_learned = self.autocomplete.learn_from_file(file_path, language)
            
            # Basic code analysis
            issues = self._basic_code_analysis(content, language)
            
            logger.info(f"Analyzed {file_path}: learned {patterns_learned} patterns, found {len(issues)} issues")
            
            # Queue an event with the analysis results
            self.event_queue.put({
                'type': 'code_analyzed',
                'data': {
                    'file_path': file_path,
                    'language': language,
                    'patterns_learned': patterns_learned,
                    'issues': issues
                }
            })
            
        except Exception as e:
            logger.error(f"Error analyzing {file_path}: {str(e)}")
    
    def _learn_patterns_from_file(self, file_path):
        """Learn patterns from a file for autocomplete suggestions."""
        if not os.path.exists(file_path):
            logger.warning(f"File not found: {file_path}")
            return
        
        try:
            patterns_learned = self.autocomplete.learn_from_file(file_path)
            logger.info(f"Learned {patterns_learned} patterns from {file_path}")
            
            # Queue an event
            self.event_queue.put({
                'type': 'patterns_learned',
                'data': {
                    'file_path': file_path,
                    'patterns_learned': patterns_learned
                }
            })
            
        except Exception as e:
            logger.error(f"Error learning patterns from {file_path}: {str(e)}")
    
    def _run_function(self, module_name, function_name, **kwargs):
        """Run a named function from a module."""
        if not module_name or not function_name:
            logger.warning(f"Module or function name is empty")
            return
        
        try:
            # Dynamic import of the module
            module = importlib.import_module(module_name)
            
            # Get the function
            if not hasattr(module, function_name):
                logger.warning(f"Function '{function_name}' not found in module '{module_name}'")
                return
                
            func = getattr(module, function_name)
            
            # Call the function with kwargs
            result = func(**kwargs)
            
            logger.info(f"Function '{module_name}.{function_name}' executed successfully")
            return result
            
        except ImportError:
            logger.error(f"Module '{module_name}' not found")
        except Exception as e:
            logger.error(f"Error running function '{module_name}.{function_name}': {str(e)}")
    
    def _run_code_improver(self, directory, patterns, max_files):
        """Run code improver on matching files."""
        from comment_assistant import analyze_code_file, generate_improved_file
        
        try:
            # Find matching files
            matching_files = []
            for pattern in patterns:
                for root, _, files in os.walk(directory):
                    for file in files:
                        if re.match(pattern, file):
                            file_path = os.path.join(root, file)
                            matching_files.append(file_path)
            
            # Limit the number of files
            matching_files = matching_files[:max_files]
            
            # Process each file
            for file_path in matching_files:
                try:
                    # Analyze the file
                    analysis = analyze_code_file(file_path)
                    
                    # If there are missing docstrings or comments, improve the file
                    if analysis.get('missing_docstrings', 0) > 0 or analysis.get('suggested_inline', 0) > 0:
                        # Generate an improved version
                        improved_content = generate_improved_file(file_path)
                        
                        # Create a backup
                        backup_path = f"{file_path}.bak"
                        with open(file_path, 'r', encoding='utf-8') as f:
                            original_content = f.read()
                        
                        with open(backup_path, 'w', encoding='utf-8') as f:
                            f.write(original_content)
                        
                        # Write the improved version
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(improved_content)
                        
                        logger.info(f"Improved file: {file_path}")
                        
                        # Queue an event
                        self.event_queue.put({
                            'type': 'file_improved',
                            'data': {
                                'file_path': file_path,
                                'backup_path': backup_path
                            }
                        })
                
                except Exception as e:
                    logger.error(f"Error improving file {file_path}: {str(e)}")
        
        except Exception as e:
            logger.error(f"Error in code improver: {str(e)}")
    
    def _run_snippet_collector(self, directory, patterns, min_lines, max_files):
        """Collect code snippets from files."""
        try:
            # Find matching files
            matching_files = []
            for pattern in patterns:
                for root, _, files in os.walk(directory):
                    for file in files:
                        if re.match(pattern, file):
                            file_path = os.path.join(root, file)
                            matching_files.append(file_path)
            
            # Limit the number of files
            matching_files = matching_files[:max_files]
            
            snippets_added = 0
            
            # Process each file
            for file_path in matching_files:
                try:
                    # Determine language from file extension
                    _, ext = os.path.splitext(file_path)
                    language = None
                    
                    if ext == '.py':
                        language = 'python'
                        # Extract Python functions and classes
                        snippets_added += self._extract_python_snippets(file_path, min_lines)
                    elif ext in ['.js', '.jsx']:
                        language = 'javascript'
                        # Extract JavaScript functions and classes
                        # (Implementation would be similar to Python)
                
                except Exception as e:
                    logger.error(f"Error collecting snippets from {file_path}: {str(e)}")
            
            logger.info(f"Collected {snippets_added} snippets from {len(matching_files)} files")
            
        except Exception as e:
            logger.error(f"Error in snippet collector: {str(e)}")
    
    def _extract_python_snippets(self, file_path, min_lines):
        """Extract functions and classes from Python files as snippets."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            snippets_added = 0
            
            try:
                tree = ast.parse(content)
                
                # Extract functions
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        # Get the function code
                        func_lines = content.splitlines()[node.lineno-1:node.end_lineno]
                        func_code = '\n'.join(func_lines)
                        
                        # Only add if it's substantial enough
                        if len(func_lines) >= min_lines:
                            # Add as a snippet
                            self.autocomplete.add_snippet(
                                name=f"func_{node.name}",
                                language='python',
                                code=func_code,
                                description=f"Function {node.name} from {os.path.basename(file_path)}"
                            )
                            snippets_added += 1
                    
                    elif isinstance(node, ast.ClassDef):
                        # Get the class code
                        class_lines = content.splitlines()[node.lineno-1:node.end_lineno]
                        class_code = '\n'.join(class_lines)
                        
                        # Only add if it's substantial enough
                        if len(class_lines) >= min_lines:
                            # Add as a snippet
                            self.autocomplete.add_snippet(
                                name=f"class_{node.name}",
                                language='python',
                                code=class_code,
                                description=f"Class {node.name} from {os.path.basename(file_path)}"
                            )
                            snippets_added += 1
            
            except SyntaxError:
                # If there's a syntax error, we'll extract snippets differently
                # using regular expressions
                
                # Function pattern
                func_pattern = r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(.*?\):\s*(?:\s*""".*?""")?(?:\s*#.*?$)*((?:\s+.*?$)+)'
                for match in re.finditer(func_pattern, content, re.MULTILINE | re.DOTALL):
                    func_name = match.group(1)
                    func_code = match.group(0)
                    
                    # Count the lines
                    lines = func_code.splitlines()
                    if len(lines) >= min_lines:
                        # Add as a snippet
                        self.autocomplete.add_snippet(
                            name=f"func_{func_name}",
                            language='python',
                            code=func_code,
                            description=f"Function {func_name} from {os.path.basename(file_path)}"
                        )
                        snippets_added += 1
                
                # Class pattern
                class_pattern = r'class\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*(?:\(.*?\))?:\s*(?:\s*""".*?""")?(?:\s*#.*?$)*((?:\s+.*?$)+)'
                for match in re.finditer(class_pattern, content, re.MULTILINE | re.DOTALL):
                    class_name = match.group(1)
                    class_code = match.group(0)
                    
                    # Count the lines
                    lines = class_code.splitlines()
                    if len(lines) >= min_lines:
                        # Add as a snippet
                        self.autocomplete.add_snippet(
                            name=f"class_{class_name}",
                            language='python',
                            code=class_code,
                            description=f"Class {class_name} from {os.path.basename(file_path)}"
                        )
                        snippets_added += 1
            
            return snippets_added
            
        except Exception as e:
            logger.error(f"Error extracting Python snippets from {file_path}: {str(e)}")
            return 0
    
    def _run_code_generator(self, task_name, template, output_file, params):
        """Generate code from a template."""
        if not template or not output_file:
            logger.warning(f"Template or output file is empty")
            return
        
        try:
            # Check if the template is a file path or a string template
            template_content = ""
            if os.path.exists(template):
                with open(template, 'r', encoding='utf-8') as f:
                    template_content = f.read()
            else:
                template_content = template
            
            # Simple template replacement
            for key, value in params.items():
                template_content = template_content.replace(f"{{{key}}}", str(value))
            
            # Create parent directories if needed
            os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
            
            # Write to the output file
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(template_content)
            
            logger.info(f"Generated code written to {output_file}")
            
            # Queue an event
            self.event_queue.put({
                'type': 'code_generated',
                'data': {
                    'task_name': task_name,
                    'output_file': output_file
                }
            })
            
        except Exception as e:
            logger.error(f"Error in code generator: {str(e)}")
    
    def _basic_code_analysis(self, content, language):
        """Perform basic code analysis to identify issues."""
        issues = []
        
        if language == 'python':
            # Check for potential Python issues
            try:
                # Parse the AST
                tree = ast.parse(content)
                
                # Check for excessively complex functions
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        # Count the number of nodes in the function
                        complexity = sum(1 for _ in ast.walk(node))
                        
                        if complexity > 50:  # Arbitrary threshold
                            issues.append({
                                'type': 'complexity',
                                'line': node.lineno,
                                'message': f"Function '{node.name}' is too complex (complexity: {complexity})"
                            })
                
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
                            'message': f"Unused import: '{name}'"
                        })
            
            except SyntaxError as e:
                issues.append({
                    'type': 'syntax_error',
                    'line': e.lineno,
                    'message': f"Syntax error: {str(e)}"
                })
            except Exception as e:
                issues.append({
                    'type': 'analysis_error',
                    'message': f"Error during analysis: {str(e)}"
                })
        
        return issues
    
    def register_event_handler(self, event_type, handler):
        """
        Register a handler for a specific event type.
        
        Args:
            event_type: Type of event
            handler: Function to call when event occurs
        """
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
            
        self.event_handlers[event_type].append(handler)
    
    def trigger_event(self, event_type, event_data=None):
        """
        Manually trigger an event.
        
        Args:
            event_type: Type of event
            event_data: Optional event data
        """
        self.event_queue.put({
            'type': event_type,
            'data': event_data or {}
        })
    
    def add_automation_task(self, task_name, task_type, trigger, action):
        """
        Add a new automation task.
        
        Args:
            task_name: Name of the task
            task_type: Type of task
            trigger: What triggers the task
            action: Action to perform
            
        Returns:
            Task ID or None on failure
        """
        try:
            # Add to database
            task_id = self.db.add_automation_task(
                task_name=task_name,
                task_type=task_type,
                trigger=trigger,
                action=action
            )
            
            # Register the task
            task_data = {
                'id': task_id,
                'task_name': task_name,
                'task_type': task_type,
                'trigger': trigger,
                'action': action,
                'is_active': True
            }
            self._register_task(task_data)
            
            # Start the task if automation is running
            if self.running:
                self._start_task(task_name)
            
            logger.info(f"Added automation task: {task_name}")
            return task_id
            
        except Exception as e:
            logger.error(f"Failed to add automation task: {str(e)}")
            return None
    
    def toggle_task(self, task_name, is_active):
        """
        Enable or disable a task.
        
        Args:
            task_name: Name of the task
            is_active: Whether the task should be active
            
        Returns:
            Success status
        """
        if task_name not in self.tasks:
            logger.warning(f"Task '{task_name}' not found")
            return False
        
        task = self.tasks[task_name]
        
        try:
            # Update in database
            success = self.db.toggle_automation_task(task['id'], is_active)
            
            if success:
                # Update local task
                task['is_active'] = is_active
                
                # Start or stop the task
                if is_active and self.running:
                    if not task.get('thread') or not task['thread'].is_alive():
                        self._start_task(task_name)
                else:
                    self._stop_task(task_name)
                
                logger.info(f"Task '{task_name}' {'enabled' if is_active else 'disabled'}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to toggle task: {str(e)}")
            return False


# Singleton instance
_automation_manager = None

def get_automation_manager():
    """
    Get a singleton instance of the automation manager.
    
    Returns:
        AutomationManager: Automation manager instance
    """
    global _automation_manager
    if _automation_manager is None:
        _automation_manager = AutomationManager()
    return _automation_manager


# Example usage
if __name__ == "__main__":
    print("Initializing PyWrite Automation Manager...")
    
    # Get the manager
    manager = get_automation_manager()
    
    # Start the manager
    manager.start()
    
    # Add a file watcher task
    task_id = manager.add_automation_task(
        task_name="Python File Watcher",
        task_type="file_watcher",
        trigger="file_modified",
        action={
            "directory": ".",
            "patterns": ["*.py"],
            "action_type": "learn_patterns"
        }
    )
    
    print(f"Added task with ID: {task_id}")
    
    # Register an event handler
    def file_modified_handler(data):
        print(f"File modified: {data.get('file_path')}")
    
    manager.register_event_handler('file_modified', file_modified_handler)
    
    print("Automation manager running. Press Ctrl+C to stop.")
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping automation manager...")
        manager.stop()
        print("Automation manager stopped.")