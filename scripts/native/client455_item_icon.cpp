#include "userinterface/guicontroller/guiitem.h"
#include "userinterface/spritemgr.h"
#include "client455_item_icon.h"
#include "client455_font.h"
#include <cstdio>
#include <cwchar>
#include <stdexcept>

std::uint32_t RF455_ItemGradeColor(std::uint8_t grade){
    static const std::uint32_t colors[]={0xffc8d9ff,0xffffff80,0xffbd91ff,0xfffc9d07,0xff0099ff,0xffffccff,
        0xff9af0fc,0xff66ff66,0xff66ff66,0xffecd0a6,0xffff3b0d,0xffff00ff};
    return grade<12?colors[grade]:colors[0];
}
bool RF455_ItemQuantityVisible(std::uint8_t type,std::uint16_t quantity,bool enabled,bool clipped){
    return enabled&&((quantity>1&&(type==0||type==7||(!clipped&&type==2)))||(!quantity&&type==0));
}
void CGUIItem::SetGrade455(BYTE grade){m_grade455=grade;m_gradeFrame455.SetARGB(RF455_ItemGradeColor(grade));}
void CGUIItem::SetPos(LONG x,LONG y){CGUIObject::SetPos(x,y);m_gradeFrame455.SetPos(x,y);m_timer455.SetPos(x,y);
    m_readyCue455.SetPos(x+(m_ptSize.x-m_readyCue455.GetSizeX())/2,y+(m_ptSize.y-m_readyCue455.GetSizeY())/2);}
void CGUIItem::SetSize(LONG width,LONG height){
    CGUIObject::SetSize(width,height);m_gradeFrame455.SetSize(width,height);m_timer455.SetSize(width,height);
    //61B450 selects the two grade-frame cells by signed displayed width.
    m_gradeFrame455.GetSpriteInfo()->wActionNo=3;m_gradeFrame455.GetSpriteInfo()->wFrameNo=width>=64?3:2;
}
BOOL CGUIItem::DrawTypedIcon455(RECT* clip){
    if(!IsShow())return FALSE;auto* image=GetSpriteInfo()->pSprite;if(!image)return TRUE;
    image->InitPageSprite(m_bySpriteSize,m_bySpriteSize);
    SetARGB((GetARGB()&0xff000000)|(m_byUsable?0xffffff:0x666666));
    const auto drawGrade=[&](){if(m_gradeFrameVisible455){
        //Target reference6/action3/frame2-or3 is an inventory grade border,
        //not text. Its sprite ID differs from the old UI's group6 shop.
        auto* skin=gSpriteMgr.GetTargetSprite455(6);
        const WORD frame=m_ptSize.x>=64?3:2;
        if(!skin||skin->GetMaxActions()<=3||skin->GetMaxFrames(3)<=frame)throw std::runtime_error("455 inventory grade-frame sprite missing");
        SPRITE_INFO reference={skin,3,frame};m_gradeFrame455.SetSpriteInfo(&reference);m_gradeFrame455.Show(TRUE);
        if(clip)m_gradeFrame455.Draw(*clip);else m_gradeFrame455.Draw();
    }};
    if(clip)drawGrade();
    const BOOL drawn=clip?CGUIObject::Draw(*clip):CGUIObject::Draw();if(!drawn)return FALSE;
    if(!clip)drawGrade();
    if(RF455_ItemQuantityVisible(m_byIconType,m_wNum,m_bDrawItemNum!=0,clip!=nullptr)){
        char number[8];std::snprintf(number,sizeof(number),"%u",unsigned(m_wNum));DrawR3Hangul(m_ptPos.x,m_ptPos.y+m_ptSize.y-12,number,0xffffffff,32);
    }
    if(clip)m_timer455.Draw(*clip);else m_timer455.Draw();
    DrawTimerLabel455(clip);return TRUE;
}
void CGUIItem::Update(){CGUIObject::Update();if(m_typedIcon455)m_timer455.Update();}
BOOL CGUIItem::DrawTimerLabel455(RECT* clip){
    RF455TimerLabel label={};const auto value=RF455_TimerLabel455(static_cast<DWORD>(m_timer455.State455().remaining),m_ownerContext455,label);
    if(label.unit==3)return TRUE;
    // Target callers supply contexts0..5. Unknown contexts leave position/scale
    // unwritten; do not accept that undefined draw domain as successful output.
    if(m_ownerContext455>5)throw std::logic_error("455 timer label context has unwritten geometry");
    const float x=static_cast<float>(static_cast<LONG>(DWORD(m_ptPos.x)+DWORD(m_ptSize.x)+DWORD(label.offset.x)));
    const float y=static_cast<float>(static_cast<LONG>(DWORD(m_ptPos.y)+DWORD(m_ptSize.y)-DWORD(label.offset.y)));
    if(clip&&(x<clip->left||y<clip->top||clip->right<x+label.scale*16.0f||clip->bottom<y+label.scale*16.0f))return FALSE;
    wchar_t text[16];if(label.unit==0)std::swprintf(text,16,L"%u",value);else std::swprintf(text,16,label.unit==1?L"%um":L"%uh",value);
    float position[4]={x,y,0,1};return SUCCEEDED(RF455_DrawText(position,text,label.color,0x80000060,label.scale));
}
