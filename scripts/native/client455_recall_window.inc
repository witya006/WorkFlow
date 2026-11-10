//455x86/b1b5febf...:6AE7B0..6B0BEF. Full ASM/CFG:recall162-reference.
#undef min
#undef max
namespace {
CSprite* RecallSprite455(BYTE id,WORD action,WORD frame){
    auto* sprite=gSpriteMgr.GetTargetSprite455(id);
    if(!sprite||action>=sprite->GetMaxActions()||frame>=sprite->GetMaxFrames(action))throw std::runtime_error("455Recall sprite/frame missing");
    return sprite;
}
void RecallBind455(CGUIObject& object,BYTE id,WORD action,WORD frame){
    auto* sprite=RecallSprite455(id,action,frame);SPRITE_INFO info={sprite,action,frame};object.SetSpriteInfo(&info);object.SetSize(sprite->GetSpriteOrgXL(action,frame),sprite->GetSpriteOrgYL(action,frame));
}
void RecallFullBar455(CGUIObjectEx& bar,WORD frame){RecallBind455(bar,13,0,frame);bar.SetSpriteU(0,1);bar.SetSpriteV(0,1);}
void RecallCrop455(CGUIObjectEx& bar,float amount){
    if(!std::isfinite(amount)||std::fabs(double(amount))>1000000)throw std::domain_error("455Recall crop outside admitted finite coordinate domain");
    auto* info=bar.GetSpriteInfo();if(!info->pSprite)throw std::logic_error("455Recall crop before sprite initialization");
    bar.SetSpriteU(0,amount);bar.SetSize(LONG(double(info->pSprite->GetSpriteOrgXL(info->wActionNo,info->wFrameNo))*double(amount)),bar.GetSizeY());
}
int RecallSigned455(DWORD value){int result;std::memcpy(&result,&value,4);return result;}
void RecallButton455(CGUIButton& button,WORD frame){
    auto* sprite=RecallSprite455(1,0,WORD(frame+2));SPRITE_INFO normal={sprite,0,frame};button.SetSpriteInfoEx(&normal);
    SPRITE_INFO hover={sprite,0,WORD(frame+1)},pressed={sprite,0,WORD(frame+2)};button.SetSpriteInfoEx(HOVERED,&hover);button.SetSpriteInfoEx(PRESSED,&pressed);button.SetSize(sprite->GetSpriteOrgXL(0,frame),sprite->GetSpriteOrgYL(0,frame));
}
}

