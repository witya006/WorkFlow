#include "gameobject/manager/ccharactermgr.h"
#include "gameobject/board/common/cboardmanager.h"
#include "cland.h"
#include "ccamera.h"
#include "datafile.h"
#include "datatable/cresourcedatamgr.h"
#include "item/citemmgr.h"
#include "input/imeedit.h"
#include "baseheader.h"
#include "gameprogress/cgameprogress.h"
#include "userinterface/spritemgr.h"
#include "mainapp.h"
#include "client455_connection.h"
#include "client455_nation_paths.h"
#include "client455_language.h"
#include <cstdio>
#include <cstring>
#include <memory>
#include <string>
#include <vector>
extern CMainApp g_MainApp;
template<class Tag,typename Tag::Type Member>struct MemberAccess{friend typename Tag::Type access(Tag){return Member;}};
struct NetworkMember{using Type=CNetworkMgr CMainApp::*;friend Type access(NetworkMember);};
struct SendBuffer{using Type=_NET_BUFFER* CNetProcess::*;friend Type access(SendBuffer);};
struct ReceiveBuffer{using Type=_NET_BUFFER* CNetProcess::*;friend Type access(ReceiveBuffer);};
struct Owner{using Type=CNetWorking* CNetProcess::*;friend Type access(Owner);};
struct AcceptList{using Type=CNetIndexList CNetProcess::*;friend Type access(AcceptList);};
struct CloseList{using Type=CNetIndexList CNetProcess::*;friend Type access(CloseList);};
struct ReadyList{using Type=CNetIndexList CNetProcess::*;friend Type access(ReadyList);};
template struct MemberAccess<NetworkMember,&CMainApp::m_cNetworkMgr>;
template struct MemberAccess<SendBuffer,&CNetProcess::m_pSendBuffer>;
template struct MemberAccess<ReceiveBuffer,&CNetProcess::m_pRecvBuffer>;
template struct MemberAccess<Owner,&CNetProcess::m_pNetwork>;
template struct MemberAccess<AcceptList,&CNetProcess::m_listAcceptEvent>;
template struct MemberAccess<CloseList,&CNetProcess::m_listCloseEvent>;
template struct MemberAccess<ReadyList,&CNetProcess::m_listAcceptReady>;
#define REQUIRE(x) do{if(!(x)){std::fprintf(stderr,"Connection failure line%d: %s\n",__LINE__,#x);return 1;}}while(0)
struct ClockFixture{std::vector<std::uint32_t> ticks;unsigned at=0,pumps=0,sleeps=0,connectedAfter=0;bool badSleep=false;};
static RF455ConnectionWait clockApi(ClockFixture& f){return RF455ConnectionWait{&f,
    [](void* p)->std::uint32_t{auto& f=*static_cast<ClockFixture*>(p);const auto at=f.at++;return f.ticks[at<f.ticks.size()?at:f.ticks.size()-1];},
    [](void* p){++static_cast<ClockFixture*>(p)->pumps;},
    [](void* p)->bool{auto& f=*static_cast<ClockFixture*>(p);return f.connectedAfter&&f.pumps>=f.connectedAfter;},
    [](void* p,std::uint32_t ms){auto& f=*static_cast<ClockFixture*>(p);++f.sleeps;f.badSleep|=ms!=4;}};}
struct Capture: CNetWorking{unsigned accepts=0;void AcceptClientCheck(DWORD,DWORD,DWORD) override{++accepts;}};
static unsigned dialogs=0;static std::string dialogText;
static BOOL CALLBACK captureText(HWND child,LPARAM){char type[64],text[1024];GetClassNameA(child,type,sizeof(type));if(!std::strcmp(type,"Static")&&GetWindowTextA(child,text,sizeof(text))&&dialogText.empty())dialogText=text;return TRUE;}
static void CALLBACK closeOwnDialog(HWND window,UINT,UINT_PTR timer,DWORD){KillTimer(window,timer);++dialogs;dialogText.clear();EnumChildWindows(window,captureText,0);EndDialog(window,IDOK);}
static LRESULT CALLBACK ownDialogHook(int code,WPARAM value,LPARAM param){
    if(code==HCBT_ACTIVATE){HWND window=reinterpret_cast<HWND>(value);char type[64];GetClassNameA(window,type,sizeof(type));if(!std::strcmp(type,"#32770"))SetTimer(window,0x455,25,closeOwnDialog);}
    return CallNextHookEx(nullptr,code,value,param);
}

