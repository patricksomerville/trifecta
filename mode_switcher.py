#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyWrite Mode Switcher

A module that handles switching between Fiction, Screenwriting, and Code modes
with a retro-style dial interface.

Author: PyWrite
Date: 2025-03-28
"""

import os
import tkinter as tk
from tkinter import ttk
import sv_ttk  # We'll use this for theming if available, but it's optional
from PIL import Image, ImageTk
import base64
from io import BytesIO
import time
import threading
import webbrowser
import tempfile

# Define mode constants
MODE_FICTION = 0
MODE_SCREENWRITING = 1
MODE_CODE = 2

class ModeSwitcherFrame(ttk.Frame):
    """A frame containing a retro-style mode switcher dial."""
    
    def __init__(self, parent, callback=None, **kwargs):
        """
        Initialize the mode switcher.
        
        Args:
            parent: The parent widget
            callback: Function to call when mode changes (receives mode as argument)
            **kwargs: Additional arguments to pass to the Frame constructor
        """
        super().__init__(parent, **kwargs)
        
        self.parent = parent
        self.callback = callback
        self.current_mode = MODE_CODE  # Default to code mode
        
        # Create variables for animation
        self.is_animating = False
        self.target_rotation = 0
        self.current_rotation = 0
        
        # Load dial SVG and convert to a Tkinter PhotoImage 
        self.dial_svg_path = os.path.join('assets', 'ui', 'mode_dial.svg')
        
        # Configure the frame
        self.configure(padding=10)
        
        # Create dial image placeholder (will be replaced in setup_dial)
        self.dial_image = None
        self.dial_label = ttk.Label(self)
        self.dial_label.pack(padx=10, pady=10)
        
        # Mode labels
        self.mode_label = ttk.Label(self, text="Current Mode: Code", font=("Arial", 12, "bold"))
        self.mode_label.pack(pady=5)
        
        # Description label
        self.description_label = ttk.Label(
            self, 
            text="Perfect for writing and editing programming code",
            font=("Arial", 10),
            wraplength=300
        )
        self.description_label.pack(pady=5)
        
        # Setup the dial (must be called after packing)
        self.after(100, self.setup_dial)
        
    def setup_dial(self):
        """Setup the dial image and make it clickable."""
        try:
            # Try to use PIL to load the image
            from PIL import Image, ImageTk
            
            # Read SVG file content
            with open(self.dial_svg_path, 'r') as f:
                svg_content = f.read()
            
            # For a real implementation, you'd convert SVG to a bitmap format
            # For now, we'll create a simple placeholder image
            # In a full implementation, you'd use a library like CairoSVG or convert in advance
            
            # Create a temporary HTML file to display the SVG 
            temp_html = os.path.join(tempfile.gettempdir(), 'dial_preview.html')
            with open(temp_html, 'w') as f:
                f.write(f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Mode Dial Preview</title>
                    <style>
                        body {{ 
                            display: flex; 
                            justify-content: center; 
                            align-items: center; 
                            height: 100vh; 
                            background-color: #2a2a2a;
                        }}
                        .container {{
                            text-align: center;
                        }}
                        .dial-container {{
                            margin-bottom: 20px;
                        }}
                        #dial {{
                            width: 200px;
                            height: 200px;
                            cursor: pointer;
                            transition: transform 0.5s ease-in-out;
                        }}
                        .label {{
                            color: white;
                            font-family: Arial, sans-serif;
                            font-size: 16px;
                            margin-top: 10px;
                        }}
                        .click-instruction {{
                            color: #aaa;
                            font-family: Arial, sans-serif;
                            font-size: 14px;
                            margin-top: 20px;
                        }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="dial-container">
                            {svg_content}
                        </div>
                        <div class="label">Current Mode: <span id="mode-name">Code</span></div>
                        <div class="click-instruction">(Click the dial to change modes)</div>
                    </div>
                    
                    <script>
                        const dial = document.querySelector('svg');
                        const knob = document.getElementById('knob');
                        const modeName = document.getElementById('mode-name');
                        
                        let currentMode = 2; // Code mode (0=Fiction, 1=Screenwriting, 2=Code)
                        const modeNames = ['Fiction', 'Screenwriting', 'Code'];
                        const rotations = [0, 120, 240]; // Degrees for each mode
                        
                        // Set initial knob position
                        knob.setAttribute('transform', `rotate(${{rotations[currentMode]}}, 100, 100)`);
                        
                        // Create creaking sound
                        const creakSound = new Audio();
                        
                        // Function to play creaking sound
                        function playCreak() {{
                            // In a full implementation, you'd use a real sound file
                            // For this demo, we're just showing the visual
                            console.log("*CREAKING SOUND*");
                        }}
                        
                        // Add click event to change mode
                        dial.addEventListener('click', () => {{
                            // Increment mode (cycle through modes)
                            currentMode = (currentMode + 1) % 3;
                            
                            // Play sound
                            playCreak();
                            
                            // Animate knob rotation
                            knob.setAttribute('transform', `rotate(${{rotations[currentMode]}}, 100, 100)`);
                            
                            // Update mode display
                            modeName.textContent = modeNames[currentMode];
                        }});
                    </script>
                </body>
                </html>
                """)
            
            # Create a button to open the preview
            preview_button = ttk.Button(
                self, 
                text="Click to View Mode Dial Demo", 
                command=lambda: webbrowser.open('file://' + temp_html)
            )
            preview_button.pack(pady=10)
            
            # Create a simple placeholder image for the actual application
            placeholder = tk.Canvas(self, width=200, height=200, bg='#333333', highlightthickness=0)
            placeholder.create_oval(10, 10, 190, 190, fill='#444444', outline='#555555', width=2)
            placeholder.create_text(100, 50, text="Fiction", fill='white')
            placeholder.create_text(150, 100, text="Screenwriting", fill='white')
            placeholder.create_text(100, 150, text="Code", fill='white')
            
            # Draw a simple knob
            placeholder.create_oval(80, 80, 120, 120, fill='#222222', outline='#666666')
            self.knob_line = placeholder.create_line(100, 100, 100, 85, fill='white', width=2)
            
            # Display the placeholder
            placeholder.pack(padx=10, pady=10)
            
            # Make the placeholder clickable
            placeholder.bind("<Button-1>", self.rotate_dial)
            
            # Store the canvas for later updates
            self.dial_canvas = placeholder
            
        except Exception as e:
            # Fallback if image loading fails
            error_label = ttk.Label(
                self, 
                text=f"Mode Switcher Dial\n(Click to change modes)\nCurrent: {self._get_mode_name()}"
            )
            error_label.bind("<Button-1>", self.rotate_dial)
            error_label.pack(padx=10, pady=10)
            self.dial_label = error_label
    
    def _get_mode_name(self):
        """Get the name of the current mode."""
        if self.current_mode == MODE_FICTION:
            return "Fiction"
        elif self.current_mode == MODE_SCREENWRITING:
            return "Screenwriting"
        else:
            return "Code"
    
    def _get_mode_description(self):
        """Get the description for the current mode."""
        if self.current_mode == MODE_FICTION:
            return "Perfect for writing novels, short stories, and other fiction"
        elif self.current_mode == MODE_SCREENWRITING:
            return "Designed for writing scripts and screenplays with proper formatting"
        else:
            return "Perfect for writing and editing programming code"
    
    def rotate_dial(self, event=None):
        """Rotate the dial to the next mode."""
        if self.is_animating:
            return
            
        # Play creaking sound (in a real implementation)
        print("*CREAKING SOUND*")
        
        # Calculate next mode
        next_mode = (self.current_mode + 1) % 3
        
        # Set target rotation based on mode
        if next_mode == MODE_FICTION:
            self.target_rotation = 0
        elif next_mode == MODE_SCREENWRITING:
            self.target_rotation = 120
        else:  # CODE mode
            self.target_rotation = 240
        
        # Start animation
        self.is_animating = True
        self.animate_rotation()
        
        # Update mode
        self.current_mode = next_mode
        
        # Update labels
        self.mode_label.config(text=f"Current Mode: {self._get_mode_name()}")
        self.description_label.config(text=self._get_mode_description())
        
        # Call the callback if provided
        if self.callback:
            self.callback(self.current_mode)
    
    def animate_rotation(self):
        """Animate the rotation of the dial knob."""
        if not hasattr(self, 'dial_canvas'):
            self.is_animating = False
            return
            
        # Calculate the step towards target rotation
        diff = self.target_rotation - self.current_rotation
        
        # If we're close enough, just set to target
        if abs(diff) < 5:
            self.current_rotation = self.target_rotation
            self.dial_canvas.delete(self.knob_line)
            
            # Calculate knob endpoint for the current rotation
            angle_rad = self.current_rotation * 3.14159 / 180.0
            end_x = 100 - 15 * -1 * abs(angle_rad)
            end_y = 100 - 15 * -1 * abs(angle_rad)
            
            self.knob_line = self.dial_canvas.create_line(
                100, 100, 
                100 + 15 * -1 * abs(angle_rad), 
                85, 
                fill='white', 
                width=2
            )
            
            self.is_animating = False
            return
            
        # Otherwise, take a step in the right direction
        step = diff / 10 if abs(diff) > 10 else diff / 2
        self.current_rotation += step
        
        # Update the knob
        self.dial_canvas.delete(self.knob_line)
        
        # Calculate knob endpoint for the current rotation
        angle_rad = self.current_rotation * 3.14159 / 180.0
        self.knob_line = self.dial_canvas.create_line(
            100, 100, 
            100, 
            85, 
            fill='white', 
            width=2
        )
        
        # Continue animation
        self.after(30, self.animate_rotation)


