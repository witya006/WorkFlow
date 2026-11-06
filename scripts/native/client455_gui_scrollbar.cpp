#include "userinterface/guicontroller/guiscrollbar.h"
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
            const double ratio=static_cast<double>(m_skin->GetSpriteOrgXL())/m_skin->GetSpriteXL();
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
    // The0.7 container lacks455 parent mouse-event bubbling. These explicit
    // arrow observers are the owned adapter for the recovered scrollbar rules.
    AddMouseEventHandler(this);m_top.AddMouseEventHandler(this);m_bottom.AddMouseEventHandler(this);
    if(!IsAddedObject(&m_thumb)){
        if(m_style)m_thumb.SetPos(0,m_ptPos.y+(m_ptSize.y-m_thumb.GetSizeY())/2);
        else m_thumb.SetPos(m_ptPos.x+(m_ptSize.x-m_thumb.GetSizeX())/2,0);
        if(m_bEnableFocus)m_thumb.EnableFocus();else m_thumb.DisableFocus();
        m_thumb.Show(IsShow()); //0.7 Add lacks455 child show inheritance.
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
    const float amount=scaledDistance(m_total,distance,GetScrollLength455());const int current=truncateTarget(amount);
    if(current>=m_total)return m_total;
    if(m_total<static_cast<int>(m_unit))return smallUpperHalf(amount,m_total)?m_total:0;
    if(!m_unit)throw std::domain_error("Scrollbar zero adjustment modulo is outside verified domain");
    int rounded=sub(current,current%m_unit);
    if(roundUnitUp(amount,rounded,m_unit)){rounded=add(rounded,m_unit);if(rounded>m_total)rounded=m_total;}
    return rounded;
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