static int checkDisconnect(CNetworkMgr& network)
{
    struct Socket {
        SOCKET handle;
        ~Socket() { if (handle != INVALID_SOCKET) closesocket(handle); }
    } listener{socket(AF_INET, SOCK_STREAM, IPPROTO_TCP)};
    REQUIRE(listener.handle != INVALID_SOCKET);
    sockaddr_in address{};
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = inet_addr("127.0.0.1");
    REQUIRE(bind(listener.handle, reinterpret_cast<sockaddr*>(&address), sizeof address) == 0);
    REQUIRE(listen(listener.handle, 1) == 0);
    int addressSize = sizeof address;
    REQUIRE(getsockname(listener.handle, reinterpret_cast<sockaddr*>(&address), &addressSize) == 0);
    network.SetServerIP(GST_WORLD, address.sin_addr.s_addr);
    network.SetServerPort(GST_WORLD, ntohs(address.sin_port));

    const auto pumpUntil = [&](const auto& ready) {
        const DWORD start = timeGetTime();
        do {
            network.PumpEvents455();
            if (ready()) return true;
            Sleep(4);
        } while (timeGetTime() - start < 5000);
        return false;
    };
    auto& process = network.m_Process[NST_GAME_SERVER];
    const auto* transport = process.m_NetSocket.GetSocket(0);
    auto& pendingAccept = process.*access(ReadyList{});
    network.Close(GST_WORLD);
    REQUIRE(transport->m_Socket == INVALID_SOCKET && !network.IsConnectedToServer(GST_WORLD));
    enum class End { BeforePublication, Reset, Graceful };
    for (const auto end : {End::BeforePublication, End::Reset, End::Graceful}) {
        REQUIRE(network.ConnectToServer455(GST_WORLD, NST_GAME_SERVER) == 0);
        Socket peer{accept(listener.handle, nullptr, nullptr)};
        REQUIRE(peer.handle != INVALID_SOCKET);
        if (end == End::BeforePublication) {
            DWORD waiting = 0;
            network.PumpEvents455();
            const DWORD start = timeGetTime();
            while (!pendingAccept.CopyFront(&waiting) && timeGetTime() - start < 300) {
                Sleep(1);
                network.PumpEvents455();
            }
            REQUIRE(pendingAccept.CopyFront(&waiting) && !network.IsConnectedToServer(GST_WORLD));
        } else {
            REQUIRE(pumpUntil([&] { return network.IsConnectedToServer(GST_WORLD) != FALSE; }));
            static_cast<CNetWorking&>(network).CloseClientCheck(NST_LOCAL_CHAT, 0, 0);
            REQUIRE(network.IsConnectedToServer(GST_WORLD) && network.GetActiveServerID() == GST_WORLD);
        }

        if (end == End::Reset) {
            const linger settings{1, 0};
            REQUIRE(setsockopt(peer.handle, SOL_SOCKET, SO_LINGER,
                               reinterpret_cast<const char*>(&settings), sizeof settings) == 0);
            REQUIRE(closesocket(peer.handle) == 0);
            peer.handle = INVALID_SOCKET;
        } else {
            REQUIRE(shutdown(peer.handle, SD_SEND) == 0);
        }
        REQUIRE(pumpUntil([&] { return transport->m_Socket == INVALID_SOCKET; }));
        DWORD stale = 0;
        REQUIRE(!transport->m_bAccept && !pendingAccept.CopyFront(&stale));
        REQUIRE(!network.IsConnectedToServer(GST_WORLD) && network.GetActiveServerID() == GST_NONE);
    }

    FILE* result = std::fopen("result.json", "wb");
    REQUIRE(result);
    std::fputs("{\"status\":\"PASS\",\"loopback_connections\":3,\"early_fin_clears_pending_accept\":true,"
               "\"rst_clears_active_connection\":true,\"fin_clears_active_connection\":true,"
               "\"reconnect_after_rst\":true,\"unmapped_close_preserves_game_connection\":true,"
               "\"authentication_performed\":false}\n", result);
    std::fclose(result);
    return 0;
}

