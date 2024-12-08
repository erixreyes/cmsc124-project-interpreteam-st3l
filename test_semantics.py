# semantics.py

import os
import sys
from lexical import tokenize_line
from lexical import TokenType


# Initialize and manage the symbol table
class SymbolTable:
    def __init__(self):
        self.table = {}

    def declare_variable(self, name, value=None, var_type="NOOB"):
        if name in self.table:
            raise ValueError(f"Variable '{name}' already declared.")
        self.table[name] = {"type": var_type, "value": value}

    def update_variable(self, name, value):
        if name not in self.table:
            raise ValueError(f"Variable '{name}' is not declared.")
        self.table[name]["value"] = value

    def get_variable(self, name):
        if name not in self.table:
            raise ValueError(f"Variable '{name}' is not declared.")
        return self.table[name]

    def to_file(self, file_name="symbol_table.txt"):
        try:
            with open(file_name, "w") as file:
                file.write("=== Symbol Table ===\n")
                file.write("Variable Name\tType\tValue\n")
                file.write("-" * 40 + "\n")
                for name, details in self.table.items():
                    file.write(f"{name}\t\t{details['type']}\t{details['value']}\n")
                file.write("-" * 40 + "\n")
                file.write("=== End of Symbol Table ===\n")
        except IOError as e:
            print(f"Error writing to symbol table file: {e}")


# Interpreted file handling
def initialize_interpreted_file(file_name="interpreted.txt"):
    try:
        with open(file_name, "w") as file:
            file.write("=== Interpreted LOLCODE Output ===\n\n")
    except IOError as e:
        print(f"Error initializing interpreted file: {e}")


def write_to_interpreted_file(line, file_name="interpreted.txt"):
    try:
        with open(file_name, "a") as file:
            file.write(line + "\n")
    except IOError as e:
        print(f"Error writing to interpreted file: {e}")


def finalize_interpreted_file(file_name="interpreted.txt"):
    try:
        with open(file_name, "a") as file:
            file.write("\n=== End of Interpreted LOLCODE ===\n")
    except IOError as e:
        print(f"Error finalizing interpreted file: {e}")


def semantic_analysis(tokens, symbol_table):
    # Skip comments (BTW)
    if not tokens or tokens[0]["type"] == TokenType.COMMENT:
        return symbol_table  # Skip processing empty lines or comments

    # Ensure there are enough tokens to proceed
    if len(tokens) < 2 and tokens[0]["type"] not in [TokenType.KEYWORD]:
        raise ValueError(f"Insufficient tokens for analysis: {tokens}")

    first_token = tokens[0]["value"]

    # Variable declaration (e.g., "I HAS A var")
    if first_token == "I" and tokens[1]["value"] == "HAS" and tokens[2]["value"] == "A":
        if len(tokens) < 4:
            raise ValueError(f"Invalid variable declaration: {tokens}")
        var_name = tokens[3]["value"]
        value = None
        var_type = "NOOB"
        if len(tokens) > 4 and tokens[4]["value"] == "ITZ":
            if len(tokens) < 6:
                raise ValueError(f"Invalid ITZ initialization: {tokens}")
            value = tokens[5]["value"]
            var_type = infer_type(value)
        symbol_table.declare_variable(var_name, value, var_type)

    # Assignment (e.g., "var R SUM OF var AN 10")
    elif len(tokens) > 1 and tokens[1]["value"] == "R":
        var_name = tokens[0]["value"]
        if len(tokens) < 3:
            raise ValueError(f"Invalid assignment: {tokens}")
        operation = tokens[2]["value"]
        operands = [token["value"] for token in tokens[3:]]
        if operation in ["SUM OF", "DIFF OF", "PRODUKT OF", "QUOSHUNT OF", "MOD OF", "BIGGR OF", "SMALLR OF"]:
            result = arithmeticAnalyzer(operation, operands, symbol_table)
        elif operation in ["BOTH OF", "EITHER OF", "WON OF", "NOT", "ANY OF", "ALL OF"]:
            result = logicalAnalyzer(operation, operands, symbol_table)
        else:
            raise ValueError(f"Unsupported operation: {operation}")
        symbol_table.update_variable(var_name, result)

    # VISIBLE (output) statement
    elif first_token == "VISIBLE":
        if len(tokens) < 2:
            raise ValueError(f"VISIBLE requires an argument: {tokens}")

        expression = [token["value"] for token in tokens[1:]]

        # Check that all tokens in the expression are valid (either literals or declared variables)
        for expr_token in expression:
            if expr_token not in symbol_table.table and not expr_token.startswith('"') and expr_token not in ["WIN", "FAIL"]:
                raise ValueError(f"Invalid token in VISIBLE statement: {expr_token}")
        
        # Evaluate the expression and output the result
        result = outputEvaluator(expression, symbol_table)
        print(result)
        write_to_interpreted_file(result)


    # Handle other statements (e.g., GIMMEH, flow control, etc.)
    elif first_token == "GIMMEH":
        if len(tokens) < 2:
            raise ValueError(f"GIMMEH requires a variable name: {tokens}")
        variable = tokens[1]["value"]
        inputHandler(variable, symbol_table)

    return symbol_table





