#pragma once
#include "userinterface/guicontroller/guiwindow.h"
#include "userinterface/guicontroller/guibutton.h"
#include "client455_linker_owners.h"
#include "client455_hotbar.h"
#include "client455_image_text.h"
class CLinkBoard;
BOOL RF455_LinkerIconDelaying455(CGUIItem*);

class CGUILinkWindow455:public CGUIItemWindow {
    struct Bank {CGUIContainer row;CGUIObject decoration;CGUIButton pin;CGUIObject selector;CGUIImageText455 label;};
    Bank banks[5];
    RF455LinkerIconSlots icons;
    RF455HotbarWindowState state;
    CGUIContainer mainRow;
    CGUIButton expandButton,allButton,nextButton,previousButton;
    CGUIObject numberAnchor;
    CGUIImageText455 number;
    CLinkBoard* owner=nullptr;
    BOOL expanded=FALSE,initialized=FALSE;
    float scale=1;
    void SetButton455(CGUIButton&,BYTE,WORD,WORD,WORD);
    void BankVisual455(BYTE);
    void ExpandVisual455();
    void Reflow455();
public:
    CGUILinkWindow455();
    void BindBoard455(CLinkBoard* board){owner=board;}
    RF455LinkerIconSlots& LinkerIcons455(){return icons;}
    RF455HotbarWindowState& HotbarState455(){return state;}
    void Init()override;
    void SetSprite()override;
    void Layout455(LONG viewportWidth);
    float Scale455()const{return scale;}
    BOOL Expanded455()const{return expanded;}
    void SetExpanded455(BOOL);
    void SelectBank455(BYTE);
    void CycleBank455(BOOL next);
    void SetBankFlag455(BYTE,int);
    void ResetBankFlags455();
    void MouseEvent(_mouse_event&)override;
    // This seam receives the real key/drag state in production;the native
    // harness can exercise the same dispatch without changing global keys.
    void DispatchMouse455(_mouse_event&,BOOL drag,BOOL control,BOOL shift,BOOL alt);
    virtual BOOL UseItem455(BYTE,BYTE);
    BOOL FindIcon455(CGUIObject*,BYTE&,BYTE&);
    BOOL TakeInItem(BYTE bank,BYTE slot,CGUIItem* source){return icons.takeIn(bank,slot,source);}
    BOOL TakeInItem(BYTE slot,CGUIItem* source){return TakeInItem(state.active<5?state.active:0,slot,source);}
    BOOL TakeInItem(BYTE,BYTE,DWORD,DWORD,BYTE,BYTE=NONE_LEVEL)override{return FALSE;} //667420
    BOOL TakeOutItem(BYTE bank,BYTE slot,BYTE=0,CGUIItem* =nullptr)override{return icons.takeOut(bank,slot);}
    BOOL TakeOutItem(BYTE slot){return TakeOutItem(state.active<5?state.active:0,slot);}
    CGUIItem* GetItem(BYTE bank,BYTE slot)override{return icons.get(bank,slot);}
    CGUIItem* GetItem(BYTE slot){return GetItem(state.active<5?state.active:0,slot);}
    CGUIObject* Control455(unsigned kind,BYTE bank=0);
};
