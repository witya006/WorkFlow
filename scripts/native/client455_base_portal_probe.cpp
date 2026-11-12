#include "gameobject/manager/ccharactermgr.h"
#include "gameobject/manager/ctargetmgr.h"
#include "gameobject/board/common/cboardmanager.h"
#include "network/netmsgprocessor/map/cnetmsgprocessor_map.h"
#include "network/netmsgprocessor/itemtrade/cnetmsgprocessor_itemtrade.h"
#include "gameobject/board/general/cpartyboard.h"
#include "cland.h"
#include "ccamera.h"
#include "datafile.h"
#include "datatable/cresourcedatamgr.h"
#include "input/imeedit.h"
#include "gameprogress/cgameprogress.h"
#include "gameprogress/cinputprocessmgr.h"
#include "userinterface/spritemgr.h"
#include "client455_client_items.h"
#include "client455_item_icon_metadata.h"
#include "client455_nuclear_registry.h"
#include "client455_nation_paths.h"
#include "mainapp.h"
#include "userinterface/gamewindow/etcwin/guimaploadingwindow.h"
#include "userinterface/gamewindow/etcwin/guiradarwindow.h"
#include "userinterface/gamewindow/etcwin/guiminimapwindow.h"
#include "jerror.h"

#include <array>
#include <cstdio>
#include <fstream>
#include <initializer_list>
#include <iterator>
#include <memory>
#include <stdexcept>
#include <string>
#include <vector>

extern CMainApp g_MainApp;

namespace {
void require(bool condition, const char* message)
{
    if (!condition) throw std::runtime_error(message);
}

template<class Tag, typename Tag::Type Member>
struct MemberAccess { friend typename Tag::Type access(Tag) { return Member; } };
struct Boards { using Type = CBaseBoard*(CBoardManager::*)[MAX_BOARD_TYPE]; friend Type access(Boards); };
struct Packs { using Type = CObjectPack* CObjectBoard::*; friend Type access(Packs); };
struct SendBuffer { using Type = _NET_BUFFER* CNetProcess::*; friend Type access(SendBuffer); };
struct Owner { using Type = CNetWorking* CNetProcess::*; friend Type access(Owner); };
struct Active { using Type = BYTE(CNetworkMgr::*)[6]; friend Type access(Active); };
struct Processors {
    using Type = CNetMsgProcessor_Base*(CNetworkMgr::*)[MAX_NET_MSG_PROCESSOR];
    friend Type access(Processors);
};
struct ControlKey { using Type = BOOL CInputProcessMgr::*; friend Type access(ControlKey); };
template struct MemberAccess<Boards, &CBoardManager::m_listBoard>;
template struct MemberAccess<Packs, &CObjectBoard::m_listItemPack>;
template struct MemberAccess<SendBuffer, &CNetProcess::m_pSendBuffer>;
template struct MemberAccess<Owner, &CNetProcess::m_pNetwork>;
template struct MemberAccess<Active, &CNetworkMgr::m_activeServer455>;
template struct MemberAccess<Processors, &CNetworkMgr::m_pNetMsgProcessor>;
template struct MemberAccess<ControlKey, &CInputProcessMgr::m_bControlKeyDown>;

struct Network : CNetworkMgr {
    using CNetworkMgr::AnalysisServerPacket;
    using CNetworkMgr::SendAvatarMove455;
};
struct Avatar : CAvatar {
    Avatar() { m_pMoveMapInfo = new MOVEMAP_INFO; }
};
struct LinkerInput : CInputProcessMgr {
    using CInputProcessMgr::ProcessLinkerKeys455;
};

struct SendRing {
    CNetProcess& process;
    _NET_BUFFER buffer;
    std::vector<char> storage;
    RF455NetworkCodec peer;

