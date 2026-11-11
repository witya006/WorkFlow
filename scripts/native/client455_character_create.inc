namespace {
// Original 455 sends four armor variants, the starter head, then the face.
constexpr BYTE creationParts455[] = {1, 2, 3, 4, 10, 0};

DWORD CreationAppearance455(CAvatar& avatar)
{
    const DWORD raceStart = avatar.GetRace() * MAX_DEFAULT_ITEM_NUM;
    DWORD shape = 0;
    for (unsigned i = 0; i < sizeof(creationParts455); ++i) {
        const auto* part = avatar.GetEquipItem455(creationParts455[i]);
        if (!part) continue;
        const DWORD index = part->GetTableIndex455();
        if (index >= raceStart && index - raceStart < MAX_DEFAULT_ITEM_NUM)
            shape |= (index - raceStart) << (4 * i);
    }
    return shape;
}
}

BOOL CNetworkMgr::SystemMsg_AddCharRequest_zone(BYTE slot)
{
    auto* avatar = _GetAvatar();
    const char* name = avatar->GetName();
    const auto nameLength = std::strlen(name);
    if (slot > 2 || avatar->GetRace() > 4 || !nameLength || nameLength > max_name_len ||
        !_GetCharDataMgr()->GetClassData455(m_gClassTypeString).data)
        return FALSE;

    _add_char_request_zone request{};
    static_assert(sizeof(request) == 28 && offsetof(_add_char_request_zone, dwBaseShape) == 24,
                  "455 create character payload layout");
    request.bySlotIndex = slot;
    request.byRaceSexCode = avatar->GetRace();
    std::memcpy(request.szCharName, name, nameLength);
    std::memcpy(request.szClassCode, m_gClassTypeString, class_code_len);
    request.dwBaseShape = CreationAppearance455(*avatar);

    BYTE type[] = {system_msg, add_char_request_zone};
    if (!SendNetMessage(NST_GAME_SERVER, type, reinterpret_cast<char*>(&request), sizeof(request))) {
        NetLogWrite("455 create character request failed");
        return FALSE;
    }
    avatar->SetClassDTIndexByStrDTCode(0, request.szClassCode);
    SendRequestMsg();
    return TRUE;
}

void CNetworkMgr::SystemMsg_AddCharResult_zone(char* packet)
{
    _add_char_result_zone reply{};
    static_assert(sizeof(reply) == 2, "455 create character reply layout");
    std::memcpy(&reply, packet, sizeof(reply));
    m_byResultOfCharacterCreate = reply.byRetCode;
    if (reply.byRetCode == CHAR_CREATE_SUCCESS) {
        auto* avatar = _GetAvatar();
        avatar->SetMaxHP(70);
        avatar->SetHP(70);
        avatar->SetMaxFP(35);
        avatar->SetFP(35);
        avatar->SetMaxSP(120);
        avatar->SetSP(120);
        avatar->SetSkipTutorial455(0);
    }
    ReceiveResponseMsg();
    RF455_ObserveProtocol("create-result", reply.byRetCode, reply.byAddSlotIndex, 0);
}
