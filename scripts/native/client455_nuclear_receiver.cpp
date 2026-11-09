#include "gameobject/manager/ccharactermgr.h"
#include "gameobject/board/common/cboardmanager.h"
#include "cland.h"
#include "ccamera.h"
#include "datafile.h"
#include "datatable/cresourcedatamgr.h"
#include "input/imeedit.h"
#include "gameprogress/cgameprogress.h"
#include "userinterface/spritemgr.h"
#include "userinterface/gamewindow/etcwin/guiminimapwindow.h"
#include "mainapp.h"
#include "client455_nuclear_receiver.h"
#include "client455_nuclear_wire.h"
#include "client455_nuclear_registry.h"
#include "client455_language.h"
#include "client455_message_dispatch.h"
#include <stdexcept>

namespace {
CAvatar& avatar(){auto* value=_GetAvatar();if(!value)throw std::logic_error("455 nuclear receiver requires actual Avatar");return *value;}
BYTE race(){return static_cast<BYTE>(avatar().GetRace()/2);}
BYTE statusIndex(){switch(static_cast<BYTE>(avatar().GetStatusCode455())){case 10:return 0;case 2:return 1;case 6:return 2;default:return 255;}}
void marker(BOOL show,BYTE index){
    auto* owner=RF455_GetNuclearContainer();if(!owner)return;
    auto* map=_GetMinimapWindow();if(!map)throw std::logic_error("455 nuclear receiver requires actual MiniMap");
    // 5C59D0 selects this+0x2DC4+index*540;70BF30 obtains the local-race
    // record and leaves the existing UI untouched when lookup fails.
    map->SetNuclearMarker455(index,show,show?owner->Position(race(),index):nullptr);
}
void requestOff(){_GetGBM()->SetRequestProcessState(FALSE);}
void message(unsigned id){RF455_ShowSystemMessage(RF455_GetNormalLanguagePack()->get(id));}
}

void RF455_CompleteNuclearInventoryUse(CBoardObject* object){
    auto* payload=object?object->GetItem455():nullptr;if(!payload)return;
    auto* basic=dynamic_cast<RF455BasicItem*>(payload);
    if(!basic||payload->header().kind!=0)throw std::logic_error("455 nonphysical typed inventory use remains open");
    const auto data=basic->rawData();if(!data.data||data.size<=88)throw std::logic_error("455 inventory use requires actual item metadata");
    if(data.data[88]!=33)throw std::logic_error("455 other typed inventory use branches remain open");
    // Vtable AAC50C+124→475A90,category33→4757D0(empty),then475E10.
    avatar().ClearUsingItem455();
}

void CNetMsgProcessor_Nuclear::Result455(BYTE result){
    auto& owner=RF455_NuclearContainer();auto* manager=_GetGBM();
    if(avatar().IsDeath()){
        owner.Aiming().Clear();marker(FALSE,statusIndex());message(0xce6);return;
    }
    if(!result){RF455_BeginNuclearSelection();return;}
    if(result==1){
        auto* object=manager->GetOrgObject();auto* item=object?object->GetItem455():nullptr;
        if(!item)return;
        WORD serial=static_cast<WORD>(item->header().serial);
        manager->SetRequestProcessState(TRUE);SendNetMessage(60,1,&serial,2);return;
    }
    if(result==2){
        if(manager->GetOrgBoardType()==0){
            auto* board=dynamic_cast<CObjectBoard*>(manager->GetBoard(0));
            if(!board)throw std::logic_error("455 nuclear result2 requires actual inventory board");
            board->UI_UseResult(TRUE);
        }
        marker(TRUE,statusIndex());return;
    }
    requestOff();unsigned id=0xcf0;
    if(result>=3&&result<=7)id=0xce8+result-3;
    else if(result==8)id=0x16c;
    else if(result>=9&&result<=11)id=0xced+result-9;
    else if(result==12)id=0xce6;
    message(id);
}

bool CNetMsgProcessor_Nuclear::AnalysisServerPacket(_MSG_HEADER* header,char* payload){
    if(!header||header->m_wSize<4||header->m_byType[0]!=60)return false;
    switch(header->m_byType[1]){case 0:case 3:case 4:case 5:case 6:case 7:case 8:case 9:case 10:break;
    default:m_pNetworkMgr->NetLogWrite("Unknown Message : CNetMsgProcessor_Nuclear::AnalysisServerPacket()\n");return false;}
    RF455NuclearWireMessage value;
    if(!RF455_ReadNuclearPayload(header->m_byType[1],payload,header->m_wSize-4,value))return false;
    if(value.opcode==10&&value.ignoredList)return true;
    auto& owner=RF455_NuclearContainer();
    switch(value.opcode){
    case 0:Result455(value.result);break;
    case 3:requestOff();owner.SetPosition(race(),value.index,value.position.data());marker(TRUE,value.index);break;
    case 4:
        requestOff();owner.Add(value.race,value.index);
        if(race()!=value.race)owner.SetCountdown(value.race,value.index,9);
        if(avatar().GetLevel()>24)owner.NotifyRace(value.race,value.index);break;
    case 5:requestOff();owner.Launch(value.race,value.index);break;
    case 6:
        requestOff();owner.Aiming().SetPending(0);owner.Radar(value.race,value.index,FALSE);
        if(race()==value.race)marker(FALSE,value.index);
        owner.Impact(value.race,value.index);break;
    case 7:requestOff();owner.SetPosition(value.race,value.index,value.position.data());owner.Radar(value.race,value.index,TRUE);break;
    case 8:case 9:
        if(race()==value.race)marker(FALSE,value.index);
        owner.Remove(value.race,value.index);break;
    case 10:
        owner.ResetRecords();owner.ClearAll();
        for(unsigned i=0;i<value.count;++i){const auto& entry=value.entries[i];
            marker(FALSE,entry.index);owner.Add(entry.race,entry.index);
            if(entry.position[0]!=0&&entry.position[1]!=0&&entry.position[2]!=0)
                owner.SetPosition(entry.race,entry.index,entry.position.data());
        }
        break;
    default:return false;
    }
    return true;
}
