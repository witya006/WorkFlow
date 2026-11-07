#include "gameobject/manager/ccharactermgr.h"
#include "gameobject/board/common/cboardmanager.h"
#include "cland.h"
#include "ccamera.h"
#include "datafile.h"
#include "datatable/cresourcedatamgr.h"
#include "item/citemmgr.h"
#include "input/imeedit.h"
#include "baseheader.h"
#include "gameprogress/cgp_maingame.h"
#include "mainapp.h"
#include "client455_tutorial_board.h"
#include "client455_briefing_window.h"
#include <cstdio>
#include <typeinfo>

extern CMainApp g_MainApp;
template<class Tag, typename Tag::Type Member> struct MemberAccess {
    friend typename Tag::Type access(Tag) { return Member; }
};
struct NetworkMember { using Type = CNetworkMgr CMainApp::*; friend Type access(NetworkMember); };
template struct MemberAccess<NetworkMember, &CMainApp::m_cNetworkMgr>;
struct NetworkScope {
    CNetworkMgr& network = g_MainApp.*access(NetworkMember{});
    NetworkScope() { if (!network.Create()) throw 1; }
    ~NetworkScope() { network.Destroy(); }
};

// Measures the current source, including its gaps. No reference executable,
// graphics device, stage/factory change or simulated gameplay is involved.
static int measure() {
    // Board constructors resolve their real network-message processor. The
    // normal client creates this owner before creating gameplay boards.
    NetworkScope context;
    CBoardManager manager;
    manager.Create();
    std::printf("{\"source_registry_limit\":%u,\"source_main_game_bytes\":%u,"
                "\"source_avatar_bytes\":%u,\"source_tutorial_board_bytes\":%u,"
                "\"source_briefing_bytes\":%u,\"boards\":[",
                unsigned(MAX_BOARD_TYPE), unsigned(sizeof(CGP_MainGame)),
                unsigned(sizeof(CAvatar)), unsigned(sizeof(CTutorialBoard)),
                unsigned(sizeof(CGUIBriefingWindow)));
    bool comma = false;
    unsigned count = 0;
    for (unsigned slot = 0; slot < MAX_BOARD_TYPE; ++slot) {
        if (slot == 2) continue; // This public ID aliases equipment in both versions.
        auto* object = manager.GetBoard(BYTE(slot));
        if (!object) continue;
        std::printf("%s{\"id\":%u,\"class\":\"%s\"}", comma ? "," : "", slot, typeid(*object).name());
        comma = true;
        ++count;
    }
    std::printf("],\"source_objects\":%u,\"equipment_alias\":%s,"
                "\"out_of_range_null\":%s,\"actual_Tutorial\":false}\n",
                count, manager.GetBoard(2) == manager.GetBoard(1) ? "true" : "false",
                !manager.GetBoard(255) && !manager.GetBoard(MAX_BOARD_TYPE) ? "true" : "false");
    return 0;
}
static LONG recordFailure(EXCEPTION_POINTERS* info) {
    std::fprintf(stderr, "exception=%08lx ownRVA=%08lx ECX=%08lx EAX=%08lx\n",
                 info->ExceptionRecord->ExceptionCode,
                 DWORD(info->ExceptionRecord->ExceptionAddress) - DWORD(GetModuleHandleA(nullptr)),
                 info->ContextRecord->Ecx, info->ContextRecord->Eax);
    return EXCEPTION_EXECUTE_HANDLER;
}
int main() {
    __try { return measure(); }
    __except(recordFailure(GetExceptionInformation())) { return 99; }
}
