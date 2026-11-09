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
#include <client455_character_flags.h>
#include <mmsystem.h>
#include <array>
#include <cstdio>
#include <stdexcept>
#include <vector>
extern CMainApp g_MainApp;
static unsigned checks=0,ticks=0;static RF455CharacterFlags* ticking=nullptr;static DWORD expectedBefore=0;
static void check(bool value,const char* why){++checks;if(!value)throw std::runtime_error(why);}
static std::uint32_t clock455(){check(ticking&&ticking->value==expectedBefore,"flag1 clock precedes OR store");return 0xfffffff0u+32u*ticks++;}
template<class Tag,typename Tag::Type Member>struct MemberAccess{friend typename Tag::Type access(Tag){return Member;}};
struct Network{using Type=CNetworkMgr CMainApp::*;friend Type access(Network);};template struct MemberAccess<Network,&CMainApp::m_cNetworkMgr>;
struct Action{using Type=DWORD CCharacter::*;friend Type access(Action);};template struct MemberAccess<Action,&CCharacter::m_dwActionID>;
static int run(){
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX|SEM_NOOPENFILEERRORBOX);
    RF455CharacterFlags state;check(!state.value&&!state.touchedKnown&&!state.blocked(0xffffffff)&&state.none(0)&&!state.any(0),"confirmed constructor flags0,any/none0");
    ticking=&state;expectedBefore=0;state.enable(1,clock455);check(state.value==1&&state.touchedKnown&&state.touchedAt==0xfffffff0,"flag1 clock");expectedBefore=1;state.enable(1,clock455);check(state.touchedAt==16&&ticks==2,"DWORD clock wrap/repeated flag1 still timestamps");
    state.disable(1);check(!state.value&&state.touchedAt==16,"clear retains clock");state.enable(2,nullptr);check(state.value==2&&!state.none(3)&&state.none(1)&&state.any(3),"none is not all-bits comparison");state.toggle(2,false,nullptr);state.toggle(0x80000000,true,nullptr);check(state.value==0x80000000&&!state.blocked(0x10000000),"unrelated highbit preserved without clock");
    bool rejected=false;try{state.enable(1,nullptr);}catch(const std::logic_error&){rejected=true;}check(rejected&&state.value==0x80000000,"unknown clock rejects before flag mutation");
    struct Case {DWORD initial,action;std::uint64_t wire;DWORD result,finalAction;bool cached;std::vector<DWORD> changes;};
    const std::array<Case,8> cases={{
        {0,0x10000000,0,0x60000,0x10000000,false,{}},
        {2,0x50000001,0,0x60000,0x10000000,false,{0x10000000}},
        {3,0x50000001,std::uint64_t(1)<<5,0x60001,0x50000001,true,{}},
        {0,0x10000000,std::uint64_t(1)<<19,0x60002,0x50000001,false,{0x50000001}},
        {0,0x50000001,std::uint64_t(1)<<19,0x60000,0x50000001,true,{}},
        {1,0x10000000,0,0x60000,0x10000000,false,{}},
        {0,0x10000000,std::uint64_t(1)<<5,0x60000,0x50000001,false,{0x50000001}},
        {0x80000000,0x10000000,(std::uint64_t(1)<<14)|(std::uint64_t(1)<<15),0x80000000,0x10000000,false,{}}
    }};
    for(const auto& row:cases){
        RF455CharacterFlags flags;flags.value=row.initial;DWORD action=row.action;std::vector<DWORD> observed;const auto before=ticks;
        const bool cached=flags.applyServer(row.wire,[&]{return action;},[&](DWORD next,bool duplicate){check(!duplicate,"target control action duplicate checkFALSE");observed.push_back(next);action=next;},clock455);
        check(flags.value==row.result&&action==row.finalAction&&cached==row.cached&&observed==row.changes&&ticks==before,"target-derived ordered control/action trace");
    }
    auto& network=g_MainApp.*access(Network{});check(network.Create()!=0,"actual offline NetworkMgr Create");
    {
        CAvatar avatar;check(avatar.CharacterFlags455()==0,"actual source Avatar owns ctor0");rejected=false;try{avatar.CharacterFlagTime455();}catch(const std::logic_error&){rejected=true;}check(rejected,"own motion clock remains unknown before producer");
        const DWORD masks[]={0,1,2,3,4,0x20000,0x40000,0x80000000};
        for(DWORD mask:masks){
            avatar.DisableCharacterFlags455(0xffffffff);avatar.EnableCharacterFlags455(mask);check(avatar.CharacterFlags455()==mask,"actual enable/clear wrappers");
            if(mask&1){const auto now=timeGetTime();check(now-avatar.CharacterFlagTime455()<10000,"actual flag1 uses WinMM clock");}
            for(DWORD high=0;high<16;++high){avatar.*access(Action{})=(high<<28)|0x1234567;const bool expected=high==5||(mask&3)!=0;check(!!avatar.IsDeath()==expected,"ordinary source IsDeath uses action highnibble OR internal bits1/2");}
            check(!!avatar.AnyCharacterFlags455(3)==((mask&3)!=0)&&!!avatar.NoneCharacterFlags455(3)==((mask&3)==0),"actual any/none methods");
        }
        avatar.DisableCharacterFlags455(0xffffffff);avatar.*access(Action{})=0xffffffff;avatar.SetServerStatusFlag((ULONGLONG(1)<<17)|(ULONGLONG(1)<<40));
        check(avatar.CharacterFlags455()==0x60000&&avatar.GetStatusCode455()==9&&!avatar.IsDeath(),"ordinary64bit server producer separates internal flags from player status");
        avatar.ToggleCharacterFlags455(2,7);check(avatar.IsDeath()&&avatar.AnyCharacterFlags455(2),"actual nonzero BOOL toggle");avatar.ToggleCharacterFlags455(2,FALSE);check(!avatar.IsDeath(),"actual toggle clear");
    }
    network.Destroy();FILE* out=std::fopen("result.json","wb");check(out!=nullptr,"result");std::fprintf(out,"{\"status\":\"PASS\",\"checks\":%u,\"target_trace_cases\":8,\"actual_Avatar\":true,\"actual_ordinary_IsDeath\":true,\"action_highnibbles\":16,\"internal_masks\":8,\"any_none_semantics\":true,\"source_flag_clock\":true,\"ordinary64bit_producer\":true,\"control_before_status\":true,\"action_transitions_kernel_only\":true,\"full_movement_controller\":false,\"full_action_pipeline\":false,\"full_455_status_writer\":false,\"normal_nuclear_receiver\":false,\"full_client\":false}\n",checks);std::fclose(out);return 0;
}
int main(){try{return run();}catch(const std::exception& error){std::fprintf(stderr,"Character flags:%s checks=%u\n",error.what(),checks);return 1;}}
