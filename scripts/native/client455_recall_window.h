#pragma once
#include "client455_briefing_window.h"
#include "client455_image_text.h"
#include "userinterface/guicontroller/guiscrollbar.h"
#include "userinterface/guicontroller/guiitem.h"
#include <list>
#include <memory>
#include <cstddef>

// Source owners for455Recall. Private target C++ object layouts are not shared.
class CGUIRecallUnit : public CGUIContainer {
public:
    enum UnitState {Enabled,Disabled,Linked,NoneUnit};
private:
    UnitState m_state=static_cast<UnitState>(-1); // Target pre-setter state is uninitialized.
    DWORD m_index=0xffffffff;
    CGUIText m_name,m_level;
    CGUIItem m_item;
    CGUIObject m_gaugeBase,m_expBase,m_underline,m_cover;
    CGUIObjectEx m_hp,m_fp,m_exp;
    CGUIImageText455 m_hpText,m_fpText,m_expText;
public:
    CGUIRecallUnit();
    ~CGUIRecallUnit();
    void SetSprite();
    void SetUnitState(UnitState);
    UnitState GetUnitState(){return m_state;}
    void SetIndex(DWORD value){m_index=value;}
    DWORD GetIndex(){return m_index;}
    void SetMobName(char*);
    void SetLevel(BYTE);
    void SetItem(DWORD item,DWORD sprite);
    DWORD GetItemID(){return m_item.GetItemID();}
    CGUIItem* GetItem(){return &m_item;}
    void SetHP(DWORD current,DWORD maximum);
    void SetFP(DWORD current,DWORD maximum);
    void SetExp(float percentage);
    float GetExpRate(){return m_exp.GetU()[1];}
    CGUIObject* GetCover(){return &m_cover;}
    CGUIText& Name455(){return m_name;}
    CGUIText& Level455(){return m_level;}
    CGUIObject& GaugeBase455(){return m_gaugeBase;}
    CGUIObject& ExpBase455(){return m_expBase;}
    CGUIObjectEx& HP455(){return m_hp;}
    CGUIObjectEx& FP455(){return m_fp;}
    CGUIObjectEx& Exp455(){return m_exp;}
    CGUIImageText455& HPText455(){return m_hpText;}
    CGUIImageText455& FPText455(){return m_fpText;}
    CGUIImageText455& ExpText455(){return m_expText;}
};

//6AFDF0 consumes name first,then index. Existing source producers address the
//named fields;this internal record is not a network packet or a target overlay.
struct _recall_info {
    char* pName;DWORD dwIndex,dwItemID,dwSpriteID;BYTE byLevel;
    int nCurHP,nMaxHP,nCurFP,nMaxFP;float fExp;
};
static_assert(sizeof(_recall_info)==40&&offsetof(_recall_info,pName)==0&&offsetof(_recall_info,dwIndex)==4&&offsetof(_recall_info,nCurHP)==20,"455Recall source record");

class CGUIRecallWindow : public CGUIWindow,public IScrollObserver {
public:
    typedef std::list<CGUIRecallUnit*> CGUIRecallList;
private:
    std::list<std::unique_ptr<CGUIRecallUnit>> m_units;
    RF455GuiOutlineBoard m_background;
    CGUIText m_title;
    RF455GuiAnimatedImage m_header;
    CGUIButton m_close,m_help;
    CGUIObject m_resize;
    CGUIContainerEx m_viewport;
    CGUIContainer m_content;
    CGUIScrollbar m_scroll;
    void UpdateScrollbar();
    CGUIRecallUnit* Resolve455(DWORD value,BOOL byIndex){return byIndex?GetRecallUnitByIndex(value):GetRecallUnitByItemID(value);}
public:
    CGUIRecallWindow()=default;
    ~CGUIRecallWindow();
    void Init() override;
    void SetSprite() override;
    void SetBound(RECT&) override;
    BOOL TakeInItem(_recall_info*);
    BOOL TakeOutItem(DWORD index);
    BOOL TakeOutLink(DWORD index,BOOL byIndex=TRUE);
    void SetLevel(DWORD index,BYTE value,BOOL byIndex=TRUE);
    void SetHP(DWORD index,int current,int maximum,BOOL byIndex=TRUE);
    void SetFP(DWORD index,int current,int maximum,BOOL byIndex=TRUE);
    void SetExp(DWORD index,float percentage,BOOL byIndex=TRUE);
    void SetItemState(DWORD index,CGUIRecallUnit::UnitState,BOOL byIndex=TRUE);
    void MouseEvent(_mouse_event&) override;
    void ScrollEvent(_scroll_event&) override;
    CGUIRecallUnit* GetRecallUnitByIndex(DWORD);
    CGUIRecallUnit* GetRecallUnitByItemID(DWORD);
    CGUIRecallUnit* GetRecallUnitByEventObj(CGUIObject*);
    std::size_t Count455()const{return m_units.size();}
    CGUIContainerEx& Viewport455(){return m_viewport;}
    CGUIContainer& Content455(){return m_content;}
    CGUIScrollbar& Scrollbar455(){return m_scroll;}
    RF455GuiAnimatedImage& Header455(){return m_header;}
    CGUIText& Title455(){return m_title;}
    CGUIObject& Resize455(){return m_resize;}
    CGUIButton& Close455(){return m_close;}
    CGUIButton& Help455(){return m_help;}
};
