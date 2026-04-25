import textwrap
import re

import parso
import shutil

def readfile(path):
    with open(path, 'r') as f:
        return f.read()

# ----------------------------------------------

class MatchRule:
    kind    = None
    
class Name(MatchRule):
    def __init__(self, pattern, replacer):
        self.kind    = "name"
        self.pattern = pattern
        self.repl    = replacer

class Call(MatchRule):
    def __init__(self):
        self.kind    = "call"
        
      
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

def type_match(type, node):
    match type:
        case "name":
            return node.type == "name"
        
        case "call":
            return None
        
        case _:
            return None

def apply_rule(rule: MatchRule, node):
    if type_match(rule.kind, node):
        if node.type == "name":
            val = node.value
            m = re.match(rule.pattern, val)
            if m:
                return rule.repl(m)

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
            res = apply_rule(rule, node)
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

def build_project(content, dest="./dist", title="better code"):
    with open(f"{dest}/index.html", "w") as f:
        f.write(f"""
        <!DOCTYPE html>
            <html>
            <head>
                <link rel="stylesheet" href="/katex.min.css">
                <script defer src="/katex.min.js"></script>
                <script defer src="/script.js"></script>
                
                <title>{title}</title>
            </head>
            <body>
            {content}
            </body>
        </html>
        """)
        
    shutil.copyfile("./src/browser/script.js", f"{dest}/script.js")
    shutil.copyfile("./node_modules/katex/dist/katex.min.js", f"{dest}/katex.min.js")
    shutil.copyfile("./node_modules/katex/dist/katex.min.css", f"{dest}/katex.min.css")
            
# ----------------------------------------------

if __name__ == "__main__":
    raw  = readfile("./test/sample.py")
    rules = [
        Name(r"(\w+?)__(\w+)", lambda m: BetterCode.Node.math(f"{'{'}{m.group(1)}{'}'}_{'{'}{m.group(2)}{'}'}")),
        Name(r"delta_(\w+)",   lambda m: BetterCode.Node.math(f"\\Delta {'{'}{m.group(1)}{'}'}")),
        Call(),
    ]
    
    
    code = textwrap.dedent(raw)
    print(code)

    tree = parso.parse(code)
    print(tree.dump())
    
    ir  = to_IR(tree, rules)
    print(ir)
    
    out = to_html(ir)
    print(out)

    build_project(out)