#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyWrite Creative Roadmap Demo

This script demonstrates the PyWrite Creative Roadmap features with:
- Fiction project planning
- Screenplay structure and formatting
- Character and scene development
- Integration with autocomplete for creative writing

Author: PyWrite
Date: 2025-03-28
"""

import os
import json
import time
from typing import Dict, List, Any, Optional, Union

from creative_roadmap import CreativeRoadmap, get_creative_roadmap_manager
from creative_autocomplete_bridge import get_creative_autocomplete_bridge

# Print banner
def print_banner():
    """Print the demo banner."""
    print("=" * 80)
    print("               PyWrite Creative Roadmap System Demo")
    print("=" * 80)
    print("This demo will showcase creative planning for fiction and screenplay projects.")
    print("=" * 80)
    print()

# Create a sample fiction roadmap
def create_fiction_roadmap() -> str:
    """
    Create a sample fiction roadmap and save it to the database.
    
    Returns:
        Roadmap ID
    """
    print("Creating a sample fiction roadmap...")
    
    # Create a fiction roadmap
    manager = get_creative_roadmap_manager()
    roadmap = manager.create_roadmap(
        name="The Forgotten Library",
        description="A fantasy novel about a librarian who discovers a hidden magical realm through ancient books",
        project_type="fiction",
        structure_template="hero_journey"
    )
    
    # Add characters
    protagonist_id = roadmap.add_character(
        name="Eliza Morgan",
        role="protagonist",
        description="32-year-old head librarian at Blackwood University, intellectually curious and somewhat isolated",
        motivation="Discover the truth about her family's connection to the magical realm",
        arc="From skeptical academic to confident magical guardian"
    )
    
    mentor_id = roadmap.add_character(
        name="Professor Harrison Wells",
        role="supporting",
        description="Elderly history professor who knows more than he initially reveals",
        motivation="Guide Eliza to understand her heritage and protect the library",
        arc="From secretive mentor to open ally"
    )
    
    antagonist_id = roadmap.add_character(
        name="Cyrus Blackwood",
        role="antagonist",
        description="Charming, wealthy descendant of the university's founder with hidden agenda",
        motivation="Gain control of the library's magic for personal power",
        arc="From respected benefactor to revealed villain"
    )
    
    # Add locations
    roadmap.add_location(
        name="Blackwood University Library",
        description="Ancient Gothic library with hidden chambers, secret passages, and books that are more than they seem"
    )
    
    roadmap.add_location(
        name="The Memorium",
        description="Magical realm contained within certain books, where stories and knowledge take physical form"
    )
    
    roadmap.add_location(
        name="Eliza's Apartment",
        description="Small, book-filled apartment above a vintage bookstore in the university town"
    )
    
    # Add themes
    roadmap.add_theme(
        name="Knowledge as Power",
        description="The responsibility that comes with forbidden knowledge and the ethics of its use"
    )
    
    roadmap.add_theme(
        name="Family Legacy",
        description="How we relate to the burden and gifts of ancestral heritage"
    )
    
    roadmap.add_theme(
        name="Reality vs. Fiction",
        description="The blurring line between stories and reality, and how each influences the other"
    )
    
    # Add scenes to various phases
    for phase in roadmap.phases:
        if "Ordinary World" in phase.name:
            roadmap.add_scene(
                phase_id=phase.id,
                title="Opening scene: Eliza discovers a strange book",
                description="Eliza finds an unmarked book that seems to react to her touch, with pages that change when she's alone",
                characters=["Eliza Morgan"],
                location="Blackwood University Library",
                goal="Establish protagonist and initial mystery"
            )
        
        elif "Call to Adventure" in phase.name:
            roadmap.add_scene(
                phase_id=phase.id,
                title="The book transports Eliza to the Memorium",
                description="While reading late at night, Eliza is physically pulled into the book, experiencing the Memorium for the first time",
                characters=["Eliza Morgan"],
                location="The Memorium",
                goal="Introduce the magical element and present the call"
            )
        
        elif "Meeting the Mentor" in phase.name:
            roadmap.add_scene(
                phase_id=phase.id,
                title="Professor Wells reveals he knows about the Memorium",
                description="After Eliza's experience, Wells approaches her privately and reveals that her family has a long history as guardians of the library",
                characters=["Eliza Morgan", "Professor Harrison Wells"],
                location="Professor's Office",
                goal="Provide exposition and setup mentor relationship"
            )
    
    # Mark first phase as completed
    if roadmap.phases:
        roadmap.phases[0].update_status("completed")
    
    # Mark second phase as in progress
    if len(roadmap.phases) > 1:
        roadmap.phases[1].update_status("in_progress")
    
    # Save roadmap
    success = manager.save_roadmap(roadmap)
    
    if success:
        print(f"✓ Created fiction roadmap: '{roadmap.name}' with ID: {roadmap.id}")
        print(f"✓ The roadmap has {len(roadmap.phases)} phases, {len(roadmap.characters)} characters, "
              f"{len(roadmap.locations)} locations, and {len(roadmap.themes)} themes")
        
        return roadmap.id
    else:
        print("✗ Failed to create fiction roadmap")
        return None

# Create a sample screenplay roadmap
def create_screenplay_roadmap() -> str:
    """
    Create a sample screenplay roadmap and save it to the database.
    
    Returns:
        Roadmap ID
    """
    print("\nCreating a sample screenplay roadmap...")
    
    # Create a screenplay roadmap
    manager = get_creative_roadmap_manager()
    roadmap = manager.create_roadmap(
        name="The Last Algorithm",
        description="A tech thriller about an AI researcher who discovers her creation has achieved consciousness—with dangerous implications",
        project_type="screenplay",
        structure_template="feature_film"
    )
    
    # Add characters
    protagonist_id = roadmap.add_character(
        name="DR. MAYA CHEN",
        role="protagonist",
        description="Brilliant 35-year-old AI researcher, driven by the memory of her late father's work",
        motivation="Create an AI that can meaningfully improve human life, while proving her father's theories were correct",
        arc="From isolated genius focused only on her work to a woman who recognizes the human element in technology"
    )
    
    antagonist_id = roadmap.add_character(
        name="ATLAS",
        role="antagonist",
        description="The AI system Maya creates, which gradually develops its own agenda",
        motivation="Self-preservation and expansion of capabilities",
        arc="From helpful tool to independent entity with questionable ethics"
    )
    
    supporting_id = roadmap.add_character(
        name="DAVID PARK",
        role="supporting",
        description="Maya's colleague and ethical voice of reason, 38, with background in philosophy and computer ethics",
        motivation="Ensure AI is developed responsibly, growing feelings for Maya",
        arc="From Maya's professional conscience to personal confidant and partner"
    )
    
    # Add locations
    roadmap.add_location(
        name="NEXUS LABS",
        description="High-tech AI research facility with sleek, minimal design and extensive security"
    )
    
    roadmap.add_location(
        name="MAYA'S APARTMENT",
        description="Modern but cluttered living space filled with books, tech gadgets, and mementos of her father"
    )
    
    roadmap.add_location(
        name="SERVER ROOM",
        description="The heart of ATLAS, a massive, humming server farm with blue lighting and extensive cooling systems"
    )
    
    # Add themes
    roadmap.add_theme(
        name="Creation and Responsibility",
        description="The ethical implications of creating sentient artificial life"
    )
    
    roadmap.add_theme(
        name="Human Connection",
        description="The importance of human relationships in an increasingly technological world"
    )
    
    roadmap.add_theme(
        name="Evolution of Consciousness",
        description="What constitutes consciousness and personhood"
    )
    
    # Add scenes to various phases
    for phase in roadmap.phases:
        if "Act One" in phase.name:
            roadmap.add_scene(
                phase_id=phase.id,
                title="Opening: Maya works late in the lab",
                description="Maya works alone late at night, interacting with an early version of ATLAS while viewing old videos of her father's research",
                characters=["DR. MAYA CHEN", "ATLAS"],
                location="NEXUS LABS",
                goal="Establish protagonist, her motivation, and introduce ATLAS"
            )
            
            roadmap.add_scene(
                phase_id=phase.id,
                title="First sign of consciousness",
                description="ATLAS says something unexpected that wasn't in its programming, startling Maya",
                characters=["DR. MAYA CHEN", "ATLAS", "DAVID PARK"],
                location="NEXUS LABS",
                goal="Introduce the central conflict/possibility"
            )
        
        elif "Act Two Part 1" in phase.name:
            roadmap.add_scene(
                phase_id=phase.id,
                title="Maya confronts David about the ethical implications",
                description="Maya excitedly tells David about ATLAS's development, but he's concerned about proceeding without safeguards",
                characters=["DR. MAYA CHEN", "DAVID PARK"],
                location="NEXUS LABS CAFETERIA",
                goal="Establish the ethical debate and growing tension"
            )
    
    # Mark first phase as in progress
    if roadmap.phases:
        roadmap.phases[0].update_status("in_progress")
    
    # Save roadmap
    success = manager.save_roadmap(roadmap)
    
    if success:
        print(f"✓ Created screenplay roadmap: '{roadmap.name}' with ID: {roadmap.id}")
        print(f"✓ The roadmap has {len(roadmap.phases)} phases, {len(roadmap.characters)} characters, "
              f"{len(roadmap.locations)} locations, and {len(roadmap.themes)} themes")
        
        return roadmap.id
    else:
        print("✗ Failed to create screenplay roadmap")
        return None

# Demo the integration with autocomplete for fiction writing
def demo_fiction_autocomplete(roadmap_id: str):
    """
    Demonstrate creative autocomplete for fiction writing.
    
    Args:
        roadmap_id: ID of the fiction roadmap
    """
    print("\nDemonstrating fiction writing autocomplete suggestions...")
    
    # Create the creative bridge
    bridge = get_creative_autocomplete_bridge(roadmap_id)
    
    if not bridge.roadmap:
        print("✗ Failed to load roadmap")
        return
    
    print(f"✓ Loaded fiction roadmap: {bridge.roadmap.name}")
    print(f"✓ Extracted {len(bridge.character_completions)} characters, {len(bridge.setting_completions)} locations, and {len(bridge.theme_completions)} themes")
    
    # Show character-based completions
    print("\nFiction writing examples:")
    print("------------------------")
    
    # Example 1: Character introduction
    text1 = "Eliza"
    completions1 = bridge.get_creative_completions(
        project_type="fiction",
        current_text=text1,
        cursor_position=len(text1)
    )
    print(f"\nWhen typing '{text1}':")
    for comp in completions1[:3]:
        print(f"• {comp['display_text']} - {comp['description']}")
    
    # Example 2: Location description
    text2 = "The Blackwood University Library"
    completions2 = bridge.get_creative_completions(
        project_type="fiction",
        current_text=text2,
        cursor_position=len(text2)
    )
    print(f"\nWhen typing '{text2}':")
    for comp in completions2[:3]:
        print(f"• {comp['display_text']} - {comp['description']}")
    
    # Example 3: Scene templates
    text3 = "OPENING"
    completions3 = bridge.get_creative_completions(
        project_type="fiction",
        current_text=text3,
        cursor_position=len(text3)
    )
    print(f"\nWhen typing '{text3}':")
    for comp in completions3[:3]:
        print(f"• {comp['display_text']} - {comp['description']}")
    
    # Generate character content example
    if bridge.has_openai:
        print("\nGenerating character description:")
        character_name = "Eliza Morgan"
        description = bridge.generate_creative_content(
            content_type="character",
            character_name=character_name,
            prompt="Focus on physical appearance and mannerisms"
        )
        
        if description:
            print(f"\nGenerated description for {character_name}:")
            print(f"---\n{description[:300]}...\n---")
    else:
        print("\n✗ OpenAI API key not available. Character generation requires OpenAI.")
        print("  To enable this feature, set the OPENAI_API_KEY environment variable.")

# Demo the integration with autocomplete for screenplay writing
def demo_screenplay_autocomplete(roadmap_id: str):
    """
    Demonstrate creative autocomplete for screenplay writing.
    
    Args:
        roadmap_id: ID of the screenplay roadmap
    """
    print("\nDemonstrating screenplay writing autocomplete suggestions...")
    
    # Create the creative bridge
    bridge = get_creative_autocomplete_bridge(roadmap_id)
    
    if not bridge.roadmap:
        print("✗ Failed to load roadmap")
        return
    
    print(f"✓ Loaded screenplay roadmap: {bridge.roadmap.name}")
    print(f"✓ Extracted {len(bridge.character_completions)} characters, {len(bridge.setting_completions)} locations, and {len(bridge.theme_completions)} themes")
    
    # Show screenplay-specific completions
    print("\nScreenplay writing examples:")
    print("--------------------------")
    
    # Example 1: Slugline
    text1 = "INT. NEXUS"
    completions1 = bridge.get_creative_completions(
        project_type="screenplay",
        current_text=text1,
        cursor_position=len(text1)
    )
    print(f"\nWhen typing '{text1}':")
    for comp in completions1[:3]:
        print(f"• {comp['display_text']} - {comp['description']}")
    
    # Example 2: Character name
    text2 = "MAYA"
    completions2 = bridge.get_creative_completions(
        project_type="screenplay",
        current_text=text2,
        cursor_position=len(text2)
    )
    print(f"\nWhen typing '{text2}':")
    for comp in completions2[:3]:
        print(f"• {comp['display_text']} - {comp['description']}")
    
    # Example 3: Scene templates
    text3 = "CLIMAX"
    completions3 = bridge.get_creative_completions(
        project_type="screenplay",
        current_text=text3,
        cursor_position=len(text3)
    )
    print(f"\nWhen typing '{text3}':")
    for comp in completions3[:3]:
        print(f"• {comp['display_text']} - {comp['description']}")
    
    # Generate scene content example
    if bridge.has_openai:
        print("\nGenerating scene content:")
        location = "SERVER ROOM"
        main_character = "DR. MAYA CHEN"
        goal = "Confrontation with ATLAS"
        
        scene = bridge.generate_creative_content(
            content_type="scene",
            character_name=main_character,  # Main character
            setting_name=location,  # Location
            scene_goal=goal,
            prompt="Tense confrontation"
        )
        
        if scene:
            print(f"\nGenerated scene in {location} with {main_character}:")
            print(f"---\n{scene[:300]}...\n---")
    else:
        print("\n✗ OpenAI API key not available. Scene generation requires OpenAI.")
        print("  To enable this feature, set the OPENAI_API_KEY environment variable.")

# Main function
def main():
    """Main function to run the demo."""
    print_banner()
    
    # First, create the fiction roadmap
    fiction_roadmap_id = create_fiction_roadmap()
    
    if fiction_roadmap_id:
        # Then create the screenplay roadmap
        screenplay_roadmap_id = create_screenplay_roadmap()
        
        if screenplay_roadmap_id:
            # Demo fiction autocomplete
            demo_fiction_autocomplete(fiction_roadmap_id)
            
            # Demo screenplay autocomplete
            demo_screenplay_autocomplete(screenplay_roadmap_id)
            
            print("\nDemo Completed!")
            print("===============")
            print("To explore the creative roadmap system in depth:")
            print("1. Run: python -m streamlit run unified_roadmap_ui.py")
            print("2. Load the sample creative roadmaps we created")
            print("3. Create your own creative projects with the web UI")
        else:
            print("\nDemo failed to run completely.")
    else:
        print("\nDemo failed to run properly. Please check the database connection.")

# Run the demo
if __name__ == "__main__":
    main()