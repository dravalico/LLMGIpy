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


def extract_distinct_functions(s: str) -> str:
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
    
    all_funcs: list[list[str]] = [remove_nested_functions(extract_single_function(l[t[i][0]:])) for i in range(len(t))]
    main_func_idx: int = None
    
    for i in range(len(all_funcs)):
        if all_funcs[i][0].strip() == main_code_line.strip():
            main_func_idx = i
            break

    all_funcs = all_funcs[:main_func_idx] + all_funcs[main_func_idx + 1:] + [all_funcs[main_func_idx]]
    
    return '\n\n'.join(['\n'.join(all_funcs[i]) for i in range(len(all_funcs))])
    

def properly_arrange_code_with_imports_functions_globals(s: str) -> str:
    l: list[str] = s.split('\n')
    i: str = extract_imports(l)
    f: str = add_global_declarations_before_function_definitions(extract_distinct_functions('\n'.join(remove_nested_imports(l))))
    c: str = '\n'.join(remove_imports_and_functions(l))
    return i + '\n\n' + f + '\n\n' + c + '\n'
    

def try_main():
    s = 'import numpy as np\nimport math\nimport string\nprint("---")\ndef incr(x):\n    return x + 1\nprint("---")\n'
    s += 'def incr2(x) -> int:\n    def incr3(x):\n        def incr4() -> int:\n            import os\n            return 5\n        return 4 + incr4()\n    return incr(x) + incr3(x) + 1\n\n'
    s += 'print(incr2(5))\nprint(incr(1))\nprint(incr3(3))\nprint(incr4())\nfor _ in range(3):\n    for _ in range(2):\n        print("-")\n\n'
    print(s)
    print('='*20)
    s = properly_arrange_code_with_imports_functions_globals(s)
    print(s)
    print('='*20)
    exec(s)
    

if __name__ == '__main__':
    try_main()

