"""Restore the measured MainGame Linker startup sequence, retaining other gaps."""


def port_board_startup(raw, relative, section, native):
    if relative == 'gameobject/board/common/clinkboard.h':
        anchor = b'\tCLinkBoard();'
        if raw.count(anchor) != 1:
            raise ValueError('Linker startup declaration boundary')
        return raw.replace(anchor, anchor + b'\r\n\tvoid InitializeMainGame455();'), True
    if relative == 'gameobject/board/common/clinkboard.cpp':
        return raw + b'\n' + (native / 'client455_linker_startup.inc').read_bytes(), True
    if relative != 'gameprogress/cgp_maingame.cpp':
        return raw, False
    first, last = section(raw, b'CGP_MainGame::Create_Board(', b'CGP_MainGame::Create_Board(')
    body = raw[first:last]
    start = body.index(b'\t// init link board')
    end = body.index(b'\t// init unit tuning board', start)
    old = body[start:end]
    if old.count(b'_GetBeltBoard()') != 4 or old.count(b'_GetLinkBoard()') != 4:
        raise ValueError('Legacy MainGame Linker/Belt startup boundary')
    # 455 goes straight from Linker Open(1) to UnitTuning. No separate Belt
    # owner occurs here. Later legacy consumers still raise their existing
    # explicit migration error; this is not a claim of a complete factory.
    body = body[:start] + (
        b'\t//455 RVA147832..1478CB: five ten-slot Linker banks, window3.\r\n'
        b'\t_GetLinkBoard()->InitializeMainGame455();\r\n\r\n'
    ) + body[end:]
    return raw[:first] + body + raw[last:], True
