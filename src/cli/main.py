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
        
        def newline():
            return ("newline", None)
        
        def other(node):
             return ("other", node)
        
# ----------------------------------------------

def apply_rule(node, rule):
    if node.type == "name":
        kind, pat, fn = rule
        val = node.value
        m = re.match(pat, val)
        if m:
            return fn(m)

    return None

def to_IR(node, rules): 
    ret = []
    
    if hasattr(node, 'prefix'):
        ret.append(("space", node.prefix))
    
    if hasattr(node, 'children'):
        for ch in node.children:
            for r in to_IR(ch, rules):
                ret.append(r)

    else:
        found = False
        for rule in rules:
            res = apply_rule(node, rule)
            if res:
                found = True
                ret.append(res)
                break
            else:
                pass
                
            
        if not found:
            if node.type == "newline":
                ret.append(BetterCode.Node.newline())

            elif node.type == "operator":
                if   node.value == "*" : op = r"\times"
                elif node.value == "<=": op = r"\leq"
                elif node.value == ">=": op = r"\geq"
                elif node.value == "=": op = r"\gets"
                else: op = None
                
                if op:
                    ret.append(BetterCode.Node.math(op))
                else:
                    ret.append(BetterCode.Node.other(node))
                    
            else:
                ret.append(BetterCode.Node.other(node))

    return ret
    

def to_html(ir_list):
    ret  = []
    for r in ir_list:
        kind, data = r
        
        if kind == "math":
            ret.append(f'<span class="latex">{data}</span>')
        
        elif kind == "space":
            ret.append(f'<span class="space" style="margin-left: {len(data) * 6}px">{data}</span>')
            
        elif kind == "newline":
            ret.append("<br>")
            
        else:
            ret.append(f'<span class="code">{data.value}</span>')
            
            
    return "".join(ret)
            

# def build_rewrite_rules_dict(rules_list):
#     ret = {}
#     for r in rules_list:
#         if r[0] not in ret:
#             ret[r[0]] = []
        
#         # pattern = re.compile(r[1])
#         ret[r[0]].append((r[1:]))
        
#     return ret


# ----------------------------------------------

if __name__ == "__main__":
    raw  = """
    if a >= 5:
        f__T = delta_h * y
        call(1, 2, 3)
        bracket[1, 2, 3]
    """
    rules = [
        # [score.]node, pattern, repl
        ("name", r"(\w+?)__(\w+)", lambda m: BetterCode.Node.math(f"{'{'}{m.group(1)}{'}'}_{'{'}{m.group(2)}{'}'}")),
        ("name", r"delta_(\w+)",   lambda m: BetterCode.Node.math(f"\\Delta {'{'}{m.group(1)}{'}'}")),
        # ("call", r"delta_(\w+)",   lambda m: BetterCode.Node.math(f"\\Delta {'{'}{m.group(1)}{'}'}"))
    ]
    
    
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
                
                <title>better code</title>
            </head>
            <body>
            {out}
            </body>
        </html>
        """)
        
    shutil.copyfile("./src/browser/script.js", "./dist/script.js")
    shutil.copyfile("./node_modules/katex/dist/katex.min.js", "./dist/katex.min.js")
    shutil.copyfile("./node_modules/katex/dist/katex.min.css", "./dist/katex.min.css")