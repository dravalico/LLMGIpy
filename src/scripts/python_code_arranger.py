import re 


def add_global_declarations_before_function_definitions(s: str) -> str:
    p = re.compile('^(\s*)def (.+)\((.*)\)(.*):(\s*)$')
    l: list[str] = s.split('\n')
    t = [(i, re.findall(r'def (.+)\(', l[i])[0], len(l[i]) - len(l[i].lstrip())) for i in range(len(l)) if p.match(l[i])][::-1]
    for i, function_name, num_lead_spaces in t:
        l.insert(i, f'{" " * num_lead_spaces}global {function_name}')
    return '\n'.join(l)


def extract_imports(l: list[str]) -> str:
    p = re.compile('^(\s*)(import (.+)|import (.+) as (.+)|from (.+) import (.+))(\s*)$')
    actual_imports: list[str] = [line.strip() for line in l if p.match(line)]
    return '\n'.join(actual_imports)
    
    
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
    

def extract_single_function(l: list[str]) -> list[str]:
    num_lead_spaces: int = len(l[0]) - len(l[0].lstrip())
    func_lines_end: int = 0
    for j in range(1, len(l)):
        if len(l[j]) - len(l[j].lstrip()) == num_lead_spaces:
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
                if len(l[j]) - len(l[j].lstrip()) == num_lead_spaces:
                    break
                idx_to_remove.add(j)
    
    idx_to_remove_l: list[int] = sorted(list(idx_to_remove), reverse=True)
    l_copy = l[:]
    for i in idx_to_remove_l:
        del l_copy[i]
    
    return l_copy


def remove_typing_from_header_func(s: str) -> str:
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
                if len(l[j]) - len(l[j].lstrip()) == num_lead_spaces:
                    break
                idx_to_remove.add(j)
            
    
    idx_to_remove_l: list[int] = sorted(list(idx_to_remove), reverse=True)
    l_copy = l[:]
    for i in idx_to_remove_l:
        del l_copy[i]
    
    return l_copy


def remove_comments(l: list[str]) -> list[str]:
    idx_to_remove: set[int] = set()
    to_be_removed_1: bool = False
    to_be_removed_2: bool = False

    for i in range(len(l)):
        line: str = l[i]
        if line.strip().startswith('#'):
            idx_to_remove.add(i)
        elif to_be_removed_1:
            idx_to_remove.add(i)
            if line.strip() == "'''":
                to_be_removed_1 = not to_be_removed_1
        elif to_be_removed_2:
            idx_to_remove.add(i)
            if line.strip() == '"""':
                to_be_removed_2 = not to_be_removed_2
        else:
            if line.strip() == "'''":
                idx_to_remove.add(i)
                to_be_removed_1 = not to_be_removed_1
            elif line.strip() == '"""':
                idx_to_remove.add(i)
                to_be_removed_2 = not to_be_removed_2

    idx_to_remove_l: list[int] = sorted(list(idx_to_remove), reverse=True)
    l_copy = l[:]
    for i in idx_to_remove_l:
        del l_copy[i]
    
    return l_copy


def extract_distinct_functions(s: str) -> tuple[str, str, str, int]:
    p = re.compile('^(\s*)def (.+)\((.*)\)(.*):(\s*)$')
    l: list[str] = s.split('\n')
    t = [(i, re.findall(r'def (.+)\(', l[i])[0], len(l[i]) - len(l[i].lstrip()), len(l[i]) - len(l[i].lstrip()) != 0) for i in range(len(l)) if p.match(l[i])]
    
    # PICK LAST NON-NESTED FUNCTION (THE MAIN CODE FUNCTION)
    last_non_nested_function = t[0]
    for i in range(len(t)):
        if not t[i][3]:
            last_non_nested_function = t[i]
    
    # PUT MAIN FUNCTION CODE AT THE END AS LAST FUNCTION
    main_code_line = l[last_non_nested_function[0]]
    entry_point = last_non_nested_function[1]

    all_funcs: list[list[str]] = [remove_nested_functions(extract_single_function(l[t[i][0]:])) for i in range(len(t))]
    main_func_idx: int = None
    
    for i in range(len(all_funcs)):
        if all_funcs[i][0].strip() == main_code_line.strip():
            main_func_idx = i
            break

    all_funcs = all_funcs[:main_func_idx] + all_funcs[main_func_idx + 1:] + [all_funcs[main_func_idx]]
    
    for func in all_funcs:
        func[0] = remove_typing_from_header_func(func[0])

    indent_size: int = len(all_funcs[-1][1]) - len(all_funcs[-1][1].lstrip())

    return '\n\n'.join(['\n'.join(all_funcs[i]) for i in range(len(all_funcs))]), entry_point, '\n'.join(all_funcs[-1]), indent_size


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


def properly_arrange_code_with_imports_functions_globals(s: str, include_free_code: bool) -> tuple[str, str, list[str], str]:
    l: list[str] = [elem for elem in remove_comments(s.split('\n')) if elem.strip() != '']
    i: str = extract_imports(l)
    distinct_funcs, entry_point, main_func, indent_size = extract_distinct_functions('\n'.join(remove_internal_code_typing(remove_nested_imports(l))))
    f: str = tabs_as_symbols(distinct_funcs, indent_size)
    main_func = tabs_as_symbols(main_func, indent_size)
    if include_free_code:
        c: str = tabs_as_symbols('\n'.join(remove_imports_and_functions(l)), indent_size)
        return i + '\n\n' + f + '\n\n' + c + '\n', entry_point, i.split('\n'), main_func
    else:
        return i + '\n\n' + f + '\n\n', entry_point, i.split('\n'), main_func
    

def try_main():
    s = 'import numpy as np\nimport math\nimport string\nprint("---")\n#A comment\n# Another comment here\ndef incr(x):\n    # inside a comment\n    return x + 1\nprint("---")\n"""\nmultiline\ncomment\nhere\n"""\n'
    s += "'''\n" + '"""\n' + 'comment\n' + 'comment\n' + '"""\n' + "'''\n"
    s += '"""\n' + "'''\n" + 'comment\n' + 'comment\n' + "'''\n" + '"""\n' 
    s += "def incr2(x: int, y:float) -> float:\n    def incr3(x):\n        def incr4() -> int:\n            import os\n            '''\n            another\n            multiline\n            comment\n            here\n            '''\n            return 5\n        h: str = str([1, 2, 3, 4, 5][:2]) + str({k: k + 1 for k in [1, 2, 3]}) + str(5 == 6) \n        return 4 + incr4()\n    return incr(x) + incr3(x) + y\n\n"
    s += 'print(incr2(5, 1.0))\nprint(incr(1))\nprint(incr3(3))\nprint(incr4())\nfor _ in range(3):\n    for _ in range(2):\n        print("-" + "    ")\n\n'
    s += '"""\n' + "'''\n" + 'comment\n' + '"""\n' 
    s += "'''\n" + '"""\n' + 'comment\n' + 'comment\n' + "'''\n"
    print(s)
    print('='*100)
    s, entry_point, all_import, main_func = properly_arrange_code_with_imports_functions_globals(s, True)
    print(s)
    print('ENTRY POINT: ', entry_point)
    print('IMPORTS ', all_import)
    print('MAIN FUNC')
    print(main_func)
    print('='*100)
    exec(s, locals())
    #with open('file1.txt', 'w') as f:
    #    f.write(s)
    

if __name__ == '__main__':
    try_main()