CGUIRecallUnit::CGUIRecallUnit(){
    SetSprite();SetSize(204,56);m_cover.SetSize(m_ptSize);m_underline.SetSize(GetSizeX(),1);m_item.SetSize(38,38);
    m_name.SetPos(GetPosX()+45,GetPosY()+5);m_level.SetPos(GetPosX()+165,GetPosY()+5);m_item.SetPos(GetPosX()+2,GetPosY()+4);
    m_gaugeBase.SetPos(GetPosX()+40,GetPosY()+21);m_hp.SetPos(m_gaugeBase.GetPosX()+22,m_gaugeBase.GetPosY());m_fp.SetPos(m_gaugeBase.GetPosX()+22,m_gaugeBase.GetPosY()+11);m_exp.SetPos(m_gaugeBase.GetPosX()+22,m_gaugeBase.GetPosY()+24);
    m_hpText.SetPos(m_gaugeBase.GetPosX()+25,m_hp.GetPosY());m_fpText.SetPos(m_gaugeBase.GetPosX()+25,m_fp.GetPosY());m_expText.SetPos(m_gaugeBase.GetPosX()+m_gaugeBase.GetSizeX()-m_expText.GetSizeX()-5,m_exp.GetPosY()-3);
    m_underline.SetPos(GetPosX(),GetPosY()+GetSizeY()-1);m_cover.SetPos(m_ptPos);
    CGUIObject* objects[]={&m_name,&m_level,&m_item,&m_gaugeBase,&m_hp,&m_fp,&m_exp,&m_hpText,&m_fpText,&m_expBase,&m_expText,&m_underline,&m_cover};for(auto* object:objects)Add(object);
    m_underline.SetARGB(0xa0020202);m_name.GetFont()->dwColor=0xffffffff;m_level.GetFont()->dwColor=0xffffb847;m_expBase.SetARGB(DWORD(-14539224));m_expText.SetARGB(0xfffffec6);
}
CGUIRecallUnit::~CGUIRecallUnit(){RemoveAll();}
void CGUIRecallUnit::SetSprite(){
    RecallBind455(m_gaugeBase,13,0,0);RecallFullBar455(m_hp,1);RecallFullBar455(m_fp,2);RecallFullBar455(m_exp,3);
    m_hpText.Configure455(1,7,3,7,9);m_fpText.Configure455(1,7,3,7,9);m_expText.Configure455(1,7,3,7,9);
}
void CGUIRecallUnit::SetUnitState(UnitState state){
    if(m_state==state)return;m_state=state;
    switch(state){case Enabled:case Linked:m_cover.SetARGB(0xffffffff);break;case Disabled:m_cover.SetARGB(0x80a05050);break;case NoneUnit:m_cover.SetARGB(0xb0000000);break;}
    if(state!=Linked)m_item.SetRefItem(nullptr);
}
void CGUIRecallUnit::SetMobName(char* value){m_name.SetString(value);}
void CGUIRecallUnit::SetLevel(BYTE level){char text[16];std::snprintf(text,sizeof(text),"Lv %u",unsigned(level));m_level.SetString(text);}
void CGUIRecallUnit::SetItem(DWORD item,DWORD sprite){m_item.SetItemID(item);m_item.SetSpriteID(sprite);m_item.SetIconType455(4);m_item.SetSprite();}
void CGUIRecallUnit::SetHP(DWORD current,DWORD maximum){
    char text[32];std::snprintf(text,sizeof(text),"%8d / %d",RecallSigned455(current),RecallSigned455(maximum));m_hpText.SetString455(text);
    const float ratio=maximum?float(double(current)/double(maximum)):0.0f;RecallCrop455(m_hp,std::min(1.0f,ratio));
}
void CGUIRecallUnit::SetFP(DWORD current,DWORD maximum){
    char text[32];std::snprintf(text,sizeof(text),"%8d / %d",RecallSigned455(current),RecallSigned455(maximum));m_fpText.SetString455(text);
    const float ratio=maximum?float(double(current)/double(maximum)):0.0f;RecallCrop455(m_fp,std::min(1.0f,ratio));
}
void CGUIRecallUnit::SetExp(float percentage){
    //Only the text is capped. The target retains an uncapped geometric ratio.
    if(!std::isfinite(percentage))throw std::domain_error("455Recall nonfinite EXP outside verified domain");
    RecallCrop455(m_exp,percentage/100.0f);if(percentage>99.98999786376953f)percentage=99.98999786376953f;
    char text[64];std::snprintf(text,sizeof(text),"%.2f%%",double(percentage));m_expText.SetString455(text);
    m_expText.SetPos(m_gaugeBase.GetPosX()+m_gaugeBase.GetSizeX()-m_expText.GetSizeX()-5,m_exp.GetPosY()-3);
    m_expBase.SetSize(m_expText.GetSizeX()+10,m_expText.GetSizeY());m_expBase.SetPos(m_expText.GetPosX()-5,m_expText.GetPosY());
}

