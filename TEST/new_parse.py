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
        self.inside_wazzup = False 
        
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
        """Parse an expression: arithmetic, logical, literal, or variable."""
        # Handle SMOOSH (string concatenation)
        if self.match("KEYWORD", "SMOOSH"):
            return self.parse_smoosh()  # Handle the string concatenation

        # Handle arithmetic and comparison operations (SUM OF, DIFF OF, etc.)
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

        # Handle logical operators: BOTH OF, EITHER OF, WON OF
        if self.match("KEYWORD", "BOTH OF") or self.match("KEYWORD", "EITHER OF") or self.match("KEYWORD", "WON OF"):
            operator = self.tokens[self.current - 1]["value"]
            if not self.parse_expression():
                self.error(f"Expected the first operand after '{operator}'")
            operand1 = self.it
            if not self.match("KEYWORD", "AN"):
                self.error(f"Expected 'AN' between operands in '{operator}'")
            if not self.parse_expression():
                self.error(f"Expected the second operand after 'AN' in '{operator}'")
            operand2 = self.it

            # Evaluate the logical operation
            if operator == "BOTH OF":
                self.it = operand1 and operand2
            elif operator == "EITHER OF":
                self.it = operand1 or operand2
            elif operator == "WON OF":
                self.it = bool(operand1) ^ bool(operand2)  # XOR operation
            return True

        # Handle NOT (unary operator)
        if self.match("KEYWORD", "NOT"):
            if not self.parse_expression():
                self.error("Expected an operand after 'NOT'")
            operand = self.it
            self.it = not operand
            return True

        # Handle ALL OF and ANY OF (multi-arity logical operators)
        if self.match("KEYWORD", "ALL OF") or self.match("KEYWORD", "ANY OF"):
            operator = self.tokens[self.current - 1]["value"]
            operands = []

            # Parse multiple operands until MKAY
            while not self.match("KEYWORD", "MKAY"):
                if self.match("KEYWORD", "AN"):  # Skip over 'AN' if present
                    continue
                if not self.parse_expression():
                    self.error(f"Expected an operand in '{operator}'")
                operands.append(self.it)

            # Evaluate the logical operation
            if operator == "ALL OF":
                self.it = all(operands)
            elif operator == "ANY OF":
                self.it = any(operands)
            return True

        # Handle the MAEK A type casting
        if self.match("KEYWORD", "MAEK A"):
            varident = self.match("VARIABLE_IDENTIFIER")
            if not varident:
                self.error("Expected a variable identifier after 'MAEK A'")

            # Parse the target type (NUMBR, NUMBAR, YARN, etc.)
            type_ = self.match("KEYWORD")
            if not type_:
                self.error("Expected a type after 'MAEK A'")

            # Typecast the variable and return the result in IT
            if type_:
                if type_["value"] == "NUMBR":
                    self.it = int(self.variables.get(varident["value"], 0))
                elif type_["value"] == "NUMBAR":
                    self.it = float(self.variables.get(varident["value"], 0))
                elif type_["value"] == "YARN":
                    self.it = str(self.variables.get(varident["value"], ""))
                elif type_["value"] == "TROOF":
                    self.it = bool(self.variables.get(varident["value"], False))
                else:
                    self.error(f"Unsupported type '{type_['value']}' after 'MAEK A'")
            return True

        # Now check if it's a literal, variable, or TROOF
        literal = self.parse_literal()  # This handles number, string, etc.
        if literal:
            self.it = literal["value"]  # Store the literal value in 'IT'
            return True

        # Handle TROOF (WIN and FAIL) casting to NUMBR or NUMBAR
        troof = self.match("TROOF_LITERAL")
        if troof:
            if troof["value"] == "WIN":
                self.it = 1  # WIN becomes 1
            elif troof["value"] == "FAIL":
                self.it = 0  # FAIL becomes 0
            return True

        # Handle variable identifiers (for variables)
        varident = self.match("VARIABLE_IDENTIFIER")
        if varident:
            if varident["value"] in self.variables:
                self.it = self.variables[varident["value"]]  # Directly fetch the variable's value
                return True
            else:
                self.error(f"Variable '{varident['value']}' not declared.")
            if self.match("KEYWORD", "R"):  # If 'R' is found after the variable identifier
                # After matching 'R', we need to parse the expression on the right-hand side of the assignment
                self.parse_assignment(varident)  # Pass the variable identifier to handle assignment

            # Handle typecasting (if 'IS NOW A' is found)
            elif self.match("KEYWORD", "IS NOW A"):  # If it's a type-casting operation
                self.parse_is_now_a(varident)  # Pass the variable identifier to handle typecasting
        return False

    
    def parse_smoosh(self):
            """Parse the SMOOSH operation: SMOOSH <expr> AN <expr> AN ... AN <expr>."""
            operands = []  # List of operands to be concatenated

            # Start parsing the first operand
            operands.append(self.parse_expression())

            # Continue parsing subsequent operands connected by AN or '+'
            while self.match("KEYWORD", "AN") or self.match("CONCAT_OPERATOR", "+"):
                operand = self.parse_expression()
                operands.append(operand)

            # Ensure the operands are implicitly cast to YARN and concatenate them
            result = "".join([str(op) for op in operands])  # Concatenate all operands into a single string
            self.it = result  # Set the result of SMOOSH to IT (the "return" value of the expression)
            return result
    
    def parse_print_list(self):
        """Parse a list of values or expressions: <expr> (+ <expr>)*."""
        result = []  # To store concatenated parts

        # First, parse the initial expression
        if not self.parse_expression():
            self.error("Expected an expression or value after 'VISIBLE'")
        result.append(str(self.it))  # Add the result of the expression

        # Handle concatenation using '+' or 'AN'
        while self.match("CONCAT_OPERATOR", "+") or self.match("KEYWORD", "AN"):
            if not self.parse_expression():  # Parse the next expression
                self.error("Expected an expression after '+' or 'AN'")
            result.append(str(self.it))  # Append the result as a string

        # Concatenate all parts into a single string and store in IT
        self.it = "".join(result)

    def parse_inline_comment(self):
        """Parse an optional inline comment: BTW <text>."""
        self.match("COMMENT")  # Simply consume the COMMENT token if present

    def parse_wazzup(self):
        """Parse the WAZZUP block: WAZZUP ... BUHBYE."""
        if not self.match("KEYWORD", "WAZZUP"):
            self.error("Expected 'WAZZUP' after 'HAI'")

        self.inside_wazzup = True  # Enter WAZZUP block

        while not self.match("KEYWORD", "BUHBYE"):
            if not self.peek():
                self.error("Unterminated 'WAZZUP' block. Expected 'BUHBYE'")
            self.parse_i_has_a()  # Parse variable declarations only

        self.inside_wazzup = False  # Exit WAZZUP block

    def parse_visible(self):
        """Parse a VISIBLE statement: VISIBLE <print_list> <inline_comment>?."""
        if not self.match("KEYWORD", "VISIBLE"):
            self.error("Expected 'VISIBLE' for print statement")

        # Parse the list of expressions/literals
        self.parse_print_list()

        # Handle optional inline comment
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
        """Parse the 'I HAS A' statement: I HAS A varident (ITZ <literal|varident|expression>)?."""
        if not self.inside_wazzup:
            self.error("Variable declarations are only allowed inside the 'WAZZUP ... BUHBYE' block")

        if not self.match("KEYWORD", "I HAS A"):
            self.error("Expected 'I HAS A' to declare a variable")

        # Parse the variable identifier (the name of the variable)
        varident = self.match("VARIABLE_IDENTIFIER")
        if not varident:
            self.error("Expected a variable identifier after 'I HAS A'")

        # Check if the variable is initialized with ITZ
        if self.match("KEYWORD", "ITZ"):
            # Parse the value for initialization
            literal = self.parse_literal()
            if literal:
                # Store the variable with its initialized value
                self.variables[varident["value"]] = literal["value"]
            else:
                var_value = self.match("VARIABLE_IDENTIFIER")
                if var_value:
                    if var_value["value"] in self.variables:
                        self.variables[varident["value"]] = self.variables[var_value["value"]]
                    else:
                        self.error(f"Variable '{var_value['value']}' not declared.")
                else:
                    if not self.parse_expression():
                        self.error("Expected a literal, variable, or expression after 'ITZ'")
                    self.variables[varident["value"]] = self.it
        else:
            self.variables[varident["value"]] = None

    def parse_loop(self):
        """Parse a loop: IM IN YR <loopname> (TIL/WILE <condition>) ... IM OUTTA YR <loopname>."""
        if not self.match("KEYWORD", "IM IN YR"):
            self.error("Expected 'IM IN YR' to start a loop")

        # Parse the loop name
        loopname_token = self.match("VARIABLE_IDENTIFIER")
        if not loopname_token:
            self.error("Expected a loop name after 'IM IN YR'")
        loopname = loopname_token["value"]

        # Parse the loop condition type (TIL/WILE)
        if self.match("KEYWORD", "TIL"):
            condition_type = "TIL"
        elif self.match("KEYWORD", "WILE"):
            condition_type = "WILE"
        else:
            self.error("Expected 'TIL' or 'WILE' after loop name")

        # Parse the loop condition
        if not self.parse_expression():
            self.error(f"Expected an expression after '{condition_type}' in loop")

        # Execute the loop
        while True:
            # Evaluate the condition based on the loop type
            condition_result = self.it == "WIN"
            if (condition_type == "TIL" and condition_result) or (condition_type == "WILE" and not condition_result):
                break  # Exit the loop when the condition is met (TIL) or fails (WILE)

            # Parse the loop body
            self.parse_statements()

            # Re-evaluate the condition after parsing the body
            if not self.parse_expression():
                self.error(f"Expected an expression after '{condition_type}' in loop")

        # Ensure the loop ends with IM OUTTA YR <loopname>
        if not self.match("KEYWORD", "IM OUTTA YR"):
            self.error("Expected 'IM OUTTA YR' to end the loop")
        if not self.match("VARIABLE_IDENTIFIER", loopname):
            self.error(f"Expected loop name '{loopname}' after 'IM OUTTA YR'")

    def parse_orly(self):
        """Parse an if-then statement: O RLY? YA RLY ... MEBBE ... NO WAI ... OIC."""
        if not self.match("KEYWORD", "O RLY?"):
            self.error("Expected 'O RLY?'")

        executed = False  # Track whether any block has executed

        # YA RLY block (if-clause)
        if self.match("KEYWORD", "YA RLY"):
            if self.it == "WIN":
                self.parse_statements()  # Execute true block
                executed = True
            else:
                self.skip_block()  # Skip true block if IT is not WIN

        # MEBBE blocks (else-if clauses)
        while self.match("KEYWORD", "MEBBE"):
            if executed:
                self.skip_block()  # Skip this block since a previous block executed
            else:
                # Evaluate the condition for MEBBE
                if not self.parse_expression():
                    self.error("Expected an expression after 'MEBBE'")
                if self.it == "WIN":
                    self.parse_statements()  # Execute this block if condition is true
                    executed = True
                else:
                    self.skip_block()  # Skip this block if condition is false

        # NO WAI block (else-clause)
        if self.match("KEYWORD", "NO WAI"):
            if not executed:  # Only execute if no previous block executed
                self.parse_statements()
            else:
                self.skip_block()  # Skip else block if a previous block executed

        # Expect OIC to end the conditional block
        if not self.match("KEYWORD", "OIC"):
            self.error("Expected 'OIC' to close 'O RLY?' block")
    
    def parse_gimmeh(self):
        """Parse the GIMMEH statement: GIMMEH <varident>."""
        if not self.match("KEYWORD", "GIMMEH"):
            self.error("Expected 'GIMMEH' to read input")

        # Parse the variable identifier
        varident = self.match("VARIABLE_IDENTIFIER")
        if not varident:
            self.error("Expected a variable identifier after 'GIMMEH'")

    def skip_block(self):
        """Skip over a block until encountering a terminating keyword."""
        while self.peek():
            token = self.peek()
            if token["value"] in ["OIC", "NO WAI", "KTHXBYE"]:
                return  # Exit on block terminators
            self.consume()

    def parse_assignment(self, varident):
        """Parse an assignment: varident R <expression>."""

        if not varident:
            self.error("Expected a variable identifier before 'R'")

        if not self.match("KEYWORD", "R"):
            self.error("Expected 'R' for assignment")

        # Parse the expression to be assigned
        if not self.parse_expression():
            self.error("Expected an expression after 'R' for assignment")

        # Store the result in the variable as a direct value
        self.variables[varident["value"]] = self.it  # Directly store the evaluated result
        return self.it
        
    def parse_is_now_a(self, varident):
        """Parse 'IS NOW A' type casting: varident IS NOW A <type>."""
        if not varident:
            self.error("Expected a variable identifier before 'IS NOW A'")

        if not self.match("KEYWORD", "IS NOW A"):
            self.error("Expected 'IS NOW A' for typecasting")

        # Now, we expect a type (NUMBR, NUMBAR, YARN, TROOF, etc.)
        type_ = self.match("KEYWORD")
        if not type_:
            self.error("Expected a type after 'IS NOW A'")

        # Handle the typecasting logic based on the type
        if type_:
            # Change the type of the variable without changing the value
            if type_["value"] == "NUMBR":
                self.variables[varident["value"]] = {"value": self.variables.get(varident["value"], 0), "type": "NUMBR"}
            elif type_["value"] == "NUMBAR":
                self.variables[varident["value"]] = {"value": self.variables.get(varident["value"], 0), "type": "NUMBAR"}
            elif type_["value"] == "YARN":
                self.variables[varident["value"]] = {"value": str(self.variables.get(varident["value"], "")), "type": "YARN"}
            elif type_["value"] == "TROOF":
                self.variables[varident["value"]] = {"value": bool(self.variables.get(varident["value"], False)), "type": "TROOF"}
            else:
                self.error(f"Unsupported type '{type_['value']}' after 'IS NOW A'")
        else:
            self.error(f"Unsupported type '{type_['value']}' after 'IS NOW A'")

    def parse_maek(self):
        """Parse explicit typecasting with 'MAEK A': MAEK A varident <type>."""
        varident = self.match("VARIABLE_IDENTIFIER")
        if not varident:
            self.error("Expected a variable identifier after 'MAEK A'")

        # Parse the target type (NUMBR, NUMBAR, YARN, etc.)
        type_ = self.match("KEYWORD")

        # Typecast the variable and return the result in IT
        if type_:
            # Change the type of the variable without changing the value
            if type_["value"] == "NUMBR":
                self.variables[varident["value"]] = {"value": self.variables.get(varident["value"], 0), "type": "NUMBR"}
            elif type_["value"] == "NUMBAR":
                self.variables[varident["value"]] = {"value": self.variables.get(varident["value"], 0), "type": "NUMBAR"}
            elif type_["value"] == "YARN":
                self.variables[varident["value"]] = {"value": str(self.variables.get(varident["value"], "")), "type": "YARN"}
            elif type_["value"] == "TROOF":
                self.variables[varident["value"]] = self.cast_to_troof(self.variables.get(varident["value"], 0))
        else:
            self.error(f"Unsupported type '{type_['value']}' after 'MAEK A'")

        return self.it
    def cast_to_troof(self, value):
        """Cast any value to a TROOF."""
        if value == 0 or value == 0.0 or value == "":  # Empty string or zero
            return False  # FAIL
        else:
            return True  # WIN
    
    def parse_literal(self):
        """Parse a literal: numbr, numbar, yarn, troof."""
        # Check for TROOF literal (WIN or FAIL)
        troof = self.match("TROOF_LITERAL")
        if troof:
            if troof["value"] == "WIN":
                self.it = True  # WIN is considered True
            elif troof["value"] == "FAIL":
                self.it = False  # FAIL is considered False
            return troof

        # Proceed with the rest of the literals (numbr, numbar, yarn, etc.)
        return (
            self.match("NUMBR_LITERAL") or
            self.match("NUMBAR_LITERAL") or
            self.match("YARN_LITERAL")
        )
    
    def parse_statements(self):
        """Parse a sequence of statements within a block."""
        while self.peek():
            token = self.peek()
            if token["value"] in ["OIC", "NO WAI", "MEBBE", "IM OUTTA YR", "KTHXBYE"]:
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
            elif self.match("KEYWORD", "IM IN YR"):
                self.current -= 1  # Allow nested loops
                self.parse_loop()
            elif self.match("KEYWORD", "WAZZUP"):
                self.current -= 1  # Allow nested WAZZUP blocks
                self.parse_wazzup()
            elif self.match("KEYWORD", "GIMMEH"):
                self.current -= 1   
                self.parse_gimmeh()
            elif self.match("KEYWORD", "SMOOSH"):
                self.current -= 1
                self.parse_smoosh()
            elif self.match("VARIABLE_IDENTIFIER"):
                varident = self.tokens[self.current - 1]  # Store the current variable identifier
                print(f"Variable identifier found: {varident}")  # Debugging

                if self.peek()["value"] == "R":  # Check for 'R' without consuming
                    print(f"'R' found after variable '{varident['value']}'")  # Debugging
                    self.parse_assignment(varident)  # Proceed with assignment parsing
                elif self.peek()["value"] == "IS NOW A":  # If it's a type-casting operation
                    self.parse_is_now_a(varident)  # Pass the variable identifier to handle typecasting
                else:  # Otherwise, treat it as part of an expression
                    self.current -= 1  # Roll back to allow parse_expression to handle it
                    self.parse_expression()
                # Handle typecasting (if 'IS NOW A' is found)
                
                
            elif self.match("KEYWORD", "MAEK A"):
                self.current -= 1  
                self.parse_maek()
            else:
                self.error(f"Unexpected token inside block: {token}")

    def parse_program_structure(self):
        """Parse the program structure with support for comments and valid statements."""
        if not self.match("KEYWORD", "HAI"):
            self.error("Expected 'HAI' at the start of the program")
        if self.peek() and self.match("KEYWORD", "WAZZUP"):
            self.current -= 1  # Roll back to parse the WAZZUP block
            self.parse_wazzup()
        else:
            self.error("Expected 'WAZZUP' after 'HAI' for variable declarations")

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