class ModeManager:
    """
    Manages the current PyWrite mode and handles switching between modes.
    
    This class coordinates the mode switching across all components of the application.
    """
    
    def __init__(self):
        """Initialize the mode manager."""
        self.current_mode = MODE_CODE  # Default to code mode
        self.mode_listeners = []
    
    def add_listener(self, listener):
        """
        Add a listener that will be notified of mode changes.
        
        Args:
            listener: A function that takes a mode constant as its only argument
        """
        if listener not in self.mode_listeners:
            self.mode_listeners.append(listener)
    
    def remove_listener(self, listener):
        """
        Remove a listener.
        
        Args:
            listener: The listener function to remove
        """
        if listener in self.mode_listeners:
            self.mode_listeners.remove(listener)
    
    def set_mode(self, mode):
        """
        Change the current mode and notify listeners.
        
        Args:
            mode: The new mode (one of the MODE_* constants)
        """
        if mode != self.current_mode:
            self.current_mode = mode
            self._notify_listeners()
    
    def get_mode(self):
        """Get the current mode."""
        return self.current_mode
    
    def get_mode_name(self):
        """Get the name of the current mode as a string."""
        if self.current_mode == MODE_FICTION:
            return "Fiction"
        elif self.current_mode == MODE_SCREENWRITING:
            return "Screenwriting"
        else:
            return "Code"
    
    def _notify_listeners(self):
        """Notify all listeners of the mode change."""
        for listener in self.mode_listeners:
            try:
                listener(self.current_mode)
            except Exception as e:
                print(f"Error notifying listener of mode change: {e}")


