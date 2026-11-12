// The 455 radar initialization (RVA 0x317790) centers the two 93x93
// rotating layers in the marker board, inset from the frame's origin.
void CGUIRadarWindow::Init()
{
    SetSprite();
    const auto compassSize = m_uiCompassBase.m_ptSize;
    m_uiRadarBoard.SetSize(compassSize.x + 4, compassSize.y + 4);
    m_uiRadarBoard.SetPos(m_ptPos.x + 31, m_ptPos.y + 32);
    const auto boardOrigin = m_uiRadarBoard.m_ptPos;
    m_uiCompassBase.SetPos(boardOrigin.x + 2, boardOrigin.y + 2);
    m_uiAvatarObject.SetPos(boardOrigin.x + 2, boardOrigin.y + 2);

    Add(&m_uiCompassBase);
    Add(&m_uiAvatarObject);
    Add(&m_uiRadarBoard);

    m_uiCompassBase.SetARGB(0xc0ffffff);
    m_uiAvatarObject.SetARGB(0x88ffffff);
    SetMoveObject(this);
    SetMoveObject(&m_uiRadarBoard);
    SetMovable(TRUE);
    m_ptCharObjSize = {4, 4};
    m_bCreated = TRUE;
}

// The base, compass, and avatar layers use main.spr action 3 (RVA 0x317ec0).
void CGUIRadarWindow::SetSprite()
{
    constexpr WORD action = 3;
    auto* sprite = gSpriteMgr.GetTargetSprite455(4);
    if (!sprite || sprite->GetMaxActions() <= action || sprite->GetMaxFrames(action) < 3)
        throw std::runtime_error("455 radar sprite frames missing");

    CGUIObject* const layers[] = {this, &m_uiCompassBase, &m_uiAvatarObject};
    for (WORD frame = 0; frame < _countof(layers); ++frame) {
        SPRITE_INFO info = {sprite, action, frame};
        layers[frame]->SetSpriteInfo(&info);
        layers[frame]->SetSize(sprite->GetSpriteOrgXL(action, frame), sprite->GetSpriteOrgYL(action, frame));
    }
    m_uiCompassBase.SetSpriteU(0, 1.0f);
    m_uiCompassBase.SetSpriteV(0, 1.0f);
    m_uiAvatarObject.SetSpriteU(0, 1.0f);
    m_uiAvatarObject.SetSpriteV(0, 1.0f);

    if (m_bCreated) {
        for (auto* character : m_listChar) {
            auto* marker = character->uiCharObj.GetSpriteInfo();
            auto* direction = character->uiCharDir.GetSpriteInfo();
            if (marker->pSprite) marker->pSprite = sprite;
            if (direction->pSprite) direction->pSprite = sprite;
        }
    }
}