    explicit SendRing(Network& network) : process(network.m_Process[0]), storage(10000)
    {
        require(buffer.Configure(10000, 10000, storage.data()), "send buffer");
        process.*access(SendBuffer{}) = &buffer;
        process.*access(Owner{}) = &network;
        process.m_nIndex = 0;
        process.m_Type.m_wSocketMaxNum = 1;
        process.m_codec455.initializeDefault(true);
        peer.initializeDefault(true);
        peer.receiveKey = process.m_codec455.sendKey;
        (network.*access(Active{}))[0] = 0;
    }

    ~SendRing()
    {
        SetConnected(false);
        process.*access(SendBuffer{}) = nullptr;
        process.*access(Owner{}) = nullptr;
    }

    void SetConnected(bool connected) { process.m_NetSocket.GetSocket(0)->m_bAccept = connected; }

    bool Empty() { return buffer.GetTotalPush() == buffer.GetTotalPop(); }

    std::vector<BYTE> ReadRequest()
    {
        int size = 0;
        bool empty = false;
        const auto* wire = buffer.GetSendPoint(&size, &empty);
        std::array<BYTE, 32> payload{};
        std::size_t produced = 0;
        require(wire && !empty && peer.decode(wire, size, payload.data(), payload.size(), produced),
                "decode ordinary send ring");
        buffer.AddPopPos(size);
        return {payload.begin(), payload.begin() + produced};
    }

