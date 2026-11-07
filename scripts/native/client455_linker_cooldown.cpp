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
#include "client455_gui_input.h"
#include "client455_linker_cooldown.h"
#include <cstring>
#include <stdexcept>

DWORD& RF455_SFDelayGate455(){static DWORD gate=0;return gate;}
namespace {
RF455ItemDataSpan itemData(RF455ManagedItem& item){
    if(auto* basic=dynamic_cast<RF455BasicItem*>(&item))return basic->rawData();
    if(auto* sf=dynamic_cast<RF455SkillForceItem*>(&item))return sf->rawData();
    throw std::logic_error("455 cooldown needs the actual managed payload data owner");
}
DWORD itemCode(RF455ManagedItem& item){const auto data=itemData(item);if(!data.data)return 0xffffffff;if(data.size<8)throw std::out_of_range("455 item code outside data owner");DWORD code;std::memcpy(&code,data.data+4,4);return code;}
CObjectBoard* board(BYTE id){return dynamic_cast<CObjectBoard*>(_GetBoard(id));}
void start(CBoardObject* object,DWORD duration,LONG elapsed){
    if(!object)return;auto* icon=object->GetIcon();if(!icon)return;
    if(!object->GetItem455()||!icon->UsesTypedIcon455())throw std::logic_error("455 cooldown source board owner is still legacy");
    icon->BeginDelayAnimation455(duration,elapsed);
}
}
CBoardObject* CLinkBoard::FindOriginalTyped455(RF455ManagedItem& item,BOOL equal){
    BYTE ids[3]={255,255,255};const BYTE kind=item.header().kind;
    if(kind==0){ids[0]=1;ids[1]=0;if(!equal)ids[2]=5;}
    else if(kind==1){auto* sf=dynamic_cast<RF455SkillForceItem*>(&item);if(!sf)throw std::logic_error("455 SF owner missing");ids[0]=sf->record().subtype==1?3:7;}
    else if(kind==2)ids[0]=4;else if(kind==6)ids[0]=22;else if(kind==7)ids[0]=35;
    for(BYTE id:ids)if(id!=255){auto* source=board(id);if(!source)continue;
        if(!equal&&kind!=0){for(BYTE bank=0;bank<source->GetMaxPackNum();++bank)for(BYTE slot=0;slot<source->GetMaxSocketNum455(bank);++slot){auto* found=source->GetObject(bank,slot);if(found&&found->GetItem455()==&item)return found;}}
        else if(auto* found=source->GetObjectByIndex(item.header().serial))return found;
    }return nullptr;
}
void CLinkBoard::BeginTypedDelay455(RF455ManagedItem& item,DWORD duration,LONG elapsed){
    if(RF455_SFDelayGate455()&&item.isKind(1))return;
    if(m_byMaxPackNum>5)throw std::out_of_range("455 cooldown bank count outside fixed fifty slots");
    const auto code=itemCode(item);
    for(BYTE bank=0;bank<m_byMaxPackNum;++bank)if(m_uiLinkWindow.IsAddedObject(m_uiLinkWindow.Control455(6,bank))||m_uiLinkWindow.HotbarState455().active==bank){
        const auto count=m_listItemPack[bank].GetMaxSocketNum();if(count>10)throw std::out_of_range("455 cooldown slots outside fixed fifty owners");
        for(BYTE slot=0;slot<count;++slot){auto& record=m_linkerCooldown455.records[static_cast<BYTE>(slot+count*bank)];if(record.object)continue;auto* object=GetObject(bank,slot);if(!object)continue;auto* candidate=object->GetItem455();
            if(candidate&&candidate->header().kind==item.header().kind&&itemCode(*candidate)==code&&object->GetIndex()==item.header().serial){record.bank=bank;record.object=object;record.startedAt=RF455_GuiInputTime();record.elapsedOffset=elapsed==-1?0:static_cast<DWORD>(elapsed);record.duration=duration;}}
    }
    if(item.isKind(1)){
        auto* sf=dynamic_cast<RF455SkillForceItem*>(&item);if(!sf)throw std::logic_error("455 SF delay owner missing");const auto subtype=sf->record().subtype;
        if(subtype==2){start(FindOriginalTyped455(item,TRUE),duration,elapsed);return;}
        const auto data=sf->rawData();if(!data.data)return;if(data.size<=15)throw std::out_of_range("455 SF delay group outside data owner");
        BYTE pack=data.data[12];if(subtype==1)pack=pack<2?0:pack<6?BYTE(pack-1):BYTE(255);
        auto* originalBoard=board(subtype==1?3:7);if(!originalBoard)return;
        const BYTE count=originalBoard->GetMaxSocketNum455(pack);for(BYTE slot=0;slot<count;++slot){auto* object=originalBoard->GetObject(pack,slot);if(!object)continue;auto* payload=object->GetItem455();if(!payload)throw std::logic_error("455 SF delay pack still uses legacy payloads");const auto row=itemData(*payload);
            if(!row.data)continue;if(row.size<=15)throw std::out_of_range("455 SF source delay group outside data owner");if(row.data[15]==data.data[15])start(object,duration,elapsed);}
    }else start(FindOriginalTyped455(item,item.isKind(7)?FALSE:TRUE),duration,elapsed);
}
void CLinkBoard::RemoveCooldownObject455(CBoardObject* object){for(auto& record:m_linkerCooldown455.records)if(record.object==object){record.object=nullptr;record.startedAt=0;}}
void CLinkBoard::ProcessCooldowns455(){
    for(auto& record:m_linkerCooldown455.records)if(record.object){const DWORD elapsed=record.elapsedOffset+RF455_GuiInputTime()-record.startedAt;if(elapsed>=record.duration){
        if(m_uiLinkWindow.IsAddedObject(m_uiLinkWindow.Control455(6,record.bank))||m_uiLinkWindow.HotbarState455().active==record.bank){if(auto* icon=record.object->GetIcon()){
            auto& cue=icon->ReadyCue455();if(!cue.ReadyConfigured455())throw std::logic_error("455 cooldown icon has no configured ready animation");m_uiLinkWindow.Add(&cue);cue.SetFrame455(0,FALSE);m_linkerCooldown455.pending.push_back(&cue);}}
        std::memset(&record,0,sizeof(record));}}
    // Target erases to next,then increments again. Explicitly model its
    // sentinel-next wrap instead of relying on ++std::list::end() undefinedness.
    auto& pending=m_linkerCooldown455.pending;for(auto it=pending.begin();it!=pending.end();){
        if((*it)->State455().stopped){m_uiLinkWindow.Remove(*it);it=pending.erase(it);if(it==pending.end()){if(!pending.empty())it=pending.begin();}else ++it;}
        else ++it;
    }
}
