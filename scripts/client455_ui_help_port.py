"""Route the live help owners through the localized 455 UIHelp reader."""


def port_ui_help(raw, relative, section, native):
    if relative == 'userinterface/gamewindow/etcwin/guihelpwindow.cpp':
        edits = (
            (b'm_pHelpInfoList[i].m_dwSectionID != m_pHelpInfoList[i+1].m_dwSectionID',
             b'pi_pHelpInfoList[i].m_dwSectionID != pi_pHelpInfoList[i+1].m_dwSectionID'),
            (b'if( m_pHelpInfoList[i].m_byTotalStrNum > 0 )',
             b'if( pi_pHelpInfoList[i].m_byTotalStrNum > 0 )'),
            (b"if( pi_pHelpInfoList[i].m_pStringInfoList[l_byLastStrIndex].m_pString[pi_pHelpInfoList[i].m_pStringInfoList[l_byLastStrIndex].m_wStrLen-1] != '\\n' )",
             b"const auto& last = pi_pHelpInfoList[i].m_pStringInfoList[l_byLastStrIndex];\n"
             b"                if (!last.m_wStrLen || last.m_pString[last.m_wStrLen - 1] != '\\n')"),
            (b'm_pHelpInfoList[i].m_byTotalStrNum\t= pi_pHelpInfoList[i].m_byTotalStrNum + l_byNewLineNum;',
             b'const unsigned room = 255u - pi_pHelpInfoList[i].m_byTotalStrNum;\n'
             b'        if (l_byNewLineNum > room) l_byNewLineNum = static_cast<BYTE>(room);\n'
             b'        m_pHelpInfoList[i].m_byTotalStrNum = pi_pHelpInfoList[i].m_byTotalStrNum + l_byNewLineNum;'),
        )
        for old, new in edits:
            if raw.count(old) != 1:
                raise ValueError('UIHelp string copy changed: ' + repr(old))
            raw = raw.replace(old, new)
        return raw, True

    if relative == 'gameobject/board/general/chelpboard.h':
        anchor = b'typedef vector< HSD_HELP * >'
        declaration = b'#define MAX_HELP_TYPE_NUM\t( MAX_UI + 1 )'
        helper = b'\tBOOL\t\tLoadData_HSDString( HSD_BASE_DATA * pio_pHSDData, CDataString * pi_pSourceData );'
        if raw.count(anchor) != 2:
            raise ValueError('Help list and iterator declarations changed')
        for marker in (declaration, helper):
            if raw.count(marker) != 1:
                raise ValueError('Help board declaration changed: ' + repr(marker))
        raw = raw.replace(anchor, b'typedef vector< std::unique_ptr<HSD_HELP> >')
        raw = raw.replace(declaration, b'#define MAX_HELP_TYPE_NUM RF455_UI_HELP_GROUPS')
        raw = raw.replace(helper, b'')
        return b'#include "client455_ui_help.h"\n#include <memory>\n' + raw, True

    if relative == 'gameobject/board/general/chelpboard.cpp':
        def replace(name, code):
            nonlocal raw
            signature = b'CHelpBoard::' + name
            start, end = section(raw, signature, signature)
            raw = raw[:start] + signature + b'\n' + code + raw[end:]

        replace(b'~CHelpBoard()', b'= default;')
        replace(b'LoadData_Help( void )', b'''{
    try {
        RF455UiHelpGroups groups;
        if (!RF455_LoadUiHelp(uiHelpPath455().c_str(), groups)) return FALSE;
        CHelpList next[MAX_HELP_TYPE_NUM];
        for (unsigned i = 0; i < groups.size(); ++i) {
            next[i].reserve(groups[i].size());
            for (const auto& page : groups[i]) {
                auto record = std::make_unique<HSD_HELP>();
                assignUiHelp455(*record, page);
                next[i].push_back(std::move(record));
            }
        }
        for (unsigned i = 0; i < groups.size(); ++i) m_listHelp[i].swap(next[i]);
        m_dwPrevOpendWindowID = ID_INVALID;
        return TRUE;
    } catch (const std::bad_alloc&) {
        return FALSE;
    } catch (const std::length_error&) {
        return FALSE;
    }
}''')
        signature = b'CHelpBoard::LoadData_HSDString('
        start, end = section(raw, signature, signature)
        before = raw.rfind(b'BOOL', 0, start)
        if raw[before:start].strip() != b'BOOL':
            raise ValueError('Help fragment reader return type changed')
        raw = raw[:before] + raw[end:]
        signature = b'CHelpBoard::OpenHelpWindow( DWORD pi_dwWindowID )'
        start, end = section(raw, signature, signature)
        body = raw[start:end]
        brace = body.index(b'{') + 1
        body = body[:brace] + b'\n    if (pi_dwWindowID >= MAX_HELP_TYPE_NUM || m_listHelp[pi_dwWindowID].size() > 255) return;\n' + body[brace:]
        window = b'( *iter )->m_dwWindowID;'
        if body.count(window) != 1:
            raise ValueError('UIHelp window section boundary changed')
        body = body.replace(window, window + b'\n        l_listHelp[i].m_dwSectionID = (*iter)->m_dwSectionID;')
        raw = raw[:start] + body + raw[end:]
    elif relative == 'datafile.cpp':
        signature = b'CUIHelpMgr::LoadData( void )'
        start, end = section(raw, signature, signature)
        raw = raw[:start] + signature + b'''
{
    try {
        std::vector<RF455UiHelpPage> pages;
        if (!RF455_LoadUiHelp(uiHelpPath455().c_str(), pages)) return FALSE;
        auto next = std::make_unique<HSD_HELP[]>(pages.size());
        for (std::size_t i = 0; i < pages.size(); ++i) assignUiHelp455(next[i], pages[i]);
        delete[] m_listUIHelp;
        m_listUIHelp = next.release();
        m_dwTotalHelpNum = static_cast<DWORD>(pages.size());
        return TRUE;
    } catch (const std::bad_alloc&) {
        return FALSE;
    } catch (const std::length_error&) {
        return FALSE;
    }
}''' + raw[end:]
    else:
        return raw, False

    include = b'#include "CHelpBoard.h"' if relative.endswith('chelpboard.cpp') else b'#include "DataFile.h"'
    if raw.count(include) != 1:
        raise ValueError('UIHelp owner include changed: ' + repr(include))
    return raw.replace(include, include + b'\n' + (native / 'client455_ui_help_owner.inc').read_bytes()), True
