"""Restore the unit tuning and storehouse views in the ordinary client."""
import re


def replace_once(raw, before, after):
    if raw.count(before) != 1:
        raise ValueError(f'Unit window source anchor changed: {before!r}')
    return raw.replace(before, after)


def remove_method(raw, section, signature, return_type=b'void'):
    start, end = section(raw, signature, signature)
    declaration = raw.rfind(return_type, 0, start)
    if raw[declaration:start].strip() != return_type:
        raise ValueError(f'Unit window method boundary changed: {signature!r}')
    return raw[:declaration] + raw[end:]


def port_unit_windows(raw, relative, section, native):
    root = 'userinterface/gamewindow/unit/'
    tuning = root + 'guiunittuningwindow'
    store = root + 'guiunitstorewindow'
    if relative == tuning + '.h':
        raw = replace_once(raw, b'CGUIObjectAni\t\tm_uiAniTitleBar;',
                           b'RF455GuiAnimatedImage\tm_uiAniTitleBar;')
        raw = replace_once(raw, b'\tBOOL\t\t\t\tm_bIsCreated;', b'')
        return b'#include "client455_briefing_controls.h"\n' + raw, True
    if relative == store + '.h':
        raw = replace_once(raw, b'CGUIObject\t\t\tm_uiTitleBoard;',
                           b'RF455GuiOutlineBoard m_uiFrame455;\n\tRF455GuiAnimatedImage m_uiTitleBoard;')
        raw = replace_once(raw, b'\tBOOL\t\t\t\tm_bIsCreated;', b'')
        raw = replace_once(raw, b'\tBOOL\tDraw( void );', b'')
        return b'#include "client455_briefing_window.h"\n' + raw, True
    if relative in (tuning + '.cpp', store + '.cpp'):
        is_tuning = relative == tuning + '.cpp'
        owner = b'CGUIUnitTuningWindow::' if is_tuning else b'CGUIUnitStoreWindow::'
        methods = [b'Init', b'SetSprite']
        if is_tuning:
            methods += [b'Select_Parts', b'Select_Bullet', b'SetPartsBuyingState',
                        b'SetBulletBuyingState', b'SetBackpackBulletBuyingState',
                        b'Enable_Shouler_Bullet', b'Enable_BackPack_Bullet']
        for method in methods:
            raw = remove_method(raw, section, owner + method + b'(')
        raw, count = re.subn(rb'^\s*m_bIsCreated\s*= FALSE;\r?\n', b'\n', raw, flags=re.M)
        if count != 1:
            raise ValueError('Unit window constructor boundary changed')
        if is_tuning:
            remove_message = b'PostUIMessage( WM_BOARD_REMOVE_OBJECT,'
            if raw.count(remove_message) != 3:
                raise ValueError('Unit tuning remove message sites changed')
            raw = raw.replace(remove_message, b'PostUIMessage( WM_BOARD_CHECK_REMOVE_OBJECT,')
            raw, count = re.subn(rb'm_uiBackPackBulletTitle\.SetString\([^\r\n]+\);',
                                 b'm_uiBackPackBulletTitle.SetString(RF455UnitView::Text(0x41a));', raw)
            if count != 1:
                raise ValueError('Unit backpack label boundary changed')
            raw, count = re.subn(rb'static char PARTS_TAB_STR[^\r\n]+\r?\n[^\r\n]+SetString[^\r\n]+',
                                 b'static constexpr unsigned categoryLabels[] = {1051, 1052, 1053, 1054, 1055, 1050};\n'
                                 b'\t\tm_uiActiveTabName.SetString(RF455UnitView::Text(categoryLabels[m_byCurBuyTabIndex]));', raw)
            if count != 1:
                raise ValueError('Unit category label boundary changed')
            filename = 'client455_unit_tuning.inc'
        else:
            raw = remove_method(raw, section, owner + b'Draw(', b'BOOL')
            filename = 'client455_unit_storehouse.inc'
        return b'#include "client455_unit_view_skin.h"\n' + raw + b'\n' + (native / filename).read_bytes(), True
    if relative == 'gameobject/board/shopboard/cunittuningboard.cpp':
        start, end = section(raw, b'CUnitTuningBoard::MsgProc(', b'CUnitTuningBoard::MsgProc(')
        body = replace_once(raw[start:end], b'case WM_BOARD_REMOVE_OBJECT', b'case WM_BOARD_CHECK_REMOVE_OBJECT')
        return raw[:start] + body + raw[end:], True
    if relative == 'define.h':
        # Consecutive board windows in MainGame RVA 147915..147BA2.
        ids = ((b'UII_ANIMUS_WINDOW', 33, 32), (b'UII_ANIMUS_CONTROL_WINDOW', 34, 33),
               (b'UII_UNIT_TUNING_WINDOW', 35, 34), (b'UII_UNIT_STOREHOUSE_WINDOW', 36, 35))
        for name, old, new in ids:
            pattern = rb'(#define[ \t]+' + name + rb'[ \t]+)' + str(old).encode() + rb'\b'
            raw, count = re.subn(pattern, lambda match: match[1] + str(new).encode(), raw)
            if count != 1:
                raise ValueError(f'Unit board window ID changed: {name!r}')
        return raw, True
    if relative == 'definemessage.h':
        for name, old, new in [(b'REPAIR', 0x140, 0x135), (b'TUNING', 0x141, 0x136),
                               (b'CANCEL', 0x142, 0x137), (b'MAINFRAME', 0x143, 0x138)]:
            pattern = rb'(#define[ \t]+WM_TUNING_BOARD_' + name + rb'[ \t]+\( WM_USER \+ )' + f'0x{old:04X}'.encode()
            raw, count = re.subn(pattern, lambda match: match[1] + f'0x{new:04X}'.encode(), raw)
            if count != 1:
                raise ValueError(f'Unit command ID changed: {name!r}')
        return raw, True
    if relative == 'gameprogress/cgp_maingame.cpp':
        start, end = section(raw, b'CGP_MainGame::Create_Board(', b'CGP_MainGame::Create_Board(')
        body = raw[start:end]
        first = body.index(b'\t// init unit tuning board')
        last = body.index(b'\t// init equip board', first)
        if body[first:last].count(b'_GetUnitTuningBoard()') != 3 or body[first:last].count(b'_GetUnitStorehouseBoard()') != 3:
            raise ValueError('Unit board startup boundary changed')
        body = body[:first] + (
            b'\t// init unit tuning board: RVA 1478D4..14794D\n'
            b'\t_GetUnitTuningBoard()->Create(IBT_UNIT_TUNING, 8, 200);\n'
            b'\t_GetUnitTuningBoard()->InitWindow(UII_UNIT_TUNING_WINDOW, 300, 0);\n'
            b'\tfor (BYTE pack = 0; pack < 8; ++pack)\n'
            b'\t\t_GetUnitTuningBoard()->AddPack(pack);\n\n'
            b'\t// init unit storehouse board: RVA 147958..1479B4\n'
            b'\t_GetUnitStorehouseBoard()->Create(IBT_UNIT_STOREHOUSE, 1, 4);\n'
            b'\t_GetUnitStorehouseBoard()->AddPack(0);\n'
            b'\t_GetUnitStorehouseBoard()->InitWindow(UII_UNIT_STOREHOUSE_WINDOW, 300, 100);\n\n'
        ) + body[last:]
        return raw[:start] + body + raw[end:], True
    return raw, False
