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
#include "client455_linker_owners.h"
#include "client455_icon_links.h"
#include "client455_item_icon_metadata.h"
#include <cstring>
#include <memory>
#include <stdexcept>

BOOL RF455LinkerIconSlots::takeIn(BYTE bank,BYTE slot,CGUIItem* source){
    auto* icon=get(bank,slot);if(!icon||!source)return FALSE;
    icon->SetData(source);
    //61AA10 finishes by reapplying the destination position to its children.
    icon->SetPos(icon->m_ptPos.x,icon->m_ptPos.y);
    icon->SetSize(Size455(),Size455());icon->SetRefItem(nullptr);return TRUE;
}
BOOL RF455LinkerIconSlots::takeOut(BYTE bank,BYTE slot){
    auto* icon=get(bank,slot);if(!icon)return FALSE;
    // 61BB80 resets identity/quantity locally, after the owning board unregisters.
    // Other target children/reset fields remain open.
    icon->ResetTimerOnEmpty455();
    icon->SetObjectIndex455(0xffffffff);icon->SetItemID(0xffffffff);
    icon->m_wNum=1;icon->SetRefItem(nullptr);icon->SetGradeFrameColor455(0);return TRUE;
}
namespace {
RF455ItemDataSpan data(RF455ManagedItem& item){
    if(auto* basic=dynamic_cast<RF455BasicItem*>(&item))return basic->rawMetadata();
    if(auto* sf=dynamic_cast<RF455SkillForceItem*>(&item))return sf->rawData();
    throw std::logic_error("455 Linker payload data provider is not restored");
}
void requireLinkerProviders(RF455ManagedItem& item){
    if(item.header().flag21)throw std::logic_error("455 Linker item lock overlay provider is not restored");
    if(auto* sf=dynamic_cast<RF455SkillForceItem*>(&item)){
        if(sf->record().iconBoard)throw std::logic_error("455 live SF source-board state callback is not restored");
    }else if(item.isKind(2)){
        auto* basic=dynamic_cast<RF455BasicItem*>(&item);if(!basic)throw std::logic_error("455 Animus source-board owner missing");
        const auto state=basic->recordBytes();std::uint32_t owner=0;
        if(state.size<100)throw std::out_of_range("455 Animus source-board field outside owner");
        std::memcpy(&owner,state.data+96,4);if(owner)throw std::logic_error("455 live Animus source-board state callback is not restored");
    }
    const auto table=data(item);
    if(table.data){if(table.size<=88)throw std::out_of_range("455 Linker classification outside data owner");
        if(table.data[88]==11)throw std::logic_error("455 Linker potion cooldown cache provider is not restored");}
}
}
CGUIItem* CLinkBoard::LinkerIcon455(BYTE bank,BYTE slot){return m_uiLinkWindow.LinkerIcons455().get(bank,slot);}
BOOL CLinkBoard::AddTypedObject455(BYTE bank,BYTE slot,CBoardObject* original){
    if(bank>=5||slot>=10||bank>=m_byMaxPackNum||!original||!original->GetItem455())return FALSE;
    auto* source=original->GetIcon();
    if(!source||!source->UsesTypedIcon455())throw std::logic_error("455 Linker requires the real typed original icon");
    requireLinkerProviders(*original->GetItem455());
    // 46B720(0), then virtual Clone. Do not register a borrowed original.
    source->SetRefItem(nullptr);std::unique_ptr<CBoardObject> copy(original->Clone());
    if(!copy)return FALSE;
    if(!m_listItemPack[bank].Add(slot,copy.get()))return FALSE;
    auto* owned=copy.release();m_linkerOwned455[10*bank+slot]=true;
    if(!m_uiLinkWindow.LinkerIcons455().takeIn(bank,slot,source))throw std::logic_error("455 admitted Linker icon handoff failed");
    auto* icon=LinkerIcon455(bank,slot);owned->SetIcon(icon);RF455_GameIconLinks().registerIcon(*icon);
    icon->SetOwnerContext455(2);
    icon->SetGrade455(owned->GetItem455()->isKind(0)?RF455_ReadBasicIconMetadata(*owned->GetItem455()).grade:0);
    return TRUE;
}
BOOL CLinkBoard::RemoveTypedObject455(BYTE bank,BYTE slot){
    if(bank>=5||slot>=10||!m_linkerOwned455[10*bank+slot])return FALSE;
    auto* icon=LinkerIcon455(bank,slot);RF455_GameIconLinks().unregisterIcon(*icon);
    RemoveCooldownObject455(GetObject(bank,slot));
    m_uiLinkWindow.LinkerIcons455().takeOut(bank,slot);
    const BOOL result=m_listItemPack[bank].Remove(slot);m_linkerOwned455[10*bank+slot]=false;return result;
}
void CLinkBoard::ClearTypedLinker455(){
    for(BYTE bank=0;bank<5&&bank<m_byMaxPackNum;++bank)for(BYTE slot=0;slot<10;++slot)
        if(m_linkerOwned455[10*bank+slot])RemoveTypedObject455(bank,slot);
}
