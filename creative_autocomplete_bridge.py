#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyWrite Creative Autocomplete Bridge

This module integrates creative roadmaps with autocomplete:
- Character-based suggestions for dialogue and actions
- Setting-based descriptions
- Plot structure suggestions
- Theme integration
- Writing style consistency

Author: PyWrite
Date: 2025-03-28
"""

import os
import re
import json
import logging
from typing import Dict, List, Tuple, Any, Optional, Union, Set

# Import PyWrite modules
from creative_roadmap import CreativeRoadmap, get_creative_roadmap_manager
from roadmap_autocomplete_bridge import RoadmapAutocompleteBridge
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
        logging.FileHandler('creative_bridge.log')
    ]
)

logger = logging.getLogger('PyWrite.CreativeBridge')


class CreativeAutocompleteBridge(RoadmapAutocompleteBridge):
    """Integrates creative roadmaps with writing-focused autocomplete."""
    
    def __init__(self, roadmap_id: Optional[str] = None):
        """
        Initialize the creative bridge.
        
        Args:
            roadmap_id: Optional ID of a specific roadmap to use
        """
        super().__init__(roadmap_id)
        
        # Track completions specific to creative writing
        self.character_completions = {}
        self.dialogue_completions = {}
        self.setting_completions = {}
        self.theme_completions = {}
        
        # Extract patterns from roadmap if available
        if self.roadmap and hasattr(self.roadmap, 'characters'):
            self._extract_creative_patterns()
    
    def set_roadmap(self, roadmap_id: str) -> bool:
        """
        Set the current roadmap, using creative manager if appropriate.
        
        Args:
            roadmap_id: ID of the roadmap to use
            
        Returns:
            Success status
        """
        # First try to load as creative roadmap
        creative_manager = get_creative_roadmap_manager()
        roadmap = creative_manager.get_roadmap(roadmap_id)
        
        if roadmap:
            self.roadmap = roadmap
            self.roadmap_id = roadmap_id
            self._extract_creative_patterns()
            return True
        
        # Fall back to standard roadmap
        return super().set_roadmap(roadmap_id)
    
    def _extract_creative_patterns(self) -> None:
        """Extract writing patterns from the creative roadmap."""
        if not hasattr(self.roadmap, 'characters'):
            logger.warning("Not a creative roadmap, skipping creative pattern extraction")
            return
        
        creative_roadmap = self.roadmap
        logger.info(f"Extracting creative patterns from roadmap: {creative_roadmap.name}")
        
        # Extract character patterns
        self._extract_character_patterns(creative_roadmap)
        
        # Extract setting patterns
        self._extract_setting_patterns(creative_roadmap)
        
        # Extract theme patterns
        self._extract_theme_patterns(creative_roadmap)
        
        # Extract narrative style patterns
        self._extract_narrative_patterns(creative_roadmap)
        
        # Convert patterns to completions
        self._convert_to_creative_completions()
    
    def _extract_character_patterns(self, roadmap: CreativeRoadmap) -> None:
        """
        Extract character patterns from the roadmap.
        
        Args:
            roadmap: CreativeRoadmap to extract from
        """
        characters = {}
        
        for character in roadmap.characters:
            name = character.get('name', '')
            if not name:
                continue
                
            # Store character data
            characters[name] = {
                "description": character.get('description', ''),
                "role": character.get('role', 'supporting'),
                "motivation": character.get('motivation', ''),
                "arc": character.get('arc', ''),
                "traits": character.get('traits', []),
                "dialogue_style": self._infer_dialogue_style(character)
            }
            
            # Find scenes with this character
            scenes = roadmap.get_scenes_for_character(name)
            if scenes:
                characters[name]["scenes"] = scenes
        
        # Store the results
        self.character_completions = characters
    
    def _infer_dialogue_style(self, character: Dict) -> str:
        """
        Infer a character's dialogue style from their traits and description.
        
        Args:
            character: Character dictionary
            
        Returns:
            Dialogue style description
        """
        # This is a simple implementation - a real version would use more sophisticated analysis
        description = character.get('description', '').lower()
        
        if "professor" in description or "academic" in description or "scholar" in description:
            return "Formal, precise, and academic with occasional literary references"
        elif "shy" in description or "quiet" in description or "reserved" in description:
            return "Brief, hesitant, with frequent pauses and qualifiers"
        elif "confident" in description or "bold" in description or "charismatic" in description:
            return "Bold, direct statements with commanding tone"
        elif "villain" in description or "antagonist" in character.get('role', ''):
            return "Sharp, cutting remarks with subtle threats beneath the surface"
        
        # Default style based on role
        if character.get('role') == "protagonist":
            return "Clear, thoughtful speech that reveals inner character development"
        elif character.get('role') == "supporting":
            return "Practical dialogue that serves to move the plot forward"
        
        return "Natural, conversational dialogue appropriate to the character's background"
    
    def _extract_setting_patterns(self, roadmap: CreativeRoadmap) -> None:
        """
        Extract setting patterns from the roadmap.
        
        Args:
            roadmap: CreativeRoadmap to extract from
        """
        settings = {}
        
        for location in roadmap.locations:
            name = location.get('name', '')
            if not name:
                continue
                
            # Store location data
            settings[name] = {
                "description": location.get('description', ''),
                "sensory_details": self._extract_sensory_details(location.get('description', ''))
            }
        
        # Store the results
        self.setting_completions = settings
    
    def _extract_sensory_details(self, description: str) -> Dict[str, List[str]]:
        """
        Extract sensory details from a location description.
        
        Args:
            description: Location description
            
        Returns:
            Dictionary of sensory details
        """
        # This is a simple implementation - a real version would use NLP
        details = {
            "visual": [],
            "auditory": [],
            "olfactory": [],
            "tactile": [],
            "taste": []
        }
        
        # Simple pattern matching for sensory words
        visual_patterns = ["saw", "looked", "appeared", "bright", "dark", "color", "shape"]
        for pattern in visual_patterns:
            if pattern in description.lower():
                context = self._extract_context(description, pattern)
                if context:
                    details["visual"].append(context)
        
        auditory_patterns = ["heard", "sound", "noise", "quiet", "loud", "silence", "voice"]
        for pattern in auditory_patterns:
            if pattern in description.lower():
                context = self._extract_context(description, pattern)
                if context:
                    details["auditory"].append(context)
        
        olfactory_patterns = ["smell", "scent", "aroma", "odor", "fragrance", "stench"]
        for pattern in olfactory_patterns:
            if pattern in description.lower():
                context = self._extract_context(description, pattern)
                if context:
                    details["olfactory"].append(context)
        
        tactile_patterns = ["touch", "feel", "texture", "rough", "smooth", "hard", "soft"]
        for pattern in tactile_patterns:
            if pattern in description.lower():
                context = self._extract_context(description, pattern)
                if context:
                    details["tactile"].append(context)
        
        taste_patterns = ["taste", "flavor", "sweet", "bitter", "sour", "salty"]
        for pattern in taste_patterns:
            if pattern in description.lower():
                context = self._extract_context(description, pattern)
                if context:
                    details["taste"].append(context)
        
        return details
    
    def _extract_context(self, text: str, keyword: str, window: int = 10) -> str:
        """
        Extract context around a keyword in text.
        
        Args:
            text: Text to search
            keyword: Keyword to find
            window: Number of words for context window
            
        Returns:
            Context snippet or empty string if not found
        """
        words = text.split()
        for i, word in enumerate(words):
            if keyword.lower() in word.lower():
                start = max(0, i - window)
                end = min(len(words), i + window + 1)
                return " ".join(words[start:end])
        return ""
    
    def _extract_theme_patterns(self, roadmap: CreativeRoadmap) -> None:
        """
        Extract theme patterns from the roadmap.
        
        Args:
            roadmap: CreativeRoadmap to extract from
        """
        themes = {}
        
        for theme in roadmap.themes:
            name = theme.get('name', '')
            if not name:
                continue
                
            # Store theme data
            themes[name] = {
                "description": theme.get('description', ''),
                "keywords": self._extract_theme_keywords(name, theme.get('description', ''))
            }
        
        # Store the results
        self.theme_completions = themes
    
    def _extract_theme_keywords(self, theme_name: str, description: str) -> List[str]:
        """
        Extract keywords for a theme.
        
        Args:
            theme_name: Theme name
            description: Theme description
            
        Returns:
            List of theme keywords
        """
        # Split the theme name and description into words
        words = re.findall(r'\w+', theme_name.lower() + ' ' + description.lower())
        
        # Filter out common words and duplicates
        stopwords = {"a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for", "with", 
                    "about", "is", "are", "was", "were", "be", "been", "being", "of"}
        keywords = [word for word in words if word not in stopwords and len(word) > 3]
        
        # Return unique keywords
        return list(set(keywords))
    
    def _extract_narrative_patterns(self, roadmap: CreativeRoadmap) -> None:
        """
        Extract narrative style patterns from the roadmap.
        
        Args:
            roadmap: CreativeRoadmap to extract from
        """
        # This would be implemented in a real version, possibly using
        # AI to analyze and generate appropriate narrative style patterns
        pass
    
    def _convert_to_creative_completions(self) -> None:
        """Convert extracted creative patterns to completion suggestions."""
        completions = {}
        
        # Character introductions
        for name, info in self.character_completions.items():
            # Character description
            desc_template = f"{name} {self._character_description_template(info)}"
            completions[f"{name} "] = {
                "text": desc_template,
                "display_text": f"{name} (character description)",
                "type": "character_description",
                "description": f"Insert description of {name}",
                "score": 90,
                "prefix_match": len(name) + 1
            }
            
            # Character dialogue
            if roadmap.project_type == "fiction":
                # Fiction dialogue format
                dialogue_template = f"\"{self._generate_dialogue_template(name, info)}\""
                completions[f"{name} said"] = {
                    "text": f"{name} said, {dialogue_template}",
                    "display_text": f"{name} said (dialogue)",
                    "type": "character_dialogue",
                    "description": f"Insert dialogue for {name}",
                    "score": 85,
                    "prefix_match": len(f"{name} said")
                }
                
                # Additional dialogue tags
                for tag in ["whispered", "shouted", "replied", "asked", "murmured", "muttered"]:
                    completions[f"{name} {tag}"] = {
                        "text": f"{name} {tag}, {dialogue_template}",
                        "display_text": f"{name} {tag} (dialogue)",
                        "type": "character_dialogue",
                        "description": f"Insert dialogue for {name}",
                        "score": 83,
                        "prefix_match": len(f"{name} {tag}")
                    }
            
            elif roadmap.project_type == "screenplay":
                # Screenplay dialogue format
                dialogue_template = self._generate_dialogue_template(name, info)
                completions[f"{name.upper()}"] = {
                    "text": f"{name.upper()}\n{dialogue_template}",
                    "display_text": f"{name.upper()} (dialogue)",
                    "type": "character_dialogue",
                    "description": f"Insert dialogue for {name}",
                    "score": 90,
                    "prefix_match": len(name.upper())
                }
                
                # Character action (parenthetical)
                completions[f"{name.upper()} ("] = {
                    "text": f"{name.upper()} (emotion)\n{dialogue_template}",
                    "display_text": f"{name.upper()} (with parenthetical)",
                    "type": "character_action",
                    "description": f"Insert action and dialogue for {name}",
                    "score": 85,
                    "prefix_match": len(f"{name.upper()} (")
                }
        
        # Setting descriptions
        for name, info in self.setting_completions.items():
            # Setting description
            desc_template = self._setting_description_template(name, info)
            completions[f"{name} "] = {
                "text": desc_template,
                "display_text": f"{name} (setting description)",
                "type": "setting_description",
                "description": f"Insert description of {name}",
                "score": 90,
                "prefix_match": len(name) + 1
            }
            
            if roadmap.project_type == "screenplay":
                # Screenplay slugline
                completions[f"INT. {name}"] = {
                    "text": f"INT. {name} - DAY\n\n",
                    "display_text": f"INT. {name} - DAY",
                    "type": "slugline",
                    "description": f"Interior scene at {name} during day",
                    "score": 95,
                    "prefix_match": len(f"INT. {name}")
                }
                
                completions[f"EXT. {name}"] = {
                    "text": f"EXT. {name} - DAY\n\n",
                    "display_text": f"EXT. {name} - DAY",
                    "type": "slugline", 
                    "description": f"Exterior scene at {name} during day",
                    "score": 95,
                    "prefix_match": len(f"EXT. {name}")
                }
        
        # Theme references
        for name, info in self.theme_completions.items():
            template = self._theme_reference_template(name, info)
            completions[f"theme of {name.lower()}"] = {
                "text": template,
                "display_text": f"Theme: {name}",
                "type": "theme_reference",
                "description": f"Insert reference to theme: {name}",
                "score": 80,
                "prefix_match": len(f"theme of {name.lower()}")
            }
        
        # Add phase-specific templates
        if hasattr(self.roadmap, 'phases'):
            for phase in self.roadmap.phases:
                if "Setup" in phase.name or "Ordinary World" in phase.name:
                    # Opening/introduction template
                    completions["OPENING SCENE"] = {
                        "text": self._opening_scene_template(),
                        "display_text": "OPENING SCENE",
                        "type": "scene_template",
                        "description": "Template for opening scene",
                        "score": 90,
                        "prefix_match": len("OPENING SCENE")
                    }
                
                elif "Climax" in phase.name or "Ordeal" in phase.name:
                    # Climax template
                    completions["CLIMAX SCENE"] = {
                        "text": self._climax_scene_template(),
                        "display_text": "CLIMAX SCENE",
                        "type": "scene_template",
                        "description": "Template for climactic scene",
                        "score": 90,
                        "prefix_match": len("CLIMAX SCENE")
                    }
                
                elif "Resolution" in phase.name or "Return" in phase.name:
                    # Resolution template
                    completions["RESOLUTION SCENE"] = {
                        "text": self._resolution_scene_template(),
                        "display_text": "RESOLUTION SCENE",
                        "type": "scene_template",
                        "description": "Template for resolution scene",
                        "score": 90,
                        "prefix_match": len("RESOLUTION SCENE")
                    }
        
        # Store the creative completions
        self.roadmap_completions.update(completions)
    
    def _character_description_template(self, character_info: Dict) -> str:
        """
        Generate a character description template.
        
        Args:
            character_info: Character information dictionary
            
        Returns:
            Description template
        """
        desc = character_info.get('description', '')
        if not desc:
            if character_info.get('role') == "protagonist":
                return "was the kind of person who commanded attention without trying."
            elif character_info.get('role') == "antagonist":
                return "carried an aura of subtle menace that made others instinctively wary."
            else:
                return "stood with an expression that revealed years of complex experiences."
        
        return f"- {desc}"
    
    def _generate_dialogue_template(self, character_name: str, character_info: Dict) -> str:
        """
        Generate a dialogue template for a character.
        
        Args:
            character_name: Character name
            character_info: Character information dictionary
            
        Returns:
            Dialogue template
        """
        style = character_info.get('dialogue_style', '')
        motivation = character_info.get('motivation', '')
        
        if "formal" in style.lower():
            return "I believe we should proceed with caution. The situation demands careful consideration."
        elif "hesitant" in style.lower():
            return "I... I'm not sure if this is the right way forward... maybe we should try something else?"
        elif "bold" in style.lower():
            return "Listen to me. This is exactly what we need to do, and we need to do it now."
        elif "sharp" in style.lower() or "threat" in style.lower():
            return "Perhaps you haven't fully understood the consequences of your actions. Allow me to clarify."
        
        # Default based on role
        if character_info.get('role') == "protagonist":
            return "We need to find out what's really happening here. I won't stop until we uncover the truth."
        elif character_info.get('role') == "antagonist":
            return "You're too late. Everything is already in motion, and there's nothing you can do to stop it."
        else:
            return "I'm not sure what to make of all this, but I know we need to stick together."
    
    def _setting_description_template(self, setting_name: str, setting_info: Dict) -> str:
        """
        Generate a setting description template.
        
        Args:
            setting_name: Setting name
            setting_info: Setting information dictionary
            
        Returns:
            Setting description template
        """
        desc = setting_info.get('description', '')
        sensory = setting_info.get('sensory_details', {})
        
        # Use the provided description if available
        if desc:
            return f"- {desc}"
        
        # Create a description from sensory details
        description_parts = []
        
        visual = sensory.get('visual', [])
        if visual:
            description_parts.append(visual[0])
        
        auditory = sensory.get('auditory', [])
        if auditory:
            description_parts.append(auditory[0])
        
        olfactory = sensory.get('olfactory', [])
        if olfactory:
            description_parts.append(olfactory[0])
        
        if description_parts:
            return " ".join(description_parts)
        
        # Default description
        if "library" in setting_name.lower():
            return "The shelves towered with ancient volumes, dust motes dancing in the slanted sunlight from tall windows."
        elif "castle" in setting_name.lower() or "palace" in setting_name.lower():
            return "Stone walls echoed with the footsteps of generations past, the air cool and heavy with history."
        elif "forest" in setting_name.lower() or "woods" in setting_name.lower():
            return "Trees creaked and whispered in the gentle breeze, dappled sunlight creating ever-shifting patterns on the leaf-strewn ground."
        elif "ocean" in setting_name.lower() or "sea" in setting_name.lower():
            return "Waves crashed against the shore in a timeless rhythm, the salty air filling the lungs with each breath."
        else:
            return "The space held an atmosphere that seemed to reflect its history, every detail telling a story to those who knew how to look."
    
    def _theme_reference_template(self, theme_name: str, theme_info: Dict) -> str:
        """
        Generate a theme reference template.
        
        Args:
            theme_name: Theme name
            theme_info: Theme information dictionary
            
        Returns:
            Theme reference template
        """
        desc = theme_info.get('description', '')
        
        if desc:
            return f"// Theme: {theme_name} - {desc}"
        
        # Generic themes
        if "identity" in theme_name.lower():
            return "// Theme: Identity - The question of who we truly are beneath our surface"
        elif "power" in theme_name.lower():
            return "// Theme: Power - The corrupting influence and responsibility of power"
        elif "love" in theme_name.lower():
            return "// Theme: Love - The transformative power of deep connection"
        elif "justice" in theme_name.lower():
            return "// Theme: Justice - The complex nature of fairness and retribution"
        else:
            return f"// Theme: {theme_name} - Central thematic element"
    
    def _opening_scene_template(self) -> str:
        """
        Generate an opening scene template.
        
        Returns:
            Opening scene template
        """
        if self.roadmap.project_type == "screenplay":
            return "// OPENING SCENE\n\nEXT. [LOCATION] - [TIME OF DAY]\n\n[Introduce protagonist in their ordinary world, revealing their normal life and suggesting their character flaws or needs]\n\n"
        else:
            return "// OPENING SCENE\n\n[Introduce protagonist in their ordinary world. Show their normal life, routine, and relationships. Hint at their character flaws, desires, and the changes that will come. Establish tone through careful description of setting and character actions.]\n\n"
    
    def _climax_scene_template(self) -> str:
        """
        Generate a climax scene template.
        
        Returns:
            Climax scene template
        """
        if self.roadmap.project_type == "screenplay":
            return "// CLIMAX SCENE\n\nINT./EXT. [LOCATION] - [TIME OF DAY]\n\n[The protagonist faces their ultimate challenge, with the highest stakes and the greatest obstacles. This scene represents the culmination of the external and internal conflicts.]\n\n"
        else:
            return "// CLIMAX SCENE\n\n[The protagonist faces their greatest challenge, with all obstacles converging at once. The stakes are at their highest, with the external and internal conflicts reaching their peak intensity. Everything the character has learned and become is put to the test in this pivotal moment.]\n\n"
    
    def _resolution_scene_template(self) -> str:
        """
        Generate a resolution scene template.
        
        Returns:
            Resolution scene template
        """
        if self.roadmap.project_type == "screenplay":
            return "// RESOLUTION SCENE\n\nEXT./INT. [LOCATION] - [TIME OF DAY]\n\n[Show the new world or status quo after the climax. Demonstrate how the protagonist has changed and what they've learned. Provide closure to the main conflicts while possibly leaving room for future stories.]\n\n"
        else:
            return "// RESOLUTION SCENE\n\n[Show the new world or status quo after the climax. Demonstrate how the protagonist has changed and what they've learned. The main conflicts should be resolved, with emotional satisfaction for the reader. Consider the thematic implications of the ending and how it reflects the journey.]\n\n"
    
    def get_creative_completions(self, 
                               project_type: str,
                               current_text: str, 
                               cursor_position: int) -> List[Dict]:
        """
        Get creative writing completions based on the roadmap.
        
        Args:
            project_type: Type of project (fiction, screenplay)
            current_text: Current text
            cursor_position: Position of the cursor
            
        Returns:
            List of completion suggestions
        """
        if not hasattr(self.roadmap, 'characters'):
            return []
        
        # Get the text up to the cursor position
        text_context = current_text[:cursor_position]
        
        # Extract the current line and the last "word" being typed
        last_line = text_context.split('\n')[-1] if '\n' in text_context else text_context
        last_word_match = re.search(r'[\w\s.]+$', last_line)
        last_word = last_word_match.group(0) if last_word_match else ""
        
        completions = []
        
        # Look for character-based completions
        for character_name in self.character_completions.keys():
            # Match character name at start of word/line
            if last_word.strip() and character_name.lower().startswith(last_word.strip().lower()):
                # Find matching completions
                for key, comp in self.roadmap_completions.items():
                    if key.startswith(character_name) and "character" in comp['type']:
                        # Add to completions with adjusted prefix match
                        adjusted_comp = comp.copy()
                        adjusted_comp['prefix_match'] = len(last_word.strip())
                        completions.append(adjusted_comp)
        
        # Look for setting-based completions
        for setting_name in self.setting_completions.keys():
            # Match setting name at start of word/line
            if last_word.strip() and setting_name.lower().startswith(last_word.strip().lower()):
                # Find matching completions
                for key, comp in self.roadmap_completions.items():
                    if key.startswith(setting_name) and "setting" in comp['type']:
                        # Add to completions with adjusted prefix match
                        adjusted_comp = comp.copy()
                        adjusted_comp['prefix_match'] = len(last_word.strip())
                        completions.append(adjusted_comp)
        
        # Look for scene templates
        if "OPENING" in last_word.upper():
            for key, comp in self.roadmap_completions.items():
                if "OPENING SCENE" in key:
                    adjusted_comp = comp.copy()
                    adjusted_comp['prefix_match'] = len(last_word)
                    completions.append(adjusted_comp)
        
        if "CLIMAX" in last_word.upper():
            for key, comp in self.roadmap_completions.items():
                if "CLIMAX SCENE" in key:
                    adjusted_comp = comp.copy()
                    adjusted_comp['prefix_match'] = len(last_word)
                    completions.append(adjusted_comp)
        
        if "RESOLUTION" in last_word.upper():
            for key, comp in self.roadmap_completions.items():
                if "RESOLUTION SCENE" in key:
                    adjusted_comp = comp.copy()
                    adjusted_comp['prefix_match'] = len(last_word)
                    completions.append(adjusted_comp)
        
        # Screenplay-specific completions
        if project_type == "screenplay":
            # Slugline completions
            if "INT" in last_word.upper() or "EXT" in last_word.upper():
                for key, comp in self.roadmap_completions.items():
                    if comp['type'] == "slugline" and (key.startswith("INT.") or key.startswith("EXT.")):
                        adjusted_comp = comp.copy()
                        adjusted_comp['prefix_match'] = len(last_word)
                        completions.append(adjusted_comp)
            
            # Character dialogue completions (uppercase names)
            uppercase_word = last_word.strip().upper()
            if uppercase_word and all(c.isupper() for c in uppercase_word):
                for character_name in self.character_completions.keys():
                    if character_name.upper().startswith(uppercase_word):
                        for key, comp in self.roadmap_completions.items():
                            if key.startswith(character_name.upper()) and comp['type'] == "character_dialogue":
                                adjusted_comp = comp.copy()
                                adjusted_comp['prefix_match'] = len(uppercase_word)
                                completions.append(adjusted_comp)
        
        # Fiction-specific completions
        if project_type == "fiction":
            # Scene break
            if "###" in last_word:
                completions.append({
                    "text": "###\n\n",
                    "display_text": "### (Scene Break)",
                    "type": "formatting",
                    "description": "Insert scene break",
                    "score": 90,
                    "prefix_match": len(last_word)
                })
            
            # Chapter heading
            if last_word.strip().lower().startswith("chapter"):
                chapter_number = len([l for l in current_text.split('\n') if l.strip().lower().startswith("chapter")])
                completions.append({
                    "text": f"Chapter {chapter_number + 1}\n\n",
                    "display_text": f"Chapter {chapter_number + 1}",
                    "type": "formatting",
                    "description": "Insert chapter heading",
                    "score": 95,
                    "prefix_match": len(last_word.strip())
                })
        
        return sorted(completions, key=lambda x: (-x['score'], -x['prefix_match']))
    
    def enhance_creative_autocomplete(self, 
                                    project_type: str,
                                    current_text: str, 
                                    cursor_position: int,
                                    file_content: str = "",
                                    filename: str = None) -> List[Dict]:
        """
        Enhance autocomplete suggestions with creative roadmap information.
        
        Args:
            project_type: Type of project (fiction, screenplay)
            current_text: Current text
            cursor_position: Position of the cursor
            file_content: Full content of the file (for context)
            filename: Name of the file being edited
            
        Returns:
            Enhanced list of completion suggestions
        """
        # Get normal autocomplete suggestions (few will apply for creative text)
        standard_completions = self.autocomplete.get_completions(
            language="markdown" if project_type == "fiction" else "fountain",
            current_code=current_text,
            cursor_position=cursor_position,
            file_content=file_content,
            filename=filename
        )
        
        # Get creative-based completions
        creative_completions = self.get_creative_completions(
            project_type=project_type,
            current_text=current_text,
            cursor_position=cursor_position
        )
        
        # Combine the two sets of completions, prioritizing creative ones
        all_completions = creative_completions + standard_completions
        
        # Deduplicate completions
        seen_displays = set()
        unique_completions = []
        
        for comp in all_completions:
            display = comp['display_text']
            if display not in seen_displays:
                seen_displays.add(display)
                unique_completions.append(comp)
        
        # Return the deduplicated, combined list
        return unique_completions
    
    def generate_creative_content(self, 
                                content_type: str, 
                                prompt: str = None,
                                character_name: str = None,
                                setting_name: str = None,
                                scene_goal: str = None) -> Optional[str]:
        """
        Generate creative content using AI if available.
        
        Args:
            content_type: Type of content to generate (dialogue, description, scene)
            prompt: Optional prompt to guide generation
            character_name: Optional character name for character-based content
            setting_name: Optional setting name for setting-based content
            scene_goal: Optional scene goal for scene-based content
            
        Returns:
            Generated content or None if generation failed
        """
        if not hasattr(self.roadmap, 'characters') or not self.has_openai:
            return None
        
        try:
            # Get creative context
            context = self.roadmap.generate_writing_context()
            
            # Prepare prompt based on content type
            generation_prompt = ""
            
            if content_type == "dialogue":
                generation_prompt = self._prepare_dialogue_prompt(context, character_name, prompt)
            elif content_type == "description":
                generation_prompt = self._prepare_description_prompt(context, setting_name, prompt)
            elif content_type == "scene":
                generation_prompt = self._prepare_scene_prompt(context, character_name, setting_name, scene_goal, prompt)
            elif content_type == "character":
                generation_prompt = self._prepare_character_prompt(context, character_name, prompt)
            else:
                logger.warning(f"Unknown content type: {content_type}")
                return None
            
            # Call OpenAI API
            response = self.continuous_coding.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": generation_prompt}],
                temperature=0.7,
                max_tokens=500
            )
            
            # Extract the generated content
            content = response.choices[0].message.content
            
            return content
            
        except Exception as e:
            logger.error(f"Error generating creative content: {str(e)}")
            return None
    
    def _prepare_dialogue_prompt(self, context: Dict, character_name: str, prompt: str) -> str:
        """
        Prepare prompt for dialogue generation.
        
        Args:
            context: Creative context dictionary
            character_name: Character name
            prompt: User prompt
            
        Returns:
            Generation prompt
        """
        # Find character info
        character_info = None
        for character in context.get('characters', []):
            if character.get('name') == character_name:
                character_info = character
                break
        
        dialogue_prompt = (
            f"You are writing dialogue for a {context['project_type']} project titled \"{context['project_name']}\".\n\n"
        )
        
        if character_info:
            dialogue_prompt += (
                f"Character information for {character_name}:\n"
                f"- Description: {character_info.get('description', 'N/A')}\n"
                f"- Role: {character_info.get('role', 'N/A')}\n"
                f"- Motivation: {character_info.get('motivation', 'N/A')}\n"
                f"- Character arc: {character_info.get('arc', 'N/A')}\n\n"
            )
        
        dialogue_prompt += (
            f"Please write realistic, character-appropriate dialogue for {character_name} "
            f"that sounds natural and reveals character. "
        )
        
        if prompt:
            dialogue_prompt += f"Additional context: {prompt}\n\n"
        
        dialogue_prompt += (
            f"If this is a screenplay, format as proper screenplay dialogue. "
            f"If this is fiction, format as dialogue with appropriate tags and formatting."
        )
        
        return dialogue_prompt
    
    def _prepare_description_prompt(self, context: Dict, setting_name: str, prompt: str) -> str:
        """
        Prepare prompt for description generation.
        
        Args:
            context: Creative context dictionary
            setting_name: Setting name
            prompt: User prompt
            
        Returns:
            Generation prompt
        """
        # Find setting info
        setting_info = None
        for location in context.get('locations', []):
            if location.get('name') == setting_name:
                setting_info = location
                break
        
        description_prompt = (
            f"You are writing description for a {context['project_type']} project titled \"{context['project_name']}\".\n\n"
        )
        
        if setting_info:
            description_prompt += (
                f"Setting information for {setting_name}:\n"
                f"- Description: {setting_info.get('description', 'N/A')}\n\n"
            )
        
        # Add theme context
        if context.get('themes'):
            description_prompt += "Project themes:\n"
            for theme in context.get('themes', []):
                description_prompt += f"- {theme.get('name')}: {theme.get('description', 'N/A')}\n"
            description_prompt += "\n"
        
        description_prompt += (
            f"Please write a vivid, sensory description of {setting_name or 'the setting'} "
            f"that establishes mood and atmosphere while supporting the themes of the project. "
            f"Include visual details, sounds, smells, and textures as appropriate. "
        )
        
        if prompt:
            description_prompt += f"Additional context: {prompt}\n\n"
        
        description_prompt += (
            f"If this is a screenplay, format as proper screenplay description. "
            f"If this is fiction, write prose description appropriate for narrative."
        )
        
        return description_prompt
    
    def _prepare_scene_prompt(self, context: Dict, character_name: str, setting_name: str, 
                            scene_goal: str, prompt: str) -> str:
        """
        Prepare prompt for scene generation.
        
        Args:
            context: Creative context dictionary
            character_name: Primary character name
            setting_name: Setting name
            scene_goal: Scene goal/purpose
            prompt: User prompt
            
        Returns:
            Generation prompt
        """
        scene_prompt = (
            f"You are writing a scene for a {context['project_type']} project titled \"{context['project_name']}\".\n\n"
            f"Project description: {context['project_description']}\n\n"
        )
        
        # Add character context
        characters_in_scene = []
        if character_name:
            characters_in_scene.append(character_name)
            
            # Find character info
            for character in context.get('characters', []):
                if character.get('name') == character_name:
                    scene_prompt += (
                        f"Primary character information for {character_name}:\n"
                        f"- Description: {character.get('description', 'N/A')}\n"
                        f"- Role: {character.get('role', 'N/A')}\n"
                        f"- Motivation: {character.get('motivation', 'N/A')}\n\n"
                    )
                    break
        
        # Add setting context
        if setting_name:
            # Find setting info
            for location in context.get('locations', []):
                if location.get('name') == setting_name:
                    scene_prompt += (
                        f"Setting information for {setting_name}:\n"
                        f"- Description: {location.get('description', 'N/A')}\n\n"
                    )
                    break
        
        # Add scene goal
        if scene_goal:
            scene_prompt += f"Scene goal: {scene_goal}\n\n"
        
        # Add additional context
        if prompt:
            scene_prompt += f"Additional context: {prompt}\n\n"
        
        # Format instructions
        if context['project_type'] == "screenplay":
            scene_prompt += (
                f"Please write a scene in proper screenplay format, including:\n"
                f"- Slugline (INT/EXT, location, time of day)\n"
                f"- Action description\n"
                f"- Character names in ALL CAPS when first introduced\n"
                f"- Dialogue with character names in ALL CAPS\n"
                f"- Parentheticals for brief actions or emotion cues\n\n"
                f"Keep the scene focused, dramatic, and revealing of character and plot."
            )
        else:
            scene_prompt += (
                f"Please write a prose scene that includes:\n"
                f"- Setting description that establishes atmosphere\n"
                f"- Character actions and reactions\n"
                f"- Dialogue with appropriate attributions\n"
                f"- Internal character thoughts if appropriate\n\n"
                f"Balance description, action, and dialogue to create an engaging scene "
                f"that advances the plot and reveals character."
            )
        
        return scene_prompt
    
    def _prepare_character_prompt(self, context: Dict, character_name: str, prompt: str) -> str:
        """
        Prepare prompt for character development.
        
        Args:
            context: Creative context dictionary
            character_name: Character name
            prompt: User prompt
            
        Returns:
            Generation prompt
        """
        character_prompt = (
            f"You are developing a character for a {context['project_type']} project titled \"{context['project_name']}\".\n\n"
            f"Project description: {context['project_description']}\n\n"
        )
        
        # Add character context if this is an existing character
        existing_character = None
        for character in context.get('characters', []):
            if character.get('name') == character_name:
                existing_character = character
                break
        
        if existing_character:
            character_prompt += (
                f"Existing information for character {character_name}:\n"
                f"- Description: {existing_character.get('description', 'N/A')}\n"
                f"- Role: {existing_character.get('role', 'N/A')}\n"
                f"- Motivation: {existing_character.get('motivation', 'N/A')}\n"
                f"- Character arc: {existing_character.get('arc', 'N/A')}\n\n"
                f"Please expand on this character by adding depth, backstory, and complexity."
            )
        else:
            character_prompt += (
                f"Create a new character named {character_name or '[Character Name]'} for this project.\n"
                f"Develop a multi-dimensional character with:\n"
                f"- Detailed physical description\n"
                f"- Background/backstory\n"
                f"- Personality traits and quirks\n"
                f"- Internal and external motivations\n"
                f"- Goals and conflicts\n"
                f"- Character arc/development path\n"
                f"- Role in the story\n"
                f"- Unique voice/dialogue style\n"
            )
        
        # Add theme context
        if context.get('themes'):
            character_prompt += "\nProject themes that might influence the character:\n"
            for theme in context.get('themes', []):
                character_prompt += f"- {theme.get('name')}: {theme.get('description', 'N/A')}\n"
        
        # Add additional context
        if prompt:
            character_prompt += f"\nAdditional context: {prompt}\n"
        
        character_prompt += (
            f"\nProvide a comprehensive character profile that can be used to write "
            f"consistent, believable scenes and dialogue for this character."
        )
        
        return character_prompt
    
    def analyze_writing_with_roadmap(self, file_path: str) -> Dict:
        """
        Analyze creative writing against the roadmap.
        
        Args:
            file_path: Path to the file to analyze
            
        Returns:
            Analysis results
        """
        if not hasattr(self.roadmap, 'characters'):
            return {"error": "Not a creative roadmap"}
        
        try:
            # Read the file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Get creative context
            context = self.roadmap.generate_writing_context()
            
            results = {
                "file_path": file_path,
                "roadmap_name": self.roadmap.name,
                "character_usage": [],
                "setting_usage": [],
                "theme_analysis": [],
                "scene_analysis": [],
                "suggestions": []
            }
            
            # Analyze character usage
            for character in context.get('characters', []):
                name = character.get('name', '')
                if name:
                    occurrences = content.count(name)
                    results["character_usage"].append({
                        "name": name,
                        "occurrences": occurrences,
                        "has_dialogue": self._has_character_dialogue(content, name, self.roadmap.project_type)
                    })
            
            # Analyze setting usage
            for location in context.get('locations', []):
                name = location.get('name', '')
                if name:
                    occurrences = content.count(name)
                    results["setting_usage"].append({
                        "name": name,
                        "occurrences": occurrences
                    })
            
            # Analyze theme usage
            for theme in context.get('themes', []):
                name = theme.get('name', '')
                keywords = theme.get('keywords', [])
                if name:
                    keyword_matches = []
                    for keyword in keywords:
                        count = content.lower().count(keyword.lower())
                        if count > 0:
                            keyword_matches.append({
                                "keyword": keyword,
                                "count": count
                            })
                    
                    results["theme_analysis"].append({
                        "name": name,
                        "keyword_matches": keyword_matches,
                        "strength": len(keyword_matches) / max(1, len(keywords))
                    })
            
            # Analyze scene structure
            if self.roadmap.project_type == "screenplay":
                # Count sluglines as scenes
                sluglines = re.findall(r'(INT|EXT|INT\./EXT|EXT\./INT)\..*?(\n|$)', content, re.IGNORECASE)
                results["scene_analysis"].append({
                    "total_scenes": len(sluglines),
                    "scene_breakdown": self._analyze_screenplay_structure(content)
                })
            else:
                # Count scene breaks as scenes
                scene_breaks = re.findall(r'#{3,}', content)
                chapter_headings = re.findall(r'chapter\s+\d+', content, re.IGNORECASE)
                results["scene_analysis"].append({
                    "total_scenes": len(scene_breaks) + 1,  # +1 for the beginning
                    "total_chapters": len(chapter_headings),
                    "scenes_per_chapter": (len(scene_breaks) + 1) / max(1, len(chapter_headings)) if chapter_headings else 0
                })
            
            # Generate suggestions based on analysis
            if self.has_openai:
                suggestions = self._generate_writing_suggestions(content, results, context)
                if suggestions:
                    results["suggestions"] = suggestions
            
            return results
            
        except Exception as e:
            logger.error(f"Error analyzing writing with roadmap: {str(e)}")
            return {"error": str(e)}
    
    def _has_character_dialogue(self, content: str, character_name: str, project_type: str) -> bool:
        """
        Check if a character has dialogue in the content.
        
        Args:
            content: Text content
            character_name: Character name
            project_type: Project type (fiction, screenplay)
            
        Returns:
            True if character has dialogue, False otherwise
        """
        if project_type == "screenplay":
            # Look for character name in all caps followed by dialogue
            pattern = fr'{character_name.upper()}\s*\n'
            return bool(re.search(pattern, content))
        else:
            # Look for common dialogue attributions
            patterns = [
                fr'{character_name} said',
                fr'{character_name} asked',
                fr'{character_name} replied',
                fr'{character_name} whispered',
                fr'{character_name} shouted',
                fr'\"{character_name} said',
                fr'\"{character_name} asked'
            ]
            
            for pattern in patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    return True
            
            return False
    
    def _analyze_screenplay_structure(self, content: str) -> Dict:
        """
        Analyze screenplay structure.
        
        Args:
            content: Screenplay content
            
        Returns:
            Structure analysis
        """
        # Simple heuristic analysis - in a real implementation this would be more sophisticated
        total_lines = len(content.split('\n'))
        
        # Estimate page count (1 page ≈ 55 lines in a screenplay)
        estimated_pages = total_lines / 55
        
        # Sluglines and scenes
        sluglines = re.findall(r'(INT|EXT|INT\./EXT|EXT\./INT)\..*?(\n|$)', content, re.IGNORECASE)
        
        # Rough breakdown by act
        if estimated_pages > 0:
            first_quarter = content[:int(len(content)/4)]
            second_quarter = content[int(len(content)/4):int(len(content)/2)]
            third_quarter = content[int(len(content)/2):int(3*len(content)/4)]
            fourth_quarter = content[int(3*len(content)/4):]
            
            act1_sluglines = len(re.findall(r'(INT|EXT|INT\./EXT|EXT\./INT)\..*?(\n|$)', first_quarter, re.IGNORECASE))
            act2a_sluglines = len(re.findall(r'(INT|EXT|INT\./EXT|EXT\./INT)\..*?(\n|$)', second_quarter, re.IGNORECASE))
            act2b_sluglines = len(re.findall(r'(INT|EXT|INT\./EXT|EXT\./INT)\..*?(\n|$)', third_quarter, re.IGNORECASE))
            act3_sluglines = len(re.findall(r'(INT|EXT|INT\./EXT|EXT\./INT)\..*?(\n|$)', fourth_quarter, re.IGNORECASE))
            
            return {
                "estimated_pages": round(estimated_pages, 1),
                "total_scenes": len(sluglines),
                "act_breakdown": {
                    "act1": act1_sluglines,
                    "act2a": act2a_sluglines,
                    "act2b": act2b_sluglines,
                    "act3": act3_sluglines
                }
            }
        
        return {
            "estimated_pages": 0,
            "total_scenes": len(sluglines),
            "act_breakdown": {
                "act1": 0,
                "act2a": 0,
                "act2b": 0,
                "act3": 0
            }
        }
    
    def _generate_writing_suggestions(self, content: str, analysis: Dict, context: Dict) -> List[Dict]:
        """
        Generate writing suggestions based on analysis and roadmap.
        
        Args:
            content: File content
            analysis: Analysis results
            context: Creative context
            
        Returns:
            List of suggestions
        """
        if not self.has_openai:
            return []
        
        try:
            # Prepare prompt for suggestions
            prompt = (
                f"You are analyzing a {context['project_type']} project titled \"{context['project_name']}\".\n\n"
                f"Project description: {context['project_description']}\n\n"
            )
            
            # Character analysis
            prompt += "Character usage:\n"
            for char in analysis["character_usage"]:
                dialogue_status = "has dialogue" if char["has_dialogue"] else "no dialogue"
                prompt += f"- {char['name']}: {char['occurrences']} occurrences, {dialogue_status}\n"
            
            # Setting analysis
            prompt += "\nSetting usage:\n"
            for setting in analysis["setting_usage"]:
                prompt += f"- {setting['name']}: {setting['occurrences']} occurrences\n"
            
            # Theme analysis
            prompt += "\nTheme analysis:\n"
            for theme in analysis["theme_analysis"]:
                strength = theme["strength"]
                strength_text = "strong" if strength > 0.5 else "moderate" if strength > 0.2 else "weak"
                prompt += f"- {theme['name']}: {strength_text} presence\n"
            
            # Scene analysis
            prompt += "\nStructure analysis:\n"
            for scene_data in analysis["scene_analysis"]:
                prompt += f"- Total scenes: {scene_data.get('total_scenes', 0)}\n"
                if "total_chapters" in scene_data:
                    prompt += f"- Total chapters: {scene_data.get('total_chapters', 0)}\n"
                    prompt += f"- Scenes per chapter: {scene_data.get('scenes_per_chapter', 0):.1f}\n"
                if "estimated_pages" in scene_data:
                    prompt += f"- Estimated pages: {scene_data.get('estimated_pages', 0)}\n"
                if "act_breakdown" in scene_data:
                    breakdown = scene_data["act_breakdown"]
                    prompt += f"- Act breakdown: Act 1: {breakdown.get('act1', 0)} scenes, Act 2a: {breakdown.get('act2a', 0)} scenes, Act 2b: {breakdown.get('act2b', 0)} scenes, Act 3: {breakdown.get('act3', 0)} scenes\n"
            
            # Add request for suggestions
            prompt += (
                "\nBased on this analysis and the project's creative roadmap, provide concrete suggestions "
                "for improving the writing. Focus on character development, plot structure, theme integration, "
                "and stylistic considerations. Provide 3-5 specific, actionable suggestions that would "
                "strengthen the piece and better align it with the project goals.\n\n"
                "Return your response as a JSON array of suggestion objects, each with 'title' and 'details' fields."
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
            logger.error(f"Error generating writing suggestions: {str(e)}")
            return []


# Singleton instance
_creative_autocomplete_bridge = None

def get_creative_autocomplete_bridge(roadmap_id: Optional[str] = None) -> CreativeAutocompleteBridge:
    """
    Get a singleton instance of the creative autocomplete bridge.
    
    Args:
        roadmap_id: Optional ID of a roadmap to use
        
    Returns:
        CreativeAutocompleteBridge instance
    """
    global _creative_autocomplete_bridge
    if _creative_autocomplete_bridge is None:
        _creative_autocomplete_bridge = CreativeAutocompleteBridge(roadmap_id)
    elif roadmap_id and _creative_autocomplete_bridge.roadmap_id != roadmap_id:
        _creative_autocomplete_bridge.set_roadmap(roadmap_id)
    return _creative_autocomplete_bridge


# Example usage
if __name__ == "__main__":
    # Get a creative roadmap manager
    manager = get_creative_roadmap_manager()
    
    # List available roadmaps
    roadmaps = manager.list_roadmaps()
    
    print("Available creative roadmaps:")
    for i, roadmap in enumerate(roadmaps):
        print(f"{i+1}. {roadmap['name']} (ID: {roadmap['id']})")
    
    if roadmaps:
        # Use the first roadmap for demonstration
        roadmap_id = roadmaps[0]['id']
        
        # Initialize the bridge
        bridge = get_creative_autocomplete_bridge(roadmap_id)
        
        print(f"\nLoaded roadmap: {bridge.roadmap.name}")
        
        # Show some example completions
        project_type = bridge.roadmap.project_type
        
        print(f"\nExample {project_type} completions:")
        
        if project_type == "fiction":
            # Fiction example
            sample_text = "Eleanor entered the Blackwood Library, her fingers"
            completions = bridge.get_creative_completions(
                project_type=project_type,
                current_text=sample_text,
                cursor_position=len(sample_text)
            )
            
            print(f"For the text: '{sample_text}'")
            for completion in completions[:3]:
                print(f"- {completion['display_text']} - {completion['description']}")
                
            # Character dialogue example
            sample_text = "Eleanor said"
            completions = bridge.get_creative_completions(
                project_type=project_type,
                current_text=sample_text,
                cursor_position=len(sample_text)
            )
            
            print(f"\nFor the text: '{sample_text}'")
            for completion in completions[:3]:
                print(f"- {completion['display_text']} - {completion['description']}")
                
        elif project_type == "screenplay":
            # Screenplay example
            sample_text = "INT. "
            completions = bridge.get_creative_completions(
                project_type=project_type,
                current_text=sample_text,
                cursor_position=len(sample_text)
            )
            
            print(f"For the text: '{sample_text}'")
            for completion in completions[:3]:
                print(f"- {completion['display_text']} - {completion['description']}")
                
            # Character name example
            if bridge.character_completions:
                character_name = next(iter(bridge.character_completions.keys()))
                sample_text = character_name.upper()
                completions = bridge.get_creative_completions(
                    project_type=project_type,
                    current_text=sample_text,
                    cursor_position=len(sample_text)
                )
                
                print(f"\nFor the text: '{sample_text}'")
                for completion in completions[:3]:
                    print(f"- {completion['display_text']} - {completion['description']}")
        
        # Generate creative content example
        if bridge.has_openai:
            print("\nGenerating dialogue example:")
            
            if bridge.character_completions:
                character_name = next(iter(bridge.character_completions.keys()))
                dialogue = bridge.generate_creative_content(
                    content_type="dialogue",
                    character_name=character_name,
                    prompt="expressing determination"
                )
                
                if dialogue:
                    print(f"\nGenerated dialogue for {character_name}:")
                    print(f"---\n{dialogue}\n---")
    else:
        print("No creative roadmaps found. Create one first using the Creative Roadmap Manager.")