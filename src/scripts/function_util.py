import regex
import ast
from typing import List, Any
from ast import Module


def extract_function_from_str(code: str) -> str:
    code = code[code.index("def"): len(code):]
    while len(code.split('\n')) > 1:
        try:
            ast.parse(code)
            break
        except:
            code = '\n'.join(code.split('\n')[:-1])
    return code


def extract_function_name(f: str) -> str:
    return f[f.index("def ") + len("def "): f.index("(")]


def tabs_as_symbol(f: str) -> str:
    return f.replace("    ", '\t').replace("  ", '\t')


def remove_inline_comments(python_code: str) -> str:
    res: str = ""
    for line in python_code.split('\n'):
        try:
            comment: str = line.split('#', 1)[1].split('\n', 1)[0]
            res += line.replace('#' + comment, '').rstrip()
        except:
            res += line
        res += '\n'
    return res


def remove_multiline_comments(python_code: str) -> str:
    triple_2q: str = '"""'
    triple_1q: str = "'''"
    res: str = ""
    line_init: str = python_code.split('\n')[0].lstrip()
    is_take: bool = False if (line_init == triple_2q) or (line_init == triple_1q) else True
    is_stmn: bool = True if ((triple_2q in line_init) or (triple_1q in line_init)) and is_take else False
    is_take_prev: bool = is_take
    for line in python_code.split('\n'):
        if len(line.lstrip()) > 0:
            if (line.lstrip()[0] == '"""' and line.rstrip()[-1] == '"""') or \
                    (line.lstrip()[0] == "'''" and line.rstrip()[-1] == "'''"):
                continue
        if (triple_2q in line) or (triple_1q in line):
            if ((line.lstrip() == triple_2q) or (line.lstrip() == triple_1q)) and not is_stmn:
                is_take = not is_take
            else:
                is_stmn = not is_stmn
                is_take = True
        if is_take and is_take_prev:
            res += line + '\n'
        is_take_prev = is_take
    return res


def remove_empty_lines(python_code: str) -> str:
    res: List[str] = []
    for line in python_code.split('\n'):
        if not regex.match(r'^\s*$', line):
            res.append(line + '\n')
    res[-1] = res[-1].replace('\n', '')
    return ''.join(res)


def substitute_tabs_with_pony_encode(python_code: str) -> str:
    start_tab: str = "{:"
    end_tab: str = ":}"
    tab_counter: int = 0
    tmp_tab_counter: int = 0
    res: List[res] = []
    index: int = 0
    for line in python_code.split('\n'):
        tmp_tab_counter = line.count('\t')
        line = line.replace('\t', '')
        if tmp_tab_counter > tab_counter:
            if index != 0:
                res[index - 1] = res[index - 1].replace('\n', start_tab + '\n')
                res.append(line)
            else:
                res.append(line + start_tab + '\n')
        if tmp_tab_counter < tab_counter:
            res[index - 1] += end_tab + '\n'
            res.append(line)
        if tmp_tab_counter == tab_counter:
            res.append(line)
        res += '\n'
        tab_counter = tmp_tab_counter
        index = index + 2
    res.append(end_tab)
    return ''.join(res)


def to_pony_individual(python_code: str) -> str:
    python_code = remove_inline_comments(python_code)
    python_code = remove_multiline_comments(python_code)
    python_code = remove_empty_lines(python_code)
    return substitute_tabs_with_pony_encode(python_code)


def extract_function_imports(f: str) -> List[str]:
    imports: List[str] = []
    tree: Module = ast.parse(f)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(f"import {alias.name}")
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ''
            for alias in node.names:
                imports.append(f"from {module} import {alias.name}")
    return imports


def remove_function_imports(f: str) -> str:
    tree: Module = ast.parse(f)
    new_body: List[Any] = []
    for node in tree.body:
        if not isinstance(node, (ast.Import, ast.ImportFrom)):
            new_body.append(node)
    if hasattr(ast, "TypeIgnore"):
        new_tree = ast.Module(body=new_body, type_ignores=[])
    else:
        new_tree = ast.Module(body=new_body)
    return ast.unparse(new_tree).strip()


def remove_imports_and_comments_and_format_tabs(f: str) -> str:
    f = remove_inline_comments(f)
    f = remove_multiline_comments(f)
    f = remove_function_imports(f)
    f = tabs_as_symbol(f)
    return f
