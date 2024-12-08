def initialize_interpreted_file(file_name="interpreted.txt"):
    """
    Initialize the interpreted.txt file for writing LOLCODE translations.
    If the file already exists, it clears its contents.
    """
    try:
        with open(file_name, "w") as file:
            file.write("=== Interpreted LOLCODE Output ===\n\n")
        print(f"File '{file_name}' initialized successfully.")
    except IOError as e:
        print(f"Error initializing file '{file_name}': {e}")


def write_to_interpreted_file(line, file_name="interpreted.txt"):
    """
    Append a single line of interpreted LOLCODE to the interpreted.txt file.
    :param line: The line of interpreted LOLCODE to write.
    :param file_name: The name of the file (default is "interpreted.txt").
    """
    try:
        with open(file_name, "a") as file:
            file.write(line + "\n")
    except IOError as e:
        print(f"Error writing to file '{file_name}': {e}")


def finalize_interpreted_file(file_name="interpreted.txt"):
    """
    Append a footer to the interpreted.txt file indicating the end of interpretation.
    :param file_name: The name of the file (default is "interpreted.txt").
    """
    try:
        with open(file_name, "a") as file:
            file.write("\n=== End of Interpreted LOLCODE ===\n")
        print(f"File '{file_name}' finalized successfully.")
    except IOError as e:
        print(f"Error finalizing file '{file_name}': {e}")

