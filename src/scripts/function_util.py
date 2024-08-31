import ast
from typing import List, Any
from ast import Module
import re
from re import Match


def compute_bnf_type_from_dynamic_bnf_param(dynamic_bnf: str) -> str:
    if dynamic_bnf not in ("True", "False"):
        raise ValueError(f'Unrecognized {dynamic_bnf} as dynamic_bnf, can be either True or False (as string).')
    bnf_type = "dynamicbnf" if dynamic_bnf == "True" else "staticbnf"
    return bnf_type


def orderering_preserving_duplicates_elimination(local_vars):
    actual_local_vars = []
    for local_var in local_vars:
        if local_var not in actual_local_vars:
            actual_local_vars.append(local_var)

    return actual_local_vars


def extract_external_imports(text: str) -> List[str]:
    pattern: str = r"(?:^|\n)(?:from\s+(\S+)\s+)?import\s+(.+?)(?:\s+as\s+(\w+))?(?=$|\n)"
    imports_match: List[str] = re.findall(pattern, text, re.MULTILINE)
    imports: List[str] = []
    for import_data in imports_match:
        package, items, alias = import_data
        if items:
            if package:
                if alias:
                    imports.append(f"from {package} import {items} as {alias}")
                else:
                    imports.append(f"from {package} import {items}")
            else:
                if alias:
                    imports.append(f"import {items} as {alias}")
                else:
                    imports.append(f"import {items}")
    return imports


def extract_function(text: str) -> str:  # NOTE starts from def, imports should already be saved
    code: str = try_extract_code_inside_tags(text)
    if code is not None:
        return code
    code = text[text.index("def"): len(text):]
    while len(code.split('\n')) > 1:
        try:
            ast.parse(code)
            break
        except:
            code = '\n'.join(code.split('\n')[:-1])
    if len(code.split('\n')) == 1:
        return code + "\n\tpass"
    return try_to_remove_extra_strings(code)


def try_extract_code_inside_tags(text: str) -> str:
    pattern: str = r'```python\s*([\s\S]*?)\s*```'
    match: Match[str] = re.search(pattern, text)
    if match:
        return try_to_remove_extra_strings(match.group(1))
    pattern = r'```\s*([\s\S]*?)\s*```'
    if match:
        return try_to_remove_extra_strings(match.group(1))
    pattern = r'\begin{code}\s*([\s\S]*?)\s*\end{code}'
    if match:
        return try_to_remove_extra_strings(match.group(1))
    return None


def try_to_remove_extra_strings(code: str) -> str:
    code: str = code.replace("    ", '\t')
    lines: List[str] = code.split('\n')
    code = lines[0]
    is_start: bool = True
    for line in lines[1:]:
        if is_start and line.count('\t') < 1:
            code += '\n' + line
            continue
        if line.count('\t') >= 1:
            is_start = False
            code += '\n' + line
    return code


def extract_function_name(code: str) -> str:
    return code[code.index("def ") + len("def "): code.index('(')]


def tabs_as_symbol(f: str) -> str:
    return f.replace("    ", '\t').replace("  ", '\t')


def remove_inline_comments(code: str) -> str:
    res: str = ""
    for line in code.split('\n'):
        try:
            comment: str = line.split('#', 1)[1].split('\n', 1)[0]
            res += line.replace('#' + comment, '').rstrip()
        except:
            res += line
        res += '\n'
    return res


def remove_multiline_comments(code: str) -> str:
    triple_2q: str = '"""'
    triple_1q: str = "'''"
    res: str = ""
    line_init: str = code.split('\n')[0].lstrip()
    is_take: bool = False if (line_init == triple_2q) or (line_init == triple_1q) else True
    is_stmn: bool = True if ((triple_2q in line_init) or (triple_1q in line_init)) and is_take else False
    is_take_prev: bool = is_take
    for line in code.split('\n'):
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


def remove_empty_lines(code: str) -> str:
    res: List[str] = []
    for line in code.split('\n'):
        if not re.match(r'^\s*$', line):
            res.append(line + '\n')
    try:
        res[-1] = res[-1].replace('\n', '')
    except:
        pass
    return ''.join(res)


def extract_internal_imports(code: str) -> List[str]:
    code = tabs_as_symbol(code)
    imports: List[str] = []
    tree: Module = ast.parse(code)
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


def remove_internal_function_imports(code: str) -> str:
    tree: ast.Module = ast.parse(code)
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


def remove_external_function_imports(code: str) -> str:
    tree: Module = ast.parse(code)
    new_body: List[Any] = []
    for node in tree.body:
        if not isinstance(node, (ast.Import, ast.ImportFrom)):
            new_body.append(node)
    if hasattr(ast, "TypeIgnore"):
        new_tree = ast.Module(body=new_body, type_ignores=[])
    else:
        new_tree = ast.Module(body=new_body)
    return ast.unparse(new_tree).strip()


def remove_imports_and_comments_and_format_tabs(code: str) -> str:
    code = remove_inline_comments(code)
    code = remove_multiline_comments(code)
    code = remove_internal_function_imports(code)
    code = remove_external_function_imports(code)
    code = remove_empty_lines(code)
    code = tabs_as_symbol(code)
    return code


def insert_strings_after_signature(code: str, imports: List[str]) -> str:
    if imports == []:
        return code
    code_lines: List[str] = code.split('\n')
    function_line_index: str = next((i for i, line in enumerate(code_lines) if line.strip().startswith("def")), None)
    if function_line_index is None:
        raise ValueError("Problems with the function")
    for string in imports:
        code_lines.insert(function_line_index + 1, '\t' + string)
    modified_code = '\n'.join(code_lines)
    return modified_code
