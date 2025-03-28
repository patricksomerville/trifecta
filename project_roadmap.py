#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyWrite Project Roadmap System

This module provides a structured planning system for coding projects:
- Phase-based roadmap creation and management
- Project requirement specification
- Component architecture planning
- Detailed task breakdown
- Integration with autocomplete and coding features

Author: PyWrite
Date: 2025-03-28
"""

import os
import json
import uuid
import time
import datetime
from typing import Dict, List, Any, Optional, Union
from database_helper import get_db_instance

class RoadmapPhase:
    """Represents a single phase in a project roadmap."""
    
    def __init__(self, 
                name: str, 
                description: str = "", 
                status: str = "planned",
                order: int = 0):
        """
        Initialize a roadmap phase.
        
        Args:
            name: Name of the phase
            description: Description of what happens in this phase
            status: Current status (planned, in_progress, completed, blocked)
            order: Display order in the roadmap
        """
        self.id = str(uuid.uuid4())
        self.name = name
        self.description = description
        self.status = status
        self.order = order
        self.tasks = []
        self.components = []
        self.requirements = []
        self.created_at = datetime.datetime.now().isoformat()
        self.updated_at = self.created_at
    
    def to_dict(self) -> Dict:
        """Convert phase to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "status": self.status,
            "order": self.order,
            "tasks": self.tasks,
            "components": self.components,
            "requirements": self.requirements,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'RoadmapPhase':
        """Create phase from dictionary."""
        phase = cls(
            name=data.get("name", "Unnamed Phase"),
            description=data.get("description", ""),
            status=data.get("status", "planned"),
            order=data.get("order", 0)
        )
        phase.id = data.get("id", phase.id)
        phase.tasks = data.get("tasks", [])
        phase.components = data.get("components", [])
        phase.requirements = data.get("requirements", [])
        phase.created_at = data.get("created_at", phase.created_at)
        phase.updated_at = data.get("updated_at", phase.updated_at)
        return phase
    
    def add_task(self, title: str, description: str = "", 
                priority: str = "medium", 
                estimated_hours: float = 1.0) -> str:
        """
        Add a task to this phase.
        
        Args:
            title: Task title
            description: Detailed description
            priority: Priority level (low, medium, high)
            estimated_hours: Estimated hours to complete
            
        Returns:
            Task ID
        """
        task_id = str(uuid.uuid4())
        task = {
            "id": task_id,
            "title": title,
            "description": description,
            "priority": priority,
            "estimated_hours": estimated_hours,
            "status": "todo",
            "created_at": datetime.datetime.now().isoformat()
        }
        self.tasks.append(task)
        self.updated_at = datetime.datetime.now().isoformat()
        return task_id
    
    def add_component(self, name: str, purpose: str = "", 
                     implementation_details: str = "",
                     dependencies: List[str] = None) -> str:
        """
        Add a component to this phase.
        
        Args:
            name: Component name
            purpose: Purpose of the component
            implementation_details: Implementation guidance
            dependencies: List of dependency component names
            
        Returns:
            Component ID
        """
        if dependencies is None:
            dependencies = []
            
        component_id = str(uuid.uuid4())
        component = {
            "id": component_id,
            "name": name,
            "purpose": purpose,
            "implementation_details": implementation_details,
            "dependencies": dependencies,
            "created_at": datetime.datetime.now().isoformat()
        }
        self.components.append(component)
        self.updated_at = datetime.datetime.now().isoformat()
        return component_id
    
    def add_requirement(self, title: str, description: str = "", 
                       requirement_type: str = "functional",
                       priority: str = "medium") -> str:
        """
        Add a requirement to this phase.
        
        Args:
            title: Requirement title
            description: Detailed description
            requirement_type: Type (functional, non_functional, technical)
            priority: Priority level (low, medium, high)
            
        Returns:
            Requirement ID
        """
        requirement_id = str(uuid.uuid4())
        requirement = {
            "id": requirement_id,
            "title": title,
            "description": description,
            "type": requirement_type,
            "priority": priority,
            "status": "defined",
            "created_at": datetime.datetime.now().isoformat()
        }
        self.requirements.append(requirement)
        self.updated_at = datetime.datetime.now().isoformat()
        return requirement_id
    
    def update_status(self, status: str) -> None:
        """
        Update phase status.
        
        Args:
            status: New status (planned, in_progress, completed, blocked)
        """
        self.status = status
        self.updated_at = datetime.datetime.now().isoformat()


