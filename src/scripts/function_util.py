import regex
import ast
from typing import List, Any
from ast import Module
import re


# TODO start from top and verify import, from ... import and only then verify the def
def extract_function_from_str(text: str) -> str:
    python_code: str = try_extract_code_inside_python_tag(text)
    if python_code is not None:
        return python_code
    text = text[text.index("def"): len(text):]
    while len(text.split('\n')) > 1:
        try:
            ast.parse(text)
            break
        except:
            text = '\n'.join(text.split('\n')[:-1])
    if len(text.split('\n')) == 1:
        text = text + "\n\tpass"
    return text


def try_extract_code_inside_python_tag(text: str) -> str:
    pattern = r'```python\s*([\s\S]*?)\s*```'
    match = re.search(pattern, text)
    if match:
        return match.group(1)
    return None


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


def substitute_tabs_and_newlines_with_pony_encode(python_code: str) -> str:
    start_tab: str = "{:"
    end_tab: str = ":}"
    newline: str = '#'
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
    res.insert(0, start_tab)
    res.insert(1, newline)
    for _ in range(tab_counter):
        res.append(end_tab)
    return ''.join(res).replace('\n', '#')


def insert_strings_after_signature(python_code: str, imports: str) -> str:
    code_lines: List[str] = python_code.split("\n")
    function_line_index: str = next((i for i, line in enumerate(code_lines) if line.strip().startswith("def")), None)
    if function_line_index is None:
        raise ValueError("Problems with the function")
    for string in imports:
        code_lines.insert(function_line_index + 1, '\t' + string)
    modified_code = "\n".join(code_lines)
    return modified_code


def to_pony_individual(python_code: str, imports: str) -> str:
    python_code = remove_inline_comments(python_code)
    python_code = remove_multiline_comments(python_code)
    python_code = remove_empty_lines(python_code)
    python_code = insert_strings_after_signature(python_code, imports)
    return substitute_tabs_and_newlines_with_pony_encode(python_code)


def extract_function_imports(f: str) -> List[str]:
    imports: List[str] = []
    tree: Module = ast.parse(f)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.asname != None:
                    imports.append(f"import {alias.name} as {alias.asname}")
                else:
                    imports.append(f"import {alias.name}")
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ''
            for alias in node.names:
                if alias.asname != None:
                    imports.append(f"from {module} import {alias.name} as {alias.asname}")
                else:
                    imports.append(f"from {module} import {alias.name}")
    return imports


def remove_internal_function_imports(f: str) -> str:
    tree: ast.Module = ast.parse(f)
    new_body: List[Any] = []
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            function_body: List[Any] = []
            for function_node in node.body:
                if not isinstance(function_node, (ast.Import, ast.ImportFrom)):
                    function_body.append(function_node)
            node.body = function_body
        new_body.append(node)
    if hasattr(ast, "TypeIgnore"):
        new_tree = ast.Module(body=new_body, type_ignores=[])
    else:
        new_tree = ast.Module(body=new_body)
    return ast.unparse(new_tree).strip()


def remove_external_function_imports(f: str) -> str:
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
    f = remove_internal_function_imports(f)
    f = remove_external_function_imports(f)
    f = tabs_as_symbol(f)
    return f
