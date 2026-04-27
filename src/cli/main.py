import textwrap
import re
import os

import shutil

import parso
from   parso.tree import Leaf, Node, NodeOrLeaf
from parso.python.tree import Name, Operator

# ----------------------------------------------

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

class Method(MatchRule):
    def __init__(self, callee, repl):
        self.kind    = "method"
        self.callee  = callee
        self.repl    = repl

class Call(MatchRule):
    def __init__(self, callee, repl):
        self.kind    = "call"
        self.callee  = callee
        self.repl    = repl

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
        # testlist_comp
        # atom_expr
        # number 
        # endmarker 
        # string
        # strings

        def text(data):
            return ("text", data)

        def img(path):
            return ("img", path)

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

def type_match_where(type, node, info=None):
    # TODO return more information for complex nodes such as index
    
    # print(type, node.type)
    
    match type:
        case "name":
            return node.type == "name"
        
        case "call": # function call
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
                   
        case "dot": 
            return node.type == "atom_expr"
        
        case "__dot": 
            return \
                node.type              == 'trailer'  and \
                node.children[0].type  == 'operator' and \
                node.children[0].value == '.'        and \
                node.children[1].type  == 'name'
        
        case "operator":
            return node.type  == 'operator'
                
        case "operator=":
            return node.type  == 'operator' and \
                   node.value == info
                
        case "__callparen": 
            return \
                node.type     == 'trailer'  and \
                type_match_where('operator=', node.children[0] , '(') and \
                type_match_where('operator=', node.children[-1], ')')
        
        case "method":
            if node.type == "atom_expr":
                for i in range(2, len(node.children)):
                    if type_match_where('__dot',       node.children[i-1]) and \
                       type_match_where('__callparen', node.children[i  ]) :
                        return i
                        
        
        case "tuple":
            return node.type == "atom"

        case "paren":
            return node.type == "atom"

        case "list":
            return node.type == "atom"
        
        case "defn": ...
        case "lambda": ...
        
        case "class": ...
        
        case "if": ...
        case "elif": ...
        case "else": ...
        
        case "match": ...
        case "case": ...
        
        case "for": ...
        case "while": ...
        
        case "import": ...
        case "return": ...
        
        case _: ...
        
    return None

def apply_rule(rule: MatchRule, node, parent, index):
    # print(node.type, rule.kind)
    
    if ret := type_match_where(rule.kind, node):
        
        match rule.kind:
            case "name":
                val = node.value
                m = re.match(rule.pattern, val)
                if m:
                    return rule.repl(m)
        
            case "method":
                dot_i  = ret - 1
                call_i = ret
                if node.children[dot_i].children[1].value == rule.callee:
                    repl_nodes = rule.repl(Node('atom_expr', node.children[:dot_i]), node.children[call_i].children[1:-1])
                    node.children = [*repl_nodes, *node.children[call_i+1:]]

    return None

def to_IR(node, rules, parent, index): 
    ret = []
    is_leaf = not hasattr(node, 'children')
    
    if hasattr(node, 'prefix'):
        ret.append(("space", node.prefix))

    found = False
    for rule in rules:
        if res := apply_rule(rule, node, parent, index):
            found = True
            for r in res:
                ret.append(r)
            break
    
    if not is_leaf:
        i = 0
        while i < len(node.children):
            for r in to_IR(node.children[i], rules, node, i):
                ret.append(r)
            i += 1
        
            
    if not found and is_leaf:
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
                    
                if node.value[0] == '$':
                    op = node.value.strip('$')
                
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
            # print(">> ", r)
            kind, data = r
            
            match kind:
                case "space":
                    ret.append(f'<span class="space" style="margin-left: {len(data) * 6}px">{data}</span>')
                case "newline":
                    ret.append("<br>")
                case "img":
                    ret.append(f'<img class="inline-img" height="20" src="/assets/{data}"/>')
                case "keyword":
                    ret.append(f'<span class="keyword">{data.value}</span>')
                case "math":
                    ret.append(f'<span class="latex">{data}</span>')
                case "string":
                    ret.append(f'<span class="string">{data.value}</span>')
                case "text":
                    ret.append(f'<span class="text">{data}</span>')
                case _:
                    ret.append(f'<span class="code">{data.value}</span>')
                
            
    return "".join(ret)

def build_project(content, dest="./dist", title="better code"):
    os.makedirs(dest, exist_ok=True)
    
    with open(f"{dest}/index.html", "w", encoding='utf-8') as f:
        f.write(f"""
        <!DOCTYPE html>
            <html>
            <head>
                <link rel="stylesheet" href="/lib/katex.min.css">
                <script defer src="/lib/katex.min.js"></script>
                
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
    shutil.copytree("./node_modules/katex/dist/", f"{dest}/lib/", dirs_exist_ok=True)
    shutil.copytree("./assets/", f"{dest}/assets/", dirs_exist_ok=True)
    
    print(f"\n:: now serve a simple http server at {dest} ::")
            
# ----------------------------------------------

# TODO write a matcher like clang-query

def add_prefix(node):
    is_leaf = not hasattr(node, 'children')
    
    if is_leaf:
        node.prefix = " " + node.prefix
    else:
        add_prefix(node.children[0])

def mm1(obj, args):
    add_prefix(args[0])
    return [Node('term', [obj, Operator(r'$\cdot$', (1, 0), " "), args[0]])]

def mm2(obj, args):
    add_prefix(args[0])
    return [Node('term', [obj, Operator(r'$\times$', (1, 0), " "), args[0]])]

if __name__ == "__main__":
    rules = [
        Name(r"(\w+?)__(\w+)",  lambda m: [BetterCode.Node.math(f"{'{'}{m.group(1)}{'}'}_{'{'}{m.group(2)}{'}'}")]),
        Name(r"delta_(\w+)",    lambda m: [BetterCode.Node.math(f"\\Delta {'{'}{m.group(1)}{'}'}")]),
        Name(r"(\w*)firefox(\w*)",   lambda m: [BetterCode.Node.math(escape_for_katex(m.group(1))), BetterCode.Node.img("firefox.png"), BetterCode.Node.math(escape_for_katex(m.group(2)))]),
        Name(r"(\w*)mouse(\w*)",   lambda m: [BetterCode.Node.math(escape_for_katex(m.group(1))), BetterCode.Node.text("🖱"), BetterCode.Node.math(escape_for_katex(m.group(2)))]),

        Method("dot", mm1),
        Method("mul", mm2),
        
        # Kw("or", "\\vee"),
        # Kw("and", "\\wedge"),
    ]
    
    raw  = readfile("./test/sample.py")
    code = textwrap.dedent(raw)
    print(code)

    tree = parso.parse(code)
    print(tree.dump())
    
    ir  = to_IR(tree, rules, None, None)
    print(ir)
    
    out = to_html(ir)
    build_project(out)
