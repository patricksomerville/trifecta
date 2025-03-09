import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox, ttk
import os
import sys
import ast
import io
from contextlib import redirect_stdout, redirect_stderr

class PyWriteEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("PyWrite Editor")
        
        # Simple theme colors that should work in any environment
        self.bg_color = "#ffffff"  # White
        self.text_color = "#000000"  # Black
        self.accent_color = "#0000ff"  # Blue
        
        # Configure the root window
        self.root.configure(bg=self.bg_color)
        
        # Create a style for ttk widgets - using system defaults for maximum compatibility
        self.style = ttk.Style()
        
        # Variables
        self.current_file = None
        self.file_changed = False
        
        # Create the main layout
        self.create_menu()
        self.create_toolbar()
        self.create_editor()
        self.create_output_panel()
        self.create_status_bar()
        
        # Bind keyboard shortcuts
        self.root.bind('<Control-s>', self.save_file)
        self.root.bind('<Control-o>', self.open_file)
        self.root.bind('<Control-n>', self.new_file)
        self.root.bind('<F5>', self.run_code)
        
        # Set up the initial content
        self.set_initial_content()
        
    def create_menu(self):
        """Create the application menu bar"""
        menubar = tk.Menu(self.root)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New", accelerator="Ctrl+N", command=self.new_file)
        
        # Submenu for New with templates
        new_with_template_menu = tk.Menu(file_menu, tearoff=0)
        new_with_template_menu.add_command(label="Python", command=lambda: self.new_file_with_template("python"))
        new_with_template_menu.add_command(label="HTML", command=lambda: self.new_file_with_template("html"))
        new_with_template_menu.add_command(label="CSS", command=lambda: self.new_file_with_template("css"))
        new_with_template_menu.add_command(label="JavaScript", command=lambda: self.new_file_with_template("javascript"))
        new_with_template_menu.add_command(label="JSON", command=lambda: self.new_file_with_template("json"))
        new_with_template_menu.add_command(label="Markdown", command=lambda: self.new_file_with_template("markdown"))
        file_menu.add_cascade(label="New with Template", menu=new_with_template_menu)
        
        file_menu.add_command(label="Open", accelerator="Ctrl+O", command=self.open_file)
        file_menu.add_command(label="Save", accelerator="Ctrl+S", command=self.save_file)
        file_menu.add_command(label="Save As", command=self.save_file_as)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Cut", accelerator="Ctrl+X", 
                             command=lambda: self.editor.event_generate("<<Cut>>"))
        edit_menu.add_command(label="Copy", accelerator="Ctrl+C", 
                             command=lambda: self.editor.event_generate("<<Copy>>"))
        edit_menu.add_command(label="Paste", accelerator="Ctrl+V", 
                             command=lambda: self.editor.event_generate("<<Paste>>"))
        menubar.add_cascade(label="Edit", menu=edit_menu)
        
        # Run menu
        run_menu = tk.Menu(menubar, tearoff=0)
        run_menu.add_command(label="Run", accelerator="F5", command=self.run_code)
        run_menu.add_command(label="Check Syntax", command=self.check_syntax)
        menubar.add_cascade(label="Run", menu=run_menu)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)
        
        self.root.config(menu=menubar)
    
    def create_toolbar(self):
        """Create a toolbar with common actions"""
        toolbar_frame = ttk.Frame(self.root)
        toolbar_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=2)
        
        # Toolbar buttons
        new_btn = ttk.Button(toolbar_frame, text="New", command=self.new_file)
        new_btn.pack(side=tk.LEFT, padx=2)
        
        open_btn = ttk.Button(toolbar_frame, text="Open", command=self.open_file)
        open_btn.pack(side=tk.LEFT, padx=2)
        
        save_btn = ttk.Button(toolbar_frame, text="Save", command=self.save_file)
        save_btn.pack(side=tk.LEFT, padx=2)
        
        run_btn = ttk.Button(toolbar_frame, text="Run", command=self.run_code)
        run_btn.pack(side=tk.LEFT, padx=2)
        
        check_btn = ttk.Button(toolbar_frame, text="Check Syntax", command=self.check_syntax)
        check_btn.pack(side=tk.LEFT, padx=2)
        
        clear_output_btn = ttk.Button(toolbar_frame, text="Clear Output", command=self.clear_output)
        clear_output_btn.pack(side=tk.LEFT, padx=2)
    
    def create_editor(self):
        """Create the main text editor"""
        editor_frame = ttk.Frame(self.root)
        editor_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Label for the editor
        editor_label = ttk.Label(editor_frame, text="Python Code Editor")
        editor_label.pack(side=tk.TOP, anchor='w')
        
        # Text widget for the editor
        self.editor = scrolledtext.ScrolledText(
            editor_frame, 
            wrap=tk.WORD,
            font=("Courier New", 12),
            undo=True,
            bg="white",
            fg=self.text_color,
            insertbackground=self.text_color,
        )
        self.editor.pack(fill=tk.BOTH, expand=True)
        
        # Set tab width (in spaces) - using a different approach
        tab_width = 4
        tab_size_in_chars = " " * tab_width
        self.editor.config(tabs=tab_size_in_chars)
        
        # Bind events to track changes
        self.editor.bind("<<Modified>>", self.on_text_modified)
        
    def create_output_panel(self):
        """Create the output panel for code execution results"""
        output_frame = ttk.Frame(self.root)
        output_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
        
        # Label for the output
        output_label = ttk.Label(output_frame, text="Output")
        output_label.pack(side=tk.TOP, anchor='w')
        
        # Text widget for output
        self.output = scrolledtext.ScrolledText(
            output_frame, 
            wrap=tk.WORD,
            font=("Courier New", 10),
            height=8,
            bg="#f0f0f0",
            fg="#333333",
        )
        self.output.pack(fill=tk.X)
        self.output.config(state=tk.DISABLED)
    
    def create_status_bar(self):
        """Create a status bar at the bottom of the window"""
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        
        status_bar = ttk.Label(
            self.root, 
            textvariable=self.status_var, 
            relief=tk.SUNKEN, 
            anchor=tk.W
        )
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def set_initial_content(self):
        """Set initial content for the editor"""
        initial_code = """# Welcome to PyWrite Editor!
# Write your Python code here.

def hello_world():
    print("Hello, World!")

# Main code execution
if __name__ == "__main__":
    hello_world()
"""
        self.editor.insert(tk.END, initial_code)
        self.update_title()
    
    def update_title(self):
        """Update the window title with the current file name"""
        title = "PyWrite Editor"
        if self.current_file:
            title += f" - {os.path.basename(self.current_file)}"
        if self.file_changed:
            title += " *"
        self.root.title(title)
    
    def on_text_modified(self, event):
        """Handle text modification events"""
        self.editor.edit_modified(False)  # Reset the modified flag
        if not self.file_changed:
            self.file_changed = True
            self.update_title()
    
    def new_file(self, event=None):
        """Create a new file"""
        if self.file_changed:
            save = messagebox.askyesnocancel("Save Changes", 
                "Do you want to save changes to the current file?")
            if save is None:
                return  # Cancel was pressed
            if save:
                self.save_file()
        
        self.editor.delete(1.0, tk.END)
        self.current_file = None
        self.file_changed = False
        self.update_title()
        self.status_var.set("New file created")
        return "break"  # Prevent default handling
    
    def open_file(self, event=None):
        """Open a file"""
        if self.file_changed:
            save = messagebox.askyesnocancel("Save Changes", 
                "Do you want to save changes to the current file?")
            if save is None:
                return  # Cancel was pressed
            if save:
                self.save_file()
        
        file_path = filedialog.askopenfilename(
            defaultextension=".py",
            filetypes=[
                ("Python Files", "*.py"),
                ("Text Files", "*.txt"),
                ("All Files", "*.*")
            ]
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as file:
                    content = file.read()
                

    def new_file_with_template(self, template_type):
        """Create a new file with the specified template"""
        if self.file_changed:
            save = messagebox.askyesnocancel("Save Changes", 
                "Do you want to save changes to the current file?")
            if save is None:
                return  # Cancel was pressed
            if save:
                self.save_file()
        
        # Import template creation function from simple_editor
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        try:
            from simple_editor import create_from_template
            
            # Create a temporary file with the template
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{template_type}") as tmp:
                tmp_path = tmp.name
            
            # Use the template function
            create_from_template(tmp_path, template_type)
            
            # Load the template content
            with open(tmp_path, 'r') as file:
                content = file.read()
            
            # Delete the temporary file
            os.unlink(tmp_path)
            
            # Update the editor
            self.editor.delete(1.0, tk.END)
            self.editor.insert(tk.END, content)
            self.current_file = None
            self.file_changed = False
            self.update_title()
            self.status_var.set(f"Created new {template_type} file from template")
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not create template: {str(e)}")

                self.editor.delete(1.0, tk.END)
                self.editor.insert(tk.END, content)
                self.current_file = file_path
                self.file_changed = False
                self.update_title()
                self.status_var.set(f"Opened {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not open file: {str(e)}")
        
        return "break"  # Prevent default handling
    
    def save_file(self, event=None):
        """Save the current file"""
        if not self.current_file:
            return self.save_file_as()
        
        try:
            content = self.editor.get(1.0, tk.END)
            with open(self.current_file, 'w') as file:
                file.write(content)
            
            self.file_changed = False
            self.update_title()
            self.status_var.set(f"Saved {os.path.basename(self.current_file)}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save file: {str(e)}")
        
        return "break"  # Prevent default handling
    
    def save_file_as(self):
        """Save the current file with a new name"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".py",
            filetypes=[
                ("Python Files", "*.py"),
                ("Text Files", "*.txt"),
                ("All Files", "*.*")
            ]
        )
        
        if file_path:
            self.current_file = file_path
            self.save_file()
            return True
        
        return False
    
    def update_output(self, text, append=False):
        """Update the output text widget"""
        self.output.config(state=tk.NORMAL)
        if not append:
            self.output.delete(1.0, tk.END)
        self.output.insert(tk.END, text)
        self.output.config(state=tk.DISABLED)
        self.output.see(tk.END)  # Scroll to the end
    
    def clear_output(self):
        """Clear the output panel"""
        self.output.config(state=tk.NORMAL)
        self.output.delete(1.0, tk.END)
        self.output.config(state=tk.DISABLED)
        self.status_var.set("Output cleared")
    
    def run_code(self, event=None):
        """Execute the Python code in the editor"""
        code = self.editor.get(1.0, tk.END)
        self.clear_output()
        self.status_var.set("Running code...")
        
        # Capture stdout and stderr
        out_buffer = io.StringIO()
        
        try:
            # First check for syntax errors
            compile(code, '<string>', 'exec')
            
            # Execute in the current process (not ideal for production but okay for simple editor)
            with redirect_stdout(out_buffer), redirect_stderr(out_buffer):
                exec(code, {})
            
            output = out_buffer.getvalue()
            if output:
                self.update_output(output)
            else:
                self.update_output("Code executed with no output.")
            
            self.status_var.set("Code executed successfully")
        
        except SyntaxError as e:
            error_msg = f"Syntax Error: {str(e)}\nLine {e.lineno}, Column {e.offset}"
            self.update_output(error_msg)
            self.status_var.set("Syntax error detected")
        
        except Exception as e:
            error_msg = f"Runtime Error: {str(e)}"
            self.update_output(error_msg)
            self.status_var.set("Runtime error detected")
        
        return "break"  # Prevent default handling
    
    def check_syntax(self):
        """Check the syntax of the code without executing it"""
        code = self.editor.get(1.0, tk.END)
        self.clear_output()
        
        try:
            ast.parse(code)
            self.update_output("Syntax check passed. No errors detected.")
            self.status_var.set("Syntax check passed")
        except SyntaxError as e:
            error_msg = f"Syntax Error: {str(e)}\nLine {e.lineno}, Column {e.offset}"
            self.update_output(error_msg)
            self.status_var.set("Syntax error detected")
    
    def show_about(self):
        """Show the about dialog"""
        about_text = """PyWrite Editor

A lightweight Python code editor built with Tkinter.

Features:
- Syntax checking
- Code execution
- File management

Created as a simple writing application for Python code.
"""
        messagebox.showinfo("About PyWrite Editor", about_text)

def main():
    root = tk.Tk()
    app = PyWriteEditor(root)
    root.mainloop()

if __name__ == "__main__":
    main()