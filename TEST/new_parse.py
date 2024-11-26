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
        self.variables = {}  # Store declared variables
        self.it = None  # Represent the IT variable

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

    def parse_expression(self):
        """Parse an expression: arithmetic, literal, or variable."""
        if self.match("KEYWORD", "SUM OF") or self.match("KEYWORD", "DIFF OF") or \
           self.match("KEYWORD", "PRODUKT OF") or self.match("KEYWORD", "QUOSHUNT OF") or \
           self.match("KEYWORD", "MOD OF") or self.match("KEYWORD", "BIGGR OF") or \
           self.match("KEYWORD", "SMALLR OF"):
            operator = self.tokens[self.current - 1]["value"]
            if not self.parse_expression():
                self.error(f"Expected an expression after '{operator}'")
            if not self.match("KEYWORD", "AN"):
                self.error(f"Expected 'AN' between operands in '{operator}'")
            if not self.parse_expression():
                self.error(f"Expected an expression after 'AN' in '{operator}'")
            return True

        return self.parse_literal() or self.match("VARIABLE_IDENTIFIER")

    def parse_print_list(self):
        """Parse a list of values or expressions: <expr> (AN <expr>)*."""
        if not self.parse_expression():
            self.error("Expected an expression or value after 'VISIBLE'")
        
        while self.match("KEYWORD", "AN"):  # Match additional expressions connected by "AN"
            if not self.parse_expression():
                self.error("Expected an expression after 'AN'")

    def parse_inline_comment(self):
        """Parse an optional inline comment: BTW <text>."""
        self.match("COMMENT")  # Simply consume the COMMENT token if present

    def parse_visible(self):
        """Parse a VISIBLE statement: VISIBLE <print_list> <inline_comment>?."""
        if not self.match("KEYWORD", "VISIBLE"):
            self.error("Expected 'VISIBLE' for print statement")
        
        # Parse the list of literals or expressions
        self.parse_print_list()
        
        # Parse an optional inline comment
        self.parse_inline_comment()

    def parse_multiline_comment(self):
        """Parse a multiline comment: OBTW ... TLDR."""
        if not self.match("MULTILINE_COMMENT_START", "OBTW"):
            self.error("Expected 'OBTW' to start a multiline comment")

        # Ensure there's no other token after OBTW on the same line
        if self.peek() and self.peek()["type"] != "MULTILINE_COMMENT_END":
            self.error("Invalid token after 'OBTW'. It should be the only token on the line.")
        
        # Consume the OBTW token
        self.consume()

        # Now, we expect the next token to be 'TLDR' on a new line
        if not self.match("MULTILINE_COMMENT_END", "TLDR"):
            self.error("Expected 'TLDR' after 'OBTW'")

    def parse_i_has_a(self):
        """Parse the 'I HAS A' statement: I HAS A varident (ITZ <literal>)?."""
        if not self.match("KEYWORD", "I HAS A"):
            self.error("Expected 'I HAS A' to declare a variable")

        # Parse the variable identifier (the name of the variable)
        varident = self.match("VARIABLE_IDENTIFIER")
        if not varident:
            self.error("Expected a variable identifier after 'I HAS A'")

        # Check if the variable is initialized with ITZ and a literal
        if self.match("KEYWORD", "ITZ"):
            literal = self.parse_literal()
            if not literal:
                self.error("Expected a literal after 'ITZ'")
            # Store the variable with its initialized value
            self.variables[varident["value"]] = literal["value"]
        else:
            # If no ITZ, just declare the variable without initialization
            self.variables[varident["value"]] = None

    def parse_orly(self):
        """Parse an if-then statement: O RLY? YA RLY ... NO WAI ... OIC."""
        if not self.match("KEYWORD", "O RLY?"):
            self.error("Expected 'O RLY?'")

        # Check for YA RLY block
        if self.match("KEYWORD", "YA RLY"):
            if self.it == "WIN":
                self.parse_statements()  # Parse true block
            else:
                self.skip_block()  # Skip the true block if IT is not WIN

        # Check for NO WAI block
        if self.match("KEYWORD", "NO WAI"):
            if self.it != "WIN":
                self.parse_statements()  # Parse false block
            else:
                self.skip_block()  # Skip the false block if IT is WIN

        # Expect OIC to end the conditional block
        if not self.match("KEYWORD", "OIC"):
            self.error("Expected 'OIC' to close 'O RLY?' block")

    def skip_block(self):
        """Skip over a block until encountering a terminating keyword."""
        while self.peek():
            token = self.peek()
            if token["value"] in ["OIC", "NO WAI", "KTHXBYE"]:
                return  # Exit on block terminators
            self.consume()

    def parse_statements(self):
        """Parse a sequence of statements within a block."""
        while self.peek():
            token = self.peek()
            if token["value"] in ["OIC", "NO WAI", "KTHXBYE"]:
                return  # Exit on block terminators
            elif self.match("KEYWORD", "VISIBLE"):
                self.current -= 1  # Allow parse_visible to handle it
                self.parse_visible()
            elif self.match("KEYWORD", "I HAS A"):
                self.current -= 1  # Allow parse_i_has_a to handle it
                self.parse_i_has_a()
            elif self.match("KEYWORD", "O RLY?"):
                self.current -= 1  # Allow nested conditional blocks
                self.parse_orly()
            else:
                self.error(f"Unexpected token inside block: {token}")

    def parse_program_structure(self):
        """Parse the program structure with support for comments and valid statements."""
        if not self.match("KEYWORD", "HAI"):
            self.error("Expected 'HAI' at the start of the program")
        while self.peek():
            if self.match("KEYWORD", "KTHXBYE"):
                print("Program structure validated: HAI and KTHXBYE are present, with valid statements.")
                return
            self.parse_statements()

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
        print(f"Declared Variables: {parser.variables}")  # Output the variables

    except SyntaxError as e:
        with open("parsing_output.txt", "w") as output_file:
            output_file.write(f"Parsing failed: {e}\n")
        print(f"Parsing failed: {e}")

if __name__ == "__main__":
    main()
