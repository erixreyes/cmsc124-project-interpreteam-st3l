#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <regex.h>
#include "lexemes.h"

// Helper function to match a regex pattern to a text
int match_regex(const char *regex_pattern, const char *text) {
    regex_t regex;
    if (regcomp(&regex, regex_pattern, REG_EXTENDED)) {
        fprintf(stderr, "Could not compile regex: %s\n", regex_pattern);
        exit(1);
    }
    int match = regexec(&regex, text, 0, NULL, 0) == 0;
    regfree(&regex);
    return match;
}

// Determine the token type based on regex matching
TokenType determine_token_type(const char *word) {
    if (match_regex(REGEX_KEYWORD, word)) return KEYWORD;
    if (match_regex(REGEX_NUMBR_LITERAL, word)) return NUMBR_LITERAL;
    if (match_regex(REGEX_NUMBAR_LITERAL, word)) return NUMBAR_LITERAL;
    if (match_regex(REGEX_YARN_LITERAL, word)) return YARN_LITERAL;
    if (match_regex(REGEX_TROOF_LITERAL, word)) return TROOF_LITERAL;
    if (match_regex(REGEX_COMMENT, word)) return COMMENT;
    if (match_regex(REGEX_MULTILINE_COMMENT_START, word)) return MULTILINE_COMMENT_START;
    if (match_regex(REGEX_MULTILINE_COMMENT_END, word)) return MULTILINE_COMMENT_END;
    if (match_regex(REGEX_VARIABLE_IDENTIFIER, word)) return VARIDENT;
    return UNKNOWN;
}

// Function to strip quotes from a YARN_LITERAL token
void strip_quotes(char *word) {
    size_t len = strlen(word);
    if (len >= 2 && word[0] == '"' && word[len - 1] == '"') {
        memmove(word, word + 1, len - 2);
        word[len - 2] = '\0';
    }
}

// Function to get a string representation of token types
const char* token_type_to_string(TokenType type) {
    switch (type) {
        case KEYWORD: return "KEYWORD";
        case VARIDENT: return "VARIABLE_IDENTIFIER";
        case NUMBR_LITERAL: return "NUMBR_LITERAL";
        case NUMBAR_LITERAL: return "NUMBAR_LITERAL";
        case YARN_LITERAL: return "YARN_LITERAL";
        case TROOF_LITERAL: return "TROOF_LITERAL";
        case COMMENT: return "COMMENT";
        case MULTILINE_COMMENT_START: return "MULTILINE_COMMENT_START";
        case MULTILINE_COMMENT_END: return "MULTILINE_COMMENT_END";
        default: return "UNKNOWN";
    }
}

// Tokenize a line of text
void tokenize_line(char *line, FILE *output_file) {
    static int in_multiline_comment = 0;

    // Check if we're inside a multiline comment block
    if (in_multiline_comment) {
        if (match_regex(REGEX_MULTILINE_COMMENT_END, line)) {
            fprintf(output_file, "Token Type: MULTILINE_COMMENT_END, Value: TLDR\n");
            in_multiline_comment = 0;
        }
        return;
    }

    // Handle inline comments
    if (match_regex(REGEX_COMMENT, line)) {
        fprintf(output_file, "Token Type: COMMENT, Value: %s", line);
        return;
    }

    // Handle tokens
    char *token = strtok(line, " \t\n");
    while (token != NULL) {
        TokenType type = determine_token_type(token);

        // Check for start of multiline comment
        if (type == MULTILINE_COMMENT_START) {
            fprintf(output_file, "Token Type: MULTILINE_COMMENT_START, Value: OBTW\n");
            in_multiline_comment = 1;
            break;
        }

        // Prepare token struct
        Token current_token;
        current_token.type = type;
        strncpy(current_token.value, token, sizeof(current_token.value) - 1);
        current_token.value[sizeof(current_token.value) - 1] = '\0';

        // Handle yarn literals by stripping quotes
        if (type == YARN_LITERAL) {
            strip_quotes(current_token.value);
        }

        // Write token type and value to output file
        fprintf(output_file, "Token Type: %s, Value: %s\n", token_type_to_string(current_token.type), current_token.value);

        token = strtok(NULL, " \t\n");
    }
}

// Main function to read from input.txt and write tokens to output.txt
int main() {
    FILE *input_file = fopen("input.txt", "r");
    FILE *output_file = fopen("output.txt", "w");

    if (input_file == NULL) {
        fprintf(stderr, "Could not open input.txt\n");
        return 1;
    }
    if (output_file == NULL) {
        fprintf(stderr, "Could not open output.txt\n");
        fclose(input_file);
        return 1;
    }

    char line[1024];
    while (fgets(line, sizeof(line), input_file)) {
        tokenize_line(line, output_file);
    }

    fclose(input_file);
    fclose(output_file);

    printf("Tokenization complete. Check output.txt for results.\n");
    return 0;
}
