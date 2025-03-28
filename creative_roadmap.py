#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyWrite Creative Roadmap Extension

This module extends the roadmap planning system for creative writing:
- Story outlining and structure for fiction writing
- Screenplay development and formatting
- Character development tracking
- Scene planning and organization
- Integrated with autocomplete for creative suggestions

Author: PyWrite
Date: 2025-03-28
"""

import os
import json
import uuid
import datetime
from typing import Dict, List, Optional, Union, Any
from project_roadmap import ProjectRoadmap, RoadmapPhase, get_roadmap_manager

# Story structure templates
STORY_TEMPLATES = {
    "three_act": [
        ("1. Setup", "Introduce protagonist, setting, and the status quo"),
        ("2. Confrontation", "Present obstacles, raise stakes, and develop conflicts"),
        ("3. Resolution", "Resolve the central conflict and establish new status quo")
    ],
    "hero_journey": [
        ("1. Ordinary World", "Establish protagonist's normal life before adventure"),
        ("2. Call to Adventure", "Present the catalyst that begins the journey"),
        ("3. Refusal of the Call", "Show initial reluctance or doubt"),
        ("4. Meeting the Mentor", "Introduce a guide figure who provides advice/tools"),
        ("5. Crossing the Threshold", "Enter the special world of the adventure"),
        ("6. Tests, Allies, Enemies", "Navigate challenges and form relationships"),
        ("7. Approach to Inmost Cave", "Prepare for major challenge/ordeal"),
        ("8. Ordeal", "Face the central crisis or challenge"),
        ("9. Reward", "Achieve the goal, but with complications"),
        ("10. The Road Back", "Begin the return journey"),
        ("11. Resurrection", "Face final test, applying what was learned"),
        ("12. Return with Elixir", "Return transformed with something to benefit others")
    ],
    "five_act": [
        ("1. Exposition", "Introduce characters, setting, and initial situation"),
        ("2. Rising Action", "Develop conflicts and tension"),
        ("3. Climax", "Reach turning point of major conflict"),
        ("4. Falling Action", "Show consequences of climax"),
        ("5. Resolution", "Present final outcome and new equilibrium")
    ],
    "save_the_cat": [
        ("1. Opening Image", "Establish tone and initial situation"),
        ("2. Theme Stated", "Hint at the thematic premise"),
        ("3. Setup", "Establish protagonist's world and flaws"),
        ("4. Catalyst", "Present the inciting incident"),
        ("5. Debate", "Show protagonist's resistance to change"),
        ("6. Break into Two", "Enter the new situation/adventure"),
        ("7. B Story", "Introduce secondary plot, often a relationship"),
        ("8. Fun and Games", "Explore the premise and promise of the concept"),
        ("9. Midpoint", "Raise stakes and shift the goal"),
        ("10. Bad Guys Close In", "Antagonists regroup and apply pressure"),
        ("11. All Is Lost", "Reach lowest point with seeming defeat"),
        ("12. Dark Night of the Soul", "Moment of reflection before breakthrough"),
        ("13. Break into Three", "Find the solution and begin final push"),
        ("14. Finale", "Execute the plan and resolve the story"),
        ("15. Final Image", "Show the transformed world")
    ]
}

# Screenplay structure templates
SCREENPLAY_TEMPLATES = {
    "feature_film": [
        ("1. Act One", "Setup - First 30 pages/minutes"),
        ("2. Act Two Part 1", "Confrontation - Pages 30-60"),
        ("3. Act Two Part 2", "Complications - Pages 60-90"),
        ("4. Act Three", "Resolution - Final 30 pages")
    ],
    "tv_pilot": [
        ("1. Teaser", "Hook audience before opening credits"),
        ("2. Act One", "Establish world and central conflict"),
        ("3. Act Two", "Develop the problem and raise stakes"),
        ("4. Act Three", "Reach crisis point"),
        ("5. Act Four", "Resolve immediate problem, set up series")
    ],
    "sitcom": [
        ("1. Teaser/Cold Open", "Quick comedic scene before credits"),
        ("2. Act One", "Establish the episode's problem"),
        ("3. Act Two", "Complicate the problem"),
        ("4. Act Three", "Resolve the problem and deliver moral/wrap-up")
    ]
}

class CreativeRoadmap(ProjectRoadmap):
    """Extends ProjectRoadmap for creative writing projects."""
    
    def __init__(self, 
                name: str, 
                description: str = "", 
                project_type: str = "fiction"):
        """
        Initialize a creative roadmap.
        
        Args:
            name: Project name (book title, screenplay title)
            description: Project description (high concept, logline)
            project_type: Type of project (fiction, screenplay)
        """
        super().__init__(name, description, project_type)
        
        # Creative project specific attributes
        self.characters = []
        self.locations = []
        self.themes = []
        self.narrative_style = ""
        self.target_audience = ""
        self.word_count_goal = 0 if project_type == "fiction" else None
        self.page_count_goal = 120 if project_type == "screenplay" else None
        
        # Override default phases with creative-specific phases
        self.phases.clear()
        self._create_creative_default_phases()
    
    def _create_creative_default_phases(self) -> None:
        """Create default phases based on creative project type."""
        if self.project_type == "fiction":
            # Default to three-act structure for fiction
            phases = STORY_TEMPLATES["three_act"]
            
            for i, (name, desc) in enumerate(phases):
                self.add_phase(name, desc, "planned", i)
            
            # Add common fiction development phases
            additional_phases = [
                ("Character Development", "Create detailed character profiles and arcs"),
                ("Setting Development", "Design key locations and world-building"),
                ("Outline & Plotting", "Create detailed chapter-by-chapter outline"),
                ("First Draft", "Write the complete first draft"),
                ("Revision", "Edit and improve the manuscript")
            ]
            
            for i, (name, desc) in enumerate(additional_phases, start=len(phases)):
                self.add_phase(name, desc, "planned", i)
                
        elif self.project_type == "screenplay":
            # Default to feature film structure for screenplays
            phases = SCREENPLAY_TEMPLATES["feature_film"]
            
            for i, (name, desc) in enumerate(phases):
                self.add_phase(name, desc, "planned", i)
            
            # Add common screenplay development phases
            additional_phases = [
                ("Characters & Dialogue", "Develop distinctive voices and dialogue styles"),
                ("Scene Breakdown", "Create detailed scene-by-scene outline"),
                ("Treatment", "Write a prose version of the story"),
                ("First Draft", "Write the complete first draft screenplay"),
                ("Revision", "Polish and refine the screenplay")
            ]
            
            for i, (name, desc) in enumerate(additional_phases, start=len(phases)):
                self.add_phase(name, desc, "planned", i)
    
    def change_story_structure(self, structure_template: str) -> bool:
        """
        Change the story structure template.
        
        Args:
            structure_template: Name of template (three_act, hero_journey, etc.)
            
        Returns:
            Success status
        """
        # Store creative-specific phases
        creative_phases = [phase for phase in self.phases 
                          if phase.name not in [p[0] for p in STORY_TEMPLATES.get(structure_template, [])]]
        
        # Clear existing structure phases
        self.phases = creative_phases
        
        # Get the new template
        if self.project_type == "fiction":
            template = STORY_TEMPLATES.get(structure_template)
        else:  # screenplay
            template = SCREENPLAY_TEMPLATES.get(structure_template)
        
        if not template:
            return False
        
        # Add new structure phases
        for i, (name, desc) in enumerate(template):
            self.add_phase(name, desc, "planned", i)
        
        # Reorder phases to put structure first
        structure_phases = [phase for phase in self.phases 
                           if phase.name in [p[0] for p in template]]
        other_phases = [phase for phase in self.phases 
                       if phase.name not in [p[0] for p in template]]
        
        self.phases = structure_phases + other_phases
        
        # Update order values
        for i, phase in enumerate(self.phases):
            phase.order = i
        
        return True
    
    def add_character(self, name: str, role: str = "supporting", 
                    description: str = "", motivation: str = "",
                    arc: str = "") -> str:
        """
        Add a character to the roadmap.
        
        Args:
            name: Character name
            role: Character role (protagonist, antagonist, supporting)
            description: Character description
            motivation: Character motivation/goal
            arc: Character arc/development
            
        Returns:
            Character ID
        """
        character_id = str(uuid.uuid4())
        character = {
            "id": character_id,
            "name": name,
            "role": role,
            "description": description,
            "motivation": motivation,
            "arc": arc,
            "traits": [],
            "relationships": [],
            "created_at": datetime.datetime.now().isoformat()
        }
        self.characters.append(character)
        self.updated_at = datetime.datetime.now().isoformat()
        return character_id
    
    def add_location(self, name: str, description: str = "") -> str:
        """
        Add a location to the roadmap.
        
        Args:
            name: Location name
            description: Location description
            
        Returns:
            Location ID
        """
        location_id = str(uuid.uuid4())
        location = {
            "id": location_id,
            "name": name,
            "description": description,
            "created_at": datetime.datetime.now().isoformat()
        }
        self.locations.append(location)
        self.updated_at = datetime.datetime.now().isoformat()
        return location_id
    
    def add_theme(self, name: str, description: str = "") -> str:
        """
        Add a theme to the roadmap.
        
        Args:
            name: Theme name
            description: Theme description
            
        Returns:
            Theme ID
        """
        theme_id = str(uuid.uuid4())
        theme = {
            "id": theme_id,
            "name": name,
            "description": description,
            "created_at": datetime.datetime.now().isoformat()
        }
        self.themes.append(theme)
        self.updated_at = datetime.datetime.now().isoformat()
        return theme_id
    
    def add_scene(self, phase_id: str, title: str, description: str = "",
                characters: Optional[List[str]] = None, location: str = "",
                goal: str = "") -> Optional[str]:
        """
        Add a scene to a phase.
        
        Args:
            phase_id: ID of the phase
            title: Scene title
            description: Scene description
            characters: List of character names in the scene
            location: Location name
            goal: Purpose of the scene
            
        Returns:
            Scene ID or None if phase not found
        """
        phase = self.get_phase(phase_id)
        if not phase:
            return None
        
        if characters is None:
            characters = []
            
        scene_id = str(uuid.uuid4())
        scene = {
            "id": scene_id,
            "title": title,
            "description": description,
            "characters": characters,
            "location": location,
            "goal": goal,
            "created_at": datetime.datetime.now().isoformat()
        }
        
        # Add to phase's tasks
        task_id = phase.add_task(
            title=f"Scene: {title}",
            description=description,
            priority="medium"
        )
        
        # Store the scene data in the task's metadata
        for task in phase.tasks:
            if task["id"] == task_id:
                task["scene_data"] = scene
                break
        
        self.updated_at = datetime.datetime.now().isoformat()
        return scene_id
    
    def to_dict(self) -> Dict:
        """Convert roadmap to dictionary."""
        base_dict = super().to_dict()
        
        # Add creative-specific attributes
        base_dict.update({
            "characters": self.characters,
            "locations": self.locations,
            "themes": self.themes,
            "narrative_style": self.narrative_style,
            "target_audience": self.target_audience,
            "word_count_goal": self.word_count_goal,
            "page_count_goal": self.page_count_goal
        })
        
        return base_dict
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'CreativeRoadmap':
        """Create roadmap from dictionary."""
        roadmap = cls(
            name=data.get("name", "Unnamed Project"),
            description=data.get("description", ""),
            project_type=data.get("project_type", "fiction")
        )
        roadmap.id = data.get("id", roadmap.id)
        roadmap.tags = data.get("tags", [])
        roadmap.created_at = data.get("created_at", roadmap.created_at)
        roadmap.updated_at = data.get("updated_at", roadmap.updated_at)
        
        # Clear default phases and load saved phases
        roadmap.phases.clear()
        for phase_data in data.get("phases", []):
            roadmap.phases.append(RoadmapPhase.from_dict(phase_data))
        
        # Load creative-specific attributes
        roadmap.characters = data.get("characters", [])
        roadmap.locations = data.get("locations", [])
        roadmap.themes = data.get("themes", [])
        roadmap.narrative_style = data.get("narrative_style", "")
        roadmap.target_audience = data.get("target_audience", "")
        roadmap.word_count_goal = data.get("word_count_goal", 0 if roadmap.project_type == "fiction" else None)
        roadmap.page_count_goal = data.get("page_count_goal", 120 if roadmap.project_type == "screenplay" else None)
        
        return roadmap
    
    def generate_writing_context(self) -> Dict:
        """
        Generate a context dictionary for creative writing.
        
        Returns:
            Dictionary with creative context information
        """
        context = super().generate_code_context()
        
        # Add creative-specific context
        context.update({
            "characters": self.characters,
            "locations": self.locations,
            "themes": self.themes,
            "narrative_style": self.narrative_style,
            "target_audience": self.target_audience
        })
        
        # Find current phase
        current_phase = None
        for phase in self.phases:
            if phase.status == "in_progress":
                current_phase = phase
                break
                
        if not current_phase and self.phases:
            current_phase = self.phases[0]
            
        if current_phase:
            # Extract scenes from tasks
            scenes = []
            for task in current_phase.tasks:
                if "scene_data" in task:
                    scenes.append(task["scene_data"])
                    
            context["scenes"] = scenes
        
        return context
    
    def get_suggested_templates(self) -> List[Dict]:
        """
        Get suggested writing templates based on project type and phase.
        
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
            if self.project_type == "fiction":
                # Fiction templates based on current phase
                if "Character" in current_phase.name:
                    templates.append({
                        "name": "Character Profile",
                        "file_type": "markdown",
                        "description": "Create a detailed character profile",
                        "template": "# Character Profile: {CharacterName}\n\n## Basic Information\n- **Full Name:** \n- **Age:** \n- **Occupation:** \n- **Physical Description:** \n\n## Background\n\n## Personality\n\n## Goals and Motivations\n\n## Conflicts\n\n## Character Arc\n\n## Relationships\n\n## Notes\n"
                    })
                
                if "Setting" in current_phase.name:
                    templates.append({
                        "name": "Location Description",
                        "file_type": "markdown",
                        "description": "Create a detailed location description",
                        "template": "# Location: {LocationName}\n\n## Description\n\n## History\n\n## Significance to Story\n\n## Sensory Details\n- **Sights:** \n- **Sounds:** \n- **Smells:** \n- **Textures:** \n\n## Notes\n"
                    })
                
                if "Outline" in current_phase.name:
                    templates.append({
                        "name": "Chapter Outline",
                        "file_type": "markdown",
                        "description": "Create a chapter outline",
                        "template": "# Chapter {ChapterNumber}: {ChapterTitle}\n\n## Summary\n\n## Scenes\n1. \n2. \n3. \n\n## Characters Present\n- \n\n## Locations\n- \n\n## Key Plot Points\n- \n\n## Notes\n"
                    })
                    
                if "Draft" in current_phase.name:
                    templates.append({
                        "name": "Scene Template",
                        "file_type": "markdown",
                        "description": "Template for writing a scene",
                        "template": "# Scene: {SceneTitle}\n\n## Setting\n- **Location:** \n- **Time:** \n- **Weather/Atmosphere:** \n\n## Characters Present\n- \n\n## Scene Goal\n\n## Conflict\n\n## Outcome\n\n## Notes\n\n---\n\n[SCENE TEXT BEGINS HERE]\n\n"
                    })
            
            elif self.project_type == "screenplay":
                # Screenplay templates
                if "Characters" in current_phase.name:
                    templates.append({
                        "name": "Character Profile",
                        "file_type": "markdown",
                        "description": "Create a detailed character profile for screenplay",
                        "template": "# Character: {CharacterName}\n\n## Basic Information\n- **Age:** \n- **Occupation:** \n- **Archetype:** \n\n## Character Description\n\n## Background\n\n## Personality\n\n## Goals/Wants\n\n## Needs\n\n## Dialogue Style\n\n## Character Arc\n\n## Relationships\n\n## Casting Notes\n"
                    })
                
                if "Scene" in current_phase.name:
                    templates.append({
                        "name": "Scene Breakdown",
                        "file_type": "markdown",
                        "description": "Create a detailed scene breakdown",
                        "template": "# Scene {SceneNumber}: {SceneTitle}\n\n## Slugline\n\n## Characters\n\n## Purpose\n\n## Action/Description\n\n## Dialogue Highlights\n\n## Emotional Shifts\n\n## Subtext\n\n## Visual Notes\n"
                    })
                    
                if "Treatment" in current_phase.name or "First Draft" in current_phase.name:
                    templates.append({
                        "name": "Screenplay Page",
                        "file_type": "fountain",
                        "description": "Create a screenplay page in Fountain format",
                        "template": "INT. {LOCATION} - {TIME}\n\n{Action description.}\n\n{CHARACTER NAME}\n{Dialogue}\n\n{Action description.}\n\n{CHARACTER NAME}\n{Dialogue}\n"
                    })
        
        return templates
    
    def get_character_by_name(self, name: str) -> Optional[Dict]:
        """
        Get a character by name.
        
        Args:
            name: Character name
            
        Returns:
            Character dict or None if not found
        """
        for character in self.characters:
            if character["name"].lower() == name.lower():
                return character
        return None
    
    def get_location_by_name(self, name: str) -> Optional[Dict]:
        """
        Get a location by name.
        
        Args:
            name: Location name
            
        Returns:
            Location dict or None if not found
        """
        for location in self.locations:
            if location["name"].lower() == name.lower():
                return location
        return None
    
    def get_scenes_for_character(self, character_name: str) -> List[Dict]:
        """
        Get all scenes featuring a particular character.
        
        Args:
            character_name: Name of the character
            
        Returns:
            List of scenes
        """
        scenes = []
        
        for phase in self.phases:
            for task in phase.tasks:
                if "scene_data" in task and character_name in task["scene_data"].get("characters", []):
                    scenes.append(task["scene_data"])
        
        return scenes
    
    def generate_story_elements(self, element_type: str, prompt: Optional[str] = None) -> List[Dict]:
        """
        Generate story elements using AI if available.
        
        Args:
            element_type: Type of element to generate (character, location, plot_point)
            prompt: Optional prompt to guide generation
            
        Returns:
            List of generated elements
        """
        # This is a placeholder - in the real implementation, this would use
        # the OpenAI API (similar to how code generation works in RoadmapAutocompleteBridge)
        
        if element_type == "character":
            return [
                {
                    "name": "Example Character",
                    "role": "supporting",
                    "description": "This is an example character. To generate real characters, set OPENAI_API_KEY.",
                    "motivation": "Has goals and desires",
                    "arc": "Changes throughout the story"
                }
            ]
        elif element_type == "location":
            return [
                {
                    "name": "Example Location",
                    "description": "This is an example location. To generate real locations, set OPENAI_API_KEY."
                }
            ]
        elif element_type == "plot_point":
            return [
                {
                    "title": "Example Plot Point",
                    "description": "This is an example plot point. To generate real plot points, set OPENAI_API_KEY."
                }
            ]
            
        return []


