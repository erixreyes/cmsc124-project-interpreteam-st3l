#include <stdio.h>
#include <string.h>
#include <regex.h>
#include <stdbool.h>
#include "lexemes.h"

// Function to match a regex pattern against a given text
bool match_regex(const char *pattern, const char *text, char *matched_text, size_t max_length) {
    regex_t regex;
    regmatch_t match;
    int result;

    // Compile the regex pattern
    result = regcomp(&regex, pattern, REG_EXTENDED);
    if (result != 0) {
        fprintf(stderr, "Error compiling regex.\n");
        return false;
    }

    // Execute regex match
    result = regexec(&regex, text, 1, &match, 0);
    if (result == 0 && match.rm_so != -1) { // Check if match is found
        size_t length = match.rm_eo - match.rm_so;
        if (length < max_length) {
            strncpy(matched_text, text + match.rm_so, length);
            matched_text[length] = '\0'; // Null-terminate the string
        }
        regfree(&regex);
        return true;
    }

    regfree(&regex);
    return false;
}

// Tokenize function that reads from input.txt and writes to output.txt
void tokenize() {
    FILE *input_file = fopen("input.txt", "r");
    FILE *output_file = fopen("output.txt", "w");

    if (input_file == NULL) {
        fprintf(stderr, "Failed to open input.txt for reading.\n");
        return;
    }
    if (output_file == NULL) {
        fprintf(stderr, "Failed to open output.txt for writing.\n");
        fclose(input_file);
        return;
    }

    char source_code[1024];
    char matched_text[256];
    int index = 0;

    // Read the entire input file into source_code
    fread(source_code, sizeof(char), 1024, input_file);
    fclose(input_file);

    // Tokenize the source_code
    while (source_code[index] != '\0') {
        // Skip whitespace but not newlines
        if (match_regex(REGEX_WHITESPACE, &source_code[index], matched_text, sizeof(matched_text))) {
            index += strlen(matched_text);
            continue;
        }

        // Check for newline token
        if (match_regex(REGEX_NEWLINE, &source_code[index], matched_text, sizeof(matched_text))) {
            fprintf(output_file, "Token: NEWLINE\n");
            index += strlen(matched_text);
            continue;
        }

        // Try to match each regex pattern and print the corresponding token type and value
        if (match_regex(REGEX_KEYWORD, &source_code[index], matched_text, sizeof(matched_text))) {
            fprintf(output_file, "Token: KEYWORD, Value: %s\n", matched_text);
            index += strlen(matched_text);
        } else if (match_regex(REGEX_NUMBR_LITERAL, &source_code[index], matched_text, sizeof(matched_text))) {
            fprintf(output_file, "Token: NUMBR_LITERAL, Value: %s\n", matched_text);
            index += strlen(matched_text);
        } else if (match_regex(REGEX_NUMBAR_LITERAL, &source_code[index], matched_text, sizeof(matched_text))) {
            fprintf(output_file, "Token: NUMBAR_LITERAL, Value: %s\n", matched_text);
            index += strlen(matched_text);
        } else if (match_regex(REGEX_YARN_LITERAL, &source_code[index], matched_text, sizeof(matched_text))) {
            fprintf(output_file, "Token: YARN_LITERAL, Value: %s\n", matched_text);
            index += strlen(matched_text);
        } else if (match_regex(REGEX_TROOF_LITERAL, &source_code[index], matched_text, sizeof(matched_text))) {
            fprintf(output_file, "Token: TROOF_LITERAL, Value: %s\n", matched_text);
            index += strlen(matched_text);
        } else if (match_regex(REGEX_COMMENT, &source_code[index], matched_text, sizeof(matched_text))) {
            fprintf(output_file, "Token: COMMENT, Value: %s\n", matched_text);
            index += strlen(matched_text);
        } else if (match_regex(REGEX_MULTILINE_COMMENT_START, &source_code[index], matched_text, sizeof(matched_text))) {
            fprintf(output_file, "Token: MULTILINE_COMMENT_START, Value: %s\n", matched_text);
            index += strlen(matched_text);
        } else if (match_regex(REGEX_MULTILINE_COMMENT_END, &source_code[index], matched_text, sizeof(matched_text))) {
            fprintf(output_file, "Token: MULTILINE_COMMENT_END, Value: %s\n", matched_text);
            index += strlen(matched_text);
        } else if (match_regex(REGEX_VARIABLE_IDENTIFIER, &source_code[index], matched_text, sizeof(matched_text))) {
            fprintf(output_file, "Token: VARIDENT, Value: %s\n", matched_text);
            index += strlen(matched_text);
        } else {
            fprintf(output_file, "Unexpected character at index %d: %c\n", index, source_code[index]);
            index++;
        }
    }

    fclose(output_file); // Close the file after tokenization
}

int main() {
    tokenize();
    return 0;
}
