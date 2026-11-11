BOOL CNetMsgProcessor_ItemArrangement::RequestMonsterTarget455(CCharacter& target)
{
    // 455 RVA 0x18bf00: object kind, type, zone index, and object serial.
    BYTE payload[8]{};
    payload[1] = CTI_MONSTER;
    const WORD zoneIndex = static_cast<WORD>(target.GetServerIndex());
    const DWORD serial = target.GetIndex();
    std::memcpy(payload + 2, &zoneIndex, sizeof zoneIndex);
    std::memcpy(payload + 4, &serial, sizeof serial);
    return SendNetMessage(26, payload, sizeof payload);
}

BOOL CNetMsgProcessor_ItemArrangement::CancelMonsterTarget455()
{
    BYTE payload = 0;
    return SendNetMessage(28, &payload, sizeof payload);
}

bool CNetMsgProcessor_ItemArrangement::MonsterHealth455(BYTE opcode, const char* bytes, std::size_t size)
{
    if (!bytes) return false;
    const auto* data = reinterpret_cast<const BYTE*>(bytes);
    DWORD serial;
    WORD fraction;
    if (opcode == 29) {
        if (size < 8 || data[1] != CTI_MONSTER) return false;
        std::memcpy(&serial, data + 2, sizeof serial);
        std::memcpy(&fraction, data + 6, sizeof fraction);
    } else {
        // The local server sends an 11-byte variant with the same HP prefix.
        if (size != 11 && size < 16) return false;
        if (data[0] != 0) {
            RF455_ObserveProtocol("target-info-rejected", data[0], 0, 0);
            return true;
        }
        if (data[2] != CTI_MONSTER) return false;
        std::memcpy(&serial, data + 3, sizeof serial);
        std::memcpy(&fraction, data + 7, sizeof fraction);
    }

    auto* manager = _GetCharMgr();
    auto* monster = manager ? manager->GetMonster(serial) : nullptr;
    if (monster) monster->ReceiveHealth455(fraction);
    RF455_ObserveProtocol("monster-health", opcode, fraction, monster != nullptr);
    RF455_ObserveProtocol("monster-health-target", serial, opcode, fraction);
    return true;
}
