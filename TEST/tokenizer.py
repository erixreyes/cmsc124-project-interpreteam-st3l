import re
import json

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
    CONCAT_OPERATOR = "CONCAT_OPERATOR"
    UNKNOWN = "UNKNOWN"

# Keywords used
KEYWORDS = [
    "HAI", "KTHXBYE", "WAZZUP", "BUHBYE", "BTW", "OBTW", "TLDR", "I HAS A", 
    "ITZ", "R", "SUM OF", "DIFF OF", "PRODUKT OF", "QUOSHUNT OF", "MOD OF", "BIGGR OF", "SMALLR OF", 
    "BOTH OF", "EITHER OF", "WON OF", "NOT", "ANY OF", "ALL OF", "BOTH SAEM", "DIFFRINT", "SMOOSH", "MAEK", 
    "A", "IS NOW A", "VISIBLE", "GIMMEH", "O RLY?", "YA RLY", "MEBBE", "NO WAI", "OIC", "TIL", "WILE", 
    "IM IN YR", "IM OUTTA YR", "MKAY", "AN", "NUMBR", "NUMBAR", "YARN", "TROOF"
]

# Multi-word keywords need stricter handling
MULTIWORD_KEYWORDS = sorted([kw for kw in KEYWORDS if " " in kw], key=len, reverse=True)

# RegEx patterns for token types
REGEX_PATTERNS = {
    TokenType.KEYWORD: r"\b(" + "|".join(re.escape(keyword) for keyword in KEYWORDS) + r")\b",
    TokenType.NUMBR_LITERAL: r"^-?[0-9]+$",
    TokenType.NUMBAR_LITERAL: r"^-?[0-9]+\.[0-9]+$",
    TokenType.YARN_LITERAL: r'^".*"$',
    TokenType.TROOF_LITERAL: r"^(WIN|FAIL)$",
    TokenType.COMMENT: r"^(BTW)(.*)$",  # Match BTW and capture the rest as a comment
    TokenType.MULTILINE_COMMENT_START: r"^OBTW$",
    TokenType.MULTILINE_COMMENT_END: r"^TLDR$",
    TokenType.VARIDENT: r"^[A-Za-z_][A-Za-z0-9_]*$",
    TokenType.CONCAT_OPERATOR: r"^\+$",
}

def match_regex(regex_pattern, text):
    """Check if a text matches a regex pattern."""
    return re.match(regex_pattern, text) is not None

def determine_token_type(word):
    """Determine the type of a token."""
    for token_type, regex_pattern in REGEX_PATTERNS.items():
        if match_regex(regex_pattern, word):
            return token_type
    return TokenType.UNKNOWN

def tokenize_line(line, in_multiline_comment):
    tokens = []
    line = line.strip()

    # Handle multi-line comment blocks
    if in_multiline_comment:
        if match_regex(REGEX_PATTERNS[TokenType.MULTILINE_COMMENT_END], line):
            tokens.append({"type": TokenType.MULTILINE_COMMENT_END, "value": "TLDR"})
            return tokens, False  # End of multi-line comment block
        return tokens, True  # Skip processing lines within the comment block

    # Check if the line starts a multi-line comment
    if match_regex(REGEX_PATTERNS[TokenType.MULTILINE_COMMENT_START], line):
        tokens.append({"type": TokenType.MULTILINE_COMMENT_START, "value": "OBTW"})
        return tokens, True  # Enter multi-line comment mode

    # Handle inline comments (BTW)
    if "BTW" in line:
        # Split the line at BTW
        before_btw, btw_comment = line.split("BTW", 1)
        before_btw = before_btw.strip()  # Any tokens before BTW
        btw_comment = btw_comment.strip()  # The comment after BTW

        # Tokenize anything before BTW
        combined_pattern = r'"[^"]*"|' + REGEX_PATTERNS[TokenType.KEYWORD] + r'|[^\s]+'
        for match in re.finditer(combined_pattern, before_btw):
            token = match.group(0)
            token_type = determine_token_type(token)
            tokens.append({"type": token_type, "value": token})

        # Add the entire BTW comment as a single token
        tokens.append({"type": TokenType.COMMENT, "value": "BTW " + btw_comment})
        return tokens, False  # Stop processing this line further

    # Tokenize the rest of the line as usual
    combined_pattern = r'"[^"]*"|' + REGEX_PATTERNS[TokenType.KEYWORD] + r'|[^\s]+'
    for match in re.finditer(combined_pattern, line):
        token = match.group(0)
        token_type = determine_token_type(token)
        tokens.append({"type": token_type, "value": token})

    return tokens, False

def tokenize_string(line):
    """Tokenize a string into separate tokens."""
    tokens = []
    
    # Handle multi-word keywords first
    while line:
        matched = False
        for multiword in MULTIWORD_KEYWORDS:
            if line.startswith(multiword):
                tokens.append({"type": TokenType.KEYWORD, "value": multiword})
                line = line[len(multiword):].strip()
                matched = True
                break
        if matched:
            continue

        # Tokenize remaining parts
        combined_pattern = r'"[^"]*"|' + REGEX_PATTERNS[TokenType.KEYWORD] + r'|\+|[^\s]+'
        for match in re.finditer(combined_pattern, line):
            token = match.group(0)
            token_type = determine_token_type(token)
            tokens.append({"type": token_type, "value": token})
            line = line[len(token):].strip()
            break
        else:
            break  # No match found, exit loop

    return tokens

# Main function
def main():
    in_multiline_comment = False
    try:
        with open("input.txt", "r") as input_file, open("output.txt", "w") as output_file:
            for line in input_file:
                tokens, in_multiline_comment = tokenize_line(line, in_multiline_comment)
                for token in tokens:
                    output_file.write(json.dumps(token) + "\n")
        print("Tokenization complete. Check output.txt for results.")
    except FileNotFoundError as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
