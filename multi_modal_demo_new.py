#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyWrite Multi-Modal Demo

A demonstration of the PyWrite multi-modal system that combines:
- The retro-style mode switcher dial
- Mode-specific content templates and functionality
- Integration with the Sidecar assistant

Author: PyWrite
Date: 2023-3-28
"""

import os
import sys
import tempfile
import datetime
import webbrowser

def create_multi_modal_demo():
    """Generate an HTML page that showcases the multi-modal system."""
    
    # Get current date in format YYYY-M-D (avoid leading zeros)
    today = datetime.datetime.now().strftime("%Y-%-m-%-d")
    
    # Create the HTML content with dynamic date
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>PyWrite Multi-Modal System</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background-color: #2a2a2a;
            color: white;
            margin: 0;
            padding: 0;
            display: flex;
            flex-direction: column;
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
            max-width: 1200px;
            margin: 0 auto;
            gap: 20px;
            padding: 0 20px;
            flex: 1;
        }}
        .left-panel {{
            width: 300px;
            display: flex;
            flex-direction: column;
        }}
        .dial-container {{
            background-color: #333;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            margin-bottom: 20px;
        }}
        .dial {{
            width: 200px;
            height: 200px;
            margin: 0 auto;
            position: relative;
            background-color: #444;
            border-radius: 50%;
            border: 5px solid #222;
            box-shadow: 0 5px 15px rgba(0,0,0,0.5);
            cursor: pointer;
        }}
        .dial-label {{
            width: 200px;
            text-align: center;
            margin-top: 10px;
            font-weight: bold;
            color: #eee;
        }}
        .dial-tick {{
            position: absolute;
            width: 4px;
            height: 15px;
            background-color: #ddd;
        }}
        .dial-tick-fiction {{
            top: 10px;
            left: 98px;
        }}
        .dial-tick-screenwriting {{
            transform: rotate(120deg);
            transform-origin: center 100px;
            top: 10px;
            left: 98px;
        }}
        .dial-tick-code {{
            transform: rotate(240deg);
            transform-origin: center 100px;
            top: 10px;
            left: 98px;
        }}
        .dial-text {{
            position: absolute;
            color: #ddd;
            font-size: 12px;
            font-weight: bold;
        }}
        .dial-text-fiction {{
            top: 20px;
            left: 50%;
            transform: translateX(-50%);
        }}
        .dial-text-screenwriting {{
            top: 100px;
            right: 0;
            transform: rotate(0deg);
        }}
        .dial-text-code {{
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
        }}
        .knob {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 60px;
            height: 60px;
            background-color: #333;
            border-radius: 50%;
            border: 2px solid #555;
            box-shadow: inset 0 2px 5px rgba(255,255,255,0.2);
        }}
        .knob::after {{
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -100%);
            width: 4px;
            height: 20px;
            background-color: #ddd;
        }}
        .sidecar {{
            flex: 1;
            background-color: #333;
            padding: 20px;
            border-radius: 10px;
        }}
        .sidecar-header {{
            display: flex;
            align-items: center;
            margin-bottom: 15px;
        }}
        .sidecar-icon {{
            width: 30px;
            height: 30px;
            background-color: #4a6da7;
            border-radius: 50%;
            margin-right: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
        }}
        .sidecar-title {{
            font-size: 18px;
            font-weight: bold;
        }}
        .sidecar-content {{
            max-height: 400px;
            overflow-y: auto;
        }}
        .chat-message {{
            margin-bottom: 15px;
        }}
        .chat-user {{
            background-color: #2c5d9e;
            padding: 10px 15px;
            border-radius: 18px 18px 18px 0;
            display: inline-block;
            max-width: 80%;
        }}
        .chat-assistant {{
            background-color: #444;
            padding: 10px 15px;
            border-radius: 18px 18px 0 18px;
            display: inline-block;
            max-width: 80%;
            margin-left: auto;
            text-align: right;
        }}
        .prompt-suggestions {{
            margin-top: 20px;
        }}
        .prompt-title {{
            font-size: 14px;
            color: #aaa;
            margin-bottom: 10px;
        }}
        .prompt-button {{
            background-color: #444;
            border: none;
            color: #ddd;
            padding: 8px 12px;
            border-radius: 15px;
            margin: 0 5px 8px 0;
            cursor: pointer;
            font-size: 12px;
        }}
        .prompt-button:hover {{
            background-color: #555;
        }}
        .main-content {{
            flex: 1;
            display: flex;
            flex-direction: column;
        }}
        .toolbar {{
            background-color: #333;
            padding: 10px 15px;
            border-radius: 8px 8px 0 0;
            display: flex;
            gap: 10px;
        }}
        .toolbar-button {{
            background-color: transparent;
            border: none;
            color: #ddd;
            padding: 5px 10px;
            cursor: pointer;
            font-size: 14px;
            border-radius: 4px;
        }}
        .toolbar-button:hover {{
            background-color: #444;
        }}
        .active-button {{
            background-color: #444;
        }}
        .editor-container {{
            flex: 1;
            background-color: #1e1e1e;
            border-radius: 0 0 8px 8px;
            padding: 10px;
            display: flex;
            flex-direction: column;
        }}
        .file-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
            color: #aaa;
            font-size: 12px;
        }}
        .editor {{
            flex: 1;
            background-color: #1e1e1e;
            border: 1px solid #333;
            padding: 10px;
            font-family: monospace;
            white-space: pre;
            overflow: auto;
            color: #d4d4d4;
            height: 400px;
        }}
        footer {{
            margin-top: 30px;
            padding: 20px;
            background-color: #1a1a1a;
            width: 100%;
            text-align: center;
            color: #888;
            font-size: 12px;
        }}
        /* Mode-specific styles */
        .fiction-theme .toolbar {{
            background-color: #2c3e50;
        }}
        .fiction-theme .active-button {{
            background-color: #34495e;
        }}
        .fiction-theme .editor-container {{
            background-color: #1c2833;
        }}
        .fiction-theme .sidecar-icon {{
            background-color: #2980b9;
        }}
        
        .screenwriting-theme .toolbar {{
            background-color: #614a19;
        }}
        .screenwriting-theme .active-button {{
            background-color: #7d6024;
        }}
        .screenwriting-theme .editor-container {{
            background-color: #32281e;
        }}
        .screenwriting-theme .sidecar-icon {{
            background-color: #d4ac0d;
        }}
        
        .code-theme .toolbar {{
            background-color: #1e3b2c;
        }}
        .code-theme .active-button {{
            background-color: #2a5a3e;
        }}
        .code-theme .editor-container {{
            background-color: #0f241a;
        }}
        .code-theme .sidecar-icon {{
            background-color: #27ae60;
        }}
        .file-tabs {{
            display: flex;
            background-color: #252525;
            margin-bottom: 10px;
        }}
        .file-tab {{
            padding: 5px 15px;
            font-size: 14px;
            cursor: pointer;
            border-right: 1px solid #333;
        }}
        .file-tab.active {{
            background-color: #1e1e1e;
            border-bottom: 2px solid #4a9eff;
        }}
        .creak-animation {{
            position: absolute;
            width: 250px;
            height: 250px;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
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
        .sidebar {{
            flex: 0 0 250px;
            background-color: #333;
            border-radius: 8px;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            margin-left: 20px;
        }}
        .sidebar-header {{
            background-color: #252525;
            padding: 10px 15px;
            font-weight: bold;
        }}
        .sidebar-content {{
            padding: 10px 15px;
            flex: 1;
            overflow-y: auto;
        }}
        .sidebar-tab {{
            padding: 8px 10px;
            margin-bottom: 5px;
            cursor: pointer;
            border-radius: 4px;
        }}
        .sidebar-tab:hover {{
            background-color: #444;
        }}
        .sidebar-tab.active {{
            background-color: #444;
        }}
        .empty-message {{
            color: #888;
            font-style: italic;
            margin-top: 10px;
        }}
    </style>
</head>
<body class="code-theme" id="app-body">
    <header>
        <h1>PyWrite Multi-Modal System</h1>
        <div class="subtitle">One tool for all your writing needs</div>
    </header>
    
    <div class="container">
        <div class="left-panel">
            <div class="dial-container">
                <div class="dial" id="mode-dial">
                    <div class="dial-tick dial-tick-fiction"></div>
                    <div class="dial-tick dial-tick-screenwriting"></div>
                    <div class="dial-tick dial-tick-code"></div>
                    
                    <div class="dial-text dial-text-fiction">Fiction</div>
                    <div class="dial-text dial-text-screenwriting">Screenwriting</div>
                    <div class="dial-text dial-text-code">Code</div>
                    
                    <div class="knob" id="knob" style="transform: translate(-50%, -50%) rotate(240deg)"></div>
                    
                    <div class="creak-animation" id="creak-anim">
                        <div class="creak-text">CREAAAK!</div>
                    </div>
                </div>
                <div class="dial-label">Current Mode: <span id="mode-name">Code</span></div>
            </div>
            
            <div class="sidecar">
                <div class="sidecar-header">
                    <div class="sidecar-icon">S</div>
                    <div class="sidecar-title">Sidecar Assistant</div>
                </div>
                
                <div class="sidecar-content">
                    <div class="chat-message">
                        <div class="chat-user">
                            What's the best way to structure my code?
                        </div>
                    </div>
                    
                    <div class="chat-message">
                        <div class="chat-assistant">
                            For a well-organized Python project, I recommend using:
                            <br><br>
                            1. Separate modules for related functionality
                            <br>
                            2. Classes to encapsulate complex behavior
                            <br>
                            3. Clear docstrings for all functions
                            <br>
                            4. Type hints for better readability
                            <br><br>
                            Would you like me to help you refactor your current code?
                        </div>
                    </div>
                    
                    <div class="prompt-suggestions">
                        <div class="prompt-title">Ask Sidecar about:</div>
                        <div id="prompt-buttons-container">
                            <button class="prompt-button">How can I optimize this function?</button>
                            <button class="prompt-button">Help me debug this error</button>
                            <button class="prompt-button">How can I make this code more readable?</button>
                            <button class="prompt-button">Can you suggest comments for this?</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="main-content">
            <div class="toolbar" id="toolbar">
                <button class="toolbar-button active-button">Run</button>
                <button class="toolbar-button">Debug</button>
                <button class="toolbar-button">Format</button>
                <button class="toolbar-button">Comments</button>
            </div>
            
            <div class="editor-container">
                <div class="file-tabs">
                    <div class="file-tab active">main.py</div>
                    <div class="file-tab">utils.py</div>
                </div>
                
                <div class="file-header">
                    <span>Python File</span>
                    <span>Ln 1, Col 1</span>
                </div>
                
                <div class="editor" id="editor">#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Description: A Python script
Author: PyWrite
Date: {today}
"""