# Helper function for type inference
def infer_type(value):
    """
    Infer the type of a given value for the symbol table.
    """
    try:
        if "." in value:
            float(value)
            return "NUMBAR"
        else:
            int(value)
            return "NUMBR"
    except ValueError:
        if value in ["WIN", "FAIL"]:
            return "TROOF"
        elif value.startswith('"') and value.endswith('"'):
            return "YARN"
        return "UNKNOWN"



# Analyzers to implement
# place arithmeticAnalyzer here
def arithmeticAnalyzer(operation, operands, symbol_table):
    """
    Perform arithmetic operations based on the LOLCODE tokens.
    :param operation: The arithmetic operation (e.g., 'SUM OF').
    :param operands: A list of operands (variable names or literals).
    :param symbol_table: The current symbol table.
    :return: The computed result of the operation.
    """
    # Supported operations
    operations = {
        "SUM OF": lambda x, y: x + y,
        "DIFF OF": lambda x, y: x - y,
        "PRODUKT OF": lambda x, y: x * y,
        "QUOSHUNT OF": lambda x, y: x / y if y != 0 else None,
        "MOD OF": lambda x, y: x % y,
        "BIGGR OF": lambda x, y: max(x, y),
        "SMALLR OF": lambda x, y: min(x, y),
    }

    # Ensure the operation is valid
    if operation not in operations:
        raise ValueError(f"Unsupported operation: {operation}")

    # Resolve operands
    resolved_operands = []
    for operand in operands:
        if operand in symbol_table.table:
            resolved_operands.append(symbol_table.table[operand]["value"])
        else:
            try:
                resolved_operands.append(float(operand))  # Try interpreting as a number
            except ValueError:
                raise ValueError(f"Invalid operand: {operand}")

    # Ensure exactly two operands
    if len(resolved_operands) != 2:
        raise ValueError(f"{operation} requires exactly two operands, got {len(resolved_operands)}")

    # Perform the operation
    result = operations[operation](resolved_operands[0], resolved_operands[1])
    if result is None:
        raise ZeroDivisionError("Division by zero in arithmetic operation")

    return result

# place logicalAnalyzer here
def logicalAnalyzer(operation, operands, symbol_table):
    """
    Perform logical operations based on the LOLCODE tokens.
    :param operation: The logical operation (e.g., 'BOTH OF').
    :param operands: A list of operands (variable names or literals).
    :param symbol_table: The current symbol table.
    :return: The computed result of the operation ('WIN' or 'FAIL').
    """
    # Supported operations
    operations = {
        "BOTH OF": lambda x, y: "WIN" if x == "WIN" and y == "WIN" else "FAIL",
        "EITHER OF": lambda x, y: "WIN" if x == "WIN" or y == "WIN" else "FAIL",
        "WON OF": lambda x, y: "WIN" if (x == "WIN") ^ (y == "WIN") else "FAIL",
        "NOT": lambda x: "FAIL" if x == "WIN" else "WIN",
    }

    # Resolve operands
    resolved_operands = []
    for operand in operands:
        if operand in symbol_table.table:
            value = symbol_table.table[operand]["value"]
            resolved_operands.append("WIN" if value else "FAIL")
        elif operand in ["WIN", "FAIL"]:
            resolved_operands.append(operand)
        else:
            raise ValueError(f"Invalid operand for logical operation: {operand}")

    # Handle unary operations like 'NOT'
    if operation == "NOT":
        if len(resolved_operands) != 1:
            raise ValueError("NOT requires exactly one operand")
        return operations[operation](resolved_operands[0])

    # Handle binary operations
    if len(resolved_operands) != 2:
        raise ValueError(f"{operation} requires exactly two operands")
    return operations[operation](resolved_operands[0], resolved_operands[1])

