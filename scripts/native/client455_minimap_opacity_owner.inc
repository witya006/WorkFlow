void CGUIMiniMapWindow::SetSprite(){
    //An owned resource bridges the0.7 sprite-ID collision until all GUI IDs port.
    //The image is the pinned455 main resource,not a legacy minimap replacement.
    if(!m_frameSkin455.GetMaxActions()&&GetD3dDevice()){
        char path[260];if(RF455_SelectSpritePath(4,path,sizeof(path))&&_access(path,0)==0)m_frameSkin455.LoadSprite(path);
    }
    CSprite* main=m_frameSkin455.GetMaxActions()?&m_frameSkin455:nullptr;
    auto assign=[&](CGUIObject& object,WORD frame){
        SPRITE_INFO image={main,5,frame};object.SetSpriteInfo(&image);
        if(main&&main->GetMaxActions()>5&&frame<main->GetMaxFrames(5))object.SetSize(main->GetSpriteOrgXL(5,frame),main->GetSpriteOrgYL(5,frame));
    };
    assign(m_uiTitleBoard,0);assign(m_uiAvatarObject,1);assign(m_mapBackground455,32);
    auto* terrain = gSpriteMgr.GetSprite(SP_ID_MINIMAP);
    if (terrain && terrain->GetMaxActions() && terrain->GetMaxFrames(0)) {
        SPRITE_INFO image{terrain, 0, 0};
        m_mapTerrain455.SetSpriteInfo(&image);
        m_mapTerrain455.SetARGB((static_cast<DWORD>(m_alpha455) << 24) | 0xffffff);
    } else {
        m_mapTerrain455.SetSpriteInfo(nullptr);
        m_mapTerrain455.SetARGB(0xffffffff);
    }
    RF455_ConfigureModalButton(m_uiCloseButton,true);
    RF455_ConfigureOpacityScrollbar(&m_opacityScrollbar455,gSpriteMgr.GetSprite(SP_ID_COMMON),0);
}
void CGUIMiniMapWindow::InitOpacity455(){
    m_uiCloseButton.SetPos(m_uiTitleBoard.GetPosX()+m_uiTitleBoard.GetSizeX()-m_uiCloseButton.GetSizeX()-2,m_uiTitleBoard.GetPosY()+2);
    m_uiMiniMap.SetPos(m_ptPos.x+1,m_ptPos.y+m_uiTitleBoard.GetSizeY());
    m_mapBackground455.SetPos(m_uiMiniMap.GetPosX(),m_uiMiniMap.GetPosY());
    m_mapBackground455.SetSize(400,400);m_mapBackground455.DisableFocus();
    m_uiMiniMap.Add(&m_mapBackground455);
    m_mapTerrain455.SetPos(m_uiMiniMap.m_ptPos);
    m_mapTerrain455.SetSize(m_uiMiniMap.m_ptSize);
    m_mapTerrain455.SetMouseInput455(FALSE);
    m_uiMiniMap.Add(&m_mapTerrain455);
    SetAlpha455(255);
    RF455_AlignGuiObject(m_opacityScrollbar455,m_uiTitleBoard.m_ptPos,m_uiTitleBoard.m_ptSize,-1,-1);
    m_opacityScrollbar455.SetPos(m_opacityScrollbar455.GetPosX(),m_opacityScrollbar455.GetPosY()+15);
    m_opacityScrollbar455.SetAmount(80,80);m_opacityScrollbar455.AddScrollHandler(this);
    Add(&m_opacityScrollbar455);
}
void CGUIMiniMapWindow::SetAlpha455(BYTE alpha){
    auto apply=[alpha](CGUIObject& object){object.SetARGB((object.GetARGB()&0xffffff)|(static_cast<DWORD>(alpha)<<24));};
    //Mapped existing455 groups;additional455 controls are tracked separately.
    apply(m_uiMiniMap);apply(m_uiTitleBoard);apply(m_uiTitle);apply(m_uiCloseButton);
    if (m_mapTerrain455.GetSpriteInfo()->pSprite) apply(m_mapTerrain455);
    apply(m_uiAvatarObject);apply(m_uiAvatarPosition);
    for(auto* object:m_listMiniMapObject)apply(object->uiObject);
    for(auto* object:m_listTooltipList)apply(object->uiObject);
    m_mapBackground455.SetARGB((m_mapBackground455.GetARGB()&0xffffff)|(static_cast<DWORD>(RF455_MinimapBackgroundAlpha(alpha))<<24));
    m_opacityScrollbar455.SetAlpha455(alpha);m_alpha455=alpha;m_zoomEligible455=alpha==100;
}
bool CGUIMiniMapWindow::IsCurrentMapBound455(BYTE map)
{
    return map != 0xff && m_byMapIndex == map && m_byMiniMapIndex == map &&
        m_mapTerrain455.GetSpriteInfo()->pSprite &&
        m_mapTerrain455.GetSpriteInfo()->pSprite == gSpriteMgr.GetSprite(SP_ID_MINIMAP);
}
BOOL CGUIMiniMapWindow::TakeCameraZoomGate455(){
    if(!m_suppressZoom455)return m_zoomEligible455;
    if(m_clearZoomSuppression455){m_suppressZoom455=FALSE;m_clearZoomSuppression455=FALSE;}
    return FALSE;
}
void CGUIMiniMapWindow::ScrollEvent(_scroll_event& event){
    if(event.source==&m_opacityScrollbar455)SetAlpha455(RF455_MinimapAlphaForAmount(m_opacityScrollbar455.GetCurrentAmount()));
    if(TakeCameraZoomGate455())throw std::domain_error("455minimap camera zoom requires restored Avatar/world consumer555940");
}
BOOL CGUIMiniMapWindow::Draw(){
    if(!CGUIContainer::Draw())return FALSE;
    DrawDialogBox();return TRUE;
}
