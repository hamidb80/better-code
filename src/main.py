import textwrap
import re

import parso

# ----------------------------------------------

def get_all_tokens(node):
    tokens = []
    if hasattr(node, 'children'):
        for child in node.children:
            tokens.extend(get_all_tokens(child))
    else:
        tokens.append(node)
        
    # for token in tokens:
    #     print(f"Token: {repr(token.value)}")
    #     # print(f"  Start: {token.start_pos}")
    #     # print(f"  End:   {token.end_pos}")

    return tokens

def to_repr(node, rules): 
    ret = []
    
    # match node.type:
    # file_input
    # funcdef
    # keyword 
    # name 
    # parameters 
    # operator 
    # param 
    # suite 
    # newline 
    # simple_stmt 
    # expr_stmt 
    # term 
    # trailer
    # return_stmt 
    # arith_expr 
    # atom_expr
    # number 
    # endmarker 
        
    
    if hasattr(node, 'children'):
        for ch in node.children:
            to_repr(ch, rules)

    else:
        rules.get(node.type, [])
        node.value
        
    
    
    
def build_rules_dict(rules_list):
    ret = {}
    for r in rules_list:
        if r[0] not in ret:
            ret[r[0]] = []
        
        # pattern = re.compile(r[1])
        ret[r[0]].append((r[1:]))
        
    return ret


class BetterCode:
    class Node:
        # def keyword(kw):
        #     return ("keyword", kw)
        
        # def name(n):
        #     return ("name", n)
        
        # def number(n):
        #     return ("number", n)
            
        def math(latex):
            return ("math", latex)
        
        def token(node):
            return ("node", node)
        
# ----------------------------------------------

if __name__ == "__main__":
    raw  = """
    def calculate(x, y):
        a,b = x,y
        result = x * y
        result.val.a += 10
        result[1] = 2
    """
    code = textwrap.dedent(raw)
    tree = parso.parse(code)

    print(tree.dump())
    
    rules = build_rules_dict([
        # [score.]node, pattern, repl
        ("name", r"(\w+?)__(\w+)", lambda m: BetterCode.Node.math(f"${m.group(1)}_{m.group(2)}$"))
    ])
    
    output = to_repr(tree, rules)
    print(output)
    print(rules)