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
    void Send455(UINT,WPARAM=0);
public:
    CGUIOptionWindow();
    ~CGUIOptionWindow();
    void Init() override;
    void SetSprite() override;
    void Update() override;
    void SetSoundOption(SoundOption,float);
    float GetSoundOption(SoundOption);
    void SetGraphicOption(GraphicOption,float);
    float GetGraphicOption(GraphicOption);
    void SwitchOn(EtcOption,BOOL);
    BOOL IsSwitchOn(EtcOption);
    void SelectCamera(BYTE);
    BYTE GetSelectedCamera(){return m_camera;}
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
