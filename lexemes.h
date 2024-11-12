#ifndef LEXEMES_H
#define LEXEMES_H

// Enumerating token types
typedef enum {
    KEYWORD,                        // keywords like HAI, KTHXBYE, etc.
    VARIDENT,                       // variable identifiers (e.g., variable names)
    
    // for literals
    NUMBR_LITERAL,                  // integer 
    NUMBAR_LITERAL,                 // floating point
    YARN_LITERAL,                   // strings (quotes " ")
    TROOF_LITERAL,                  // boolean (WIN or FAIL)

    // for comments
    COMMENT,                        // INLINE COMMENTS
    MULTILINE_COMMENT_START,        // OBTW (start of multiline comment)
    MULTILINE_COMMENT_END,          // TLDR (end of multiline comment)

    // unknown tokens
    UNKNOWN                
} TokenType;

// Structure to define a token
typedef struct {
    TokenType type;        // Token type
    char value[256];       // Token value (up to 256 characters)
} Token;

// Defining regex for token matching
#define REGEX_VARIABLE_IDENTIFIER "^[A-Za-z_][A-Za-z0-9_]*$"
#define REGEX_NUMBR_LITERAL "^-?\\d+$"            // Match integers
#define REGEX_NUMBAR_LITERAL "^-?\\d+\\.\\d+$"    // Match floating point numbers
#define REGEX_YARN_LITERAL "^\"(.*?)\"$"          // Match string literals (strip quotes)
#define REGEX_TROOF_LITERAL "^(WIN|FAIL)$"        // Match boolean literals (WIN/FAIL)
#define REGEX_KEYWORD "\\b(HAI|KTHXBYE|VISIBLE|I HAS A|ITZ|R|SUM OF|DIFF OF|PRODUKT OF|QUOSHUNT OF|MOD OF|BIGGR OF|SMALLR OF|BOTH SAEM|DIFFRINT|O RLY\\?|YA RLY|MEBBE|NOWAI|OIC|WTF\\?|OMG|OMGWTF|IM IN YR|UPPIN|NERFIN|YR|TIL|WILE|IM OUTTA YR|HOW IZ I|IF U SAY SO|GTFO|FOUND YR|MKAY)\\b"
#define REGEX_COMMENT "^(BTW\\b.*)"               // Match inline comments (BTW)
#define REGEX_MULTILINE_COMMENT_START "^OBTW$"    // Start of multiline comment
#define REGEX_MULTILINE_COMMENT_END "^TLDR$"      // End of multiline comment

#endif
