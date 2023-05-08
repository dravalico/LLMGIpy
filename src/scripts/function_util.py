import regex

def extract_function_from_str(output: str) -> str: # TODO More general and handle exception
    return output[output.index("def"): len(output):]


def extract_function_name(f: str) -> str: # TODO Handle the case of no name
    return f[f.index("def ") + len("def "): f.index("(")]


def tabs_as_symbol(f: str) -> str:
    return f.replace("    ", '\t').replace("  ", '\t')


def to_pony_individual(python_code: str) -> str:
    python_code = _remove_inline_comments(python_code)
    python_code = _remove_multiline_comments(python_code)
    python_code = _remove_empty_lines(python_code)
    return _substitute_tabs_with_pony_encode(python_code)


def _remove_inline_comments(python_code: str) -> str:
    res: str = ""
    for line in python_code.split('\n'):
        try:
            comment: str = line.split('#', 1)[1].split('\n', 1)[0]
            res += line.replace('#' + comment, '').rstrip()
        except:
            res += line
        res += '\n'
    return res


def _remove_multiline_comments(python_code: str) -> str:
    triple_2q: str = '"""'
    triple_1q: str = "'''"
    res: str = ""
    line_init: str = python_code.split('\n')[0].lstrip()
    is_take: bool = False if (line_init == triple_2q) or (
        line_init == triple_1q) else True
    is_stmn: bool = True if ((triple_2q in line_init) or (
        triple_1q in line_init)) and is_take else False
    is_take_prev: bool = is_take
    for line in python_code.split('\n'):
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


def _remove_empty_lines(python_code: str) -> str:
    res: list = []
    for line in python_code.split('\n'):
        if not regex.match(r'^\s*$', line):
            res.append(line + '\n')
    res[-1] = res[-1].replace('\n', '')
    return ''.join(res)


def _substitute_tabs_with_pony_encode(python_code: str) -> str:
    start_tab: str = "{:"
    end_tab: str = ":}"
    tab_counter: int = 0
    tmp_tab_counter: int = 0
    res: list = []
    index: int = 0
    for line in python_code.split('\n'):
        tmp_tab_counter = line.count('\t')
        line = line.replace('\t', '')
        if tmp_tab_counter > tab_counter:
            if index != 0:
                res[index - 1] = res[index - 1] \
                    .replace('\n', start_tab + '\n')
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
