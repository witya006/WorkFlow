#ifndef __GUISCROLLBAR_H__
#define __GUISCROLLBAR_H__
#include "GUIContainer.h"
#include "GUIButton.h"

typedef DWORD (*RF455ScrollbarClock)();
RF455ScrollbarClock RF455_SetScrollbarClock(RF455ScrollbarClock provider);

class CGUIScrollbarButton : public CGUIContainer {
    CGUIObject m_segments[3];
    WORD m_frames[3][2]={{44,47},{45,48},{46,49}};
    BOOL m_segmented=FALSE;
    BYTE m_pressed=0;
    CSprite* m_skin=nullptr;
public:
    CGUIScrollbarButton();
    void SetSize(LONG width,LONG height);
    void SetSize(POINT& size){SetSize(size.x,size.y);}
    void SetPressed455(BYTE pressed);
    void SetSegmented455(CSprite* sprite);
    BOOL Draw();
    BOOL Draw(RECT& clipping){return Draw();}
    BYTE GetPressed455() const{return m_pressed;}
    CGUIObject& GetSegment455(unsigned index){return m_segments[index];}
};

class CGUIScrollbar : public CGUIContainer, public IMouseObserver, public IMouseMotionObserver {
public:
    enum Style {Vertical,Horizontal};
private:
    Style m_style=Vertical;
    CGUIButton m_top,m_bottom;
    CGUIScrollbarButton m_thumb;
    BOOL m_autoThumb=TRUE;
    LONG m_minThumb=20,m_total=0,m_current=0;
    WORD m_unit=1,m_arrowUnit=0;
    DWORD m_scrolledTime=0,m_strokedTime=0;
    WORD m_speed=150;
    int m_grabOffset=0;
    IScrollObserver* m_observer=nullptr;

    int CalcCurrentAmount(int distance);
    void CommitMouseAmount(int requested);
public:
    CGUIScrollbar();
    ~CGUIScrollbar();
    void SetStyle(Style style);
    void SetBarColor455(DWORD color){m_thumb.SetARGB(color);}
    void SetBarSize(POINT& size){m_thumb.SetSize(size);}
    void SetTopArrowSize(POINT& size){m_top.SetSize(size);}
    void SetBottomArrowSize(POINT& size){m_bottom.SetSize(size);}
    int GetMinSize();
    void SetSize(POINT& size){SetSize(size.x,size.y);}
    void SetSize(LONG width,LONG height);
    void SetBound(RECT& bound);
    void AddScrollHandler(IScrollObserver* observer){m_observer=observer;}
    void SetTopArrowSpriteInfo(SPRITE_INFO* images);
    void SetBottomArrowSpriteInfo(SPRITE_INFO* images);
    void SetBarSpriteInfo(SPRITE_INFO* image);
    void SetSprite(CSprite* sprite);
    void SetScrollSpeed(WORD speed){if(speed)m_speed=speed;}
    void SetAdjustmentUnit(WORD unit){m_unit=unit;}
    WORD GetAdjustmentUnit(){return m_unit;}
    void SetArrowAdjustmentUnit(WORD unit){m_arrowUnit=unit;}
    void SetTotalAmount(LONG total){SetAmount(total,m_current);}
    void SetCurrentAmount(LONG current){SetAmount(m_total,current);}
    void SetAmount(LONG total,LONG current);
    LONG GetTotalAmount(){return m_total;}
    LONG GetCurrentAmount(){return m_current;}
    void UpdateBar();
    void MouseEvent(_mouse_event& event);
    void MouseMotionEvent(_mouse_motion_event& event);
    void SendScrollEvent(WORD id);

    // Named source interfaces for recovered properties/geometry and replay.
    void SetAutoThumb455(BOOL enabled){m_autoThumb=enabled;}
    void SetMinimumThumb455(LONG minimum);
    LONG GetMinimumThumb455() const{return m_minThumb;}
    int GetScrollLength455() const;
    int CalculateAmount455(int distance){return CalcCurrentAmount(distance);}
    DWORD GetLastScrollTime455() const{return m_scrolledTime;}
    DWORD GetStrokeTime455() const{return m_strokedTime;}
    CGUIButton& GetTopArrow455(){return m_top;}
    CGUIButton& GetBottomArrow455(){return m_bottom;}
    CGUIScrollbarButton& GetThumb455(){return m_thumb;}
    BOOL Draw();
    BOOL Draw(RECT& clipping);
};
#endif
