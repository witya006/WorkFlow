#include "userinterface/guicontroller/guiscrollbar.h"
#include "userinterface/spritemgr.h"
#include <algorithm>
#include <cstdint>
#include <stdexcept>
#undef min
#undef max

namespace {
RF455ScrollbarClock clockProvider=nullptr;
DWORD clockNow(){return clockProvider?clockProvider():timeGetTime();}
LONG add(LONG a,LONG b){return static_cast<LONG>(static_cast<DWORD>(a)+static_cast<DWORD>(b));}
LONG sub(LONG a,LONG b){return static_cast<LONG>(static_cast<DWORD>(a)-static_cast<DWORD>(b));}
LONG multiply(LONG a,LONG b){return static_cast<LONG>(static_cast<DWORD>(a)*static_cast<DWORD>(b));}
float scaledDistance(LONG total,int distance,int scrollLength){
    double savedTotal,savedDistance;float amount;
    __asm {
        fild total
        fild distance
        fxch st(1)
        fstp savedTotal
        fstp savedDistance
        fild scrollLength
        fdivr savedDistance
        fmul savedTotal
        fstp amount
    }
    return amount;
}
int truncateTarget(float amount){
    double widened;int result;
    static const bool sse2=IsProcessorFeaturePresent(PF_XMMI64_INSTRUCTIONS_AVAILABLE)!=0;
    if(sse2){
        __asm {fld amount
               fstp widened
               cvttsd2si eax,widened
               mov result,eax}
    }else{
        // Older target helper returns the low DWORD of an x87 int64 result.
        // The supported modern MSVC environment takes the SSE2 branch above.
        __int64 value;unsigned short before,chop;
        __asm {fnstcw before}
        chop=before|0x0c00;
        __asm {fldcw chop
               fld amount
               fistp value
               fldcw before}
        result=static_cast<int>(value);
    }
    return result;
}
bool smallUpperHalf(float amount,LONG total){
    const double two=2;unsigned short status;
    __asm {fild total
           fdiv two
           fld amount
           fcompp
           fnstsw status}
    // Target TEST AH,5 / JP includes unordered in its upper-half branch.
    const unsigned flags=(status>>8)&5;return flags==0||flags==5;
}
bool roundUnitUp(float amount,int rounded,int unit){
    const double two=2;unsigned short status;
    __asm {fild rounded
           fsubr amount
           fild unit
           fdiv two
           fcompp
           fnstsw status}
    const unsigned flags=(status>>8)&0x41;return flags==1||flags==0x40;
}
int snapAmount(LONG total,WORD unit,int distance,int scrollLength){
    const float amount=scaledDistance(total,distance,scrollLength);const int current=truncateTarget(amount);
    if(current>=total)return total;
    if(total<static_cast<int>(unit))return smallUpperHalf(amount,total)?total:0;
    if(!unit)throw std::domain_error("Scrollbar zero adjustment modulo is outside verified domain");
    int rounded=sub(current,current%unit);
    if(roundUnitUp(amount,rounded,unit)){rounded=add(rounded,unit);if(rounded>total)rounded=total;}
    return rounded;
}
void setAlpha(CGUIObject& object,BYTE alpha){object.SetARGB((object.GetARGB()&0xffffff)|(static_cast<DWORD>(alpha)<<24));}
void setSizedImage(CGUIObject& object,SPRITE_INFO& image){
    object.SetSpriteInfo(&image);auto* sprite=image.pSprite;
    //626060's resize flag queries the requested action/frame;it does not clamp.
    if(sprite&&image.wActionNo<sprite->GetMaxActions()&&image.wFrameNo<sprite->GetMaxFrames(image.wActionNo)&&sprite->GetSpriteOrgXL(image.wActionNo,image.wFrameNo))
        object.SetSize(sprite->GetSpriteOrgXL(image.wActionNo,image.wFrameNo),sprite->GetSpriteOrgYL(image.wActionNo,image.wFrameNo));
}
LONG imageHeight(CGUIObject& object){
    auto& image=*object.GetSpriteInfo();auto* sprite=image.pSprite;
    return sprite&&image.wActionNo<sprite->GetMaxActions()&&image.wFrameNo<sprite->GetMaxFrames(image.wActionNo)?sprite->GetSpriteOrgYL(image.wActionNo,image.wFrameNo):0;
}
void drawRow(CGUIObject& object,CSprite* sprite,WORD action,WORD frame,LONG width,LONG x,LONG y){
    if(!sprite||!object.IsShow())return;
    sprite->SetAction(action);sprite->SetFrame(frame);
    const float ratio=static_cast<float>(static_cast<double>(sprite->GetSpriteOrgXL())/sprite->GetSpriteXL());
    float uv[2][2]={{0,static_cast<float>(static_cast<double>(width)/sprite->GetSpriteOrgXL()*ratio)},
                   {static_cast<float>(2.0/sprite->GetSpriteOrgYL()*ratio),static_cast<float>(2.0/sprite->GetSpriteOrgYL()*ratio)}};
    sprite->DrawSpriteUV(x,y,uv,x+width,y+1,object.GetARGB());
}
}
RF455ScrollbarClock RF455_SetScrollbarClock(RF455ScrollbarClock provider){auto old=clockProvider;clockProvider=provider;return old;}

