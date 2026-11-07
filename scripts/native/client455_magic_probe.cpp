#include "addcodebyjang/cmagicscript.h"
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
#include "addcodebyjang/effectcore.h"
#include "addcodebyjang/effectentitylist.h"
#include "client455_resource_io.h"
#include "jmalloc.h"
#include <cstdio>
#include <cstring>
#include <cstddef>
#include <cmath>
#include <stdexcept>
static_assert(sizeof(_MAGIC_TRACK)==46,"track46");
static_assert(sizeof(CProcessMagic)==3004,"process3004");
static_assert(offsetof(CProcessMagic,mState)==4&&offsetof(CProcessMagic,mCreateType)==8&&offsetof(CProcessMagic,mIsLoaded)==12,"magic prefix");
static_assert(offsetof(CProcessMagic,mTrackNum)==16&&offsetof(CProcessMagic,m_control455)==36&&offsetof(CProcessMagic,mMagicTrack)==60,"magic prefix2");
static_assert(offsetof(CMagicList,mMagicPtr)==344,"runtime magic pointer");
static unsigned checks=0,warnings=0;
static void check(bool value,const char* message){++checks;if(!value)throw std::runtime_error(message);}
static void warning(char*){++warnings;}
static void cleanup(RF455MagicControl& value){auto* node=value.first;while(node){auto* next=node->next;delete node;node=next;}std::memset(&value,0,sizeof(value));}
static int run(){
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX|SEM_NOOPENFILEERRORBOX);
    std::fprintf(stderr,"layout:runtime=%u effectInfo=%u eInfoOffset=%u yOffset=%u\n",unsigned(sizeof(CMagicList)),unsigned(sizeof(EffectInfo)),unsigned(offsetof(CMagicList,mEInfo)),unsigned(offsetof(CMagicList,mYOldAngle)));
    check(sizeof(CMagicList)==456,"runtime456");
    EffectInfo initial;unsigned char expectedInfo[56]={};std::memset(expectedInfo,255,24);expectedInfo[37]=255;std::memset(expectedInfo+52,255,4);
    check(sizeof(initial)==56&&!std::memcmp(&initial,expectedInfo,56),"whole EffectInfo56 constructor includingtail");
    initial.unknown48_455=123;initial.unknown52_455=456;initial.SetMyself(nullptr);initial.SetTarget(nullptr);
    check(initial.unknown48_455==123&&initial.unknown52_455==456,"existing effect setters preserve newtail");
    InitR3Engine();SetWarningMessageProc(warning);const auto baseline=GetDmallocSize();
    RF455_RpkGroup group;group.LoadDirectory(".\\Effect\\");check(group.count==1,"actual archive group");auto* previous=RF455_SetResourceGroup(&group);
    CreateEffectsList(".\\Effect\\EffectEntityList.spt");CreateMagicSptList(".\\Effect\\MagicSptList.spt");
    check(IsExistFromMagicSpt(1358041136)!=0,"actual cue mapping");
    CProcessMagic cue;std::memset(&cue,0,sizeof(cue));cue.mFlag=0x12345678;cue.mState=0xabcdef55;
    cue.CreateMagicTrack(GetFilenameFromMagicSpt(1358041136));
    check(cue.IsLoaded()&&cue.mTrackNum==6&&cue.mSpeed==100&&cue.mCreateType==10,"actual RPK cue parsed andstoppedatend");
    check(cue.mFlag==0x12345678&&cue.mState==0xabcdef55&&!cue.mAxisType455&&!cue.mAxisInfo455,"parser partialwrites");
    const unsigned ids[6]={90061,90063,90062,90066,90065,90064};const float times[6]={0,0,.2f,.2f,.3f,.4f},scales[6]={2,6,10,2,2,2},ys[6]={0,0,0,10,12,14};
    for(unsigned i=0;i<6;++i){
        _MAGIC_TRACK expected={};expected.Flag=i?0x20:0x110;expected.Time=times[i];expected.Pos[1]=ys[i];expected.EntityID=GetRealID(ids[i]);expected.Scale=scales[i];expected.Color=0xff46a920;expected.AlphaApear=i==2?.3f:0;
        check(!std::memcmp(&expected,&cue.mMagicTrack[i],46),"whole packed track matches actual cue fields");
    }
    LONG start=99;check(cue.GetEntityIDs(0,0,&start)==-1&&start==99,"time zero doesnot fire");
    check(cue.GetEntityIDs(0,1,&start)==2&&start==0,"two timezero tracks");
    check(cue.GetEntityIDs(6,7,&start)==2&&start==2,"inclusive old/exclusive new endpoint");
    check(cue.GetEntityIDs(7,8,&start)==-1,"no new track");
    check(cue.GetEntityIDs(12,13,&start)==1&&start==5,"lasttrack boundary");
    check(cue.GetEntityIDs(13,14,&start)==-2,"finished cue");
    CProcessMagic empty;std::memset(&empty,0,sizeof(empty));empty.mState=0xaabbccdd;
    check(empty.GetEntityIDs(0,1,&start)==-2&&empty.mState==0xaabbcc00,"empty selector clears onlylowBYTEstate");
    empty.mTrackNum=1;empty.mMagicTrack[0].Time=std::nanf("");check(empty.GetEntityIDs(0,1,&start)==-2,"unordered final comparison");
    CProcessMagic fields;std::memset(&fields,0,sizeof(fields));fields.CreateMagicTrack("fields.spt");
    check(fields.mTrackNum==1&&fields.mAxisType455==2&&fields.mAxisInfo455==3&&fields.mMagicTrack[0].Flag==0x1840,"newaxis/blur/duplicatebillboard flags");
    check(fields.mMagicTrack[0].QuakeTime==2&&fields.mMagicTrack[0].QuakeDensity==.25f,"screen blur aliases");
    check(fields.mMagicTrack[61].Rand1[0]==-2&&fields.mMagicTrack[61].Rand2[0]==2&&fields.mMagicTrack[63].Rand1[2]==13,"reserved controls61..63");
    auto& control=fields.m_control455;check(control.count==3&&control.multiple==3&&control.angle==15&&control.delay==1000,"parabola/multi metadata");
    check(control.first->flags==7&&control.first->angle==90&&control.first->curve==2&&control.first->end==.4f,"firstcurve andclamp");
    check(control.first->next->begin==.4f&&control.first->next->end==.8f&&control.first->next->curve==-3&&control.last->previous==control.first->next,"insertbeforetail");
    check(control.last->begin==.8f&&control.last->end==1&&control.last->angle==12&&control.last->curve==5,"tailoverwrite");
    auto* old=control.first;fields.DestoryMagicTrack();check(control.first==old,"target empty Destroy leavescontrolnodes");cleanup(control);
    CProcessMagic boundary;std::memset(&boundary,0,sizeof(boundary));boundary.CreateMagicTrack("boundary.spt");
    check(boundary.mTrackNum==64&&boundary.mMagicTrack[63].Time==63,"64 actual track slots");
    bool refused=false;try{boundary.CreateMagicTrack("overflow.spt");}catch(const std::out_of_range&){refused=true;}
    check(refused&&boundary.mTrackNum==64,"65thtrack explicitrefusal beforeoutofbounds");
    float pos[3]={1,2,3};const DWORD instance=StartMagicEffect(pos,0,1358041136,nullptr,_EF_STATE_ALWAYS_LIVE);
    auto* runtime=GetMagicListFromID(instance);check(instance&&runtime&&runtime->mEntityUniqueIDCnt==6&&runtime->mState==1,"ordinary magic cache createsreal RPK cue");
    auto* cached=static_cast<CProcessMagic*>(runtime->mMagicPtr);check(cached&&cached->mTrackNum==6&&cached->mCreateType==10,"actual cached process3004");
    check(SetDisapearTimeMagicEffect(instance,0)&&runtime->mState==2,"ordinary disappear updatesreal runtime owner");
    ResetEffectManager();DestroyEffectsList();DestroyMagicSptList();RF455_SetResourceGroup(previous);group.Release();
    check(GetDmallocSize()==baseline,"resource/cache/table allocations released");ReleaseR3Engine();
    FILE* out=std::fopen("result.json","wb");check(out!=nullptr,"output");
    std::fprintf(out,"{\"status\":\"PASS\",\"checks\":%u,\"warnings\":%u,\"process_bytes\":3004,\"runtime_bytes\":456,\"track_bytes\":46,\"maximum_tracks\":64,\"real_RPK_cue_tracks\":6,\"packed_tracks_equal\":true,\"actual_entity_mapping\":true,\"ordinary_cache_start_disappear\":true,\"selector_boundaries_and_NaN\":true,\"control_nodes_and_multi\":true,\"all_allocations_released\":true,\"full_effect_rendering\":false,\"full_nuclear_aiming\":false,\"full_client\":false}\n",checks,warnings);std::fclose(out);return 0;
}
static LONG filter(EXCEPTION_POINTERS* p){if(p->ExceptionRecord->ExceptionCode==0xe06d7363)return EXCEPTION_CONTINUE_SEARCH;std::fprintf(stderr,"exception=%08lx ownRVA=%08lx\n",p->ExceptionRecord->ExceptionCode,DWORD(p->ExceptionRecord->ExceptionAddress)-DWORD(GetModuleHandleA(nullptr)));return EXCEPTION_EXECUTE_HANDLER;}
static int guarded(){__try{return run();}__except(filter(GetExceptionInformation())){return 99;}}
int main(){try{return guarded();}catch(const std::exception& e){std::fprintf(stderr,"Magic:%s\n",e.what());return 1;}}
