from itertools import takewhile

DOT = "."
OPEN_GENERIC = "["
CLOSE_GENERIC = "]"
COMMA_SPACE = ", "
DELIMETERS = {OPEN_GENERIC, CLOSE_GENERIC, COMMA_SPACE}
SENTINEL = "~~~TERMINATE~~~"


def _dedot(string: str) -> str:
    return COMMA_SPACE.join(part.split(DOT)[-1] for part in string.split(COMMA_SPACE))


def undot_type_str(type_str: str) -> str:
    it = iter(type_str)

    while True:
        char = next(it, SENTINEL)
        if char == SENTINEL:
            return ""
        elif char not in DELIMETERS:
            word = _dedot(char + "".join(takewhile(lambda x: x not in DELIMETERS, it)))
            rest = type_str.split(word, maxsplit=1)[-1]
            return f"{word}{undot_type_str(rest)}"
        elif char == OPEN_GENERIC:
            inner_word = "".join(takewhile(lambda x: x != CLOSE_GENERIC, it))
            rest = type_str.split(inner_word, maxsplit=1)[-1]
            # for Callable[] the first generic arg is a [], so we need to check for that
            special_case = OPEN_GENERIC if inner_word.startswith(OPEN_GENERIC) else ""
            return f"{char}{special_case}{_dedot(inner_word)}{undot_type_str(rest)}"
        elif char == CLOSE_GENERIC:
            rest = type_str.split(char, maxsplit=1)[-1]
            word = _dedot(char + "".join(takewhile(lambda x: x not in DELIMETERS, it)))
            return f"{char}{_dedot(rest)}"
