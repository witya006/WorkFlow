#pragma once
#include "client455_gui_tab_board.h"
#include "client455_briefing_window.h"
#include "client455_image_text.h"

class CGUICharInfoWindow;
// Semantic source owners, not a binary overlay of the three embedded455 pages.
// Action/equipment population and tooltips remain separate unported contracts.
class RF455CharInfoView {
    CGUICharInfoWindow& owner;
    bool ready=false;
    void InitMain455();
    void InitPage455(CGUITabBoard455&,BYTE count,const unsigned* titles);
public:
    struct MasteryRow {CGUIObject back;CGUIObjectEx bar;CGUIImageText455 percent;};
    RF455GuiOutlineBoard background;
    RF455GuiAnimatedImage header,highlight;
    CGUIObject tabs[3];
    CGUITabBoard455 main,actions,equipment;
    CGUIText titles[23],extraTitles[7],extraValues[7],resistNames[4];
    CGUIObject battleHeader,makeHeader,resistBack[4];
    CGUIObjectEx resistBar[4];
    MasteryRow battle[6],make[3];
    WORD battleMaximum[6]={},makeMaximum[3]={};
    BYTE selected=255;
    explicit RF455CharInfoView(CGUICharInfoWindow& window):owner(window){}
    ~RF455CharInfoView();
    void Init455();
    void SetSprite455();
    void SetMainSprite455();
    void SetBound455(RECT&);
    void SelectPage455(BYTE);
    void RefreshRace455(BYTE);
    void SetBattle455(BYTE,WORD current,WORD maximum);
    void SetMake455(BYTE,WORD current,WORD maximum);
    void SetBattleExp455(BYTE,float);
    void SetMakeExp455(BYTE,float);
    void SetResist455(BYTE,int current,int minimum,int maximum);
    void SetResistText455(BYTE,int current);
    CGUITabBoard455* Page455(BYTE page){return page==0?&main:page==1?&actions:page==2?&equipment:nullptr;}
    bool Ready455()const{return ready;}
};
