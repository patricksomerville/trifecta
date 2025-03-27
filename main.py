#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main entry point for PyWrite
This displays help information by default and directs users to the shell script.
"""

import os
import sys


def main():
    """
    Main function that starts the PyWrite editor application.
    This displays help information by default.
    """
    print("====================================")
    print("  Welcome to PyWrite!")
    print("====================================")
    print("")
    print("PyWrite is a powerful Python writing application with advanced")
    print("file management utilities and an AI-powered comment assistant.")
    print("")
    print("To get started, use the following commands:")
    print("")
    print("  ./pywrite.sh help         - Show all available commands")
    print("  ./pywrite.sh guide        - Show detailed usage guide")
    print("  ./pywrite.sh demo         - Run a demonstration")
    print("  ./pywrite.sh view FILE    - View a file with line numbers")
    print("  ./pywrite.sh run FILE     - Run a Python file")
    print("  ./pywrite.sh create FILE  - Create a new file from template")
    print("")
    print("For more information, see the README.md file.")
    print("")
    
    # Check if the shell script is executable
    if not os.access("pywrite.sh", os.X_OK):
        print("NOTE: The pywrite.sh script is not executable.")
        print("Run the following command to make it executable:")
        print("")
        print("  chmod +x pywrite.sh")
        print("")


if __name__ == "__main__":
    main()