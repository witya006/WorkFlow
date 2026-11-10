// Pinned455 b1b5febf...,x86/base400000. Inventory views use real owners,not ABI overlays.
namespace {
CSprite* IV455Sprite(BYTE id,WORD action,WORD frame){
    auto* sprite=gSpriteMgr.GetTargetSprite455(id);
    if(!sprite||action>=sprite->GetMaxActions()||frame>=sprite->GetMaxFrames(action)){
        char error[128];std::snprintf(error,sizeof(error),"455 inventory view skin unavailable:id=%u action=%u frame=%u loaded=%u",unsigned(id),unsigned(action),unsigned(frame),unsigned(sprite!=nullptr));throw std::runtime_error(error);
    }
    return sprite;
}
void IV455Bind(CGUIObject& object,BYTE id,WORD action,WORD frame){auto* sprite=IV455Sprite(id,action,frame);SPRITE_INFO image={sprite,action,frame};object.SetSpriteInfo(&image);object.SetSize(sprite->GetSpriteOrgXL(action,frame),sprite->GetSpriteOrgYL(action,frame));}
void IV455Button(CGUIButton& button,BYTE id,WORD action,WORD first){auto* sprite=IV455Sprite(id,action,WORD(first+2));const WORD states[]={0,HOVERED,PRESSED};for(unsigned i=0;i<3;++i){SPRITE_INFO image={sprite,action,WORD(first+i)};button.SetSpriteInfoEx(states[i],&image);}button.SetSize(sprite->GetSpriteOrgXL(action,first),sprite->GetSpriteOrgYL(action,first));}
const char* IV455Text(unsigned id){auto* pack=RF455_GetNormalLanguagePack();if(!pack||pack->records.empty())throw std::logic_error("455 inventory language provider unavailable");return pack->get(id);}
void IV455String(CGUIText& object,unsigned id){object.SetString(const_cast<char*>(IV455Text(id)));}
void IV455Overlay(CGUIObject& object,WORD action,unsigned size,BOOL enabled,BYTE alpha){
    auto* image=object.GetSpriteInfo();image->pSprite=enabled?IV455Sprite(44,action,size==32?0:4):nullptr;image->wActionNo=action;image->wFrameNo=size==32?0:4;
    object.SetARGB((object.GetARGB()&0x00ffffff)|(DWORD(alpha)<<24));
}
}
void CGUIInventoryWindow::SetSprite(){
    IV455Bind(*this,6,0,0);m_uiAniTitleBar.SetImage455(IV455Sprite(1,4,0),4,0,true);
    IV455Button(m_uiCloseButton,1,0,0);IV455Button(m_uiHelpButton,1,0,3);
}
void CGUIInventoryWindow::Init(){
    SetSprite();RemoveAll();IV455String(m_uiTitle,0x47b);
    const unsigned race=BYTE(_GetAvatarRace())/2;
    m_uiDalantTitle.SetString(race<3?const_cast<char*>(IV455Text(10+race)):nullptr);
    IV455String(m_uiGoldTitle,0x3c7);
    m_uiAniTitleBar.SetPos(m_ptPos.x+(m_ptSize.x-m_uiAniTitleBar.GetSizeX())/2,m_ptPos.y+6);
    m_uiTitle.SetPos(m_uiAniTitleBar.GetPosX()+(m_uiAniTitleBar.GetSizeX()-m_uiTitle.GetSizeX())/2,m_uiAniTitleBar.GetPosY()+(m_uiAniTitleBar.GetSizeY()-m_uiTitle.GetSizeY())/2);
    m_uiCloseButton.SetPos(m_uiAniTitleBar.GetPosX()+m_uiAniTitleBar.GetSizeX()-m_uiCloseButton.GetSizeX()-4,m_uiAniTitleBar.GetPosY()+4);
    m_uiHelpButton.SetPos(m_uiAniTitleBar.GetPosX()+4,m_uiAniTitleBar.GetPosY()+4);
    m_uiDalantTitle.SetPos(m_ptPos.x+m_ptSize.x-m_uiDalantTitle.GetSizeX()-16,m_ptPos.y+318);
    m_uiGoldTitle.SetPos(m_ptPos.x+m_ptSize.x-m_uiGoldTitle.GetSizeX()-16,m_ptPos.y+335);
    m_uiPackOpenOption.SetPos(m_ptPos.x+15,m_ptPos.y+324);
    for(unsigned i=0;i<TOTAL_PACK;++i)m_uiPackButton[i].SetPos(m_ptPos.x+41*i+16,m_ptPos.y+354);
    Add(&m_uiAniTitleBar);Add(&m_uiTitle);
    m_uiCloseButton.AddMouseEventHandler(this);m_uiHelpButton.AddMouseEventHandler(this);Add(&m_uiCloseButton);Add(&m_uiHelpButton);
    Add(&m_uiDalantTitle);Add(&m_uiGoldTitle);Add(&m_uiDalant);Add(&m_uiGold);
    m_uiPackOpenOption.AddMouseEventHandler(this);Add(&m_uiPackOpenOption);
    for(auto& button:m_uiPackButton)Add(&button);
    m_uiTitle.GetFont()->dwColor=0xffc7bdb6;m_uiDalant.GetFont()->dwColor=0xffc7bdb6;m_uiGold.GetFont()->dwColor=0xffc7bdb6;
    m_uiDalantTitle.GetFont()->dwColor=0xffbaac9f;m_uiGoldTitle.GetFont()->dwColor=0xffbaac9f;
    SetARGB((GetARGB()&0x00ffffff)|0xd8000000);m_uiTitle.DisableFocus();SetMoveObject(&m_uiAniTitleBar);SetMovable(TRUE);EnableDocking(TRUE);
    SetOpenOnlyOnePack(m_bOpenOnlyOnePack);SoundOn(TRUE);SetName("Inventory");m_bIsCreated=TRUE;
}
void CGUIInventoryWindow::SetEquipWindow(CGUIEquipWindow* window){
    if(!window)throw std::logic_error("455 inventory requires its real equipment window");
    if(m_pEquipWindow)Remove(m_pEquipWindow);
    m_pEquipWindow=window;window->SetInventoryWin(this);window->SetPos(m_ptPos.x,m_uiAniTitleBar.GetPosY()+m_uiAniTitleBar.GetSizeY());Add(window);
}
void CGUIInventoryWindow::SetOpenOnlyOnePack(BOOL one){
    //455 stores the pressed descriptor without resolving it. Stock action2
    // has11frames (0..10):retain frame11,do not substitute another frame or
    // reject normal initialization because of an inactive pressed state.
    m_bOpenOnlyOnePack=one;auto* sprite=IV455Sprite(6,2,WORD(one?9:10));SPRITE_INFO normal={sprite,2,WORD(one?9:10)},pressed={sprite,2,11};
    m_uiPackOpenOption.SetSpriteInfoEx(&normal);m_uiPackOpenOption.SetSpriteInfoEx(PRESSED,&pressed);m_uiPackOpenOption.SetSize(sprite->GetSpriteOrgXL(2,normal.wFrameNo),sprite->GetSpriteOrgYL(2,normal.wFrameNo));
    if(one){unsigned opened=0;for(auto* pack:m_pPackWindow)if(pack&&pack->IsShow())++opened;if(opened>1)for(unsigned i=0;i<TOTAL_PACK;++i)if(m_pPackWindow[i]&&i!=m_byLastOpenedPack)m_pPackWindow[i]->Close();}
}
void CGUIInventoryWindow::SetPackState(BYTE index,BOOL open){
    if(index>=TOTAL_PACK)throw std::out_of_range("455 pack state index outside established owner domain");
    if(m_pPackWindow[index])m_uiPackButton[index].GetSpriteInfo()->wFrameNo=WORD(2*(BYTE(_GetAvatarRace())/2)+(open?2:1));
}
void CGUIInventoryWindow::SetOwnDalant(__int64 amount){
    m_dwOwnDalant=amount;m_uiDalant.SetString(RF455_GetMoneyText(amount));
    const LONG edge=m_uiDalantTitle.GetSizeX()>m_uiGoldTitle.GetSizeX()?m_uiDalantTitle.GetPosX():m_uiGoldTitle.GetPosX();
    m_uiDalant.SetPos(edge-10-m_uiDalant.GetSizeX(),m_uiDalantTitle.GetPosY());
}
void CGUIInventoryWindow::SetOwnGold(__int64 amount){
    m_dwOwnGold=amount;m_uiGold.SetString(RF455_GetMoneyText(amount));
    const LONG edge=m_uiDalantTitle.GetSizeX()>m_uiGoldTitle.GetSizeX()?m_uiDalantTitle.GetPosX():m_uiGoldTitle.GetPosX();
    m_uiGold.SetPos(edge-10-m_uiGold.GetSizeX(),m_uiGoldTitle.GetPosY());
}
void CGUIInventoryWindow::MouseEvent(_mouse_event& event){
    CGUIWindow::MouseEvent(event);if(m_pEquipWindow)m_pEquipWindow->MouseEvent(event);
    if(event.id==1||event.id==7){for(BYTE i=0;i<TOTAL_PACK;++i)if(event.source==&m_uiPackButton[i]){OpenPack(i,!IsOpenedPack(i));return;}if(event.source==&m_uiPackOpenOption)SetOpenOnlyOnePack(!m_bOpenOnlyOnePack);}
    else if(event.id==4){if(event.source==&m_uiCloseButton)Close();else if(event.source==&m_uiHelpButton)PostMessageA(CGUIScreen::GetSingletonPtr()->GetHWND(),0x1204,m_dwID,0);}
}
void CGUIInventoryWindow::PickingObjectEvent(BOOL pick){if(m_pEquipWindow)m_pEquipWindow->PickingObjectEvent(pick);}
void CGUIInventoryWindow::Open(){
    if(!m_pEquipWindow)throw std::logic_error("455 inventory Open requires its equipment owner");
    OpenDockingPack(TRUE);if(!m_pEquipWindow->IsShow())m_pEquipWindow->Open();CGUIWindow::Open();
}
void CGUIInventoryWindow::Close(){if(IsShow())OpenDockingPack(FALSE);CGUIWindow::Close();if(m_pEquipWindow)m_pEquipWindow->Close();_CloseAllDialogBox(this);}
void CGUIInventoryWindow::OpenDockingPack(BOOL open){
    for(auto* pack:m_pPackWindow)if(pack&&(pack->GetDockingBorder()!=CGUIWindow::NONE_BORDER||m_bOpenOnlyOnePack)){
        if(open){if(pack->m_bIsClosedWidhEquipWin)pack->Open();}
        else{pack->m_bIsClosedWidhEquipWin=pack->IsShow();pack->Close();}
    }
}
BOOL CGUIInventoryWindow::AddPack(BYTE index,BOOL){
    if(index>=TOTAL_PACK||m_pPackWindow[index])return FALSE;
    IV455Bind(m_uiPackButton[index],6,2,4);m_uiPackButton[index].AddMouseEventHandler(this);
    auto* pack=new CGUIInventoryBoard;m_pPackWindow[index]=pack;pack->Init(index);pack->SetInventoryWindow(this);SetPackState(index,FALSE);
    CGUIScreen::GetSingletonPtr()->Add(pack);AddDockingCustomer(pack);pack->EnableDockingBorder(CGUIWindow::BOTTOM,TRUE);pack->SetDockingBorder(CGUIWindow::BOTTOM);
    if(index==0){SetPackState(index,IsShow());pack->SetClosedWithEquipWin(TRUE);if(IsShow())pack->Open();}return TRUE;
}
void CGUIInventoryBoard::SetSprite(){
    IV455Bind(*this,6,0,3);for(unsigned i=0;i<TOTAL_INVENTORY;++i){IV455Bind(m_uiUselessItemMark[i],44,2,0);IV455Bind(m_uiUselessSocketMark[i],44,2,0);IV455Bind(m_uiTradeItemMark[i],44,0,0);}IV455Button(m_uiCloseButton,1,0,15);
}
void CGUIInventoryBoard::Init(BYTE index){
    m_byPackID=index;char label[16];const int length=std::snprintf(label,sizeof(label),IV455Text(0x483),unsigned(index)+1);
    if(length<0||length>=sizeof(label))throw std::logic_error("455 pack title exceeds target16byte domain");
    m_uiTitle.SetString(label);m_uiTitle.GetFont()->dwColor=0xffc3c1be;m_uiTitle.DisableFocus();RemoveAll();Add(&m_uiTitle);SetSprite();SetSize(228,176);
    for(BYTE i=0;i<TOTAL_INVENTORY;++i){m_uiItem[i].SetSize(32,32);m_uiItem[i].SetPos(39*(i%5)+19,36*(i/5)+26);m_uiUselessItemMark[i].SetPos(m_uiItem[i].GetPosX()-1,m_uiItem[i].GetPosY()-1);m_uiUselessItemMark[i].SetSize(34,34);m_uiUselessSocketMark[i].SetPos(m_uiUselessItemMark[i].m_ptPos);m_uiUselessSocketMark[i].SetSize(34,34);m_uiTradeItemMark[i].SetPos(m_uiUselessItemMark[i].m_ptPos);m_uiTradeItemMark[i].SetSize(34,34);Add(&m_uiItem[i]);Add(&m_uiUselessItemMark[i]);Add(&m_uiUselessSocketMark[i]);m_uiTradeItemMark[i].AddMouseEventHandler(this);Add(&m_uiTradeItemMark[i]);SetUselessItem(i,FALSE);SetUselessSocket(i,FALSE);}
    m_uiTitle.SetPos(m_ptPos.x+(m_ptSize.x-m_uiTitle.GetSizeX())/2,m_ptPos.y+(22-m_uiTitle.GetSizeY())/2);m_uiCloseButton.SetPos(m_ptPos.x+209,m_ptPos.y+3);m_uiCloseButton.AddMouseEventHandler(this);Add(&m_uiCloseButton);m_uiSelectedSocket.DisableFocus();Add(&m_uiSelectedSocket);SetMoveObject(this);SetMovable(TRUE);DisableFocus();SetARGB((GetARGB()&0x00ffffff)|0xd8000000);SetName("invenBoard");m_bCreated=TRUE;
}
void CGUIInventoryBoard::SetTradeItem(BYTE index,BOOL enabled){if(index<TOTAL_INVENTORY)m_uiTradeItemMark[index].GetSpriteInfo()->pSprite=enabled?IV455Sprite(44,0,0):nullptr;}
void CGUIInventoryBoard::SetUselessSocket(BYTE index,BOOL enabled){if(index<TOTAL_INVENTORY)IV455Overlay(m_uiUselessSocketMark[index],2,32,enabled,enabled?0x90:0xff);}
void CGUIInventoryBoard::SetUselessItem(BYTE index,BOOL enabled){if(index<TOTAL_INVENTORY)IV455Overlay(m_uiUselessItemMark[index],2,32,enabled,enabled?0x90:0xff);}
void CGUIEquipWindow::SetSprite(){
    for(unsigned i=0;i<15;++i)IV455Bind(m_uiEmptyEquipMark[i],6,1,WORD(i));
    for(unsigned i=13;i<16;++i)IV455Bind(m_uiEmptyEquipMark[i],6,1,WORD(i-1));
    for(unsigned i=0;i<TOTAL_EQUIP_ITEM;++i){const unsigned size=i<8?64:32;IV455Bind(m_uiUselessSocketMark[i],44,2,size==32?0:4);IV455Bind(m_uiTradeItemMark[i],44,0,size==32?0:4);}
}
void CGUIEquipWindow::Init(){
    SetSprite();SetSize(228,287);RemoveAll();const LONG pos[16][2]={{82,7},{82,77},{82,147},{12,77},{82,217},{152,147},{152,77},{12,147},{44,217},{152,217},{150,39},{185,39},{11,39},{46,39},{46,4},{150,4}};
    for(BYTE i=0;i<TOTAL_EQUIP_ITEM;++i){auto& item=m_uiEquipItem[i];item.SetSize(m_uiEmptyEquipMark[i].m_ptSize);item.SetPos(m_ptPos.x+pos[i][0],m_ptPos.y+pos[i][1]);m_uiEmptyEquipMark[i].SetPos(item.m_ptPos);m_uiTradeItemMark[i].SetSize(item.GetSizeX()+2,item.GetSizeY()+2);m_uiTradeItemMark[i].SetPos(item.GetPosX()-1,item.GetPosY()-1);m_uiUselessSocketMark[i].SetPos(item.GetPosX()-1,item.GetPosY()-1);Add(&m_uiEmptyEquipMark[i]);Add(&item);Add(&m_uiUselessSocketMark[i]);m_uiTradeItemMark[i].AddMouseEventHandler(this);Add(&m_uiTradeItemMark[i]);SetEmpty(i);SetUselessSocket(0,i,FALSE);}
    m_uiEquipAbleSocket.DisableFocus();m_uiEquipAbleSocketEx.DisableFocus();m_uiDisableEquipShield.DisableFocus();Add(&m_uiEquipAbleSocket);Add(&m_uiEquipAbleSocketEx);Add(&m_uiDisableEquipShield);m_bIsCreated=TRUE;
}
void CGUIEquipWindow::SetEmpty(BYTE index){if(index<TOTAL_EQUIP_ITEM){m_uiEquipItem[index].SetEmpty();m_uiEmptyEquipMark[index].GetSpriteInfo()->pSprite=IV455Sprite(6,1,m_uiEmptyEquipMark[index].GetSpriteInfo()->wFrameNo);m_uiEmptyEquipMark[index].SetARGB((m_uiEmptyEquipMark[index].GetARGB()&0x00ffffff)|0x70000000);SetTradeItem(0,index,FALSE);}}
void CGUIEquipWindow::SetTradeItem(BYTE,BYTE index,BOOL enabled){if(index<TOTAL_EQUIP_ITEM)m_uiTradeItemMark[index].GetSpriteInfo()->pSprite=enabled?IV455Sprite(44,0,index<8?4:0):nullptr;}
void CGUIEquipWindow::SetUselessSocket(BYTE,BYTE index,BOOL enabled){if(index<TOTAL_EQUIP_ITEM)IV455Overlay(m_uiUselessSocketMark[index],2,index<8?64:32,enabled,enabled?0x90:0xff);}
void CGUIEquipWindow::Open(){CGUIWindow::Open();if(m_pInventoryWin)m_pInventoryWin->Open();}
void CGUIEquipWindow::Close(){CGUIWindow::Close();}
// Both455vtables inherit65EA40:normal window draw always returns1 even hidden.
// The selected/ready objects already belong to the actual child list.
BOOL CGUIInventoryBoard::Draw(){return CGUIWindow::Draw();}
BOOL CGUIEquipWindow::Draw(){return CGUIWindow::Draw();}