class ProjectRoadmap:
    """Manages a complete project roadmap with multiple phases."""
    
    def __init__(self, 
                name: str, 
                description: str = "", 
                project_type: str = "software"):
        """
        Initialize a project roadmap.
        
        Args:
            name: Project name
            description: Project description
            project_type: Type of project (software, data, etc.)
        """
        self.id = str(uuid.uuid4())
        self.name = name
        self.description = description
        self.project_type = project_type
        self.phases = []
        self.tags = []
        self.created_at = datetime.datetime.now().isoformat()
        self.updated_at = self.created_at
        
        # Create default phases based on project type
        self._create_default_phases()
    
    def _create_default_phases(self) -> None:
        """Create default phases based on project type."""
        if self.project_type == "software":
            phases = [
                ("1. Requirements", "Define project requirements and specifications"),
                ("2. Design", "Design application architecture and components"),
                ("3. Implementation", "Implement core functionality"),
                ("4. Testing", "Test the application for bugs and issues"),
                ("5. Deployment", "Prepare for and execute deployment"),
                ("6. Maintenance", "Ongoing maintenance and improvements")
            ]
            
            for i, (name, desc) in enumerate(phases):
                self.add_phase(name, desc, "planned", i)
        
        elif self.project_type == "data":
            phases = [
                ("1. Data Collection", "Identify and collect required data"),
                ("2. Data Cleaning", "Clean and preprocess data"),
                ("3. Exploratory Analysis", "Analyze data patterns and insights"),
                ("4. Modeling", "Develop data models"),
                ("5. Evaluation", "Evaluate model performance"),
                ("6. Deployment", "Deploy models to production")
            ]
            
            for i, (name, desc) in enumerate(phases):
                self.add_phase(name, desc, "planned", i)
    
    def to_dict(self) -> Dict:
        """Convert roadmap to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "project_type": self.project_type,
            "phases": [phase.to_dict() for phase in self.phases],
            "tags": self.tags,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ProjectRoadmap':
        """Create roadmap from dictionary."""
        roadmap = cls(
            name=data.get("name", "Unnamed Project"),
            description=data.get("description", ""),
            project_type=data.get("project_type", "software")
        )
        roadmap.id = data.get("id", roadmap.id)
        roadmap.tags = data.get("tags", [])
        roadmap.created_at = data.get("created_at", roadmap.created_at)
        roadmap.updated_at = data.get("updated_at", roadmap.updated_at)
        
        # Clear default phases and load saved phases
        roadmap.phases.clear()
        for phase_data in data.get("phases", []):
            roadmap.phases.append(RoadmapPhase.from_dict(phase_data))
        
        return roadmap
    
    def add_phase(self, name: str, description: str = "", 
                 status: str = "planned", order: int = None) -> str:
        """
        Add a phase to the roadmap.
        
        Args:
            name: Phase name
            description: Phase description
            status: Phase status
            order: Display order (if None, appended to end)
            
        Returns:
            Phase ID
        """
        if order is None:
            order = len(self.phases)
            
        phase = RoadmapPhase(name, description, status, order)
        self.phases.append(phase)
        self.updated_at = datetime.datetime.now().isoformat()
        return phase.id
    
    def get_phase(self, phase_id: str) -> Optional[RoadmapPhase]:
        """
        Get a phase by ID.
        
        Args:
            phase_id: ID of the phase to retrieve
            
        Returns:
            RoadmapPhase object or None if not found
        """
        for phase in self.phases:
            if phase.id == phase_id:
                return phase
        return None
    
    def reorder_phases(self, phase_ids: List[str]) -> bool:
        """
        Reorder phases based on list of phase IDs.
        
        Args:
            phase_ids: Ordered list of phase IDs
            
        Returns:
            Success status
        """
        if len(phase_ids) != len(self.phases):
            return False
            
        # Verify all phase IDs exist
        phase_dict = {phase.id: phase for phase in self.phases}
        for phase_id in phase_ids:
            if phase_id not in phase_dict:
                return False
                
        # Update order
        for i, phase_id in enumerate(phase_ids):
            phase_dict[phase_id].order = i
            
        # Sort phases by order
        self.phases.sort(key=lambda p: p.order)
        self.updated_at = datetime.datetime.now().isoformat()
        return True
    
    def add_tag(self, tag: str) -> None:
        """
        Add a tag to the roadmap.
        
        Args:
            tag: Tag to add
        """
        if tag not in self.tags:
            self.tags.append(tag)
            self.updated_at = datetime.datetime.now().isoformat()
    
    def generate_code_context(self) -> Dict:
        """
        Generate a context dictionary for code generation.
        
        Returns:
            Dictionary with project context information
        """
        context = {
            "project_name": self.name,
            "project_description": self.description,
            "project_type": self.project_type,
            "components": [],
            "requirements": [],
            "current_phase": None
        }
        
        # Find current phase
        current_phase = None
        for phase in self.phases:
            if phase.status == "in_progress":
                current_phase = phase
                break
                
        if not current_phase and self.phases:
            current_phase = self.phases[0]
            
        if current_phase:
            context["current_phase"] = {
                "name": current_phase.name,
                "description": current_phase.description
            }
            
            # Add components and requirements from the current phase
            context["components"] = current_phase.components
            context["requirements"] = current_phase.requirements
            
            # Add tasks from the current phase
            context["tasks"] = current_phase.tasks
        
        return context
    
    def get_suggested_templates(self) -> List[Dict]:
        """
        Get suggested file templates based on project and phase.
        
        Returns:
            List of suggested templates
        """
        templates = []
        
        # Find current phase
        current_phase = None
        for phase in self.phases:
            if phase.status == "in_progress":
                current_phase = phase
                break
                
        if not current_phase and self.phases:
            current_phase = self.phases[0]
            
        if current_phase:
            # Add templates based on project type and current phase
            if self.project_type == "software":
                if "Design" in current_phase.name:
                    templates.append({
                        "name": "Class Diagram",
                        "file_type": "python",
                        "description": "Define the class structure of your application",
                        "template": "class {ClassName}:\n    \"\"\"Class description.\"\"\"\n    \n    def __init__(self):\n        \"\"\"Initialize the class.\"\"\"\n        pass\n"
                    })
                    templates.append({
                        "name": "Architecture Overview",
                        "file_type": "markdown",
                        "description": "Document the system architecture",
                        "template": "# Architecture Overview\n\n## Components\n\n## Interactions\n\n## Data Flow\n"
                    })
                
                if "Implementation" in current_phase.name:
                    templates.append({
                        "name": "Module Implementation",
                        "file_type": "python",
                        "description": "Implement a module based on design",
                        "template": "\"\"\"Module description.\"\"\"\n\nclass {ModuleName}:\n    \"\"\"Class description.\"\"\"\n    \n    def __init__(self):\n        \"\"\"Initialize the class.\"\"\"\n        pass\n    \n    def process(self, data):\n        \"\"\"Process data.\"\"\"\n        return data\n"
                    })
                    
                if "Testing" in current_phase.name:
                    templates.append({
                        "name": "Unit Tests",
                        "file_type": "python",
                        "description": "Create unit tests for your code",
                        "template": "import unittest\n\nclass Test{ModuleName}(unittest.TestCase):\n    \"\"\"Test cases for {ModuleName}.\"\"\"\n    \n    def setUp(self):\n        \"\"\"Set up test environment.\"\"\"\n        pass\n    \n    def test_example(self):\n        \"\"\"Test example functionality.\"\"\"\n        self.assertEqual(1, 1)\n\nif __name__ == '__main__':\n    unittest.main()\n"
                    })
            
            elif self.project_type == "data":
                if "Data Collection" in current_phase.name:
                    templates.append({
                        "name": "Data Collector",
                        "file_type": "python",
                        "description": "Script to collect data from sources",
                        "template": "\"\"\"Data collection script.\"\"\"\n\nimport pandas as pd\n\ndef collect_data(source_url):\n    \"\"\"Collect data from source.\"\"\"\n    # Add your code here\n    return pd.DataFrame()\n\ndef save_data(data, output_path):\n    \"\"\"Save collected data.\"\"\"\n    data.to_csv(output_path, index=False)\n    print(f\"Data saved to {output_path}\")\n\nif __name__ == '__main__':\n    source_url = 'https://example.com/data'\n    output_path = 'collected_data.csv'\n    \n    data = collect_data(source_url)\n    save_data(data, output_path)\n"
                    })
                
                if "Data Cleaning" in current_phase.name:
                    templates.append({
                        "name": "Data Cleaner",
                        "file_type": "python",
                        "description": "Script to clean and preprocess data",
                        "template": "\"\"\"Data cleaning script.\"\"\"\n\nimport pandas as pd\nimport numpy as np\n\ndef load_data(file_path):\n    \"\"\"Load data from file.\"\"\"\n    return pd.read_csv(file_path)\n\ndef clean_data(df):\n    \"\"\"Clean and preprocess data.\"\"\"\n    # Remove duplicates\n    df = df.drop_duplicates()\n    \n    # Handle missing values\n    df = df.fillna(0)  # Example: fill with zeros\n    \n    # Add more cleaning steps as needed\n    \n    return df\n\ndef save_cleaned_data(df, output_path):\n    \"\"\"Save cleaned data.\"\"\"\n    df.to_csv(output_path, index=False)\n    print(f\"Cleaned data saved to {output_path}\")\n\nif __name__ == '__main__':\n    input_path = 'collected_data.csv'\n    output_path = 'cleaned_data.csv'\n    \n    df = load_data(input_path)\n    df_cleaned = clean_data(df)\n    save_cleaned_data(df_cleaned, output_path)\n"
                    })
        
        return templates


class RoadmapManager:
    """Manages storage and retrieval of project roadmaps."""
    
    def __init__(self):
        """Initialize roadmap manager."""
        self.db = get_db_instance()
        self._init_tables()
    
    def _init_tables(self) -> None:
        """Initialize database tables for roadmaps."""
        self.db.cursor.execute("""
        CREATE TABLE IF NOT EXISTS project_roadmaps (
            id VARCHAR(255) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            project_type VARCHAR(50) NOT NULL,
            data JSONB NOT NULL,
            tags TEXT[],
            user_id VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        self.db.conn.commit()
    
    def save_roadmap(self, roadmap: ProjectRoadmap, user_id: str = None) -> bool:
        """
        Save a roadmap to the database.
        
        Args:
            roadmap: ProjectRoadmap object to save
            user_id: Optional user ID to associate with the roadmap
            
        Returns:
            Success status
        """
        try:
            roadmap_dict = roadmap.to_dict()
            roadmap_id = roadmap_dict["id"]
            
            # Check if roadmap already exists
            self.db.cursor.execute(
                "SELECT id FROM project_roadmaps WHERE id = %s",
                (roadmap_id,)
            )
            exists = self.db.cursor.fetchone() is not None
            
            if exists:
                # Update existing roadmap
                self.db.cursor.execute("""
                UPDATE project_roadmaps
                SET name = %s, description = %s, project_type = %s, 
                    data = %s, tags = %s, user_id = %s, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
                """, (
                    roadmap.name, roadmap.description, roadmap.project_type,
                    json.dumps(roadmap_dict), roadmap.tags, user_id, roadmap_id
                ))
            else:
                # Insert new roadmap
                self.db.cursor.execute("""
                INSERT INTO project_roadmaps
                (id, name, description, project_type, data, tags, user_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    roadmap_id, roadmap.name, roadmap.description, roadmap.project_type,
                    json.dumps(roadmap_dict), roadmap.tags, user_id
                ))
            
            self.db.conn.commit()
            return True
            
        except Exception as e:
            print(f"Error saving roadmap: {str(e)}")
            return False
    
    def get_roadmap(self, roadmap_id: str) -> Optional[ProjectRoadmap]:
        """
        Get a roadmap by ID.
        
        Args:
            roadmap_id: ID of the roadmap to retrieve
            
        Returns:
            ProjectRoadmap object or None if not found
        """
        try:
            self.db.cursor.execute(
                "SELECT data FROM project_roadmaps WHERE id = %s",
                (roadmap_id,)
            )
            result = self.db.cursor.fetchone()
            
            if result and result[0]:
                # Convert to string if we received a dict (for compatibility)
                roadmap_data = result[0]
                if isinstance(roadmap_data, dict):
                    roadmap_dict = roadmap_data
                else:
                    roadmap_dict = json.loads(roadmap_data)
                return ProjectRoadmap.from_dict(roadmap_dict)
            
            return None
            
        except Exception as e:
            print(f"Error getting roadmap: {str(e)}")
            return None
    
    def list_roadmaps(self, user_id: str = None, tag: str = None, 
                     limit: int = 20) -> List[Dict]:
        """
        List roadmaps with optional filtering.
        
        Args:
            user_id: Filter by user ID
            tag: Filter by tag
            limit: Maximum number of results
            
        Returns:
            List of roadmap summaries
        """
        try:
            query = """
            SELECT id, name, description, project_type, tags, created_at, updated_at
            FROM project_roadmaps
            WHERE 1=1
            """
            params = []
            
            if user_id:
                query += " AND user_id = %s"
                params.append(user_id)
            
            if tag:
                query += " AND %s = ANY(tags)"
                params.append(tag)
            
            query += " ORDER BY updated_at DESC LIMIT %s"
            params.append(limit)
            
            self.db.cursor.execute(query, params)
            results = self.db.cursor.fetchall()
            
            roadmaps = []
            for row in results:
                roadmaps.append({
                    "id": row[0],
                    "name": row[1],
                    "description": row[2],
                    "project_type": row[3],
                    "tags": row[4],
                    "created_at": row[5],
                    "updated_at": row[6]
                })
            
            return roadmaps
            
        except Exception as e:
            print(f"Error listing roadmaps: {str(e)}")
            return []
    
    def delete_roadmap(self, roadmap_id: str) -> bool:
        """
        Delete a roadmap.
        
        Args:
            roadmap_id: ID of the roadmap to delete
            
        Returns:
            Success status
        """
        try:
            self.db.cursor.execute(
                "DELETE FROM project_roadmaps WHERE id = %s",
                (roadmap_id,)
            )
            self.db.conn.commit()
            return self.db.cursor.rowcount > 0
            
        except Exception as e:
            print(f"Error deleting roadmap: {str(e)}")
            return False


# Singleton instance
_roadmap_manager = None

def get_roadmap_manager() -> RoadmapManager:
    """
    Get a singleton instance of the roadmap manager.
    
    Returns:
        RoadmapManager: Roadmap manager instance
    """
    global _roadmap_manager
    if _roadmap_manager is None:
        _roadmap_manager = RoadmapManager()
    return _roadmap_manager


# Example usage
if __name__ == "__main__":
    # Create a sample project roadmap
    roadmap = ProjectRoadmap(
        name="Sample Web Application",
        description="A sample web application to demonstrate roadmap functionality",
        project_type="software"
    )
    
    # Access the first phase (Requirements)
    if roadmap.phases:
        req_phase = roadmap.phases[0]
        
        # Add requirements
        req_phase.add_requirement(
            title="User Authentication",
            description="Users should be able to register, log in, and log out",
            requirement_type="functional",
            priority="high"
        )
        
        req_phase.add_requirement(
            title="Responsive Design",
            description="The application should work well on mobile devices",
            requirement_type="non_functional",
            priority="medium"
        )
        
        # Mark phase as in progress
        req_phase.update_status("in_progress")
    
    # Access the design phase
    if len(roadmap.phases) > 1:
        design_phase = roadmap.phases[1]
        
        # Add components
        design_phase.add_component(
            name="UserAuthentication",
            purpose="Manage user authentication and session handling",
            implementation_details="Use a combination of server-side sessions and JWT tokens"
        )
        
        design_phase.add_component(
            name="DatabaseService",
            purpose="Handle all database operations",
            implementation_details="Use PostgreSQL with SQLAlchemy ORM"
        )
    
    # Save roadmap
    manager = get_roadmap_manager()
    success = manager.save_roadmap(roadmap)
    
    if success:
        print(f"Saved roadmap with ID: {roadmap.id}")
        
        # Retrieve roadmap
        retrieved = manager.get_roadmap(roadmap.id)
        if retrieved:
            print(f"Retrieved roadmap: {retrieved.name}")
            print(f"Found {len(retrieved.phases)} phases")
        
        # List roadmaps
        roadmaps = manager.list_roadmaps()
        print(f"Found {len(roadmaps)} roadmaps")
    else:
        print("Failed to save roadmap")