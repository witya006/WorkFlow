// Source-owned tabbed settings. Legacy public accessors remain for stage adapters.
#include "client455_enhanced_lighting.h"
#include "client455_lobby_post.h"
#include <string>
#undef min
#undef max
extern void EP_Logout();
extern void EP_QuitProgram();
namespace {
bool OP455Blocked(){auto* screen=CGUIScreen::GetSingletonPtr();return screen&&screen->ExistObject();}
const char* OP455Text(unsigned index){return RF455_GetNormalLanguagePack()->get(index);}
std::string OP455Local(const wchar_t* russian,const char* english){
    const auto* nation=RF455_GetNormalNationPaths();
    if(!nation||nation->nation!=RF455_MapNation("Russia"))return english;
    const UINT cp=RF455_GetFontSettings().codepage;
    const int bytes=WideCharToMultiByte(cp,0,russian,-1,nullptr,0,nullptr,nullptr);
    if(bytes<=0)return english;
    std::string output(bytes,0);WideCharToMultiByte(cp,0,russian,-1,&output[0],bytes,nullptr,nullptr);
    output.resize(bytes-1);return output;
}
void OP455Label(CGUIText& label,const wchar_t* ru,const char* en){
    const auto text=OP455Local(ru,en);label.SetString(const_cast<char*>(text.c_str()));
    label.GetFont()->dwColor=0xffd4dbe3;label.SetMouseInput455(FALSE);
}
void OP455ButtonText(CGUIButtonEx& button,const wchar_t* ru,const char* en){
    const auto text=OP455Local(ru,en);button.SetLabel(const_cast<char*>(text.c_str()));
    const auto size=RF455_MeasureLegacyText(text.c_str());button.SetLabelMetrics455(size.cx,size.cy);
    button.SetLabelStyle(0x20);button.SetLabelColor(0xffe8edf2);button.SetLabelHoveredColor(0xffffffff);
}
void OP455ModernButton(CGUIButtonEx& button,LONG width=126,LONG height=30){
    button.SetSpriteInfoEx(nullptr);button.SetSize(width,height);button.SetARGB(0xff263442);
}
void OP455ButtonColor(CGUIButtonEx& button,bool selected=false){
    const WORD state=button.GetState();
    button.SetARGB(state&DISABLED?0xff1e252d:state&PRESSED?0xff405a70:
                   state&HOVERED?0xff344b60:selected?0xff31516c:0xff263442);
}
CSprite* OP455Sprite(BYTE id,WORD action,WORD frame){
    auto* sprite=gSpriteMgr.GetTargetSprite455(id);
    if(!sprite||action>=sprite->GetMaxActions()||frame>=sprite->GetMaxFrames(action))
        throw std::runtime_error("Settings sprite/frame missing");
    return sprite;
}
void OP455Bind(CGUIObject& object,BYTE id,WORD action,WORD frame){
    auto* sprite=OP455Sprite(id,action,frame);SPRITE_INFO image={sprite,action,frame};
    object.SetSpriteInfo(&image);object.SetSize(sprite->GetSpriteOrgXL(action,frame),sprite->GetSpriteOrgYL(action,frame));
}
void OP455Slider(CGUIScrollbar& slider){
    OP455Bind(slider,1,8,0);const LONG width=slider.GetSizeX(),height=slider.GetSizeY();OP455Bind(slider.GetThumb455(),1,8,1);
    auto* sprite=OP455Sprite(1,8,5);SPRITE_INFO top[2]={{sprite,8,2},{sprite,8,3}},bottom[2]={{sprite,8,4},{sprite,8,5}};
    slider.SetTopArrowSpriteInfo(top);slider.SetBottomArrowSpriteInfo(bottom);
    POINT size={sprite->GetSpriteOrgXL(8,2),sprite->GetSpriteOrgYL(8,2)};slider.SetTopArrowSize(size);
    size={sprite->GetSpriteOrgXL(8,4),sprite->GetSpriteOrgYL(8,4)};slider.SetBottomArrowSize(size);
    slider.SetSize(width+slider.GetTopArrow455().GetSizeX()+slider.GetBottomArrow455().GetSizeX(),height);
    slider.SetAutoThumb455(FALSE);slider.SetStyle(CGUIScrollbar::Horizontal);
}
bool OP455Write(const char* file,const char* section,const char* key,LONG value){
    char text[32];std::sprintf(text,"%ld",value);return WritePrivateProfileStringA(section,key,text,file)!=FALSE;
}
bool OP455Volume(const char* key,LONG value){
    char text[32];std::sprintf(text,"%.4f",double(value)/160.0);
    return WritePrivateProfileStringA("Sound",key,text,".\\R3Engine.ini")!=FALSE;
}
}
CGUIOptionWindow::CGUIOptionWindow(){m_actions.logout=EP_Logout;m_actions.quit=EP_QuitProgram;m_actions.blocked=OP455Blocked;}
CGUIOptionWindow::~CGUIOptionWindow(){RemoveAll();for(auto& page:m_pages)page.RemoveAll();}
void CGUIOptionWindow::SetSprite(){
    SettingsSnapshot saved;
    if(m_initialized)saved=Capture455();
    for(auto& slider:m_sound)OP455Slider(slider);
    for(auto& slider:m_graphic)OP455Slider(slider);
    for(auto& flag:m_etc)OP455Bind(flag,5,0,0);
    for(unsigned i=0;i<5;++i){OP455Bind(m_cameras[i],5,0,WORD(i+4));OP455Bind(m_targetFilters[i],5,0,1);}
    for(auto& icon:m_eaxIcons)OP455Bind(icon,5,0,18);
    for(auto& icon:m_specialIcons)OP455Bind(icon,5,0,18);
    for(auto& icon:m_targetModes)OP455Bind(icon,5,0,18);
    RemoveSpriteInfo();SetARGB(0xf018202a);SetSize(720,560);
    m_modernHeader.SetSize(720,50);m_modernHeader.SetARGB(0xff202d3a);
    m_divider.SetSize(672,1);m_divider.SetARGB(0xff3c4b5b);m_divider.SetMouseInput455(FALSE);
    m_close.SetSpriteInfoEx(nullptr);m_close.SetSize(30,30);m_close.SetARGB(0xff633d43);
    for(auto& button:m_tabs)OP455ModernButton(button,128);
    for(auto& button:m_actionsButtons)OP455ModernButton(button,188);
    OP455ModernButton(m_apply,148);OP455ModernButton(m_cancel,148);
    for(auto& button:m_resolution)OP455ModernButton(button,154);
    for(auto& button:m_msaa)OP455ModernButton(button,100);
    for(auto& button:m_lighting)OP455ModernButton(button,154);
    for(auto& button:m_lobbyQuality)OP455ModernButton(button,154);
    for(auto& button:m_diagnostics)OP455ModernButton(button,154);
    if(m_initialized){Restore455(saved);Layout455();}
}
void CGUIOptionWindow::Init(){
    if(m_initialized)return;
    SetSprite();m_etcCount=8;m_ratingVisible=false;
    OP455Label(m_title,L"\u041d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0438","Settings");
    const wchar_t* ruTabs[]={L"\u0417\u0432\u0443\u043a",L"\u0418\u0437\u043e\u0431\u0440\u0430\u0436\u0435\u043d\u0438\u0435",L"\u0413\u0440\u0430\u0444\u0438\u043a\u0430",L"\u0418\u0433\u0440\u0430",L"HUD"};
    const char* enTabs[]={"Sound","Image","Graphics","Game","HUD"};
    for(unsigned i=0;i<PageCount;++i){OP455ButtonText(m_tabs[i],ruTabs[i],enTabs[i]);m_tabs[i].AddMouseEventHandler(this);Add(&m_tabs[i]);m_pages[i].SetSize(672,330);}
    OP455ButtonText(m_apply,L"\u041f\u0440\u0438\u043c\u0435\u043d\u0438\u0442\u044c","Apply");OP455ButtonText(m_cancel,L"\u041e\u0442\u043c\u0435\u043d\u0430","Cancel");
    m_apply.AddMouseEventHandler(this);m_cancel.AddMouseEventHandler(this);m_close.AddMouseEventHandler(this);
    OP455Label(m_closeLabel,L"X","X");m_close.Add(&m_closeLabel);
    Add(&m_modernHeader);Add(&m_title);Add(&m_close);Add(&m_divider);Add(&m_apply);Add(&m_cancel);Add(&m_status);
    SetMoveObject(&m_modernHeader);SetMovable(TRUE);m_title.SetMouseInput455(FALSE);
    for(auto& slider:m_sound){slider.SetTotalAmount(160);slider.SetAdjustmentUnit(1);slider.SetArrowAdjustmentUnit(8);slider.AddScrollHandler(this);}
    const LONG totals[]={10,3,3,3,2,3};
    for(unsigned i=0;i<6;++i){m_graphic[i].SetTotalAmount(totals[i]);m_graphic[i].AddScrollHandler(this);}
    OP455Label(m_soundLabels[Effect_Snd],L"\u0413\u0440\u043e\u043c\u043a\u043e\u0441\u0442\u044c \u044d\u0444\u0444\u0435\u043a\u0442\u043e\u0432","Effects volume");
    OP455Label(m_soundLabels[BGM],L"\u0413\u0440\u043e\u043c\u043a\u043e\u0441\u0442\u044c \u043c\u0443\u0437\u044b\u043a\u0438","Music volume");
    for(unsigned i:{unsigned(Effect_Snd),unsigned(BGM)}){m_pages[SoundPage].Add(&m_soundLabels[i]);m_pages[SoundPage].Add(&m_sound[i]);}
    OP455Label(m_resolutionTitle,L"\u0420\u0430\u0437\u0440\u0435\u0448\u0435\u043d\u0438\u0435 \u043e\u043a\u043d\u0430","Window resolution");
    m_pages[ImagePage].Add(&m_resolutionTitle);
    OP455ButtonText(m_resolution[0],L"1280 x 720","1280 x 720");
    OP455ButtonText(m_resolution[1],L"1920 x 1080","1920 x 1080");
    for(auto& button:m_resolution){button.AddMouseEventHandler(this);m_pages[ImagePage].Add(&button);}
    OP455Label(m_pageNote[ImagePage],L"\u041f\u0440\u0438\u043c\u0435\u043d\u0438\u0442\u0441\u044f \u043f\u043e\u0441\u043b\u0435 \u043f\u0435\u0440\u0435\u0437\u0430\u043f\u0443\u0441\u043a\u0430 \u043a\u043b\u0438\u0435\u043d\u0442\u0430.","Takes effect after restarting the client.");
    OP455Label(m_msaaTitle,L"\u0421\u0433\u043b\u0430\u0436\u0438\u0432\u0430\u043d\u0438\u0435","Anti-aliasing");
    OP455Label(m_lightingTitle,L"\u041e\u0441\u0432\u0435\u0449\u0435\u043d\u0438\u0435 \u043f\u0435\u0440\u0441\u043e\u043d\u0430\u0436\u0435\u0439","Character lighting");
    m_pages[GraphicsPage].Add(&m_msaaTitle);m_pages[GraphicsPage].Add(&m_lightingTitle);
    OP455Label(m_lobbyQualityTitle,L"\u041a\u0430\u0447\u0435\u0441\u0442\u0432\u043e \u0441\u0446\u0435\u043d\u044b \u0432\u0445\u043e\u0434\u0430","Lobby scene quality");
    m_pages[GraphicsPage].Add(&m_lobbyQualityTitle);
    OP455ButtonText(m_lobbyQuality[0],L"\u041a\u043b\u0430\u0441\u0441\u0438\u0447\u0435\u0441\u043a\u043e\u0435","Classic");
    OP455ButtonText(m_lobbyQuality[1],L"\u0423\u043b\u0443\u0447\u0448\u0435\u043d\u043d\u043e\u0435","Enhanced");
    for(auto& button:m_lobbyQuality){button.AddMouseEventHandler(this);m_pages[GraphicsPage].Add(&button);}
    OP455ButtonText(m_msaa[0],L"\u0412\u044b\u043a\u043b.","Off");OP455ButtonText(m_msaa[1],L"2x MSAA","2x MSAA");OP455ButtonText(m_msaa[2],L"4x MSAA","4x MSAA");
    OP455ButtonText(m_lighting[0],L"\u041a\u043b\u0430\u0441\u0441\u0438\u0447\u0435\u0441\u043a\u043e\u0435","Classic");OP455ButtonText(m_lighting[1],L"\u0423\u043b\u0443\u0447\u0448\u0435\u043d\u043d\u043e\u0435","Enhanced");
    for(auto& button:m_msaa){button.AddMouseEventHandler(this);m_pages[GraphicsPage].Add(&button);}
    for(auto& button:m_lighting){button.AddMouseEventHandler(this);m_pages[GraphicsPage].Add(&button);}
    OP455Label(m_graphicLabels[DynamicLighting],L"\u0414\u0438\u043d\u0430\u043c\u0438\u0447\u0435\u0441\u043a\u043e\u0435 \u043e\u0441\u0432\u0435\u0449\u0435\u043d\u0438\u0435","Dynamic lighting");
    OP455Label(m_graphicLabels[Shadow],L"\u0422\u0435\u043d\u0438","Shadows");
    OP455Label(m_graphicLabels[SeeDist],L"\u0414\u0430\u043b\u044c\u043d\u043e\u0441\u0442\u044c \u043e\u0442\u0440\u0438\u0441\u043e\u0432\u043a\u0438 \u043f\u0435\u0440\u0441\u043e\u043d\u0430\u0436\u0435\u0439","Character draw distance");
    for(unsigned i:{unsigned(DynamicLighting),unsigned(Shadow),unsigned(SeeDist)}){
        m_pages[GraphicsPage].Add(&m_graphicLabels[i]);m_pages[GraphicsPage].Add(&m_graphic[i]);
    }
    OP455Label(m_etcLabels[AutoSeeDist],L"\u0410\u0432\u0442\u043e\u043f\u043e\u0434\u0431\u043e\u0440 \u0434\u0430\u043b\u044c\u043d\u043e\u0441\u0442\u0438 \u043e\u0442\u0440\u0438\u0441\u043e\u0432\u043a\u0438","Automatic draw distance");
    m_etc[AutoSeeDist].AddMouseEventHandler(this);m_etcLabels[AutoSeeDist].SetMouseInput455(TRUE);m_etcLabels[AutoSeeDist].AddMouseEventHandler(this);
    m_pages[GraphicsPage].Add(&m_etc[AutoSeeDist]);m_pages[GraphicsPage].Add(&m_etcLabels[AutoSeeDist]);
    OP455Label(m_pageNote[GraphicsPage],L"\u0421\u0433\u043b\u0430\u0436\u0438\u0432\u0430\u043d\u0438\u0435 \u0438\u0437\u043c\u0435\u043d\u0438\u0442\u0441\u044f \u043f\u043e\u0441\u043b\u0435 \u043f\u0435\u0440\u0435\u0437\u0430\u043f\u0443\u0441\u043a\u0430 \u0438\u0433\u0440\u044b.","Anti-aliasing changes after restarting the game.");
    OP455Label(m_cameraTitle,L"\u0420\u0435\u0436\u0438\u043c \u043a\u0430\u043c\u0435\u0440\u044b","Camera mode");m_pages[GamePage].Add(&m_cameraTitle);
    for(auto& camera:m_cameras){camera.AddMouseEventHandler(this);m_pages[GamePage].Add(&camera);}
    OP455ButtonText(m_actionsButtons[0],L"\u0412\u044b\u0431\u043e\u0440 \u043f\u0435\u0440\u0441\u043e\u043d\u0430\u0436\u0430","Character selection");OP455ButtonText(m_actionsButtons[1],L"\u0412\u044b\u0439\u0442\u0438 \u0438\u0437 \u0438\u0433\u0440\u044b","Exit game");
    for(unsigned i=0;i<2;++i){m_actionsButtons[i].AddMouseEventHandler(this);m_pages[GamePage].Add(&m_actionsButtons[i]);}
    OP455Label(m_etcLabels[Hint],L"\u041f\u043e\u043a\u0430\u0437\u044b\u0432\u0430\u0442\u044c \u043f\u043e\u0434\u0441\u043a\u0430\u0437\u043a\u0438","Show hints");m_etc[Hint].AddMouseEventHandler(this);
    m_etcLabels[Hint].SetMouseInput455(TRUE);m_etcLabels[Hint].AddMouseEventHandler(this);
    m_pages[HUDPage].Add(&m_etc[Hint]);m_pages[HUDPage].Add(&m_etcLabels[Hint]);
    OP455Label(m_diagnosticsTitle,L"FPS \u0438 \u0434\u0438\u0430\u0433\u043d\u043e\u0441\u0442\u0438\u043a\u0430 \u043b\u043e\u0431\u0431\u0438","Lobby FPS and diagnostics");
    m_pages[HUDPage].Add(&m_diagnosticsTitle);
    OP455ButtonText(m_diagnostics[0],L"\u0421\u043a\u0440\u044b\u0442\u044c","Hide");
    OP455ButtonText(m_diagnostics[1],L"\u041f\u043e\u043a\u0430\u0437\u0430\u0442\u044c","Show");
    for(auto& button:m_diagnostics){button.AddMouseEventHandler(this);m_pages[HUDPage].Add(&button);}
    OP455Label(m_pageNote[SoundPage],L"\u0418\u0437\u043c\u0435\u043d\u0435\u043d\u0438\u044f \u0432\u0441\u0442\u0443\u043f\u0430\u044e\u0442 \u0432 \u0441\u0438\u043b\u0443 \u043f\u043e\u0441\u043b\u0435 \u00ab\u041f\u0440\u0438\u043c\u0435\u043d\u0438\u0442\u044c\u00bb.","Changes take effect when you select Apply.");
    OP455Label(m_pageNote[GamePage],L"\u041a\u0430\u043c\u0435\u0440\u0430 \u043c\u0435\u043d\u044f\u0435\u0442\u0441\u044f \u043f\u043e\u0441\u043b\u0435 \u00ab\u041f\u0440\u0438\u043c\u0435\u043d\u0438\u0442\u044c\u00bb.","Camera mode changes when you select Apply.");
    OP455Label(m_pageNote[HUDPage],L"\u041d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0438 \u0438\u0433\u0440\u043e\u0432\u043e\u0433\u043e \u0438\u043d\u0442\u0435\u0440\u0444\u0435\u0439\u0441\u0430.","Game interface settings.");
    for(unsigned i=0;i<PageCount;++i)m_pages[i].Add(&m_pageNote[i]);
    Restore455(m_applied);
    m_requestedMsaa=GetPrivateProfileIntA("RenderState","MSAA",4,".\\R3Engine.ini");
    m_requestedMsaa=m_requestedMsaa>=4?4:m_requestedMsaa>=2?2:0;
    m_requestedWidth=GetPrivateProfileIntA("RenderState","ScreenXSize",1920,".\\R3Engine.ini");
    m_requestedHeight=GetPrivateProfileIntA("RenderState","ScreenYSize",1080,".\\R3Engine.ini");
    if(m_requestedWidth!=1280||m_requestedHeight!=720){m_requestedWidth=1920;m_requestedHeight=1080;}
    m_enhanced=RF455_EnhancedActorLightingEnabled();
    m_lobbyPost=RF455_LobbyPostEnabled();
    m_showDiagnostics=GetPrivateProfileIntA("HUD","LobbyDiagnostics",1,".\\R3Engine.ini")!=0;
    const UINT camera=GetPrivateProfileIntA("Camera","Mode",1,".\\DataTable\\GameSetting.ini");
    SelectCamera(BYTE(camera<5?camera:1));
    SwitchOn(Hint,GetPrivateProfileIntA("UI","ShowHint",TRUE,".\\DataTable\\GameSetting.ini")!=0);
    SwitchOn(AutoSeeDist,GetPrivateProfileIntA("Performance","AutoVisualFieldAdjustment",TRUE,".\\DataTable\\GameSetting.ini")!=0);
    SetGraphicOption(SeeDist,float(GetPrivateProfileIntA("Performance","VisualFieldAdjustmentLevel",4,".\\DataTable\\GameSetting.ini")));
    m_initialized=true;m_applied=Capture455();Layout455();SetPage455(SoundPage);
}
void CGUIOptionWindow::Layout455(){
    const LONG x=GetPosX(),y=GetPosY();
    m_modernHeader.SetPos(x,y);m_title.SetPos(x+24,y+17);m_close.SetPos(x+668,y+10);m_closeLabel.SetPos(x+678,y+17);
    for(unsigned i=0;i<PageCount;++i)m_tabs[i].SetPos(x+24+136*i,y+72);
    m_divider.SetPos(x+24,y+116);
    for(auto& page:m_pages)page.SetPos(x+24,y+136);
    m_soundLabels[Effect_Snd].SetPos(x+40,y+160);m_sound[Effect_Snd].SetPos(x+338,y+160);
    m_soundLabels[BGM].SetPos(x+40,y+222);m_sound[BGM].SetPos(x+338,y+222);
    m_resolutionTitle.SetPos(x+40,y+160);
    for(unsigned i=0;i<2;++i)m_resolution[i].SetPos(x+338+164*i,y+152);
    m_lobbyQualityTitle.SetPos(x+40,y+160);for(unsigned i=0;i<2;++i)m_lobbyQuality[i].SetPos(x+338+164*i,y+152);
    m_lightingTitle.SetPos(x+40,y+205);for(unsigned i=0;i<2;++i)m_lighting[i].SetPos(x+338+164*i,y+197);
    m_msaaTitle.SetPos(x+40,y+250);for(unsigned i=0;i<3;++i)m_msaa[i].SetPos(x+338+109*i,y+242);
    for(unsigned i=1;i<=3;++i){m_graphicLabels[i].SetPos(x+40,y+258+42*i);m_graphic[i].SetPos(x+338,y+258+42*i);}
    m_etc[AutoSeeDist].SetPos(x+40,y+424);m_etcLabels[AutoSeeDist].SetPos(x+62,y+424);
    m_cameraTitle.SetPos(x+40,y+160);for(unsigned i=0;i<5;++i)m_cameras[i].SetPos(x+338+48*i,y+160);
    for(unsigned i=0;i<2;++i)m_actionsButtons[i].SetPos(x+40+208*i,y+246);
    m_etc[Hint].SetPos(x+40,y+160);m_etcLabels[Hint].SetPos(x+64,y+160);
    m_diagnosticsTitle.SetPos(x+40,y+222);for(unsigned i=0;i<2;++i)m_diagnostics[i].SetPos(x+338+164*i,y+214);
    for(auto& note:m_pageNote)note.SetPos(x+40,y+460);
    m_status.SetPos(x+24,y+492);m_apply.SetPos(x+376,y+516);m_cancel.SetPos(x+548,y+516);
}
CGUIOptionWindow::SettingsSnapshot CGUIOptionWindow::Capture455(){
    SettingsSnapshot value;
    for(unsigned i=0;i<3;++i)value.sound[i]=m_sound[i].GetCurrentAmount();
    for(unsigned i=0;i<6;++i)value.graphics[i]=LONG(GetGraphicOption(GraphicOption(i)));
    for(unsigned i=0;i<8;++i)value.flags[i]=IsSwitchOn(EtcOption(i));
    value.camera=m_camera;value.msaa=m_requestedMsaa;value.width=m_requestedWidth;value.height=m_requestedHeight;value.enhanced=m_enhanced;
    value.lobbyPost=m_lobbyPost;
    value.lobbyDiagnostics=m_showDiagnostics;
    return value;
}
void CGUIOptionWindow::Restore455(const SettingsSnapshot& value){
    for(unsigned i=0;i<3;++i)m_sound[i].SetCurrentAmount(value.sound[i]);
    for(unsigned i=0;i<6;++i)m_graphic[i].SetCurrentAmount(i==SeeDist?
        (std::max)(1L,(std::min)(4L,value.graphics[i]))-1:value.graphics[i]);
    for(unsigned i=0;i<8;++i)m_etc[i].GetSpriteInfo()->wFrameNo=value.flags[i]?0:1;
    m_camera=value.camera<5?value.camera:1;
    for(unsigned i=0;i<5;++i)m_cameras[i].GetSpriteInfo()->wFrameNo=WORD((i==m_camera?9:4)+i);
    m_requestedMsaa=value.msaa;m_requestedWidth=value.width;m_requestedHeight=value.height;m_enhanced=value.enhanced;
    m_lobbyPost=value.lobbyPost;
    m_showDiagnostics=value.lobbyDiagnostics;
}
void CGUIOptionWindow::RememberExternal455(){if(m_initialized&&!m_editing)m_applied=Capture455();}
void CGUIOptionWindow::SetStatus455(const wchar_t* ru,const char* en){OP455Label(m_status,ru,en);}
void CGUIOptionWindow::SetPage455(SettingsPage page){
    if(unsigned(page)>=PageCount)return;
    for(auto& body:m_pages){Remove(&body);body.Show(FALSE);}
    m_page=page;Layout455();Add(&m_pages[page]);m_pages[page].Show(IsShow());Update();
}
void CGUIOptionWindow::Open(){
    if(!m_initialized)Init();
    if(!IsShow()){m_applied=Capture455();m_editing=true;SetStatus455(L"","");}
    CGUIWindow::Open();SetPage455(m_page);
}
void CGUIOptionWindow::Close(){if(m_editing)Cancel455();CGUIWindow::Close();}
void CGUIOptionWindow::Cancel455(){Restore455(m_applied);m_editing=false;SetStatus455(L"","");Update();}
bool CGUIOptionWindow::Persist455(const SettingsSnapshot& value){
    const char* engine=".\\R3Engine.ini";const char* game=".\\DataTable\\GameSetting.ini";
    bool ok=true;
    ok=OP455Write(engine,"RenderState","MSAA",value.msaa)&&ok;
    ok=OP455Write(engine,"RenderState","LobbyPost",value.lobbyPost)&&ok;
    ok=OP455Write(engine,"HUD","LobbyDiagnostics",value.lobbyDiagnostics)&&ok;
    ok=OP455Write(engine,"RenderState","ScreenXSize",value.width)&&ok;
    ok=OP455Write(engine,"RenderState","ScreenYSize",value.height)&&ok;
    ok=OP455Write(engine,"RenderState","DynamicLight",value.graphics[DynamicLighting])&&ok;
    ok=OP455Write(engine,"RenderState","ShadowDetail",value.graphics[Shadow])&&ok;
    ok=OP455Volume("SoundVol",value.sound[Effect_Snd])&&ok;ok=OP455Volume("MusicVol",value.sound[BGM])&&ok;
    ok=OP455Write(game,"Performance","VisualFieldAdjustmentLevel",value.graphics[SeeDist])&&ok;
    ok=OP455Write(game,"Performance","AutoVisualFieldAdjustment",value.flags[AutoSeeDist])&&ok;
    ok=OP455Write(game,"Camera","Mode",value.camera)&&ok;ok=OP455Write(game,"UI","ShowHint",value.flags[Hint])&&ok;
    return ok;
}
bool CGUIOptionWindow::Apply455(){
    const auto edited=Capture455();
    auto* screen=CGUIScreen::GetSingletonPtr();const HWND window=screen?screen->GetHWND():nullptr;
    if(!window||!IsWindow(window)){SetStatus455(L"Settings are not attached to the game window.","Settings are not attached to the game window.");return false;}
    if(edited.enhanced&&!RF455_EnhancedActorLightingAvailable()){
        SetStatus455(L"\u0423\u043b\u0443\u0447\u0448\u0435\u043d\u043d\u043e\u0435 \u043e\u0441\u0432\u0435\u0449\u0435\u043d\u0438\u0435 \u043d\u0435\u0434\u043e\u0441\u0442\u0443\u043f\u043d\u043e \u043d\u0430 \u044d\u0442\u043e\u043c \u0443\u0441\u0442\u0440\u043e\u0439\u0441\u0442\u0432\u0435.","Enhanced lighting is unavailable on this device.");return false;
    }
    if(!Persist455(edited)){Persist455(m_applied);SetStatus455(L"\u041d\u0435 \u0443\u0434\u0430\u043b\u043e\u0441\u044c \u0441\u043e\u0445\u0440\u0430\u043d\u0438\u0442\u044c \u043d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0438.","Could not save settings.");return false;}
    if(edited.enhanced!=RF455_EnhancedActorLightingEnabled()&&!RF455_SetEnhancedActorLightingEnabled(edited.enhanced)){
        Persist455(m_applied);SetStatus455(L"\u041d\u0435 \u0443\u0434\u0430\u043b\u043e\u0441\u044c \u043f\u0440\u0438\u043c\u0435\u043d\u0438\u0442\u044c \u043e\u0441\u0432\u0435\u0449\u0435\u043d\u0438\u0435.","Could not apply lighting.");return false;
    }
    RF455_SetLobbyPostEnabled(edited.lobbyPost);
    if(window){
        // Existing real stage handlers read volume widgets and apply other values from wParam.
        SendMessage(window,WM_OPTION_ADJUST_EFFECT_SOUND,0,0);SendMessage(window,WM_OPTION_ADJUST_BGM_SOUND,0,0);
        SendMessage(window,WM_OPTION_ADJUST_DYNAMIC_LIGHTING,edited.graphics[DynamicLighting],0);
        SendMessage(window,WM_OPTION_ADJUST_SHADOW,edited.graphics[Shadow],0);
        SendMessage(window,WM_OPTION_CHANGE_VF_DIST,edited.graphics[SeeDist],0);
        SendMessage(window,WM_OPTION_TOGGLE_AUTO_VF_ADJUST,edited.flags[AutoSeeDist],0);
        SendMessage(window,WM_OPTION_CHANGE_CAMERA_MODE,edited.camera,0);SendMessage(window,WM_OPTION_TOGGLE_HINT,edited.flags[Hint],0);
    }
    const bool restart=edited.msaa!=m_applied.msaa||edited.width!=m_applied.width||edited.height!=m_applied.height;
    m_applied=edited;
    SetStatus455(restart?L"\u0421\u043e\u0445\u0440\u0430\u043d\u0435\u043d\u043e. \u0420\u0430\u0437\u0440\u0435\u0448\u0435\u043d\u0438\u0435 \u0438 MSAA: \u043f\u043e\u0441\u043b\u0435 \u043f\u0435\u0440\u0435\u0437\u0430\u043f\u0443\u0441\u043a\u0430.":L"\u041d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0438 \u043f\u0440\u0438\u043c\u0435\u043d\u0435\u043d\u044b.",
                 restart?"Saved. Resolution and MSAA take effect after restart.":"Settings applied.");
    return true;
}
void CGUIOptionWindow::Send455(UINT message,WPARAM value){auto* screen=CGUIScreen::GetSingletonPtr();if(screen)PostMessage(screen->GetHWND(),message,value,0);}
void CGUIOptionWindow::SetSoundOption(SoundOption which,float value){const unsigned i=unsigned(which);if(i>=3)return;if(!std::isfinite(value))throw std::invalid_argument("455 Option nonfinite volume outside admitted domain");m_sound[i].SetCurrentAmount(int(double(m_sound[i].GetTotalAmount())*double(value)));RememberExternal455();}
float CGUIOptionWindow::GetSoundOption(SoundOption which){const unsigned i=unsigned(which);return i<3?float(double(m_sound[i].GetCurrentAmount())/double(m_sound[i].GetTotalAmount())):0;}
void CGUIOptionWindow::SetGraphicOption(GraphicOption which,float value){
    const unsigned i=unsigned(which);if(i>=6)return;
    if(!std::isfinite(value))throw std::invalid_argument("455 Option nonfinite graphics outside admitted domain");
    // The manager uses levels1..4; the native scrollbar represents four positions0..3.
    if(which==SeeDist)m_graphic[i].SetCurrentAmount(int((std::max)(1.f,(std::min)(4.f,value)))-1);
    else m_graphic[i].SetCurrentAmount(i?int(value):int(double(m_graphic[i].GetTotalAmount())*(double(value)-0.8)));
    RememberExternal455();
}
float CGUIOptionWindow::GetGraphicOption(GraphicOption which){const unsigned i=unsigned(which);return i<6?float(m_graphic[i].GetCurrentAmount()+(which==SeeDist?1:0)):0;}
void CGUIOptionWindow::SwitchOn(EtcOption which,BOOL value){const unsigned i=unsigned(which);if(i>=8){if(i<10)m_legacyFlags[i-8]=value;return;}m_etc[i].GetSpriteInfo()->wFrameNo=value?0:1;RememberExternal455();}
BOOL CGUIOptionWindow::IsSwitchOn(EtcOption which){const unsigned i=unsigned(which);if(i>=8)return i<10?m_legacyFlags[i-8]:FALSE;return m_etc[i].GetSpriteInfo()->wFrameNo==0;}
void CGUIOptionWindow::SelectCamera(BYTE value){if(value>=5)return;m_camera=value;for(unsigned i=0;i<5;++i)m_cameras[i].GetSpriteInfo()->wFrameNo=WORD((i==value?9:4)+i);RememberExternal455();}
void CGUIOptionWindow::SelectEax455(BYTE value){if(value==m_eax||value>=2||m_eax>=2)return;m_eaxIcons[m_eax].GetSpriteInfo()->wFrameNo=18;m_eax=value;m_eaxIcons[value].GetSpriteInfo()->wFrameNo=19;}
void CGUIOptionWindow::SelectSpecial455(BYTE value){if(value==m_special||value>=2||m_special>=2)return;m_specialIcons[m_special].GetSpriteInfo()->wFrameNo=18;m_special=value;m_specialIcons[value].GetSpriteInfo()->wFrameNo=19;}
void CGUIOptionWindow::SetTargetingMode455(int value){if(unsigned(value)>=2)return;for(unsigned i=0;i<2;++i)OP455Bind(m_targetModes[i],5,0,i==unsigned(value)?19:18);Send455(0x62a,value);m_targetMode=BYTE(value);}
void CGUIOptionWindow::SetTargetingFilter455(int index,WPARAM value){if(unsigned(index)>=5)return;OP455Bind(m_targetFilters[index],5,0,value?0:1);Send455(0x62b+index,value);m_targetMask^=BYTE(1u<<index);}
void CGUIOptionWindow::SetTargetingFilters455(BYTE mask){for(unsigned i=0;i<5;++i)SetTargetingFilter455(i,(1u<<i)&mask);}
void CGUIOptionWindow::Update(){
    CGUIWindow::Update();
    for(unsigned i=0;i<2;++i){if(m_logoutRestricted)m_actionsButtons[i].Disable();else m_actionsButtons[i].Enable();OP455ButtonColor(m_actionsButtons[i]);}
    for(unsigned i=0;i<PageCount;++i)OP455ButtonColor(m_tabs[i],i==m_page);
    for(unsigned i=0;i<2;++i)OP455ButtonColor(m_resolution[i],i==(m_requestedWidth==1280?0u:1u));
    const unsigned samples[]={0,2,4};for(unsigned i=0;i<3;++i)OP455ButtonColor(m_msaa[i],samples[i]==m_requestedMsaa);
    if(RF455_EnhancedActorLightingAvailable())m_lighting[1].Enable();else m_lighting[1].Disable();
    for(unsigned i=0;i<2;++i)OP455ButtonColor(m_lighting[i],bool(i)==m_enhanced);
    for(unsigned i=0;i<2;++i)OP455ButtonColor(m_lobbyQuality[i],bool(i)==m_lobbyPost);
    for(unsigned i=0;i<2;++i)OP455ButtonColor(m_diagnostics[i],bool(i)==m_showDiagnostics);
    OP455ButtonColor(m_apply);OP455ButtonColor(m_cancel);
}
void CGUIOptionWindow::MouseEvent(_mouse_event& event){
    CGUIWindow::MouseEvent(event);
    if(event.id==MOUSE_CLICKED){
        for(unsigned i=0;i<PageCount;++i)if(event.source==&m_tabs[i]){SetPage455(SettingsPage(i));return;}
        if(event.source==&m_apply){Apply455();return;}
        if(event.source==&m_cancel||event.source==&m_close){Close();return;}
        for(unsigned i=0;i<2;++i){
            if(event.source==&m_lobbyQuality[i]){m_lobbyPost=i!=0;Update();return;}
            if(event.source==&m_diagnostics[i]){m_showDiagnostics=i!=0;Update();return;}
            if(event.source==&m_resolution[i]){m_requestedWidth=i?1920:1280;m_requestedHeight=i?1080:720;Update();return;}
            if(event.source==&m_lighting[i]){if(!i||RF455_EnhancedActorLightingAvailable())m_enhanced=i!=0;Update();return;}
            if(event.source==&m_actionsButtons[i]){if(m_actions.blocked&&m_actions.blocked())return;const auto action=i?m_actions.quit:m_actions.logout;if(action)action();return;}
        }
        for(unsigned i=0;i<3;++i)if(event.source==&m_msaa[i]){const unsigned samples[]={0,2,4};m_requestedMsaa=samples[i];Update();return;}
    }
    if(event.id!=MOUSE_STROKED)return;
    for(unsigned i:{unsigned(Hint),unsigned(AutoSeeDist)})if(event.source==&m_etc[i]||event.source==&m_etcLabels[i]){SwitchOn(EtcOption(i),!IsSwitchOn(EtcOption(i)));return;}
    for(unsigned i=0;i<5;++i)if(event.source==&m_cameras[i]){SelectCamera(BYTE(i));return;}
}
void CGUIOptionWindow::ScrollEvent(_scroll_event& event){
    if(event.source==&m_graphic[SeeDist])SwitchOn(AutoSeeDist,FALSE);
    // Sliders edit only. Apply forwards the complete snapshot to the live stage.
}
