#include "gameobject/manager/ccharactermgr.h"
#include "gameobject/board/common/cboardmanager.h"
#include "cland.h"
#include "ccamera.h"
#include "datafile.h"
#include "datatable/cresourcedatamgr.h"
#include "input/imeedit.h"
#include "gameprogress/cgameprogress.h"
#include "userinterface/spritemgr.h"
#include "mainapp.h"
#include "gameprogress/cgp_maingame.h"
#include "client455_player_status.h"
#include "client455_nuclear_aiming.h"
#include <cstdio>
#include <memory>
#include <stdexcept>
extern CMainApp g_MainApp;
template<class Tag,typename Tag::Type Member>struct MemberAccess{friend typename Tag::Type access(Tag){return Member;}};
struct NetworkMember{using Type=CNetworkMgr CMainApp::*;friend Type access(NetworkMember);};
template struct MemberAccess<NetworkMember,&CMainApp::m_cNetworkMgr>;
static unsigned checks=0;
static void check(bool value,const char* message){++checks;if(!value)throw std::runtime_error(message);}
template<class F>static bool refuses(F fn){try{fn();return false;}catch(const std::logic_error&){return true;}}
static std::uint64_t bit(unsigned n){return std::uint64_t(1)<<n;}
struct NetworkScope {
    CNetworkMgr& network=g_MainApp.*access(NetworkMember{});
    CGUIScreen* oldScreen=g_pUiScreen;
    NetworkScope(){g_pUiScreen=&gScreen;check(network.Create()!=0,"actual network owner initialization");}
    ~NetworkScope(){network.Destroy();g_pUiScreen=oldScreen;}
};
struct AvatarBinding {
    CAvatar* old=g_pAvatar;
    AvatarBinding(CAvatar& avatar){g_pAvatar=&avatar;}
    ~AvatarBinding(){g_pAvatar=old;}
};
static int run(){
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX|SEM_NOOPENFILEERRORBOX);
    check(!_GetAvatar()&&!RF455_AvatarRequiresHoverCancel(),"actual null-avatar short circuit");
    NetworkScope network;
    std::unique_ptr<CGP_MainGame> game(new CGP_MainGame);
    check(RF455_GetNuclearContainer()==&game->Nuclear455(),"actual MainGame constructor binds the aiming owner before UI creation");
    CAvatar avatar;AvatarBinding binding(avatar);
    check(refuses([&]{avatar.GetStatusCode455();}),"constructor status has no confirmed initialization");
    {
        CBoardManager startup;
        check(RF455_NuclearAiming().pending==0,"startup has no pending aiming");
        check(!refuses([&]{startup.SetHoverObject(nullptr);})&&!startup.GetHoverObject(),"legal startup hover clear does not need an unknown status when no aiming is pending");
        check(refuses([&]{avatar.GetStatusCode455();}),"startup clear does not fabricate a player status");
        RF455_NuclearAiming().pending=1;
        check(refuses([&]{startup.SetHoverObject(nullptr);})&&!startup.GetHoverObject(),"pending aiming still requires a known status before mutation");
        RF455_NuclearAiming().pending=0;
    }
    avatar.ApplyStatusFlags455(bit(17));
    check(refuses([&]{avatar.GetStatusCode455();}),"no subtype preserves unknown state");
    avatar.SetStatusCode455(0x12345678);avatar.ApplyStatusFlags455(bit(17)|bit(42));
    check(avatar.GetStatusCode455()==0x12345678,"bit17 preserves old DWORD and wins bit42 withoutsubtype");
    avatar.ApplyStatusFlags455(bit(16)|bit(17)|bit(33)|bit(42));
    check(avatar.GetStatusCode455()==10&&RF455_AvatarRequiresHoverCancel(),"bit16 priority");
    unsigned branches=0;
    for(unsigned n=33;n<=40;++n){
        avatar.ApplyStatusFlags455(bit(17)|bit(n)|bit(42));
        const unsigned expected=n-31;
        check(avatar.GetStatusCode455()==expected,"full-width flags select subtype");
        check(RF455_AvatarRequiresHoverCancel()==(expected==2||expected==6),"actual avatar subtype predicate");++branches;
    }
    avatar.ApplyStatusFlags455(bit(17)|bit(33)|bit(37)|bit(40));
    check(avatar.GetStatusCode455()==2,"first set subtype wins");
    avatar.ApplyStatusFlags455(bit(42));check(avatar.GetStatusCode455()==1,"bit42 without16/17");
    avatar.ApplyStatusFlags455(bit(63)|bit(40));check(avatar.GetStatusCode455()==0,"unrelated high bits");
    unsigned lowCases=0;
    for(DWORD code:{0u,1u,2u,3u,6u,9u,10u,255u,0x102u,0xffffff06u,0x1000au,0xffffffffu}){
        avatar.SetStatusCode455(code);const BYTE low=BYTE(code);
        check(avatar.GetStatusCode455()==code,"DWORD setter/getter");
        check(RF455_AvatarRequiresHoverCancel()==(low==2||low==6||low==10),"lowBYTE predicate");++lowCases;
    }
    // The existing ordinary setter also supplies the new state, without
    // truncating bit40. Its other legacy sideeffects are not accepted as455.
    avatar.SetServerStatusFlag(bit(17)|bit(40));
    check(avatar.GetStatusCode455()==9,"ordinary SetServerStatusFlag keeps64bits");
    avatar.SetServerStatusFlag(0);check(avatar.GetStatusCode455()==0,"ordinary status reset");
    CGUIItem icon;icon.SetObjectIndex455(33);CBoardObject source;source.SetIndex(33);source.SetIcon(&icon);
    CBoardManager manager;
    auto* hovered=manager.SetHoverObject(&source);
    check(hovered&&hovered!=&source&&gScreen.ExistObject(),"live ordinary avatar actual hover handoff");
    for(DWORD code:{2u,6u,10u,0x102u}){
        avatar.SetStatusCode455(code);
        check(!refuses([&]{manager.SetHoverObject(nullptr);})&&!manager.GetHoverObject()&&!gScreen.ExistObject(),"actual pending0 permits target-status hover clear");
        hovered=manager.SetHoverObject(&source);
        // The real aiming/world/effect/audio/message path has its own lab.
        // This CPU fixture deliberately has no language/message providers.
        RF455_NuclearAiming().pending=1;
        check(refuses([&]{manager.SetHoverObject(nullptr);})&&manager.GetHoverObject()==hovered&&gScreen.ExistObject(),"pending cancellation still refuses missing message providers before hover mutation");
        RF455_NuclearAiming().pending=0;
    }
    avatar.ApplyStatusFlags455(0);manager.SetHoverObject(nullptr);manager.ClearHoverBackups455();
    check(!manager.GetHoverObject()&&!gScreen.ExistObject(),"live ordinary avatar clears real hover andscreen");
    FILE* out=std::fopen("result.json","wb");check(out!=nullptr,"output");
    std::fprintf(out,"{\"status\":\"PASS\",\"checks\":%u,\"flag_subtypes\":%u,\"DWORD_lowBYTE_cases\":%u,\"actual_avatar\":true,\"ordinary_64bit_status_setter\":true,\"unknown_state_refusal\":true,\"stale_no_subtype\":true,\"actual_hover_and_screen\":true,\"pending_zero_allows_hover_clear\":true,\"nuclear_refusal_before_mutation\":true,\"full_nuclear_owner\":false,\"full_status_sideeffects\":false,\"full_455_wire_receivers\":false,\"full_client\":false}\n",checks,branches,lowCases);
    std::fclose(out);return 0;
}
static LONG filter(EXCEPTION_POINTERS* info){if(info->ExceptionRecord->ExceptionCode==0xe06d7363)return EXCEPTION_CONTINUE_SEARCH;std::fprintf(stderr,"exception=%08lx ownRVA=%08lx\n",info->ExceptionRecord->ExceptionCode,DWORD(info->ExceptionRecord->ExceptionAddress)-DWORD(GetModuleHandleA(nullptr)));return EXCEPTION_EXECUTE_HANDLER;}
static int guarded(){__try{return run();}__except(filter(GetExceptionInformation())){return 99;}}
int main(){try{return guarded();}catch(const std::exception& e){std::fprintf(stderr,"Player status:%s\n",e.what());return 1;}}
