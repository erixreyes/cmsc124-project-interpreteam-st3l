from tokenizer import main as lexical_main

class ParseTreeNode:
    def __init__(self, name, children=None):
        self.name = name
        self.children = children if children else []

    def __repr__(self):
        return self.to_string()

    def to_string(self, level=0):
        result = "  " * level + f"{self.name}\n"
        for child in self.children:
            result += child.to_string(level + 1)
        return result

class SyntaxAnalyzer:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token_index = 0
        self.parse_tree = None  # Root 

    def get_current_token(self):
        if self.current_token_index < len(self.tokens):
            return self.tokens[self.current_token_index]
        return None

    def advance_token(self):
        self.current_token_index += 1

    def parse_program(self):
        root = ParseTreeNode("Program")

        # Ignore comments before HAI
        while self.match("COMMENT") or self.match("MULTILINE_COMMENT_START"):
            root.children.append(self.parse_comment())

        # Must start with HAI
        if not self.match("KEYWORD", "HAI"):
            raise SyntaxError("Program must start with HAI.")
        root.children.append(ParseTreeNode("HAI"))
        self.advance_token()

        # Process the rest of the program
        root.children.append(self.parse_body())

        # Must end with KTHXBYE
        if not self.match("KEYWORD", "KTHXBYE"):
            raise SyntaxError("Program must end with KTHXBYE.")
        root.children.append(ParseTreeNode("KTHXBYE"))
        self.advance_token()

        self.parse_tree = root

    def parse_comment(self):
        if self.match("COMMENT"):
            node = ParseTreeNode("COMMENT", [ParseTreeNode(self.get_current_token()["value"])] )
            self.advance_token()
            return node
        elif self.match("MULTILINE_COMMENT_START"):
            node = ParseTreeNode("MULTILINE_COMMENT")
            self.advance_token()
            while not self.match("MULTILINE_COMMENT_END"):
                if self.get_current_token() is None:
                    raise SyntaxError("Unclosed multiline comment.")
                node.children.append(ParseTreeNode(self.get_current_token()["value"]))
                self.advance_token()
            self.advance_token() 
            return node

    def parse_body(self):
        body_node = ParseTreeNode("Body")
        while not self.match("KEYWORD", "KTHXBYE") and self.get_current_token() is not None:
            # Parse statements (placeholder muna)
            body_node.children.append(ParseTreeNode(f"Token: {self.get_current_token()}"))
            self.advance_token()
        return body_node

    def match(self, token_type, token_value=None):
        current_token = self.get_current_token()
        if current_token is None:
            return False
        if current_token["type"] == token_type:
            if token_value is None or current_token["value"] == token_value:
                return True
        return False

def main():
    try:
        # read tokens from tokenizer.py
        with open("output.txt", "r") as token_file: #
            tokens = []
            for line in token_file:
                parts = line.strip().split(", ")
                token_type = parts[0].split(": ")[1]
                token_value = parts[1].split(": ")[1]
                tokens.append({"type": token_type, "value": token_value})

        # Validate syntax
        parser = SyntaxAnalyzer(tokens)
        parser.parse_program()

        # Write parse tree to syntax_output.txt
        with open("syntax_output.txt", "w") as output_file:
            output_file.write("Syntax is valid!\n\n")
            output_file.write("Parse Tree:\n")
            output_file.write(parser.parse_tree.to_string())
        print("Syntax analysis complete. Check syntax_output.txt for results.")

    except SyntaxError as e:
        with open("syntax_output.txt", "w") as output_file:
            output_file.write(f"Syntax Error: {e}\n")
        print("Syntax analysis complete with errors. Check syntax_output.txt for details.")

if __name__ == "__main__":
    lexical_main()  # runs lexical analyzer
    main()
