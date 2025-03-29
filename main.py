#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main entry point for Trifecta
This displays help information by default and directs users to the shell script.
"""

import os
import sys
import argparse
import subprocess

from automation import AutoSaver, FileWatcher, BatchProcessor
try:
    from database_helper import get_db_instance
    from autocomplete_engine import AutocompleteEngine
    from automation_manager import get_automation_manager
    from continuous_coding import get_continuous_coding_engine
    has_enhanced_features = True
except ImportError:
    has_enhanced_features = False

def start_streamlit_app(enhanced=False):
    """
    Start the Streamlit web interface for Trifecta.
    
    Args:
        enhanced: Whether to use the enhanced version with autocomplete and automation
    """
    try:
        script_name = "streamlit_pywrite_enhanced.py" if enhanced else "streamlit_pywrite.py"
        if not os.path.exists(script_name):
            print(f"Error: {script_name} not found")
            return False

        # Use subprocess to start Streamlit in a new process
        cmd = [
            "python", "-m", "streamlit", "run", script_name,
            "--server.port=5000", "--server.address=0.0.0.0"
        ]
        
        print(f"Starting Trifecta Streamlit interface: {' '.join(cmd)}")
        process = subprocess.Popen(cmd)
        
        # Print instructions
        print(f"\nTrifecta Streamlit interface is running at: http://localhost:5000")
        print("Press Ctrl+C to stop the server")
        
        # Wait for the process to complete (or be interrupted)
        process.wait()
        return True
    except KeyboardInterrupt:
        print("\nStopping Trifecta Streamlit interface...")
        return True
    except Exception as e:
        print(f"Error starting Streamlit app: {str(e)}")
        return False

def start_enhanced_features():
    """Start the enhanced automation and continuous coding features."""
    if not has_enhanced_features:
        print("Enhanced features are not available in this installation.")
        return False
    
    try:
        # Initialize database
        db = get_db_instance()
        
        # Initialize and start automation manager
        automation = get_automation_manager()
        automation.start()
        
        # Check for OpenAI API key
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            print("Warning: OPENAI_API_KEY environment variable not set.")
            print("Continuous coding features requiring AI will be disabled.")
        
        # Initialize and start continuous coding engine
        continuous_coding = get_continuous_coding_engine(api_key)
        continuous_coding.start()
        
        print("Enhanced features started successfully.")
        return True
    except Exception as e:
        print(f"Error starting enhanced features: {str(e)}")
        return False

def main():
    """
    Main function that starts the Trifecta editor application.
    This displays help information by default and initializes automation.
    """
    parser = argparse.ArgumentParser(description="Trifecta - Python Writing Application")
    parser.add_argument("--streamlit", action="store_true", help="Start the Streamlit web interface")
    parser.add_argument("--enhanced", action="store_true", help="Start with enhanced automation and continuous coding features")
    
    args = parser.parse_args()
    
    # If streamlit flag is provided, start the web interface
    if args.streamlit:
        return start_streamlit_app(enhanced=args.enhanced)
    
    # If enhanced flag is provided, start the enhanced features
    if args.enhanced:
        start_enhanced_features()
    
    # Initialize basic automation
    auto_saver = AutoSaver(save_interval=300)  # 5 minutes
    file_watcher = FileWatcher(".", [".py", ".txt", ".md"])
    batch_processor = BatchProcessor()
    
    # Start automation services
    auto_saver.start()
    file_watcher.start()
    print("====================================")
    print("  Welcome to Trifecta!")
    print("====================================")
    print("")
    print("Trifecta is a powerful Python writing application with advanced")
    print("file management utilities and an AI-powered comment assistant.")
    print("It now includes a Sidecar feature for real-time AI assistance.")
    print("")
    print("NEW! Continuous Coding Features:")
    print("  - AI-powered code completion and generation")
    print("  - Smart file processing and refactoring")
    print("  - Autocomplete with context-aware suggestions")
    print("  - Database-backed code snippets and patterns")
    print("")
    print("To get started, use the following commands:")
    print("")
    print("  ./trifecta.sh help         - Show all available commands")
    print("  ./trifecta.sh guide        - Show detailed usage guide")
    print("  ./trifecta.sh demo         - Run a demonstration")
    print("  ./trifecta.sh view FILE    - View a file with line numbers")
    print("  ./trifecta.sh run FILE     - Run a Python file")
    print("  ./trifecta.sh create FILE  - Create a new file from template")
    print("  ./trifecta.sh sidecar      - Start AI assistant with voice chat")
    print("  ./trifecta.sh streamlit    - Start the web-based interface")
    print("  ./trifecta.sh enhanced     - Start with continuous coding features")
    print("")
    print("  The legacy ./pywrite.sh script still works for backward compatibility.")
    print("")
    print("For more information, see the README.md file.")
    print("")
    
    # Check if the shell scripts are executable
    if not os.access("trifecta.sh", os.X_OK):
        print("NOTE: The trifecta.sh script is not executable.")
        print("Run the following command to make it executable:")
        print("")
        print("  chmod +x trifecta.sh")
        print("")
    
    if not os.access("pywrite.sh", os.X_OK):
        print("NOTE: The legacy pywrite.sh script is not executable.")
        print("Run the following command to make it executable:")
        print("")
        print("  chmod +x pywrite.sh")
        print("")


if __name__ == "__main__":
    main()