CGUIScrollbarButton::CGUIScrollbarButton(){SetSize(6,18);}
void CGUIScrollbarButton::SetSize(LONG width,LONG height){
    CGUIObject::SetSize(std::max<LONG>(6,width),std::max<LONG>(18,height));
    for(auto& segment:m_segments)segment.Show(TRUE);
}
void CGUIScrollbarButton::SetSegmented455(CSprite* sprite){
    m_skin=sprite;m_segmented=sprite!=nullptr;
    if(!sprite)return;
    for(unsigned i=0;i<3;++i){
        SPRITE_INFO image={sprite,2,m_frames[i][m_pressed]};m_segments[i].SetSpriteInfo(&image);
        sprite->SetAction(2);sprite->SetFrame(m_frames[i][m_pressed]);
        m_segments[i].SetSize(sprite->GetSpriteOrgXL(),sprite->GetSpriteOrgYL());
    }
}
void CGUIScrollbarButton::SetPressed455(BYTE pressed){
    if(pressed>1)throw std::out_of_range("Scrollbar thumb state outside two-mode domain");
    m_pressed=pressed;
    m_segments[0].GetSpriteInfo()->wFrameNo=m_frames[0][pressed];m_segments[2].GetSpriteInfo()->wFrameNo=m_frames[2][pressed];
}
BOOL CGUIScrollbarButton::Draw(){
    if(m_segmented){
        m_segments[0].SetPos(m_ptPos.x,m_ptPos.y);m_segments[0].Draw();
        if(m_skin&&m_segments[1].IsShow()){
            const WORD frame=m_frames[1][m_pressed];m_skin->SetAction(2);m_skin->SetFrame(frame);
            const float ratio=static_cast<float>(static_cast<double>(m_skin->GetSpriteOrgXL())/m_skin->GetSpriteXL());
            float uv[2][2]={{0,static_cast<float>(static_cast<double>(m_ptSize.x)/m_skin->GetSpriteOrgXL()*ratio)},
                           {static_cast<float>(2.0/m_skin->GetSpriteOrgYL()*ratio),static_cast<float>(2.0/m_skin->GetSpriteOrgYL()*ratio)}};
            for(int i=0;i<m_ptSize.y-12;++i){const LONG y=m_ptPos.y+m_segments[0].GetSizeY()+i;m_skin->DrawSpriteUV(m_ptPos.x,y,uv,m_ptPos.x+m_ptSize.x,y+1,m_segments[1].GetARGB());}
        }
        m_segments[1].SetPos(m_ptPos.x,m_ptPos.y+m_segments[0].GetSizeY());
        m_segments[2].SetPos(m_ptPos.x,m_ptPos.y+m_ptSize.y-m_segments[2].GetSizeY());m_segments[2].Draw();
    }
    return CGUIContainer::Draw();
}
CGUIScrollbar::CGUIScrollbar(){
    m_thumb.AddMouseEventHandler(this);m_thumb.AddMouseMotionEventHandler(this);
    Add(&m_top);Add(&m_bottom);SetStyle(Vertical);
}
CGUIScrollbar::~CGUIScrollbar(){}
void CGUIScrollbar::SetStyle(Style style){m_style=style;SetSize(m_ptSize.x,m_ptSize.y);}
void CGUIScrollbar::SetMinimumThumb455(LONG minimum){
    m_minThumb=minimum;const LONG available=m_style?m_ptSize.x-m_top.GetSizeX()-m_bottom.GetSizeX():m_ptSize.y-m_top.GetSizeY()-m_bottom.GetSizeY();
    if(m_minThumb>available)m_minThumb=available;
}
int CGUIScrollbar::GetMinSize(){return m_style?m_thumb.GetSizeX()+m_top.GetSizeX()+m_bottom.GetSizeX()+1:m_thumb.GetSizeY()+m_top.GetSizeY()+m_bottom.GetSizeY()+1;}
void CGUIScrollbar::SetBound(RECT& bound){SetPos(bound.left,bound.top);SetSize(bound.right-bound.left,bound.bottom-bound.top);}
void CGUIScrollbar::SetSize(LONG width,LONG height){
    CGUIObject::SetSize(width,height);
    if(m_style){
        m_top.SetPos(m_ptPos.x,m_ptPos.y+(m_ptSize.y-m_top.GetSizeY())/2);
        m_bottom.SetPos(m_ptPos.x+m_ptSize.x-m_bottom.GetSizeX(),m_top.GetPosY());
        m_thumb.SetPos(m_ptPos.x+m_top.GetSizeX(),m_ptPos.y);
    }else{
        m_top.SetPos(m_ptPos.x+(m_ptSize.x-m_top.GetSizeX())/2,m_ptPos.y);
        m_bottom.SetPos(m_top.GetPosX(),m_ptPos.y+m_ptSize.y-m_bottom.GetSizeY());
        m_thumb.SetPos(m_ptPos.x+(m_ptSize.x-m_thumb.GetSizeX())/2,m_ptPos.y+m_top.GetSizeY());
    }
    SetAmount(m_total,m_current);
}
void CGUIScrollbar::SetAmount(LONG total,LONG current){
    m_total=std::max<LONG>(0,total);m_current=std::max<LONG>(0,std::min(current,m_total));
    if(!m_total){
        m_top.RemoveMouseEventHandler();m_bottom.RemoveMouseEventHandler();RemoveMouseEventHandler();
        if(GetAddedObjectNum()==3)Remove(&m_thumb);return;
    }
    //639590 registers only self. Base ctor binds the composite thumb;arrows
    //remain unbound here. EX registers its own arrows explicitly in63A750.
    AddMouseEventHandler(this);
    if(!IsAddedObject(&m_thumb)){
        if(m_style)m_thumb.SetPos(0,m_ptPos.y+(m_ptSize.y-m_thumb.GetSizeY())/2);
        else m_thumb.SetPos(m_ptPos.x+(m_ptSize.x-m_thumb.GetSizeX())/2,0);
        if(m_bEnableFocus)m_thumb.EnableFocus();else m_thumb.DisableFocus();
        Add(&m_thumb);
    }
    if(m_autoThumb){
        if(m_style)m_thumb.m_ptSize.x=std::max(m_minThumb,m_ptSize.x-m_top.GetSizeX()-m_bottom.GetSizeX()-m_total);
        else m_thumb.m_ptSize.y=std::max(m_minThumb,m_ptSize.y-m_top.GetSizeY()-m_bottom.GetSizeY()-m_total);
    }
    m_thumb.SetSize(m_thumb.GetSizeX(),m_thumb.GetSizeY());UpdateBar();
}
int CGUIScrollbar::GetScrollLength455() const{
    return m_style?m_ptSize.x-m_top.m_ptSize.x-m_bottom.m_ptSize.x-m_thumb.m_ptSize.x:m_ptSize.y-m_top.m_ptSize.y-m_bottom.m_ptSize.y-m_thumb.m_ptSize.y;
}
void CGUIScrollbar::UpdateBar(){
    if(!m_total)throw std::domain_error("Scrollbar UpdateBar requires nonzero total");
    const int position=multiply(m_current,GetScrollLength455())/m_total;
    if(m_style)m_thumb.m_ptPos.x=add(position,add(m_top.GetPosX(),m_top.GetSizeX()));
    else m_thumb.m_ptPos.y=add(position,add(m_top.GetPosY(),m_top.GetSizeY()));
}
int CGUIScrollbar::CalcCurrentAmount(int distance){
    return snapAmount(m_total,m_unit,distance,GetScrollLength455());
}
void CGUIScrollbar::SendScrollEvent(WORD id){
    if(m_observer){_event_queue_data event;event.pEventHandler=m_observer;event.pSource=this;event.wEventID=id;CGUIObject::SendEvent(event);}
    m_scrolledTime=clockNow();
}
void CGUIScrollbar::CommitMouseAmount(int requested){
    if(requested==m_current)return;
    SetCurrentAmount(requested);
    // Target compares AFTER updating/clamping current, so an in-range upward
    // track/drag move can still send SCROLLED_DOWN. Preserve that ordering.
    SendScrollEvent(requested<m_current?SCROLLED_UP:SCROLLED_DOWN);
}
void CGUIScrollbar::MouseEvent(_mouse_event& event){
    if(event.id==MOUSE_STROKED){
        if(event.source==&m_top||event.source==&m_bottom){
            m_strokedTime=clockNow();const LONG unit=m_arrowUnit?m_arrowUnit:m_unit;
            SetCurrentAmount(event.source==&m_top?sub(m_current,unit):add(m_current,unit));SendScrollEvent(event.source==&m_top?SCROLLED_UP:SCROLLED_DOWN);
        }else if(event.source==&m_thumb){m_grabOffset=m_style?sub(event.xPos,m_thumb.GetPosX()):sub(event.yPos,m_thumb.GetPosY());m_thumb.SetPressed455(1);}
        else if(event.source==this){LONG distance=m_style?event.xPos-m_thumb.GetSizeX()/2-m_top.GetPosX()-m_top.GetSizeX():event.yPos-m_thumb.GetSizeY()/2-m_top.GetPosY()-m_top.GetSizeY();CommitMouseAmount(CalcCurrentAmount(std::max<LONG>(0,distance)));}
    }else if(event.id==MOUSE_PRESSED){
        if(event.source==&m_top||event.source==&m_bottom){
            if(clockNow()-m_scrolledTime<m_speed)return;
            if(!m_speed)throw std::domain_error("Scrollbar repeat with zero speed");
            const DWORD step=(static_cast<DWORD>(m_arrowUnit?m_arrowUnit:m_unit)*(clockNow()-m_scrolledTime))/m_speed;
            SetCurrentAmount(event.source==&m_top?sub(m_current,static_cast<LONG>(step)):add(m_current,static_cast<LONG>(step)));SendScrollEvent(event.source==&m_top?SCROLLED_UP:SCROLLED_DOWN);
        }
    }else if((event.id==MOUSE_RELEASED||event.id==MOUSE_CLICKED)&&event.source==&m_thumb){
        const LONG distance=m_style?event.xPos-m_grabOffset-m_top.GetPosX()-m_top.GetSizeX():event.yPos-m_grabOffset-m_top.GetPosY()-m_top.GetSizeY();const int requested=CalcCurrentAmount(std::max<LONG>(0,distance));
        if(requested==m_current)UpdateBar();else CommitMouseAmount(requested);m_thumb.SetPressed455(0);
    }
}
void CGUIScrollbar::MouseMotionEvent(_mouse_motion_event& event){
    if(event.id!=MOUSE_DRAG||event.source!=&m_thumb)return;
    const LONG first=m_style?m_top.GetPosX()+m_top.GetSizeX():m_top.GetPosY()+m_top.GetSizeY();const LONG last=m_style?m_bottom.GetPosX()-m_thumb.GetSizeX():m_bottom.GetPosY()-m_thumb.GetSizeY();
    LONG position=sub(m_style?event.xPos:event.yPos,m_grabOffset);
    if(position<first)position=first;else if(position>last)position=last;
    CommitMouseAmount(CalcCurrentAmount(sub(position,first)));
    if(m_style)m_thumb.m_ptPos.x=position;else m_thumb.m_ptPos.y=position;
}
void CGUIScrollbar::SetTopArrowSpriteInfo(SPRITE_INFO* images){m_top.SetSpriteInfoEx(images);m_top.SetSpriteInfoEx(PRESSED,images+1);}
void CGUIScrollbar::SetBottomArrowSpriteInfo(SPRITE_INFO* images){m_bottom.SetSpriteInfoEx(images);m_bottom.SetSpriteInfoEx(PRESSED,images+1);}
void CGUIScrollbar::SetBarSpriteInfo(SPRITE_INFO* image){m_thumb.SetSpriteInfo(image);}
void CGUIScrollbar::SetSprite(CSprite* sprite){m_top.SetSprite(sprite);m_bottom.SetSprite(sprite);m_thumb.GetSpriteInfo()->pSprite=sprite;if(GetSpriteInfo()->pSprite)GetSpriteInfo()->pSprite=sprite;}
BOOL CGUIScrollbar::Draw(RECT& clipping){return CGUIContainer::Draw(clipping)&&m_thumb.Draw(clipping);}
BOOL CGUIScrollbar::Draw(){return CGUIContainer::Draw()&&m_thumb.Draw();}

