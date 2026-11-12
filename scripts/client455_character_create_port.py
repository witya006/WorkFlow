"""Connect the 455 creation protocol to the existing client login flow."""

from client455_trade_ore_port import replace


def port_character_create(raw, relative, native, section):
    if relative == 'network/protocol/pt_zone_client.h':
        raw = replace(raw, b'#define add_char_request_zone 9', b'#define add_char_request_zone 10')
        raw = replace(raw, b'#define add_char_result_zone 10', b'#define add_char_result_zone 11')
    elif relative == 'network/cnetworkmgr_masterservermsg.cpp':
        first, _ = section(raw, b'\nDWORD\nSetEquipFlag(', b'SetEquipFlag(')
        _, last = section(raw, b'CNetworkMgr::SystemMsg_AddCharResult_zone(',
                          b'CNetworkMgr::SystemMsg_AddCharResult_zone(')
        raw = raw[:first] + b'\n#include "client455_character_create.inc"\n' + raw[last:]
    elif relative == 'network/cnetworkmgr.cpp':
        raw = replace(raw, b'\t\t\t\tcase add_char_result_zone :\n',
                      b'\t\t\t\tcase add_char_result_zone :\n'
                      b'\t\t\t\t\tif (!pi_pMsg || pMsgHeader->m_wSize < 4 + sizeof(_add_char_result_zone)) return false;\n')
    elif relative == 'userinterface/loginwindow/guiselectrace.cpp':
        # 455 RVA 0x3ac610 uses the localized labels and fits the 740x482 card
        # between the race buttons and the confirmation panel.
        raw = b'#include "client455_language.h"\n#include <algorithm>\n' + raw
        first = raw.index(b'\tm_cRaceSelectButton[0].SetLabel(')
        last = raw.index(b'\n', raw.index(b'\tm_cCancelButton.SetLabel(', first))
        raw = raw[:first] + b'''    const auto* language = RF455_GetNormalLanguagePack();
    m_cRaceSelectButton[0].SetLabel(const_cast<char*>(language->get(0x4c0)));
    m_cRaceSelectButton[1].SetLabel(const_cast<char*>(language->get(0x4c1)));
    m_cRaceSelectButton[2].SetLabel(const_cast<char*>(language->get(2)));
    m_cCreateButton.SetLabel(const_cast<char*>(language->get(0x4c2)));
    m_cCancelButton.SetLabel(const_cast<char*>(language->get(0x4c3)));''' + raw[last:]
        raw = replace(raw, b'\tm_cRaceProfile.SetSize( 486, 309 );\n', b'')
        first = raw.index(b'\tm_cRaceProfile.SetPos(')
        last = raw.index(b');', first) + 2
        raw = raw[:first] + raw[last:]
        anchor = b'\tm_cCancelButton.SetLabelPos( 110, 12 );'
        raw = replace(raw, anchor, anchor + b'''

    constexpr int nativeWidth = 740;
    constexpr int nativeHeight = 482;
    const auto& firstButton = m_cRaceSelectButton[0];
    const int available = m_cLowerBoard.m_ptPos.y - firstButton.m_ptPos.y - firstButton.m_ptSize.y - 70;
    const int height = (std::max)(1, (std::min)(available, nativeHeight));
    const int width = height * nativeWidth / nativeHeight;
    m_cRaceProfile.SetSize(width, height);
    m_cRaceProfile.SetPos((m_ptSize.x - width) / 2, (m_ptSize.y - height) / 2);''')
    elif relative == 'gameprogress/cgp_login.cpp':
        signature = b'void LoadAttribute(CGUISelectAttribute * attb)'
        first, last = section(raw, signature, signature)
        raw = raw[:first] + b'#include "client455_starter_attributes.inc"\n' + raw[last:]
        raw = replace(raw, b'if( ( race > 2 ) || ( attb > 4 ) )', b'if (race >= 3 || attb >= 4)')
        first, last = section(raw, b'void EventSelectBELLATORMale()', b'void EventSelectBELLATORMale()')
        end = raw.index(b'\n#define MAX_LOGIN_DEFAULT_ITEM_NUM', last)
        preview = raw[first:end].replace(b'PutOnEquipment( CEPT_HAIR,', b'PutOnEquipment( 10,')
        raw = raw[:first] + preview + raw[end:]
        for name in (b'EventLeftSelectFace', b'EventRightSelectFace', b'EventLeftSelectHead',
                     b'EventRightSelectHead', b'EventLeftSelectUpper', b'EventRightSelectUpper',
                     b'EventLeftSelectLower', b'EventRightSelectLower', b'EventLeftSelectGloves',
                     b'EventRightSelectGloves', b'EventLeftSelectShoes', b'EventRightSelectShoes'):
            signature = b'void ' + name + b'()'
            first, last = section(raw, signature, signature)
            body = raw[first:last].replace(b'CEPT_HAIR', b'10')
            start, end = body.index(b'GetEquipItem('), body.index(b' )->GetDTIndex()')
            part = body[start + len(b'GetEquipItem( '):end]
            body = body.replace(b'_GetAvatar()->GetEquipItem( ' + part + b' )->GetDTIndex()',
                                b'item->GetTableIndex455()')
            body = body.replace(b'{\n', b'{\n\tconst auto* item = _GetAvatar()->GetEquipItem455(' + part +
                                b');\n\tif (!item) return;\n', 1)
            raw = raw[:first] + body + raw[last:]
        begin = raw.index(b'\t\t\t\t_GetAvatarDummy(m_Course)->SetDefaultItem( CEPT_UPPER_PART')
        end = raw.index(b'\t\t\t\t_GetAvatarDummy(m_Course)->PutOffEquipment( IEPT_HELMET );', begin)
        raw = raw[:begin] + b'''                auto* preview = _GetAvatar();
                auto* character = _GetAvatarDummy(m_Course);
                character->SetSkipTutorial455(0);
                for (BYTE part : {BYTE(1), BYTE(2), BYTE(3), BYTE(4), BYTE(10), BYTE(0)}) {
                    auto* equipment = preview->GetEquipItem455(part);
                    if (!equipment) continue;
                    character->SetDefaultItem455(part == 10 ? BYTE(5) : part, equipment);
                    character->PutOnEquipment(part, equipment->GetTableIndex455());
                }
''' + raw[end:]
    else:
        return raw, False
    return raw, True
