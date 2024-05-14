import re
from typing import Any, Optional
import traceback
import json
from scripts.ponyge.individual_formatter import replace_variables_with_names 
from scripts.json_data_saver import read_json


def add_global_declarations_before_function_definitions(s: str) -> str:
    p = re.compile('^(\s*)def (.+)\((.*)\)(.*):(\s*)$')
    l: list[str] = s.split('\n')
    t = [(i, re.findall(r'def (.+)\(', l[i])[0], len(l[i]) - len(l[i].lstrip())) for i in range(len(l)) if p.match(l[i])][::-1]
    for i, function_name, num_lead_spaces in t:
        l.insert(i, f'{" " * num_lead_spaces}global {function_name}')
    return '\n'.join(l)


def enforce_syntactically_valid_function(s: str, potentially_new_name: str, n_inputs: Optional[int] = None) -> str:
    l: list[str] = s.split('\n')
    keep_removing_lines: bool = True

    if len(l) == 1:
        l.append('\tpass')
        keep_removing_lines = False

    try:
        exec('\n'.join([l[0], '\tpass']), locals())
    except SyntaxError:
        if n_inputs is None:
            raise ValueError(f'Required n_inputs different from None if function definition line has syntax errors.')
        if potentially_new_name.strip() == '':
            raise ValueError(f'Required potentially_new_name different from empty string if function definition line has syntax errors.')
        l[0] = f'def {potentially_new_name.strip()}({", ".join(f"v{i}" for i in range(n_inputs))}):'

    while keep_removing_lines:
        try:
            exec('\n'.join(l), locals())
            keep_removing_lines = False
        except SyntaxError as e:
            del l[e.lineno - 1]
            if len(l) == 1:
                l.append('\tpass')
                keep_removing_lines = False

    if len(l) == 2 and l[1] == '\tpass':
        try:
            exec('\n'.join(l), locals())
        except SyntaxError:
            if n_inputs is None:
                raise ValueError(f'Required n_inputs different from None if function definition line has syntax errors.')
            if potentially_new_name.strip() == '':
                raise ValueError(f'Required potentially_new_name different from empty string if function definition line has syntax errors.')
            l = [f'def {potentially_new_name.strip()}({", ".join(f"v{i}" for i in range(n_inputs))}):', '\tpass']
    
    return '\n'.join(l)


def extract_imports(l: list[str], remove_non_existing_import: bool) -> list[str]:
    p = re.compile('^(\s*)(import (.+)|import (.+) as (.+)|from (.+) import (.+))(\s*)$')
    actual_imports: list[str] = list(set([line.strip() for line in l if p.match(line.strip()) and line.strip() != '']))
    actual_imports = [imp for imp in actual_imports if ' typing ' not in imp]
    
    actual_imports_0 = actual_imports[:]
    actual_imports = []

    for imp in actual_imports_0:
        try:
            exec(imp)
            actual_imports.append(imp)
        except SyntaxError:
            pass
    
    if remove_non_existing_import:
        existing_imports: list[str] = []
        for imp in actual_imports:
            try:
                exec(imp)
                existing_imports.append(imp)
            except ImportError:
                pass
        return existing_imports
    else:
        return actual_imports
    
    
def remove_nested_imports(l: list[str]) -> list[str]:
    p = re.compile('^(\s*)(import (.+)|import (.+) as (.+)|from (.+) import (.+))(\s*)$')
    
    idx_to_remove: set[int] = set()
    for i in range(len(l)):
        if p.match(l[i]) and len(l[i]) - len(l[i].lstrip()) != 0:
            idx_to_remove.add(i)
    
    idx_to_remove_l: list[int] = sorted(list(idx_to_remove), reverse=True)
    l_copy = l[:]
    for i in idx_to_remove_l:
        del l_copy[i]

    return l_copy


