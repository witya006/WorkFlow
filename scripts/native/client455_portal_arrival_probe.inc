void arrivalError(char* message)
{
    std::fprintf(stderr, "engine error: %s\n", message);
    std::exit(2);
}

void arrivalWarning(char* message)
{
    std::fprintf(stderr, "engine warning: %s\n", message);
}

int runPortalArrival(bool assigned)
{
    InitR3Engine();
    SetErrorMessageProc(arrivalError);
    SetWarningMessageProc(arrivalWarning);
    g_pMainApp = &g_MainApp;
    g_MainApp.SetGameProgressID(GPI_TITLE);
    auto* state = GetR3State();
    state->mScreenXsize = 640;
    state->mScreenYsize = 480;
    state->mbFullScreen = FALSE;
    std::strcpy(state->MapPath, ".\\Map\\");
    std::strcpy(state->EntityPath, ".\\Map\\Entity\\");
    std::strcpy(state->EffectPath, ".\\Effect\\");
    ForceFullScreen();
    require(SUCCEEDED(g_MainApp.InitR3D3D(GetModuleHandleA(nullptr), 0)), "arrival graphics device");
    require(RF455_InitializeNationPaths(), "arrival nation paths");
    g_pUiScreen = &gScreen;
    ChInterface renderer;
    g_ifCharIF = &renderer;
    require(_CreateAnimationMgr(), "arrival animation owner");
    float firstStepDistance = 0;
    {
        const auto networkOwner = std::make_unique<Network>();
        auto& network = *networkOwner;
        g_pNetworkMgr = &network;
        auto& processors = network.*access(Processors{});
        processors[NMP_MAP] = new CNetMsgProcessor_Map;
        processors[NMP_ITEM_TRADE] = new CNetMsgProcessor_ItemTrade;
        SendRing ring(network);
        ring.SetConnected(true);
        CCamera camera;
        g_pCamera = &camera;
        CCharacterMgr characters;
        g_pCharacterMgr = &characters;
        characters.CreateAvatar();
        auto& avatar = *characters.GetAvatar();
        avatar.CreateBoard();
        avatar.CCharacter::SetAction(CAI_MOVE_STOP);
        avatar.Enable(ROSF_MOVABLE);
        avatar.SetSpeed(90.0f);
        avatar.SetIndex(1234);
        CNextActionMgr nextAction;
        g_pNextActionMgr = &nextAction;
        CPartyBoard partyBoard;
        g_pPartyBoard = &partyBoard;
        struct ReleaseParty {
            ~ReleaseParty() { g_pPartyBoard = nullptr; }
        } releaseParty;
        CGUIMapLoadingWindow loading;
        const auto radar = std::make_unique<CGUIRadarWindow>();
        const auto minimap = std::make_unique<CGUIMiniMapWindow>();
        g_pUiMapLoadingWindow = &loading;
        g_pUiRadarWindow = radar.get();
        g_pUiMinimapWindow = minimap.get();
        loading.Show(FALSE);

        CLand land;
        require(land.Create() && land.LoadData(), "arrival map catalog");
        land.SetMapIndex(0);
        land.SetPortalIndex(3);
        auto* gate = land.GetPortalInfo(0, 2);
        auto* exit = land.GetPortalInfo(2, 13);
        require(gate && exit && gate->byLinkedPortal[0][0] == 2 && gate->byLinkedPortal[0][1] == 13,
                "actual NeutralB to Resources link");
        require(land.LoadLevel(land.GetMapInfo(0)->pFileName), "load initial NeutralB terrain");
        const auto midpoint = [](const PORTAL_INFO& portal, unsigned axis) {
            return (portal.vecMin[axis] + portal.vecMax[axis]) * 0.5f;
        };
        Vector3f oldPosition{midpoint(*gate, 0), midpoint(*gate, 1), midpoint(*gate, 2)};
        avatar.SetPosition(oldPosition, TRUE, FALSE);
        auto& move = *avatar.GetMoveMapInfo();
        const auto deliverPortal = [&](BYTE map, const Vector3f& position, BYTE zone, WORD size = 15) {
            std::array<char, 15> result{};
            result[1] = map;
            std::memcpy(result.data() + 2, position, sizeof position);
            result[14] = zone;
            _MSG_HEADER header{WORD(4 + size), {8, 2}};
            return network.AnalysisServerPacket(&header, result.data());
        };
        if (assigned) {
            require(move.MoveToPortal_Request(0), "start a local portal request before server reassignment");
            ring.ExpectRequest({11, 0, 8, 1, 0, 255, 255, 255, 255, 255, 255});
            Vector3f sameMapPosition{oldPosition[0] - 1.25f, oldPosition[1], oldPosition[2] + 2.5f};
            require(!deliverPortal(0, sameMapPosition, 2, 14) && _GetGBM()->IsRequestProcess(),
                    "truncated result preserves the pending request");
            require(deliverPortal(0, sameMapPosition, 2) && !_GetGBM()->IsRequestProcess() &&
                    move.m_byMoveType == GST_BASE_PORTAL && move.m_bIsMoved &&
                    !move.m_pEnterPortalInfo && !move.m_pExitPortalInfo &&
                    deliverPortal(0, oldPosition, 0) && move.m_vecPosition[0] == sameMapPosition[0] &&
                    move.m_vecPosition[2] == sameMapPosition[2],
                    "server destination supersedes the local request and its late result");
            move.m_dwMoveStepStartTime = timeGetTime() - 701;
            move.FrameMove();
            require(move.m_byMoveStep == MOVEMAP_INFO::MMS_LOAD_DATA && !loading.IsShow() && ring.Empty(),
                    "same-map reassignment skips the loading window");
            move.Init();
            avatar.Enable(ROSF_MOVABLE);
        }
        Vector3f oldTarget{oldPosition[0] + 24, oldPosition[1], oldPosition[2]};
        require(network.SendAvatarMove455(oldTarget), "leave an old-map movement awaiting its reply");
        auto packet = ring.ReadRequest();
        require(packet.size() == 30 && packet[2] == 4 && packet[3] == 1, "old-map movement wire");

        if (!assigned) {
            require(move.MoveToPortal_Request(2), "ordinary cross-map portal input");
            ring.ExpectRequest({11, 0, 8, 1, 2, 255, 255, 255, 255, 255, 255});
        }
        const BYTE arrivalMode = assigned ? GST_BASE_PORTAL : GST_PORTAL;
        const BYTE destinationPortal = assigned ? 0xff : 13;
        Vector3f destination{midpoint(*exit, 0), midpoint(*exit, 1), midpoint(*exit, 2)};
        require(deliverPortal(2, destination, assigned ? 2 : 0), "cross-map result");
        require(move.m_byMoveStep == MOVEMAP_INFO::MMS_PREV_LOAD_DATA && move.m_byMoveType == arrivalMode &&
                land.GetMapIndex() == 0 && land.GetPortalIndex() == 3 && avatar.IsDisable(ROSF_MOVABLE) &&
                !network.PositionMsg_MoveRequest_clzo(oldTarget, FALSE) && ring.Empty(),
                "map result starts transition without changing the current map or sending another request");
        RF455StopResult lateStop{avatar.GetIndex(), {-5800, 575, 5650}};
        _MSG_HEADER stopHeader{WORD(4 + sizeof lateStop), {4, 20}};
        require(network.AnalysisServerPacket(&stopHeader, reinterpret_cast<char*>(&lateStop)) &&
                nextAction.IsEmpty(), "old stop result cannot queue a return to NeutralB");

        std::fputs("load Resources\n", stderr);
        move.m_dwMoveStepStartTime = timeGetTime() - 900;
        move.FrameMove();
        require(!loading.IsShow() && move.m_byMoveStep == MOVEMAP_INFO::MMS_PREV_LOAD_DATA,
                "cross-map overlay waits for the transition delay");
        move.m_dwMoveStepStartTime = timeGetTime() - 1301;
        move.FrameMove();
        require(loading.IsShow() && move.m_byMoveStep == MOVEMAP_INFO::MMS_LOAD_DATA, "open cross-map overlay");
        move.FrameMove();
        require(!loading.IsShow() && move.m_byMoveStep == MOVEMAP_INFO::MMS_AFTER_LOAD_DATA &&
                land.GetMapIndex() == 2 && land.GetPortalIndex() == destinationPortal &&
                land.GetLevel()->IsLoadedBsp() && !_stricmp(land.GetLevel()->GetMapName(), "Resources") &&
                avatar.GetPosX() == destination[0] && avatar.GetPosZ() == destination[2],
                "loaded terrain and authoritative destination publish together");
        ring.ExpectRequest({4, 0, 12, 8});
        require(ring.Empty(), "arrival is not reported during loading");

        require(move.m_dwMoveDelay == 1300, "arrival delay applies to both portal modes");
        move.m_dwMoveStepStartTime = timeGetTime() - 1301;
        move.FrameMove();
        move.FrameMove();
        ring.ExpectRequest({5, 0, 3, 1, arrivalMode});
        require(move.m_byMoveStep == MOVEMAP_INFO::MMS_NONE && !avatar.IsDisable(ROSF_MOVABLE),
                "arrival sends once and releases input");
        char mode = arrivalMode;
        _MSG_HEADER arrivalHeader{5, {3, 2}};
        require(network.AnalysisServerPacket(&arrivalHeader, &mode), "normal arrival acknowledgment");
        require(!network.PositionMsg_PlayerStop_clzo(FALSE) && ring.Empty(),
                "the old movement does not arm a stop packet on Resources");
        Vector3f target{avatar.GetPosX() + 30, avatar.GetPosY(), avatar.GetPosZ()};
        require(network.PositionMsg_MoveRequest_clzo(target, FALSE), "first ordinary movement from Resources");
        packet = ring.ReadRequest();
        RF455MoveRequest movement{};
        require(packet.size() == 30 && packet[2] == 4 && packet[3] == 1,
                "first movement wire on Resources");
        for (std::size_t i = 4; i < packet.size(); ++i)
            packet[i] = BYTE((packet[i] ^ 33) - 24);  // Inverse body transform for the fixture's zero account keys.
        std::memcpy(&movement, packet.data() + 4, sizeof movement);
        require(movement.current[0] == destination[0] && movement.current[2] == destination[2] &&
                movement.sequence == 2, "first request uses Resources position and keeps sequence continuity");
        RF455MoveBroadcast accepted{avatar.GetIndex(),
            {short(avatar.GetPosX()), short(avatar.GetPosY()), short(avatar.GetPosZ())},
            {movement.targetXZ[0], movement.targetXZ[1]}, 300, 0};
        _MSG_HEADER movementHeader{WORD(4 + sizeof accepted), {4, 4}};
        require(network.AnalysisServerPacket(&movementHeader, reinterpret_cast<char*>(&accepted)) &&
                avatar.IsEqualAction(CAI_MOVE_MOVING), "first movement acknowledgment starts the Resources path");
        R3SetLoopTime(1.0f / 30.0f);
        avatar.AdvanceLocalMovement455();
        firstStepDistance = GetDist(avatar.GetPosition(), destination);
        require(avatar.GetPosX() != destination[0] && firstStepDistance < 60.0f,
                "the first frame advances on Resources without a position reset");

        require(land.Destroy(), "release both map owners");
        g_pUiMapLoadingWindow = nullptr;
        g_pUiRadarWindow = nullptr;
        g_pUiMinimapWindow = nullptr;
        g_pNextActionMgr = nullptr;
        g_pCharacterMgr = nullptr;
        g_pCamera = nullptr;
    }
    g_pUiScreen = nullptr;
    g_pNetworkMgr = nullptr;
    _DestroyAnimationMgr();
    g_ifCharIF = nullptr;
    g_MainApp.ReleaseR3D3D();
    ReleaseR3Engine();
    std::printf("{\"status\":\"PASS\",\"map\":2,\"portal\":%d,\"arrival\":[3,1,3,2],"
                "\"arrival_mode\":%d,\"movement\":[4,1,4,4],\"late_stop_ignored\":true,"
                "\"movement_sequence\":2,\"first_frame_advanced\":true,\"first_step_distance\":%.6f}\n",
                assigned ? 0xff : 13, assigned ? GST_BASE_PORTAL : GST_PORTAL, firstStepDistance);
    return 0;
}

LONG reportArrivalFault(EXCEPTION_POINTERS* fault)
{
    const auto* record = fault->ExceptionRecord;
    if (record->ExceptionCode == 0xe06d7363) return EXCEPTION_CONTINUE_SEARCH;
    std::fprintf(stderr, "arrival exception %08lx at RVA %08lx\n", record->ExceptionCode,
                 reinterpret_cast<DWORD>(record->ExceptionAddress) -
                 reinterpret_cast<DWORD>(GetModuleHandleA(nullptr)));
    return EXCEPTION_EXECUTE_HANDLER;
}

int guardedPortalArrival(bool assigned)
{
    __try { return runPortalArrival(assigned); }
    __except(reportArrivalFault(GetExceptionInformation())) { return 99; }
}
