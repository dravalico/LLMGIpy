from typing import List, Any
import ast
import re
from llmpony.llm.functions.function_util import orderering_preserving_duplicates_elimination


def substitute_tabs_and_newlines_with_pony_encode(code: str) -> str:
    start_tab: str = "{:"
    end_tab: str = ":}"
    newline: str = '#'
    previous_tab_counter: int = 0
    final_code: List[Any] = []
    index: int = 0
    for line in code.split('\n'):
        tab_counter = line.count('\t')
        line = line.replace('\t', '')
        if tab_counter > previous_tab_counter:
            if index != 0:
                final_code[index - 1] = final_code[index - 1].replace('\n', start_tab + '\n')
                final_code.append(line)
            else:
                final_code.append(line + start_tab + '\n')
        if tab_counter < previous_tab_counter:
            for _ in range(previous_tab_counter - tab_counter):
                final_code[index - 1] += end_tab
            final_code.append(line)
        if tab_counter == previous_tab_counter:
            final_code.append(line)
        final_code += '\n'
        previous_tab_counter = tab_counter
        index = index + 2
    temp_final_code: str = ''.join(final_code)
    missing_tabs: int = temp_final_code.count(start_tab) - temp_final_code.count(end_tab)
    for _ in range(missing_tabs):
        final_code.append(end_tab)
    return ''.join(final_code).replace('\n', newline)


def convert_main_func_to_pony_ind(code: str) -> str:
    final_ind: str = ''

    start_tab: str = "{:"
    end_tab: str = ":}"
    newline: str = '#'

    code_lines: list[str] = code.split('\n')
    final_ind += code_lines[0].strip()
    code_lines = code_lines[1:]

    indent_size: int = len(code_lines[0]) - len(code_lines[0].lstrip())
    code_lines = [line[indent_size:] for line in code_lines]

    final_ind = final_ind + start_tab + newline + __convert_main_func_to_pony_ind_recursive(code_lines) + end_tab
    final_ind = final_ind.replace(newline + start_tab, start_tab + newline)

    return final_ind


def __convert_main_func_to_pony_ind_recursive(code_lines: list[str]) -> str:
    if code_lines == []:
        return ''

    final_ind: str = ''

    start_tab: str = "{:"
    end_tab: str = ":}"
    newline: str = '#'

    i: int = 0
    while i < len(code_lines):
        indent_size: int = len(code_lines[i]) - len(code_lines[i].lstrip())
        if indent_size == 0:
            final_ind += code_lines[i]
            final_ind += newline
            i += 1
        else:
            sub_code_lines: list[str] = []
            j: int = i
            while j < len(code_lines):
                sub_indent_size: int = len(code_lines[j]) - len(code_lines[j].lstrip())
                if sub_indent_size > 0:
                    sub_code_lines.append(code_lines[j][indent_size:])
                    j += 1
                else:
                    break
            final_ind += start_tab + __convert_main_func_to_pony_ind_recursive(sub_code_lines) + end_tab
            i = j

    return final_ind


def import_manipulation(imports):
    final = []
    for imp in imports:
        i = imp.replace(',', ' ')
        i = re.sub(r'\s+', ' ', i)
        l = [elem.strip() for elem in i.split()]
        if l[0] == 'from':
            if 'as' in l:
                final.append(l[-1])
            else:
                for elem in l[3:]:
                    final.append(elem)
        else:
            if 'as' in l:
                final.append(l[-1])
            else:
                for elem in l[1:]:
                    final.append(elem)

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
    
    return orderering_preserving_duplicates_elimination(local_vars)


def replace_variables_with_names(code: str, imports):
    variables = extract_variables_names(code)
    var_names = [f"v{i}" for i in range(len(variables))]
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
    return modified_code, orderering_preserving_duplicates_elimination(used_variables + import_manipulation(imports))


def extract_all_methods_from_imports(imports: list[str], include_sub_methods: bool):
    functions = []
    methods = []

    for imp in imports:
        try:
            exec(imp)
        except:
            pass

    imp_vars = import_manipulation(imports)

    temp = []

    for a in imp_vars:
        try:
            cl = eval(a)
            l = [method for method in cl.__dict__ if callable(getattr(cl, method)) and not method.startswith("_")]
            temp.extend([method for method in l])

            if include_sub_methods:
                for iii in l:
                    try:
                        exec("import " + iii)
                        cl_2 = eval(iii)
                        l_2 = [method_2 for method_2 in cl_2.__dict__ if callable(getattr(cl_2, method_2)) and not method_2.startswith("_")]
                        temp.extend([method_2 for method_2 in l_2])
                    except:
                        pass
        except:
            pass

    functions.extend([t for t in temp if t[0].isupper()])
    methods.extend(['.' + t for t in temp if t[0].islower()])

    return orderering_preserving_duplicates_elimination(functions), orderering_preserving_duplicates_elimination(methods)
