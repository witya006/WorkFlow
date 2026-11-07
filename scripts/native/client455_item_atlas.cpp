#include "userinterface/spritemgr.h"
#include "userinterface/guicontroller/guiitem.h"
#include "client455_item_atlas.h"

bool RF455_ItemAtlasPage(std::uint32_t classification,std::uint32_t& id,std::uint8_t& page){
    page=0;
    switch(classification>>28){
    case 1:page=1;return true;
    case 2:page=26;return true;
    case 3:page=2;return true;
    case 4:page=24;return true;
    case 6:page=27;return true;
    case 7:page=28;return true;
    case 8:page=32;return true;
    case 0:break;
    default:return true; //7B068F default retains page0.
    }
    const auto extension=static_cast<std::uint8_t>(classification>>8);
    switch((classification>>16)&15){
    case 0:{static const std::uint8_t armor[]={13,13,14,15,16,17,19,18,19,19};if(extension>=10)return false;page=armor[extension];break;}
    case 1:page=extension==29||extension==30||extension==31?30:0;break;
    case 2:page=extension==3||extension==4||extension==14?4:extension==13?34:5;break;
    case 3:{
        static const std::uint8_t other[]={7,8,12,8,9,6,10,11,11,11,11,20,21,22,25,29,31,0,33,30,30,30,35,36,37,8,8,8,8,8};
        if(extension>=30)return false;page=other[extension];
        if(page==12&&id>1023){if(id<=2047){page=37;id-=1024;}else{page=39;id-=2048;}}
        break;
    }
    case 4:page=extension<=5?3:23;break;
    case 8:page=38;break;
    default:return false;
    }
    return true;
}
namespace {
bool geometry(CSprite* sprite,std::uint32_t id,std::uint32_t page,int width,SPRITE_INFO& out){
    if(page>=sprite->GetPageNum())return false;
    out.wActionNo=static_cast<WORD>(page<<8);
    sprite->InitPageSprite(static_cast<WORD>(width),static_cast<WORD>(width));sprite->SetPage(page);
    //Target uses signed IDIV for dimensions, unsigned DIV for spriteID, then
    //truncates the row toWORD before its signed comparison with available rows.
    const int columns=sprite->GetSpriteOrgXL()/width;if(!columns)return false;
    const auto divisor=static_cast<std::uint32_t>(columns);
    out.wActionNo=static_cast<WORD>(out.wActionNo|(id%divisor));out.wFrameNo=static_cast<WORD>(id/divisor);
    if(static_cast<int>(out.wFrameNo)<sprite->GetSpriteOrgYL()/width)return true;
    out.wFrameNo=0;return false;
}
}
bool RF455_ItemSpriteSearch455(std::uint32_t id,std::uint32_t classification,int width,SPRITE_INFO& out){
    if(!width||!out.pSprite)return false;std::uint8_t page=0;
    return RF455_ItemAtlasPage(classification,id,page)&&geometry(out.pSprite,id,page,width,out);
}
bool RF455_UnitPartsSearch455(std::uint32_t id,std::uint32_t page,int width,SPRITE_INFO& out){
    if(!width||!out.pSprite)return false;return geometry(out.pSprite,id,page,width,out);
}
bool RF455_DefaultSpriteSearch455(std::uint32_t id,SPRITE_INFO& out){out.wActionNo=static_cast<WORD>((id>>8)&255);out.wFrameNo=static_cast<BYTE>(id);return true;}
BOOL CSpriteMgr::GetTargetSpriteInfo455(BYTE targetID,DWORD id,DWORD classification,int width,SPRITE_INFO& out){
    auto* sprite=GetTargetSprite455(targetID);if(!sprite)return FALSE;out.pSprite=sprite;
    const bool found=targetID==8?RF455_ItemSpriteSearch455(id,classification,width,out):targetID==19?RF455_UnitPartsSearch455(id,classification,width,out):RF455_DefaultSpriteSearch455(id,out);
    if(!found){out.wActionNo=0;out.wFrameNo=0;}return found;
}
void CGUIItem::SetTypedSprite455(){
    if(m_dwItemID==0xffffffff)return;
    const POINT displayed=m_ptSize;SPRITE_INFO selected={};
    const BYTE targetID=m_byIconType==5?19:8;
    const DWORD classification=targetID==19?m_dwItemID:(std::uint32_t(m_byIconType)<<28)|(m_dwItemID&0x0fffffff);
    gSpriteMgr.GetTargetSpriteInfo455(targetID,m_dwSpriteID,classification,m_bySpriteSize,selected);
    SetSpriteInfo(&selected);SetSize(displayed.x,displayed.y);
    //Other61AF30 child/timer/lock-skin initializers remain tracked separately.
}
