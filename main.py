import os
import sys
import subprocess

def main():
    """
    Main function that starts the PyWrite editor application.
    This displays help information by default.
    """
    print("Starting PyWrite Editor...")
    
    # If no args were provided, show help
    if len(sys.argv) == 1:
        args = ["help"]
    else:
        args = sys.argv[1:]
    
    try:
        # Launch app.py with any provided arguments
        cmd = [sys.executable, "app.py"] + args
        return subprocess.call(cmd)
    except Exception as e:
        print(f"Error launching PyWrite Editor: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
