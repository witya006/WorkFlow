CGUIInventoryWindow::SetOwnDalant(__int64 pi_dwDalant){
    m_dwOwnDalant=pi_dwDalant;m_uiDalant.SetString(RF455_GetMoneyText(pi_dwDalant));
    const LONG titleX=m_uiDalantTitle.GetSizeX()<=m_uiGoldTitle.GetSizeX()?m_uiGoldTitle.GetPosX():m_uiDalantTitle.GetPosX();
    m_uiDalant.SetPos(titleX-10-m_uiDalant.GetSizeX(),m_uiDalantTitle.GetPosY());
}
