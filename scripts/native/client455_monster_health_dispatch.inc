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
        if (size < 16 || data[0] != 0 || data[2] != CTI_MONSTER) return false;
        std::memcpy(&serial, data + 3, sizeof serial);
        std::memcpy(&fraction, data + 7, sizeof fraction);
    }

    auto* manager = _GetCharMgr();
    auto* monster = manager ? manager->GetMonster(serial) : nullptr;
    if (monster) monster->ReceiveHealth455(fraction);
    RF455_ObserveProtocol("monster-health", opcode, fraction, monster != nullptr);
    return true;
}
