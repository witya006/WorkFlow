#pragma once
#include "userinterface/guicontroller/guicontainer.h"
#include "userinterface/guicontroller/guitext.h"
#include "userinterface/guicontroller/guiscrollbar.h"
#include <memory>
#include <vector>

struct RF455TabSprite {BYTE id=255;WORD action=0,frame=0;};
//620230..6214D4: source-owned expandable sections and scroll owner.
//Private1268/492-byte target layouts are not shared with the modern client.
class CGUITabBoard455:public CGUIContainerEx,public IScrollObserver,public IMouseObserver {
    struct Group {CGUIContainer root;CGUIObject header;CGUIText label;CGUIContainer content;};
    CGUIContainer body;
    CGUIScrollbar scroll;
    std::vector<std::unique_ptr<Group>> groups;
    RF455TabSprite skin[2];
    void BindHeader455(CGUIObject&,const RF455TabSprite&);
public:
    CGUITabBoard455()=default;
    ~CGUITabBoard455();
    virtual void Init455(BYTE count,LONG contentWidth,LONG headerHeight,LONG width,LONG height);
    void Clear455();
    virtual void SetSize(LONG width,LONG height);
    void SetSize(POINT& size){SetSize(size.x,size.y);}
    void SetBound(RECT&)override;
    void SetHeaderSprites455(const RF455TabSprite& collapsed,const RF455TabSprite& expanded);
    void SetTitle455(BYTE,const char*,DWORD color);
    BOOL IsOpened455(BYTE)const;
    void SetOpened455(BYTE,BOOL);
    void Reflow455();
    void RepositionScroll455();
    CGUIContainer* Content455(BYTE);
    CGUIContainer* Group455(BYTE);
    CGUIObject* Header455(BYTE);
    CGUIText* Label455(BYTE);
    CGUIScrollbar& Scrollbar455(){return scroll;}
    unsigned Count455()const{return unsigned(groups.size());}
    void ScrollEvent(_scroll_event&)override;
    void MouseEvent(_mouse_event&)override;
};
