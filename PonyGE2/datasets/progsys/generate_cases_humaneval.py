import json
import math
import re
import numpy as np
import random
import string
from typing import Any
from collections import Counter


# ======================================================================================
# SUPPORT FUNCTION
# ======================================================================================


def blank_space() -> str:
    return ' '


def generate_nested_parentheses() -> str:
    nested_str: str = ""
    for _ in range(random.randint(0, 10)):
        nested_str += '(' + __generate_nested_macro_group(random.randint(0, 10)) + ')' + ' '
    return nested_str.strip()


def __generate_nested_macro_group(num_groups: int) -> str:
    nested_str: str = ""
    for _ in range(num_groups):
        nested_str += __generate_nested_group(random.randint(0, 10))
    return nested_str


def __generate_nested_group(max_depth: int) -> str:
    depth: int = random.randint(0, max_depth)
    nested_group: str = ""
    for _ in range(depth):
        nested_group += "("
    for _ in range(depth):
        nested_group += ")"
    return nested_group


def generate_random_palindrome(length: int) -> str:
    s: str = ''.join(random.choice(string.ascii_letters) for _ in range(length))
    return s + s[::-1]


def add_zero_for_single_digit(n: int) -> str:
    if 0 <= n <= 9:
        return f'0{n}'
    return str(n)


def add_global_declarations_before_function_definitions(s: str) -> str:
    p = re.compile('^(\s*)def (.+)\((.*)\)(.*):(\s*)$')
    l: list[str] = s.split('\n')
    t = [(i, re.findall(r'def (.+)\(', l[i])[0], len(l[i]) - len(l[i].lstrip())) for i in range(len(l)) if p.match(l[i])][::-1]
    for i, function_name, num_lead_spaces in t:
        l.insert(i, f'{" " * num_lead_spaces}global {function_name}')
    return '\n'.join(l)


# ======================================================================================
# GENERATE INPUT FOR EACH PROBLEM AT RANDOM
# ======================================================================================


