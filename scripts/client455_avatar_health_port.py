"""Route the 455 event HP update to the local player's health owner."""


def port_avatar_health(raw, relative):
    if relative == 'character/avatar/cavatar.h':
        anchor = b'\t\t\tvoid\t\tSetHP( DWORD pi_dwMaxHP );'
        updated = anchor + b'\n\t\t\tvoid SetPlayerHP455(DWORD hp);'
    elif relative == 'character/avatar/cavatar_etc.cpp':
        anchor = b'void\nCAvatar::SetMaxFP('
        updated = b'''void CAvatar::SetPlayerHP455(DWORD hp)
{
    CCharacter::SetHP(hp);
    if (auto* gauge = _GetGaugeWindow())
        gauge->SetGauge(CGUIGaugeExpWindow::LIFE_BAR, GetMaxHP(), GetHP());
}

''' + anchor
    elif relative == 'network/netmsgprocessor/event/cnetmsgprocessor_event.cpp':
        raw = b'#include <cstring>\n#include "client455_protocol_observation.h"\n' + raw
        anchor = b'\t\tcase recover_zocl'
        updated = b'''        case 14: { // 455 11/14: current player HP.
            DWORD hp;
            if (!pi_pMsg || pMsgHeader->m_wSize != 4 + sizeof hp) return false;
            std::memcpy(&hp, pi_pMsg, sizeof hp);
            if (auto* avatar = _GetAvatar()) {
                avatar->SetPlayerHP455(hp);
                RF455_ObserveProtocol("avatar-health", hp, avatar->GetHP(), avatar->GetMaxHP());
            }
            return true;
        }

''' + anchor
    else:
        return raw, False
    if raw.count(anchor) != 1:
        raise ValueError(f'455 player health source anchor changed in {relative}')
    return raw.replace(anchor, updated), True
