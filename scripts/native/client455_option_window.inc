// Primary b1b5febf...,x86/base400000,7113C0/713060/713440..7144D1.
#undef min
#undef max
extern void EP_Logout();
extern void EP_QuitProgram();
namespace {
bool OP455Blocked(){auto* screen=CGUIScreen::GetSingletonPtr();return screen&&screen->ExistObject();}
const char* OP455Text(unsigned index){return RF455_GetNormalLanguagePack()->get(index);}
CSprite* OP455Sprite(BYTE id,WORD action,WORD frame){auto* sprite=gSpriteMgr.GetTargetSprite455(id);if(!sprite||action>=sprite->GetMaxActions()||frame>=sprite->GetMaxFrames(action))throw std::runtime_error("455 Option sprite/frame missing");return sprite;}
void OP455Bind(CGUIObject& object,BYTE id,WORD action,WORD frame){auto* sprite=OP455Sprite(id,action,frame);SPRITE_INFO image={sprite,action,frame};object.SetSpriteInfo(&image);object.SetSize(sprite->GetSpriteOrgXL(action,frame),sprite->GetSpriteOrgYL(action,frame));}
void OP455Button(CGUIButton& button,WORD action,WORD first,unsigned states){auto* sprite=OP455Sprite(1,action,WORD(first+states-1));SPRITE_INFO normal={sprite,action,first};button.SetSpriteInfoEx(&normal);const WORD flags[]={0,HOVERED,PRESSED,DISABLED};for(unsigned i=1;i<states;++i){SPRITE_INFO image={sprite,action,WORD(first+i)};button.SetSpriteInfoEx(flags[i],&image);}button.SetSize(sprite->GetSpriteOrgXL(action,first),sprite->GetSpriteOrgYL(action,first));}
void OP455Center(CGUIObject& object,LONG x,LONG y,LONG width,LONG height){object.SetPos(x+(width-object.GetSizeX())/2,y+(height-object.GetSizeY())/2);}
void OP455String(CGUIText& object,unsigned id){object.SetString(const_cast<char*>(OP455Text(id)));}
void OP455Slider(CGUIScrollbar& slider){
    OP455Bind(slider,1,8,0);const LONG width=slider.GetSizeX(),height=slider.GetSizeY();OP455Bind(slider.GetThumb455(),1,8,1);
    auto* sprite=OP455Sprite(1,8,5);SPRITE_INFO top[2]={{sprite,8,2},{sprite,8,3}},bottom[2]={{sprite,8,4},{sprite,8,5}};
    slider.SetTopArrowSpriteInfo(top);slider.SetBottomArrowSpriteInfo(bottom);POINT size={sprite->GetSpriteOrgXL(8,2),sprite->GetSpriteOrgYL(8,2)};slider.SetTopArrowSize(size);size={sprite->GetSpriteOrgXL(8,4),sprite->GetSpriteOrgYL(8,4)};slider.SetBottomArrowSize(size);
    slider.SetSize(width+slider.GetTopArrow455().GetSizeX()+slider.GetBottomArrow455().GetSizeX(),height);slider.SetAutoThumb455(FALSE);slider.SetStyle(CGUIScrollbar::Horizontal);
}
void OP455Radio(CGUIObject* objects,BYTE& selected,BYTE next,unsigned count,WORD first,WORD active){if(selected==next||next>=count||selected>=count)return;objects[selected].GetSpriteInfo()->wFrameNo=WORD(first+selected);selected=next;objects[next].GetSpriteInfo()->wFrameNo=WORD(active+next);}
}
CGUIOptionWindow::CGUIOptionWindow(){m_actions.logout=EP_Logout;m_actions.quit=EP_QuitProgram;m_actions.blocked=OP455Blocked;}
CGUIOptionWindow::~CGUIOptionWindow(){RemoveAll();}
void CGUIOptionWindow::SetSprite(){
    for(auto& slider:m_sound)OP455Slider(slider);for(auto& slider:m_graphic)OP455Slider(slider);
    OP455Bind(*this,5,0,20);for(auto& icon:m_eaxIcons)OP455Bind(icon,5,0,18);for(auto& icon:m_specialIcons)OP455Bind(icon,5,0,18);
    const WORD frames[]={2,3,14,15,16,3};for(unsigned i=0;i<6;++i)OP455Bind(m_marks[i],5,0,frames[i]);
    const auto* nation=RF455_GetNormalNationPaths();m_ratingVisible=nation->configured&&nation->nation==0;m_etcCount=m_ratingVisible?8:6;
    for(unsigned i=0;i<m_etcCount;++i)OP455Bind(m_etc[i],5,0,0);
    for(unsigned i=0;i<5;++i){OP455Bind(m_cameras[i],5,0,WORD(i+4));OP455Bind(m_targetFilters[i],5,0,1);}for(auto& icon:m_targetModes)OP455Bind(icon,5,0,18);
    for(auto& button:m_actionsButtons)OP455Button(button,1,4,4);
    auto* common=OP455Sprite(1,4,12);m_header.SetImage455(common,4,12,true);OP455Button(m_close,0,0,3);OP455Button(m_help,0,3,3);
}
void CGUIOptionWindow::Init(){
    SetSprite();OP455String(m_title,0x3ec);const unsigned actionNames[]={0x3ed,0x3ee,0x129e};for(unsigned i=0;i<3;++i){m_actionsButtons[i].SetLabel(const_cast<char*>(OP455Text(actionNames[i])));const auto extent=RF455_MeasureLegacyText(OP455Text(actionNames[i]));m_actionsButtons[i].SetLabelMetrics455(extent.cx,extent.cy);m_actionsButtons[i].SetLabelStyle(0x20);m_actionsButtons[i].SetLabelColor(0xffe8e8e8);}
    OP455String(m_soundTitle,0x3ef);const unsigned soundNames[]={0x3f1,0x3f0,0xe88,0xe89,0xe8a};for(unsigned i=0;i<5;++i)OP455String(m_soundLabels[i],soundNames[i]);
    for(unsigned i=0;i<2;++i){OP455String(m_eaxLabels[i],i?0xe8b:0xe8c);OP455String(m_specialLabels[i],i?0xe8b:0xe8c);}
    OP455String(m_graphicTitle,0x3f2);const unsigned graphicNames[]={0x3f3,0x3f4,0x3f5,0x3f6,0x3f7,0xe0b};for(unsigned i=0;i<6;++i)OP455String(m_graphicLabels[i],graphicNames[i]);
    OP455String(m_etcTitle,0x3f8);const unsigned etcNames[]={0x3f9,0x3fd,0x3fb,0x3fa,0x3fe,0x3fc,0xd18,0xe8d};for(unsigned i=0;i<8;++i)OP455String(m_etcLabels[i],etcNames[i]);
    OP455String(m_targetTitle,0x13ce);OP455String(m_targetModeLabels[0],0x13cf);OP455String(m_targetModeLabels[1],0x13d0);const unsigned filterNames[]={0x353,0,1,2,0x78b};for(unsigned i=0;i<5;++i)OP455String(m_targetFilterLabels[i],filterNames[i]);OP455String(m_cameraTitle,0x3ff);
    OP455Center(m_header,GetPosX(),GetPosY()+6,GetSizeX(),m_header.GetSizeY());OP455Center(m_title,m_header.GetPosX(),m_header.GetPosY(),m_header.GetSizeX(),m_header.GetSizeY());m_close.SetPos(m_header.GetPosX()+m_header.GetSizeX()-m_close.GetSizeX()-4,m_header.GetPosY()+4);m_help.SetPos(m_header.GetPosX()+4,m_header.GetPosY()+4);
    const LONG buttonX[]={237,346,128};for(unsigned i=0;i<3;++i)m_actionsButtons[i].SetPos(GetPosX()+buttonX[i],GetPosY()+38);
    m_soundTitle.SetPos(GetPosX()+11,GetPosY()+76);for(unsigned i=0;i<3;++i){OP455Center(m_soundLabels[i],GetPosX()+130,GetPosY()+91+40*i,94,17);m_sound[i].SetPos(GetPosX()+25,GetPosY()+108+40*i);}for(unsigned i=0;i<2;++i)OP455Center(m_soundLabels[i+3],GetPosX()+267,GetPosY()+91+40*i,94,17);
    for(unsigned i=0;i<2;++i){m_eaxIcons[i].SetPos(GetPosX()+369,GetPosY()+101-12*i);m_eaxLabels[i].SetPos(m_eaxIcons[i].GetPosX()+16,m_eaxIcons[i].GetPosY());m_specialIcons[i].SetPos(GetPosX()+369,GetPosY()+141-12*i);m_specialLabels[i].SetPos(m_specialIcons[i].GetPosX()+16,m_specialIcons[i].GetPosY());}
    m_graphicTitle.SetPos(GetPosX()+11,GetPosY()+213);const LONG sliderY[]={244,291,340,244,291,340},markX[]={30,33,24,248,241,248},markY[]={255,303,350,256,303,351};
    for(unsigned i=0;i<6;++i){OP455Center(m_graphicLabels[i],GetPosX()+(i<3?130:346),GetPosY()+228+48*(i%3),i<3?94:90,17);m_graphic[i].SetPos(GetPosX()+(i<3?24:240),GetPosY()+sliderY[i]);m_marks[i].SetPos(GetPosX()+markX[i],GetPosY()+markY[i]);}
    m_targetTitle.SetPos(GetPosX()+11,GetPosY()+376);LONG x=0;for(unsigned i=0;i<2;++i){m_targetModes[i].SetPos(GetPosX()+x+8,GetPosY()+401);x+=m_targetModes[i].GetSizeX()+5;m_targetModeLabels[i].SetPos(GetPosX()+x+8,GetPosY()+401);x+=m_targetModeLabels[i].GetSizeX()+10;}
    x=0;for(unsigned i=0;i<5;++i){m_targetFilters[i].SetPos(GetPosX()+x+8,GetPosY()+420);x+=m_targetFilters[i].GetSizeX()+5;m_targetFilterLabels[i].SetPos(GetPosX()+x+8,GetPosY()+420);x+=m_targetFilterLabels[i].GetSizeX()+10;}
    m_etcTitle.SetPos(GetPosX()+11,GetPosY()+445);for(unsigned i=0;i<m_etcCount;++i){m_etc[i].SetPos(GetPosX()+8+101*(i<3?i:i-3),GetPosY()+(i<3?470:489));m_etcLabels[i].SetPos(m_etc[i].GetPosX()+m_etc[i].GetSizeX()+5,m_etc[i].GetPosY());}
    for(unsigned i=6;i<8;++i){m_etc[i].SetPos(GetPosX()+311,GetPosY()+(i==6?470:489));m_etcLabels[i].SetPos(m_etc[i].GetPosX()+m_etc[i].GetSizeX()+5,m_etc[i].GetPosY());}
    m_cameraTitle.SetPos(GetPosX()+256,GetPosY()+517);for(unsigned i=0;i<5;++i)m_cameras[i].SetPos(GetPosX()+340+17*i,GetPosY()+513);
    Add(&m_header);Add(&m_title);m_close.AddMouseEventHandler(this);m_help.AddMouseEventHandler(this);Add(&m_close);Add(&m_help);
    for(unsigned i=0;i<(m_ratingVisible?3u:2u);++i){m_actionsButtons[i].AddMouseEventHandler(this);Add(&m_actionsButtons[i]);}Add(&m_soundTitle);
    for(unsigned i=0;i<3;++i){m_sound[i].AddScrollHandler(this);Add(&m_soundLabels[i]);Add(&m_sound[i]);}Add(&m_soundLabels[3]);Add(&m_soundLabels[4]);
    for(unsigned i=0;i<2;++i){m_eaxIcons[i].AddMouseEventHandler(this);m_eaxLabels[i].AddMouseEventHandler(this);Add(&m_eaxLabels[i]);Add(&m_eaxIcons[i]);m_specialIcons[i].AddMouseEventHandler(this);m_specialLabels[i].AddMouseEventHandler(this);Add(&m_specialLabels[i]);Add(&m_specialIcons[i]);}
    Add(&m_graphicTitle);for(unsigned i=0;i<6;++i){m_graphic[i].AddScrollHandler(this);Add(&m_graphicLabels[i]);Add(&m_graphic[i]);Add(&m_marks[i]);}
    Add(&m_etcTitle);for(unsigned i=0;i<m_etcCount;++i){m_etc[i].AddMouseEventHandler(this);m_etcLabels[i].AddMouseEventHandler(this);Add(&m_etc[i]);Add(&m_etcLabels[i]);}Add(&m_cameraTitle);for(auto& camera:m_cameras){camera.AddMouseEventHandler(this);Add(&camera);}
    Add(&m_targetTitle);for(unsigned i=0;i<2;++i){m_targetModes[i].AddMouseEventHandler(this);Add(&m_targetModes[i]);Add(&m_targetModeLabels[i]);}for(unsigned i=0;i<5;++i){m_targetFilters[i].AddMouseEventHandler(this);Add(&m_targetFilters[i]);Add(&m_targetFilterLabels[i]);}
    m_title.GetFont()->dwColor=0xffc3c1be;m_soundTitle.GetFont()->dwColor=m_graphicTitle.GetFont()->dwColor=m_etcTitle.GetFont()->dwColor=m_targetTitle.GetFont()->dwColor=0xffd4d0be;m_cameraTitle.GetFont()->dwColor=0xffc3c1be;
    for(auto& label:m_soundLabels)label.GetFont()->dwColor=0xffc3c1be;for(auto& label:m_graphicLabels)label.GetFont()->dwColor=0xffc3c1be;for(unsigned i=0;i<m_etcCount;++i)m_etcLabels[i].GetFont()->dwColor=0xffc3c1be;for(auto& label:m_targetModeLabels)label.GetFont()->dwColor=0xffe8e8e8;for(auto& label:m_targetFilterLabels)label.GetFont()->dwColor=0xffe8e8e8;
    m_title.SetMouseInput455(FALSE);SetMoveObject(&m_header);SetMovable(TRUE);for(auto& slider:m_sound){slider.SetTotalAmount(160);slider.SetAdjustmentUnit(1);slider.SetArrowAdjustmentUnit(8);}const LONG totals[]={10,3,3,6,2,3};for(unsigned i=0;i<6;++i)m_graphic[i].SetTotalAmount(totals[i]);for(unsigned i=0;i<m_etcCount;++i)SwitchOn(EtcOption(i),FALSE);SetARGB((GetARGB()&0xffffff)|0xe0000000);
}
void CGUIOptionWindow::Send455(UINT message,WPARAM value){auto* screen=CGUIScreen::GetSingletonPtr();if(screen)PostMessage(screen->GetHWND(),message,value,0);}
void CGUIOptionWindow::SetSoundOption(SoundOption which,float value){const unsigned i=unsigned(which);if(i>=3)return;if(!std::isfinite(value))throw std::invalid_argument("455 Option nonfinite volume outside admitted domain");m_sound[i].SetCurrentAmount(int(double(m_sound[i].GetTotalAmount())*double(value)));}
float CGUIOptionWindow::GetSoundOption(SoundOption which){const unsigned i=unsigned(which);return i<3?float(double(m_sound[i].GetCurrentAmount())/double(m_sound[i].GetTotalAmount())):0;}
void CGUIOptionWindow::SetGraphicOption(GraphicOption which,float value){const unsigned i=unsigned(which);if(i>=6)return;if(!std::isfinite(value))throw std::invalid_argument("455 Option nonfinite graphics outside admitted domain");m_graphic[i].SetCurrentAmount(i?int(value):int(double(m_graphic[i].GetTotalAmount())*(double(value)-0.8)));}
float CGUIOptionWindow::GetGraphicOption(GraphicOption which){const unsigned i=unsigned(which);return i<6?float(m_graphic[i].GetCurrentAmount()):0;}
void CGUIOptionWindow::SwitchOn(EtcOption which,BOOL value){const unsigned i=unsigned(which);if(i>=8){if(i<10)m_legacyFlags[i-8]=value;return;}if(i<m_etcCount)m_etc[i].GetSpriteInfo()->wFrameNo=value?0:1;}
BOOL CGUIOptionWindow::IsSwitchOn(EtcOption which){const unsigned i=unsigned(which);if(i>=8)return i<10?m_legacyFlags[i-8]:FALSE;return i<m_etcCount&&m_etc[i].GetSpriteInfo()->wFrameNo==0;}
void CGUIOptionWindow::SelectCamera(BYTE value){OP455Radio(m_cameras,m_camera,value,5,4,9);}
void CGUIOptionWindow::SelectEax455(BYTE value){if(value==m_eax||value>=2||m_eax>=2)return;m_eaxIcons[m_eax].GetSpriteInfo()->wFrameNo=18;m_eax=value;m_eaxIcons[value].GetSpriteInfo()->wFrameNo=19;}
void CGUIOptionWindow::SelectSpecial455(BYTE value){if(value==m_special||value>=2||m_special>=2)return;m_specialIcons[m_special].GetSpriteInfo()->wFrameNo=18;m_special=value;m_specialIcons[value].GetSpriteInfo()->wFrameNo=19;}
void CGUIOptionWindow::SetTargetingMode455(int value){if(unsigned(value)>=2)return;for(unsigned i=0;i<2;++i)OP455Bind(m_targetModes[i],5,0,i==unsigned(value)?19:18);Send455(0x62a,value);m_targetMode=BYTE(value);}
void CGUIOptionWindow::SetTargetingFilter455(int index,WPARAM value){if(unsigned(index)>=5)return;OP455Bind(m_targetFilters[index],5,0,value?0:1);Send455(0x62b+index,value);m_targetMask^=BYTE(1u<<index);}
void CGUIOptionWindow::SetTargetingFilters455(BYTE mask){for(unsigned i=0;i<5;++i)SetTargetingFilter455(i,(1u<<i)&mask);}
void CGUIOptionWindow::Update(){for(unsigned i=0;i<2;++i){if(m_logoutRestricted)m_actionsButtons[i].Disable();else m_actionsButtons[i].Enable();}}
void CGUIOptionWindow::MouseEvent(_mouse_event& event){
    CGUIWindow::MouseEvent(event);
    if(event.id==MOUSE_CLICKED){if(event.source==&m_actionsButtons[0]||event.source==&m_actionsButtons[1]){if(m_actions.blocked&&m_actions.blocked())return;const auto action=event.source==&m_actionsButtons[0]?m_actions.logout:m_actions.quit;if(action)action();}else if(event.source==&m_actionsButtons[2]){if(m_actions.rating)m_actions.rating();}else if(event.source==&m_close)Close();else if(event.source==&m_help)Send455(0x1204,m_dwID);return;}
    if(event.id!=MOUSE_STROKED)return;
    const UINT messages[]={0x602,0x600,0x604,0x603,0x601,0x605};for(unsigned i=0;i<m_etcCount;++i)if(event.source==&m_etc[i]||event.source==&m_etcLabels[i]){if(i<6)Send455(messages[i],!IsSwitchOn(EtcOption(i)));else{SwitchOn(EtcOption(i),!IsSwitchOn(EtcOption(i)));if(i==6&&!IsSwitchOn(EtcOption(i))&&m_actions.dismissStartupBoard)m_actions.dismissStartupBoard();}return;}
    for(unsigned i=0;i<5;++i)if(event.source==&m_cameras[i]){if(m_camera!=i)Send455(0x608,i);return;}
    for(unsigned i=0;i<2;++i){if(event.source==&m_eaxIcons[i]||event.source==&m_eaxLabels[i]){if(m_eax!=i)Send455(0x626,i);return;}if(event.source==&m_specialIcons[i]||event.source==&m_specialLabels[i]){if(m_special!=i)Send455(0x627,i);return;}}
    for(unsigned i=0;i<2;++i)if(event.source==&m_targetModes[i]&&m_targetMode!=i)SetTargetingMode455(i);
    for(unsigned i=0;i<5;++i)if(event.source==&m_targetFilters[i])SetTargetingFilter455(i,!IsTargetingFilter455(BYTE(i)));
}
void CGUIOptionWindow::ScrollEvent(_scroll_event& event){const UINT soundMessages[]={0x628,0x609,0x610},graphicsMessages[]={0x611,0x612,0x613,0x606,0x614,0x625};for(unsigned i=0;i<3;++i)if(event.source==&m_sound[i]){Send455(soundMessages[i]);return;}for(unsigned i=0;i<6;++i)if(event.source==&m_graphic[i]){Send455(graphicsMessages[i],m_graphic[i].GetCurrentAmount());if(i==3&&IsSwitchOn(AutoSeeDist))Send455(0x601,0);return;}}