def generate_single_input_case(idx: int) -> list[Any]:
    if idx == 0:
        return [[round(random.uniform(0.0, 220.0), 2) for _ in range(random.randint(0, 40))], round(random.random(), 2)]
    elif idx == 1:
        return [generate_nested_parentheses() if random.random() < 0.5 else generate_nested_parentheses().replace(' ', '')]
    elif idx == 2:
        return [round(random.uniform(0.0, 100000.0), 2)]
    elif idx == 3:
        if random.random() < 0.2:
            return [[random.randint(-10, 40) for _ in range(random.randint(0, 40))]]
        else:
            return [random.choice([[60, 42, 12], [423, 40, -50, 32, -5], [5, 4, -30, 2], [-20, 100, 200], [2, 5, 10, -7], [50, -200, 500], [2, 1, 5, -1], [-10, 5, 5], [0, 0, 0, 0, 0], [0, 0], [-2], [-50, -6, -7, -7], [1, 1, 12, 5, 7, -2, -5], [6, 1, 2, 4, -20], [5, 40, -80, 6], [64, 100, 50, 45, -105, 41, -5], [1, 2, 3], [1, 2, -4, 5], [1, 2, -3, 1, 2, -3], [1, 2, -4, 5, 6], [1, -1, 2, -2, 5, -5, 4, -4], [1, -1, 2, -2, 5, -5, 4, -5], [1, -2, 2, -2, 5, -5, 4, -4]])]
    elif idx == 4:
        return [[round(random.uniform(0.0, 10000.0), 2) for _ in range(random.randint(1, 40))]]
    elif idx == 5:
        c: int = random.randint(0, 40)
        l: list[int] = []
        for _ in range(random.randint(0, 40)):
            if random.random() < 0.4:
                l.append(c)
                c = random.randint(0, 40)
            else:
                c = random.randint(0, 40)
                l.append(c)
        return [l, random.randint(0, 1000)]
    elif idx == 6:
        return [generate_nested_parentheses()]
    elif idx == 7:
        if random.random() < 0.9:
            if random.random() < 0.5:
                return [[''.join(random.choice(string.ascii_letters + blank_space()) for _ in range(random.randint(0, 40))) for _ in range(random.randint(0, 40))], ''.join(random.choice(string.ascii_letters) for _ in range(random.randint(0, 10)))]
            else:
                ss: str = ''.join(random.choice(string.ascii_letters) for _ in range(random.randint(2, 10)))
                l: list[str] = [''.join(random.choice(string.ascii_letters + blank_space()) for _ in range(random.randint(0, 40))) if random.random() < 0.4 else ''.join(random.choice(string.ascii_letters + blank_space()) for _ in range(random.randint(0, 15))) + ss + ''.join(random.choice(string.ascii_letters + blank_space()) for _ in range(random.randint(0, 15))) for _ in range(random.randint(0, 40))]
                return [l, ss]
        else:
            return random.choice([[['abc', 'bacd', 'cde', 'array'], 'a'], [['xxx', 'asd', 'xxy', 'john doe', 'xxxAAA', 'xxx'], 'xxx'], [['xxx', 'asd', 'aaaxxy', 'john doe', 'xxxAAA', 'xxx'], 'xx'], [['grunt', 'trumpet', 'prune', 'gruesome'], 'run']])
    elif idx == 8:
        return [[random.randint(0, 100) for _ in range(random.randint(0, 40))]]
    elif idx == 9:
        return [[random.randint(0, 100) for _ in range(random.randint(0, 40))]]
    elif idx == 10:
        return [''.join(random.choice(string.ascii_lowercase) for _ in range(random.randint(0, 40))) if random.random() < 0.7 else generate_random_palindrome(random.randint(0, 20)).lower()]
    elif idx == 11:
        n: int = random.randint(0, 40)
        return [''.join(random.choice(['0', '1']) for _ in range(n)), ''.join(random.choice(['0', '1']) for _ in range(n))]
    elif idx == 12:
        return [[''.join(random.choice(string.ascii_lowercase) for _ in range(random.randint(0, 40))) for _ in range(random.randint(0, 40))]]
    elif idx == 13:
        return [random.randint(1, 500), random.randint(1, 500)]
    elif idx == 14:
        return [''.join(random.choice(string.ascii_letters) for _ in range(random.randint(0, 20)))]
    elif idx == 15:
        return [random.randint(0, 100)]
    elif idx == 16:
        return [''.join(random.choice(string.ascii_letters + blank_space()) for _ in range(random.randint(0, 40)))]
    elif idx == 17:
        return [' '.join(random.choice(['o', 'o|', '.|']) for _ in range(random.randint(0, 40)))]
    elif idx == 18:
        if random.random() < 0.9:
            if random.random() < 0.5:
                return [''.join(random.choice(string.ascii_lowercase + blank_space()) for _ in range(random.randint(0, 40))), ''.join(random.choice(string.ascii_lowercase) for _ in range(random.randint(0, 10)))]
            else:
                ss: str = ''.join(random.choice(string.ascii_lowercase) for _ in range(random.randint(2, 10)))
                l: list[str] = [''.join(random.choice(string.ascii_lowercase + blank_space()) for _ in range(random.randint(0, 40))) if random.random() < 0.5 else ss for _ in range(random.randint(0, 40))]
                return [''.join(l), ss]
        else:
            return random.choice([['aaa', 'a'], ['aaaa', 'aa'], ['xyxyxyx', 'x'], ['cacacacac', 'cac'], ['john doe', 'john']])
    elif idx == 19:
        return [' '.join(random.choice(['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine']) for _ in range(random.randint(0, 40)))]
    elif idx == 20:
        return [[round(random.uniform(0.0, 10000.0), 2) for _ in range(random.randint(2, 40))]]
    elif idx == 21:
        return [[round(random.uniform(0.0, 10000.0), 2) for _ in range(random.randint(2, 40))]]
    elif idx == 22:
        return [[random.choice([[]] * random.randint(0, 5) + [{}] * random.randint(0, 5) + [set()] * random.randint(0, 5) + [random.randint(0, 500)] * random.randint(0, 15) + [random.uniform(0, 500.0)] * random.randint(0, 5) + [''.join(random.choice(string.ascii_letters) for _ in range(random.randint(0, 10)))] * random.randint(0, 5) + [True] * random.randint(0, 5) + [False] * random.randint(0, 5)) for _ in range(random.randint(0, 40))]]
    elif idx == 23:
        return [''.join(random.choice(string.ascii_letters) for _ in range(random.randint(0, 40)))]
    elif idx == 24:
        return [random.randint(0, 10000)]
    elif idx == 25:
        return [random.randint(0, 10000)]
    elif idx == 26:
        return [[random.randint(0, 20) for _ in range(random.randint(0, 40))]]
    elif idx == 27:
        return [''.join(random.choice(string.ascii_letters + '!.?$^' + string.digits + blank_space()) for _ in range(random.randint(0, 40)))]
    elif idx == 28:
        return [[''.join(random.choice(string.ascii_letters) for _ in range(random.randint(0, 40))) for _ in range(random.randint(0, 40))]]
    elif idx == 29:
        if random.random() < 0.95:
            if random.random() < 0.5:
                return [[''.join(random.choice(string.ascii_lowercase) for _ in range(random.randint(0, 40))) for _ in range(random.randint(0, 40))], ''.join(random.choice(string.ascii_lowercase) for _ in range(random.randint(0, 5)))]
            else:
                ss: str = ''.join(random.choice(string.ascii_lowercase) for _ in range(random.randint(2, 10)))
                l: list[str] = [''.join(random.choice(string.ascii_lowercase) for _ in range(random.randint(0, 40))) if random.random() < 0.5 else ss + ''.join(random.choice(string.ascii_lowercase) for _ in range(random.randint(0, 15))) for _ in range(random.randint(0, 40))]
                return [l, ss]
        else:
            return random.choice([[['abc', 'bcd', 'cde', 'array'], 'a'], [['xxx', 'asd', 'xxy', 'john doe', 'xxxAAA', 'xxx'], 'xxx']])
    elif idx == 30:
        return [[random.randint(-1000, 1000) for _ in range(random.randint(0, 40))]]
    elif idx == 31:
        return [random.randint(0, 10000)] if random.random() < 0.55 else [random.choice([2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71])]
    elif idx == 32:
        return [[(-1 if random.random() < 0.5 else 1) * random.randint(1, 100) for _ in range(random.choice([2, 4, 6, 8, 10, 12, 14, 16, 18, 20]))]]
    elif idx == 33:
        return [[random.randint(-1000, 1000) for _ in range(random.randint(3, 40))]]
    elif idx == 34:
        return [[random.randint(0, 20) for _ in range(random.randint(0, 40))]]
    elif idx == 35:
        return [[random.randint(-1000, 1000) for _ in range(random.randint(1, 40))]]
    elif idx == 36:
        return [random.randint(0, 2000)]
    elif idx == 37:
        return [[random.randint(-1000, 1000) for _ in range(random.randint(3, 40))]]
    elif idx == 38:
        return [''.join(random.choice(string.ascii_lowercase) for _ in range(random.randint(0, 40)))]
    elif idx == 39:
        return [random.randint(0, 10)]
    elif idx == 40:
        if random.random() < 0.85:
            return [[random.randint(-1000, 1000) for _ in range(random.randint(0, 40))]]
        else:
            c: int = random.randint(-1000, 1000)
            if random.random() < 0.5:
                l: list[int] = [c, -c, 0] + [random.randint(-1000, 1000) for _ in range(random.randint(0, 37))]
            else:
                l: list[int] = [c, c, -2 * c] + [random.randint(-1000, 1000) for _ in range(random.randint(0, 37))]
            random.shuffle(l)
            return [random.choice([[1, 3, -2, 1], [2, 4, -5, 3, 9, 7], [10, 20, -50, 30, -2], [-20, -40, 5, 4, 60], [-2, 3, -1, 0], l, l, l, l, l, l, l, l, l, l])]
    elif idx == 41:
        return [random.randint(0, 10000)]
    elif idx == 42:
        return [[random.randint(-1000, 1000) for _ in range(random.randint(0, 40))]]
    elif idx == 43:
        if random.random() < 0.55:
            return [[random.randint(-1000, 1000) for _ in range(random.randint(0, 40))]]
        else:
            c: int = random.randint(-1000, 1000)
            l: list[int] = [c, -c] + [random.randint(-1000, 1000) for _ in range(random.randint(0, 38))]
            random.shuffle(l)
            return [random.choice([[2, 4, -5, 3, 5, 7], [-3, 9, -1, 3, 2, 31], [-3, 9, -1, 3, 2, 30], [-5, 5], [10, 12, -15, 40, -5, -40, 7, 2], l, l, l, l, l, l, l, l, l, l])]
    elif idx == 44:
        return [random.randint(0, 100), random.randint(2, 10)]
    elif idx == 45:
        return [random.randint(0, 10000), random.randint(0, 10000)]
    elif idx == 46:
        return [random.randint(0, 50)]
    elif idx == 47:
        return [[random.randint(-1000, 1000) for _ in range(random.randint(1, 40))]]
    elif idx == 48:
        return [''.join(random.choice(string.ascii_lowercase) for _ in range(random.randint(0, 40))) if random.random() < 0.55 else generate_random_palindrome(random.randint(0, 20)).lower()]
    elif idx == 49:
        return [random.randint(0, 100), random.randint(1, 100)]
    elif idx == 50:
        return [''.join(random.choice(string.ascii_lowercase) for _ in range(random.randint(0, 40)))]
    elif idx == 51:
        if random.random() < 0.8:
            return [''.join(random.choice(string.ascii_letters + 'aeiouAEIOU' * 3 + '.?!^$') for _ in range(random.randint(0, 40)))]
        else:
            return [random.choice(['abcdef.nghijklm', 'abcdef', 'aaaaa', 'aaBAA', 'zbcd', 'fedcba', 'eeeee', 'acBAA', 'EcBOO', 'ybcd'])]
    elif idx == 52:
        if random.random() < 0.55:
            return [[random.randint(0, 100) for _ in range(random.randint(0, 40))], random.randint(0, 100)]
        else:
            l: list[int] = [random.randint(0, 100) for _ in range(random.randint(1, 40))]
            m: int = max(l) + random.randint(1, 40)
            return [l, m]
    elif idx == 53:
        return [random.randint(0, 10000), random.randint(0, 10000)]
    elif idx == 54:
        if random.random() < 0.5:
            return [''.join(random.choice(string.ascii_lowercase) for _ in range(random.randint(0, 40))), ''.join(random.choice(string.ascii_lowercase) for _ in range(random.randint(0, 40)))]
        else:
            l: list[str] = [random.choice(string.ascii_lowercase) for _ in range(random.randint(0, 20))]
            l1: list[str] = [c for c in l]
            random.shuffle(l1)
            return [''.join(l) * random.randint(1, 4), ''.join(l1) * random.randint(1, 4)]
    elif idx == 55:
        return [random.randint(0, 20)]
    elif idx == 56:
        if random.random() < 0.5:
            return [''.join(random.choice(['<', '>']) for _ in range(random.randint(0, 40)))]
        else:
            n: int = random.randint(0, 20)
            if random.random() < 0.5:
                return ['<>' * n if random.random() < 0.5 else '<' * n + '>' * n]
            else:
                return ['<' + '<>' * n + '>' if random.random() < 0.5 else '<' * n + '<>' * random.randint(2, 5) + '>' * n]
    elif idx == 57:
        return [[random.randint(-200, 200) for _ in range(random.randint(0, 40))] if random.random() < 0.53 else sorted([random.randint(-200, 200) for _ in range(random.randint(0, 40))], reverse=(True if random.random() < 0.5 else False))]
    elif idx == 58:
        return [[random.randint(0, 20) for _ in range(random.randint(0, 40))], [random.randint(0, 20) for _ in range(random.randint(0, 40))]]
    elif idx == 59:
        return [random.randint(4, 10000)]
    elif idx == 60:
        return [random.randint(0, 10000)]
    elif idx == 61: # SIMILAR TO 56
        if random.random() < 0.5:
            return [''.join(random.choice(['(', ')']) for _ in range(random.randint(0, 40)))]
        else:
            n: int = random.randint(0, 20)
            if random.random() < 0.5:
                return ['()' * n if random.random() < 0.5 else '(' * n + ')' * n]
            else:
                return ['(' + '()' * n + ')' if random.random() < 0.5 else '(' * n + '()' * random.randint(2, 5) + ')' * n]
    elif idx == 62:
        return [[random.randint(1, 100) for _ in range(random.randint(2, 40))]]
    elif idx == 63:
        return [random.randint(0, 12)]
    elif idx == 64:
        if random.random() < 0.65:
            return [''.join(random.choice(string.ascii_letters + 'aeiouAEIOUyY' * 3) for _ in range(random.randint(1, 40)))]
        else:
            return [''.join(random.choice(string.ascii_letters + 'aeiouAEIOUyY' * 3) + random.choice(['y', 'Y']) for _ in range(random.randint(1, 40)))]
    elif idx == 65:
        return [random.randint(1, 1000), random.randint(1, 100)] if random.random() < 0.5 else [random.randint(1, 1000), random.randint(1, 3)]
    elif idx == 66:
        return [''.join(random.choice(string.ascii_letters + blank_space()) for _ in range(random.randint(0, 40)))]
    elif idx == 67:
        apples: int = random.randint(0, 100)
        oranges: int = random.randint(0, 100)
        mangos: int = random.randint(0, 100)
        return [f'{apples} apples and {oranges} oranges', apples + oranges + mangos]
    elif idx == 68:
        return [[random.randint(0, 1000) for _ in range(random.randint(0, 40))]]
    elif idx == 69:
        if random.random() < 0.5:
            return [[random.randint(1, 100) for _ in range(random.randint(1, 40))]]
        else:
            n: int = random.randint(1, 10)
            l: list[int] = [n] * (n + random.randint(0, 5)) + [random.randint(1, 100) for _ in range(random.randint(1, 30))]
            random.shuffle(l)
            return [l]
    elif idx == 70:
        return [[random.randint(-100, 100) for _ in range(random.randint(0, 40))]]
    elif idx == 71:
        return [random.randint(1, 100), random.randint(1, 100), random.randint(1, 100)] if random.random() < 0.75 else random.choice([[random.randint(1, 25), random.randint(1, 25), random.randint(50, 100)], [random.randint(1, 25), random.randint(50, 100), random.randint(1, 25)], [random.randint(50, 100), random.randint(1, 25), random.randint(1, 25)]])
    elif idx == 72:
        if random.random() < 0.5:
            return [[random.randint(1, 100) for _ in range(random.randint(1, 40))], random.randint(1, 100)]
        else:
            l: list[int] = [random.randint(1, 100) for _ in range(random.randint(1, 20))]
            l = l + l[::-1]
            n: int = sum(l)
            return [l, random.randint(n, n + 50)]
    elif idx == 73:
        if random.random() < 0.5:
            return [[random.randint(0, 20) for _ in range(random.randint(0, 40))]]
        else:
            l: list[int] = [[random.randint(0, 20) for _ in range(random.randint(1, 20))]]
            l = l + l[::-1]
            for _ in range(random.randint(0, len(l) // 2)):
                l[random.randint(0, len(l) - 1)] = random.randint(0, 20)
            return [l]
    elif idx == 74:
        return [[''.join(random.choice(string.ascii_letters + string.digits) for _ in range(random.randint(0, 40))) for _ in range(random.randint(0, 40))], [''.join(random.choice(string.ascii_letters + string.digits) for _ in range(random.randint(0, 40))) for _ in range(random.randint(0, 40))]]
    elif idx == 75:
        if random.random() < 0.65:
            return [random.randint(0, 60)]
        else:
            l: list[int] = random.choice([[2, 2, 2], [3, 3, 3], [2, 2, 3], [3, 3, 2], [2, 2, 5], [3, 3, 5], [2, 3, 5], [2, 2, 7], [2, 3, 7], [2, 5, 5], [7, 3, 3], [13, 2, 2], [11, 2, 2], [11, 3, 2]])
            return [l[0] * l[1] * l[2]]
    elif idx == 76:
        if random.random() < 0.5:
            return [random.randint(1, 1000), random.randint(1, 5)]
        else:
            n: int = random.randint(1, 5)
            x: int = n ** random.randint(0, 5)
            return [x, n] if random.random() < 0.8 else random.choice([[1, 4], [2, 2], [8, 2], [16, 2], [4, 2], [9, 3], [16, 4], [1, 1], [1, 12]])
    elif idx == 77:
        return [random.randint(-1000, 1000)] if random.random() < 0.52 else [random.randint(-100, 100) ** 3]
    elif idx == 78:
        return [''.join(random.choice(['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F']) for _ in range(random.randint(0, 40)))]
    elif idx == 79:
        return [random.randint(0, 1000)]
    elif idx == 80:
        if random.random() < 0.65:
            return [''.join(random.choice(string.ascii_lowercase) for _ in range(random.randint(0, 40)))]
        else:
            l: list[str] = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
            random.shuffle(l)
            l = l[random.randint(0, 20):]
            return [''.join(l)]
    elif idx == 81:
        return [[random.choice([round(i, 2) for i in np.linspace(start=0.0, stop=4.0, num=41).tolist()]) for _ in range(random.randint(0, 40))]]
    elif idx == 82:
        return [''.join(random.choice(string.ascii_lowercase) for _ in range(random.randint(0, 40)))] if random.random() < 0.68 else [''.join(random.choice(string.ascii_lowercase) for _ in range(random.choice([2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71])))]
    elif idx == 83:
        return [random.randint(1, 40)]
    elif idx == 84:
        return [random.randint(0, 10000)]
    elif idx == 85:
        return [[random.randint(0, 1000) for _ in range(random.randint(1, 40))]]
    elif idx == 86:
        return [' '.join([''.join(random.choice(string.ascii_letters + '!?^$.-_') for _ in range(random.randint(0, 40))) for _ in range(random.randint(0, 40))])]
    elif idx == 87:
        n: int = random.randint(1, 20)
        l: list[list[int]] = []
        for _ in range(random.randint(1, 10)):
            l1: list[int] = [random.randint(1, 20) for _ in range(random.randint(1, 9))]
            if random.random() < 0.5:
                l1 = l1 + [n]
            random.shuffle(l1)
            l.append(l1)
        random.shuffle(l)
        return [l, n]
    elif idx == 88:
        return [[random.randint(0, 100) for _ in range(random.randint(0, 40))]]
    elif idx == 89:
        return [''.join(random.choice(string.ascii_lowercase + '-_.!?^$#@') for _ in range(random.randint(0, 40)))]
    elif idx == 90:
        return [[random.randint(-100, 100) for _ in range(random.randint(0, 40))]]
    elif idx == 91:
        s: str = ''
        n: int = random.randint(0, 40)
        for _ in range(n):
            if random.random() < 0.5:
                s += 'I '
            s += ''.join(random.choice(string.ascii_letters + blank_space() * 12) for _ in range(random.randint(0, 40)))
            s += random.choice(['.', '?', '!', ' .', ' ?', ' !'])
            s += ' '
        return [s]
    elif idx == 92:
        if random.random() < 0.5:
            return [random.randint(-100, 100) if random.random() < 0.7 else round(random.uniform(-100.0, 100.0), 2), random.randint(-100, 100) if random.random() < 0.7 else round(random.uniform(-100.0, 100.0), 2), random.randint(-100, 100) if random.random() < 0.7 else round(random.uniform(-100.0, 100.0), 2)]
        else:
            n1: int = random.randint(-100, 100)
            n2: int = random.randint(-100, 100)
            l: list[int] = [n1, n2, n1 + n2]
            random.shuffle(l)
            return l
    elif idx == 93:
        return [''.join(random.choice(string.ascii_letters + blank_space() * 12) for _ in range(random.randint(0, 40)))]
    elif idx == 94:
        if random.random() < 0.8:
            l: list[int] = [random.randint(0, 1000) for _ in range(random.randint(0, 39))] + [random.choice([2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71])]
            random.shuffle(l)
            return [l]
        else:
            return [[random.randint(0, 1000) for _ in range(random.randint(0, 10))]]
    elif idx == 95:
        d: dict[str, str] = {}
        if random.random() < 0.48:
            for _ in range(random.randint(0, 10)):
                d[''.join(random.choice(string.ascii_letters) for _ in range(random.randint(1, 10)))] = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(random.randint(0, 10)))
        else:
            if random.random() < 0.5:
                for _ in range(random.randint(0, 10)):
                    d[''.join(random.choice(string.ascii_lowercase) for _ in range(random.randint(1, 10)))] = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(random.randint(0, 10)))
            else:
                for _ in range(random.randint(0, 10)):
                    d[''.join(random.choice(string.ascii_uppercase) for _ in range(random.randint(1, 10)))] = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(random.randint(0, 10)))
        return [d]
    elif idx == 96:
        return [random.randint(0, 200)]
    elif idx == 97:
        return [random.randint(-2000, 2000), random.randint(-2000, 2000)]
    elif idx == 98:
        if random.random() < 0.5:
            return [''.join(random.choice(string.ascii_letters) for _ in range(random.randint(0, 40)))]
        else:
            l: list[str] = ['A', 'E', 'I', 'O', 'U'] * 4 + [random.choice(string.ascii_letters) for _ in range(random.randint(0, 20))]
            random.shuffle(l)
            return [''.join(l)]
    elif idx == 99:
        return [str(random.randint(-2000, 2000)) if random.random() < 0.5 else str(round(random.uniform(-2000.0, 2000.0), 2))]
    elif idx == 100:
        return [random.randint(0, 40)]
    elif idx == 101:
        s: str = ''
        for _ in range(random.randint(0, 20)):
            s += ''.join(random.choice(string.ascii_letters) for _ in range(random.randint(0, 20)))
            s += random.choice([',', ' ', ', '])
        return [s]
    elif idx == 102:
        n1: int = random.randint(1, 1000)
        n2: int = random.randint(1, 1000)
        return [min(n1, n2), max(n1, n2)] if random.random() < 0.65 else [max(n1, n2), min(n1, n2)]
    elif idx == 103:
        n1: int = random.randint(1, 1000)
        n2: int = random.randint(1, 1000)
        return [min(n1, n2), max(n1, n2)] if random.random() < 0.65 else [max(n1, n2), min(n1, n2)]
    elif idx == 104:
        return [[random.randint(0, 1000) for _ in range(random.randint(0, 40))]] if random.random() < 0.6 else [[random.choice([0, 1, 3, 5, 7, 9, 10, 11, 13, 15, 17, 19, 20, 30, 31, 33, 35, 37, 39, 40, 50, 51, 53, 55, 57, 59, 60, 70, 71, 73, 75, 77, 79, 80, 90, 91, 93, 95, 97, 99, 100] + [2, 4, 6, 8, 12, 14, 16, 18, 42, 44, 46, 48, 82, 84, 86, 88]) for _ in range(random.randint(0, 40))]]
    elif idx == 105:
        return [[random.randint(-10, 20) for _ in range(random.randint(0, 40))]]
    elif idx == 106:
        return [random.randint(0, 20)]
    elif idx == 107:
        return [random.randint(1, 1500)]
    elif idx == 108:
        return [[random.randint(-1000, 1000) for _ in range(random.randint(0, 40))]]
    elif idx == 109:
        if random.random() < 0.55:
            return [list(set([random.randint(1, 1000) for _ in range(random.randint(0, 40))]))]
        else:
            l: list[int] = []
            n: int = 1
            for _ in range(random.randint(4, 40)):
                l.append(random.randint(n, n + 9))
                n += 10
            if random.random() < 0.85:
                c: int = random.randint(1, len(l) - 2)
                return [l[c:] + l[:c]]
            return [l]
    elif idx == 110:
        return [[random.randint(1, 1000) for _ in range(random.randint(1, 40))], [random.randint(1, 1000) for _ in range(random.randint(1, 40))]]
    elif idx == 111:
        return [' '.join(random.choice(string.ascii_lowercase) for _ in range(random.randint(0, 40)))]
    elif idx == 112:
        if random.random() < 0.55:
            return [''.join(random.choice(string.ascii_lowercase) for _ in range(random.randint(0, 40))), ''.join(random.choice(string.ascii_lowercase) for _ in range(random.randint(0, 10)))]
        else:
            alphabet: list[str] = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
            random.shuffle(alphabet)
            c: int = random.randint(10, 20)
            alphabet1: list[str] = alphabet[:c]
            alphabet2: list[str] = alphabet[c:]
            s1: list[str] = [random.choice(alphabet1) if random.random() < 0.5 else random.choice(alphabet2) for _ in range(random.randint(0, 40))]
            s2: list[str] = [random.choice(alphabet2) for _ in range(random.randint(0, 40))]
            sp: list[str] = [char for char in s1 if char not in s2]
            return [''.join(s1 + sp[::-1]) if random.random() < 0.5 else ''.join(s1 + s1[::-1]), ''.join(s2)]
    elif idx == 113:
        return [[''.join(random.choice(string.digits) for _ in range(random.randint(0, 40))) for _ in range(random.randint(0, 40))]]
    elif idx == 114:
        return [[random.randint(-10000, 10000) for _ in range(random.randint(1, 40))]]
    elif idx == 115:
        n_rows: int = random.randint(1, 10)
        n_cols: int = random.randint(1, 10)
        grid: list[list[int]] = [[random.choice([0, 1]) for _ in range(n_cols)] for _ in range(n_rows)]
        return [grid, random.randint(1, 10)]
    elif idx == 116:
        return [[random.randint(0, 1000) for _ in range(random.randint(0, 40))]]
    elif idx == 117:
        if random.random() < 0.55:
            return [' '.join(''.join(random.choice(string.ascii_letters) for _ in range(random.randint(1, 14))) for _ in range(random.randint(0, 20))), random.randint(1, 10)]
        else:
            consonants: list[str] = ['b', 'c', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'm', 'n', 'p', 'q', 'r', 's', 't', 'v', 'w', 'x', 'y', 'z']
            consonants = consonants + [c.upper() for c in consonants]
            s: str = ''
            n: int = random.randint(1, 10)
            for _ in range(random.randint(0, 20)):
                if random.random() < 0.5:
                    l = [random.choice(consonants) for _ in range(n)] + [random.choice('aeiouAEIOU') for _ in range(random.randint(1, 4))]
                    random.shuffle(l)
                    s += ''.join(l)
                else:
                    s += ''.join(random.choice(string.ascii_letters) for _ in range(random.randint(1, 14)))
                s += ' '
            return [s, n]
    elif idx == 118:
        if random.random() < 0.2:
            return [''.join(random.choice(string.ascii_letters) for _ in range(random.randint(0, 40)))]
        else:
            if random.random() < 0.5:
                return [''.join([random.choice(string.ascii_lowercase + 'aeiou') for _ in range(random.randint(0, 40))])]
            else:
                return [''.join([random.choice(string.ascii_uppercase + 'AEIOU') for _ in range(random.randint(0, 40))])]
    elif idx == 119:
        if random.random() < 0.5:
            return [[''.join(random.choice(['(', ')']) for _ in range(random.randint(0, 40))), ''.join(random.choice(['(', ')']) for _ in range(random.randint(0, 40)))]]
        else:
            n: int = random.randint(1, 20)
            if random.random() < 0.5:
                s1: list[str] = ['('] * n
                s2: list[str] = [')'] * n
            else:
                if random.random() < 0.5:
                    s1: list[str] = ['()'] * n + ['(']
                    s2: list[str] = [')'] + ['()'] * n
                else:
                    s1: list[str] = ['('] + ['()'] * n + ['(']
                    s2: list[str] = [')'] + ['()'] * n + [')']
            return [[''.join(s1), ''.join(s2)]] if random.random() < 0.5 else [[''.join(s2), ''.join(s1)]]
    elif idx == 120:
        array_size: int = random.randint(1, 40)
        return [[random.randint(-1000, 1000) for _ in range(array_size)], random.randint(0, array_size)]
    elif idx == 121:
        return [[random.randint(1, 1000) for _ in range(random.randint(1, 40))]]
    elif idx == 122:
        array_size: int = random.randint(1, 40)
        return [[random.randint(-10, 160) for _ in range(array_size)], random.randint(1, array_size)]
    elif idx == 123:
        return [random.randint(0, 1000)]
    elif idx == 124:
        return [f'{random.randint(1, 20)-random.randint(1, 100)}' if random.random() < 0.2 else f'{add_zero_for_single_digit(random.randint(0, 16))}-{add_zero_for_single_digit(random.randint(0, 35))}-{random.randint(1900, 2024)}']
    elif idx == 125:
        if random.random() < 0.6:
            if random.random() < 0.5:
                return [' '.join(''.join(random.choice(string.ascii_letters + ',,,,,,,,,,' + '!?.') for _ in range(random.randint(0, 20))) for _ in range(random.randint(0, 20)))]
            else:
                return [','.join(''.join(random.choice(string.ascii_letters + '!?.') for _ in range(random.randint(0, 20))) for _ in range(random.randint(0, 20)))]
        else:
            alphabet: list[str] = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
            alphabet = [alpha.upper() for alpha in alphabet]
            random.shuffle(alphabet)
            return [''.join(''.join(random.choice(string.ascii_lowercase + '!?.' + ''.join(alphabet[:6])) for _ in range(random.randint(0, 20))) for _ in range(random.randint(0, 20)))]
    elif idx == 126:
        return [[random.randint(0, 100) for _ in range(random.randint(0, 20))] if random.random() < 0.4 else (sorted(list(set([random.randint(0, 100) for _ in range(random.randint(0, 20))]))) if random.random() < 0.5 else sorted(list([random.randint(0, 10) for _ in range(random.randint(0, 20))])))]
    elif idx == 127:
        if random.random() < 0.63:
            n1: int = random.randint(-40, 40)
            n2: int = random.randint(-40, 40)
            return [(min(n1, n2), min(n1, n2) + random.randint(0, 40)), (max(n1, n2), max(n1, n2) + random.randint(0, 40))]
        else:
            n1: int = random.randint(-40, 40)
            n2: int = random.choice([2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71])
            return [(n1, n1 + 2 * n2), (n1 + n2, n1 + n2 + 2 * n2)]
    elif idx == 128:
        return [[random.randint(-100, 100) for _ in range(random.randint(0, 40))]]
    elif idx == 129:
        n: int = random.randint(2, 20)
        l: list[int] = list(range(1, n*n + 1))
        random.shuffle(l)
        return [np.reshape(l, (n, n)).tolist(), random.randint(1, 20)]
    elif idx == 130:
        return [random.randint(0, 50)]
    elif idx == 131:
        return [random.randint(0, 100000)] if random.random() < 0.9 else [random.choice([20, 40, 60, 80, 200, 220, 422, 642, 8246, 4642, 622, 442, 888, 666, 2424])]
    elif idx == 132:
        if random.random() < 0.55:
            return [''.join(random.choice(['[', ']']) for _ in range(random.randint(0, 40)))]
        else:
            n: int = random.randint(0, 20)
            return [random.choice([']' * n + '[', ']' + '[' * n, '[' + ']' * n, '[' * n + ']', '[]' * n, ']' * n, '[' * n])]
    elif idx == 133:
        return [[round(random.uniform(-1000.0, 1000.0), 2) for _ in range(random.randint(0, 40))]]
    elif idx == 134:
        if random.random() < 0.5:
            return [''.join(random.choice(string.ascii_letters) if random.random() < 0.65 else ' ' for _ in range(random.randint(0, 40)))]
        else:
            if random.random() < 0.8:
                return [''.join(random.choice(string.ascii_letters) if random.random() < 0.65 else ' ' for _ in range(random.randint(0, 40))) + ' ' + random.choice(string.ascii_letters)]
            else:
                return [''.join(random.choice(string.ascii_letters) if random.random() < 0.65 else ' ' for _ in range(random.randint(0, 40))) + ' ' + random.choice(string.digits)]
    elif idx == 135:
        if random.random() < 0.6:
            return [list(set([random.randint(0, 1000) for _ in range(random.randint(0, 40))]))]
        else:
            n: int = random.randint(100, 500)
            d: int = random.randint(1, 10)
            l1: list[int] = list(set([random.randint(0, n - d - 1) for _ in range(random.randint(0, 20))]))
            l2: list[int] = list(set([random.randint(n + 1, 1000) for _ in range(random.randint(0, 20))]))
            return [l1 + [n, n - d] + l2] if random.random() < 0.5 else [l2 + [n, n - d] + l1]
    elif idx == 136:
        if random.random() < 0.7:
            return [[random.randint(-1000, 1000) for _ in range(random.randint(0, 40))]]
        else:
            if random.random() < 0.5:
                return [[random.randint(0, 1000) for _ in range(random.randint(0, 40))]]
            else:
                return [[random.randint(-1000, 0) for _ in range(random.randint(0, 40))]]
    elif idx == 137:
        if random.random() < 0.7:
            return [random.choice([random.randint(-1000, 1000), str(random.randint(-1000, 1000)), round(random.uniform(-1000.0, 1000.0), 2), str(round(random.uniform(-1000.0, 1000.0), 2)), str(round(random.uniform(-1000.0, 1000.0), 2)).replace('.', ',')]), random.choice([random.randint(-1000, 1000), str(random.randint(-1000, 1000)), round(random.uniform(-1000.0, 1000.0), 2), str(round(random.uniform(-1000.0, 1000.0), 2)), str(round(random.uniform(-1000.0, 1000.0), 2)).replace('.', ',')])]
        else:
            if random.random() < 0.5:
                n: int = random.randint(-1000, 1000)
                return [random.choice([n, str(n), float(n)]), random.choice([n, str(n), float(n)])]
            else:
                n: float = round(random.uniform(-1000.0, 1000.0), 2)
                return [random.choice([n, str(n), str(n).replace('.', ',')]), random.choice([n, str(n), str(n).replace('.', ',')])]
    elif idx == 138:
        if random.random() < 0.95:
            return [random.randint(0, 10000)]
        else:
            return [random.randint(0, 7)]
    elif idx == 139:
        return [random.randint(0, 10)]
    elif idx == 140:
        return [''.join(random.choice([' ', random.choice(string.ascii_letters + string.digits), random.choice(string.ascii_letters + string.digits), random.choice(string.ascii_letters + string.digits)]) for _ in range(random.randint(0, 40)))]
    elif idx == 141:
        if random.random() < 0.5:
            all_chars: list[str] = [random.choice(string.ascii_letters + '.') for _ in range(random.randint(0, 26))] + [random.choice(string.digits) for _ in range(random.randint(0, 10))]
            random.shuffle(all_chars)
            return [''.join(all_chars) + random.choice(['.', '']) + random.choice(['jpeg', 'png', 'pdf', ''])]
        else:
            all_chars: list[str] = [random.choice(string.ascii_letters) for _ in range(random.randint(1, 20))] + [random.choice(string.digits) for _ in range(random.randint(0, 3))]
            random.shuffle(all_chars)
            return [random.choice(string.ascii_letters) + ''.join(all_chars) + '.' + random.choice(['txt', 'exe', 'dll'])]
    elif idx == 142:
        return [[random.randint(-1000, 1000) for _ in range(random.randint(0, 40))]]
    elif idx == 143:
        return [''.join(random.choice([' ', random.choice(string.ascii_letters), random.choice(string.ascii_letters), random.choice(string.ascii_letters), random.choice(string.ascii_letters)]) for _ in range(random.randint(1, 100)))]
    elif idx == 144:
        if random.random() < 0.6:
            return [f'{random.randint(1, 50)}/{random.randint(1, 10)}', f'{random.randint(1, 50)}/{random.randint(1, 10)}']
        else:
            n: int = random.randint(1, 30)
            m: int = random.randint(1, 30)
            if random.random() < 0.5:
                if random.random() < 0.5:
                    return [f'1/{n * m}', f'{n * m}/1'] if random.random() < 0.5 else [f'{n * m}/1', f'1/{n * m}']
                else:
                    return [f'{m}/{n}', f'{n}/{m}'] if random.random() < 0.5 else [f'{n}/{m}', f'{m}/{n}']
            else:
                if random.random() < 0.5:
                    return [f'1/{n}', f'{n * m}/{m}'] if random.random() < 0.5 else [f'{n * m}/{m}', f'1/{n}']
                else:
                    return [f'{m}/{n * m}', f'{n}/1'] if random.random() < 0.5 else [f'{n}/1', f'{m}/{n * m}']
    elif idx == 145:
        return [[random.randint(-1000, 1000) for _ in range(random.randint(0, 40))]]
    elif idx == 146:
        return [[random.randint(-100, 10000) if random.random() < 0.9 else random.randint(-100, 10) for _ in range(random.randint(0, 40))]]
    elif idx == 147:
        return [random.randint(0, 25)]
    elif idx == 148:
        return [random.choice(["Mercury", "Venus", "Earth", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune"]), random.choice(["Mercury", "Venus", "Earth", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune"])]
    elif idx == 149:
        return [[''.join(random.choice(string.ascii_letters) for _ in range(random.randint(0, 20))) for _ in range(random.randint(0, 40))]]
    elif idx == 150:
        if random.random() < 0.6:
            return [random.randint(1, 10000), random.randint(-10000, 10000), random.randint(-10000, 10000)]
        else:
            return [random.choice([2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71]), random.randint(-10000, 10000), random.randint(-10000, 10000)]
    elif idx == 151:
        return [[random.choice([random.randint(-100, 0), round(random.uniform(-100.0, 100.0), 2)]) if random.random() < 0.3 else random.randint(0, 1000) for _ in range(random.randint(0, 40))]]
    elif idx == 152:
        n: int = random.randint(0, 40)
        return [[random.randint(-100, 100) for _ in range(n)], [random.randint(-100, 100) for _ in range(n)]]
    elif idx == 153:
        return [''.join(random.choice(string.ascii_letters + '-_.' + string.digits) for _ in range(random.randint(1, 40))), [''.join(random.choice(string.ascii_letters + '-_.' + string.digits) for _ in range(random.randint(1, 30))) for _ in range(random.randint(1, 20))]]
    elif idx == 154:
        if random.random() < 0.55:
            return [''.join(random.choice(string.ascii_lowercase) for _ in range(random.randint(1, 20))), ''.join(random.choice(string.ascii_lowercase) for _ in range(random.randint(1, 10)))]
        else:
            s: list[str] = [random.choice(string.ascii_lowercase) for _ in range(random.randint(8, 20))]
            n: int = random.randint(1, len(s) - 4)
            ss: list[str] = s[n:min(len(s), n + random.randint(3, 6))]
            if random.random() < 0.7:
                return [''.join(s), ''.join(ss)]
            else:
                return random.choice([["abab", "baa"], ["himenss", "simen"], ["efef", "fee"], ["winemtt", "tinem"]])
    elif idx == 155:
        return [random.randint(-100000, 100000)]
    elif idx == 156:
        return [random.randint(1, 1000)]
    elif idx == 157:
        if random.random() < 0.85:
            if random.random() < 0.2:
                return [random.randint(1, 100), random.randint(1, 100), random.randint(1, 100)]
            else:
                a: int = random.randint(1, 100)
                b: int = random.randint(1, 100)
                c: float = math.sqrt(a * a + b * b)
                l = [a, b, c]
                random.shuffle(l)
                return l
        else:
            return random.choice([[3, 4, 5], [10, 6, 8], [7, 24, 25], [5, 12, 13], [15, 8, 17], [48, 55, 73]])
    elif idx == 158:
        return [[''.join(random.choice(string.ascii_lowercase) for _ in range(random.randint(1, 20))) for _ in range(random.randint(1, 40))]]
    elif idx == 159:
        return [random.randint(0, 1000), random.randint(0, 1000), random.randint(0, 1000)]
    elif idx == 160:
        if random.random() < 0.65:
            n: int = random.randint(2, 6)
            return [[random.choice(['+', '-', '*', '//']) for _ in range(n - 1)], [random.randint(1, 8) for _ in range(n)]]
        else:
            n: int = random.randint(2, 3)
            return [[random.choice(['+', '-', '**']) for _ in range(n - 1)], [random.randint(1, 5) for _ in range(n)]]
    elif idx == 161:
        if random.random() < 0.6:
            return [''.join(random.choice(string.ascii_letters + string.digits + '-_.!?#@ ^$') for _ in range(random.randint(0, 40)))]
        else:
            return [''.join(random.choice(string.digits + '-_.!?#@ ^$') for _ in range(random.randint(0, 40)))]
    elif idx == 162:
        return [''.join(random.choice(string.ascii_letters + string.digits + '-_.!?#@ ^$') for _ in range(random.randint(0, 40)))]
    elif idx == 163:
        if random.random() < 0.2:
            return [random.randint(0, 100), random.randint(0, 100)]
        else:
            if random.random() < 0.5:
                return [random.randint(0, 10), random.randint(0, 10)]
            else:
                return [random.randint(0, 100), random.randint(0, 10)] if random.random() < 0.5 else [random.randint(0, 10), random.randint(0, 100)]
    else:
        return None


