"""Use the 455 crafting and upgrade windows in the ordinary item boards."""
import re


WINDOWS = 'userinterface/gamewindow/itemproc/'


def replace(raw, before, after):
    if raw.count(before) != 1:
        raise ValueError(f'Item work source anchor changed: {before!r}')
    return raw.replace(before, after)


def remove_methods(raw, section, owner, names, return_type=b'void'):
    for name in names:
        anchor = owner + b'::' + name + b'('
        start, end = section(raw, anchor, anchor)
        declaration = re.search(rb'\b' + re.escape(return_type) + rb'[ \t\r\n]*$', raw[:start])
        if declaration is None:
            raise ValueError(f'Item work declaration changed: {anchor!r}')
        raw = raw[:declaration.start()] + raw[end:]
    return raw


def crafting_header(raw):
    begin = raw.index(b'private :', raw.index(b'class CGUIItemListWindow'))
    end = raw.index(b'// < Member Function >', begin)
    raw = raw[:begin] + b'''private:
    BYTE m_group = 0xff, m_tab = 0xff, m_capacity = 0, m_selected = 0xff;
    CGUIObject m_uiTabBase;
    std::unique_ptr<CGUIObject[]> m_tabs;
    std::vector<std::unique_ptr<CGUIItem[]>> m_items;
    std::vector<BYTE> m_lastItem;
    CGUISocket m_uiSocket[TOTAL_ITEM_SOCKET_NUM];
    RF455GuiPageBoard m_pages;
    BOOL m_bIsCreated = FALSE;

    void UpdatePageCount();

''' + raw[end:]
    raw = replace(raw, b'#include <vector>',
                  b'#include "client455_briefing_controls.h"\n#include "client455_gui_page_board.h"\n'
                  b'#include <memory>\n#include <vector>')
    raw = replace(raw, b'CGUIObjectAni\t\tm_uiAniTitleBar;', b'RF455GuiAnimatedImage m_uiAniTitleBar;')
    raw = replace(raw, b'BOOL\t\t\t\tm_bIsCreated;', b'')
    return replace(raw, b'return &m_uiMakeItemList[pi_byMakeGroup];',
                   b'return pi_byMakeGroup < None ? &m_uiMakeItemList[pi_byMakeGroup] : nullptr;')


def crafting_source(raw, section, native):
    start = raw.index(b'CGUIItemListWindow::CGUIItemListWindow(')
    end = raw.index(b'CGUIItemMakeWindow::CGUIItemMakeWindow(', start)
    raw = raw[:start] + raw[end:]
    raw = replace(raw, b'WORD g_wTabNum[3] = { WEAPON_CLASS_NUM, ARMOR_CLASS_NUM, CONSUME_CLASS_NUM };', b'')
    raw = replace(raw, b'\tm_bIsCreated\t= FALSE;', b'')
    raw = remove_methods(raw, section, b'CGUIItemMakeWindow', (b'Init', b'SetSprite', b'SetMakeGroup', b'SetMaterialStr'))
    return raw + b'\n' + (native / 'client455_item_make.inc').read_bytes()


def upgrade_header(raw):
    for before, after in (
        (b'#include "../../GUIController/GUIMessageBox.h"',
         b'#include "../../GUIController/GUIMessageBox.h"\n#include "client455_briefing_controls.h"'),
        (b'CGUIObjectAni\t\tm_uiAniTitleBar;', b'RF455GuiAnimatedImage m_uiAniTitleBar;'),
        (b'CGUIObject\t\t\tm_uiEmptySocketMark[TOTAL_UPGRADE_SOCKET_NO];', b''),
        (b'BOOL\t\t\t\tm_bIsCreated;', b'CGUIButtonEx m_uiReturnButton455;'),
        (b'void\tSetEmptySocket( UpgradeSocket pi_eSocket, BOOL pi_bIsEmpty );', b'void UpdateReturnButton455();'),
        (b'void\tSetNonEmptySocket( UpgradeSocket pi_eSocket );', b''),
    ):
        raw = replace(raw, before, after)
    return raw


def upgrade_source(raw, section, native):
    owner = b'CGUIItemUpgradeWindow'
    raw = replace(raw, b'\tm_bIsCreated = FALSE;', b'')
    raw = remove_methods(raw, section, owner, (b'Init', b'SetSprite', b'SetEmptySocket', b'MouseEvent'))
    raw = remove_methods(raw, section, owner, (b'TakeInItem', b'TakeOutItem'), b'BOOL')
    raw = remove_methods(raw, section, owner, (b'GetItem',), b'CGUIItem *')
    return raw + b'\n' + (native / 'client455_item_upgrade.inc').read_bytes()


def port_item_work(raw, relative, section, native):
    if relative == WINDOWS + 'guiitemmakewindow.h':
        return crafting_header(raw), True
    if relative == WINDOWS + 'guiitemmakewindow.cpp':
        return crafting_source(raw, section, native), True
    if relative == WINDOWS + 'guiitemupgradewindow.h':
        return upgrade_header(raw), True
    if relative == WINDOWS + 'guiitemupgradewindow.cpp':
        return upgrade_source(raw, section, native), True
    if relative == 'definemessage.h':
        for name, old, new in ((b'WORK_BOARD_PROCESS', b'0160', b'0182'), (b'WORK_BOARD_CANCEL', b'0161', b'0183'),
                               (b'UPGRADE_BOARD_PROCESS', b'0170', b'0184'), (b'UPGRADE_BOARD_CANCEL', b'0171', b'3F09')):
            pattern = rb'(#define[ \t]+WM_ITEM_' + name + rb'[ \t]+\( WM_USER \+ 0x)' + old + rb'\b'
            raw, count = re.subn(pattern, lambda match: match[1] + new, raw)
            if count != 1:
                raise ValueError(f'Item work message changed: {name!r}')
        return raw, True
    if relative == 'gameobject/board/itemboard/citemworkboard.cpp':
        raw = replace(raw, b'if( !pi_pWorkTool )',
                      b'if (!pi_pWorkTool || pi_pWorkTool->GetDTIndex() >= WTT_NUM)')
        raw = replace(raw, b'm_clsItemListBoard[m_byWorkToolType].MsgProc( hWnd, uMsg, wParam, lParam );',
                      b'if (m_byWorkToolType < WTT_NUM)\n'
                      b'\t\t\t\tm_clsItemListBoard[m_byWorkToolType].MsgProc(hWnd, uMsg, wParam, lParam);')
        return raw, True
    if relative == 'gameobject/board/itemboard/citemupgradeboard.cpp':
        raw = replace(raw, b'case WM_CLOSE_WINDOW', b'case WM_ITEM_UPGRADE_BOARD_CANCEL:\n\tcase WM_CLOSE_WINDOW')
        raw = replace(raw, b'return CItemBoard::MsgProc( hWnd, uMsg, wParam, lParam );',
                      b'if (uMsg == WM_BOARD_CHECK_REMOVE_OBJECT) uMsg = WM_BOARD_REMOVE_OBJECT;\n'
                      b'\treturn CItemBoard::MsgProc(hWnd, uMsg, wParam, lParam);')
        return raw, True
    return raw, False
