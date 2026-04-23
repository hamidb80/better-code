import parso


code = """
def calculate(x, y):
    result = x * y
    return result + 10
"""
tree = parso.parse(code)

def get_all_tokens(node):
    tokens = []
    if hasattr(node, 'children'):
        for child in node.children:
            tokens.extend(get_all_tokens(child))
    else:
        tokens.append(node)
    return tokens

tokens = get_all_tokens(tree)

for token in tokens:
    print(f"Token: {repr(token.value)}")
    print(f"  Start: {token.start_pos}")
    print(f"  End: {token.end_pos}")
    print()

print(tree.dump())