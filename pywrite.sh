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
    echo "  sidecar                  - Start AI assistant with voice chat"
    echo "  voice                    - Start hands-free voice navigation"
    echo "  streamlit                - Start web-based editor interface"
    echo "  enhanced                 - Start with continuous coding features"
    echo "  autocomplete             - Test autocomplete functionality"
    echo "  continuous               - Start continuous coding mode"
    echo "  roadmap                  - Open the roadmap planning system"
    echo "  roadmap-demo             - Run a demo of the roadmap system"
    echo "  creative-roadmap         - Open the unified roadmap system (code, fiction, screenplay)"
    echo "  creative-roadmap-demo    - Run a demo of the creative roadmap system"
    echo "  sentence-completer       - Start the sentence completion assistant"
    echo "  guide                    - Show PyWrite guide"
    echo "  demo                     - Run PyWrite demo"
    echo "  multi-modal              - Launch the multi-modal system demo"
    echo "  help                     - Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./pywrite.sh view example_code.py"
    echo "  ./pywrite.sh create new_file.py python"
    echo "  ./pywrite.sh analyze complex_example.py"
    echo "  ./pywrite.sh sidecar     - Start the AI assistant"
    echo "  ./pywrite.sh voice       - Start voice navigation"
    echo "  ./pywrite.sh streamlit   - Start the web interface"
    echo "  ./pywrite.sh enhanced    - Start with continuous coding"
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
    sidecar)
        python "$SCRIPT_DIR/sidecar.py"
        ;;
    guide)
        python "$SCRIPT_DIR/pywrite_guide.py"
        ;;
    demo)
        python "$SCRIPT_DIR/pywrite_example.py"
        ;;
    multi-modal)
        python "$SCRIPT_DIR/multi_modal_demo.py"
        ;;
    voice)
        python "$SCRIPT_DIR/voice_navigation.py"
        ;;
    streamlit)
        python "$SCRIPT_DIR/main.py" --streamlit
        ;;
    enhanced)
        python "$SCRIPT_DIR/main.py" --streamlit --enhanced
        ;;
    autocomplete)
        python "$SCRIPT_DIR/autocomplete_engine.py"
        ;;
    continuous)
        python "$SCRIPT_DIR/continuous_coding.py"
        ;;
    roadmap)
        python -m streamlit run "$SCRIPT_DIR/roadmap_ui.py" --server.port=5000 --server.address=0.0.0.0
        ;;
    roadmap-demo)
        python "$SCRIPT_DIR/roadmap_demo.py"
        ;;
    creative-roadmap)
        python -m streamlit run "$SCRIPT_DIR/unified_roadmap_ui.py" --server.port=5000 --server.address=0.0.0.0
        ;;
    creative-roadmap-demo)
        python "$SCRIPT_DIR/creative_roadmap_demo.py"
        ;;
    sentence-completer)
        python "$SCRIPT_DIR/sentence_completer_demo.py"
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