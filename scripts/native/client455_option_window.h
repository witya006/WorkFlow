#pragma once
#include "userinterface/guicontroller/guiwindow.h"
#include "userinterface/guicontroller/guibutton.h"
#include "userinterface/guicontroller/guiscrollbar.h"
#include "client455_briefing_controls.h"
#define TOTAL_CAMERA_NUM 5

struct RF455OptionActions {
    void (*logout)()=nullptr;
    void (*quit)()=nullptr;
    void (*rating)()=nullptr;
    void (*dismissStartupBoard)()=nullptr;
    bool (*blocked)()=nullptr;
};
class CGUIOptionWindow:public CGUIWindow,public IScrollObserver {
public:
    enum SoundOption{Ambient=0,Effect_Snd=1,BGM=2,SOUND_OPTION_NUM=3};
    enum GraphicOption{Gamma,DynamicLighting,Shadow,SeeDist,Bloom,EnvironmentDetail,GRAPHIC_OPTION_NUM};
    enum EtcOption{Whisper=0,Hint=1,Trade=2,Party=3,AutoSeeDist=4,RemoveEnvironment=5,DisableStartupBoard=6,RememberPage=7,ETC_OPTION_NUM=8,
        Guild=8,DetailTexture=9}; // Explicit unrepresented legacy source adapters.
    enum SettingsPage {SoundPage, ImagePage, GraphicsPage, GamePage, HUDPage, PageCount};
private:
    CGUIText m_title,m_soundTitle,m_soundLabels[5],m_graphicTitle,m_graphicLabels[6],m_etcTitle,m_etcLabels[8],m_cameraTitle,m_targetTitle;
    RF455GuiAnimatedImage m_header;
    CGUIButton m_close,m_help;
    CGUIButtonEx m_actionsButtons[3];
    CGUIScrollbar m_sound[3],m_graphic[6];
    CGUIObject m_eaxIcons[2],m_specialIcons[2],m_marks[6],m_etc[8],m_cameras[5],m_targetModes[2],m_targetFilters[5];
    CGUIText m_eaxLabels[2],m_specialLabels[2],m_targetModeLabels[2],m_targetFilterLabels[5];
    BYTE m_camera=0,m_eax=0,m_special=0,m_targetMode=255,m_targetMask=255;
    BOOL m_legacyFlags[2]={FALSE,FALSE},m_logoutRestricted=FALSE;
    unsigned m_etcCount=8;
    bool m_ratingVisible=false;
    RF455OptionActions m_actions;
    struct SettingsSnapshot {
        LONG sound[3]={160,160,160},graphics[6]={2,3,2,4,0,0};
        BOOL flags[8]={FALSE,TRUE,FALSE,FALSE,TRUE,FALSE,FALSE,FALSE};
        BYTE camera=1;
        unsigned msaa=4,width=1920,height=1080;
        bool enhanced=false,lobbyPost=false,lobbyDiagnostics=true,vsync=false;
    };
    CGUIContainer m_pages[PageCount];
    CGUIButtonEx m_tabs[PageCount],m_apply,m_cancel,m_resolution[2],m_vsync[2],m_msaa[3],m_lighting[2],m_lobbyQuality[2];
    CGUIText m_resolutionTitle,m_vsyncTitle,m_msaaTitle,m_lightingTitle,m_lobbyQualityTitle,m_notice,m_status,m_closeLabel,m_pageNote[PageCount];
    CGUIObject m_modernHeader,m_divider;
    CGUIButtonEx m_diagnostics[2];CGUIText m_diagnosticsTitle;
    SettingsSnapshot m_applied;
    SettingsPage m_page=SoundPage;
    unsigned m_requestedMsaa=4,m_requestedWidth=1920,m_requestedHeight=1080;
    bool m_enhanced=false,m_lobbyPost=false,m_editing=false,m_initialized=false,m_showDiagnostics=true,m_requestedVsync=false;
    SettingsSnapshot Capture455();
    void Restore455(const SettingsSnapshot&);
    void RememberExternal455();
    bool Persist455(const SettingsSnapshot&);
    void Layout455();
    void SetStatus455(const wchar_t*,const char*);
    void Send455(UINT,WPARAM=0);
public:
    CGUIOptionWindow();
    ~CGUIOptionWindow();
    void Init() override;
    void SetSprite() override;
    void Update() override;
    void Open() override;
    void Close() override;
    void SetPage455(SettingsPage);
    bool Apply455();
    void Cancel455();
    CGUIButtonEx& Tab455(unsigned i){return m_tabs[i];}
    CGUIContainer& Page455(unsigned i){return m_pages[i];}
    CGUIButtonEx& ApplyButton455(){return m_apply;}
    CGUIButtonEx& CancelButton455(){return m_cancel;}
    CGUIButtonEx& Resolution455(unsigned i){return m_resolution[i];}
    CGUIButtonEx& VSync455(unsigned i){return m_vsync[i];}
    bool RequestedVSync455()const{return m_requestedVsync;}
    CGUIButtonEx& Multisampling455(unsigned i){return m_msaa[i];}
    CGUIButtonEx& Lighting455(unsigned i){return m_lighting[i];}
    CGUIButtonEx& LobbyQuality455(unsigned i){return m_lobbyQuality[i];}
    CGUIButtonEx& Diagnostics455(unsigned i){return m_diagnostics[i];}
    unsigned RequestedMultisampling455()const{return m_requestedMsaa;}
    SettingsPage SelectedPage455()const{return m_page;}
    void SetSoundOption(SoundOption,float);
    float GetSoundOption(SoundOption);
    void SetGraphicOption(GraphicOption,float);
    float GetGraphicOption(GraphicOption);
    void SwitchOn(EtcOption,BOOL);
    BOOL IsSwitchOn(EtcOption);
    void SelectCamera(BYTE);
    BYTE GetSelectedCamera(){return m_editing?m_applied.camera:m_camera;}
    void SelectEax455(BYTE);
    void SelectSpecial455(BYTE);
    void SetTargetingMode455(int);
    void SetTargetingFilters455(BYTE);
    void SetTargetingFilter455(int,WPARAM);
    BYTE GetTargetingMode455()const{return m_targetMode;}
    BOOL IsTargetingFilter455(BYTE index)const{return (m_targetMask&(1u<<index))!=0;}
    void SetActions455(RF455OptionActions actions){m_actions=actions;}
    void SetLogoutRestricted455(BOOL restricted){m_logoutRestricted=restricted;}
    void MouseEvent(_mouse_event&) override;
    void ScrollEvent(_scroll_event&) override;
    CGUIScrollbar& Sound455(unsigned i){return m_sound[i];}
    CGUIScrollbar& Graphic455(unsigned i){return m_graphic[i];}
    CGUIObject& Etc455(unsigned i){return m_etc[i];}
    CGUIText& EtcLabel455(unsigned i){return m_etcLabels[i];}
    CGUIObject& Camera455(unsigned i){return m_cameras[i];}
    CGUIObject& Eax455(unsigned i){return m_eaxIcons[i];}
    CGUIObject& Special455(unsigned i){return m_specialIcons[i];}
    CGUIObject& TargetMode455(unsigned i){return m_targetModes[i];}
    CGUIObject& TargetFilter455(unsigned i){return m_targetFilters[i];}
    CGUIButtonEx& Action455(unsigned i){return m_actionsButtons[i];}
    CGUIButton& Close455(){return m_close;}
    CGUIButton& Help455(){return m_help;}
    CGUIText& Title455(){return m_title;}
    RF455GuiAnimatedImage& Header455(){return m_header;}
    unsigned VisibleEtc455()const{return m_etcCount;}
    bool HasRatingProvider455()const{return m_actions.rating!=nullptr;}
};