def remove_imports_and_functions(l: list[str]) -> list[str]:
    idx_to_remove: set[int] = set()
    
    p_func = re.compile('^(\s*)def (.+)\((.*)\)(.*):(\s*)$')
    p_imp = re.compile('^(\s*)(import (.+)|import (.+) as (.+)|from (.+) import (.+))(\s*)$')
    
    for i in range(len(l)):
        if p_imp.match(l[i]):
            idx_to_remove.add(i)
        if p_func.match(l[i]):
            idx_to_remove.add(i)
            num_lead_spaces = len(l[i]) - len(l[i].lstrip())
            for j in range(i + 1, len(l)):
                if len(l[j]) - len(l[j].lstrip()) <= num_lead_spaces:
                    break
                idx_to_remove.add(j)
            
    
    idx_to_remove_l: list[int] = sorted(list(idx_to_remove), reverse=True)
    l_copy = l[:]
    for i in idx_to_remove_l:
        del l_copy[i]
    
    return l_copy


def remove_imports_only(l: list[str]) -> list[str]:
    idx_to_remove: set[int] = set()
    
    p_imp = re.compile('^(\s*)(import (.+)|import (.+) as (.+)|from (.+) import (.+))(\s*)$')
    
    for i in range(len(l)):
        if p_imp.match(l[i]):
            idx_to_remove.add(i)    
    
    idx_to_remove_l: list[int] = sorted(list(idx_to_remove), reverse=True)
    l_copy = l[:]
    for i in idx_to_remove_l:
        del l_copy[i]
    
    return l_copy


def extract_single_function(l: list[str]) -> list[str]:
    num_lead_spaces: int = len(l[0]) - len(l[0].lstrip())
    func_lines_end: int = 0
    for j in range(1, len(l)):
        if len(l[j]) - len(l[j].lstrip()) <= num_lead_spaces:
            break
        func_lines_end = j
    func_lines: list[str] = [l[k][num_lead_spaces:] for k in range(func_lines_end + 1)]
    return func_lines
    

def remove_nested_functions(l: list[str]) -> list[str]:
    p = re.compile('^(\s*)def (.+)\((.*)\)(.*):(\s*)$')
    t = [(i, re.findall(r'def (.+)\(', l[i])[0], len(l[i]) - len(l[i].lstrip()), len(l[i]) - len(l[i].lstrip()) != 0) for i in range(1, len(l)) if p.match(l[i])]
    idx_to_remove: set[int] = set()
    
    for i in range(len(t)):
        code_line, function_name, num_lead_spaces, is_nested = t[i][0], t[i][1], t[i][2], t[i][3]
        if is_nested:
            idx_to_remove.add(code_line)
            for j in range(code_line + 1, len(l)):
                if len(l[j]) - len(l[j].lstrip()) <= num_lead_spaces:
                    break
                idx_to_remove.add(j)
    
    idx_to_remove_l: list[int] = sorted(list(idx_to_remove), reverse=True)
    l_copy = l[:]
    for i in idx_to_remove_l:
        del l_copy[i]
    
    return l_copy


def remove_typing_from_header_func(s: str) -> str:
    # BE CAREFUL! CALL THIS FUNCTION ONLY ON THE HEADER OF A NON-NESTED FUNCTION DEFINITION
    s = s.strip()
    open_paren_index = s.index('(')
    closed_paren_index = s.index(')')
    s = s[:closed_paren_index + 1] + ':'
    ss = s[open_paren_index+1:closed_paren_index]
    l = ss.split(',')
    ll = []
    for e in l:
        if ':' in e:
            ll.append(e[:e.index(':')].strip())
        else:
            ll.append(e.strip())
    return s[:open_paren_index + 1] + ', '.join(ll) + s[closed_paren_index:]


def remove_internal_code_typing(l: list[str]) -> list[str]:
    p = re.compile('^(\s*)(_|[A-Z]|[a-z])[A-Za-z0-9_]*(\s*):(\s*)[A-Za-z](.*)(\s*)=(\s*)(.+)(\s*)$')

    l0 = []

    for i in range(len(l)):
        if p.match(l[i]):
            var_name = l[i][:l[i].index(':')]
            l0.append(var_name.rstrip() + ' ' + l[i][l[i].index('='):])
        else:
            l0.append(l[i])

    return l0


