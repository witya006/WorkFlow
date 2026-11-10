// Pinned455 b1b5febf...,x86/base400000:6ACFA0..6AE7A7. Full ASM/CFG bothpins.
#undef min
#undef max
namespace {
CSprite* MC455Sprite(BYTE id,WORD action,WORD frame){
    auto* sprite=gSpriteMgr.GetTargetSprite455(id);
    if(!sprite||action>=sprite->GetMaxActions()||frame>=sprite->GetMaxFrames(action))throw std::runtime_error("455 MobControl sprite/frame missing");
    return sprite;
}
void MC455Bind(CGUIObject& object,BYTE id,WORD action,WORD frame){
    auto* sprite=MC455Sprite(id,action,frame);SPRITE_INFO info={sprite,action,frame};object.SetSpriteInfo(&info);
    object.SetSize(sprite->GetSpriteOrgXL(action,frame),sprite->GetSpriteOrgYL(action,frame));
}
LONG MC455Width(CGUIObject& object){auto* info=object.GetSpriteInfo();return info->pSprite?info->pSprite->GetSpriteOrgXL(info->wActionNo,info->wFrameNo):0;}
void MC455Crop(CGUIObjectEx& object,float ratio){object.SetSpriteU(0,ratio);object.SetSize(LONG(double(MC455Width(object))*double(ratio)),object.GetSizeY());}
void MC455Gauge(CGUIObjectEx& bar,CGUIImageText455& text,int current,int maximum){
    current=std::max(0,current);maximum=std::max(0,maximum);char buffer[32];std::snprintf(buffer,sizeof(buffer),"%6d / %d",current,maximum);text.SetString455(buffer);
    float ratio=maximum?float(double(current)/double(maximum)):0.0f;if(ratio>1)ratio=1;bar.SetSpriteU(0,ratio);bar.SetSize(LONG(double(ratio)*130.0),11);
}
}
CGUIMobControl::~CGUIMobControl(){g_cMoveObjectMgr.RemoveObject(&m_commands);m_commands.RemoveAll();m_commandViewport.RemoveAll();RemoveAll();}
void CGUIMobControl::SetSprite(){
    MC455Bind(*this,13,1,0);MC455Bind(m_board,13,1,1);MC455Bind(m_exp,13,0,3);MC455Bind(m_resourceGauge,13,0,4);MC455Bind(m_commandIcon,13,2,1);
    auto* sprite=MC455Sprite(13,2,2);for(unsigned i=0;i<3;++i){SPRITE_INFO info={sprite,2,WORD(i)};m_commandButtons[i].SetSpriteInfoEx(&info);m_commandButtons[i].SetSize(sprite->GetSpriteOrgXL(2,WORD(i)),sprite->GetSpriteOrgYL(2,WORD(i)));}
    MC455Bind(m_hp,4,0,1);MC455Bind(m_fp,4,0,2);
    for(auto* text:{&m_hpText,&m_fpText,&m_level,&m_expText})text->Configure455(1,7,3,7,9);
}
void CGUIMobControl::Init(){
    SetSprite();m_board.SetSize(m_ptSize);m_commands.SetSize(m_commandButtons[0].GetSizeX()*3,m_commandButtons[0].GetSizeY());m_board.SetPos(m_ptPos);
    m_level.SetPos(GetPosX()+9,GetPosY()+49);m_name.SetPos(GetPosX()+159,GetPosY()+48);
    m_hp.SetPos(GetPosX()+26,GetPosY()+17);m_hpText.SetPos(m_hp.GetPosX()+15,m_hp.GetPosY()+1);
    m_fp.SetPos(GetPosX()+26,GetPosY()+31);m_fpText.SetPos(m_fp.GetPosX()+15,m_fp.GetPosY()+1);
    m_exp.SetPos(GetPosX()+26,GetPosY()+50);m_expRemainder.SetPos(GetPosX()+25,GetPosY()+57);
    m_resourceIcon.SetPos(GetPosX()+163,GetPosY()+16);m_commandIcon.SetPos(GetPosX()+193,GetPosY()+16);
    m_commandBoard.SetSize(GetPosX()+GetSizeX()-m_commandIcon.GetPosX(),m_commandIcon.GetSizeY());m_commandBoard.SetPos(m_commandIcon.m_ptPos);
    m_commandViewport.SetPos(GetPosX()+GetSizeX(),m_commandIcon.GetPosY());m_commands.SetPos(m_commandViewport.m_ptPos);
    for(unsigned i=0;i<3;++i){m_commandButtons[i].SetPos(m_commands.GetPosX()+m_commandButtons[i].GetSizeX()*i,m_commands.GetPosY());m_commandButtons[i].AddMouseEventHandler(this);m_commands.Add(&m_commandButtons[i]);}
    CGUIObject* children[]={&m_board,&m_name,&m_level,&m_hp,&m_hpText,&m_exp,&m_expRemainder,&m_expText,&m_fp,&m_fpText,&m_resourceIcon,&m_resourceGauge,&m_resourceText,&m_commandBoard,&m_commandIcon,&m_commandViewport};
    for(auto* child:children)Add(child);m_commandIcon.AddMouseEventHandler(this);m_commandViewport.Add(&m_commands);
    m_name.GetFont()->dwColor=DWORD(-2698033);m_resourceGauge.SetARGB(DWORD(-65408));m_expRemainder.SetARGB(DWORD(-4195107));m_expText.SetARGB(DWORD(-3491162));
    SetMoveObject(&m_board);SetMoveObject(&m_name);SetMovable(TRUE);SetLevel(1);SetExp(0);SetHP(0,0);SetFP(0,0);SetName("MobControl");SetARGB((GetARGB()&0xffffff)|0xd8000000);
}
void CGUIMobControl::SetMobName(char* value){
    const auto* country=RF455_GetNormalNationPaths();if(country->configured&&country->nation==0&&std::strlen(value)>7)value+=7;
    m_name.SetString(value);m_name.SetPos(GetPosX()+158+(42-m_name.GetSizeX())/2,m_name.GetPosY());
}
void CGUIMobControl::SetLevel(BYTE value){char text[8];std::snprintf(text,sizeof(text),"%u",unsigned(value));m_level.SetString455(text);m_level.SetPos(GetPosX()+15-m_level.GetSizeX()/2,m_level.GetPosY());}
void CGUIMobControl::SetHP(int current,int maximum){MC455Gauge(m_hp,m_hpText,current,maximum);}
void CGUIMobControl::SetFP(int current,int maximum){MC455Gauge(m_fp,m_fpText,current,maximum);}
void CGUIMobControl::SetExp(float fraction){
    if(!std::isfinite(fraction))throw std::invalid_argument("455 MobControl nonfinite EXP domain not admitted");fraction=std::max(0.0f,std::min(1.0f,fraction));
    float accumulated=0;while(double(fraction)-double(accumulated)>=double(0.1f))accumulated=float(double(accumulated)+double(0.1f));
    const float remainder=double(fraction)-double(accumulated)>0?float((double(fraction)-double(accumulated))/double(0.1f)):0;
    float step=accumulated;const LONG width=MC455Width(m_exp);if(width>0)step=float(double(9*int(double(fraction)*10.0))/double(width));if(step>1)step=1;MC455Crop(m_exp,step);
    m_expRemainder.SetSize(LONG(double(remainder)*90.0),1);float percent=float(double(fraction)*100.0);if(percent>99.98999786376953f)percent=99.98999786376953f;
    char text[16];std::snprintf(text,sizeof(text),"%.2f%%",double(percent));m_expText.SetString455(text);m_expText.SetPos(GetPosX()+157-m_expText.GetSizeX(),GetPosY()+49);
}
void CGUIMobControl::SetResource455(int current,int maximum){
    current=std::max(0,current);maximum=std::max(1,maximum);current=std::min(current,maximum);
    MC455Bind(m_resourceIcon,13,2,current?4:3);
    if(!current){m_resourceText.SetString("");m_resourceGauge.Show(FALSE);return;}
    // x86 IMUL wraps before signed IDIV; avoid C++ signed-overflow UB.
    const DWORD product=DWORD(current)*100u;int signedProduct;std::memcpy(&signedProduct,&product,4);float percent=float(signedProduct/maximum);if(percent>99.98999786376953f)percent=99.98999786376953f;
    char text[40];std::snprintf(text,sizeof(text),"%d%% / %d",int(percent),current);m_resourceText.SetString(text);
    const LONG width=MC455Width(m_resourceGauge);float ratio=width>0?float(double(9*int(double(percent)/100.0*10.0))/double(width)):0;if(ratio>1)ratio=1;
    MC455Crop(m_resourceGauge,ratio);m_resourceGauge.SetPos(GetPosX()+GetSizeX()-m_resourceGauge.GetSizeX()-80,GetPosY()+7);m_resourceGauge.Show(TRUE);
    m_resourceText.SetPos(GetPosX()+GetSizeX()-m_resourceText.GetSizeX()-10,GetPosY()+2);
}
void CGUIMobControl::OpenCmdBoard(BOOL open){
    if(open){if(m_open)return;m_commandViewport.SetSize(m_commandButtons[0].GetSizeX()*3,m_commandButtons[0].GetSizeY());m_commandViewport.Show(TRUE);
        g_cMoveObjectMgr.AddMoveObject(&m_commands,MOVE_AXIS_X,m_commandViewport.GetPosX()-m_commands.GetSizeX(),m_commandViewport.GetPosX(),200);}
    else{if(!m_open)return;g_cMoveObjectMgr.AddMoveObject(&m_commands,MOVE_AXIS_X,m_commandViewport.GetPosX(),m_commandViewport.GetPosX()-m_commands.GetSizeX(),150);}
    g_cMoveObjectMgr.StartMove(&m_commands);m_open=open;
}
void CGUIMobControl::MouseEvent(_mouse_event& event){
    CGUIWindow::MouseEvent(event);
    if(event.id==MOUSE_CLICKED){for(unsigned i=0;i<3;++i)if(event.source==&m_commandButtons[i]){PostUIMessage(WM_ANIMUSCONTROL_BOARD_COMMAND,i);OpenCmdBoard(FALSE);return;}}
    else if(event.id==MOUSE_HOVERED){if(event.source==&m_commandIcon){OpenCmdBoard(TRUE);return;}static const unsigned labels[]={0x3ce,0x3cf,0x39d};for(unsigned i=0;i<3;++i)if(event.source==&m_commandButtons[i]){SetTooltip(&m_commandButtons[i],const_cast<char*>(RF455_GetNormalLanguagePack()->get(labels[i])));return;}}
    else if(event.id==MOUSE_LEAVED){
        if(IS_HOVERED(m_commandBoard.GetState()))return;
        if(event.source==&m_commandIcon){if(IS_HOVERED(m_commandViewport.GetState()))return;}else if(IS_HOVERED(m_commandIcon.GetState()))return;
        for(auto& button:m_commandButtons)if(IS_HOVERED(button.GetState()))return;OpenCmdBoard(FALSE);
    }
}
BOOL CGUIMobControl::IsCrossed(LONG x,LONG y){return CGUIObject::IsCrossed(x,y)||m_commandViewport.IsCrossed(x,y);}
void CGUIMobControl::Update(){if(!IsShow())return;CGUIWindow::Update();if(!m_open&&m_commandViewport.GetSizeX()>0&&g_cMoveObjectMgr.IsFinishedMove(&m_commands)){m_commandViewport.SetSize(0,0);m_commandViewport.Show(FALSE);}}
