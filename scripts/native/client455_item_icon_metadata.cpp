#include "gameobject/manager/ccharactermgr.h"
#include "gameobject/board/common/cboardmanager.h"
#include "cland.h"
#include "ccamera.h"
#include "datafile.h"
#include "datatable/cresourcedatamgr.h"
#include "input/imeedit.h"
#include "gameprogress/cgameprogress.h"
#include "userinterface/spritemgr.h"
#include "userinterface/gamewindow/guiinventorywindow.h"
#include "mainapp.h"
#include "client455_item_icon_metadata.h"
#include <cstring>
#include <stdexcept>

namespace {
unsigned metadataByte(RF455ItemDataSpan data,std::size_t offset){
    if(!data.data||offset>=data.size)throw std::out_of_range("455 icon metadata byte outside its table owner");return data.data[offset];
}
std::uint32_t metadataWord(RF455ItemDataSpan data,std::size_t offset){
    if(!data.data||offset>data.size||data.size-offset<4)throw std::out_of_range("455 icon metadata word outside its table owner");
    std::uint32_t value;std::memcpy(&value,data.data+offset,4);return value;
}
}
RF455BasicIconMetadata RF455_ReadBasicIconMetadata(RF455ManagedItem& item){
    auto* basic=dynamic_cast<RF455BasicItem*>(&item);
    if(!basic||item.header().kind==5)throw std::logic_error("455 dedicated SF/Quest icon owners are not restored");
    const auto data=basic->rawMetadata();
    RF455BasicIconMetadata result={0xffffffff,0xffffffff,basic->quantity455(),0,0};
    if(!data.data)return result;
    result.itemID=metadataWord(data,72);result.spriteID=metadataWord(data,76);
    const auto kind=metadataByte(data,88);const bool equipment=kind>=1&&kind<=10;
    if(equipment)result.grade=static_cast<std::uint8_t>(metadataByte(data,152));
    std::size_t offset=0;
    if(equipment||kind==27)offset=172;
    else switch(kind){
        case 13:case 28:case 35:case 31:offset=152;break;
        case 25:case 26:offset=164;break;
        case 33:offset=157;break;
        case 34:offset=156;break;
        case 36:offset=168;break;
        case 30:offset=160;break;
        default:break;
    }
    if(offset)result.usableLevel=static_cast<std::uint8_t>(metadataByte(data,offset));return result;
}
bool RF455_IconUsable455(std::uint32_t id,std::uint8_t race,std::uint8_t level,std::uint8_t required){
    const unsigned user=(id>>20)&255;
    if(user<5){if(race!=user)return false;}
    else if(user!=10)switch(user){
        case 9:if(race==4)return false;break;
        case 8:if(race!=2&&race!=3)return false;break;
        case 7:if(race!=0&&race!=1)return false;break;
        case 6:if(!(race&1))return false;break;
        default:if(race&1)return false;break;
    }
    return level==255||required==255||level>=required;
}
BOOL CGUIInventoryBoard::TakeInItem455(BYTE slot,CBoardObject* object,BYTE race){
    if(slot>=TOTAL_INVENTORY||!object||!object->GetItem455()||!object->GetItem455()->isKind(0))return FALSE;
    const auto metadata=RF455_ReadBasicIconMetadata(*object->GetItem455());if(!metadata.quantity)return FALSE;
    if(!TakeInItemFields455(slot,metadata.itemID,metadata.spriteID,metadata.quantity,metadata.usableLevel,race))return FALSE;
    auto* bound=GetItem(slot);if(bound)bound->SetGrade455(metadata.grade);object->SetIcon(bound);return TRUE;
}
BOOL CGUIInventoryBoard::TakeInItemFields455(BYTE slot,DWORD itemID,DWORD spriteID,BYTE quantity,BYTE required,BYTE race){
    if(slot>=TOTAL_INVENTORY)return FALSE;
    auto& icon=m_uiItem[slot];icon.SetIconType455(0);icon.SetItemID(itemID);icon.SetSpriteID(spriteID);icon.SetNum(quantity);
    if(required!=255)icon.SetUsableLevel(required);
    icon.SetSprite();icon.SetSize(32,32);
    const bool usable=RF455_IconUsable455(icon.GetItemID(),race,255,icon.GetUsableLevel());icon.SetUsable(usable);
    SetUselessItem(slot,!usable);SetTradeItem(slot,FALSE);return TRUE;
}
