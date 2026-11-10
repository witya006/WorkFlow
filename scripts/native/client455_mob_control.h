#pragma once
#include "userinterface/guicontroller/guiwindow.h"
#include "userinterface/guicontroller/guibutton.h"
#include "client455_image_text.h"

// Typed source owners; the target's private object layout is not overlaid.
class CGUIMobControl:public CGUIWindow {
public:
    enum Command{Cmd_Target,Cmd_Action,Cmd_Follow,TOTAL_COMMAND_NUM};
    enum MobState{Action,Follow};
private:
    CGUIObject m_board,m_resourceIcon,m_expRemainder,m_commandIcon,m_commandBoard;
    CGUIText m_name,m_resourceText;
    CGUIImageText455 m_level,m_hpText,m_fpText,m_expText;
    CGUIObjectEx m_resourceGauge,m_hp,m_fp,m_exp;
    CGUIContainerEx m_commandViewport;
    CGUIContainer m_commands;
    CGUIButton m_commandButtons[TOTAL_COMMAND_NUM];
    BOOL m_open=FALSE;
    void OpenCmdBoard(BOOL);
public:
    CGUIMobControl()=default;
    ~CGUIMobControl();
    void Init() override;
    void SetSprite() override;
    void SetMobName(char*);
    void SetLevel(BYTE);
    void SetHP(int current,int maximum);
    void SetFP(int current,int maximum);
    void SetExp(float fraction);
    // 4711F0 produces this extra gauge from equipped records12/13. Its complete
    // gameplay semantics/providers remain open; do not call it HP,FP or EXP.
    void SetResource455(int current,int maximum);
    void SetMobState(MobState); // Legacy declaration has no observed caller/body.
    void MouseEvent(_mouse_event&) override;
    BOOL IsCrossed(LONG,LONG) override;
    void Update() override;
    CGUIObjectEx& HP455(){return m_hp;}
    CGUIObjectEx& FP455(){return m_fp;}
    CGUIObjectEx& Exp455(){return m_exp;}
    CGUIObject& ExpRemainder455(){return m_expRemainder;}
    CGUIObjectEx& Resource455(){return m_resourceGauge;}
    CGUIObject& ResourceIcon455(){return m_resourceIcon;}
    CGUIText& ResourceText455(){return m_resourceText;}
    CGUIText& Name455(){return m_name;}
    CGUIImageText455& Level455(){return m_level;}
    CGUIImageText455& HPText455(){return m_hpText;}
    CGUIImageText455& FPText455(){return m_fpText;}
    CGUIImageText455& ExpText455(){return m_expText;}
    CGUIObject& CommandIcon455(){return m_commandIcon;}
    CGUIObject& CommandBackground455(){return m_commandBoard;}
    CGUIButton& Command455(unsigned i){return m_commandButtons[i];}
    CGUIContainerEx& CommandViewport455(){return m_commandViewport;}
    CGUIContainer& CommandContent455(){return m_commands;}
    BOOL CommandsOpen455()const{return m_open;}
};
