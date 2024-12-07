symbol_table = []  # Store variables
functions = {}  # Store for functions


def get_identifiers(symbol_table):
    return [i[0] for i in symbol_table]


def symboltable_insert(symbol_table, new_identifier, new_val, datatype):
    if new_identifier not in get_identifiers(symbol_table):
        symbol_table.append([new_identifier, new_val, datatype])
    else:
        d_index = get_identifiers(symbol_table).index(new_identifier)
        symbol_table[d_index] = [new_identifier, new_val, datatype]


def find_value(symbol_table, identifier):
    for var in symbol_table:
        if var[0] == identifier:
            return [var[1], var[2]]
    return False


def typecast_to_troof(value, value_type):
    """Typecast values to TROOF Literal (Boolean)."""
    if value_type == "TROOF Literal":
        return 1 if value == "WIN" else 0
    elif value_type != "TROOF Literal":
        if value == "\"\"":
            return 0
        return 1 if int(value) != 0 else 0
    return value


def boolean_op(value1, type1, value2, type2, op):
    value1 = typecast_to_troof(value1, type1)
    value2 = typecast_to_troof(value2, type2)

    if op == "BOTH OF":
        result = value1 and value2
    elif op == "EITHER OF":
        result = value1 or value2
    elif op == "WON OF":
        result = (value1 != value2)

    return "WIN" if result else "FAIL", "TROOF Literal"


def comparison_op(value1, type1, value2, type2, op):
    # Type check before comparison
    if type1 != type2:
        return f"Error: Type mismatch between {type1} and {type2}"

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
    if type1 != type2:
        return f"Error: Type mismatch between {type1} and {type2}"

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
            return "Error: Division by zero", None
        return value1 / value2, type1
    elif op == "MOD OF":
        if value2 == 0:
            return "Error: Modulo by zero", None
        return value1 % value2, type1
    elif op == "BIGGR OF":
        return max(value1, value2), type1
    elif op == "SMALLR OF":
        return min(value1, value2), type1


def get_input(value):
    input_prompt = f"Input value of {value} :"
    x = input(input_prompt)
    return [x, "YARN Literal"] if len(x) else ["", "YARN Literal"]


def insert_function(function_name, params, return_type):
    if function_name in functions:
        return f"Error: Function {function_name} already defined"
    functions[function_name] = {"params": params, "return_type": return_type}
    return None


def check_function_call(function_name, args):
    if function_name not in functions:
        return f"Error: Function {function_name} not defined"
    func = functions[function_name]
    if len(func["params"]) != len(args):
        return f"Error: Incorrect number of arguments for {function_name}"
    for i, (param_type, arg) in enumerate(zip(func["params"], args)):
        if param_type != type(arg).__name__:
            return f"Error: Argument {i+1} type mismatch in {function_name}"
    return None


def print_symbol_table():
    for identifier, value, datatype in symbol_table:
        print(f"{identifier}: {value}")

