import sys
import os

# Redirect output to interpreted.txt
sys.stdout = open("interpreted.txt", "w")


def typecast_to_troof(value, value_type):
    """Typecast values to TROOF Literal (Boolean)."""
    if value_type == "TROOF Literal":
        return 1 if value == "WIN" else 0
    elif value_type == "YARN Literal":
        return 1 if value.strip() else 0
    elif value_type in ["NUMBR Literal", "NUMBAR Literal"]:
        return 1 if float(value) != 0 else 0
    raise TypeError(f"Cannot cast type '{value_type}' to TROOF.")


def boolean_op(value1, type1, value2, type2, op):
    """Evaluate boolean operations."""
    value1 = typecast_to_troof(value1, type1)
    value2 = typecast_to_troof(value2, type2)

    if op == "BOTH OF":
        return "WIN" if value1 and value2 else "FAIL", "TROOF Literal"
    elif op == "EITHER OF":
        return "WIN" if value1 or value2 else "FAIL", "TROOF Literal"
    elif op == "WON OF":
        return "WIN" if value1 != value2 else "FAIL", "TROOF Literal"
    elif op == "NOT":
        return "WIN" if not value1 else "FAIL", "TROOF Literal"


def comparison_op(value1, type1, value2, type2, op):
    """Evaluate comparison operations."""
    if type1 != type2:
        raise TypeError(f"Type mismatch between {type1} and {type2}")

    if type1 == "NUMBR Literal":
        value1 = int(value1)
        value2 = int(value2)
    else:
        value1 = float(value1)
        value2 = float(value2)

    if op == "BOTH SAEM":
        return "WIN" if value1 == value2 else "FAIL", "TROOF Literal"
    elif op == "DIFFRINT":
        return "WIN" if value1 != value2 else "FAIL", "TROOF Literal"


def arithmetic_op(value1, type1, value2, type2, op):
    """Evaluate arithmetic operations."""
    if type1 != type2:
        raise TypeError(f"Type mismatch between {type1} and {type2}")

    if type1 == "NUMBR Literal":
        value1 = int(value1)
        value2 = int(value2)
    else:
        value1 = float(value1)
        value2 = float(value2)

    if op == "SUM OF":
        return value1 + value2, type1
    elif op == "DIFF OF":
        return value1 - value2, type1
    elif op == "PRODUKT OF":
        return value1 * value2, type1
    elif op == "QUOSHUNT OF":
        if value2 == 0:
            raise ZeroDivisionError("Division by zero.")
        return value1 / value2, type1
    elif op == "MOD OF":
        if value2 == 0:
            raise ZeroDivisionError("Modulo by zero.")
        return value1 % value2, type1
    elif op == "BIGGR OF":
        return max(value1, value2), type1
    elif op == "SMALLR OF":
        return min(value1, value2), type1


def smoosh(values):
    """Concatenate values as strings."""
    return "".join(map(str, values)), "YARN Literal"


def get_input(prompt):
    """Handle user input."""
    try:
        return input(f"{prompt}: ")
    except EOFError:
        raise RuntimeError("Input failed.")


# Main Execution
def main():
    if len(sys.argv) < 2:
        print("Usage: python semantics.py <lolcode_file>")
        return

    lolcode_file = sys.argv[1]

    if not os.path.exists(lolcode_file):
        print(f"Error: File '{lolcode_file}' not found.")
        return

    # Ensure the input file is used for the lexical analyzer
    with open("input.txt", "w") as input_file:
        with open(lolcode_file, "r") as lolcode:
            input_file.write(lolcode.read())

    try:
        # Step 1: Tokenization using lexical.py
        from lexical import main as lexical_main
        lexical_main()

        # Step 2: Parsing and execution using new_parse.py
        from new_parse import main as parse_main
        parse_main()

    except Exception as e:
        print(f"Error during interpretation: {e}")


if __name__ == "__main__":
    main()
