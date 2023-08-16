def python_filter(txt):
    """ Create correct python syntax.

    We use {: and :} as special open and close brackets, because
    it's not possible to specify indentation correctly in a BNF
    grammar without this type of scheme."""

    indent_level = 0
    tmp = txt[:]
    i = 0
    while i < len(tmp):
        tok = tmp[i:i + 2]
        if tok == "{:":
            indent_level += 1
        elif tok == ":}":
            indent_level -= 1
        tabstr = "\n" + "  " * indent_level
        if tok == "{:" or tok == ":}":
            tmp = tmp.replace(tok, tabstr, 1)
        i += 1
    # Strip superfluous blank lines.
    txt = "\n".join([line for line in tmp.split("\n")
                     if line.strip() != ""])
    return txt
