#include "client455_briefing_controls.h"
#include "client455_language.h"
#include <cmath>
#include <stdexcept>
float R3GetLoopTime();

namespace {
RF455GuiAnimationReplay replay;
DWORD clockNow(){return replay.milliseconds?replay.milliseconds():timeGetTime();}
float frameSeconds(){return replay.frameSeconds?replay.frameSeconds():R3GetLoopTime();}
float advance(float frame,float seconds,float fps){
    float result;
    __asm {fld seconds
           fmul fps
           fadd frame
           fstp result}
    return result;
}
void image(CGUIObject& object,CSprite* sprite,WORD action,WORD frame,bool natural){
    SPRITE_INFO info={sprite,action,frame};object.SetSpriteInfo(&info);
    if(sprite&&natural){sprite->SetAction(action);sprite->SetFrame(frame);object.SetSize(sprite->GetSpriteOrgXL(),sprite->GetSpriteOrgYL());}
}
void alpha(CGUIObject& object,BYTE value){object.SetARGB((object.GetARGB()&0xffffff)|(DWORD(value)<<24));}
}
RF455GuiAnimationReplay RF455_SetGuiAnimationReplay(RF455GuiAnimationReplay value){const auto old=replay;replay=value;return old;}
void RF455GuiAnimatedImage::Reset455(){
    m_frame=0;m_total=1;m_finished=FALSE;m_fps=10;m_columns=1;
    m_paused=FALSE;m_pauseInterval=m_pauseTime=0;m_uvSize[0]=m_uvSize[1]=0;
    m_fSpriteUV[0][0]=m_fSpriteUV[1][0]=0;m_fSpriteUV[0][1]=m_fSpriteUV[1][1]=1;
    m_loop=TRUE;m_uvWidth=m_uvHeight=0;
}
void RF455GuiAnimatedImage::SetImage455(CSprite* sprite,WORD action,WORD frame,bool natural){
    image(*this,sprite,action,frame,natural);
    if(sprite){
        // Target CGUIObjectEx.SetSpriteInfo restores the original-image/texture
        // ratios, rather than sampling padding up to raw UV1.
        const float u=static_cast<float>(double(sprite->GetSpriteOrgXL())/sprite->GetSpriteXL());
        const float v=static_cast<float>(double(sprite->GetSpriteOrgYL())/sprite->GetSpriteYL());
        m_fSpriteUV[0][0]=m_fSpriteUV[1][0]=0;m_fSpriteUV[0][1]=u;m_fSpriteUV[1][1]=v;
    }
}
bool RF455GuiAnimatedImage::SetSheet455(BYTE columns,BYTE rows){
    auto* info=GetSpriteInfo();auto* sprite=info->pSprite;if(!sprite)return false;
    sprite->SetAction(info->wActionNo);sprite->SetFrame(info->wFrameNo);
    if(!columns)columns=1;if(!rows)rows=1;m_columns=columns;m_total=static_cast<WORD>(columns*rows);
    SetSize(sprite->GetSpriteOrgXL()/columns,sprite->GetSpriteOrgYL()/rows);
    const auto tw=sprite->GetSpriteXL(),th=sprite->GetSpriteYL();
    if(tw&&th){m_uvSize[0]=static_cast<float>(double(m_uvWidth?m_uvWidth:GetSizeX())/tw);m_uvSize[1]=static_cast<float>(double(m_uvHeight?m_uvHeight:GetSizeY())/th);}
    return true;
}
void RF455GuiAnimatedImage::SetUV455(){
    if(!std::isfinite(m_frame)||m_frame<0||m_frame>=2147483648.0f)throw std::domain_error("455 GUI animation frame outside verified integer domain");
    const int index=static_cast<int>(m_frame);
    m_fSpriteUV[0][0]=static_cast<float>(double(index%m_columns)*m_uvSize[0]);
    m_fSpriteUV[0][1]=m_fSpriteUV[0][0]+m_uvSize[0];
    m_fSpriteUV[1][0]=static_cast<float>(double(index/m_columns)*m_uvSize[1]);
    m_fSpriteUV[1][1]=m_fSpriteUV[1][0]+m_uvSize[1];
}
void RF455GuiAnimatedImage::SetFrame455(WORD frame,BOOL finished){
    m_frame=static_cast<float>(frame);if(m_frame>=m_total)m_frame=0;
    SetUV455();m_finished=finished;
}
void RF455GuiAnimatedImage::Update(){
    if(!IsShow()||m_finished)return;
    if(m_paused){if(clockNow()-m_pauseTime>m_pauseInterval)m_paused=FALSE;return;}
    if(m_total<=1)return;
    m_frame=advance(m_frame,frameSeconds(),m_fps);
    if(m_frame>=m_total){
        if(m_loop){m_paused=TRUE;m_pauseTime=clockNow();m_frame=0;}
        else {m_frame=static_cast<float>(double(m_total)-1.0);m_finished=TRUE;}
    }
    SetUV455();
}
BOOL RF455GuiAnimatedImage::Draw(){return GetSpriteInfo()->pSprite?CGUIObjectEx::Draw():CGUIObject::Draw();}

