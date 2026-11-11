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
