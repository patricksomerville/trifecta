#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyWrite Mode Switcher Demo

A visual demonstration of the retro-style mode switcher dial.
This generates an HTML file with the mode switcher animation
and opens it in a web browser.

Author: PyWrite
Date: 2025-03-28
"""

import os
import webbrowser
import tempfile

def get_svg_content():
    """Get the SVG dial content."""
    svg_path = os.path.join('assets', 'ui', 'mode_dial.svg')
    
    try:
        with open(svg_path, 'r') as f:
            return f.read()
    except:
        # Fallback inline SVG if file doesn't exist
        return '''<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200" viewBox="0 0 200 200">
  <!-- Dial background plate -->
  <circle cx="100" cy="100" r="95" fill="#333" stroke="#222" stroke-width="5" />
  <circle cx="100" cy="100" r="85" fill="#444" stroke="#555" stroke-width="2" />
  
  <!-- Metallic rim -->
  <circle cx="100" cy="100" r="80" fill="none" stroke="#888" stroke-width="4" />
  <circle cx="100" cy="100" r="78" fill="none" stroke="#999" stroke-width="1" />
  
  <!-- Tick marks -->
  <!-- Fiction mode (position 1) -->
  <line x1="100" y1="30" x2="100" y2="45" stroke="#DDD" stroke-width="3" />
  <text x="100" y="25" text-anchor="middle" fill="#DDD" font-family="Arial, sans-serif" font-size="12">Fiction</text>
  
  <!-- Screenwriting mode (position 2) -->
  <line x1="153" y1="73" x2="142" y2="84" stroke="#DDD" stroke-width="3" />
  <text x="163" y="70" text-anchor="middle" fill="#DDD" font-family="Arial, sans-serif" font-size="12">Screenwriting</text>
  
  <!-- Code mode (position 3) -->
  <line x1="100" y1="170" x2="100" y2="155" stroke="#DDD" stroke-width="3" />
  <text x="100" y="185" text-anchor="middle" fill="#DDD" font-family="Arial, sans-serif" font-size="12">Code</text>
  
  <!-- Center hub -->
  <circle cx="100" cy="100" r="25" fill="#222" stroke="#555" stroke-width="2" />
  <circle cx="100" cy="100" r="20" fill="#333" stroke="#888" stroke-width="1" />
  
  <!-- Dial indicator (knob) -->
  <g id="knob" transform="rotate(0, 100, 100)">
    <circle cx="100" cy="100" r="18" fill="#222" stroke="#444" stroke-width="1" />
    <circle cx="100" cy="100" r="15" fill="#333" stroke="#555" stroke-width="1" />
    <line x1="100" y1="100" x2="100" y2="85" stroke="#DDD" stroke-width="2" />
    <circle cx="100" cy="100" r="5" fill="#555" stroke="#666" stroke-width="1" />
  </g>
  
  <!-- Highlight and shadow to create 3D effect -->
  <circle cx="85" cy="85" r="75" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="3" />
</svg>'''

def generate_mode_info():
    """Generate information about the three modes."""
    modes = [
        {
            "name": "Fiction",
            "description": "Perfect for writing novels, short stories, and other fiction",
            "features": [
                "Character and plot tracking",
                "Word count and readability analysis",
                "Chapter organization tools",
                "Fiction-specific AI assistance"
            ],
            "color": "#3a7ca5"  # Blue
        },
        {
            "name": "Screenwriting",
            "description": "Designed for writing scripts and screenplays with proper formatting",
            "features": [
                "Screenplay formatting (scene headings, dialogue)",
                "Character and scene tracking",
                "Industry-standard output formats",
                "Visualization tools"
            ],
            "color": "#9a7d0a"  # Gold
        },
        {
            "name": "Code",
            "description": "Optimized for writing and editing programming code",
            "features": [
                "Syntax highlighting",
                "Intelligent code assistance",
                "Documentation helpers",
                "Testing and debugging tools"
            ],
            "color": "#2c7c43"  # Green
        }
    ]
    
    return modes

def create_html_demo():
    """Create and open an HTML demo of the mode switcher dial."""
    svg_content = get_svg_content()
    modes = generate_mode_info()
    
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>PyWrite Mode Switcher Demo</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background-color: #2a2a2a;
            color: white;
            margin: 0;
            padding: 0;
            display: flex;
            flex-direction: column;
            align-items: center;
            min-height: 100vh;
        }}
        header {{
            background-color: #1a1a1a;
            width: 100%;
            padding: 20px 0;
            text-align: center;
            margin-bottom: 30px;
        }}
        h1 {{
            margin: 0;
            color: #eee;
        }}
        .subtitle {{
            color: #aaa;
            margin-top: 5px;
        }}
        .container {{
            display: flex;
            flex-direction: column;
            align-items: center;
            max-width: 800px;
            width: 100%;
            padding: 0 20px;
        }}
        .dial-container {{
            margin-bottom: 20px;
            position: relative;
        }}
        .mode-controls {{
            display: flex;
            gap: 20px;
            margin: 20px 0;
        }}
        .mode-btn {{
            background-color: #444;
            color: white;
            border: none;
            padding: 10px 15px;
            border-radius: 5px;
            cursor: pointer;
            transition: background-color 0.3s;
        }}
        .mode-btn:hover {{
            background-color: #555;
        }}
        #dial {{
            width: 250px;
            height: 250px;
            cursor: pointer;
            transition: transform 0.5s ease-in-out;
        }}
        #knob {{
            transition: transform 1s ease-in-out;
        }}
        .info-panel {{
            background-color: #383838;
            border-radius: 10px;
            padding: 20px;
            width: 100%;
            max-width: 600px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.3);
            margin-top: 20px;
            transition: background-color 0.5s;
        }}
        .mode-title {{
            font-size: 24px;
            margin-bottom: 10px;
        }}
        .mode-description {{
            margin-bottom: 15px;
            color: #ddd;
        }}
        .features-list {{
            list-style-type: none;
            padding-left: 0;
        }}
        .features-list li {{
            padding: 8px 0;
            position: relative;
            padding-left: 25px;
        }}
        .features-list li:before {{
            content: '✓';
            position: absolute;
            left: 0;
            color: #9ec5fe;
        }}
        .instructions {{
            background-color: rgba(0,0,0,0.2);
            padding: 15px;
            border-radius: 5px;
            margin-top: 30px;
            text-align: center;
        }}
        .dial-label {{
            position: absolute;
            width: 250px;
            text-align: center;
            bottom: -30px;
            font-weight: bold;
            color: #eee;
            font-size: 16px;
            transition: opacity 0.3s;
        }}
        .creaking-animation {{
            position: absolute;
            width: 250px;
            height: 250px;
            top: 0;
            left: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            pointer-events: none;
            opacity: 0;
        }}
        .creak-text {{
            font-family: 'Comic Sans MS', cursive;
            font-size: 40px;
            color: #ffcc00;
            transform: rotate(-15deg);
            text-shadow: 2px 2px 5px rgba(0,0,0,0.5);
        }}
        footer {{
            margin-top: auto;
            padding: 20px;
            background-color: #1a1a1a;
            width: 100%;
            text-align: center;
            color: #888;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <header>
        <h1>PyWrite Mode Switcher</h1>
        <div class="subtitle">Fiction | Screenwriting | Code</div>
    </header>
    <div class="container">
        <div class="dial-container">
            {svg_content}
            <div class="dial-label">Current Mode: <span id="mode-name">Code</span></div>
            <div class="creaking-animation" id="creak-anim">
                <div class="creak-text">CREAAAK!</div>
            </div>
        </div>
        
        <div class="mode-controls">
            <button class="mode-btn" onclick="setMode(0)">Fiction</button>
            <button class="mode-btn" onclick="setMode(1)">Screenwriting</button>
            <button class="mode-btn" onclick="setMode(2)">Code</button>
        </div>
        
        <div class="info-panel" id="info-panel">
            <div class="mode-title" id="info-title">Code Mode</div>
            <div class="mode-description" id="info-description">
                Optimized for writing and editing programming code
            </div>
            <ul class="features-list" id="features-list">
                <li>Syntax highlighting</li>
                <li>Intelligent code assistance</li>
                <li>Documentation helpers</li>
                <li>Testing and debugging tools</li>
            </ul>
        </div>
        
        <div class="instructions">
            Click the dial or use the buttons to switch between modes<br>
            <small>Listen for the satisfying creaking sound when changing modes!</small>
        </div>
    </div>
    
    <footer>
        PyWrite - The multi-modal writing environment &copy; 2025
    </footer>
    
    <script>
        // Mode data
        const modes = {modes_json};
        
        // Current mode (0=Fiction, 1=Screenwriting, 2=Code)
        let currentMode = 2;
        
        // DOM elements
        const dial = document.querySelector('svg');
        const knob = document.getElementById('knob');
        const modeName = document.getElementById('mode-name');
        const infoPanel = document.getElementById('info-panel');
        const infoTitle = document.getElementById('info-title');
        const infoDescription = document.getElementById('info-description');
        const featuresList = document.getElementById('features-list');
        const creakAnim = document.getElementById('creak-anim');
        
        // Rotations for each mode (in degrees)
        const rotations = [0, 120, 240];
        
        // Set initial knob position
        knob.setAttribute('transform', `rotate(${{rotations[currentMode]}}, 100, 100)`);
        updateInfoPanel();
        
        // Create creaking sound
        const creakSound = new Audio();
        creakSound.src = 'data:audio/wav;base64,UklGRigAAABXQVZFZm10IBAAAAABAAEARKwAAIhYAQACABAAZGF0YQQAAAAAAA=='; // Empty sound as placeholder
        
        // Function to play creaking sound and show animation
        function playCreak() {{
            console.log("*CREAKING SOUND*");
            
            // Show creak animation
            creakAnim.style.opacity = 1;
            setTimeout(() => {{
                creakAnim.style.opacity = 0;
            }}, 1000);
            
            // Play sound (in a real implementation)
            try {{
                creakSound.play();
            }} catch (e) {{
                console.log("Sound could not be played:", e);
            }}
        }}
        
        // Function to update the info panel
        function updateInfoPanel() {{
            const mode = modes[currentMode];
            
            // Update text content
            infoTitle.textContent = mode.name + " Mode";
            infoDescription.textContent = mode.description;
            
            // Update features list
            featuresList.innerHTML = '';
            mode.features.forEach(feature => {{
                const li = document.createElement('li');
                li.textContent = feature;
                featuresList.appendChild(li);
            }});
            
            // Update color
            infoPanel.style.backgroundColor = mode.color;
            
            // Update mode name
            modeName.textContent = mode.name;
        }}
        
        // Function to set mode directly
        function setMode(modeIndex) {{
            if (modeIndex === currentMode) return;
            
            currentMode = modeIndex;
            
            // Play sound
            playCreak();
            
            // Animate knob rotation
            knob.setAttribute('transform', `rotate(${{rotations[currentMode]}}, 100, 100)`);
            
            // Update info panel
            updateInfoPanel();
        }}
        
        // Add click event to change mode
        dial.addEventListener('click', () => {{
            // Increment mode (cycle through modes)
            setMode((currentMode + 1) % 3);
        }});
    </script>
</body>
</html>""".replace("{modes_json}", str(modes))
    
    # Create a temporary HTML file
    temp_html = os.path.join(tempfile.gettempdir(), 'pywrite_mode_switcher_demo.html')
    with open(temp_html, 'w') as f:
        f.write(html_content)
    
    # Open in web browser
    webbrowser.open('file://' + temp_html)
    
    return temp_html

def main():
    """Main function to run the demo."""
    print("====================================")
    print("  PyWrite Mode Switcher Demo")
    print("====================================")
    print("Launching interactive demo in your web browser...")
    
    html_path = create_html_demo()
    
    print(f"\nDemo page created at: {html_path}")
    print("If the browser doesn't open automatically, you can open this file manually.")
    print("\nIn the demo, you can:")
    print("1. Click on the dial to rotate it")
    print("2. Use the buttons to switch directly to a specific mode")
    print("3. See information about each mode update in real-time")
    print("\nPress Ctrl+C to exit.")

if __name__ == "__main__":
    main()