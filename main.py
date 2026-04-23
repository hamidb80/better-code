import ast

import tokenize
import io
from token import NAME  # Import specific token types for filtering

# tree = ast.parse(code)
# print(ast.dump(tree, indent=2))

def to_AST(code):
    return ast.parse(code)

def to_tokens(code):
  readline = io.BytesIO(code.encode('utf-8')).readline
  return [*tokenize.tokenize(readline)]


def print_ast(code, indent=0, show_attrs=True, show_location=True):
    """Pretty print AST tree structure with location info"""
    node = to_AST(code)
    prefix = "  " * indent
    
    # Get node info
    node_name = node.__class__.__name__
    
    # Format location info
    location = ""
    if show_location and hasattr(node, 'lineno'):
        start = f"{node.lineno}:{node.col_offset}"
        if hasattr(node, 'end_lineno') and hasattr(node, 'end_col_offset'):
            end = f"{node.end_lineno}:{node.end_col_offset}"
            location = f" [{start} - {end}]"
        else:
            location = f" [line {node.lineno}]"
    
    print(f"{prefix}├─ {node_name}{location}", end="")
    
    # Show important attributes
    if show_attrs:
        attrs = []
        if hasattr(node, 'name') and not node_name == 'Name':
            attrs.append(f"name='{node.name}'")
        if hasattr(node, 'id'):
            attrs.append(f"id='{node.id}'")
        if hasattr(node, 'value') and node_name in ['Constant']:
            attrs.append(f"value={node.value}")
        if hasattr(node, 'ctx'):
            ctx_name = node.ctx.__class__.__name__
            attrs.append(f"ctx={ctx_name}")
        if attrs:
            print(f" ({', '.join(attrs)})")
        else:
            print()
    else:
        print()
    
    # Recursively print children
    children = list(ast.iter_child_nodes(node))
    for i, child in enumerate(children):
        is_last = (i == len(children) - 1)
        print_ast(child, indent + 1, show_attrs, show_location)

def print_tokens(code):
  for token in to_tokens(code):
      token_name = tokenize.tok_name[token.type]
      print(f"Type: {token_name} ({token.type})"
            f" | Value: {repr(token.string)} "
            f" | Line: {token.start[0]}:{token.start[1]} .. {token.end[0]}:{token.end[1]}")

# def make_sense(tokens, )

# ----------------------------------------------

code = """
def calculate(x, y):
    # 1 1 1
    # 2 2 2
    result = x * y
    return result + 10
"""

print_ast(code)
print_tokens(code)
