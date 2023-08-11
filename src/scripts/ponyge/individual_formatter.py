from typing import List, Any
import ast
import re
from scripts.function_util import extract_function_name, insert_strings_after_signature


def substitute_tabs_and_newlines_with_pony_encode(code: str) -> str:
    start_tab: str = "{:"
    end_tab: str = ":}"
    newline: str = '#'
    tab_counter: int = 0
    tmp_tab_counter: int = 0
    res: List[res] = []
    index: int = 0
    for line in code.split('\n'):
        tmp_tab_counter = line.count('\t')
        line = line.replace('\t', '')
        if tmp_tab_counter > tab_counter:
            if index != 0:
                res[index - 1] = res[index - 1].replace('\n', start_tab + '\n')
                res.append(line)
            else:
                res.append(line + start_tab + '\n')
        if tmp_tab_counter < tab_counter:
            res[index - 1] += end_tab  # NOTE + '\n' probably not correct
            res.append(line)
        if tmp_tab_counter == tab_counter:
            res.append(line)
        res += '\n'
        tab_counter = tmp_tab_counter
        index = index + 2
    res.append(end_tab)
    res.insert(0, start_tab)
    res.insert(1, '\n')
    temp_res: str = ''.join(res)
    missing_tabs: int = temp_res.count(start_tab) - temp_res.count(end_tab)
    for _ in range(missing_tabs):
        res.append(end_tab)
    return ''.join(res).replace('\n', newline)


def extract_variables_names(code: str) -> List[str]:
    exec(code, locals())
    return list(eval(extract_function_name(code)).__code__.co_varnames)  # FIXME does not work


def extract_variables_names_test(code: str) -> List[str]:  # TODO remove it
    tree = ast.parse(code)
    names = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.Assign, ast.For, ast.While)):
            if isinstance(node, ast.For):
                target = node.target
            else:
                target = node.targets[0]
            if isinstance(target, ast.Name):
                names.append(target.id)
            elif isinstance(target, ast.Tuple):
                for i in range(len(target.elts)):
                    names.append(target.elts[i].id)
    return list(set(names))


def substitute_variables_name_with_predefined(names: List[str], code: str) -> str:
    possible_names = ["v0", "v1", "v2", "v3", "v4", "v5", "v6", "v7", "v8", "v9",
                      "v10", "v11", "v12", "v13", "v14", "v15", "v16", "v17", "v18", "v19"]
    pred_names_dict = {}
    for i, v in enumerate(names):
        pred_names_dict[v] = possible_names[i]
    pattern = r'(\W+)'
    splitted_code = re.split(pattern, code)
    ss = 0
    for i in range(len(splitted_code)):
        if ss == 0:
            if splitted_code[i].find('"') != -1 or splitted_code[i].find("'") != -1 \
                    or splitted_code[i].find('"""') != -1 or splitted_code[i].find("'''") != -1:
                ss = 1
            else:
                if splitted_code[i] in pred_names_dict.keys():
                    splitted_code[i] = pred_names_dict[splitted_code[i]]
        elif ss == 1:
            if splitted_code[i].find('"') != -1 or splitted_code[i].find("'") != -1 \
                    or splitted_code[i].find('"""') != -1 or splitted_code[i].find("'''") != -1:
                ss = 0
    return ''.join(splitted_code)


def to_pony_individual_with_imports(code: str, imports: str) -> str:
    code = insert_strings_after_signature(code, imports)
    return substitute_tabs_and_newlines_with_pony_encode(code)


def substitute_variables_name(code):
    names: List[str] = extract_variables_names(code)
    code = substitute_variables_name_with_predefined(names, code)
    return substitute_tabs_and_newlines_with_pony_encode(code)
