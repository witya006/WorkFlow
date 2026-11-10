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
#include "client455_equipment_effects.h"
#include "client455_player_equipment.h"
#include "client455_effect_positions.h"
#include "client455_nation_paths.h"
#include "client455_language.h"
#include <memory>
#include "client455_tagged_audio.h"
#include "r3sound.h"
#include "mss.h"
#include <cstdio>
#include <cstring>
#include <stdexcept>
#include <string>
#include <vector>
extern CMainApp g_MainApp;
static void require(bool value,const char* reason){if(!value)throw std::runtime_error(reason);}
static void warning(char* text){std::fprintf(stderr,"warning:%s\n",text);}
class EffectActor146:public CAvatar {
public:
    void snapshot(BYTE walk,DWORD action){m_byWalkMode=walk;m_dwActionID=action;}
    void bind(CBone* bone,BBOX* box){m_pBone=bone;m_pBBox=box;}
};
class Effects146:public RF455EquipmentEffectBackend {
public:
    const RF455EffectPositionView* view=nullptr;
    RF455TaggedAudio& audio=g_MainApp.TaggedAudio455();RF455LoopSoundRegistry loops;RF455EquipmentSoundGate gate;
    EffectActor146* local=nullptr;unsigned starts=0,expires=0,plays=0,stops=0,tracked=0,untracked=0;
    std::vector<std::string> events;
    bool effectExists(std::uint32_t id)override{events.push_back("exists");return IsExistFromMagicSpt(id)!=0;}
    void expireMagic(std::uint32_t id,float delay)override{events.push_back("expire");require(delay==0,"Actual fade delay");SetDisapearTimeMagicEffect(id,delay);++expires;}
    std::uint32_t startMagic(const RF455EquipmentEffectOwner& owner,std::uint32_t id,bool flag)override{
        events.push_back("start");float pos[3];std::memcpy(pos,owner.position,12);
        //Actual magic/cache lifecycle. The target's additional bone/dummy
        //creation-position provider is deliberately still unclaimed here.
        auto unique=view?RF455_StartMagicAtActor(*view,pos,owner.yaw,id,nullptr,flag?1:0):StartMagicEffect(pos,owner.yaw,id,nullptr,flag?1:0);if(unique)++starts;return unique;
    }
    RF455EquipmentEffectLocal localActor()override{
        events.push_back("local");if(!local)return {};
        RF455EquipmentEffectLocal value;value.index=local->GetIndex();value.action=local->GetAction();value.walkMode=local->GetWalkMode();return value;
    }
    void playWave(std::uint32_t id,const float* pos,std::uint32_t loop)override{
        events.push_back("play"+std::to_string(loop));++plays;
        gate.play(id,pos,loop,[](){return static_cast<double>(R3GetTime());},[&](std::uint32_t key,const float* at,std::uint32_t repeat){audio.Play(key,repeat,0,at);});
    }
    void stopWave(std::uint32_t id,std::uint32_t tag)override{events.push_back("stop");++stops;audio.Stop(id,tag);}
    void trackLoop(std::uint32_t id,std::uint32_t tag)override{events.push_back("track");++tracked;loops.add(id,tag);}
    void untrackLoop(std::uint32_t id,std::uint32_t tag)override{
        events.push_back("untrack");++untracked;loops.remove(id,tag,[&](std::uint32_t key,std::uint32_t token){stopWave(key,token);});
    }
};
#include "client455_equipment_frame_probe.inc"
static int run(){
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX|SEM_NOOPENFILEERRORBOX);
    InitR3Engine();SetWarningMessageProc(warning);auto* engine=GetR3State();engine->mSoundOn=TRUE;SetGlobalWavVolume(0);RF455_PrepareTaggedAudio(engine->SoundPath);
    require(InitR3SoundSystem(".\\Snd\\WaveList.spt")!=0,"Actual Miles digital driver");
    Effects146 backend;require(backend.audio.Open(".\\Snd\\WaveList.spt",engine->SoundPath),"Actual tagged audio owner");backend.loops.open();
    const float listener[3]={0,0,0};backend.audio.SetListener(listener);
    RF455_RpkGroup group;group.LoadDirectory(".\\Effect\\");require(group.count==2,"Two actual cloak/empty magic archives");
    auto* previous=RF455_GetResourceGroup();RF455_SetResourceGroup(&group);
    CreateEffectsList(".\\Effect\\EffectEntityList.spt");CreateMagicSptList(".\\Effect\\MagicSptList.spt");
    EffectActor146 actor;actor.SetIndex(7);actor.SetRace(0);actor.SetPosition(20,40,60);actor.snapshot(0,0x10000000);backend.local=&actor;
    RF455EquipmentEffectOwner owner;owner.object=&actor;owner.index=actor.GetIndex();owner.race=actor.GetRace();owner.position=actor.GetPosition();owner.yaw=actor.GetRotY();
    const float equipmentPosition[3]={7,9,11};
    RF455EquipmentEffectState state;state.process(owner,equipmentPosition,0x700600,8,true,3,backend);
    require(state.magic&&GetMagicListFromID(state.magic)&&state.sound==0x50006000&&backend.loops.size()==1,"Actual cloak effect/cache and tracked loop");
    require(backend.events==std::vector<std::string>({"exists","start","local","play1","track"}),"Target effect-before-local/audio ordering");
    auto playing=backend.audio.Inspect(state.sound);require(playing.sample&&AIL_3D_sample_status(static_cast<H3DSAMPLE>(playing.sample))==SMP_PLAYING&&AIL_3D_sample_loop_count(static_cast<H3DSAMPLE>(playing.sample))==0,"Actual looped cloak WAV");
    require(playing.relative[0]==7&&playing.relative[1]==9&&playing.relative[2]==11,"46D3D0 sound uses equipment position,not actor position");
    const DWORD old=state.magic;backend.events.clear();state.process(owner,equipmentPosition,0x700600,8,false,4,backend);
    require(GetMagicListFromID(old)&&GetMagicListFromID(old)->mState==2&&state.magic&&state.sound==0&&backend.loops.size()==0,"Old magic expires andloop is untracked before replacement");
    require(backend.events.size()>=7&&backend.events[0]=="expire"&&backend.events[1]=="stop"&&backend.events[2]=="untrack"&&backend.events[3]=="stop"&&backend.events[4]=="exists"&&backend.events[5]=="start","Actual duplicate stop through loop removal");
    auto stopped=backend.audio.Inspect(0x50006000);require(!stopped.sample||AIL_3D_sample_status(static_cast<H3DSAMPLE>(stopped.sample))!=SMP_PLAYING,"Actual previous sample stopped");
    state.process(owner,equipmentPosition,0x700600,8,true,5,backend);require(state.magic==0,"Actual empty unuse script produces no runtime magic");
    backend.events.clear();backend.local=nullptr;state.process(owner,equipmentPosition,0x700600,8,true,3,backend);
    require(state.magic&&state.sound==0&&backend.events==std::vector<std::string>({"exists","start","local"}),"Invalid local avatar checked after creating magic");state.clear(backend);
    backend.local=&actor;owner.index=8;backend.events.clear();state.process(owner,equipmentPosition,0x700600,8,true,3,backend);
    require(state.magic&&!state.sound&&backend.events==std::vector<std::string>({"exists","start","local"}),"Remote attack mode does not start cloak sound");state.clear(backend);
    owner.index=actor.GetIndex();actor.snapshot(2,0x10000001);backend.loops.add(0x50006003,0);backend.events.clear();state.process(owner,equipmentPosition,0x700600,8,false,2,backend);
    require(!state.magic&&!state.sound&&backend.loops.size()==0&&backend.events==std::vector<std::string>({"exists","local","play0","untrack","stop"}),"Unequip removes the next tracked sound for walk2/action10000001");
    RF455EquipmentEffectState preserved;preserved.magic=123;auto absent=owner;absent.object=nullptr;backend.events.clear();preserved.process(absent,equipmentPosition,0,8,false,3,backend);require(preserved.magic==123&&backend.events.empty(),"Null owner does not clear existing state");
    RF455LoopSoundRegistry tracker;tracker.open();std::vector<DWORD> ended;auto stop=[&](DWORD id,DWORD tag){ended.push_back(id);backend.audio.Stop(id,tag);};
    tracker.add(100,1);tracker.add(200,2);tracker.add(100,1);require(tracker.size()==2&&tracker.row(0).count==1,"Tracked duplicate suppressed");
    require(tracker.remove(100,1,stop)&&tracker.size()==1,"First group compaction");tracker.add(300,3);
    require(tracker.row(1).count==2&&tracker.row(1).tags[0]==2&&tracker.row(1).tags[1]==3,"Reused physical last row retains its previous count/tag");
    tracker.stopAll(stop);require(tracker.size()==2&&tracker.row(0).id==0&&tracker.row(0).count==1&&tracker.row(1).id==0&&tracker.row(1).count==2,"Stop-all zeroes IDs only");
    tracker.open();for(unsigned tag=0;tag<30;++tag)tracker.add(277034,tag);tracker.add(277034,31);require(tracker.row(0).count==30,"Existing sound group cap30");
    state.clear(backend);backend.loops.stopAll([&](DWORD id,DWORD tag){backend.audio.Stop(id,tag);});backend.loops.close();
    runEquipmentFrames153(backend);
    ResetEffectManager();DestroyEffectsList();DestroyMagicSptList();RF455_SetResourceGroup(previous);group.Release();backend.audio.Close();ReleaseR3SoundSystem();ReleaseR3Engine();
    FILE* output=std::fopen("result.json","wb");require(output,"Output");std::fprintf(output,"{\"status\":\"PASS\",\"actual_magic_starts\":%u,\"actual_magic_expires\":%u,\"wave_requests\":%u,\"sample_stops\":%u,\"tracked_adds\":%u,\"tracked_removes\":%u,\"real_cloak_WAV_loop_and_stop\":true,\"physical_row_retention\":true,\"stop_all_preserves_counts\":true,\"creation_position_provider_pending\":true,\"ordinary_player_connected\":false,\"full_conditions\":false,\"full_appearance\":false}\n",backend.starts,backend.expires,backend.plays,backend.stops,backend.tracked,backend.untracked);std::fclose(output);return 0;
}
int main(){try{return run();}catch(const std::exception& error){std::fprintf(stderr,"Equipment effects146:%s\n",error.what());return 2;}}
