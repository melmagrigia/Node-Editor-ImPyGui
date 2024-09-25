import ast

# List of allowed binary and unary operators
ALLOWED_OPERATORS = {
    ast.And, ast.Or, ast.Not,
    ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE,  # Comparisons
}

def is_boolean_expression(expression: str) -> bool:
    try:
        # Parse the expression into an AST
        tree = ast.parse(expression, mode='eval')
        
        # Recursively walk through the AST tree and ensure it only contains allowed elements
        return validate_ast(tree.body)
    
    except (SyntaxError, ValueError):
        return False

def validate_ast(node):
    # Check if the node is a valid constant (True/False) or name (e.g., a variable)
    if isinstance(node, (ast.Constant, ast.Name)):
        return True
    
    # Check if the node is a valid binary operation (e.g., and/or)
    elif isinstance(node, ast.BoolOp):
        return all(validate_ast(value) for value in node.values)
    
    # Check for unary operations (e.g., not)
    elif isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
        return validate_ast(node.operand)
    
    # Check for comparisons (e.g., ==, !=, >, <, >=, <=)
    elif isinstance(node, ast.Compare):
        return all(validate_ast(comp) for comp in node.comparators) and isinstance(node.ops[0], tuple(ALLOWED_OPERATORS))
    
    # Check binary operators like and/or
    elif isinstance(node, ast.BinOp) and isinstance(node.op, (ast.And, ast.Or)):
        return validate_ast(node.left) and validate_ast(node.right)
    
    return False


def check_balanced_parentheses(expression: str) -> bool:
    count = 0
    for char in expression:
        if char == '(':
            count += 1
        elif char == ')':
            count -= 1
        if count < 0:
            return False
    return count == 0

if __name__ == "__main__":
    # Example usage
    expression = "a and (b or not c)"
    if is_boolean_expression(expression):
        print(f"'{expression}' is a valid boolean expression")
    else:
        print(f"'{expression}' is NOT a valid boolean expression")
