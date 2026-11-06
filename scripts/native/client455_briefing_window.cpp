#include "client455_briefing_window.h"
#include "client455_language.h"
#include "client455_modal.h"
#include "client455_sprites.h"
#include "client455_text_metrics.h"
#include "userinterface/spritemgr.h"
#include "userinterface/guicontroller/guiscreen.h"
#include <algorithm>
#include <cmath>
#include <cstdlib>
#include <cstring>
#include <limits>
#include <stdexcept>

extern CSpriteMgr* g_pUiSpriteMgr;
extern CGUIScreen* g_pUiScreen;
namespace {
RF455BriefingReplay replay;
DWORD clockNow(){return replay.milliseconds?replay.milliseconds():timeGetTime();}
int randomNow(){return replay.random?replay.random():std::rand();}
CSprite* common(){if(!g_pUiSpriteMgr)throw std::logic_error("455 briefing requires common sprite manager");return g_pUiSpriteMgr->GetSprite(SP_ID_COMMON);}
void load(CSprite& sprite,unsigned id){char path[260];if(!RF455_SelectSpritePath(id,path,sizeof(path)))throw std::logic_error("455 briefing sprite path");sprite.LoadSprite(path);}
void setAlpha(CGUIObject& object,BYTE alpha){object.SetARGB((object.GetARGB()&0xffffff)|(DWORD(alpha)<<24));}
}
RF455BriefingReplay RF455_SetBriefingReplay(RF455BriefingReplay value){const auto old=replay;replay=value;return old;}
BOOL RF455GuiOutlineBoard::Draw(){
    if(!IsShow())return FALSE;CGUIContainer::Draw();
    const LONG l=GetPosX()+m_inset,r=GetPosX()+GetSizeX()-m_inset,t=GetPosY()+m_inset,b=GetPosY()+GetSizeY()-m_inset;
    Draw2DRectangle(l,t,l+m_width,b,m_color);Draw2DRectangle(r-m_width,t,r,b,m_color);
    Draw2DRectangle(l+m_width,t,r-m_width,t+m_width,m_color);Draw2DRectangle(l+m_width,b-m_width,r-m_width,b,m_color);return TRUE;
}
CGUIBriefingWindow::~CGUIBriefingWindow(){
    m_keyFrame.RemoveAll();RemoveAll();
    if(m_tutorialLoaded)m_tutorialSprite.ReleaseSprite();
    for(unsigned i=0;i<3;++i)if(m_portraitLoaded[i])m_portraits[i].ReleaseSprite();
}
void CGUIBriefingWindow::FrameSkin455(BOOL full){m_main.SetCaps455(common(),full);}
void CGUIBriefingWindow::RestoreSprite(){
    FrameSkin455(TRUE);RF455_ConfigureModalButton(m_close,true);
    SPRITE_INFO info={common(),9,8};m_portraitOverlay.SetSpriteInfo(&info);
    auto* sprite=info.pSprite;sprite->SetAction(9);sprite->SetFrame(8);m_portraitOverlay.SetSize(sprite->GetSpriteOrgXL(),sprite->GetSpriteOrgYL());
}
void CGUIBriefingWindow::Init(){
    RestoreSprite();CGUIObject::SetSize(462,207);m_main.SetSize(GetSizeX(),GetSizeY());
    m_typing.SetSize(m_main.GetSizeX(),m_main.GetSizeY()-2*m_main.GetUpper455().GetSizeY());
    m_keyFrame.SetSize(140,207);m_portraitFrame.SetSize(134,134);m_portraitOverlay.SetSize(128,128);
    m_portraitFrame.SetOutline455(1,0,0xff5a5857);m_portraitFrame.SetARGB(0xff050505);setAlpha(m_portraitFrame,96);
    m_portraitOverlay.SetPos(m_portraitFrame.GetPosX()+3,m_portraitFrame.GetPosY()+3);m_portrait.SetPos(m_portraitOverlay.GetPosX(),m_portraitOverlay.GetPosY());
    m_portraitFrame.Add(&m_portrait);m_portraitFrame.Add(&m_portraitOverlay);
    m_next.SetSize(45,20);m_title.SetPos(m_main.GetPosX()+20,m_main.GetPosY()+11);
    m_typing.SetPos(m_main.GetPosX(),m_main.GetPosY()+m_main.GetUpper455().GetSizeY());
    m_close.AddMouseEventHandler(this);m_next.AddMouseEventHandler(this);
    m_main.Add(&m_title);m_main.Add(&m_typing);m_main.Add(&m_close);m_main.Add(&m_next);Add(&m_main);
    m_title.GetFont()->dwColor=0xffc7c6b6;m_main.SetColors455(0xff222628,0xff5a5857);
    m_keyFrame.SetARGB(0xff222628);m_keyFrame.SetOutline455(1,1,0xff5a5857);
    m_next.SetLabelColor(DWORD(-3431550));m_next.SetLabelHoveredColor(DWORD(-13694));m_main.SetBorder455(1,3);
    m_typing.SetMargin(25,15);m_typing.SetColumnGap(5);m_title.DisableFocus();m_typing.DisableFocus();
    SetMoveObject(&m_main);SetMovable(TRUE);m_main.SetAlpha455(216);setAlpha(m_keyFrame,216);Layout455();
}
void CGUIBriefingWindow::Layout455(){
    if(IsAddedObject(&m_portraitFrame)){
        FrameSkin455(FALSE);m_portraitFrame.SetPos(m_main.GetPosX()+15,m_main.GetPosY()+(m_main.GetSizeY()-m_portraitFrame.GetSizeY())/2);
        m_typing.SetPos(m_portraitFrame.GetPosX()+m_portraitFrame.GetSizeX(),m_typing.GetPosY());
    }else {FrameSkin455(TRUE);m_typing.SetPos(m_main.GetPosX(),m_typing.GetPosY());}
    m_main.SetSize(m_main.GetUpper455().GetSizeX(),m_main.GetSizeY());LONG width=m_main.GetSizeX();
    if(IsAddedObject(&m_keyFrame)){width+=m_keyFrame.GetSizeX();m_keyFrame.SetPos(m_main.GetPosX()+m_main.GetSizeX(),GetPosY());}
    CGUIObject::SetSize(width,m_main.GetSizeY());m_close.SetPos(m_main.GetPosX()+m_main.GetSizeX()-m_close.GetSizeX()-12,m_main.GetPosY()+10);
    m_next.SetPos(m_main.GetPosX()+m_main.GetSizeX()-m_next.GetSizeX()-7,GetPosY()+GetSizeY()-m_next.GetSizeY()-6);
}
void CGUIBriefingWindow::SetTitle455(const char* text){m_title.SetString(const_cast<char*>(text));}
void CGUIBriefingWindow::Clear455(){m_typing.Clear();m_pages=m_page=0;}
void CGUIBriefingWindow::SetReady455(BOOL value){m_ready=value;m_next.SetLabel(const_cast<char*>(RF455_GetNormalLanguagePack()->get(value?106:1059)));}
void CGUIBriefingWindow::SetText455(unsigned count,CGUITextInfo* text){
    if(count&& !text)throw std::invalid_argument("455 briefing text array missing");Clear455();
    for(unsigned i=0;i<count;++i)m_typing.InsertText(&text[i]);
    if(m_autoSize){m_typing.SetSize(m_typing.GetSizeX(),6*(RF455_DefaultTextHeight()+m_typing.GetColumnGap())+2*m_typing.GetMarginY());
        m_main.SetSize(m_main.GetSizeX(),m_typing.GetSizeY()+2*m_main.GetUpper455().GetSizeY());Layout455();}
    const int visible=m_typing.GetVisibleLines455(),total=m_typing.GetTotalLineNum();
    m_pages=visible?static_cast<BYTE>(total/visible+(total%visible?1:0)):0;m_page=0;if(IsShow())SelectPage455(0);
}
bool CGUIBriefingWindow::SelectPage455(BYTE page){
    if(!m_pages){SetReady455(TRUE);return true;}if(page>=m_pages)return false;m_page=page;
    const int first=page*m_typing.GetVisibleLines455(),last=(std::min)(first+m_typing.GetVisibleLines455()-1,m_typing.GetTotalLineNum()-1);
    m_typing.SetViewedLine455(static_cast<WORD>(first));m_typing.SetTypingInterval455(80);
    if(!m_typing.StartTyping455(first,last,page?0:250))throw std::domain_error("455 briefing typing range unavailable");SetReady455(FALSE);return true;
}
void CGUIBriefingWindow::Continue455(){
    if(!m_pages || (m_typing.IsTypingFinished455()&&m_page+1==m_pages))PostUIMessage(0x1201,LPARAM(1));
    else if(m_typing.IsTypingFinished455())SelectPage455(static_cast<BYTE>(m_page+1));
    else {m_typing.FinishTyping455();SetReady455(TRUE);}
}
void CGUIBriefingWindow::Open(){CGUIWindow::Open();if(!m_page)SelectPage455(0);}
void CGUIBriefingWindow::Close(){CGUIWindow::Close();m_race=m_role=255;}
void CGUIBriefingWindow::MouseEvent(_mouse_event& event){
    CGUIWindow::MouseEvent(event);if(event.id!=4)return;
    if(event.source==&m_close)PostUIMessage(0x1201,LPARAM(1));else if(event.source==&m_next)Continue455();
}
void CGUIBriefingWindow::ShowKeyFrame455(BOOL show){if(show)Add(&m_keyFrame);else Remove(&m_keyFrame);Layout455();}
void CGUIBriefingWindow::SetKeyRows455(BYTE count,const std::array<std::array<BYTE,2>,2>& rows){
    if(!m_keys){if(!m_tutorialLoaded){load(m_tutorialSprite,21);m_tutorialLoaded=true;}m_keys.reset(new CGUITutorialKeyBoard);m_keys->SetSprite455(&m_tutorialSprite);m_keys->SetSize(m_keyFrame.GetSizeX(),m_keyFrame.GetSizeY());}
    m_keys->RemoveAll();if(!count){m_keyFrame.Remove(m_keys.get());return;}
    m_keys->SetRows455(count,rows);m_keys->SetPos(m_keyFrame.GetPosX(),m_keyFrame.GetPosY());m_keyFrame.Add(m_keys.get());
}
void CGUIBriefingWindow::ShowKeys455(BOOL show){if(!m_keys)return;if(show){m_keys->SetPos(m_keyFrame.GetPosX(),m_keyFrame.GetPosY());m_keyFrame.Add(m_keys.get());}else m_keyFrame.Remove(m_keys.get());}
void CGUIBriefingWindow::ShowPortrait455(BOOL show,BYTE role,BYTE avatarRace){
    if(show){Add(&m_portraitFrame);m_race=m_role=255;if(role<=18){m_race=avatarRace/2;
        if((m_race==0&&role==0)||((m_race==1||m_race==2)&&role==2))m_role=0;
        else if(m_race<=2&&role==3)m_role=1;else if(m_race<=2&&role==15)m_role=2;PortraitFrame455(0);}
    }else {Remove(&m_portraitFrame);m_race=m_role=255;}Layout455();
}
void CGUIBriefingWindow::PortraitFrame455(BYTE frame){
    if(m_race==255||m_role==255)return;if(m_race>=3)throw std::domain_error("455 portrait race resource outside verified domain");
    if(!m_portraitLoaded[m_race]){load(m_portraits[m_race],m_race+31);m_portraitLoaded[m_race]=true;}
    m_portrait.SetImage455(&m_portraits[m_race],m_role,frame);
    if(m_portraitOverlay.GetSizeX()&&m_portraitOverlay.GetSizeY())m_portrait.SetSheet455(static_cast<BYTE>(m_portrait.GetSizeX()/m_portraitOverlay.GetSizeX()),static_cast<BYTE>(m_portrait.GetSizeY()/m_portraitOverlay.GetSizeY()));
    m_portrait.SetFPS455(10);m_portrait.SetPauseInterval455(0);m_portrait.SetFrame455(0,FALSE);m_portraitStart=clockNow();
}
void CGUIBriefingWindow::UpdatePortrait455(){
    if(!IsAddedObject(&m_portraitFrame))return;const double period=double(m_portrait.GetTotal455())/m_portrait.GetFPS455()*1000.0;
    if(!std::isfinite(period)||period<1||period>(std::numeric_limits<DWORD>::max)())throw std::domain_error("455 portrait timer division outside verified domain");
    const DWORD duration=static_cast<DWORD>(period),elapsed=clockNow()-m_portraitStart;const WORD loops=static_cast<WORD>(elapsed/duration);
    if(m_portrait.GetSpriteInfo()->wFrameNo){if(loops)PortraitFrame455(0);}
    else if(loops>=randomNow()%5+10)PortraitFrame455(1);
}
void CGUIBriefingWindow::Update(){CGUIWindow::Update();if(IsShow()){if(!m_ready&&m_typing.IsTypingFinished455())SetReady455(TRUE);UpdatePortrait455();}}
bool RF455TutorialBriefingWindow::showRichMessage(const RF455TutorialMessage& message,bool closeAllowed){
    if(!g_pUiScreen||message.texts.size()>255)return false;
    std::vector<CGUITextInfo> text(message.texts.size());
    for(unsigned i=0;i<text.size();++i){const auto& record=message.texts[i];if(record.bytes.size()>65535)return false;FONT_INFO font;
        font.bySize=record.font[1];font.dwStyle=record.font[0];std::memcpy(&font.dwColor,record.font.data()+4,4);text[i].SetFont(&font);
        auto bytes=record.bytes;bytes.push_back(0);text[i].SetText(reinterpret_cast<char*>(bytes.data()));}
    m_window.SetTitle455(RF455_GetNormalLanguagePack()->get(445));m_window.Clear455();m_window.SetText455(static_cast<unsigned>(text.size()),text.data());
    m_window.ShowPortrait455(FALSE,255,255);m_window.ShowKeyFrame455(TRUE);
    m_window.SetPos((g_pUiScreen->GetSizeX()-m_window.GetSizeX())/2,g_pUiScreen->GetSizeY()-m_window.GetSizeY()-40);
    if(!m_window.IsShow())m_window.Open();g_pUiScreen->SetCapture455(closeAllowed?&m_window:nullptr);return true;
}
bool RF455TutorialBriefingWindow::showKeyGuide(const RF455TutorialKeyGuide& guide){if(guide.visible)m_window.SetKeyRows455(guide.count,guide.rows);else m_window.ShowKeys455(FALSE);return true;}
