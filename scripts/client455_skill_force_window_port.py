"""Move the ordinary skill and force panels onto the 455 tab-board owners."""
import re


UI_ROOT = 'userinterface/gamewindow/skillforce/'


def replace(raw, before, after):
    if raw.count(before) != 1:
        raise ValueError(f'Skill/Force source anchor changed: {before!r}')
    return raw.replace(before, after)


def remove(raw, section, name, return_type=None):
    start, end = section(raw, name, name)
    if return_type is not None:
        match = re.search(re.escape(return_type) + rb'\s*$', raw[:start])
        if match is None:
            raise ValueError(f'Skill/Force return declaration changed: {name!r}')
        start = match.start()
    return raw[:start] + raw[end:]


def skill_header(raw):
    row_begin = raw.index(b'\tCGUISFItem\t\t')
    row_end = raw.index(b'// < Member Function >', row_begin)
    raw = raw[:row_begin] + b'''\tCGUISFItem m_cItem;
\tCGUIObject m_cIconBackground455, m_cExpBase, m_cUnderline, m_cCover;
\tCGUIText m_cItemName, m_cLevelStr;
\tCGUIObjectEx m_cExp;
\tCGUIImageText455 m_cExpNumber;
\tBYTE m_kind455 = 0, m_level455 = 0;
\tfloat m_percent455 = 0;
\tvoid Arrange455();

''' + raw[row_end:]
    raw = replace(raw, b'\tCGUISkFcUnit();', b'\tCGUISkFcUnit();\n\tvoid SetKind455(BYTE);')
    raw = replace(raw, b'class CGUISkillForceBoard : public CGUIContainerEx,',
                  b'class CGUISkillForceBoard : public CGUITabBoard455')
    raw, count = re.subn(rb'\r?\n[ \t]+public IScrollObserver,\r?\n[ \t]+public IMouseObserver', b'', raw)
    if count != 1:
        raise ValueError('Skill/Force board inheritance changed')
    begin = re.search(rb'^[ \t]+CGUIContainer[ \t]+m_uiTabBase;', raw, re.M).start()
    end = raw.index(b'// < Member Function >', begin)
    raw = raw[:begin] + b'\tCGUISkFcUnit* m_pHoveredUnit;\n\n' + raw[end:]
    board_start = raw.index(b'class CGUISkillForceBoard :')
    board_end = raw.index(b'\n};', board_start)
    board = raw[board_start:board_end]
    for obsolete in (b'SetBound', b'IsOpenedTab', b'SetTab', b'RemoveAllUnit', b'GetList',
                     b'UpdateBoard', b'ScrollEvent', b'MouseEvent'):
        board, count = re.subn(rb'^[^\r\n]*\b' + obsolete + rb'\([^\r\n]*\r?(?:\n|\Z)', b'', board, flags=re.M)
        if count != 1:
            raise ValueError(f'Skill/Force board obsolete declaration changed: {obsolete!r}')
    board = replace(board, b'RemoveUnit( WORD wIndex )', b'RemoveUnit( DWORD index )')
    raw = raw[:board_start] + board + raw[board_end:]
    for pattern, replacement in (
        (rb'CGUIButton[ \t]+\*[ \t]+m_uiSFBoardTab;', b'CGUIObject* m_uiSFBoardTab;'),
        (rb'CGUIObjectAni[ \t]+m_uiAniTitleBar;', b'RF455GuiAnimatedImage m_uiAniTitleBar;'),
        (rb'^[ \t]+BOOL[ \t]+m_bIsCreated;[^\r\n]*\r?\n', b''),
    ):
        raw, count = re.subn(pattern, replacement, raw, flags=re.M)
        if count != 1:
            raise ValueError(f'Skill/Force control declaration changed: {pattern!r}')
    start = re.search(rb'^[ \t]+CGUIObject[ \t]+m_uiBoard;', raw, re.M).start()
    end = re.search(rb'^[ \t]+CGUIObject[ \t]+m_uiResizeUnderBar;', raw, re.M).start()
    raw = raw[:start] + b'\tRF455GuiOutlineBoard m_uiBoard;\n\tRF455GuiAnimatedImage m_uiSelectedTab455;\n' + raw[end:]
    return (b'#include "client455_briefing_window.h"\n#include "client455_gui_tab_board.h"\n'
            b'#include "client455_image_text.h"\n' + raw)


