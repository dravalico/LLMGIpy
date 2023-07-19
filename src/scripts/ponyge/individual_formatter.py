from typing import List, Any


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


def insert_strings_after_signature(code: str, imports: str) -> str:
    code_lines: List[str] = code.split("\n")
    function_line_index: str = next((i for i, line in enumerate(code_lines) if line.strip().startswith("def")), None)
    if function_line_index is None:
        raise ValueError("Problems with the function")
    for string in imports:
        code_lines.insert(function_line_index + 1, '\t' + string)
    modified_code = "\n".join(code_lines)
    return modified_code


def to_pony_individual(code: str, imports: str) -> str:
    code = insert_strings_after_signature(code, imports)
    return substitute_tabs_and_newlines_with_pony_encode(code)
