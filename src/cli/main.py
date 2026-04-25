import textwrap
import re

import parso
import shutil

def readfile(path):
    with open(path, 'r') as f:
        return f.read()

def escape_for_katex(text):
    replacements = {
        '\\': '\\\\',
        '{': '\\{',
        '}': '\\}',
        '_': '\\_',
        '&': '\\&',
        '%': '\\%',
        '$': '\\$',
        '#': '\\#',
        '^': '\\^{}',
        '~': '\\textasciitilde{}',
    }
    
    for char, latex_char in replacements.items():
        text = text.replace(char, latex_char)
    return text
# ----------------------------------------------

class MatchRule:
    kind    = None
    
class Name(MatchRule):
    def __init__(self, pattern, replacer):
        self.kind    = "name"
        self.pattern = pattern
        self.repl    = replacer

class Method      (MatchRule):
    def __init__(self):
        self.kind    = "call"

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
        # string
        # strings

        def math(latex):
            return ("math", latex)
        
        def newline():
            return ("newline", None)
        
        def keyword(node):
            return ("keyword", node)

        def string(node):
            return ("string", node)
        
        def other(node):
             return ("other", node)
        
# ----------------------------------------------

def type_match(type, node):
    match type:
        case "name":
            return node.type == "name"
        
        # XXX chain of calls() and picks[] and dots. are inside one `atom_expr`
        case "call":
            return (node.type == "atom_expr")           and \
                   (node.children[0].type == "name")    and \
                   (node.children[1].type == "trailer") and \
                   (node.children[1][0].value == "(")   and \
                   (node.children[1][2].value == ")")
        
        case "pick": # bracket expr
            return (node.type == "atom_expr")           and \
                   (node.children[0].type == "name")    and \
                   (node.children[1].type == "trailer") and \
                   (node.children[1][0].value == "[")   and \
                   (node.children[1][2].value == "]")
                   
        case "dot": ...
        case "method": ...
        case "paren": ...
        
        case "defn": ...
        case "lambda": ...
        case _: ...
        
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
            match node.type:
                case "newline":
                    ret.append(BetterCode.Node.newline())

                case "string":
                    ret.append(BetterCode.Node.string(node))
                
                case  "name":
                    ret.append(BetterCode.Node.math(escape_for_katex(node.value)))
                
                case  "number":
                    ret.append(BetterCode.Node.math(escape_for_katex(node.value)))

                case  "keyword":
                    match node.value:
                        case "or":
                            ret.append(BetterCode.Node.math("\\vee"))
                        case "and":
                            ret.append(BetterCode.Node.math("\\wedge"))
                        case _:
                            ret.append(BetterCode.Node.keyword(node))
                        
                    
                case "operator":
                    match node.value:
                        case "*" : op = r"\times"
                        case "<=": op = r"\leq"
                        case ">=": op = r"\geq"
                        case "=" : op = r"\gets"
                        case "!=": op = r"\neq"
                        case "==": op = r"="
                        case    _: op = None
                    
                    if op:
                        ret.append(BetterCode.Node.math(op))
                    else:
                        ret.append(BetterCode.Node.other(node))
                    
                case _:
                    ret.append(BetterCode.Node.other(node))

    return ret
    

def to_html(ir_list):
    ret  = []
    for r in ir_list:
        kind, data = r
        
        match kind:
            case "space":
                ret.append(f'<span class="space" style="margin-left: {len(data) * 6}px">{data}</span>')
            case "newline":
                ret.append("<br>")
            case "keyword":
                ret.append(f'<span class="keyword">{data.value}</span>')
            case "math":
                ret.append(f'<span class="latex">{data}</span>')
            case "string":
                ret.append(f'<span class="string">{data.value}</span>')
            case _:
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
                
                <link rel="stylesheet" href="/style.css">
                <script defer src="/script.js"></script>
                
                <title>{title}</title>
            </head>
            <body>
            {content}
            </body>
        </html>
        """)
        
    shutil.copyfile("./src/browser/script.js", f"{dest}/script.js")
    shutil.copyfile("./src/browser/style.css", f"{dest}/style.css")
    shutil.copyfile("./node_modules/katex/dist/katex.min.js", f"{dest}/katex.min.js")
    shutil.copyfile("./node_modules/katex/dist/katex.min.css", f"{dest}/katex.min.css")
            
# ----------------------------------------------

# TODO write a matcher like clang-query

if __name__ == "__main__":
    rules = [
        Name(r"(\w+?)__(\w+)", lambda m: BetterCode.Node.math(f"{'{'}{m.group(1)}{'}'}_{'{'}{m.group(2)}{'}'}")),
        Name(r"delta_(\w+)",   lambda m: BetterCode.Node.math(f"\\Delta {'{'}{m.group(1)}{'}'}")),
        Method("dot"),
        Method("mul"),
        # Kw("or", "\\vee"),
        # Kw("and", "\\wedge"),
        # Call("$1.dot($2)", "$1 \\cdot $2"),
        # Call("$1.mul($2)", "$1 \\times $2"),
        # Call("$1 / $2", "$1 \\div $2"),
    ]
    
    raw  = readfile("./test/sample.py")
    code = textwrap.dedent(raw)
    print(code)

    tree = parso.parse(code)
    print(tree.dump())
    
    ir  = to_IR(tree, rules)
    print(ir)
    
    out = to_html(ir)
    build_project(out)