#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyWrite Database Helper

This module provides database functionality for PyWrite, including:
- Code snippet storage and retrieval
- Autocomplete suggestions based on past coding patterns
- User settings and preferences storage
- Automation task management

Author: PyWrite
Date: 2025-03-28
"""

import os
import psycopg2
import psycopg2.extras
import json
import time
import re
from typing import Dict, List, Tuple, Any, Optional, Union


class DatabaseHelper:
    """Handles database interactions for PyWrite features."""
    
    def __init__(self):
        """Initialize database connection from environment variables."""
        self.conn = psycopg2.connect(
            host=os.environ.get("PGHOST"),
            port=os.environ.get("PGPORT"),
            user=os.environ.get("PGUSER"),
            password=os.environ.get("PGPASSWORD"),
            database=os.environ.get("PGDATABASE")
        )
        self.cursor = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        self._init_tables()
    
    def _init_tables(self) -> None:
        """Initialize database tables if they don't exist."""
        # Snippets table - stores code snippets for reuse
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS snippets (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            language VARCHAR(50) NOT NULL,
            code TEXT NOT NULL,
            description TEXT,
            tags TEXT[],
            usage_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Code patterns table - stores patterns for autocomplete
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS code_patterns (
            id SERIAL PRIMARY KEY,
            language VARCHAR(50) NOT NULL,
            pattern TEXT NOT NULL,
            completion TEXT NOT NULL,
            frequency INTEGER DEFAULT 1,
            context TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # User settings table - stores user preferences
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_settings (
            id SERIAL PRIMARY KEY,
            setting_key VARCHAR(255) UNIQUE NOT NULL,
            setting_value JSONB NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Automation tasks table - stores automation configurations
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS automation_tasks (
            id SERIAL PRIMARY KEY,
            task_name VARCHAR(255) NOT NULL,
            task_type VARCHAR(50) NOT NULL,
            trigger VARCHAR(50) NOT NULL,
            action JSONB NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Session history table - stores user activity history
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS session_history (
            id SERIAL PRIMARY KEY,
            session_id VARCHAR(255) NOT NULL,
            action_type VARCHAR(50) NOT NULL,
            action_data JSONB,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        self.conn.commit()
    
    def close(self) -> None:
        """Close database connection."""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
    
    # ---------- Snippet Management ----------
    
    def add_snippet(self, name: str, language: str, code: str, 
                   description: str = "", tags: List[str] = None) -> int:
        """
        Add a code snippet to the database.
        
        Args:
            name: Name of the snippet
            language: Programming language
            code: The actual code
            description: Optional description
            tags: Optional list of tags
        
        Returns:
            Snippet ID
        """
        if tags is None:
            tags = []
            
        self.cursor.execute("""
        INSERT INTO snippets (name, language, code, description, tags)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id
        """, (name, language, code, description, tags))
        
        snippet_id = self.cursor.fetchone()[0]
        self.conn.commit()
        return snippet_id
    
    def get_snippet(self, snippet_id: int) -> Dict:
        """
        Retrieve a snippet by ID.
        
        Args:
            snippet_id: ID of the snippet to retrieve
            
        Returns:
            Dictionary with snippet information
        """
        self.cursor.execute("""
        SELECT * FROM snippets WHERE id = %s
        """, (snippet_id,))
        
        result = self.cursor.fetchone()
        if result:
            self.cursor.execute("""
            UPDATE snippets SET usage_count = usage_count + 1
            WHERE id = %s
            """, (snippet_id,))
            self.conn.commit()
            return dict(result)
        return None
    
    def search_snippets(self, 
                       search_term: str = "", 
                       language: str = None, 
                       tags: List[str] = None,
                       limit: int = 20) -> List[Dict]:
        """
        Search for snippets based on criteria.
        
        Args:
            search_term: Text to search in name, description, or code
            language: Filter by programming language
            tags: Filter by tags
            limit: Maximum number of results
            
        Returns:
            List of matching snippets
        """
        query = "SELECT * FROM snippets WHERE 1=1"
        params = []
        
        if search_term:
            query += " AND (name ILIKE %s OR description ILIKE %s OR code ILIKE %s)"
            term = f"%{search_term}%"
            params.extend([term, term, term])
        
        if language:
            query += " AND language = %s"
            params.append(language)
        
        if tags and len(tags) > 0:
            placeholders = ", ".join(["%s"] * len(tags))
            query += f" AND tags && ARRAY[{placeholders}]"
            params.extend(tags)
        
        query += " ORDER BY usage_count DESC, updated_at DESC LIMIT %s"
        params.append(limit)
        
        self.cursor.execute(query, params)
        results = self.cursor.fetchall()
        return [dict(r) for r in results]
    
    # ---------- Autocomplete Management ----------
    
    def add_code_pattern(self, 
                        language: str, 
                        pattern: str, 
                        completion: str,
                        context: str = None) -> int:
        """
        Add or update a code pattern for autocomplete.
        
        Args:
            language: Programming language
            pattern: The trigger pattern
            completion: The suggested completion
            context: Optional context where this pattern is relevant
            
        Returns:
            Pattern ID
        """
        # Check if pattern already exists
        self.cursor.execute("""
        SELECT id, frequency FROM code_patterns
        WHERE language = %s AND pattern = %s AND completion = %s
        """, (language, pattern, completion))
        
        existing = self.cursor.fetchone()
        
        if existing:
            # Update frequency of existing pattern
            self.cursor.execute("""
            UPDATE code_patterns 
            SET frequency = %s, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
            """, (existing['frequency'] + 1, existing['id']))
            self.conn.commit()
            return existing['id']
        else:
            # Insert new pattern
            self.cursor.execute("""
            INSERT INTO code_patterns (language, pattern, completion, context)
            VALUES (%s, %s, %s, %s)
            RETURNING id
            """, (language, pattern, completion, context))
            
            pattern_id = self.cursor.fetchone()[0]
            self.conn.commit()
            return pattern_id
    
    def get_completions(self, 
                       language: str, 
                       current_text: str,
                       context: str = None,
                       limit: int = 5) -> List[Dict]:
        """
        Get autocomplete suggestions based on current text.
        
        Args:
            language: Programming language
            current_text: Current code being written
            context: Optional context (function name, class, etc.)
            limit: Maximum number of suggestions
            
        Returns:
            List of completion suggestions
        """
        # Get the last few characters as the pattern to match
        # Adjust pattern length based on language
        pattern_length = min(len(current_text), 50)
        pattern = current_text[-pattern_length:] if pattern_length > 0 else ""
        
        query = """
        SELECT pattern, completion, frequency
        FROM code_patterns
        WHERE language = %s AND %s LIKE CONCAT('%%', pattern)
        """
        params = [language, pattern]
        
        if context:
            query += " AND (context IS NULL OR context = %s)"
            params.append(context)
        
        query += " ORDER BY frequency DESC, LENGTH(pattern) DESC, updated_at DESC LIMIT %s"
        params.append(limit)
        
        self.cursor.execute(query, params)
        results = self.cursor.fetchall()
        
        return [dict(r) for r in results]
    
    def learn_from_code(self, language: str, code: str) -> int:
        """
        Learn patterns from existing code to improve autocomplete.
        
        Args:
            language: Programming language
            code: Code content to learn from
            
        Returns:
            Number of patterns learned
        """
        patterns_added = 0
        
        # Different learning strategies based on language
        if language == 'python':
            # Learn Python patterns
            # 1. Function definitions
            func_pattern = r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\((.*?)\):'
            for match in re.finditer(func_pattern, code):
                func_name = match.group(1)
                params = match.group(2)
                
                # Learn function pattern
                pattern = f"def {func_name}"
                completion = f"def {func_name}({params}):"
                self.add_code_pattern(language, pattern, completion)
                patterns_added += 1
                
                # Learn parameter pattern
                if params:
                    pattern = f"{func_name}("
                    completion = f"{func_name}({params})"
                    self.add_code_pattern(language, pattern, completion)
                    patterns_added += 1
            
            # 2. Class definitions
            class_pattern = r'class\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*(\(.*?\))?:'
            for match in re.finditer(class_pattern, code):
                class_name = match.group(1)
                inheritance = match.group(2) or ""
                
                pattern = f"class {class_name}"
                completion = f"class {class_name}{inheritance}:"
                self.add_code_pattern(language, pattern, completion)
                patterns_added += 1
            
            # 3. Common imports
            import_pattern = r'(from\s+[a-zA-Z_.]+\s+import\s+.*|import\s+.*)'
            for match in re.finditer(import_pattern, code):
                import_stmt = match.group(1)
                parts = import_stmt.split()
                if len(parts) >= 2:
                    pattern = " ".join(parts[:2])
                    completion = import_stmt
                    self.add_code_pattern(language, pattern, completion)
                    patterns_added += 1
        
        # Add more language-specific learning strategies here
        
        return patterns_added
    
    # ---------- Settings Management ----------
    
    def get_setting(self, key: str, default_value: Any = None) -> Any:
        """
        Get a user setting.
        
        Args:
            key: Setting key
            default_value: Default value if setting doesn't exist
            
        Returns:
            Setting value or default
        """
        self.cursor.execute("""
        SELECT setting_value FROM user_settings WHERE setting_key = %s
        """, (key,))
        
        result = self.cursor.fetchone()
        return result['setting_value'] if result else default_value
    
    def set_setting(self, key: str, value: Any) -> None:
        """
        Set or update a user setting.
        
        Args:
            key: Setting key
            value: Setting value (must be JSON serializable)
        """
        # Convert value to JSON string if it's not already
        if not isinstance(value, str):
            value = json.dumps(value)
        
        self.cursor.execute("""
        INSERT INTO user_settings (setting_key, setting_value)
        VALUES (%s, %s)
        ON CONFLICT (setting_key) 
        DO UPDATE SET setting_value = %s, updated_at = CURRENT_TIMESTAMP
        """, (key, value, value))
        
        self.conn.commit()
    
    # ---------- Automation Management ----------
    
    def add_automation_task(self, 
                           task_name: str, 
                           task_type: str,
                           trigger: str,
                           action: Dict) -> int:
        """
        Add an automation task.
        
        Args:
            task_name: Name of the task
            task_type: Type of automation (file_watcher, timer, etc.)
            trigger: What triggers the task
            action: JSON data with action details
            
        Returns:
            Task ID
        """
        self.cursor.execute("""
        INSERT INTO automation_tasks (task_name, task_type, trigger, action)
        VALUES (%s, %s, %s, %s)
        RETURNING id
        """, (task_name, task_type, trigger, json.dumps(action)))
        
        task_id = self.cursor.fetchone()[0]
        self.conn.commit()
        return task_id
    
    def get_automation_tasks(self, 
                            task_type: str = None, 
                            is_active: bool = True) -> List[Dict]:
        """
        Get automation tasks.
        
        Args:
            task_type: Optional filter by task type
            is_active: Get only active tasks
            
        Returns:
            List of automation tasks
        """
        query = "SELECT * FROM automation_tasks WHERE is_active = %s"
        params = [is_active]
        
        if task_type:
            query += " AND task_type = %s"
            params.append(task_type)
        
        self.cursor.execute(query, params)
        results = self.cursor.fetchall()
        return [dict(r) for r in results]
    
    def toggle_automation_task(self, task_id: int, is_active: bool) -> bool:
        """
        Enable or disable an automation task.
        
        Args:
            task_id: Task ID
            is_active: Whether the task should be active
            
        Returns:
            Success status
        """
        self.cursor.execute("""
        UPDATE automation_tasks
        SET is_active = %s, updated_at = CURRENT_TIMESTAMP
        WHERE id = %s
        """, (is_active, task_id))
        
        self.conn.commit()
        return self.cursor.rowcount > 0
    
    # ---------- Session History ----------
    
    def log_activity(self, 
                    session_id: str, 
                    action_type: str, 
                    action_data: Dict = None) -> None:
        """
        Log user activity for analytics and history.
        
        Args:
            session_id: Current session identifier
            action_type: Type of action performed
            action_data: Optional data related to the action
        """
        self.cursor.execute("""
        INSERT INTO session_history (session_id, action_type, action_data)
        VALUES (%s, %s, %s)
        """, (session_id, action_type, json.dumps(action_data) if action_data else None))
        
        self.conn.commit()
    
    def get_activity_history(self, 
                            session_id: str = None, 
                            action_type: str = None,
                            limit: int = 100) -> List[Dict]:
        """
        Get user activity history.
        
        Args:
            session_id: Optional filter by session ID
            action_type: Optional filter by action type
            limit: Maximum number of records to return
            
        Returns:
            List of activity records
        """
        query = "SELECT * FROM session_history WHERE 1=1"
        params = []
        
        if session_id:
            query += " AND session_id = %s"
            params.append(session_id)
        
        if action_type:
            query += " AND action_type = %s"
            params.append(action_type)
        
        query += " ORDER BY timestamp DESC LIMIT %s"
        params.append(limit)
        
        self.cursor.execute(query, params)
        results = self.cursor.fetchall()
        return [dict(r) for r in results]


# Initialize database
db = None

def get_db_instance():
    """
    Get a singleton instance of the database.
    
    Returns:
        DatabaseHelper: Database helper instance
    """
    global db
    if db is None:
        db = DatabaseHelper()
    return db


# Test functionality if run directly
if __name__ == "__main__":
    print("Initializing PyWrite database...")
    db = get_db_instance()
    
    # Add a sample snippet
    snippet_id = db.add_snippet(
        name="Hello World",
        language="python",
        code='print("Hello, World!")',
        description="A simple hello world program",
        tags=["beginner", "example"]
    )
    print(f"Added snippet with ID: {snippet_id}")
    
    # Get the snippet
    snippet = db.get_snippet(snippet_id)
    print(f"Retrieved snippet: {snippet['name']} in {snippet['language']}")
    
    # Add some code patterns
    python_code = """
def calculate_sum(a, b):
    return a + b
    
def calculate_product(a, b):
    return a * b
    
class Calculator:
    def __init__(self):
        self.history = []
    
    def add(self, a, b):
        result = a + b
        self.history.append(f"Added {a} + {b} = {result}")
        return result
    """
    
    patterns = db.learn_from_code("python", python_code)
    print(f"Learned {patterns} patterns from code")
    
    # Get completions
    completions = db.get_completions("python", "def calculate_")
    print("Autocomplete suggestions:")
    for completion in completions:
        print(f"  {completion['completion']} (frequency: {completion['frequency']})")
    
    # Store a setting
    db.set_setting("theme", "dark")
    theme = db.get_setting("theme")
    print(f"Theme setting: {theme}")
    
    # Close the connection
    db.close()
    print("Database test complete.")