def remove_single_comments(l: list[str]) -> list[str]:
    idx_to_remove: set[int] = set()

    for i in range(len(l)):
        line: str = l[i]
        if line.strip().startswith('#'):
            idx_to_remove.add(i)
        elif line.strip().startswith("'''") and line.strip().endswith("'''") and len(line.strip()) > 3:
            idx_to_remove.add(i)
        elif line.strip().startswith('"""') and line.strip().endswith('"""') and len(line.strip()) > 3:
            idx_to_remove.add(i)

    idx_to_remove_l: list[int] = sorted(list(idx_to_remove), reverse=True)
    l_copy = l[:]
    for i in idx_to_remove_l:
        del l_copy[i]
    
    return l_copy


def remove_multi_comments(l: list[str]) -> list[str]:
    idx_to_remove: set[int] = set()
    to_be_removed_1: bool = False
    to_be_removed_2: bool = False
    pairs_of_multiline_comments_1_start: Optional[int] = None 
    pairs_of_multiline_comments_2_start: Optional[int] = None

    for i in range(len(l)):
        line: str = l[i]
        if to_be_removed_1:
            idx_to_remove.add(i)
            if line.strip().endswith("'''"):
                to_be_removed_1 = not to_be_removed_1
                pairs_of_multiline_comments_1_start = None
        elif to_be_removed_2:
            idx_to_remove.add(i)
            if line.strip().endswith('"""'):
                to_be_removed_2 = not to_be_removed_2
                pairs_of_multiline_comments_2_start = None
        else:
            if line.strip().startswith("'''"):
                idx_to_remove.add(i)
                to_be_removed_1 = not to_be_removed_1
                pairs_of_multiline_comments_1_start = i
            elif line.strip().startswith('"""'):
                idx_to_remove.add(i)
                to_be_removed_2 = not to_be_removed_2
                pairs_of_multiline_comments_2_start = i

    idx_to_remove_l: list[int] = sorted(list(idx_to_remove), reverse=True)
    l_copy = l[:]
    
    #if not (pairs_of_multiline_comments_1_start is None and pairs_of_multiline_comments_2_start is None):
    #    single_inds: list[int] = []
    #    if pairs_of_multiline_comments_1_start is not None:
    #        single_inds.append(pairs_of_multiline_comments_1_start)
    #    if pairs_of_multiline_comments_2_start is not None:
    #        single_inds.append(pairs_of_multiline_comments_2_start)
    #    stop_ind = min(single_inds)
    #    idx_to_remove_l = [i for i in idx_to_remove_l if i <= stop_ind]

    for i in idx_to_remove_l:
        del l_copy[i]

    return l_copy


def remove_comments(l: list[str]) -> list[str]:
    return remove_multi_comments(remove_single_comments(l))


def extract_distinct_functions(l: list[str], remove_syntax_errors: bool, potentially_new_name: str, n_inputs: Optional[int] = None) -> tuple[list[str], str, str, int]:
    p = re.compile('^(\s*)def (.+)\((.*)\)(.*):(\s*)$')
    
    outer_indent_size: int = min([len(l[i]) - len(l[i].lstrip()) for i in range(len(l)) if p.match(l[i])])
    l_copy: list[str] = [line[outer_indent_size:] for line in l]

    t = [(i, re.findall(r'def (.+)\(', l_copy[i])[0], len(l_copy[i]) - len(l_copy[i].lstrip()), len(l_copy[i]) - len(l_copy[i].lstrip()) != 0) for i in range(len(l_copy)) if p.match(l_copy[i])]
    
    # PICK LAST NON-NESTED FUNCTION (THE MAIN CODE FUNCTION)
    last_non_nested_function = t[-1]
    for i in range(len(t)):
        if not t[i][3]:
            last_non_nested_function = t[i]
    
    main_code_line = l_copy[last_non_nested_function[0]]
    entry_point = last_non_nested_function[1]

    # EXTRACT INDIVIDUAL FUNCTIONS (NESTED AND NON-NESTED, NESTED FUNCTIONS BECOME NON-NESTED AND THEY ARE REMOVED FROM THE MOTHER FUNCTIONS)
    all_funcs: list[list[str]] = [remove_nested_functions(extract_single_function(l_copy[t[i][0]:])) for i in range(len(t))]
    main_func_idx: int = None

    for i in range(len(all_funcs)):
        if all_funcs[i][0].strip() == main_code_line.strip():
            main_func_idx = i
            break

    # PUT MAIN FUNCTION CODE AT THE END AS LAST FUNCTION
    all_funcs = all_funcs[:main_func_idx] + all_funcs[main_func_idx + 1:] + [all_funcs[main_func_idx]]
    
    for func in all_funcs:
        func[0] = remove_typing_from_header_func(func[0])

    sup_funcs: list[list[str]] = []
    for func in all_funcs[:-1]:
        try:
            exec('\n'.join(func), locals())
            sup_funcs.append(func)
        except SyntaxError:
            pass

    main_code_func: list[str] = all_funcs[-1]

    if remove_syntax_errors:
        main_code_func = enforce_syntactically_valid_function('\n'.join(main_code_func), potentially_new_name=potentially_new_name, n_inputs=n_inputs).split('\n')

    indent_size: int = len(main_code_func[1]) - len(main_code_func[1].lstrip())

    return ['\n'.join(sup_funcs[i]) for i in range(len(sup_funcs))], entry_point, '\n'.join(main_code_func), indent_size