CGUIScrollbarEX::CGUIScrollbarEX(){
    m_button.AddMouseEventHandler(this);m_button.AddMouseMotionEventHandler(this);
    Add(&m_button);SetStyle(Vertical);
}
void CGUIScrollbarEX::SetSize(LONG width,LONG height){
    CGUIObject::SetSize(width,height);
    if(m_style){
        m_top.SetPos(m_ptPos.x,m_ptPos.y+(height-m_top.GetSizeY())/2);
        m_bottom.SetPos(m_ptPos.x+width-m_bottom.GetSizeX(),m_top.GetPosY());
        m_button.SetPos(m_ptPos.x+m_top.GetSizeX(),m_ptPos.y);
    }else{
        m_top.SetPos(m_ptPos.x+(width-m_top.GetSizeX())/2,m_ptPos.y);
        m_bottom.SetPos(m_top.GetPosX(),m_ptPos.y+height-m_bottom.GetSizeY());
        m_button.SetPos(m_ptPos.x+(width-m_button.GetSizeX())/2,m_ptPos.y+m_top.GetSizeY());
    }
    SetAmount(m_total,m_current);
}
void CGUIScrollbarEX::SetAmount(LONG total,LONG current){
    m_total=std::max<LONG>(0,total);m_current=std::max<LONG>(0,std::min(current,m_total));
    if(!m_total){m_top.RemoveMouseEventHandler();m_bottom.RemoveMouseEventHandler();m_button.RemoveMouseEventHandler();RemoveMouseEventHandler();return;}
    m_top.AddMouseEventHandler(this);m_bottom.AddMouseEventHandler(this);m_button.AddMouseEventHandler(this);AddMouseEventHandler(this);
    if(!IsAddedObject(&m_button)){
        if(m_style)m_button.SetPos(0,m_ptPos.y+(m_ptSize.y-m_button.GetSizeY())/2);
        else m_button.SetPos(m_ptPos.x+(m_ptSize.x-m_button.GetSizeX())/2,0);
        if(m_bEnableFocus)m_button.EnableFocus();else m_button.DisableFocus();
        Add(&m_button);
    }
    if(m_autoThumb){
        if(m_style)m_button.m_ptSize.x=std::max(m_minThumb,m_ptSize.x-m_top.GetSizeX()-m_bottom.GetSizeX()-m_total);
        else m_button.m_ptSize.y=std::max(m_minThumb,m_ptSize.y-m_top.GetSizeY()-m_bottom.GetSizeY()-m_total);
    }
    //EX does not call composite SetSize:its plain button has no6x18 minimum.
    UpdateBar();
}
int CGUIScrollbarEX::GetScrollLength455()const{
    return m_style?m_ptSize.x-m_top.m_ptSize.x-m_bottom.m_ptSize.x-m_button.m_ptSize.x:m_ptSize.y-m_top.m_ptSize.y-m_bottom.m_ptSize.y-m_button.m_ptSize.y;
}
void CGUIScrollbarEX::UpdateBar(){
    if(!m_total)throw std::domain_error("ScrollbarEX UpdateBar requires nonzero total");
    const LONG position=multiply(m_current,GetScrollLength455())/m_total;
    if(m_style)m_button.m_ptPos.x=add(position,add(m_top.GetPosX(),m_top.GetSizeX()));
    else m_button.m_ptPos.y=add(position,add(m_top.GetPosY(),m_top.GetSizeY()));
}
void CGUIScrollbarEX::SetAlpha455(BYTE alpha){setAlpha(m_button,alpha);setAlpha(m_top,alpha);setAlpha(m_bottom,alpha);setAlpha(m_thumb,alpha);setAlpha(*this,alpha);}
void CGUIScrollbarEX::CommitAmount455(int requested){
    if(requested==m_current)return;SetCurrentAmount(requested);SendScrollEvent(requested<m_current?SCROLLED_UP:SCROLLED_DOWN);
}
void CGUIScrollbarEX::MouseEvent(_mouse_event& event){
    if(event.id==MOUSE_STROKED){
        if(event.source==&m_top||event.source==&m_bottom){m_strokedTime=clockNow();const LONG unit=m_arrowUnit?m_arrowUnit:m_unit;SetCurrentAmount(event.source==&m_top?sub(m_current,unit):add(m_current,unit));SendScrollEvent(event.source==&m_top?SCROLLED_UP:SCROLLED_DOWN);}
        else if(event.source==&m_button)m_grabOffset=m_style?sub(event.xPos,m_button.GetPosX()):sub(event.yPos,m_button.GetPosY());
        else if(event.source==this){const LONG distance=m_style?event.xPos-m_button.GetSizeX()/2-m_top.GetPosX()-m_top.GetSizeX():event.yPos-m_button.GetSizeY()/2-m_top.GetPosY()-m_top.GetSizeY();CommitAmount455(CalcCurrentAmount(std::max<LONG>(0,distance)));}
    }else if((event.id==MOUSE_RELEASED||event.id==MOUSE_CLICKED)&&event.source==&m_button){
        const LONG distance=m_style?event.xPos-m_grabOffset-m_top.GetPosX()-m_top.GetSizeX():event.yPos-m_grabOffset-m_top.GetPosY()-m_top.GetSizeY();const int amount=CalcCurrentAmount(std::max<LONG>(0,distance));
        if(amount==m_current)UpdateBar();else CommitAmount455(amount);
    }
    //63AAE0 has no arrow-repeat/MOUSE_PRESSED branch.
}
void CGUIScrollbarEX::MouseMotionEvent(_mouse_motion_event& event){
    if(event.id!=MOUSE_DRAG||event.source!=&m_button)return;
    const LONG first=m_style?m_top.GetPosX()+m_top.GetSizeX():m_top.GetPosY()+m_top.GetSizeY();
    const LONG last=m_style?m_bottom.GetPosX()-m_button.GetSizeX():m_bottom.GetPosY()-m_button.GetSizeY();
    LONG position=sub(m_style?event.xPos:event.yPos,m_grabOffset);
    if(position<first)position=first;else if(position>last)position=last;
    CommitAmount455(CalcCurrentAmount(sub(position,first)));
    if(m_style)m_button.m_ptPos.x=position;else m_button.m_ptPos.y=position;
}

