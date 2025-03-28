#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyWrite Voice Navigation

Provides hands-free voice command functionality for coding navigation in PyWrite
using OpenAI's speech-to-text and natural language understanding capabilities.

This module allows users to:
- Navigate through code with voice commands
- Execute common actions like saving, opening, and running files
- Control the editor interface hands-free
- Switch between PyWrite modes using voice

Author: PyWrite
Date: 2025-03-28
"""

import os
import json
import time
import base64
import threading
import tempfile
import subprocess
import urllib.request
import urllib.parse
import urllib.error
import http.client
from datetime import datetime

# Command categories and their associated actions
NAVIGATION_COMMANDS = {
    "goto_line": ["go to line", "navigate to line", "jump to line"],
    "next_page": ["next page", "page down", "scroll down"],
    "prev_page": ["previous page", "page up", "scroll up"],
    "start_of_file": ["go to start", "beginning of file", "top of file"],
    "end_of_file": ["go to end", "end of file", "bottom of file"],
    "find_text": ["find", "search for", "locate"]
}

FILE_COMMANDS = {
    "open_file": ["open file", "load file", "open", "load"],
    "save_file": ["save file", "save", "write to file"],
    "save_as": ["save as", "save file as", "write to new file"],
    "new_file": ["new file", "create file", "start new file"],
    "close_file": ["close file", "close", "exit file"]
}

RUN_COMMANDS = {
    "run_code": ["run code", "execute code", "run script", "execute script"],
    "debug_code": ["debug code", "start debugging", "debug", "run debug"],
    "stop_execution": ["stop execution", "stop running", "halt execution"]
}

MODE_COMMANDS = {
    "switch_fiction": ["switch to fiction mode", "fiction mode", "writing mode"],
    "switch_screenwriting": ["switch to screenwriting mode", "screenwriting mode", "screenplay mode"],
    "switch_code": ["switch to code mode", "code mode", "programming mode"]
}

EDIT_COMMANDS = {
    "undo": ["undo", "undo last action", "go back"],
    "redo": ["redo", "redo last action", "go forward"],
    "copy": ["copy", "copy selection", "copy text"],
    "cut": ["cut", "cut selection", "cut text"],
    "paste": ["paste", "paste text", "insert clipboard"]
}

# Combined dictionary of all commands
ALL_COMMANDS = {
    **NAVIGATION_COMMANDS,
    **FILE_COMMANDS,
    **RUN_COMMANDS,
    **MODE_COMMANDS,
    **EDIT_COMMANDS
}

class VoiceNavigator:
    """Voice navigation system for hands-free coding in PyWrite."""
    
    def __init__(self):
        """Initialize the voice navigation system."""
        self.api_key = os.environ.get("OPENAI_API_KEY")
        self.is_listening = False
        self.command_thread = None
        self.temp_audio_file = os.path.join(tempfile.gettempdir(), "pywrite_voice_command.wav")
        self.last_command_time = 0
        self.command_cooldown = 1.0  # seconds between commands to prevent duplicates
        self.volume_threshold = 0.1  # Minimum volume to trigger voice detection
        self.command_callback = None
        self.active_mode = "code"  # Default to code mode
        
    def set_command_callback(self, callback):
        """Set the callback function to execute when a command is recognized.
        
        Args:
            callback: Function that takes command_type and command_args as parameters
        """
        self.command_callback = callback
        
    def start_listening(self):
        """Start listening for voice commands in a background thread."""
        if self.is_listening:
            print("Voice navigation is already active")
            return False
            
        if not self.api_key:
            print("OpenAI API key not found. Voice navigation requires an API key.")
            return False
            
        self.is_listening = True
        self.command_thread = threading.Thread(target=self._listen_loop)
        self.command_thread.daemon = True
        self.command_thread.start()
        print("Voice navigation activated. Listening for commands...")
        return True
        
    def stop_listening(self):
        """Stop listening for voice commands."""
        self.is_listening = False
        print("Voice navigation deactivated")
        return True
        
    def _listen_loop(self):
        """Background thread for continuous voice command detection."""
        try:
            while self.is_listening:
                # In real implementation, this would use a microphone
                # For demo purposes, we'll simulate voice input at intervals
                
                # Check if enough time has elapsed since last command
                current_time = time.time()
                if current_time - self.last_command_time < self.command_cooldown:
                    time.sleep(0.1)
                    continue
                    
                # In a real implementation, this would record from microphone
                # and only proceed if audio volume is above threshold
                audio_data = self._capture_audio()
                
                # If we have audio data to process
                if audio_data:
                    # In real implementation, this would be the recorded audio
                    # For demo purposes, we'll simulate recognizing common commands
                    command_text = self._recognize_speech(audio_data)
                    
                    if command_text:
                        print(f"Recognized: '{command_text}'")
                        self._process_command(command_text)
                        self.last_command_time = time.time()
                
                # Short sleep to prevent CPU hogging
                time.sleep(0.1)
                
        except Exception as e:
            print(f"Error in voice command loop: {e}")
            self.is_listening = False
    
    def _capture_audio(self):
        """Capture audio from microphone.
        
        Returns:
            Audio data or None if no significant audio detected
        """
        # In real implementation, this would capture from microphone
        # For demo purposes, we'll return a placeholder
        
        # Simulate periodic voice data for the demo
        # In real use, this would return None when no voice is detected
        # and actual audio data when voice is detected
        return b"simulated_audio_data"
    
    def _recognize_speech(self, audio_data):
        """Convert audio to text using OpenAI's Whisper API.
        
        Args:
            audio_data: Audio data as bytes
            
        Returns:
            Recognized text or None if recognition failed
        """
        try:
            # In a real implementation, this would send the audio to OpenAI Whisper API
            # For demo purposes, we'll rotate through some simulated commands
            
            # Simulate recognized text for the demo
            # In real use, this would be the text from the Whisper API
            
            # This code is for demonstration - in production, use the 
            # actual OpenAI Whisper API endpoint
            '''
            # Actual implementation would look something like this using standard library:
            import http.client
            import mimetypes
            import json
            
            # Create a boundary for multipart form data
            boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
            
            # Set up HTTP connection
            conn = http.client.HTTPSConnection("api.openai.com")
            
            # Set headers
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': f'multipart/form-data; boundary={boundary}'
            }
            
            # Read audio file
            with open(self.temp_audio_file, 'rb') as audio_file:
                file_content = audio_file.read()
            
            # Construct the payload
            payload = (
                f'--{boundary}\r\n'
                'Content-Disposition: form-data; name="model"\r\n\r\n'
                'whisper-1\r\n'
                f'--{boundary}\r\n'
                f'Content-Disposition: form-data; name="file"; filename="audio.wav"\r\n'
                f'Content-Type: {mimetypes.guess_type("audio.wav")[0] or "application/octet-stream"}\r\n\r\n'
            ).encode('utf-8')
            
            payload += file_content
            payload += f'\r\n--{boundary}--\r\n'.encode('utf-8')
            
            # Send the request
            conn.request("POST", "/v1/audio/transcriptions", payload, headers)
            
            # Get the response
            response = conn.getresponse()
            
            if response.status == 200:
                result = json.loads(response.read().decode('utf-8'))
                return result.get("text")
            else:
                print(f"Speech recognition error: {response.status} {response.reason}")
                return None
            '''
            
            # For demo purposes:
            # Get current time as seed for demo command rotation
            seed = int(time.time()) % 10
            
            demo_commands = [
                "go to line 42",
                "save file",
                "run code",
                "switch to fiction mode",
                "find the main function",
                "copy selection",
                "paste",
                "next page",
                "undo",
                "open file example.py"
            ]
            
            # Return a different command each time based on seed
            return demo_commands[seed]
            
        except Exception as e:
            print(f"Speech recognition error: {e}")
            return None
    
    def _process_command(self, command_text):
        """Process recognized command text and execute corresponding action.
        
        Args:
            command_text: Text of the recognized command
        """
        if not command_text:
            return
            
        command_text = command_text.lower()
        
        # Process the command through OpenAI to extract intent and parameters
        command_type, command_args = self._extract_command_intent(command_text)
        
        if command_type:
            print(f"Executing command: {command_type} with args: {command_args}")
            
            # If we have a callback registered, call it with the command details
            if self.command_callback:
                self.command_callback(command_type, command_args)
            else:
                # Directly handle some basic commands for demonstration
                self._execute_command(command_type, command_args)
    
    def _extract_command_intent(self, command_text):
        """Extract command intent and parameters from natural language.
        
        Args:
            command_text: Text of the recognized command
            
        Returns:
            Tuple of (command_type, command_args)
        """
        try:
            # In a real implementation, this would use OpenAI GPT API
            # to interpret the command intent and extract parameters
            
            # For demo purposes, we'll use simple matching
            command_type = None
            command_args = {}
            
            # Check against all defined command patterns
            for cmd_type, patterns in ALL_COMMANDS.items():
                for pattern in patterns:
                    if pattern in command_text:
                        command_type = cmd_type
                        break
                if command_type:
                    break
            
            # Extract arguments based on command type
            if command_type == "goto_line":
                # Extract line number
                import re
                line_match = re.search(r"line\s+(\d+)", command_text)
                if line_match:
                    command_args["line_number"] = int(line_match.group(1))
            
            elif command_type == "find_text":
                # Extract search text
                parts = command_text.split("find", 1)
                if len(parts) > 1:
                    search_text = parts[1].strip()
                    if search_text:
                        command_args["search_text"] = search_text
                
            elif command_type in ["open_file", "save_as"]:
                # Extract filename
                parts = command_text.split(command_type.split("_")[0], 1)
                if len(parts) > 1:
                    filename = parts[1].strip()
                    if filename:
                        command_args["filename"] = filename
            
            return command_type, command_args
            
        except Exception as e:
            print(f"Error extracting command intent: {e}")
            return None, {}
    
    def _execute_command(self, command_type, command_args):
        """Execute a command based on its type and arguments.
        
        Args:
            command_type: Type of command to execute
            command_args: Arguments for the command
        """
        try:
            # Navigation commands
            if command_type == "goto_line":
                line_number = command_args.get("line_number", 1)
                print(f"Navigating to line {line_number}")
                
            elif command_type == "next_page":
                print("Scrolling to next page")
                
            elif command_type == "prev_page":
                print("Scrolling to previous page")
                
            elif command_type == "start_of_file":
                print("Navigating to start of file")
                
            elif command_type == "end_of_file":
                print("Navigating to end of file")
                
            elif command_type == "find_text":
                search_text = command_args.get("search_text", "")
                print(f"Searching for: {search_text}")
                
            # File commands
            elif command_type == "open_file":
                filename = command_args.get("filename", "")
                print(f"Opening file: {filename}")
                
            elif command_type == "save_file":
                print("Saving current file")
                
            elif command_type == "save_as":
                filename = command_args.get("filename", "")
                print(f"Saving file as: {filename}")
                
            elif command_type == "new_file":
                print("Creating new file")
                
            elif command_type == "close_file":
                print("Closing current file")
                
            # Run commands
            elif command_type == "run_code":
                print("Running code")
                
            elif command_type == "debug_code":
                print("Starting debugger")
                
            elif command_type == "stop_execution":
                print("Stopping execution")
                
            # Mode commands
            elif command_type == "switch_fiction":
                self.active_mode = "fiction"
                print("Switching to fiction mode")
                
            elif command_type == "switch_screenwriting":
                self.active_mode = "screenwriting"
                print("Switching to screenwriting mode")
                
            elif command_type == "switch_code":
                self.active_mode = "code"
                print("Switching to code mode")
                
            # Edit commands
            elif command_type == "undo":
                print("Undoing last action")
                
            elif command_type == "redo":
                print("Redoing last action")
                
            elif command_type == "copy":
                print("Copying selection")
                
            elif command_type == "cut":
                print("Cutting selection")
                
            elif command_type == "paste":
                print("Pasting from clipboard")
                
        except Exception as e:
            print(f"Error executing command: {e}")

def main():
    """Run a demo of the voice navigation system."""
    print("====================================")
    print("  PyWrite Voice Navigation Demo")
    print("====================================")
    
    # Check for API key
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Warning: OpenAI API key not found. Voice navigation requires an API key.")
        print("Set the OPENAI_API_KEY environment variable for full functionality.")
        print("\nRunning in demonstration mode with simulated commands...")
    
    # Create and start voice navigator
    navigator = VoiceNavigator()
    
    # Define a callback to handle commands
    def command_handler(cmd_type, cmd_args):
        print(f"\nVoice command received: {cmd_type}")
        print(f"Arguments: {cmd_args}")
        print("------------------------------------")
    
    # Set the callback
    navigator.set_command_callback(command_handler)
    
    # Start listening
    if navigator.start_listening():
        print("\nVoice navigation active. Say commands like:")
        print("  - \"Go to line 42\"")
        print("  - \"Save file\"")
        print("  - \"Run code\"")
        print("  - \"Switch to fiction mode\"")
        
        try:
            # Run for 30 seconds to demonstrate
            print("\nDemonstrating voice commands (will run for 30 seconds)...")
            for i in range(30):
                # Every 3 seconds, simulate processing a command
                if i % 3 == 0:
                    print(f"\n[Simulating voice command detection {i//3+1}/10]")
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\nDemo interrupted by user")
        finally:
            # Stop the voice navigator
            navigator.stop_listening()
    
    print("\nVoice navigation demo complete.")
    print("In production use, this would continuously listen for actual voice commands.")

if __name__ == "__main__":
    main()