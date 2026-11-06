CGUIInventoryWindow::SetOwnGold(__int64 pi_dwGold){
    m_dwOwnGold=pi_dwGold;m_uiGold.SetString(RF455_GetMoneyText(pi_dwGold));
    const LONG titleX=m_uiDalantTitle.GetSizeX()<=m_uiGoldTitle.GetSizeX()?m_uiGoldTitle.GetPosX():m_uiDalantTitle.GetPosX();
    m_uiGold.SetPos(titleX-10-m_uiGold.GetSizeX(),m_uiGoldTitle.GetPosY());
}
