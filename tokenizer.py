import re

# Token types
class TokenType:
    KEYWORD = "KEYWORD"
    VARIDENT = "VARIABLE_IDENTIFIER"
    NUMBR_LITERAL = "NUMBR_LITERAL"
    NUMBAR_LITERAL = "NUMBAR_LITERAL"
    YARN_LITERAL = "YARN_LITERAL"
    TROOF_LITERAL = "TROOF_LITERAL"
    COMMENT = "COMMENT"
    MULTILINE_COMMENT_START = "MULTILINE_COMMENT_START"
    MULTILINE_COMMENT_END = "MULTILINE_COMMENT_END"
    UNKNOWN = "UNKNOWN"

# Keywords used
KEYWORDS = [
    "HAI", "KTHXBYE", "VISIBLE", "I HAS A", "ITZ", "R", "SUM OF", "DIFF OF",
    "PRODUKT OF", "QUOSHUNT OF", "MOD OF", "BIGGR OF", "SMALLR OF", "BOTH SAEM",
    "DIFFRINT", "O RLY?", "YA RLY", "MEBBE", "NOWAI", "OIC", "WTF?", "OMG", 
    "OMGWTF", "IM IN YR", "UPPIN", "NERFIN", "YR", "TIL", "WILE", "IM OUTTA YR", 
    "HOW IZ I", "IF U SAY SO", "GTFO", "FOUND YR", "MKAY"
]

# RegEx patterns for token types
REGEX_PATTERNS = {
    TokenType.KEYWORD: r"\b(" + "|".join(re.escape(keyword) for keyword in KEYWORDS) + r")\b",
    TokenType.NUMBR_LITERAL: r"^-?[0-9]+$",
    TokenType.NUMBAR_LITERAL: r"^-?[0-9]+\.[0-9]+$",
    TokenType.YARN_LITERAL: r'^".*"$',
    TokenType.TROOF_LITERAL: r"^(WIN|FAIL)$",
    TokenType.COMMENT: r"^(BTW).*",
    TokenType.MULTILINE_COMMENT_START: r"^OBTW$",
    TokenType.MULTILINE_COMMENT_END: r"^TLDR$",
    TokenType.VARIDENT: r"^[A-Za-z_][A-Za-z0-9_]*$",
}

# Helper function to match a regex pattern to a word
def match_regex(regex_pattern, text):
    return re.match(regex_pattern, text) is not None

# Determine the token type based on regex matching
def determine_token_type(word):
    for token_type, regex_pattern in REGEX_PATTERNS.items():
        if match_regex(regex_pattern, word):
            return token_type
    return TokenType.UNKNOWN

# Tokenize a line of text
def tokenize_line(line, in_multiline_comment):
    tokens = []
    line = line.strip()

    # Check if we're inside a multiline comment block
    if in_multiline_comment:
        if match_regex(REGEX_PATTERNS[TokenType.MULTILINE_COMMENT_END], line):
            tokens.append({"type": TokenType.MULTILINE_COMMENT_END, "value": "TLDR"})
            return tokens, False
        return tokens, True

    # Handle inline comments
    if match_regex(REGEX_PATTERNS[TokenType.COMMENT], line):
        tokens.append({"type": TokenType.COMMENT, "value": line})
        return tokens, in_multiline_comment

    # Match multi-word keywords and other tokens
    combined_pattern = r'"[^"]*"|' + REGEX_PATTERNS[TokenType.KEYWORD] + r'|[^\s]+'
    for match in re.finditer(combined_pattern, line):
        token = match.group(0)
        token_type = determine_token_type(token)

        if token_type == TokenType.MULTILINE_COMMENT_START:
            tokens.append({"type": TokenType.MULTILINE_COMMENT_START, "value": "OBTW"})
            in_multiline_comment = True
            break
        tokens.append({"type": token_type, "value": token})

    return tokens, in_multiline_comment

# Main function to read from input.txt and write tokens to output.txt
def main():
    in_multiline_comment = False

    try:
        with open("input.txt", "r") as input_file, open("output.txt", "w") as output_file:
            for line in input_file:
                tokens, in_multiline_comment = tokenize_line(line, in_multiline_comment)
                for token in tokens:
                    output_file.write(f"Token Type: {token['type']}, Value: {token['value']}\n")
        print("Tokenization complete. Check output.txt for results.")
    except FileNotFoundError as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
