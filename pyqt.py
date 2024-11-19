# wag muna galawin wonky pa to tinest ko lang yung UI ng tokenizer

import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QPushButton, QVBoxLayout, QWidget, QLabel
)

# Import your tokenizer function
from tokenizer import tokenize_line # Replace with the actual module name
from syntax_analyzer import SyntaxAnalyzer

class TokenizerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tokenizer")
        self.setGeometry(100, 100, 800, 600)

        # Layout setup
        layout = QVBoxLayout()

        # Input area
        self.input_label = QLabel("Enter code:")
        self.input_area = QTextEdit()

        # Output area
        self.output_label = QLabel("Tokens:")
        self.output_area = QTextEdit()
        self.output_area.setReadOnly(True)

        # Buttons
        self.tokenize_button = QPushButton("Tokenize")
        self.clear_button = QPushButton("Clear")

        # Connect buttons to actions
        self.tokenize_button.clicked.connect(self.tokenize_code)
        self.clear_button.clicked.connect(self.clear_text)

        # Add widgets to layout
        layout.addWidget(self.input_label)
        layout.addWidget(self.input_area)
        layout.addWidget(self.tokenize_button)
        layout.addWidget(self.clear_button)
        layout.addWidget(self.output_label)
        layout.addWidget(self.output_area)

        # Set central widget
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def tokenize_code(self):
        # Get input from the text area
        code = self.input_area.toPlainText()

        # Process each line with your tokenizer
        tokens_output = []
        in_multiline_comment = False
        try:
            for line in code.splitlines():
                tokens, in_multiline_comment = tokenize_line(line, in_multiline_comment)
                tokens_output.extend(
                    [f"Token Type: {t['type']}, Value: {t['value']}" for t in tokens]
                )

            # Display the tokens in the output area
            self.output_area.setText("\n".join(tokens_output))
        except Exception as e:
            self.output_area.setText(f"Error: {e}")

    def clear_text(self):
        self.input_area.clear()
        self.output_area.clear()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TokenizerGUI()
    window.show()
    sys.exit(app.exec())
