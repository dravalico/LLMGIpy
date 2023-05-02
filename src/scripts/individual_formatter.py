import regex

_START_TAB: str = "{:"
_END_TAB: str = ":}"


def to_pony_individual(python_function: str) -> str:
    python_function = _remove_comments_from(python_function)
    python_function = _remove_empty_lines_from(python_function)
    return _substitute_tabs_with_pony_encode(python_function)


def _remove_comments_from(python_function: str) -> str:
    result: str = ""
    for line in python_function.split('\n'):
        try:
            comment: str = line.split('#', 1)[1].split('\n', 1)[0]
            result += line.replace('#' + comment, '')
        except:
            result += line
    return result


def _remove_empty_lines_from(python_function: str) -> str:
    result: list = []
    for line in python_function.split('\n'):
        if not regex.match(r'^\s*$', line):
            result.append(line + '\n')
    result[-1] = result[-1].replace('\n', '')
    return ''.join(result)


def _substitute_tabs_with_pony_encode(python_function: str) -> str:
    tab_counter: int = 0
    temp_counter: int = 0
    result: list = []
    index: int = 0
    for line in python_function.split('\n'):
        temp_counter = line.count('\t')
        line = line.replace('\t', '')
        if temp_counter > tab_counter:
            result[index - 1] = result[index - 1].replace('\n', _START_TAB + '\n')
            result.append(line)
        if temp_counter < tab_counter:
            result[index - 1] += _END_TAB + '\n'
            result.append(line)
        if temp_counter == tab_counter:
            result.append(line)
        result += '\n'
        tab_counter = temp_counter
        index = index + 2
    result.append(_END_TAB)
    return ''.join(result)
