#!/bin/bash
# PyWrite command-line wrapper script
# This script provides convenient shortcuts to PyWrite's functionality

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

function show_help() {
    echo "PyWrite - Python Writing Utilities"
    echo "Usage: ./pywrite.sh COMMAND [ARGS]"
    echo ""
    echo "Commands:"
    echo "  view FILE [RANGE]        - View a file with line numbers"
    echo "  list [DIR] [PATTERN]     - List files in a directory"
    echo "  run FILE                 - Run a Python file"
    echo "  create FILE [TEMPLATE]   - Create a file from template"
    echo "  copy SRC DEST            - Copy a file"
    echo "  cat OUT IN1 [IN2...]     - Concatenate files"
    echo "  search PATTERN [DIR] [PAT] - Search in files"
    echo "  compare FILE1 FILE2      - Compare two files"
    echo "  analyze FILE             - Analyze code comments"
    echo "  improve FILE [OUTPUT]    - Improve code comments"
    echo "  guide                    - Show PyWrite guide"
    echo "  demo                     - Run PyWrite demo"
    echo "  help                     - Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./pywrite.sh view example_code.py"
    echo "  ./pywrite.sh create new_file.py python"
    echo "  ./pywrite.sh analyze complex_example.py"
}

if [ $# -lt 1 ]; then
    show_help
    exit 1
fi

COMMAND="$1"
shift

case "$COMMAND" in
    view|list|run|create|copy|cat|search|compare)
        python "$SCRIPT_DIR/enhanced_editor.py" "$COMMAND" "$@"
        ;;
    analyze|improve)
        if [ "$COMMAND" = "improve" ] && [ $# -gt 1 ]; then
            python "$SCRIPT_DIR/comment_assistant.py" "$COMMAND" "$1" --output "$2"
        else
            python "$SCRIPT_DIR/comment_assistant.py" "$COMMAND" "$@"
        fi
        ;;
    guide)
        python "$SCRIPT_DIR/pywrite_guide.py"
        ;;
    demo)
        python "$SCRIPT_DIR/pywrite_example.py"
        ;;
    help)
        show_help
        ;;
    *)
        echo "Unknown command: $COMMAND"
        show_help
        exit 1
        ;;
esac