CGUIScrollbarVar::CGUIScrollbarVar(){SetSprite();m_pressed=0;m_middleExtent=0;m_skinWidth=6;m_skinHeight=18;SetStyle(Vertical);}
void CGUIScrollbarVar::SetSprite(){SetSkin455(gSpriteMgr.GetSprite(SP_ID_COMMON));}
void CGUIScrollbarVar::SetSkin455(CSprite* sprite){
    for(unsigned i=0;i<3;++i)for(unsigned mode=0;mode<2;++mode)m_images[i][mode]={sprite,15,static_cast<WORD>(i+3*mode)};
    ApplyMode455(0);
}
void CGUIScrollbarVar::ApplyMode455(DWORD mode){
    setSizedImage(m_capTop,m_images[0][mode]);setSizedImage(m_middle,m_images[1][mode]);setSizedImage(m_capBottom,m_images[2][mode]);
}
void CGUIScrollbarVar::SetSpriteInfo(SPRITE_INFO*){}
void CGUIScrollbarVar::SetSize(LONG width,LONG height){
    CGUIObject::SetSize(width,height);m_skinWidth=std::max<LONG>(6,width);m_skinHeight=std::max<LONG>(18,height);
    m_capTop.SetSize(m_skinWidth,imageHeight(m_capTop));m_capBottom.SetSize(m_skinWidth,imageHeight(m_capBottom));
    //This setter does not relayout,change the amount,or restore the old extent.
}
void CGUIScrollbarVar::SetAmount(LONG total,LONG current){
    m_total=std::max<LONG>(0,total);m_current=std::max<LONG>(0,std::min(current,m_total));
    if(!m_total){Remove(&m_capTop);Remove(&m_middle);Remove(&m_capBottom);Remove(&m_thumb);RemoveMouseEventHandler();return;}
    for(CGUIObject* child:{&m_capTop,static_cast<CGUIObject*>(&m_middle),&m_capBottom})Add(child);
    AddMouseEventHandler(this);m_capTop.SetPos(m_ptPos.x,m_ptPos.y);
    m_middle.SetPos(m_ptPos.x,m_capTop.GetPosY()+imageHeight(m_capTop));m_capBottom.SetPos(m_ptPos.x,m_middle.GetPosY()+m_middle.GetSizeY());
    m_thumb.SetSize(m_capTop.GetSizeX(),add(sub(m_skinHeight,m_total),add(m_capTop.GetSizeY(),m_capBottom.GetSizeY())));
    m_thumb.SetPos(m_ptPos.x,m_ptPos.y);Add(&m_thumb);
    m_middleExtent=sub(m_skinHeight,m_total);m_thumb.AddMouseEventHandler(this);m_thumb.AddMouseMotionEventHandler(this);
}
int CGUIScrollbarVar::GetScrollLength455()const{
    return m_style?m_ptSize.x-m_capTop.m_ptSize.x-m_capBottom.m_ptSize.x-m_middleExtent:m_ptSize.y-m_capTop.m_ptSize.y-m_capBottom.m_ptSize.y-m_middleExtent;
}
int CGUIScrollbarVar::CalculateAmount455(int distance){return snapAmount(m_total,m_unit,distance,GetScrollLength455());}
void CGUIScrollbarVar::CommitAmount455(int requested){if(requested==m_current)return;SetCurrentAmount(requested);SendScrollEvent(requested<m_current?SCROLLED_UP:SCROLLED_DOWN);}
void CGUIScrollbarVar::MouseEvent(_mouse_event& event){
    if(event.id==MOUSE_STROKED){
        if(event.source==&m_thumb){m_pressed=1;ApplyMode455(1);if(!m_style)m_grabOffset=sub(event.yPos,m_thumb.GetPosY());}
        else if(event.source==this){
            if(m_style)throw std::domain_error("ScrollbarVar horizontal track click reads an uninitialized target local");
            const int requested=CalculateAmount455(std::max<LONG>(0,event.yPos-m_thumb.GetSizeY()-m_ptPos.y));CommitAmount455(requested);
            if(!m_total)throw std::domain_error("ScrollbarVar track click requires nonzero total");
            m_thumb.m_ptPos.y=add(multiply(requested,sub(m_ptSize.y,m_thumb.GetSizeY()))/m_total,m_ptPos.y);
        }
    }else if((event.id==MOUSE_RELEASED||event.id==MOUSE_CLICKED)&&event.source==&m_thumb){m_pressed=0;ApplyMode455(0);}
}
void CGUIScrollbarVar::MouseMotionEvent(_mouse_motion_event& event){
    if(event.id!=MOUSE_DRAG||event.source!=&m_thumb)return;
    LONG position=sub(event.yPos,m_grabOffset);const LONG end=m_ptPos.y+m_ptSize.y-m_thumb.GetSizeY();
    if(position<m_ptPos.y)position=m_ptPos.y;else if(position>end)position=end;
    CommitAmount455(CalculateAmount455(sub(position,m_ptPos.y)));m_thumb.m_ptPos.y=position;
}
BOOL CGUIScrollbarVar::Draw(){
    if(!m_middleExtent||!m_middle.GetSpriteInfo()->pSprite)return FALSE;
    m_capTop.SetPos(m_ptPos.x,m_thumb.GetPosY());
    const LONG first=m_capTop.GetPosY()+imageHeight(m_capTop);
    for(LONG i=0;i<m_middleExtent;++i)drawRow(m_middle,m_images[1][m_pressed].pSprite,2,m_images[1][m_pressed].wFrameNo,m_skinWidth,m_ptPos.x,first+i);
    m_middle.SetPos(m_ptPos.x,m_thumb.GetPosY()+m_capTop.GetSizeY());m_capBottom.SetPos(m_ptPos.x,m_middle.GetPosY()+m_middleExtent);
    return CGUIContainer::Draw();
}