def evaluate_expression(tokens, symbol_table):
    """
    Evaluate a complex expression (e.g., SUM OF 3 AN 5).
    :param tokens: A list of tokens representing the expression.
    :param symbol_table: The current symbol table.
    :return: The evaluated result.
    """
    if len(tokens) < 3 or tokens[1] != "OF":
        raise ValueError(f"Invalid expression: {tokens}")
    
    operation = tokens[0]
    operands = tokens[2:]  # Skip the operation and "OF"
    
    # Resolve operands
    resolved_operands = []
    for operand in operands:
        if operand in symbol_table.table:
            resolved_operands.append(symbol_table.table[operand]["value"])
        else:
            try:
                resolved_operands.append(float(operand))
            except ValueError:
                raise ValueError(f"Invalid operand in expression: {operand}")
    
    # Handle arithmetic operations
    if operation == "SUM OF":
        return sum(resolved_operands)
    elif operation == "DIFF OF":
        return resolved_operands[0] - resolved_operands[1]
    elif operation == "PRODUKT OF":
        return resolved_operands[0] * resolved_operands[1]
    elif operation == "QUOSHUNT OF":
        if resolved_operands[1] == 0:
            raise ZeroDivisionError("Division by zero in expression")
        return resolved_operands[0] / resolved_operands[1]
    elif operation == "BIGGR OF":
        return max(resolved_operands)
    elif operation == "SMALLR OF":
        return min(resolved_operands)
    else:
        raise ValueError(f"Unsupported operation: {operation}")


# place outputEvaluator here
def outputEvaluator(expression, symbol_table):
    """
    Evaluate and return the result of a VISIBLE statement.
    """
    result = []
    for token in expression:
        if token in symbol_table.table:  # Variable
            value = symbol_table.table[token]["value"]
            if value is None:
                value = "NOOB"  # Default for uninitialized variables
            result.append(str(value))
        elif token.startswith('"') and token.endswith('"'):  # String literal
            result.append(token.strip('"'))
        elif token in ["WIN", "FAIL"]:  # TROOF literals
            result.append(token)
        else:
            try:
                result.append(str(float(token)))  # Numeric literals
            except ValueError:
                raise ValueError(f"Invalid token in VISIBLE statement: {token}")
    return " ".join(result)



# place concatenationAnalyzer here
def concatenationAnalyzer(operands, symbol_table):
    """
    Concatenate strings or variable values based on LOLCODE's SMOOSH operation.
    :param operands: A list of operands (variables or literals).
    :param symbol_table: The current symbol table.
    :return: The concatenated string.
    """
    result = []
    for operand in operands:
        if operand in symbol_table.table:
            result.append(str(symbol_table.table[operand]["value"]))
        elif operand.startswith('"') and operand.endswith('"'):  # String literal
            result.append(operand.strip('"'))
        else:
            try:
                result.append(str(float(operand)))  # Numeric literal
            except ValueError:
                raise ValueError(f"Invalid operand for concatenation: {operand}")
    return "".join(result)


# place flowControlAnalyzer here
def flowControlAnalyzer(condition, if_block, else_block, symbol_table):
    """
    Evaluate flow control statements like O RLY?, YA RLY, NO WAI.
    :param condition: The condition to evaluate (TROOF).
    :param if_block: The block to execute if condition is true.
    :param else_block: The block to execute if condition is false.
    :param symbol_table: The current symbol table.
    :return: The updated symbol table after executing the block.
    """
    # Evaluate the condition
    if condition in symbol_table.table:
        condition_value = symbol_table.table[condition]["value"]
    else:
        condition_value = condition

    if condition_value == "WIN":
        for statement in if_block:
            symbol_table = semantic_analysis(statement, symbol_table)
    elif condition_value == "FAIL" and else_block is not None:
        for statement in else_block:
            symbol_table = semantic_analysis(statement, symbol_table)

    return symbol_table


