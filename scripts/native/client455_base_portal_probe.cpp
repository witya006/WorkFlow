#include "gameobject/manager/ccharactermgr.h"
#include "gameobject/board/common/cboardmanager.h"
#include "cland.h"
#include "ccamera.h"
#include "datafile.h"
#include "datatable/cresourcedatamgr.h"
#include "input/imeedit.h"
#include "gameprogress/cgameprogress.h"
#include "userinterface/spritemgr.h"
#include "client455_client_items.h"
#include "client455_item_icon_metadata.h"
#include "client455_nuclear_registry.h"
#include "mainapp.h"
#include "userinterface/gamewindow/etcwin/guimaploadingwindow.h"

#include <array>
#include <cstdio>
#include <fstream>
#include <iterator>
#include <memory>
#include <stdexcept>
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
template struct MemberAccess<Boards, &CBoardManager::m_listBoard>;
template struct MemberAccess<Packs, &CObjectBoard::m_listItemPack>;
template struct MemberAccess<SendBuffer, &CNetProcess::m_pSendBuffer>;
template struct MemberAccess<Owner, &CNetProcess::m_pNetwork>;
template struct MemberAccess<Active, &CNetworkMgr::m_activeServer455>;

struct Network : CNetworkMgr {
    using CNetworkMgr::AnalysisServerPacket;
};
struct Avatar : CAvatar {
    Avatar() { m_pMoveMapInfo = new MOVEMAP_INFO; }
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

    void ExpectRequest()
    {
        int size = 0;
        bool empty = false;
        const auto* wire = buffer.GetSendPoint(&size, &empty);
        std::array<BYTE, 32> payload{};
        std::size_t produced = 0;
        const std::array<BYTE, 6> expected{{6, 0, 4, 26, 0xcd, 0xab}};
        require(wire && !empty && peer.decode(wire, size, payload.data(), payload.size(), produced) &&
                produced == expected.size() && std::equal(expected.begin(), expected.end(), payload.begin()),
                "ordinary send ring contains 4/26 with the item's low WORD serial");
        buffer.AddPopPos(size);
    }
};

int run(const char* itemFile)
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
        move->m_bIsMoved = FALSE;
        move->m_byMoveStep = MOVEMAP_INFO::MMS_NONE;
        land.SetPortalIndex(3);
        item->SetDownloadValue455(10, 0);
    }

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
              "\"same_map_no_loading_overlay\":true}");
    return 0;
}
}

int main(int argc, char** argv)
{
    SetErrorMode(SEM_FAILCRITICALERRORS | SEM_NOGPFAULTERRORBOX | SEM_NOOPENFILEERRORBOX);
    try {
        require(argc == 2, "pinned Item.edf argument");
        return run(argv[1]);
    } catch (const std::exception& error) {
        std::fprintf(stderr, "%s\n", error.what());
        return 1;
    }
}