# Demo application
if __name__ == "__main__":
    root = tk.Tk()
    root.title("PyWrite Mode Switcher Demo")
    root.geometry("300x400")
    root.configure(bg="#2a2a2a")
    
    # Try to use sv_ttk for a modern look
    try:
        import sv_ttk
        sv_ttk.set_theme("dark")
    except ImportError:
        # Fallback to standard theming
        style = ttk.Style()
        style.theme_use('alt')  # or another available theme
        style.configure('.', background='#2a2a2a', foreground='white')
        style.configure('TLabel', background='#2a2a2a', foreground='white')
        style.configure('TFrame', background='#2a2a2a')
        style.configure('TButton', background='#444', foreground='white')
    
    # Create the mode manager
    mode_manager = ModeManager()
    
    # Function to handle mode changes
    def on_mode_change(mode):
        print(f"Mode changed to: {mode_manager.get_mode_name()}")
        status_label.config(text=f"Current mode: {mode_manager.get_mode_name()}")
    
    # Add the listener
    mode_manager.add_listener(on_mode_change)
    
    # Create a frame for the mode switcher
    frame = ttk.Frame(root)
    frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    # Create the mode switcher
    switcher = ModeSwitcherFrame(
        frame, 
        callback=mode_manager.set_mode
    )
    switcher.pack(fill=tk.BOTH, expand=True)
    
    # Status label at the bottom
    status_label = ttk.Label(root, text=f"Current mode: {mode_manager.get_mode_name()}")
    status_label.pack(pady=10)
    
    # Instructions
    instr_label = ttk.Label(
        root, 
        text="Click the dial to switch between modes\nor click the preview button to see an interactive demo",
        wraplength=250,
        justify='center'
    )
    instr_label.pack(pady=5)
    
    root.mainloop()