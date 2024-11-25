import json

def read_tokens(file_name="output.txt"):
    """Read tokens from the tokenizer output file."""
    tokens = []

    try:
        with open(file_name, "r") as token_file:
            for line in token_file:
                token = json.loads(line.strip())
                tokens.append(token)
        
        return tokens
    except FileNotFoundError:
        print(f"Error: {file_name} not found.")
        return []
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return []

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0

    def peek(self):
        """Peek at the current token."""
        while self.current < len(self.tokens):
            token = self.tokens[self.current]
            if token["type"] == "COMMENT":
                # Skip over COMMENT tokens
                self.current += 1
                continue
            return token
        return None

    def consume(self):
        """Consume and return the current token."""
        token = self.peek()
        if token:
            self.current += 1
        return token

    def match(self, expected_type, expected_value=None):
        """Match the current token against an expected type and value."""
        token = self.peek()
        if token and token["type"] == expected_type and (expected_value is None or token["value"] == expected_value):
            return self.consume()
        return None

    def error(self, message):
        """Raise a syntax error."""
        token = self.peek()
        position = self.current
        if token:
            raise SyntaxError(f"{message}. Found {token} at position {position}.")
        else:
            raise SyntaxError(f"{message}. Reached end of input.")

    def parse_literal(self):
        """Parse a literal: numbr, numbar, yarn, troof."""
        return (
            self.match("NUMBR_LITERAL") or
            self.match("NUMBAR_LITERAL") or
            self.match("YARN_LITERAL") or
            self.match("TROOF_LITERAL")
        )

    def parse_print_list(self):
        """Parse a list of values: <literal> (AN <literal>)*."""
        if not self.parse_literal():
            self.error("Expected a literal value after 'VISIBLE'")
        
        while self.match("KEYWORD", "AN"):  # Match additional literals connected by "AN"
            if not self.parse_literal():
                self.error("Expected a literal value after 'AN'")

    def parse_inline_comment(self):
        """Parse an optional inline comment: BTW <text>."""
        self.match("COMMENT")  # Simply consume the COMMENT token if present

    def parse_visible(self):
        """Parse a VISIBLE statement: VISIBLE <print_list> <inline_comment>?."""
        if not self.match("KEYWORD", "VISIBLE"):
            self.error("Expected 'VISIBLE' for print statement")
        
        # Parse the list of literals
        self.parse_print_list()
        
        # Parse an optional inline comment
        self.parse_inline_comment()

    def parse_multiline_comment(self):
        """Parse a multiline comment: OBTW ... TLDR."""
        if not self.match("MULTILINE_COMMENT_START", "OBTW"):
            self.error("Expected 'OBTW' to start a multiline comment")
        
        # Skip all tokens until we find 'TLDR'
        while not self.match("MULTILINE_COMMENT_END", "TLDR"):
            if not self.peek():
                self.error("Unterminated multiline comment. Expected 'TLDR'.")

    def parse_program_structure(self):
        """Parse the program structure with support for comments and valid statements."""
        # Check for the opening keyword
        if not self.match("KEYWORD", "HAI"):
            self.error("Expected 'HAI' at the start of the program")
        
        # Parse main program body
        while self.peek():
            if self.match("KEYWORD", "KTHXBYE"):
                print("Program structure validated: HAI and KTHXBYE are present, with valid statements.")
                return True
            
            # Handle program statements
            if self.match("KEYWORD", "VISIBLE"):
                self.current -= 1  # Roll back to let parse_visible handle this
                self.parse_visible()
            elif self.match("MULTILINE_COMMENT_START", "OBTW"):
                self.current -= 1  # Roll back to let parse_multiline_comment handle this
                self.parse_multiline_comment()
            else:
                self.error("Invalid statement")

# Main execution
def main():
    tokens = read_tokens()  # Read tokens from output.txt
    if not tokens:
        print("No tokens found. Exiting.")
        with open("parsing_output.txt", "w") as output_file:
            output_file.write("Parsing failed: No tokens found in the input.\n")
        return

    try:
        parser = Parser(tokens)
        parser.parse_program_structure()

        # Success message
        with open("parsing_output.txt", "w") as output_file:
            output_file.write("Parsing successful: Program structure is valid.\n")
        print("Parsing successful: Program structure is valid.")

    except SyntaxError as e:
        with open("parsing_output.txt", "w") as output_file:
            output_file.write(f"Parsing failed: {e}\n")
        print(f"Parsing failed: {e}")

if __name__ == "__main__":
    main()
