# PyWrite

A powerful Python writing application with advanced file management utilities and an AI-powered comment assistant.

## Features

- **File Management**: Create, view, compare, and search in files
- **Code Execution**: Run Python scripts directly from the command line
- **Template Support**: Create new files with templates for Python, HTML, CSS, JavaScript, JSON, Markdown, and YAML
- **AI-Powered Comment Assistant**: Analyze and improve code comments and documentation
- **File Comparison**: Compare two files and see the differences
- **Multiple File Operations**: Concatenate files, search across directories
- **Sidecar Feature**: Real-time AI assistant with voice chat and screen observation capabilities

## Sidecar AI Assistant

The Sidecar feature provides real-time AI assistance as you write and code. It:

- Observes your screen to understand what you're working on
- Provides contextual suggestions for code improvements
- Helps with documentation and code readability
- Answers programming questions with context-aware responses
- Assists with project organization and best practices

Sidecar uses OpenAI's GPT models for intelligent assistance. To use the full capabilities, you'll need to set your OpenAI API key as an environment variable:

```bash
export OPENAI_API_KEY=your-api-key-here
```

Without an API key, Sidecar will run in demo mode with predefined responses to common questions.

## Usage

PyWrite can be used through its command-line interface. The main script `pywrite.sh` provides a convenient wrapper around the core utilities.

### Basic Commands

```bash
# View a file with line numbers
./pywrite.sh view example_code.py

# List files in a directory
./pywrite.sh list . *.py

# Run a Python file
./pywrite.sh run example_code.py

# Create a new file from a template
./pywrite.sh create new_file.py python

# Analyze code comments
./pywrite.sh analyze complex_example.py

# Improve code comments
./pywrite.sh improve complex_example.py improved_code.py

# Start the AI assistant with voice chat
./pywrite.sh sidecar
```

### Advanced Usage

```bash
# Search for a pattern in files
./pywrite.sh search "function" . "*.py"

# Compare two files
./pywrite.sh compare original.py modified.py

# Copy a file
./pywrite.sh copy source.py destination.py

# Concatenate files
./pywrite.sh cat combined.py part1.py part2.py
```

### Interactive Demos and Guides

```bash
# Run the PyWrite demo
./pywrite.sh demo

# Show the PyWrite guide
./pywrite.sh guide
```

## Component Files

- `enhanced_editor.py`: Core file management utilities
- `comment_assistant.py`: AI-powered code comment analysis and improvement
- `sidecar.py`: AI assistant with voice chat and screen observation
- `pywrite.sh`: Command-line wrapper for PyWrite utilities
- `pywrite_example.py`: Demo script showing PyWrite capabilities
- `pywrite_guide.py`: Guide for using PyWrite commands
- `template_examples/`: Example template files for different languages

## Sample Data

The `sample_novel` directory contains example chapters and an outline for demonstrating text processing capabilities.

## Command Reference

Run `./pywrite.sh help` to see all available commands.

```
PyWrite - Python Writing Utilities
Usage: ./pywrite.sh COMMAND [ARGS]

Commands:
  view FILE [RANGE]        - View a file with line numbers
  list [DIR] [PATTERN]     - List files in a directory
  run FILE                 - Run a Python file
  create FILE [TEMPLATE]   - Create a file from template
  copy SRC DEST            - Copy a file
  cat OUT IN1 [IN2...]     - Concatenate files
  search PATTERN [DIR] [PAT] - Search in files
  compare FILE1 FILE2      - Compare two files
  analyze FILE             - Analyze code comments
  improve FILE [OUTPUT]    - Improve code comments
  sidecar                  - Start AI assistant with voice chat
  guide                    - Show PyWrite guide
  demo                     - Run PyWrite demo
  help                     - Show this help message
```