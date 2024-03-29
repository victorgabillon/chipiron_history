from typing import AnyStr


def convert_line(
        line: AnyStr,
        index: int
) -> str:
    if len(line) == 0:
        return ''

    count: int = 0
    while index + count < 8 and line[count] == '1':
        count = count + 1

    if count == 0:
        return str(line[0]) + convert_line(line[1:], index + 1)
    else:
        return str(count) + convert_line(line[count:], index + count)


def convert_to_fen(ascii_board: AnyStr) -> str:
    list_ascii_board: list[AnyStr] = ascii_board.splitlines()
    fen: str = ''
    list_ascii_board2: list[AnyStr] = list_ascii_board[:-1]
    line: AnyStr
    for line in list_ascii_board2:
        fen = fen + convert_line(line, 0) + '/'
    fen = fen[:-1]
    fen = fen + ' ' + str(list_ascii_board[-1])
    return fen