CGUIRecallWindow::~CGUIRecallWindow(){m_content.RemoveAll();m_units.clear();m_viewport.RemoveAll();RemoveAll();}
void CGUIRecallWindow::SetSprite(){
    m_header.SetImage455(RecallSprite455(1,4,0),4,0);RecallButton455(m_close,0);RecallButton455(m_help,3);RF455_ConfigureModalScrollbar(m_scroll);RecallBind455(m_resize,1,4,2);
}
void CGUIRecallWindow::Init(){
    SetSprite();SetSize(228,395);m_background.SetSize(m_ptSize);m_background.SetOutline455(3,1,DWORD(-9802126));m_background.SetARGB(DWORD(-14539224));
    m_viewport.SetSize(208,GetSizeY()-m_header.GetSizeY()-m_resize.GetSizeY()-16);m_content.SetSize(m_viewport.m_ptSize);m_title.SetString(const_cast<char*>(RF455_GetNormalLanguagePack()->get(0xc3)));
    m_background.SetPos(m_ptPos);m_header.SetPos(GetPosX()+(GetSizeX()-m_header.GetSizeX())/2,GetPosY()+6);m_title.SetPos(m_header.GetPosX()+(m_header.GetSizeX()-m_title.GetSizeX())/2,m_header.GetPosY()+(m_header.GetSizeY()-m_title.GetSizeY())/2);
    m_close.SetPos(m_header.GetPosX()+m_header.GetSizeX()-m_close.GetSizeX()-4,m_header.GetPosY()+4);m_help.SetPos(m_header.GetPosX()+4,m_header.GetPosY()+4);
    m_viewport.SetPos(GetPosX()+6,m_header.GetPosY()+m_header.GetSizeY()+12);m_content.SetPos(m_viewport.m_ptPos);
    Add(&m_background);Add(&m_header);Add(&m_title);m_close.AddMouseEventHandler(this);m_help.AddMouseEventHandler(this);Add(&m_close);Add(&m_help);m_viewport.AddMouseEventHandler(this);Add(&m_viewport);m_viewport.Add(&m_content);m_scroll.AddScrollHandler(this);Add(&m_scroll);m_resize.AddMouseEventHandler(this);Add(&m_resize);
    m_title.GetFont()->dwColor=DWORD(-3686986);m_scroll.SetAdjustmentUnit(56);SetReSizeObject(BOTTOM,&m_resize);SetReSizable(TRUE);RECT bounds;GetBound(bounds);SetBound(bounds);m_title.SetMouseInput455(FALSE);SetMoveObject(&m_header);SetMovable(TRUE);SetWheelScrollObject(&m_scroll);SetName("recallWindow");SetARGB((GetARGB()&0xffffff)|0xd8000000);
}
void CGUIRecallWindow::SetBound(RECT& bounds){
    if(bounds.bottom-bounds.top<m_header.GetSizeY()+m_resize.GetSizeY()+137)return;
    CGUIObject::SetBound(bounds);m_background.SetBound(bounds);m_resize.SetPos(GetPosX()+(GetSizeX()-m_resize.GetSizeX())/2,GetPosY()+GetSizeY()-m_resize.GetSizeY()-6);
    m_viewport.SetSize(m_viewport.GetSizeX(),m_resize.GetPosY()-GetPosY()-m_header.GetSizeY()-12);
    RECT scrollBounds={GetPosX()+GetSizeX()-m_scroll.GetSizeX()-3,m_viewport.GetPosY(),GetPosX()+GetSizeX()-3,m_resize.GetPosY()};m_scroll.SetBound(scrollBounds);UpdateScrollbar();
}
BOOL CGUIRecallWindow::TakeInItem(_recall_info* info){
    if(!info)throw std::invalid_argument("455Recall null record outside admitted domain");if(GetRecallUnitByIndex(info->dwIndex))return FALSE;
    auto row=std::unique_ptr<CGUIRecallUnit>(new CGUIRecallUnit);row->SetSprite();row->SetIndex(info->dwIndex);row->SetMobName(info->pName);row->SetItem(info->dwItemID,info->dwSpriteID);row->SetLevel(info->byLevel);row->SetHP(DWORD(info->nCurHP),DWORD(info->nMaxHP));row->SetFP(DWORD(info->nCurFP),DWORD(info->nMaxFP));row->SetExp(info->fExp);row->GetCover()->AddMouseEventHandler(this);
    row->SetPos(m_content.GetPosX(),m_content.GetPosY()+LONG(m_units.size())*row->GetSizeY());auto* added=row.get();m_units.push_back(std::move(row));m_content.Add(added);m_content.SetSize(m_content.GetSizeX(),LONG(m_units.size())*added->GetSizeY());UpdateScrollbar();return TRUE;
}
BOOL CGUIRecallWindow::TakeOutItem(DWORD index){
    for(auto it=m_units.begin();it!=m_units.end();++it)if((*it)->GetIndex()==index){m_content.Remove(it->get());m_units.erase(it);unsigned row=0;for(auto& unit:m_units){unit->SetPos(m_content.GetPosX(),m_content.GetPosY()+LONG(row++)*unit->GetSizeY());}UpdateScrollbar();return TRUE;}
    return FALSE; //6B0020 deliberately does not reduce m_content height.
}
void CGUIRecallWindow::UpdateScrollbar(){
    LONG total=m_viewport.GetPosY()-m_content.GetPosY();const LONG overflow=m_content.GetPosY()+m_content.GetSizeY()-m_viewport.GetPosY()-m_viewport.GetSizeY();if(overflow>0)total+=overflow;
    m_scroll.SetAmount(total,std::min(total,m_scroll.GetCurrentAmount()));m_content.SetPos(m_content.GetPosX(),m_viewport.GetPosY()-m_scroll.GetCurrentAmount());
}
CGUIRecallUnit* CGUIRecallWindow::GetRecallUnitByIndex(DWORD index){for(auto& row:m_units)if(row->GetIndex()==index)return row.get();return nullptr;}
CGUIRecallUnit* CGUIRecallWindow::GetRecallUnitByItemID(DWORD item){for(auto& row:m_units)if(row->GetItemID()==item)return row.get();return nullptr;}
CGUIRecallUnit* CGUIRecallWindow::GetRecallUnitByEventObj(CGUIObject* object){for(auto& row:m_units)if(row->GetCover()==object)return row.get();return nullptr;}
void CGUIRecallWindow::SetLevel(DWORD index,BYTE level,BOOL byIndex){if(auto* row=Resolve455(index,byIndex))row->SetLevel(level);}
void CGUIRecallWindow::SetHP(DWORD index,int current,int maximum,BOOL byIndex){if(auto* row=Resolve455(index,byIndex))row->SetHP(DWORD(current),DWORD(maximum));}
void CGUIRecallWindow::SetFP(DWORD index,int current,int maximum,BOOL byIndex){if(auto* row=Resolve455(index,byIndex))row->SetFP(DWORD(current),DWORD(maximum));}
void CGUIRecallWindow::SetExp(DWORD index,float percentage,BOOL byIndex){if(auto* row=Resolve455(index,byIndex))row->SetExp(percentage);}
void CGUIRecallWindow::SetItemState(DWORD index,CGUIRecallUnit::UnitState state,BOOL byIndex){if(auto* row=Resolve455(index,byIndex))row->SetUnitState(state);}
BOOL CGUIRecallWindow::TakeOutLink(DWORD index,BOOL byIndex){
    //Existing source adapter for the still-mixed Animus board drag producer.
    //Full455 drag/link lifecycle is a separate unaccepted contract.
    auto* row=Resolve455(index,byIndex);if(!row)return FALSE;gScreen.AddObject(row->GetItem());gScreen.GetObject()->SetRefItem(row->GetItem());gScreen.ResizeObject(40,40);row->SetUnitState(CGUIRecallUnit::Linked);return TRUE;
}
void CGUIRecallWindow::MouseEvent(_mouse_event& event){
    CGUIWindow::MouseEvent(event);
    if(event.id==MOUSE_STROKED){
        if(gScreen.ExistObject()){auto* hover=static_cast<CGUIItem*>(gScreen.GetObject());if(auto* row=GetRecallUnitByItemID(hover->GetItemID()))PostUIMessage(WM_BOARD_ADD_OBJECT,row->GetIndex());}
        else if(auto* row=GetRecallUnitByEventObj(event.source)){SetQuickEvent();PostUIMessage(g_bIsQuickEvent_Equip?WM_BOARD_EQUIP_HOT_KEY:WM_BOARD_REMOVE_OBJECT,row->GetIndex());}
    }else if(event.id==LMOUSE_STROKED){if(auto* row=GetRecallUnitByEventObj(event.source))PostUIMessage(WM_BOARD_USE_OBJECT,row->GetIndex());}
    else if(event.id==MOUSE_HOVERED){if(!gScreen.ExistObject())if(auto* row=GetRecallUnitByEventObj(event.source))PostUIMessage(WM_BOARD_HOVER_OBJECT,row->GetIndex());}
    else if(event.id==MOUSE_CLICKED){if(event.source==&m_close)Close();else if(event.source==&m_help)PostMessage(gScreen.GetHWND(),WM_OPEN_WINDOW_HELP,m_dwID,0);}
}
void CGUIRecallWindow::ScrollEvent(_scroll_event&){m_content.SetPos(m_content.GetPosX(),m_viewport.GetPosY()-m_scroll.GetCurrentAmount());}