def tabs_as_symbols(s: str, indent_size: int) -> str:
    l: list[str] = s.split('\n')
    l0: list[str] = []

    for i in range(len(l)):
        line = l[i]
        num_lead_spaces: int = len(line) - len(line.lstrip())
        if num_lead_spaces == 0:
            l0.append(line)
        else:
            l0.append('\t' * (num_lead_spaces // indent_size) + line.lstrip())

    return '\n'.join(l0)


def properly_arrange_code_with_imports_functions(s: str, include_free_code: bool, replace_entry_point_with_this_name: str, replace_vars: bool, remove_non_existing_import: bool, n_inputs: Optional[int] = None, remove_syntax_errors: bool = False) -> dict[str, Any]:
    try:
        l: list[str] = [elem for elem in remove_comments(s.split('\n')) if elem.strip() != '']
        actual_imports: list[str] = extract_imports(l, remove_non_existing_import=remove_non_existing_import)
        distinct_funcs, entry_point, main_func, indent_size = extract_distinct_functions(remove_internal_code_typing(remove_imports_only(l)), remove_syntax_errors=remove_syntax_errors, potentially_new_name=replace_entry_point_with_this_name, n_inputs=n_inputs)
        distinct_funcs = [tabs_as_symbols(single_func, indent_size) for single_func in distinct_funcs]
        main_func = tabs_as_symbols(main_func, indent_size)
        if replace_entry_point_with_this_name.strip() != '':
            main_func = main_func.replace(entry_point + '(', replace_entry_point_with_this_name.strip() + '(')
        res: dict[str, Any] = {
            'imports': actual_imports,
            'sup_funcs': distinct_funcs,
            'main_func': main_func,
            'entry_point': entry_point,
            'new_entry_point': replace_entry_point_with_this_name.strip() if replace_entry_point_with_this_name.strip() != '' else entry_point,
            'indent_size': indent_size
        }
        if replace_vars:
            modified_code, possible_vars = replace_variables_with_names(res['main_func'], res['imports'])
            modified_code_l: list[str] = modified_code.split('\n')
            indent_size_modified_code: int = len(modified_code_l[1]) - len(modified_code_l[1].lstrip())
            res['renamed_main_func'] = tabs_as_symbols(modified_code, indent_size_modified_code)
            res['possible_vars'] = sorted(possible_vars)
        res['full_code'] = '\n'.join(res['imports']) + '\n\n' + '\n\n'.join(res['sup_funcs']) + '\n\n' + res['main_func'] + '\n'
        res['full_code_but_no_imports'] = '\n\n'.join(res['sup_funcs']) + '\n\n' + res['main_func'] + '\n'
        res['imports_and_supports'] = '\n'.join(res['imports']) + '\n\n' + '\n\n'.join(res['sup_funcs']) + '\n'
        if include_free_code:
            c: str = tabs_as_symbols('\n'.join(remove_imports_and_functions(l)), indent_size)
            res['free_code'] = c
    except Exception as e:
        if n_inputs is None:
            raise ValueError(f'Required n_inputs different from None if major errors occur.')
        if replace_entry_point_with_this_name.strip() == '':
            raise ValueError(f'Required replace_entry_point_with_this_name different from empty string if major errors occur.')
        
        res: dict[str, Any] = {
            'imports': [],
            'sup_funcs': [],
            'main_func': '\n'.join([f'def {replace_entry_point_with_this_name.strip()}({", ".join(f"v{i}" for i in range(n_inputs))}):', '\tpass']),
            'entry_point': replace_entry_point_with_this_name.strip(),
            'new_entry_point': replace_entry_point_with_this_name.strip(),
            'indent_size': 4
        }
        res['renamed_main_func'] = res['main_func']
        res['possible_vars'] = [f"v{i}" for i in range(n_inputs)]
        res['full_code'] = '\n'.join(res['imports']) + '\n\n' + '\n\n'.join(res['sup_funcs']) + '\n\n' + res['main_func'] + '\n'
        res['full_code_but_no_imports'] = '\n\n'.join(res['sup_funcs']) + '\n\n' + res['main_func'] + '\n'
        res['imports_and_supports'] = '\n'.join(res['imports']) + '\n\n' + '\n\n'.join(res['sup_funcs']) + '\n'

        res['exception'] = str(traceback.format_exc())

    return res


def try_main():
    s = 'import numpy as np\nimport numpy as np\nimport math\nimport string\nprint("---")\n#A comment\n# Another comment here\ndef incr(x):\n    # inside a comment\n    return x + 1\nprint("---")\n"""\nmultiline\ncomment\nhere\n"""\n'
    s += "'''\n" + '"""\n' + 'comment\n' + 'comment\n' + '"""\n' + "'''\n"
    s += '"""\n' + "'''\n" + 'comment\n' + 'comment\n' + "'''\n" + '"""\n' 
    s += "def incr2(x: int, y:float) -> float:\n    def incr3(x):\n        def incr4() -> int:\n            import os\n            '''\n            another\n            multiline\n            comment\n            here\n            '''\n            return 5\n        h: str = str([1, 2, 3, 4, 5][:2]) + str({k: k + 1 for k in [1, 2, 3]}) + str(5 == 6) \n        \n        return 4 + incr4()\n    \n    \n    pippo = 5\n    pluto = False\n    return incr(x) + incr3(x) + y\n\n"
    s += 'print(evolve(5, 1.0))\nprint(incr(1))\nprint(incr3(3))\nprint(incr4())\nfor _ in range(3):\n    for _ in range(2):\n        print("-" + "    " + "  ")\n\n'
    s += '"""\n' + "'''\n" + 'comment\n' + '"""\n' 
    s += "'''\n" + '"""\n' + 'comment\n' + 'comment\n' + "'''\n"
    print(s)
    ss = ''
    print('='*100)
    res = properly_arrange_code_with_imports_functions(s, True, 'evolve', True, True, 2, True)
    ss += res['full_code']
    if 'free_code' in res:
        ss += res['free_code']
        ss += '\n'
    print(ss)
    print('ENTRY POINT: ', res['entry_point'])
    print('NEW ENTRY POINT: ', res['new_entry_point'])
    print('INDENT SIZE: ', res['indent_size'])
    if 'possible_vars' in res:
        print('POSSIBLE VARS ', res['possible_vars'])
    print('='*100)
    exec(ss, locals())
    print('='*100)
    # with open('file1.txt', 'w') as f:
    #     f.write(s)
    # ccc = read_json(model_name='Mistral7B', problem_benchmark='humaneval', problem_id=102, reask=False, iterations=10, repeatitions=5, remove_non_existing_imports=False, train_size=100, test_size=1000)
    # with open('files/Mistral7B_problem102.json', 'r') as f:
    #     ccc = json.load(f)
    #     idx = 0
    #     example_code = ccc['data'][idx]['model_response']
    #     print(ccc['data'][idx]['model_response'])
    #     print('='*100)
    #     ccc_res = properly_arrange_code_with_imports_functions(example_code, False, 'evolve', True, False, 2, False)
    #     print(ccc_res['full_code'])
    #     print('='*100)
    #     print(ccc_res['renamed_main_func'])
    #     print('='*100)
    #     exec(ccc_res['full_code'])


if __name__ == '__main__':
    try_main()

