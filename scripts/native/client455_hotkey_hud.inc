namespace {
void BindHotkeySprite455(CGUIObject& object, CSprite* atlas, WORD action, WORD frame)
{
    if (!atlas || action >= atlas->GetMaxActions() || frame >= atlas->GetMaxFrames(action))
        throw std::runtime_error("455 bottom HUD sprite frame missing");
    SPRITE_INFO info = {atlas, action, frame};
    object.SetSpriteInfo(&info);
}
}

// 455 RVA 0x26bb10 assigns atlas 4 to the frame and existing controls.
void CGUIHotKeyBoard::SetSprite()
{
    auto* atlas = gSpriteMgr.GetTargetSprite455(4);
    BindHotkeySprite455(m_uiBoard, atlas, 11, 0);
    CGUIObject* const modes[] = {&m_uiActionHotkey, &m_uiMoveHotkey, &m_uiAttackHotkey};
    for (WORD i = 0; i < _countof(modes); ++i) {
        auto& control = *modes[i];
        const WORD frame = m_bIsCreated ? control.GetSpriteInfo()->wFrameNo : WORD(i * 2);
        BindHotkeySprite455(control, atlas, 12, frame);
    }
    BindHotkeySprite455(m_uiCharInfoKey, atlas, 13, 0);
    BindHotkeySprite455(m_uiInventoryKey, atlas, 13, 1);
    BindHotkeySprite455(m_uiSystemKey, atlas, 13, 2);

    // Preserve the current popup until its separate 455 layout is connected.
    auto* popupAtlas = gSpriteMgr.GetSprite(SP_ID_BELT);
    for (WORD i = 0; i < MAX_SUB_KEY_NUM; ++i) {
        SPRITE_INFO info = {popupAtlas, 2, WORD(9 + i)};
        m_uiCharInfoSubKey[i].SetSpriteInfo(&info);
    }
    if (m_pSFWin) m_pSFWin->SetSprite();
    if (m_pUnitCtrlBoard) m_pUnitCtrlBoard->SetSprite();
}

// 455 RVA 0x26bde0 scales below native width and centers the actual frame.
void CGUIHotKeyBoard::Init()
{
    SetSprite();
    auto* atlas = m_uiBoard.GetSpriteInfo()->pSprite;
    const LONG viewport = gScreen.GetSizeX();
    const LONG nativeWidth = atlas->GetSpriteOrgXL(11, 0);
    m_boardScale455 = static_cast<float>((std::min)(1.0, double(viewport) / nativeWidth));
    const double scale = m_boardScale455;
    const auto size = [&](CGUIObject& object) {
        const auto* info = object.GetSpriteInfo();
        object.SetSize(static_cast<LONG>(atlas->GetSpriteOrgXL(info->wActionNo, info->wFrameNo) * scale),
                       static_cast<LONG>(atlas->GetSpriteOrgYL(info->wActionNo, info->wFrameNo) * scale));
    };
    size(m_uiBoard);
    SetSize(viewport, m_uiBoard.GetSizeY());
    const LONG boardX = GetPosX() + (viewport - m_uiBoard.GetSizeX()) / 2;
    const LONG boardY = GetPosY();
    m_uiBoard.SetPos(boardX, boardY);
    m_uiBoard.SetSpriteU(0, 1.0f);
    m_uiBoard.SetSpriteV(0, 1.0f);
    Add(&m_uiBoard);

    m_uiAvatarCtrlBoard.SetSize(viewport, GetSizeY());
    m_uiAvatarCtrlBoard.SetPos(m_ptPos);
    const LONG buttonY = static_cast<LONG>(boardY + scale * 22.0 - 3.0);
    LONG buttonX = static_cast<LONG>(boardX + scale * 169.0);
    for (auto* control : {&m_uiActionHotkey, &m_uiMoveHotkey, &m_uiAttackHotkey}) {
        size(*control);
        control->SetPos(buttonX, buttonY);
        control->AddMouseEventHandler(this);
        m_uiAvatarCtrlBoard.Add(control);
        buttonX += control->GetSizeX() + 1;
    }
    buttonX = static_cast<LONG>(boardX + scale * 757.0);
    for (auto* control : {&m_uiCharInfoKey, &m_uiInventoryKey, &m_uiSystemKey}) {
        size(*control);
        control->SetPos(buttonX, buttonY);
        control->AddMouseEventHandler(this);
        Add(control);
        buttonX += control->GetSizeX() + 1;
    }
    m_uiSubkeyBoard.AddMouseEventHandler(this);
    ChangeActionMode(Peace);
    ChangeMoveMode(Walk);
    ChangeAttackMode(Manual);
    SetName("Hotkey");
    SetAvatarControlBoard();
    SetRaceType(0);
    m_bIsCreated = TRUE;
}

void CGUIHotKeyBoard::SetLinkWindow455(CGUILinkWindow455* link)
{
    if (m_pSFWin && m_pSFWin != link) Remove(m_pSFWin);
    m_pSFWin = link;
    if (!link) return;
    const double scale = m_boardScale455;
    link->SetPos(static_cast<LONG>(m_uiBoard.GetPosX() + scale * 272.0),
                 static_cast<LONG>(m_uiBoard.GetPosY() + m_uiBoard.GetSizeY() - scale * 13.0 - link->GetSizeY()));
    Add(link);
    gScreen.Remove(link);
}