# place typeCastingAnalyzer here
def typeCastingAnalyzer(variable, target_type, symbol_table):
    """
    Perform type casting of a variable to a specified type.
    :param variable: The variable to cast.
    :param target_type: The target type (NUMBR, NUMBAR, YARN, TROOF).
    :param symbol_table: The current symbol table.
    :return: The updated value after casting.
    """
    if variable not in symbol_table.table:
        raise ValueError(f"Variable '{variable}' is not declared.")

    current_value = symbol_table.table[variable]["value"]
    if target_type == "NUMBR":
        new_value = int(float(current_value)) if current_value else 0
    elif target_type == "NUMBAR":
        new_value = float(current_value) if current_value else 0.0
    elif target_type == "YARN":
        new_value = str(current_value)
    elif target_type == "TROOF":
        new_value = "WIN" if current_value else "FAIL"
    else:
        raise ValueError(f"Invalid target type: {target_type}")

    symbol_table.update_variable(variable, new_value)
    symbol_table.table[variable]["type"] = target_type
    return new_value


# place inputHandler here
def inputHandler(variable, symbol_table):
    """
    Get user input and store it in the specified variable.
    :param variable: The variable to store the input.
    :param symbol_table: The current symbol table.
    """
    user_input = input(f"Input for {variable}: ")
    try:
        # Try casting to NUMBAR or NUMBR if possible
        if "." in user_input:
            user_input = float(user_input)
            var_type = "NUMBAR"
        else:
            user_input = int(user_input)
            var_type = "NUMBR"
    except ValueError:
        if user_input in ["WIN", "FAIL"]:
            var_type = "TROOF"
        else:
            var_type = "YARN"

    symbol_table.update_variable(variable, user_input)
    symbol_table.table[variable]["type"] = var_type


# place loopHandler here
def loopHandler(loop_condition, body_statements, symbol_table):
    """
    Execute a loop based on the condition.
    :param loop_condition: The condition for the loop (TIL or WILE).
    :param body_statements: The statements inside the loop.
    :param symbol_table: The current symbol table.
    :return: The updated symbol table.
    """
    while True:
        condition_value = symbol_table.table[loop_condition]["value"] if loop_condition in symbol_table.table else loop_condition
        if (loop_condition == "TIL" and condition_value == "WIN") or (loop_condition == "WILE" and condition_value == "FAIL"):
            break
        for statement in body_statements:
            symbol_table = semantic_analysis(statement, symbol_table)
    return symbol_table

    import sys

def log_error(message, error_log_file="error_log.txt"):
    """
    Log an error message to the error log file.
    :param message: The error message to log.
    :param error_log_file: The name of the error log file.
    """
    try:
        with open(error_log_file, "a") as file:
            file.write(message + "\n")
        print(f"Error logged: {message}")
    except IOError as e:
        print(f"Error writing to log file '{error_log_file}': {e}")


# Ensure the rest of the semantic analysis and analyzers are implemented as described above.

def main(input_file, interpreted_file="interpreted.txt", symbol_table_file="symbol_table.txt"):
    """
    Main function to run the LOLCODE interpreter.
    :param input_file: Path to the LOLCODE file to interpret.
    :param interpreted_file: Path to the output interpreted file.
    :param symbol_table_file: Path to the output symbol table file.
    """
    # Initialize output files
    initialize_interpreted_file(interpreted_file)
    symbol_table = SymbolTable()  # Initialize the symbol table

    try:
        # Read the input LOLCODE file
        with open(input_file, "r") as file:
            lines = file.readlines()

        # Initialize multi-line comment tracking
        in_multiline_comment = False

        # Process each line of LOLCODE
        for line in lines:
            try:
                tokens, in_multiline_comment = tokenize_line(line.strip(), in_multiline_comment)
                if tokens:
                    symbol_table = semantic_analysis(tokens, symbol_table)
            except Exception as e:
                log_error(f"Error processing line: {line.strip()} -> {e}")


        # Write the final symbol table to the file
        symbol_table.to_file(symbol_table_file)

        # Finalize the interpreted file
        finalize_interpreted_file(interpreted_file)

        print(f"Interpretation complete. Outputs written to:\n- {interpreted_file}\n- {symbol_table_file}")

    except Exception as e:
        log_error(f"Critical error during interpretation: {e}")
        print(f"Critical error during interpretation. See 'error_log.txt' for details.")


if __name__ == "__main__":
    # Ensure the LOLCODE file is provided as a command-line argument
    if len(sys.argv) != 2:
        print("Usage: python semantics.py <input_file>")
    else:
        input_file = sys.argv[1]
        main(input_file)