def main():
    """Main function."""
    print("Hello, World!")

if __name__ == "__main__":
    main()
</div>
            </div>
        </div>
        
        <div class="sidebar">
            <div class="sidebar-header">Code Explorer</div>
            <div class="sidebar-content">
                <div class="sidebar-tab active">Files</div>
                <div class="sidebar-tab">Outline</div>
                <div class="sidebar-tab">Console</div>
                
                <div class="empty-message" id="sidebar-content">
                    No files in the current directory.
                </div>
            </div>
        </div>
    </div>
    
    <footer>
        PyWrite - The multi-modal writing environment &copy; 2023
    </footer>
    
    <script>
        // Mode definitions
        const MODES = {{
            FICTION: 0,
            SCREENWRITING: 1,
            CODE: 2
        }};
        
        const modeData = [
            {{
                name: "Fiction",
                themeClass: "fiction-theme",
                toolbarButtons: ["Character", "Plot", "Settings", "Notes"],
                sidebarTabs: ["Characters", "Plot Points", "Settings"],
                sidebarContent: "No characters created yet.",
                sidecarPrompts: [
                    "Help me develop this character further",
                    "Can you suggest some plot twists?",
                    "How can I make this dialogue more realistic?",
                    "Can you help me describe this setting?"
                ],
                editorContent: `# Untitled Fiction

By: Author Name
Date: {today}

---

## Chapter 1

[Your story begins here...]
`
            }},
            {{
                name: "Screenwriting",
                themeClass: "screenwriting-theme",
                toolbarButtons: ["Scene", "Character", "Action", "Transition"],
                sidebarTabs: ["Scenes", "Characters", "Beat Sheet"],
                sidebarContent: "No scenes created yet.",
                sidecarPrompts: [
                    "How do I format a montage?",
                    "Can you suggest a good establishing shot?",
                    "Help me make this dialogue more concise",
                    "How can I describe this action sequence?"
                ],
                editorContent: `Title: UNTITLED SCREENPLAY
Credit: Written by
Author: Your Name
Draft date: {today}

/*
    This screenplay follows the Fountain syntax.
    For more information, visit fountain.io
*/

# Act 1

== Opening Scene ==

EXT. LOCATION - DAY

[Description of the scene goes here.]

CHARACTER
(action)
Dialogue goes here.
`
            }},
            {{
                name: "Code",
                themeClass: "code-theme",
                toolbarButtons: ["Run", "Debug", "Format", "Comments"],
                sidebarTabs: ["Files", "Outline", "Console"],
                sidebarContent: "No files in the current directory.",
                sidecarPrompts: [
                    "How can I optimize this function?",
                    "Help me debug this error",
                    "How can I make this code more readable?",
                    "Can you suggest comments for this?"
                ],
                editorContent: `#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Description: A Python script
Author: PyWrite
Date: {today}
"""

def main():
    """Main function."""
    print("Hello, World!")

if __name__ == "__main__":
    main()
`
            }}
        ];
        
        // Current mode (default: CODE)
        let currentMode = MODES.CODE;
        let knobRotation = 240; // Degrees
        
        // DOM elements
        const modeDial = document.getElementById('mode-dial');
        const knob = document.getElementById('knob');
        const modeName = document.getElementById('mode-name');
        const appBody = document.getElementById('app-body');
        const toolbar = document.getElementById('toolbar');
        const editor = document.getElementById('editor');
        const promptButtonsContainer = document.getElementById('prompt-buttons-container');
        const creakAnim = document.getElementById('creak-anim');
        const sidebarContent = document.getElementById('sidebar-content');
        
        // Function to update the UI based on the current mode
        function updateUI() {{
            const mode = modeData[currentMode];
            
            // Update mode name
            modeName.textContent = mode.name;
            
            // Update theme
            appBody.className = mode.themeClass;
            
            // Update toolbar buttons
            let toolbarHtml = '';
            mode.toolbarButtons.forEach((btn, index) => {{
                const activeClass = index === 0 ? 'active-button' : '';
                toolbarHtml += `<button class="toolbar-button ${{activeClass}}">${{btn}}</button>`;
            }});
            toolbar.innerHTML = toolbarHtml;
            
            // Update editor content
            editor.textContent = mode.editorContent;
            
            // Update sidecar prompt suggestions
            let promptsHtml = '';
            mode.sidecarPrompts.forEach(prompt => {{
                promptsHtml += `<button class="prompt-button">${{prompt}}</button>`;
            }});
            promptButtonsContainer.innerHTML = promptsHtml;
            
            // Update sidebar content
            sidebarContent.textContent = mode.sidebarContent;
        }}
        
        // Function to play creaking sound animation
        function playCreak() {{
            console.log("*CREAKING SOUND*");
            
            // Show creak animation
            creakAnim.style.opacity = 1;
            setTimeout(() => {{
                creakAnim.style.opacity = 0;
            }}, 1000);
        }}
        
        // Function to rotate the dial knob
        function rotateKnob(degrees) {{
            knobRotation = degrees;
            knob.style.transform = `translate(-50%, -50%) rotate(${{degrees}}deg)`;
        }}
        
        // Function to switch modes
        function switchMode(newMode) {{
            if (newMode === currentMode) return;
            
            currentMode = newMode;
            
            // Play creaking sound
            playCreak();
            
            // Rotate knob based on mode
            if (currentMode === MODES.FICTION) {{
                rotateKnob(0);
            }} else if (currentMode === MODES.SCREENWRITING) {{
                rotateKnob(120);
            }} else {{
                rotateKnob(240);
            }}
            
            // Update UI
            updateUI();
        }}
        
        // Add click event to the dial
        modeDial.addEventListener('click', () => {{
            // Cycle to the next mode
            const nextMode = (currentMode + 1) % 3;
            switchMode(nextMode);
        }});
        
        // Initialize the UI
        updateUI();
    </script>
</body>
</html>"""
    
    # Create a temporary HTML file
    temp_html = os.path.join(tempfile.gettempdir(), 'pywrite_multi_modal_demo.html')
    with open(temp_html, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    # Open in web browser
    webbrowser.open('file://' + temp_html)
    
    return temp_html

def main():
    """Main function to run the demo."""
    print("====================================")
    print("  PyWrite Multi-Modal System Demo")
    print("====================================")
    print("Launching interactive demo in your web browser...")
    
    html_path = create_multi_modal_demo()
    
    print(f"\nDemo page created at: {html_path}")
    print("If the browser doesn't open automatically, you can open this file manually.")
    print("\nIn the demo, you can:")
    print("1. Click on the retro dial to rotate it and switch between modes")
    print("2. See how the interface adapts based on the current mode")
    print("3. Observe how the Sidecar assistant provides mode-specific assistance")
    print("\nPress Ctrl+C to exit.")

if __name__ == "__main__":
    main()