#include <stdbool.h>    //standard boolean

#ifndef LEXEMES_H
#define LEXEMES_H

// enumerating token types
typedef enum {
    KEYWORD,                        // keywords like HAI, KTHXBYE, etc.
    VARIDENT,                       // variable identifiers (ex: variable names)
    
    // for literals
    NUMBR_LITERAL,                  // integer 
    NUMBAR_LITERAL,                 // floating point
    YARN_LITERAL,                   // strings (quotes " ")
    TROOF_LITERAL,                  // boolean (WIN or FAIL)

    // for comments
    COMMENT,                        // INLINE COMMENTS
    MULTILINE_COMMENT_START,        // OBTW
    MULTILINE_COMMENT_END,          // TLDR

    // for linebreak
    WHITESPACE,            
    NEWLINE,               

    // unknown tokens
    UNKNOWN                
} TokenType;

// structure to define a toke
typedef struct {
    TokenType type;        // check the token type
    char value[256];       // we set the value of the token to be up until 256 bits
} Token;

// defining based on lexemes milestone (slight adjustments since yung iba nasa grep format)
#define REGEX_VARIABLE_IDENTIFIER "^[A-Za-z_][A-Za-z0-9_]*$"
#define REGEX_FUNCTION_IDENTIFIER "^[A-Za-z_][A-Za-z0-9_]*$"
#define REGEX_LOOP_IDENTIFIER "^[A-Za-z_][A-Za-z0-9_]*$"

#define REGEX_NUMBR_LITERAL "-?\\d+"
#define REGEX_NUMBAR_LITERAL "-?\\d+\\.\\d+"
#define REGEX_YARN_LITERAL "^\".*?\"$"
#define REGEX_TROOF_LITERAL "^(WIN|FAIL)$"
#define REGEX_TYPE_LITERAL "^(NOOB|NUMBR|NUMBAR|YARN|TROOF)$"

#define REGEX_KEYWORD "\\b(HAI|KTHXBYE|VISIBLE|I HAS A|ITZ|R|SUM OF|DIFF OF|PRODUKT OF|QUOSHUNT OF|MOD OF|BIGGR OF|SMALLR OF|BOTH SAEM|DIFFRINT|O RLY\\?|YA RLY|MEBBE|NOWAI|OIC|WTF\\?|OMG|OMGWTF|IM IN YR|UPPIN|NERFIN|YR|TIL|WILE|IM OUTTA YR|HOW IZ I|IF U SAY SO|GTFO|FOUND YR|MKAY)\\b"

#define REGEX_COMMENT "(^|\\s)BTW.*$"
#define REGEX_MULTILINE_COMMENT_START "(?:^|\\n)OBTW"
#define REGEX_MULTILINE_COMMENT_END "(?:^|\\n)TLDR"

#define REGEX_WHITESPACE "\\s+"
#define REGEX_NEWLINE "\\r?\\n"

#endif 
