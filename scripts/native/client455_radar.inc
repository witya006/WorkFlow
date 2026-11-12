// The 455 radar initialization (RVA 0x317790) centers the two 93x93
// rotating layers in the marker board, inset from the frame's origin.
void CGUIRadarWindow::Init()
{
    SetSprite();
    const auto compassSize = m_uiCompassBase.m_ptSize;
    m_uiRadarBoard.SetSize(compassSize.x + 4, compassSize.y + 4);
    SetMapSize({680, 680});
    SetCameraRotate(0.0f);
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
    m_ptCharObjSize = {3, 3};
    m_bCreated = TRUE;
}

// The base, compass, and avatar layers use main.spr action 3 (RVA 0x317ec0).
void CGUIRadarWindow::SetSprite()
{
    constexpr WORD action = 3;
    auto* sprite = gSpriteMgr.GetTargetSprite455(4);
    if (!sprite || sprite->GetMaxActions() <= action || sprite->GetMaxFrames(action) < 5)
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
        for (auto* character : m_listChar)
            SetSprite_CharDir(static_cast<CharType>(character->byType), &character->uiCharDir);
    }
}

void CGUIRadarWindow::SetSprite_CharObj(CharType type, CGUIObject* marker)
{
    constexpr DWORD colors[] = {
        0xff41bb4a, 0xff99bcff, 0xff7daad7, 0xff869742, 0xffbed65e,
        0xfff090b0, 0xffa0a0e0, 0xffc0c0c0, 0xffe8e8e8, 0xffe8e8e8, 0xffe8e8e8,
        0xffffd65e, 0xffe680ff, 0xffa841ff, 0xffffffff,
    };
    static_assert(_countof(colors) == TOTAL_CHAR_TYPE_NUM, "Radar colors match character types");
    const auto index = static_cast<unsigned>(type);
    marker->SetARGB(colors[index < _countof(colors) ? index : 0]);
}

void CGUIRadarWindow::SetSprite_CharDir(CharType type, CGUIObjectEx* direction)
{
    if (type != PartyLeader && type != PartyMember) {
        direction->SetSpriteInfo(nullptr);
        Remove(direction);
        return;
    }
    const WORD frame = type == PartyLeader ? 3 : 4;
    SPRITE_INFO info{m_uiCompassBase.GetSpriteInfo()->pSprite, 3, frame};
    direction->SetSpriteInfo(&info);
    direction->SetSize(m_uiCompassBase.m_ptSize);
    direction->SetSpriteU(0, 1.0f);
    direction->SetSpriteV(0, 1.0f);
}

void CGUIRadarWindow::UpdateCharPosition(RADAR_CHAR_INFO* character)
{
    auto& marker = character->uiCharObj;
    auto& compass = m_uiAvatarObject;
    const float x = (character->vecCharPos[0] - m_vecAvatarPos[0]) * m_fPixelPerMeter[0];
    const float y = (m_vecAvatarPos[2] - character->vecCharPos[2]) * m_fPixelPerMeter[1];
    marker.SetPos(
        LONG(compass.GetPosX() + (compass.GetSizeX() - marker.GetSizeX()) / 2 +
             m_fRotateCosTheta * x - m_fRotateSinTheta * y),
        LONG(compass.GetPosY() + (compass.GetSizeY() - marker.GetSizeY()) / 2 +
             m_fRotateSinTheta * x + m_fRotateCosTheta * y));
    SetViewedCharInRadarBoard(character);
}

void CGUIRadarWindow::SetViewedCharInRadarBoard(RADAR_CHAR_INFO* character)
{
    auto& marker = character->uiCharObj;
    auto& direction = character->uiCharDir;
    const LONG centerX = m_uiRadarBoard.GetPosX() + m_uiRadarBoard.GetSizeX() / 2;
    const LONG centerY = m_uiRadarBoard.GetPosY() + m_uiRadarBoard.GetSizeY() / 2;
    const double dx = double(marker.GetPosX()) + marker.GetSizeX() / 2 - centerX;
    const double dy = double(marker.GetPosY()) + marker.GetSizeY() / 2 - centerY;
    constexpr int radius = 46;
    if (std::abs(m_vecAvatarPos[1] - character->vecCharPos[1]) <= m_fYAxisViewRange &&
        dx * dx + dy * dy <= radius * radius) {
        m_uiRadarBoard.Add(&marker);
        Remove(&direction);
        return;
    }

    m_uiRadarBoard.Remove(&marker);
    if (character->bDrawCharDir && direction.GetSpriteInfo()->pSprite && (dx != 0 || dy != 0)) {
        direction.SetPos(centerX - direction.GetSizeX() / 2, centerY - direction.GetSizeY() / 2);
        direction.SetRotate(float(std::atan2(dx, -dy) * (180.0 / 3.141592653589793)));
        Add(&direction);
    } else {
        Remove(&direction);
    }
}
