namespace {
constexpr WORD BadgeAction = 7;
constexpr WORD BadgeFrames[] = {31, 21, 22, 23, 24};

bool HasLoadingFrame(CSprite* sprite, WORD action, WORD frame)
{
    return sprite && action < sprite->GetMaxActions() && frame < sprite->GetMaxFrames(action);
}
}

void CGUILoadingWindow::Init()
{
    SetPos(0, 0);
    SetSize(gScreen.GetSizeX(), gScreen.GetSizeY());
    m_cLoading.SetPos(0, 0);
    m_cLoading.SetSize(GetSizeX(), GetSizeY());
    m_cLoading.SetMouseInput455(FALSE);
    Add(&m_cLoading);
    for (auto& badge : m_loadingBadges455) Remove(&badge);
    m_loadingFrame455 = 0;
    SetSprite();
}

void CGUILoadingWindow::SetSprite()
{
    if (!SelectLoadingFrame455(m_loadingFrame455)) m_cLoading.SetSpriteInfo(nullptr);
}

bool CGUILoadingWindow::SelectLoadingFrame455(WORD frame)
{
    auto* sprite = gSpriteMgr.GetSprite(SP_ID_LOADING);
    if (!HasLoadingFrame(sprite, 0, frame)) return false;
    SPRITE_INFO image{sprite, 0, frame};
    m_cLoading.SetSpriteInfo(&image);
    m_loadingFrame455 = frame;
    return true;
}

void CGUILoadingWindow::PrepareLoading455(bool korean, bool premium, BYTE ageKind)
{
    m_loadingFrame455 = 0;
    SetSprite();
    auto* atlas = gSpriteMgr.GetSprite(SP_ID_COMMON);
    const bool visible[] = {korean, korean, premium, korean, korean && ageKind != 3};
    constexpr LONG spacing = 13;
    LONG x = GetSizeX();
    for (unsigned i = 0; i < sizeof(BadgeFrames) / sizeof(BadgeFrames[0]); ++i) {
        auto& badge = m_loadingBadges455[i];
        Remove(&badge);
        const WORD frame = BadgeFrames[i];
        if (!visible[i] || !HasLoadingFrame(atlas, BadgeAction, frame)) continue;
        LONG width = atlas->GetSpriteOrgXL(BadgeAction, frame);
        LONG height = atlas->GetSpriteOrgYL(BadgeAction, frame);
        if (korean) {
            width = static_cast<LONG>(width * (GetSizeX() / 1600.0f));
            height = static_cast<LONG>(height * (GetSizeY() / 1200.0f));
        }
        if (width <= 0 || height <= 0) continue;
        SPRITE_INFO image{atlas, BadgeAction, frame};
        badge.SetSpriteInfo(&image);
        badge.SetSize(width, height);
        badge.SetMouseInput455(FALSE);
        Add(&badge);
        x -= width + spacing;
    }
    for (auto& badge : m_loadingBadges455) {
        if (!IsAddedObject(&badge)) continue;
        badge.SetPos(x, 17);
        x += badge.GetSizeX() + spacing;
    }
}
