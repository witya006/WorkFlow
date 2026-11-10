// Pinned455 b1b5febf... x86:661800/6629F0/6630C0/665F70/666580/666690/6669A0.
// Full paginated bodies and both-pin verification:charinfo161-reference/*.json.
#undef min
#undef max
namespace {
const char* CI455Text(unsigned index){return RF455_GetNormalLanguagePack()->get(index);}
void CI455String(CGUIText& text,unsigned index){text.SetString(const_cast<char*>(CI455Text(index)));}
CSprite* CI455Sprite(BYTE id,WORD action,WORD frame){
    auto* sprite=gSpriteMgr.GetTargetSprite455(id);
    if(!sprite||action>=sprite->GetMaxActions()||frame>=sprite->GetMaxFrames(action))throw std::runtime_error("455 CharInfo sprite/frame missing");
    return sprite;
}
void CI455Bind(CGUIObject& object,BYTE id,WORD action,WORD frame){
    auto* sprite=CI455Sprite(id,action,frame);SPRITE_INFO info={sprite,action,frame};object.SetSpriteInfo(&info);
    object.SetSize(sprite->GetSpriteOrgXL(action,frame),sprite->GetSpriteOrgYL(action,frame));
}
void CI455Center(CGUIObject& object,LONG x,LONG y,LONG width,LONG height){object.SetPos(x+(width-object.GetSizeX())/2,y+(height-object.GetSizeY())/2);}
void CI455Center(CGUIObject& object,CGUIObject& parent){CI455Center(object,parent.GetPosX(),parent.GetPosY(),parent.GetSizeX(),parent.GetSizeY());}
void CI455Button(CGUIButton& button,WORD frame){
    auto* sprite=CI455Sprite(1,0,WORD(frame+2));const WORD states[3]={0,HOVERED,PRESSED};
    SPRITE_INFO normal={sprite,0,frame};button.SetSpriteInfoEx(&normal);
    for(unsigned i=0;i<3;++i){SPRITE_INFO info={sprite,0,WORD(frame+i)};button.SetSpriteInfoEx(states[i],&info);}
    button.SetSize(sprite->GetSpriteOrgXL(0,frame),sprite->GetSpriteOrgYL(0,frame));
}
void CI455TabsSkin(CGUITabBoard455& page){RF455_ConfigureModalScrollbar(page.Scrollbar455());page.SetHeaderSprites455({1,5,0},{1,5,1});}
}
RF455CharInfoView::~RF455CharInfoView(){owner.SetWheelScrollObject(nullptr);owner.RemoveAll();}
RF455CharInfoView& CGUICharInfoWindow::View455(){if(!m_view455)m_view455.reset(new RF455CharInfoView(*this));return *m_view455;}
void RF455CharInfoView::SetMainSprite455(){
    CI455Bind(battleHeader,47,1,0);CI455Bind(makeHeader,47,1,0);
    for(auto& row:battle){CI455Bind(row.back,47,1,1);CI455Bind(row.bar,47,1,2);row.bar.SetSpriteU(0,1);row.bar.SetSpriteV(0,1);row.percent.Configure455(1,7,3,7,9);}
    for(auto& row:make){CI455Bind(row.back,47,1,1);CI455Bind(row.bar,47,1,2);row.bar.SetSpriteU(0,1);row.bar.SetSpriteV(0,1);row.percent.Configure455(1,7,3,7,9);}
    for(unsigned i=0;i<4;++i){CI455Bind(resistBack[i],47,2,0);CI455Bind(resistBar[i],47,2,WORD(i+1));resistBar[i].SetSpriteU(0,1);resistBar[i].SetSpriteV(0,1);}
    CI455TabsSkin(main);
}
void RF455CharInfoView::SetSprite455(){
    //665F70 configures a1x4 sheet only for the highlight at+1428.
    //7B5DC0 configures this header image only;its original height is retained.
    header.SetImage455(CI455Sprite(1,4,0),4,0);
    for(unsigned i=0;i<3;++i)CI455Bind(tabs[i],47,0,WORD(i));
    highlight.SetImage455(CI455Sprite(1,7,6),7,6);highlight.SetSheet455(1,4);highlight.SetFPS455(5);
    CI455Bind(owner.m_uiResizeUnderBar,1,4,2);CI455Button(owner.m_uiCloseButton,0);CI455Button(owner.m_uiHelpButton,3);
    if(ready){SetMainSprite455();CI455TabsSkin(actions);CI455TabsSkin(equipment);}
}
void RF455CharInfoView::InitPage455(CGUITabBoard455& page,BYTE count,const unsigned* labels){
    page.Init455(count,207,18,219,74);CI455TabsSkin(page);
    for(BYTE i=0;i<count;++i){page.SetTitle455(i,CI455Text(labels[i]),DWORD(-2434860));page.Content455(i)->AddMouseEventHandler(&page);}
    page.AddMouseEventHandler(&page);page.Scrollbar455().SetAdjustmentUnit(12);
}
void RF455CharInfoView::InitMain455(){
    main.Init455(5,207,18,219,74);SetMainSprite455();
    const unsigned sections[5]={0x43f,0x440,0x441,0x442,0xf74};
    const LONG h=RF455_DefaultTextHeight();const LONG heights[5]={9*(h+3)+8,14*(h+3)+8,214,110,8*h+32};
    for(BYTE i=0;i<5;++i){main.Content455(i)->SetSize(207,heights[i]);main.SetTitle455(i,CI455Text(sections[i]),DWORD(-2434860));}
    const unsigned labels[23]={0x443,0x444,0x445,0x446,0x447,0x448,0x109c,0x44a,0x44b,0x44c,0x44d,0x44e,0x7e9,0x44f,0x450,0x451,0x452,0x81c,0x81d,0x81e,0x453,0x454,0x455};
    for(unsigned i=0;i<23;++i){CI455String(titles[i],labels[i]);titles[i].GetFont()->dwColor=DWORD(-4408652);owner.m_uiInfoValues455[i].GetFont()->dwColor=DWORD(-3889263);}
    const unsigned nation=RF455_GetNormalNationPaths()->nation;const LONG pad=nation==5?5:10,gap=nation==5?4:5;const bool left=nation==6||nation==9||nation==10;
    for(unsigned group=0;group<2;++group){
        const unsigned first=group?9:0,end=group?23:9;auto& content=*main.Content455(BYTE(group));LONG maximum=0;
        for(unsigned i=first;i<end;++i)maximum=std::max(maximum,titles[i].GetSizeX());
        for(unsigned i=first;i<end;++i){
            auto& title=titles[i];const LONG x=left?main.Content455(1)->GetPosX()+2*pad:content.GetPosX()+maximum+pad-title.GetSizeX();
            title.SetPos(x,content.GetPosY()+LONG(i-first)*(title.GetSizeY()+3)+5);
            owner.m_uiInfoValues455[i].SetPos(title.GetPosX()+title.GetSizeX()+gap,title.GetPosY());content.Add(&title);content.Add(&owner.m_uiInfoValues455[i]);
        }
    }
    const unsigned resistLabels[4]={0x41,0x42,0x456,0x457};auto& resist=*main.Content455(3);
    for(unsigned i=0;i<4;++i){
        CI455String(resistNames[i],resistLabels[i]);resistNames[i].GetFont()->dwColor=DWORD(-3887958);owner.m_uiResistPoint[i].GetFont()->dwColor=DWORD(-3887958);
        resistBack[i].SetPos(resist.GetPosX()+3,resist.GetPosY()+LONG(i)*(resistBack[0].GetSizeY()+5)+10);
        CI455Center(resistNames[i],resistBack[i].GetPosX(),resistBack[i].GetPosY(),48,16);
        resistBar[i].SetPos(resistBack[i].GetPosX()+103,resistBack[i].GetPosY()+5);owner.m_uiResistPoint[i].SetPos(resistBack[i].GetPosX()+150,resistBack[i].GetPosY()+3);
        resist.Add(&resistBack[i]);resist.Add(&resistNames[i]);resist.Add(&resistBar[i]);resist.Add(&owner.m_uiResistPoint[i]);
    }
    CI455String(owner.m_uiBattleTitle,0x458);CI455String(owner.m_uiMakeTitle,0x45e);
    owner.m_uiBattleTitle.GetFont()->dwColor=DWORD(-3158065);owner.m_uiMakeTitle.GetFont()->dwColor=DWORD(-3158065);
    const unsigned battleLabels[6]={0x459,0x45a,0,0x45b,0x45c,0x45d};
    for(unsigned i=0;i<6;++i){if(i!=2)CI455String(owner.m_uiBattleName[i],battleLabels[i]);owner.m_uiBattleName[i].GetFont()->dwColor=DWORD(-4408652);owner.m_uiBattlePoint[i].GetFont()->dwColor=DWORD(-3889263);battle[i].percent.SetARGB(DWORD(-1513240));}
    for(unsigned i=0;i<3;++i){CI455String(owner.m_uiMakeName[i],0x45f+i);owner.m_uiMakeName[i].GetFont()->dwColor=DWORD(-4408652);owner.m_uiMakePoint[i].GetFont()->dwColor=DWORD(-3889263);make[i].percent.SetARGB(DWORD(-1513240));}
    const unsigned extras[7]={0xd38,0xd39,0xd3a,0,0x169f,0xf78,0xf8d};LONG maximum=0;
    for(unsigned i=0;i<7;++i){if(i!=3)CI455String(extraTitles[i],extras[i]);else extraTitles[i].SetString("");maximum=std::max(maximum,extraTitles[i].GetSizeX());}
    auto& extra=*main.Content455(4);
    for(unsigned i=0;i<7;++i){
        auto& title=extraTitles[i];title.GetFont()->dwColor=DWORD(-4408652);extraValues[i].GetFont()->dwColor=DWORD(-3889263);
        title.SetPos(extra.GetPosX()+maximum+pad-title.GetSizeX(),extra.GetPosY()+LONG(i)*(title.GetSizeY()+3)+5);
        extraValues[i].SetPos(title.GetPosX()+title.GetSizeX()+gap,title.GetPosY());extra.Add(&title);extra.Add(&extraValues[i]);
        if(i==1||i==2||i>=4)extraValues[i].SetString("0");
    }
    RefreshRace455(_GetAvatarRace());main.Scrollbar455().SetAdjustmentUnit(12);
    for(BYTE i=0;i<6;++i)SetBattle455(i,0,0);for(BYTE i=0;i<3;++i)SetMake455(i,0,0);
}
void RF455CharInfoView::RefreshRace455(BYTE race){
    if(race/2>=3)throw std::domain_error("455 CharInfo race outside verified domain");
    owner.m_byRaceType=race;owner.SetInfoText455(1,const_cast<char*>(CI455Text(6+race/2)));owner.SetInfoText455(2,const_cast<char*>(CI455Text(15+(race&1))));CI455String(owner.m_uiBattleName[2],0x4c5+race/2);
    auto* content=main.Content455(2);if(!content)return;
    // Initial composition matches455. Rebuilding explicitly detaches borrowed
    // children;repeated cross-race changes are a separate target-lifecycle gap.
    content->RemoveAll();battleHeader.SetPos(content->GetPosX()+3,content->GetPosY()+3);CI455Center(owner.m_uiBattleTitle,battleHeader);content->Add(&battleHeader);content->Add(&owner.m_uiBattleTitle);
    unsigned visible=0,last=0;
    for(unsigned i=0;i<6;++i){
        if(i==3&&race/2==2)continue;auto& row=battle[i];row.back.SetPos(battleHeader.GetPosX(),battleHeader.GetPosY()+battleHeader.GetSizeY()+LONG(visible)*(battle[0].back.GetSizeY()+3)+3);
        CI455Center(owner.m_uiBattleName[i],row.back.GetPosX(),row.back.GetPosY(),67,16);owner.m_uiBattlePoint[i].SetPos(row.back.GetPosX()+144,row.back.GetPosY()+3);
        row.bar.SetPos(row.back.GetPosX()+67,row.back.GetPosY()+3);row.percent.SetPos(row.back.GetPosX()+80,row.back.GetPosY()+4);
        content->Add(&row.back);content->Add(&owner.m_uiBattleName[i]);content->Add(&owner.m_uiBattlePoint[i]);content->Add(&row.bar);content->Add(&row.percent);++visible;last=i;
    }
    makeHeader.SetPos(content->GetPosX()+3,battle[last].back.GetPosY()+battle[last].back.GetSizeY()+7);CI455Center(owner.m_uiMakeTitle,makeHeader);content->Add(&makeHeader);content->Add(&owner.m_uiMakeTitle);
    for(unsigned i=0;i<3;++i){auto& row=make[i];row.back.SetPos(makeHeader.GetPosX(),makeHeader.GetPosY()+makeHeader.GetSizeY()+LONG(i)*(make[0].back.GetSizeY()+3)+3);
        CI455Center(owner.m_uiMakeName[i],row.back.GetPosX(),row.back.GetPosY(),67,16);owner.m_uiMakePoint[i].SetPos(row.back.GetPosX()+144,row.back.GetPosY()+3);row.bar.SetPos(row.back.GetPosX()+67,row.back.GetPosY()+3);row.percent.SetPos(row.back.GetPosX()+80,row.back.GetPosY()+4);
        content->Add(&row.back);content->Add(&owner.m_uiMakeName[i]);content->Add(&owner.m_uiMakePoint[i]);content->Add(&row.bar);content->Add(&row.percent);
    }
    content->SetSize(content->GetSizeX(),make[2].back.GetPosY()+make[2].back.GetSizeY()-battleHeader.GetPosY()+10);
}
void RF455CharInfoView::Init455(){
    if(ready)return;SetSprite455();owner.SetSize(228,119);background.SetSize(owner.m_ptSize);background.SetPos(owner.m_ptPos);CI455String(owner.m_uiTitle,0x465);
    header.SetPos(owner.GetPosX()+(owner.GetSizeX()-header.GetSizeX())/2,owner.GetPosY()+6);CI455Center(owner.m_uiTitle,header);
    owner.m_uiCloseButton.SetPos(header.GetPosX()+header.GetSizeX()-owner.m_uiCloseButton.GetSizeX()-4,header.GetPosY()+4);owner.m_uiHelpButton.SetPos(header.GetPosX()+4,header.GetPosY()+4);
    const LONG xs[3]={54,140,98};for(unsigned i=0;i<3;++i)tabs[i].SetPos(owner.GetPosX()+xs[i],header.GetPosY()+header.GetSizeY()+8);
    owner.Add(&background);owner.Add(&header);owner.Add(&owner.m_uiTitle);owner.m_uiCloseButton.AddMouseEventHandler(&owner);owner.m_uiHelpButton.AddMouseEventHandler(&owner);owner.Add(&owner.m_uiCloseButton);owner.Add(&owner.m_uiHelpButton);
    for(auto& tab:tabs){tab.AddMouseEventHandler(&owner);owner.Add(&tab);}owner.m_uiResizeUnderBar.AddMouseEventHandler(&owner);owner.Add(&owner.m_uiResizeUnderBar);
    InitMain455();const unsigned actionNames[2]={0x463,0x464},equipmentNames[4]={0xe3f,0xe40,0xe41,0xe42};InitPage455(actions,2,actionNames);InitPage455(equipment,4,equipmentNames);
    background.SetOutline455(3,1,DWORD(-9802126));background.SetARGB((DWORD(-14539224)&0xffffff)|0xd8000000);owner.m_uiTitle.GetFont()->dwColor=DWORD(-3686986);
    owner.SetMoveObject(&owner.m_uiTitle);owner.SetMoveObject(&header);owner.SetMovable(TRUE);owner.SetReSizeObject(CGUIWindow::BOTTOM,&owner.m_uiResizeUnderBar);owner.SetReSizable(TRUE);
    RECT bounds;owner.GetBound(bounds);bounds.bottom=bounds.top+395;SetBound455(bounds);
    const unsigned tabNames[3]={0x466,0x467,0xe51};for(unsigned i=0;i<3;++i)tabs[i].SetName(const_cast<char*>(CI455Text(tabNames[i])));
    SelectPage455(0);main.SetOpened455(0,TRUE);main.SetOpened455(1,TRUE);actions.SetOpened455(0,TRUE);actions.SetOpened455(1,TRUE);equipment.SetOpened455(0,TRUE);
    owner.SetName("CharInfoWin");ready=true;owner.m_bCreated=TRUE;
}
void RF455CharInfoView::SetBound455(RECT& bounds){
    if(bounds.bottom-bounds.top<header.GetSizeY()+owner.m_uiResizeUnderBar.GetSizeY()+137)return;
    owner.CGUIObject::SetBound(bounds);background.SetBound(bounds);owner.m_uiResizeUnderBar.SetPos(owner.GetPosX()+(owner.GetSizeX()-owner.m_uiResizeUnderBar.GetSizeX())/2,owner.GetPosY()+owner.GetSizeY()-owner.m_uiResizeUnderBar.GetSizeY()-6);
    RECT pageBounds={owner.GetPosX()+5,tabs[0].GetPosY()+tabs[0].GetSizeY()+8,owner.GetPosX()+5+main.GetSizeX(),owner.m_uiResizeUnderBar.GetPosY()-1};
    for(BYTE i=0;i<3;++i)if(Page455(i)->Count455())Page455(i)->SetBound(pageBounds);
}
void RF455CharInfoView::SelectPage455(BYTE index){
    auto* page=Page455(index);if(!page||owner.IsAddedObject(page))return;
    for(BYTE i=0;i<3;++i)if(i!=index)owner.Remove(Page455(i));page->SetPos(owner.GetPosX()+5,tabs[0].GetPosY()+tabs[0].GetSizeY()+8);owner.Add(page);owner.SetWheelScrollObject(&page->Scrollbar455());
    highlight.SetPos(tabs[index].m_ptPos);highlight.SetMouseInput455(FALSE);owner.Add(&highlight);selected=index;
}
void RF455CharInfoView::SetBattle455(BYTE index,WORD current,WORD maximum){
    if(index>=6)return;owner.m_byBattlePoint[index]=BYTE(current);battleMaximum[index]=maximum;char text[32];const bool gm=current>=99&&maximum==99;
    if(gm)std::strcpy(text,"G M");else std::snprintf(text,sizeof(text),"%2u/%2u Pt",unsigned(current),unsigned(maximum));auto& point=owner.m_uiBattlePoint[index];point.SetString(text);point.SetPos(battle[index].back.GetPosX()+(gm?159:143),point.GetPosY());
}
void RF455CharInfoView::SetMake455(BYTE index,WORD current,WORD maximum){
    if(index>=3)return;makeMaximum[index]=maximum;char text[32];const bool gm=current>=99&&maximum!=99;
    if(gm)std::strcpy(text,"G M");else std::snprintf(text,sizeof(text),"%2u/%2u Pt",unsigned(current),unsigned(maximum));auto& point=owner.m_uiMakePoint[index];point.SetString(text);point.SetPos(make[index].back.GetPosX()+(gm?159:143),point.GetPosY());if(gm)make[index].percent.SetString455(nullptr);
}
namespace {
void CI455Crop(CGUIObjectEx& bar,float amount){
    auto* info=bar.GetSpriteInfo();auto* sprite=info->pSprite;
    if(!sprite)throw std::logic_error("455 CharInfo crop before skin initialization");
    bar.SetSpriteU(0,amount);bar.SetSpriteV(0,1);
    bar.SetSize(LONG(double(sprite->GetSpriteOrgXL(info->wActionNo,info->wFrameNo))*double(amount)),sprite->GetSpriteOrgYL(info->wActionNo,info->wFrameNo));
}
void CI455MasteryExp(RF455CharInfoView::MasteryRow& row,float value){
    if(!std::isfinite(value))throw std::domain_error("455 nonfinite mastery outside verified domain");
    value=std::max(0.0f,std::min(1.0f,value));float percent=value*100.0f;if(percent>99.98999786376953f)percent=99.98999786376953f;
    char text[32];std::snprintf(text,sizeof(text),percent>=10?"%.2f%%":" %.2f%%",double(percent));row.percent.SetString455(text);CI455Crop(row.bar,value);
}
}
void RF455CharInfoView::SetBattleExp455(BYTE index,float value){if(index<6)CI455MasteryExp(battle[index],value);}
void RF455CharInfoView::SetMakeExp455(BYTE index,float value){if(index<3)CI455MasteryExp(make[index],value);}
void RF455CharInfoView::SetResistText455(BYTE index,int current){
    if(index>=4)return;char text[32];std::snprintf(text,sizeof(text),current>0?"+%d":"%d",current);auto& value=owner.m_uiResistPoint[index];value.SetString(text);
    value.SetPos(resistBack[index].GetPosX()+resistBack[index].GetSizeX()-value.GetSizeX()-10,value.GetPosY());
}
void RF455CharInfoView::SetResist455(BYTE index,int current,int minimum,int maximum){
    if(index>=4)return;const long long difference=static_cast<long long>(maximum)-minimum;
    if(difference<INT_MIN||difference>INT_MAX||difference/2==0)throw std::domain_error("455 resistance zero/overflow range outside verified domain");
    const float ratio=static_cast<float>(double(current)/double(int(difference)/2));const float magnitude=std::min(1.0f,std::fabs(ratio));CI455Crop(resistBar[index],magnitude);
    resistBar[index].SetPos(resistBack[index].GetPosX()+100-(current<=0?resistBar[index].GetSizeX():0),resistBack[index].GetPosY()+4);SetResistText455(index,current);
}
void CGUICharInfoWindow::Init(){View455().Init455();}
void CGUICharInfoWindow::SetSprite(){View455().SetSprite455();}
void CGUICharInfoWindow::SetBound(RECT& bounds){View455().SetBound455(bounds);}
void CGUICharInfoWindow::SetTab(BYTE index,BOOL opened){View455().main.SetOpened455(index,opened);}
BOOL CGUICharInfoWindow::IsOpenedTab(BYTE index){return View455().main.IsOpened455(index);}
void CGUICharInfoWindow::ScrollEvent(_scroll_event& event){auto* page=View455().Page455(View455().selected);if(page)page->ScrollEvent(event);}
void CGUICharInfoWindow::SetRaceType(BYTE race){m_byRaceType=race;if(m_view455&&m_view455->Ready455())m_view455->RefreshRace455(race);}
void CGUICharInfoWindow::SetBattleMastery455(BYTE index,WORD current,WORD maximum){View455().SetBattle455(index,current,maximum);}
void CGUICharInfoWindow::SetMakeMastery455(BYTE index,WORD current,WORD maximum){View455().SetMake455(index,current,maximum);}
// Legacy callers supply only current mastery. Retaining a known maximum does
// not reconstruct the missing455 maximum producer;this remains an explicit gap.
void CGUICharInfoWindow::SetBattleMastery(BYTE index,WORD current){if(index<6)View455().SetBattle455(index,current,View455().battleMaximum[index]);}
void CGUICharInfoWindow::SetMakeMastery(BYTE index,WORD current){if(index<3)View455().SetMake455(index,current,View455().makeMaximum[index]);}
void CGUICharInfoWindow::SetBattleMasteryExp(BYTE index,float value){View455().SetBattleExp455(index,value);}
void CGUICharInfoWindow::SetMakeMasteryExp(BYTE index,float value){View455().SetMakeExp455(index,value);}
void CGUICharInfoWindow::SetResistPoint455(BYTE index,int value,int minimum,int maximum){View455().SetResist455(index,value,minimum,maximum);}
// This old caller has no455 resistance bounds;only its known text is updated.
// The signed/range-aware455 producer is not replaced by invented limits.
void CGUICharInfoWindow::SetResistPoint(BYTE index,WORD value){View455().SetResistText455(index,value);}
void CGUICharInfoWindow::SetFP(DWORD current,DWORD maximum){char text[32];if(maximum)std::snprintf(text,sizeof(text),"%d / %d",RF455_CharInfoSignedWord(current),RF455_CharInfoSignedWord(maximum));else std::strcpy(text,"-");SetInfoText455(10,text);}
void CGUICharInfoWindow::SetSP(DWORD current,DWORD maximum){char text[32];if(maximum)std::snprintf(text,sizeof(text),"%d / %d",RF455_CharInfoSignedWord(current),RF455_CharInfoSignedWord(maximum));else std::strcpy(text,"-");SetInfoText455(11,text);}
void CGUICharInfoWindow::SetExp(float value){char text[64];std::snprintf(text,sizeof(text),"%.6f%%",double(value));SetInfoText455(13,text);}
void CGUICharInfoWindow::MouseEvent(_mouse_event& event){
    CGUIWindow::MouseEvent(event);auto& view=View455();
    if(event.id==MOUSE_STROKED){for(BYTE i=0;i<3;++i)if(event.source==&view.tabs[i]){view.SelectPage455(i);return;}}
    else if(event.id==MOUSE_CLICKED){if(event.source==&m_uiCloseButton)Close();else if(event.source==&m_uiHelpButton)PostMessage(gScreen.GetHWND(),WM_OPEN_WINDOW_HELP,m_dwID,0);}
    // Tab hover/tooltips and action/equipment interaction callbacks are open.
}
