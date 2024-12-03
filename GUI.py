import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from tokenizer import tokenize_line
from new_parse import Parser
from new_parse import SymbolTable

class LOLCodeInterpreterGUI:
    def __init__(self, root):
        # Initialization 
        self.root = root
        self.root.title("InterpreTeam LOLCode INTERPRETER")
        self.root.geometry("900x600")

        # To upload LOLCode
        file_frame = tk.Frame(root)
        file_frame.pack(fill=tk.X, padx=5, pady=5)

        self.file_label = tk.Label(file_frame, text="File:")
        self.file_label.pack(side=tk.LEFT, padx=5)

        self.file_entry = tk.Entry(file_frame, width=50)
        self.file_entry.pack(side=tk.LEFT, padx=5)

        self.browse_button = tk.Button(file_frame, text="Browse", command=self.browse_file)
        self.browse_button.pack(side=tk.LEFT, padx=5)

        # Text Editor
        editor_frame = tk.Frame(root)
        editor_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.text_editor = tk.Text(editor_frame, wrap=tk.WORD, height=10, bg="white", font=("Courier", 12))
        self.text_editor.pack(fill=tk.BOTH, expand=True)

        # Frame for Lexemes and Symbol Table
        table_frame = tk.Frame(root)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Lexemes Table Frame
        token_frame = tk.Frame(table_frame)
        token_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        token_label = tk.Label(token_frame, text="Lexemes", font=("Arial", 10, "bold"))
        token_label.pack()

        self.token_list = ttk.Treeview(
            token_frame, columns=("Lexeme", "Classification"), show="headings", height=8
        )
        self.token_list.heading("Lexeme", text="Lexeme")
        self.token_list.heading("Classification", text="Classification")
        self.token_list.column("Lexeme", width=150)
        self.token_list.column("Classification", width=150)
        self.token_list.pack(fill=tk.BOTH, expand=True)

        # Symbol Table Frame
        symbol_frame = tk.Frame(table_frame)
        symbol_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        symbol_label = tk.Label(symbol_frame, text="Symbol Table", font=("Arial", 10, "bold"))
        symbol_label.pack()

        self.symbol_table_view = ttk.Treeview(
            symbol_frame, columns=("Identifier", "Value"), show="headings", height=8
        )
        self.symbol_table_view.heading("Identifier", text="Identifier")
        self.symbol_table_view.heading("Value", text="Value")
        self.symbol_table_view.column("Identifier", width=150)
        self.symbol_table_view.column("Value", width=150)
        self.symbol_table_view.pack(fill=tk.BOTH, expand=True)

        # Console and Execute Button
        console_frame = tk.Frame(root)
        console_frame.pack(fill=tk.BOTH, padx=5, pady=5)

        self.console_label = tk.Label(console_frame, text="Console", font=("Arial", 10, "bold"))
        self.console_label.pack()

        self.console_output = tk.Text(console_frame, wrap=tk.WORD, height=6, bg="lightgray", state=tk.DISABLED)
        self.console_output.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        execute_frame = tk.Frame(root)
        execute_frame.pack(pady=10)

        self.execute_button = tk.Button(execute_frame, text="EXECUTE", font=("Arial", 10, "bold"), command=self.execute_code)
        self.execute_button.pack()

        # Initialize Interpreter State
        self.tokens = []

    def browse_file(self):
        filepath = filedialog.askopenfilename(filetypes=[("LOLCode Files", ".lol")])
        if filepath:
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, filepath)
            self.load_file(filepath)

    def load_file(self, filepath):
        try:
            with open(filepath, "r") as file:
                code = file.read()
            self.text_editor.delete(1.0, tk.END)
            self.text_editor.insert(tk.END, code)
        except Exception as e:
            messagebox.showerror("Error", f"Unable to load file: {e}")

    def execute_code(self):
        code = self.text_editor.get(1.0, tk.END).strip()
        if not code:
            messagebox.showwarning("Warning", "The code editor is empty.")
            return

        # Reset tokens
        self.tokens = []

        # Lexical Analysis
        lines = code.splitlines()
        in_multiline_comment = False
        for line in lines:
            line_tokens, in_multiline_comment = tokenize_line(line, in_multiline_comment)
            self.tokens.extend(line_tokens)
        self.update_token_list()

        # Syntax Analysis
        parser = Parser(self.tokens)  # Parser instance
        syntax_errors = []  # to capture syntax errors

        self.console_output.config(state=tk.NORMAL)
        self.console_output.delete(1.0, tk.END)

        if syntax_errors:
            self.console_output.insert(tk.END, "Syntax Errors Found:\n")
            for error in syntax_errors:
                self.console_output.insert(tk.END, f"{error}\n")
        else:
            self.console_output.insert(tk.END, "Syntax Analysis Passed.\n")

        self.console_output.config(state=tk.DISABLED)

        # Update the symbol table from the parser
        self.update_symbol_table(parser.symbol_table)

    def update_symbol_table(self, symbol_table):
        # Print the symbol table (for debugging)
        print("Symbol Table Contents:", symbol_table.table)

        # Clear existing entries
        for item in self.symbol_table_view.get_children():
            self.symbol_table_view.delete(item)

        # Populate with data from the SymbolTable
        for identifier, attributes in symbol_table.table.items():
            value = attributes.get("value", "NOOB")  # try "NOOB" if value is not set
            self.symbol_table_view.insert("", "end", values=(identifier, value))

    def update_token_list(self):
        # Clear existing tokens
        for item in self.token_list.get_children():
            self.token_list.delete(item)

        # Add new tokens
        for token in self.tokens:
            lexeme = token["value"]
            classification = token["type"]
            self.token_list.insert("", "end", values=(lexeme, classification))


if __name__ == "__main__":
    root = tk.Tk()
    app = LOLCodeInterpreterGUI(root)
    root.mainloop()