# ======================================================================================
# GENERATE TEST CASES
# ======================================================================================


def generate_invals(seed: int, n_total_cases: int) -> dict[int, list[list[Any]]]:
    data: dict[int, list[list[Any]]] = {i: [] for i in range(164)}

    for key in sorted(list(data.keys())):
        random.seed(seed)
        for _ in range(n_total_cases):
            single_value = generate_single_input_case(key)
            if single_value is not None:
                data[key].append(single_value)

    return data


def generate_outvals(idx: int, is_train: bool, inval: list[list[Any]]) -> None:
    inval_str: str = 'inval=' + str(inval)
    with open('humaneval.json', 'r') as f:
        data = json.load(f)

    he = data[idx]
    correct_code: str = he['prompt'] + '\n\n' + he['canonical_solution'] + '\n\n'
    correct_code += he['test'] + '\n\n'
    correct_code += f'check({he["entry_point"]})' + '\n\n'

    correct_code = add_global_declarations_before_function_definitions(correct_code)
    correct_code += '\n'
    
    correct_code += inval_str + '\n\n'
    correct_code += 'global outv' + '\n\n'
    correct_code += 'outv = []' + '\n\n'
    
    correct_code += 'for i in inval:\n    outv.append([' + he['entry_point'] + '(*i)])\n\n'
    
    exec(correct_code)
    
    outval_str: str = 'outval=' + str(outv) # type: ignore

    # TYPE THE ID OF THE PROBLEM FROM WHICH YOU WISH TO CHECK WHETHER OUTPUT VALUES ARE BALANCED
    if idx == -1:
        print(Counter([str(oo) for oo in outv])) # type: ignore
        quit()

    with open('humaneval-bench/humaneval' + str(idx) + '/' + ('Train.txt' if is_train else 'Test.txt'), 'w') as f:
        f.write(inval_str + '\n' + outval_str)


def generate_all(seed: int, n_total_cases: int) -> None:
    data: dict[int, list[list[Any]]] = generate_invals(seed=seed, n_total_cases=n_total_cases)

    for key in sorted(list(data.keys())):
        all_vals = data[key]
        if len(all_vals) == 0:
            continue
        train_vals = all_vals[:n_total_cases // 2]
        test_vals = all_vals[n_total_cases // 2:]
        generate_outvals(key, True, train_vals)
        generate_outvals(key, False, test_vals)
        print(key)


if __name__ == '__main__':   
    generate_all(seed=42, n_total_cases=2000)
