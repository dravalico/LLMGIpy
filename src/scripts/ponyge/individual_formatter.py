from typing import List
import ast
from scripts.function_util import insert_strings_after_signature


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
    # res.append(end_tab)
    # res.insert(0, start_tab)
    # res.insert(1, '\n')
    temp_res: str = ''.join(res)
    missing_tabs: int = temp_res.count(start_tab) - temp_res.count(end_tab)
    for _ in range(missing_tabs):
        res.append(end_tab)
    return ''.join(res).replace('\n', newline)


def import_manipulation1(imports):
    final = []
    for imp in imports:
        imp_splitted = imp.split()
        final.append(imp_splitted[-1])
    return final


def extract_variables_names(code: str):
    tree = ast.parse(code)
    function_defs = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
    if len(function_defs) == 0:
        return []
    first_function = function_defs[0]
    local_vars = [arg.arg for arg in first_function.args.args]
    for node in ast.walk(first_function):
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            local_vars.append(node.id)
    return local_vars


def replace_variables_with_names(code: str, imports):
    variables = extract_variables_names(code)
    var_names = ["v0", "v1", "v2", "v3", "v4", "v5", "v6", "v7", "v8", "v9",
                 "v10", "v11", "v12", "v13", "v14", "v15", "v16", "v17", "v18", "v19"]
    var_mapping = {var: new_name for var, new_name in zip(variables, var_names)}

    def replace_var_names(node):
        if isinstance(node, ast.Name) and node.id in var_mapping:
            node.id = var_mapping[node.id]
        for child_node in ast.iter_child_nodes(node):
            replace_var_names(child_node)
    tree = ast.parse(code)
    first_function = next((node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)), None)
    if first_function:
        for i, var in enumerate(var_names):
            if i < len(first_function.args.args):
                first_function.args.args[i].arg = var
    replace_var_names(tree)
    modified_code = ast.unparse(tree)
    used_variables = [var_mapping[var] for var in variables if var in var_mapping]
    return modified_code, list(set(used_variables + import_manipulation1(imports)))


def to_pony_individual_with_imports(code: str, imports: str) -> str:
    code = insert_strings_after_signature(code, imports)
    return substitute_tabs_and_newlines_with_pony_encode(code)
