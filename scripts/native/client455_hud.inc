//455VA66A0D0/66A4A0/66A5C0/66A6C0/66AA20, primary b1b5febf...
//Full MainGame root, lower EXP, unit modes and caption/notice producers open.
extern CGUICharInfoWindow* g_pUiCharInfoWindow;
namespace {
int RF455_HudSigned(DWORD v){int n;std::memcpy(&n,&v,4);return n;}
void RF455_HudBind(CGUIObject& o,BYTE id,WORD action,WORD frame){
    auto* s=gSpriteMgr.GetTargetSprite455(id);
    if(!s||action>=s->GetMaxActions()||frame>=s->GetMaxFrames(action))throw std::runtime_error("455 HUD sprite/frame missing");
    SPRITE_INFO info={s,action,frame};o.SetSpriteInfo(&info);
    o.SetSize(s->GetSpriteOrgXL(action,frame),s->GetSpriteOrgYL(action,frame));
}
}
void CGUIGaugeExpWindow::SetSprite(){
    RF455_HudBind(*this,4,0,0);
    for(unsigned i=0;i<3;++i){
        RF455_HudBind(m_uiGauge[i],4,0,WORD(i+1));RF455_HudBind(m_gaugeIcons455[i],4,0,WORD(i+4));
        m_gaugeValues455[i].Configure455(1,7,3,7,9);
    }
    //455 descriptors resolve IDs at use time. Reacquire own pointer descriptors
    //even if the cached color survived unloading/device restoration.
    m_fourthColor455=255;SetFourthColor455(1.0f);
    for(auto& bar:m_uiGauge){bar.SetSpriteU(0,1);bar.SetSpriteV(0,1);}
    m_levelImage455.Configure455(1,7,4,8,11);RF455_HudBind(m_notice455,49,0,1);
}
void CGUIGaugeExpWindow::Init(){
    SetSprite();
    for(unsigned i=0;i<3;++i){
        m_uiGaugeBoard[i].SetSize(m_uiGauge[i].m_ptSize);
        m_uiGaugeBoard[i].SetPos(m_ptPos.x+87,m_ptPos.y+14*i+16);
        RECT bounds;m_uiGaugeBoard[i].GetBound(bounds);m_uiGauge[i].SetBound(bounds);
        m_gaugeIcons455[i].SetPos(m_ptPos.x+71,m_ptPos.y+14*i+17);
        m_gaugeValues455[i].SetPos(m_uiGaugeBoard[i].m_ptPos.x,m_uiGaugeBoard[i].m_ptPos.y+1);
        m_gaugeIcons455[i].AddMouseEventHandler(this);
        Add(&m_gaugeIcons455[i]);Add(&m_uiGaugeBoard[i]);Add(&m_uiGauge[i]);Add(&m_gaugeValues455[i]);
        SetGauge(Bar(i),0,0);
    }
    m_uiGaugeBoard[3].SetSize(m_uiGauge[3].m_ptSize);m_uiGaugeBoard[3].SetPos(m_ptPos.x+15,m_ptPos.y+12);
    m_caption455.SetPos(m_ptPos.x+34,m_ptPos.y+17);
    Add(&m_uiGaugeBoard[3]);Add(&m_uiGauge[3]);Add(&m_caption455);Add(&m_levelImage455);
    SetGauge(Bar(3),100,100);
    //The target410D50(0) has an empty body; it is not a level setter.
    Add(&m_notice455);m_notice455.SetPos(85,0);m_notice455.Show(FALSE);m_bCreated=TRUE;
}
void CGUIGaugeExpWindow::SetFourthColor455(float ratio){
    const BYTE color=ratio<0.2f?2:ratio<0.7f?1:0;if(m_fourthColor455==color)return;
    m_fourthColor455=color;RF455_HudBind(m_uiGauge[3],4,0,WORD(color+7));
}
void CGUIGaugeExpWindow::SetGauge(Bar which,DWORD maximum,DWORD current){
    const unsigned i=unsigned(which);if(i>=4)return;if(current>maximum)current=maximum;
    m_nMaxGauge[i]=LONG(maximum);m_nCurrentGauge[i]=LONG(current);
    const float ratio=maximum?float(double(current)/double(maximum)):1.0f;auto& bar=m_uiGauge[i];
    if(i==3){
        SetFourthColor455(ratio);const float low=1.0f-ratio;bar.SetSpriteV(low,1);
        auto* info=bar.GetSpriteInfo();const auto h=info->pSprite->GetSpriteOrgYL(info->wActionNo,info->wFrameNo);
        bar.SetSize(bar.m_ptSize.x,LONG(double(h)*double(1.0f-low)));
        bar.SetPos(m_uiGaugeBoard[3].m_ptPos.x,m_uiGaugeBoard[3].m_ptPos.y+m_uiGaugeBoard[3].m_ptSize.y-bar.m_ptSize.y);
    }else{
        bar.SetSpriteU(0,ratio);auto* info=bar.GetSpriteInfo();const auto w=info->pSprite->GetSpriteOrgXL(info->wActionNo,info->wFrameNo);
        bar.SetSize(LONG(double(w)*double(ratio)),bar.m_ptSize.y);
        char text[32];std::snprintf(text,sizeof(text),"%8d / %d",RF455_HudSigned(current),RF455_HudSigned(maximum));m_gaugeValues455[i].SetString455(text);
    }
    if(g_pUiCharInfoWindow){
        //Target5236/5360/5484/5608,124-byte text owners, indices9..12.
        char text[32];if(i&&maximum==0)std::strcpy(text,"-");
        else std::snprintf(text,sizeof(text),"%d / %d",RF455_HudSigned(current),RF455_HudSigned(maximum));
        g_pUiCharInfoWindow->SetInfoText455(BYTE(9+i),text);
    }
}
void CGUIGaugeExpWindow::SetGauge(Bar which,DWORD current){
    if(unsigned(which)<4)SetGauge(which,DWORD(m_nMaxGauge[which]),current);
}
void CGUIGaugeExpWindow::SetLevel(WORD level){
    m_wLevel=BYTE(level);char text[8];std::snprintf(text,sizeof(text),"%u",unsigned(m_wLevel));m_levelImage455.SetString455(text);
    m_levelImage455.SetPos(36+(22-m_levelImage455.m_ptSize.x)/2,23+(18-m_levelImage455.m_ptSize.y)/2);
    if(g_pUiCharInfoWindow)g_pUiCharInfoWindow->SetInfoText455(3,text);
}