int main(){
    std::fprintf(stderr,"connection:begin\n");
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX|SEM_NOOPENFILEERRORBOX);
    std::uint32_t iterations=0;ClockFixture edge={{100,1100,1101}};REQUIRE(!RF455_WaitForConnection(clockApi(edge),1000,iterations)&&iterations==2&&edge.sleeps==1&&!edge.badSleep);
    ClockFixture overdue={{100,1200}};overdue.connectedAfter=1;REQUIRE(RF455_WaitForConnection(clockApi(overdue),1000,iterations)&&iterations==1&&!overdue.sleeps);
    ClockFixture wrap={{0xfffffffe,3,4}};REQUIRE(!RF455_WaitForConnection(clockApi(wrap),5,iterations)&&iterations==2&&wrap.sleeps==1);
    REQUIRE(!RF455_AcceptDelayElapsed(1000,0)&&RF455_AcceptDelayElapsed(1001,0)&&!RF455_AcceptDelayElapsed(998,0xfffffffe)&&RF455_AcceptDelayElapsed(999,0xfffffffe));
    {auto capture=std::make_unique<Capture>();auto process=std::make_unique<CNetProcess>();_NET_BUFFER receive,send;
     process.get()->*access(Owner{})=capture.get();process.get()->*access(ReceiveBuffer{})=&receive;process.get()->*access(SendBuffer{})=&send;process->m_nIndex=0;
     auto& accept=process.get()->*access(AcceptList{});auto& close=process.get()->*access(CloseList{});auto& ready=process.get()->*access(ReadyList{});accept.SetList(103);close.SetList(103);ready.SetList(103);
     for(unsigned i=0;i<103;++i)REQUIRE(accept.PushNode_Back(0));process->PumpEvents455();DWORD index=99;REQUIRE(accept.CopyFront(&index)&&index==0);process->PumpEvents455();REQUIRE(!accept.CopyFront(&index));
     process.get()->*access(Owner{})=nullptr;process.get()->*access(ReceiveBuffer{})=nullptr;process.get()->*access(SendBuffer{})=nullptr;}
    std::fprintf(stderr,"connection:kernel-done\n");REQUIRE(RF455_ReadConnectTimeout()==90000);
    struct Profile{const char* value;std::uint32_t ms;};for(const auto& profile:{Profile{"0",0},Profile{"1",1000},Profile{"-1",0xfffffc18},Profile{"4294968",704},Profile{"invalid",0}}){REQUIRE(WritePrivateProfileStringA("Network","ConnectTime",profile.value,"./DataTable/ClientSystem.ini"));REQUIRE(RF455_ReadConnectTimeout()==profile.ms);}
    char mode[32]={};FILE* file=std::fopen("mode.txt","rb");REQUIRE(file);std::fread(mode,1,sizeof(mode)-1,file);std::fclose(file);const bool positive=!std::strcmp(mode,"positive"),russia=!std::strcmp(mode,"russia");
    REQUIRE(RF455_InitializeNationPaths()&&RF455_InitializeLanguageData());REQUIRE(g_MainApp.CreateNetworkMgr455());g_MainApp.SetRequestLogout(FALSE);auto& network=g_MainApp.*access(NetworkMember{});
    if (!std::strcmp(mode, "disconnect")) return checkDisconnect(network);
    SOCKET reserved=INVALID_SOCKET;unsigned port=0;file=std::fopen("port.txt","r");if(file){std::fscanf(file,"%u",&port);std::fclose(file);}
    if(russia){REQUIRE(g_MainApp.GetDataFromLauncher());REQUIRE(network.GetServerIP(0)==inet_addr("127.0.0.1")&&network.GetServerIP(1)==0&&network.GetServerPort(1)==0);}
    else{
        if(!positive){reserved=socket(AF_INET,SOCK_STREAM,0);REQUIRE(reserved!=INVALID_SOCKET);sockaddr_in address={};address.sin_family=AF_INET;address.sin_addr.s_addr=inet_addr("127.0.0.1");REQUIRE(bind(reserved,reinterpret_cast<sockaddr*>(&address),sizeof(address))==0);int bytes=sizeof(address);REQUIRE(getsockname(reserved,reinterpret_cast<sockaddr*>(&address),&bytes)==0);port=ntohs(address.sin_port);}
        network.SetServerIP(1,inet_addr("127.0.0.1"));network.SetServerPort(1,port);
    }
    REQUIRE(WritePrivateProfileStringA("Network","ConnectTime",positive?"5":"0","./DataTable/ClientSystem.ini"));
    HHOOK hook=SetWindowsHookExA(WH_CBT,ownDialogHook,nullptr,GetCurrentThreadId());REQUIRE(hook);std::fprintf(stderr,"connection:calling\n");const DWORD begin=timeGetTime();const BOOL success=g_MainApp.ConnectNetwork455();std::fprintf(stderr,"connection:returned=%d\n",success);const DWORD elapsed=timeGetTime()-begin;const auto report=*RF455_GetConnectionReport();
    bool rawError=false;int peerPort=0;
    if(positive){
        REQUIRE(success&&report.outcome==RF455ConnectionOutcome::Connected&&report.rawResult==0&&report.waitIterations>0&&elapsed>=1000&&elapsed<8000&&dialogs==0&&network.IsConnectedToServer(1));
        auto* socket=network.m_Process[0].m_NetSocket.GetSocket(0);sockaddr_in peer={};int bytes=sizeof(peer);REQUIRE(getpeername(socket->m_Socket,reinterpret_cast<sockaddr*>(&peer),&bytes)==0&&peer.sin_addr.s_addr==inet_addr("127.0.0.1"));peerPort=ntohs(peer.sin_port);REQUIRE(peerPort==port);
        std::fprintf(stderr,"connection:calling-again\n");REQUIRE(!g_MainApp.ConnectNetwork455());std::fprintf(stderr,"connection:second-return\n");const auto failed=*RF455_GetConnectionReport();REQUIRE(failed.outcome==RF455ConnectionOutcome::TransportError&&failed.rawResult==-1&&!failed.waitIterations&&dialogs==1);char expected[256];_snprintf_s(expected,sizeof(expected),_TRUNCATE,RF455_GetNormalLanguagePack()->get(0x6be),-1);REQUIRE(dialogText==expected);rawError=true;
    }else{
        // Blocking Winsock connect and modal-dialog setup are outside the
        // target wait budget;the deterministic clock cases prove its boundary.
        REQUIRE(!success&&report.outcome==RF455ConnectionOutcome::Timeout&&report.rawResult==0&&report.waitIterations>0&&elapsed<8000&&dialogs==1&&!network.IsConnectedToServer(1));char expected[256];_snprintf_s(expected,sizeof(expected),_TRUNCATE,RF455_GetNormalLanguagePack()->get(0xbfa),report.detailError);REQUIRE(dialogText==expected);
    }
    UnhookWindowsHookEx(hook);if(reserved!=INVALID_SOCKET)closesocket(reserved);
    file=std::fopen("result.json","wb");REQUIRE(file);std::fprintf(file,"{\"status\":\"PASS\",\"mode\":\"%s\",\"strict_timeout_and_rollover\":true,\"accept_delay_boundary\":true,\"receipt_budget102\":true,\"profile_dword_wrap\":true,\"connected\":%s,\"elapsed_ms\":%lu,\"wait_iterations\":%lu,\"raw_result\":%d,\"timeout\":%s,\"raw_error_dialog\":%s,\"localized_dialogs\":%u,\"peer_port\":%d,\"russia_endpoint_mismatch\":%s,\"authentication_performed\":false}\n",mode,positive?"true":"false",elapsed,static_cast<unsigned long>(report.waitIterations),report.rawResult,positive?"false":"true",rawError?"true":"false",dialogs,peerPort,russia?"true":"false");std::fclose(file);return 0;
}
