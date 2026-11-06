#pragma once
#include "userinterface/guicontroller/guiwindow.h"
#include "userinterface/guicontroller/guibutton.h"
#include "client455_briefing_controls.h"
#include "client455_gui_text_typing_board.h"
#include "client455_tutorial_board.h"
#include <memory>

struct RF455BriefingReplay {DWORD (*milliseconds)()=nullptr;int (*random)()=nullptr;};
RF455BriefingReplay RF455_SetBriefingReplay(RF455BriefingReplay);

class RF455GuiOutlineBoard : public CGUIContainer {
    LONG m_width=1,m_inset=1;DWORD m_color=0;
public:
    void SetOutline455(LONG width,LONG inset,DWORD color){m_width=width;m_inset=inset;m_color=color;}
    BOOL Draw() override;
    BOOL Draw(RECT&) override{return Draw();}
};

// Semantic source ownership, not a2272-byte overlay of the455 object.
class CGUIBriefingWindow : public CGUIWindow {
    CSprite m_tutorialSprite,m_portraits[3];
    bool m_tutorialLoaded=false,m_portraitLoaded[3]={false,false,false};
    CGUIText m_title;
    RF455GuiOutlineBoard m_portraitFrame,m_keyFrame;
    RF455GuiAnimatedImage m_portrait;
    CGUIObject m_portraitOverlay;
    CGUIBriefingBoard m_main;
    CGUITextTypingBoard m_typing;
    CGUIButton m_close;
    CGUIButtonEx m_next;
    std::unique_ptr<CGUITutorialKeyBoard> m_keys;
    BOOL m_autoSize=TRUE,m_ready=FALSE;
    BYTE m_pages=0,m_page=0,m_race=255,m_role=255;
    DWORD m_portraitStart=0;
    void SetReady455(BOOL);
    void FrameSkin455(BOOL);
    void Layout455();
    void PortraitFrame455(BYTE);
    void UpdatePortrait455();
public:
    CGUIBriefingWindow()=default;
    ~CGUIBriefingWindow();
    void Init() override;
    void RestoreSprite() override;
    void Open() override;
    void Close() override;
    void Update() override;
    void MouseEvent(_mouse_event&) override;
    void SetTitle455(const char*);
    void SetAutoSize455(BOOL value){m_autoSize=value;}
    BOOL GetAutoSize455()const{return m_autoSize;}
    void Clear455();
    void SetText455(unsigned count,CGUITextInfo*);
    bool SelectPage455(BYTE);
    void Continue455();
    // Avatar race must come from the real caller;no fabricated Avatar provider.
    void ShowPortrait455(BOOL enabled,BYTE role,BYTE avatarRace);
    void ShowKeyFrame455(BOOL);
    void SetKeyRows455(BYTE,const std::array<std::array<BYTE,2>,2>&);
    void ShowKeys455(BOOL);
    BYTE GetPageCount455()const{return m_pages;}
    BYTE GetPage455()const{return m_page;}
    BOOL IsReady455()const{return m_ready;}
    BYTE GetPortraitRace455()const{return m_race;}
    BYTE GetPortraitRole455()const{return m_role;}
    DWORD GetPortraitStart455()const{return m_portraitStart;}
    CGUITextTypingBoard& GetTyping455(){return m_typing;}
    CGUIBriefingBoard& GetMain455(){return m_main;}
    CGUIText& GetTitle455(){return m_title;}
    CGUIButton& GetClose455(){return m_close;}
    CGUIButtonEx& GetNext455(){return m_next;}
    CGUITutorialKeyBoard* GetKeys455(){return m_keys.get();}
    RF455GuiAnimatedImage& GetPortrait455(){return m_portrait;}
    RF455GuiOutlineBoard& GetPortraitFrame455(){return m_portraitFrame;}
    RF455GuiOutlineBoard& GetKeyFrame455(){return m_keyFrame;}
};

class RF455TutorialBriefingWindow final : public RF455TutorialBriefingView {
    CGUIBriefingWindow m_window;
public:
    CGUIWindow& window()override{return m_window;}
    CGUIBriefingWindow& briefing(){return m_window;}
    void setAutoSize(bool value)override{m_window.SetAutoSize455(value);}
    bool showRichMessage(const RF455TutorialMessage&,bool closeAllowed)override;
    bool showKeyGuide(const RF455TutorialKeyGuide&)override;
};