    void ExpectRequest(std::initializer_list<BYTE> expected = {6, 0, 4, 26, 0xcd, 0xab})
    {
        const auto packet = ReadRequest();
        require(packet.size() == expected.size() && std::equal(expected.begin(), expected.end(), packet.begin()),
                "ordinary send ring contains the expected message and serial fields");
    }
};

void checkMapPortal(Network& network, Avatar& avatar, CLand& land,
                    CGUIMapLoadingWindow& loading, SendRing& ring)
{
    std::fputs("ordinary map portals\n", stderr);
    std::strcpy(GetR3State()->MapPath, ".\\Map\\");
    require(land.LoadData(), "real Map.edf portal catalog");
    auto& move = *avatar.GetMoveMapInfo();
    land.SetMapIndex(0);
    land.SetPortalIndex(3);
    auto* boards = _GetGBM();
    auto& processor = (network.*access(Processors{}))[NMP_MAP];
    require(!processor, "empty map processor slot");
    processor = new CNetMsgProcessor_Map;
    CNextActionMgr nextAction;
    g_pNextActionMgr = &nextAction;
    struct ClearNextAction {
        ~ClearNextAction() { g_pNextActionMgr = nullptr; }
    } cleanup;
    avatar.Enable(ROSF_MOVABLE);

    const auto stable = [&] {
        return land.GetMapIndex() == 0 && land.GetPortalIndex() == 3;
    };
    const auto ready = [&] {
        return stable() && !boards->IsRequestProcess() && !move.m_bIsMoved &&
            !move.m_pEnterPortalInfo && !move.m_pExitPortalInfo && move.m_byMoveStep == MOVEMAP_INFO::MMS_NONE;
    };
    const auto reply = [&](BYTE code, BYTE map, WORD size = 15) {
        std::array<char, 15> body{};
        body[0] = static_cast<char>(code);
        body[1] = static_cast<char>(map);
        const float position[]{-128.25f, 35.5f, 803.75f};
        std::memcpy(body.data() + 2, position, sizeof position);
        _MSG_HEADER header{WORD(size + 4), {8, 2}};
        return network.AnalysisServerPacket(&header, body.data());
    };
    const auto start = [&](BYTE portal, BYTE map, DWORD exitPortal) {
        require(move.MoveToPortal_Request(portal) && boards->IsRequestProcess() && stable() &&
                move.m_bIsMoved && move.m_byExitMapIndex == map &&
                move.m_pExitPortalInfo && move.m_pExitPortalInfo->byIndex == exitPortal,
                "ordinary request keeps the source map and resolves the link");
        ring.ExpectRequest({11, 0, 8, 1, portal, 255, 255, 255, 255, 255, 255});
    };
    require(ready(), "fresh ordinary portal state");
    ring.SetConnected(false);
    require(!move.MoveToPortal_Request(0) && ready() && ring.Empty(),
            "send failure leaves the source map and lock unchanged");
    ring.SetConnected(true);
    require(!move.MoveToPortal_Request(255) && !move.MoveToPortal_Request(8) &&
            !move.MoveToPortal_Request(3) && ready() && ring.Empty(),
            "invalid index, exit-only gate and absent destination reject before sending");
    start(0, 0, 11);
    require(!move.MoveToPortal_Request(0) && !reply(0, 0, 1) &&
            boards->IsRequestProcess() && ring.Empty(), "duplicate and short success preserve pending request");
    require(reply(2, 0, 1) && ready(), "distance refusal releases movement and board state");
    start(0, 0, 11);
    network.CancelPendingMapRequests455();
    require(reply(0, 0) && ready(), "cancellation discards a late response");

    for (const auto portal : {BYTE(0), BYTE(2)}) {
        const BYTE destination = portal == 0 ? 0 : 2;
        start(portal, destination, portal == 0 ? 11 : 13);
        require(reply(0, destination) && !boards->IsRequestProcess() && stable() &&
                move.m_byMoveStep == MOVEMAP_INFO::MMS_PREV_LOAD_DATA &&
                move.m_byMoveType == GST_PORTAL && move.m_vecPosition[0] == -128.25f &&
                move.m_vecPosition[1] == 35.5f && move.m_vecPosition[2] == 803.75f,
                "ordinary result schedules the linked map and full float coordinates");
        require(reply(2, destination, 1) && move.m_byMoveStep == MOVEMAP_INFO::MMS_PREV_LOAD_DATA,
                "duplicate reply does not cancel an accepted transition");
        move.m_dwMoveStepStartTime = timeGetTime() - (portal == 0 ? 700 : 1300);
        move.FrameMove();
        require(move.m_byMoveStep == MOVEMAP_INFO::MMS_LOAD_DATA &&
                !!loading.IsShow() == (portal != 0), "only the cross-map portal opens the loading window");
        if (loading.IsShow()) loading.Close();
        move.Init();
        avatar.Enable(ROSF_MOVABLE);
    }
}

int run(const char* itemFile, const char* keyMapFile)
{
    InitR3Engine();
    g_pMainApp = &g_MainApp;
    g_MainApp.SetGameProgressID(GPI_TITLE);
    g_pUiScreen = &gScreen;
    RF455NuclearContainer nuclear;
    RF455_BindNuclearContainer(&nuclear);
    ChInterface renderer;
    g_ifCharIF = &renderer;
    require(_CreateAnimationMgr(), "normal animation owner");
    const auto networkOwner = std::make_unique<Network>();
    auto& network = *networkOwner;
    g_pNetworkMgr = &network;
    const auto avatarOwner = std::make_unique<Avatar>();
    auto& avatar = *avatarOwner;
    g_pAvatar = &avatar;
    avatar.CCharacter::SetAction(CAI_MOVE_STOP);
    auto* move = avatar.GetMoveMapInfo();

    CLand land;
    require(land.Create(), "land owner");
    auto& maps = const_cast<RF455MapData&>(land.MapData455());
    maps.count = 2;
    maps.maps.reset(new RF455MapInfo[maps.count]);
    std::strcpy(maps.maps[1].pFileName, "missing-base-portal-map.bsp");
    land.SetMapIndex(0);
    land.SetPortalIndex(3);
    CGUIMapLoadingWindow loading;
    loading.Show(FALSE);
    g_pUiMapLoadingWindow = &loading;

    auto& items = RF455_GameItems();
    std::ifstream input(itemFile, std::ios::binary);
    const std::vector<unsigned char> bytes((std::istreambuf_iterator<char>(input)), {});
    require(items.data.loadItemEdf(bytes.data(), bytes.size(), true), "pinned Item.edf");
    auto* item = dynamic_cast<RF455BasicItem*>(items.create(0, IEPT_RETURN, 0));
    require(item && item->rawMetadata().size > 88 && item->rawMetadata().data[88] == IEPT_RETURN,
            "original Return catalog record");
    item->header().serial = 0x1234abcd;
    item->SetDownloadValue455(10, 0);

    auto* boards = _GetGBM();
    auto* inventory = new CInventoryBoard;
    (boards->*access(Boards{}))[IBT_INVENTORY] = inventory;
    inventory->CObjectBoard::Create(IBT_INVENTORY, 1, 1);
    require(inventory->CObjectBoard::AddPack(0), "inventory pack");
    auto* object = new CBoardObject;
    object->SetItem455(item);
    require((inventory->*access(Packs{}))[0].Add(0, object), "typed first socket");

    CLinkBoard linker;
    linker.CObjectBoard::Create(IBT_LINK, 5, 10);
    auto& registeredLinker = (boards->*access(Boards{}))[IBT_LINK];
    require(!registeredLinker, "empty Linker registry slot");
    registeredLinker = &linker;
    struct ReleaseRegistration {
        CBaseBoard*& slot;
        ~ReleaseRegistration() { slot = nullptr; }
    } release{registeredLinker};
    require(linker.CObjectBoard::AddPack(4), "fifth Linker bank");
    auto shortcut = std::unique_ptr<CBoardObject>(object->Clone());
    auto& bank = (linker.*access(Packs{}))[4];
    require(shortcut && bank.Add(9, shortcut.get()), "linked Return in fifth bank, tenth slot");

    SendRing ring(network);
    const auto use = [&] { return inventory->UI_UseRequest(0, 0) != FALSE; };
    const auto quantity = [&] { return RF455_ReadBasicIconMetadata(*item).quantity; };
    const auto dispatch = [&](BYTE result, BYTE destination, WORD length = 8) {
        std::array<char, 8> body{{static_cast<char>(result), static_cast<char>(destination),
                                   0x2e, static_cast<char>(0xfb), 0x37, 0, 0x29, 0x09}};
        _MSG_HEADER header{WORD(length + 4), {4, 27}};
        return network.AnalysisServerPacket(&header, body.data());
    };
    const auto ready = [&] {
        return !boards->IsRequestProcess() && !move->m_bIsMoved &&
               move->m_byMoveStep == MOVEMAP_INFO::MMS_NONE &&
               land.GetMapIndex() == 0 && land.GetPortalIndex() == 3 && quantity() == 10;
    };
    const auto start = [&] {
        require(use() && boards->IsRequestProcess() && move->m_bIsMoved &&
                land.GetMapIndex() == 0 && land.GetPortalIndex() == 3 &&
                move->m_byEnterMapIndex == 0 && quantity() == 10, "normal inventory use starts request");
        ring.ExpectRequest();
    };

    const auto useShortcut = [&](BYTE slot, BOOL dragging = FALSE) {
        auto& window = linker.LinkerWindow455();
        _mouse_event event{window.GetItem(4, slot), LMOUSE_STROKED, 0, 0};
        window.DispatchMouse455(event, dragging, FALSE, FALSE, FALSE);
    };
    const auto resetMove = [&] {
        move->m_bIsMoved = FALSE;
        move->m_byMoveStep = MOVEMAP_INFO::MMS_NONE;
        land.SetPortalIndex(3);
        item->SetDownloadValue455(10, 0);
    };

    std::fputs("send failure\n", stderr);
    require(!use() && ready(), "send failure leaves the current map and releases inventory");
    ring.SetConnected(true);
    std::fputs("first request\n", stderr);
    start();
    require(!use() && !dispatch(0, 0, 1) && !dispatch(5, 0, 2) &&
            boards->IsRequestProcess(), "duplicate use and malformed results leave request pending");
    std::fputs("server refusal\n", stderr);
    require(dispatch(5, 0, 1) && ready(), "server refusal permits another attempt");
    start();
    require(dispatch(0, 255) && ready(), "map outside the catalog preserves current scene");
    start();
    require(dispatch(0, 1) && ready(), "missing map file preserves current scene");
    start();
    network.CancelBasePortalRequest455();
    require(ready() && dispatch(10, 0) && ready(), "cancellation ignores an unsolicited reply");

    for (BYTE success : {BYTE(0), BYTE(10)}) {
        std::fprintf(stderr, "success %u\n", success);
        start();
        require(dispatch(success, 0) && !boards->IsRequestProcess() && land.GetPortalIndex() == 0xff &&
                move->m_byMoveStep == MOVEMAP_INFO::MMS_PREV_LOAD_DATA &&
                move->m_byMoveType == GST_BASE_PORTAL && move->m_byExitMapIndex == 0 &&
                move->m_vecPosition[0] == -1234 && move->m_vecPosition[1] == 55 &&
                move->m_vecPosition[2] == 2345 && quantity() == 9 &&
                boards->GetOrgObject() == nullptr, "success schedules signed destination and consumes one");
        require(dispatch(success, 0) && quantity() == 9, "duplicate result does not consume a second item");
        move->m_dwMoveStepStartTime = timeGetTime() - 701;
        move->FrameMove();
        require(move->m_byMoveStep == MOVEMAP_INFO::MMS_LOAD_DATA && !loading.IsShow(),
                "same-map return skips the loading overlay after the 455 delay");
        resetMove();
    }

    useShortcut(8);
    useShortcut(9, TRUE);
    require(ready() && !linker.UseShortcut455(5, 9), "empty, dragged or out-of-range shortcut stays idle");
    useShortcut(9);
    require(boards->IsRequestProcess() && boards->GetOrgObject() == object &&
            boards->GetOrgBoardType() == IBT_INVENTORY && boards->GetOrgSocketNo() == 0,
            "fifth-bank mouse dispatch activates the actual inventory slot");
    ring.ExpectRequest();
    require(dispatch(0, 0) && quantity() == 9 && !boards->IsRequestProcess() &&
            move->m_vecPosition[0] == -1234, "ordinary response consumes the original item");
    resetMove();

    LinkerInput inputKeys;
    const std::string path(keyMapFile);
    const auto endOfRoot = path.find_last_of("\\/");
    auto* nation = RF455_GetNormalNationPaths();
    require(endOfRoot != std::string::npos && endOfRoot < sizeof nation->dataRoot, "key map directory");
    const auto keyRoot = path.substr(0, endOfRoot);
    std::strcpy(nation->dataRoot, keyRoot.c_str());
    require(inputKeys.LoadData(), "production input loader");
    const auto pressF10 = [&](DWORD now, BOOL focused = FALSE, LPARAM flags = 0) {
        inputKeys.MsgProc(nullptr, WM_SYSKEYDOWN, VK_F10, flags);
        inputKeys.ProcessLinkerKeys455(now, focused);
    };
    auto& activeBank = linker.LinkerWindow455().HotbarState455().active;
    activeBank = 0;
    pressF10(1000);
    require(ready() && ring.Empty(), "keyboard respects the empty active bank");
    activeBank = 4;
    pressF10(1600, TRUE);
    inputKeys.ProcessLinkerKeys455(1601, FALSE);
    require(ready() && ring.Empty(), "focused chat suppresses the key and leaves no deferred use");
    pressF10(1700, FALSE, 1L << 29);
    inputKeys.*access(ControlKey{}) = TRUE;
    pressF10(1701);
    inputKeys.*access(ControlKey{}) = FALSE;
    require(ready() && ring.Empty(), "modifiers suppress the normal slot path");
    pressF10(2000);
    require(boards->IsRequestProcess() && boards->GetOrgObject() == object, "F10 uses fifth bank");
    ring.ExpectRequest();
    require(dispatch(5, 0, 1) && ready(), "keyboard request refusal leaves the item available");
    pressF10(2500);
    require(ready() && ring.Empty(), "same slot does not repeat within 500 milliseconds");
    pressF10(2501);
    require(boards->IsRequestProcess(), "slot can be used after the repeat interval");
    ring.ExpectRequest();
    require(dispatch(0, 0) && quantity() == 9 && !boards->IsRequestProcess(),
            "F10 and mouse share the item owner and result dispatcher");
    resetMove();
    for (BYTE slot = 0; slot < 9; ++slot) {
        require(bank.Add(slot, shortcut.get()), "borrow a shortcut in the selected bank");
        gScan[VK_F1 + slot] = 1;
        inputKeys.ProcessLinkerKeys455(3002, FALSE);
        require(boards->IsRequestProcess() && boards->GetOrgObject() == object,
                "each F-key uses its matching slot in the selected bank");
        ring.ExpectRequest();
        require(dispatch(5, 0, 1) && ready(), "slot use leaves no pending request after refusal");
        require(bank.Empty(slot), "release slot from keyboard fixture");
    }

    auto& inventoryPack = (inventory->*access(Packs{}))[0];
    require(inventoryPack.Empty(0), "unlink source without destroying shortcut fixture");
    require(!linker.UseShortcut455(4, 9) && ready(), "stale shortcut does not send a request");
    require(inventoryPack.Add(0, object), "return inventory ownership for cleanup");
    require(bank.Empty(9), "release borrowed Linker fixture slot");
    shortcut.reset();
    checkMapPortal(network, avatar, land, loading, ring);

    std::fputs("cleanup\n", stderr);
    (boards->*access(Boards{}))[IBT_INVENTORY] = nullptr;
    delete inventory;
    g_pUiMapLoadingWindow = nullptr;
    g_pUiScreen = nullptr;
    g_pAvatar = nullptr;
    g_pNetworkMgr = nullptr;
    RF455_UnbindNuclearContainer(&nuclear);
    _DestroyAnimationMgr();
    g_ifCharIF = nullptr;
    std::puts("{\"status\":\"PASS\",\"request\":[4,26],\"reply\":[4,27],"
              "\"success_codes\":[0,10],\"quantity\":[10,9],\"bad_map_cases\":2,"
              "\"refusal\":true,\"malformed\":true,\"send_failure\":true,\"cancel\":true,"
              "\"same_map_no_loading_overlay\":true,\"linker_mouse\":[4,9],\"stale_shortcut\":true,"
              "\"linker_f10\":[4,9],\"keyboard_slots\":10,"
              "\"chat_focus_suppressed\":true,\"repeat_interval_ms\":500,"
              "\"ordinary_portal\":{\"request\":[8,1,7],\"reply\":[8,2,15],"
              "\"same_map\":[0,0,11],\"cross_map\":[0,2,13],\"rejected_before_send\":3,"
              "\"refusal_and_cancel\":true,\"loading_overlay_only_cross_map\":true}}");
    return 0;
}
#include "client455_portal_arrival_probe.inc"
}

int main(int argc, char** argv)
{
    SetErrorMode(SEM_FAILCRITICALERRORS | SEM_NOGPFAULTERRORBOX | SEM_NOOPENFILEERRORBOX);
    try {
        if (argc == 2 && !std::strcmp(argv[1], "--arrival")) return guardedPortalArrival();
        require(argc == 3, "pinned Item.edf and KeyMap.dat arguments");
        return run(argv[1], argv[2]);
    } catch (const std::exception& error) {
        std::fprintf(stderr, "%s\n", error.what());
        return 1;
    }
}