class CreativeRoadmapManager:
    """Manages creation and storage of creative roadmaps."""
    
    def __init__(self):
        """Initialize creative roadmap manager."""
        self.roadmap_manager = get_roadmap_manager()
    
    def create_roadmap(self, name: str, description: str, project_type: str,
                      structure_template: Optional[str] = None) -> CreativeRoadmap:
        """
        Create a new creative roadmap.
        
        Args:
            name: Project name
            description: Project description
            project_type: Project type (fiction, screenplay)
            structure_template: Optional structure template
            
        Returns:
            CreativeRoadmap object
        """
        roadmap = CreativeRoadmap(
            name=name,
            description=description,
            project_type=project_type
        )
        
        # Apply structure template if provided
        if structure_template:
            roadmap.change_story_structure(structure_template)
        
        return roadmap
    
    def save_roadmap(self, roadmap: CreativeRoadmap, user_id: Optional[str] = None) -> bool:
        """
        Save a creative roadmap.
        
        Args:
            roadmap: CreativeRoadmap to save
            user_id: Optional user ID
            
        Returns:
            Success status
        """
        return self.roadmap_manager.save_roadmap(roadmap, user_id)
    
    def get_roadmap(self, roadmap_id: str) -> Optional[CreativeRoadmap]:
        """
        Get a creative roadmap by ID.
        
        Args:
            roadmap_id: ID of the roadmap
            
        Returns:
            CreativeRoadmap or None if not found
        """
        roadmap = self.roadmap_manager.get_roadmap(roadmap_id)
        
        if roadmap and (roadmap.project_type == "fiction" or roadmap.project_type == "screenplay"):
            # Convert to CreativeRoadmap
            data = roadmap.to_dict()
            return CreativeRoadmap.from_dict(data)
        
        return None
    
    def list_roadmaps(self, project_type: Optional[str] = None, user_id: Optional[str] = None) -> List[Dict]:
        """
        List creative roadmaps.
        
        Args:
            project_type: Optional project type filter (fiction, screenplay)
            user_id: Optional user ID filter
            
        Returns:
            List of roadmap summaries
        """
        roadmaps = self.roadmap_manager.list_roadmaps(user_id=user_id)
        
        if project_type:
            roadmaps = [r for r in roadmaps if r["project_type"] == project_type]
        else:
            roadmaps = [r for r in roadmaps if r["project_type"] in ["fiction", "screenplay"]]
            
        return roadmaps


