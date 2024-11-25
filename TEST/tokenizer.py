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
    UNKNOWN = "UNKNOWN"

# Keywords used
KEYWORDS = [
    "HAI", "KTHXBYE", "WAZZUP", "BUHBYE", "BTW", "OBTW", "TLDR", "I HAS A", 
    "ITZ", "R", "SUM OF", "DIFF OF", "PRODUKT OF", "QUOSHUNT OF", "MOD OF", "BIGGR OF", "SMALLR OF", 
    "BOTH OF", "EITHER OF", "WON OF", "NOT", "ANY OF", "ALL OF", "BOTH SAEM", "DIFFRINT", "SMOOSH", "MAEK", 
    "A", "IS NOW A", "VISIBLE", "GIMMEH", "O RLY?", "YA RLY", "MEBBE", "NO WAI", "OIC", "WTF?", "OMG", "OMGWTF", 
    "IM IN YR", "UPPIN", "NERFIN", "YR", "TIL", "WILE", "IM OUTTA YR", "HOW IZ I", "IF U SAY SO", "GTFO", 
    "FOUND YR", "I IZ", "MKAY", "AN"
]

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
}

# Helper function to match a regex pattern to a word
def match_regex(regex_pattern, text):
    return re.match(regex_pattern, text) is not None

# Determine the token type based on regex matching
def determine_token_type(word):
    # Check for MULTILINE_COMMENT_START and MULTILINE_COMMENT_END first
    if match_regex(REGEX_PATTERNS[TokenType.MULTILINE_COMMENT_START], word):
        return TokenType.MULTILINE_COMMENT_START
    if match_regex(REGEX_PATTERNS[TokenType.MULTILINE_COMMENT_END], word):
        return TokenType.MULTILINE_COMMENT_END
    
    # Check for inline comments (BTW)
    if match_regex(REGEX_PATTERNS[TokenType.COMMENT], word):
        return TokenType.COMMENT

    # Check other token types in order
    for token_type, regex_pattern in REGEX_PATTERNS.items():
        if token_type in [TokenType.MULTILINE_COMMENT_START, TokenType.MULTILINE_COMMENT_END, TokenType.COMMENT]:
            continue  # Already handled above
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

    # Check if the line contains a BTW comment
    match = re.match(REGEX_PATTERNS[TokenType.COMMENT], line)
    if match:
        before_btw = line[:match.start()].strip()
        comment_content = match.group(2).strip()

        # Tokenize the part before BTW
        combined_pattern = r'"[^"]*"|' + REGEX_PATTERNS[TokenType.KEYWORD] + r'|[^\s]+'
        for match in re.finditer(combined_pattern, before_btw):
            token = match.group(0)
            token_type = determine_token_type(token)
            tokens.append({"type": token_type, "value": token})

        # Add the entire comment part as a COMMENT token
        tokens.append({"type": TokenType.COMMENT, "value": "BTW " + comment_content})
        return tokens, False  # No further processing for this line

    # Match multi-word keywords and other tokens
    combined_pattern = r'"[^"]*"|' + REGEX_PATTERNS[TokenType.KEYWORD] + r'|[^\s]+'
    for match in re.finditer(combined_pattern, line):
        token = match.group(0)
        token_type = determine_token_type(token)
        tokens.append({"type": token_type, "value": token})

    return tokens, False

# Main function to read from input.txt and write tokens to output.txt
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