def skill_source(raw, section, native):
    methods = {
        b'CGUISkFcUnit::': [(b'CGUISkFcUnit', None), (b'SetSprite', b'void'), (b'SetSize', b'void'),
            (b'SetUnitState', b'void'), (b'SetItemName', b'void'), (b'SetLevel', b'void'),
            (b'SetExp', b'void'), (b'SetItem( CGUIItem', b'void'), (b'SetItem( DWORD', b'void')],
        b'CGUISkillForceBoard::': [(b'CGUISkillForceBoard', None), (b'~CGUISkillForceBoard', None),
            (b'Init', b'void'), (b'SetSprite', b'void'), (b'SetBound', b'void'), (b'IsOpenedTab', b'BOOL'),
            (b'SetTab', b'void'), (b'SetTabName', b'void'), (b'AddUnit', b'BOOL'),
            (b'RemoveUnit', b'CGUISkFcUnit *'), (b'RemoveAllUnit', b'void'), (b'UpdateBoard', b'void'),
            (b'ScrollEvent', b'void'), (b'MouseEvent', b'void')],
        b'CGUISFWindow::': [(b'~CGUISFWindow', None), (b'CreateSFBoard', b'void'), (b'Init', b'void'),
            (b'SetSprite', b'void'), (b'SetBound', b'void'), (b'SetCurBoardTab', b'void')],
        b'CGUISkillWindow::': [(b'Init', b'void'), (b'SetSprite', b'void')],
    }
    for owner, members in methods.items():
        for name, return_type in members:
            signature = name if b'(' in name else name + b'('
            raw = remove(raw, section, owner + signature, return_type)
    raw = replace(raw, b'\tm_bIsCreated\t= FALSE;', b'')
    raw = replace(raw, b'm_uiTabName[pi_byStep].SetString( l_pBuf );', b'SetTabName(pi_byStep, l_pBuf);')
    start, end = section(raw, b'CGUISFWindow::TakeInItem(', b'CGUISFWindow::TakeInItem(')
    body = raw[start:end]
    body = replace(body, b'if( pi_bySFBoardIndex >= m_bySFBoardNum )',
                   b'if( pi_bySFBoardIndex >= m_bySFBoardNum || !pi_pSFInfo )')
    body = replace(body, b'CGUISkFcUnit\t* l_pSFUnit;', b'std::unique_ptr<CGUISkFcUnit> l_pSFUnit;')
    body = replace(body, b'l_pSFUnit = new CGUISkFcUnit;',
                   b'l_pSFUnit.reset(new CGUISkFcUnit);\n\tl_pSFUnit->SetKind455(pi_pSFInfo->bySFType);')
    icon_begin = body.index(b'\tif( pi_pSFInfo->bySFType == 0 )')
    icon_end = body.index(b'\tl_pSFUnit->SetItemName', icon_begin)
    body = body[:icon_begin] + (
        b'\tconst BYTE iconTypes[] = {1, 3, 2, 2};\n'
        b'\tconst BYTE kind = pi_pSFInfo->bySFType;\n'
        b'\tl_pSFUnit->SetItem(pi_pSFInfo->dwItemID, pi_pSFInfo->dwSpriteID, kind < 4 ? iconTypes[kind] : 0);\n\n'
    ) + body[icon_end:]
    owner_begin = body.index(b'\tif( m_pSFBoardList[pi_bySFBoardIndex].AddUnit(')
    body = body[:owner_begin] + (
        b'\tif (!m_pSFBoardList[pi_bySFBoardIndex].AddUnit(l_pSFUnit.get())) return FALSE;\n'
        b'\tl_pSFUnit.release();\n\treturn TRUE;\n}'
    )
    raw = raw[:start] + body + raw[end:]
    return (b'#include <memory>\n' + raw + b'\n' + (native / 'client455_skill_force_window.inc').read_bytes() +
            b'\n' + (native / 'client455_skill_force_row.inc').read_bytes())


def port_skill_force_window(raw, relative, section, native):
    if relative == UI_ROOT + 'guiskillwindow.h':
        return skill_header(raw), True
    if relative == UI_ROOT + 'guiskillwindow.cpp':
        return skill_source(raw, section, native), True
    if relative == UI_ROOT + 'guiforcewindow.cpp':
        for name in (b'Init', b'SetSprite', b'SetRaceType'):
            raw = remove(raw, section, b'CGUIForceWindow::' + name + b'(', b'void')
        return raw + b'\n' + (native / 'client455_force_window.inc').read_bytes(), True
    if relative == 'define.h':
        for name, old, new in ((b'UII_GAUGE_WINDOW', 5, 4), (b'UII_SKILL_WINDOW', 6, 5), (b'UII_FORCE_WINDOW', 7, 6)):
            pattern = rb'(#define[ \t]+' + name + rb'[ \t]+)' + str(old).encode() + rb'\b'
            raw, count = re.subn(pattern, lambda match: match[1] + str(new).encode(), raw)
            if count != 1:
                raise ValueError(f'Skill/Force window ID changed: {name!r}')
        raw, count = re.subn(rb'^#define[ \t]+UII_SF_BELT_WINDOW[ \t]+4\r?\n', b'', raw, flags=re.M)
        if count != 1:
            raise ValueError('Unused legacy window ID changed')
        return raw, True
    if relative == 'gameprogress/cgp_maingame.cpp':
        start, end = section(raw, b'CGP_MainGame::Create_Board(', b'CGP_MainGame::Create_Board(')
        body = raw[start:end]
        first = body.index(b'\t// init skill board')
        last = body.index(b'\t// init animus board', first)
        if body[first:last].count(b'_GetSkillBoard()') != 3 or body[first:last].count(b'_GetForceBoard()') != 3:
            raise ValueError('Skill/Force board startup boundary changed')
        body = body[:first] + (
            b'\t// Skill/Force board startup at RVA 147A3F..147B15\n'
            b'\t_GetSkillBoard()->Create(IBT_SKILL, 7, 20);\n'
            b'\t_GetSkillBoard()->InitWindow(UII_SKILL_WINDOW, 200, 60);\n'
            b'\t_GetSkillBoard()->CreateBoardObject(7, 12, 100);\n\n'
            b'\t_GetForceBoard()->Create(IBT_FORCE, 6, 20);\n'
            b'\t_GetForceBoard()->InitWindow(UII_FORCE_WINDOW, 300, 60);\n'
            b'\t_GetForceBoard()->CreateBoardObject(6, 24, 100);\n\n'
        ) + body[last:]
        return raw[:start] + body + raw[end:], True
    return raw, False