# Create singleton instance
_creative_roadmap_manager = None

def get_creative_roadmap_manager() -> CreativeRoadmapManager:
    """
    Get singleton instance of the creative roadmap manager.
    
    Returns:
        CreativeRoadmapManager instance
    """
    global _creative_roadmap_manager
    if _creative_roadmap_manager is None:
        _creative_roadmap_manager = CreativeRoadmapManager()
    return _creative_roadmap_manager


# Example usage
if __name__ == "__main__":
    # Create a sample fiction roadmap
    manager = get_creative_roadmap_manager()
    
    # Create a fiction project with three-act structure
    fiction_roadmap = manager.create_roadmap(
        name="The Hidden Oracle",
        description="A fantasy novel about a librarian who discovers ancient magic",
        project_type="fiction"
    )
    
    # Add characters
    protagonist_id = fiction_roadmap.add_character(
        name="Eleanor Blackwood",
        role="protagonist",
        description="32-year-old librarian with a passion for ancient texts",
        motivation="Discover the truth about her family's connection to magic",
        arc="From skeptic to confident magic practitioner"
    )
    
    antagonist_id = fiction_roadmap.add_character(
        name="Professor Malcolm Thorne",
        role="antagonist",
        description="Charismatic history professor with secret agenda",
        motivation="Obtain the Oracle's power for himself",
        arc="From respected mentor to revealed villain"
    )
    
    # Add locations
    fiction_roadmap.add_location(
        name="Blackwood Library",
        description="Ancient library with hidden chambers and secret collections"
    )
    
    fiction_roadmap.add_location(
        name="The Oracle's Chamber",
        description="Hidden underground chamber containing the ancient Oracle artifact"
    )
    
    # Add themes
    fiction_roadmap.add_theme(
        name="Knowledge as Power",
        description="The pursuit and responsibility of forbidden knowledge"
    )
    
    fiction_roadmap.add_theme(
        name="Legacy and Identity",
        description="Discovering one's true heritage and purpose"
    )
    
    # Add scenes to the first phase
    if fiction_roadmap.phases:
        phase_id = fiction_roadmap.phases[0].id
        
        fiction_roadmap.add_scene(
            phase_id=phase_id,
            title="Opening: Eleanor discovers ancient text",
            description="Eleanor finds a mysterious book with her family's symbol",
            characters=["Eleanor Blackwood"],
            location="Blackwood Library",
            goal="Establish protagonist and mystery"
        )
        
        fiction_roadmap.add_scene(
            phase_id=phase_id,
            title="Professor Thorne offers help",
            description="Thorne recognizes the symbol and offers his expertise",
            characters=["Eleanor Blackwood", "Professor Malcolm Thorne"],
            location="University Office",
            goal="Introduce mentor/antagonist and deepen mystery"
        )
    
    # Save the roadmap
    success = manager.save_roadmap(fiction_roadmap)
    
    if success:
        print(f"Created and saved fiction roadmap: {fiction_roadmap.name}")
        
        # Create a screenplay project
        screenplay_roadmap = manager.create_roadmap(
            name="The Lost Expedition",
            description="A team of scientists discover an ancient civilization in the Amazon",
            project_type="screenplay",
            structure_template="feature_film"
        )
        
        # Add characters
        protagonist_id = screenplay_roadmap.add_character(
            name="Dr. Maya Chen",
            role="protagonist",
            description="Brilliant archaeologist haunted by a failed expedition",
            motivation="Prove her theories and redeem her reputation",
            arc="From cautious academic to bold explorer embracing the unknown"
        )
        
        # Save the screenplay roadmap
        success = manager.save_roadmap(screenplay_roadmap)
        
        if success:
            print(f"Created and saved screenplay roadmap: {screenplay_roadmap.name}")
            
            # List creative roadmaps
            roadmaps = manager.list_roadmaps()
            print(f"Found {len(roadmaps)} creative roadmaps")
        else:
            print("Failed to save screenplay roadmap")
    else:
        print("Failed to save fiction roadmap")