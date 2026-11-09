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
#include "addcodebyjang/effectcore.h"
#include "client455_nuclear_registry.h"
#include "client455_language.h"
#include "client455_message_dispatch.h"
#include <mmsystem.h>
#include <cstring>

extern CMainApp g_MainApp;
namespace {
WORD key(BYTE race,BYTE index){return static_cast<WORD>((DWORD(race)<<8)|index);}
RF455NuclearCountdownClock processClock;
RF455NuclearContainer* currentContainer=nullptr;
void radar(RF455NuclearRecord& record,BOOL on){
    if(on){
        if(record.radar){SetDisapearTimeMagicEffect(record.radar,0);record.radar=0;}
        record.radar=StartMagicEffect(record.position,0,1358041136,nullptr,_EF_STATE_ALWAYS_LIVE);
        g_MainApp.TaggedAudio455().PlayAtListener(277034,1,2);GetR3State()->mDynamicLight=3;
    }else{
        if(record.radar){SetDisapearTimeMagicEffect(record.radar,0);record.radar=0;}
        g_MainApp.TaggedAudio455().Stop(277034,2);
    }
}
void reset(RF455NuclearRecord& record){
    // Clear stops the shared tag before disappearing radar, even handle0.
    // Launch/impact are detached, not killed; position/countdown are retained.
    g_MainApp.TaggedAudio455().Stop(277034,2);SetDisapearTimeMagicEffect(record.radar,0);
    record.radar=0;record.launch=0;record.impact=0;
}
bool zeroPosition(const RF455NuclearRecord& record){return record.position[0]==0&&record.position[1]==0&&record.position[2]==0;}
}
RF455NuclearContainer* RF455_GetNuclearContainer(){return currentContainer;}
void RF455_BindNuclearContainer(RF455NuclearContainer* value){currentContainer=value;}
void RF455_UnbindNuclearContainer(RF455NuclearContainer* value){if(currentContainer==value)currentContainer=nullptr;}
RF455NuclearContainer& RF455_NuclearContainer(){if(!currentContainer)throw std::logic_error("455 nuclear stage owner unavailable");return *currentContainer;}
void CGP_MainGame::ReleaseNuclear455(){
    auto* owned=m_nuclear455.get();if(!owned)return;
    m_nuclear455.reset();RF455_UnbindNuclearContainer(owned);
}
RF455NuclearContainer::~RF455NuclearContainer(){ClearAll();}
const RF455NuclearRecord* RF455NuclearContainer::Find(BYTE race,BYTE index)const{
    const auto found=records.find(key(race,index));return found==records.end()?nullptr:found->second.get();
}
RF455NuclearRecord* RF455NuclearContainer::FindMutable(BYTE race,BYTE index){return const_cast<RF455NuclearRecord*>(Find(race,index));}
const float* RF455NuclearContainer::Position(BYTE race,BYTE index)const{const auto* record=Find(race,index);return record?record->position:nullptr;}
BOOL RF455NuclearContainer::Add(BYTE race,BYTE index){
    const WORD id=key(race,index);if(records.find(id)!=records.end())return FALSE;
    records.emplace(id,std::unique_ptr<RF455NuclearRecord>(new RF455NuclearRecord));return TRUE;
}
BOOL RF455NuclearContainer::Remove(BYTE race,BYTE index){
    aiming.SetPending(0);auto found=records.find(key(race,index));if(found==records.end())return FALSE;
    radar(*found->second,FALSE);records.erase(found);return TRUE;
}
BOOL RF455NuclearContainer::ResetRecords(){
    aiming.SetPending(0);if(records.empty())return FALSE;
    for(auto& entry:records)reset(*entry.second);return TRUE;
}
BOOL RF455NuclearContainer::ClearAll(){ResetRecords();if(records.empty())return FALSE;records.clear();return TRUE;}
BOOL RF455NuclearContainer::SetPosition(BYTE race,BYTE index,const float* value){
    auto* record=FindMutable(race,index);if(!record)return FALSE;
    for(unsigned i=0;i<3;++i)record->position[i]=value[i];return TRUE;
}
BOOL RF455NuclearContainer::Launch(BYTE race,BYTE index){
    auto* record=FindMutable(race,index);if(!record)return FALSE;
    if(zeroPosition(*record))RF455_ShowSystemMessage("Not Nuclear Posion");
    else{record->launch=StartMagicEffect(record->position,90,1358041392,nullptr,_EF_STATE_AUTO_DISAPEAR);g_MainApp.TaggedAudio455().PlayAtListener(277036,0,0);GetR3State()->mDynamicLight=3;}
    return TRUE;
}
BOOL RF455NuclearContainer::Impact(BYTE race,BYTE index){
    auto* record=FindMutable(race,index);if(!record)return FALSE;
    if(zeroPosition(*record))RF455_ShowSystemMessage("Not Nuclear Posion");
    else{record->impact=StartMagicEffect(record->position,90,1358041648,nullptr,_EF_STATE_AUTO_DISAPEAR);g_MainApp.TaggedAudio455().PlayAtListener(277038,0,0);GetR3State()->mDynamicLight=3;}
    return TRUE;
}
BOOL RF455NuclearContainer::Radar(BYTE race,BYTE index,BOOL on){auto* record=FindMutable(race,index);if(!record)return FALSE;radar(*record,on);return TRUE;}
BOOL RF455NuclearContainer::NotifyRace(BYTE race,BYTE index){
    if(!Find(race,index))return FALSE;auto* language=RF455_GetNormalLanguagePack();RF455_ShowSystemMessage(language->get(0xc15),race<3?language->get(race):"");return TRUE;
}
BOOL RF455NuclearContainer::SetCountdown(BYTE race,BYTE index,DWORD value){auto* record=FindMutable(race,index);if(!record)return FALSE;record->countdown=value;return TRUE;}
void RF455NuclearContainer::FrameMove(){
    for(auto& entry:records)processClock.Tick(entry.second->countdown,[](){return timeGetTime();},[](DWORD count){RF455_ShowSystemMessage(RF455_GetNormalLanguagePack()->get(0xc17),count);});
    aiming.FrameMove();
}
