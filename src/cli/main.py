import textwrap
import re

import parso
import shutil


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
             return ("other", node)
        
# ----------------------------------------------

def test_match(node, rule):
    
    if node.type == "name":
        pat = rule[0]
        txt = node.value 
        res = re.match(pat, txt, re.DOTALL | re.MULTILINE)
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
    

def to_html(ir_list):
    ret  = []
    for r in ir_list:
        kind, data = r
        
        if kind == "math":
            ret.append(f'<span class="latex">{data}</span>')
        
        elif kind == "space":
            ret.append(f'<span class="space" style="margin-left: {len(data) * 3}px">{data}</span>')
            
        else:
            ret.append(f'<span class="code">{data.value}</span>')
            
            
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
    rules = build_rules_dict([
        # [score.]node, pattern, repl
        ("name", r"(\w+?)__(\w+)", lambda m: BetterCode.Node.math(f"{'{'}{m.group(1)}{'}'}_{'{'}{m.group(2)}{'}'}"))
    ])
    
    
    code = textwrap.dedent(raw)
    print(code)

    tree = parso.parse(code)
    print(tree.dump())
    
    ir  = to_IR(tree, rules)
    print(ir)
    
    out = to_html(ir)
    print(out)

    
    with open("./dist/index.html", "w") as f:
        f.write(f"""
        <!DOCTYPE html>
            <html>
            <head>
                <link rel="stylesheet" href="/katex.min.css">
                <script defer src="/katex.min.js"></script>
                <script defer src="/script.js"></script>
            </head>
            <body>
            {out}
            </body>
        </html>
        """)
        
    shutil.copyfile("./src/browser/script.js", "./dist/script.js")
    shutil.copyfile("./node_modules/katex/dist/katex.min.js", "./dist/katex.min.js")
    shutil.copyfile("./node_modules/katex/dist/katex.min.css", "./dist/katex.min.css")