# PyWrite

A powerful Python writing application with advanced file management utilities, offering developers a modern and intuitive text editing experience.

## Key Features

- **File Management**: Create, view, edit, and search files with ease
- **Multiple File Template Support**: Create new files with professional templates for Python, HTML, CSS, JavaScript, JSON, Markdown and YAML
- **Extensive Search Capabilities**: Search across multiple files with pattern matching
- **File Comparison**: Compare files to identify differences
- **Code Execution**: Run Python files directly
- **AI-Powered Comment Assistant**: Analyze and improve code documentation automatically

## Application Components

The PyWrite application consists of several components that work together to provide a comprehensive development experience:

### Core Utilities (app.py, enhanced_editor.py)

The core file utilities provide command-line access to the main functions:

```
python enhanced_editor.py view <filename> [line-range]  - View a file with optional line range
python enhanced_editor.py list [directory] [pattern]    - List files matching pattern
python enhanced_editor.py run <filename.py>             - Run a Python file
python enhanced_editor.py create <filename> [template]  - Create file from template
python enhanced_editor.py copy <source> <destination>   - Copy a file
python enhanced_editor.py cat <out> <input1> [input2 ...]  - Concatenate files
python enhanced_editor.py search <pattern> [directory]  - Search for text in files
python enhanced_editor.py compare <file1> <file2>       - Compare two files
python enhanced_editor.py analyze <filename>            - Analyze comments in a file
python enhanced_editor.py improve <filename> [output]   - Improve comments in a file
```

### Comment Assistant (comment_assistant.py)

The AI-powered comment assistant automatically analyzes code files and generates appropriate comments and documentation:

- Detects missing docstrings for functions and classes
- Identifies complex code sections that need comments
- Generates improved code with proper documentation
- Supports Python, JavaScript, HTML, and CSS files

Example usage:

```
python comment_assistant.py analyze example.py
python comment_assistant.py improve example.py improved_example.py
```

### File Templates

PyWrite includes professional templates for multiple file types:

- **Python**: Function-based script template with proper docstrings
- **HTML**: Basic HTML5 document with header, main content, and footer sections
- **CSS**: Stylesheet with common styling patterns and responsive design
- **JavaScript**: Module with proper commenting and event listeners
- **JSON**: Structured data template with common fields
- **Markdown**: Document outline with sections
- **YAML**: Configuration file template

## Getting Started

1. Clone the repository
2. Install Python 3.11 or higher
3. Run `python main.py` to get started with PyWrite

## Example Usage

### Creating a new Python file:

```
python enhanced_editor.py create script.py python
```

### Analyzing the comments in a file:

```
python enhanced_editor.py analyze script.py
```

### Improving the comments in a file:

```
python enhanced_editor.py improve script.py improved_script.py
```

### Searching for patterns across files:

```
python enhanced_editor.py search "function" *.js
```

### Comparing two files:

```
python enhanced_editor.py compare original.py modified.py
```

## Future Development

- Visual Studio Code extension integration
- Additional language templates and support
- Extended AI capabilities for code analysis and improvement