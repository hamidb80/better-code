import textwrap
import re

import parso


class BetterCode:
    class Node:
        
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

        def math(latex):
            return ("math", latex)
        
        def other(node):
             return node
        
# ----------------------------------------------

def test_match(node, rule):
    
    if node.type == "name":
        pat = rule[0]
        txt = node.value 
        res = re.match(pat, txt, re.DOTALL | re.MULTILINE)
        print(":: ", txt, res, pat)
        return res
    
    else:
        return False
    
def apply_rule(node, rule):
    if node.type == "name":
        pat, fn = rule
        val = node.value
        m = re.match(pat, val)
        print(fn , m, f"'{val}'")
        return fn(m)
        
    else:
        return node

def to_IR(node, rules): 
    ret = []
    
    if hasattr(node, 'prefix'):
        ret.append(("space", node.prefix))
    
    if hasattr(node, 'children'):
        for ch in node.children:
            for r in to_IR(ch, rules):
                ret.append(r)

    else:
        matches_rules = rules.get(node.type, [])
        found = False
        for mr in matches_rules:
            if test_match(node, mr):
                found = True
                ret.append(apply_rule(node, mr))
                break
            else:
                pass
                
            
        if not found:
            ret.append(BetterCode.Node.other(node))

    return ret
    

def to_repr(ir_list):
    ret  = []
    for r in ir_list:
        if isinstance(r, tuple):
            kind, data = r
            
            if kind == "math":
                latex = data
                ret.append(latex)
            
            elif kind == "space":
                ret.append(data)
                
            else:
                raise f"{kind} is not defined"
            
        else:
            node = r
            ret.append(node.value)
            
            
    return "".join(ret)
            

def build_rules_dict(rules_list):
    ret = {}
    for r in rules_list:
        if r[0] not in ret:
            ret[r[0]] = []
        
        # pattern = re.compile(r[1])
        ret[r[0]].append((r[1:]))
        
    return ret


# ----------------------------------------------

if __name__ == "__main__":
    raw  = """
    if a > 5:
        f__T = x * y
    """
    code = textwrap.dedent(raw)
    tree = parso.parse(code)

    
    rules = build_rules_dict([
        # [score.]node, pattern, repl
        ("name", r"(\w+?)__(\w+)", lambda m: BetterCode.Node.math(f"${m.group(1)}_{m.group(2)}$"))
    ])
    
    ir  = to_IR(tree, rules)
    out = to_repr(ir)

    print(tree.dump())
    print(ir)
    print(out)
    print(code)
    