CGUIBriefingBoard::CGUIBriefingBoard(){m_upper.DisableFocus();m_lower.DisableFocus();Add(&m_upper);Add(&m_lower);}
void CGUIBriefingBoard::SetCaps455(CSprite* common,BOOL fullWidth){
    image(m_upper,common,fullWidth?4:9,fullWidth?3:6,true);
    image(m_lower,common,fullWidth?4:9,fullWidth?4:7,true);
}
void CGUIBriefingBoard::SetAlpha455(BYTE value){
    alpha(m_upper,value);alpha(m_lower,value);m_bodyColor=(m_bodyColor&0xffffff)|(DWORD(value)<<24);m_borderColor=(m_borderColor&0xffffff)|(DWORD(value)<<24);
}
void CGUIBriefingBoard::SetSize(LONG width,LONG height){
    CGUIObject::SetSize(width,height);m_upper.SetPos(m_ptPos);m_lower.SetPos(m_ptPos.x,m_ptPos.y+height-m_lower.GetSizeY());
}
BOOL CGUIBriefingBoard::Draw(){
    if(!IsShow())return FALSE;
    const LONG x=GetPosX(),right=x+GetSizeX(),top=m_upper.GetPosY()+m_upper.GetSizeY(),bottom=m_lower.GetPosY();
    Draw2DRectangle(x,top,right,bottom,m_bodyColor);
    Draw2DRectangle(x+m_borderInset,top,x+m_borderInset+m_borderWidth,bottom,m_borderColor);
    Draw2DRectangle(right-m_borderInset-m_borderWidth,top,right-m_borderInset,bottom,m_borderColor);
    // Target paints base image/fill and children after the manual rectangles.
    return CGUIContainer::Draw();
}

CGUITutorialKeyBoard::CGUITutorialKeyBoard(){
    for(auto& row:m_rows)row.plus.SetSize(12,12);
    m_or.SetString(const_cast<char*>(RF455_GetNormalLanguagePack()->get(1058)));
}
void CGUITutorialKeyBoard::SetSprite455(CSprite* tutorial){
    m_tutorial=tutorial;for(auto& row:m_rows)image(row.plus,tutorial,0,0,false);
}
bool CGUITutorialKeyBoard::ConfigureKey455(BYTE key,RF455GuiAnimatedImage& object){
    if(key==255)return false;object.Reset455();
    if(!m_tutorial)throw std::logic_error("455 Tutorial key sprite provider missing");
    if(key<5){
        object.SetSize(64,64);object.SetImage455(m_tutorial,1,key,true);
        switch(key){
        case 0:object.SetSheet455(1,2);object.SetFPS455(1);break;
        case 1:object.SetSheet455(1,1);break;
        case 2:object.SetSheet455(1,3);object.SetFPS455(3);break;
        default:object.SetSheet455(1,4);object.SetFPS455(3);break;
        }
        return true;
    }
    WORD frame=0;
    switch(key){
    case 17:frame=0;break;case 112:frame=1;break;case 32:frame=2;break;
    case 65:frame=3;break;case 70:frame=4;break;case 73:frame=5;break;
    case 77:frame=6;break;case 79:frame=7;break;case 87:frame=8;break;
    case 90:frame=9;break;case 83:frame=10;break;case 18:frame=11;break;
    default:return false;
    }
    object.SetImage455(m_tutorial,2,frame,true);return true;
}
void CGUITutorialKeyBoard::SetRows455(BYTE count,const std::array<std::array<BYTE,2>,2>& keys){
    RemoveAll();if(!count)return;LONG widths[2]={0,0},heights[2]={0,0};
    for(unsigned i=0;i<count&&i<2;++i){
        auto& row=m_rows[i];
        if(ConfigureKey455(keys[i][0],row.first)){Add(&row.first);widths[i]=row.first.GetSizeX();}
        if(ConfigureKey455(keys[i][1],row.second)){Add(&row.plus);Add(&row.second);widths[i]+=row.plus.GetSizeX()+5+row.second.GetSizeX();}
        if(i+1<count){Add(&m_or);widths[i]+=m_or.GetSizeX();}
        // Target uses the stored dimensions even for keys not added this time.
        heights[i]=row.first.GetSizeY()>row.second.GetSizeY()?row.first.GetSizeY():row.second.GetSizeY();
    }
    LONG width=0,height=0;
    for(unsigned i=0;i<count&&i<2;++i){if(width<widths[i])width=widths[i];height+=heights[i];if(i+1<count)height+=10;}
    LONG y=GetPosY()+(GetSizeY()-height)/2;
    for(unsigned i=0;i<count&&i<2;++i){
        auto& row=m_rows[i];LONG x=GetPosX()+(GetSizeX()-width)/2;
        if(IsAddedObject(&row.first)){row.first.SetPos(x,y+(heights[i]-row.first.GetSizeY())/2);x+=row.first.GetSizeX();}
        if(IsAddedObject(&row.second)){
            row.plus.SetPos(x+5,y+(heights[i]-row.plus.GetSizeY())/2);x+=row.plus.GetSizeX()+5;
            row.second.SetPos(x+5,y+(heights[i]-row.second.GetSizeY())/2);x+=row.second.GetSizeX()+5;
        }
        if(i+1<count)m_or.SetPos(x+5,y+heights[i]-m_or.GetSizeY());
        y+=heights[i]+10;
    }
}
