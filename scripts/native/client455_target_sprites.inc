namespace {
constexpr unsigned systemSprite = 5;
constexpr unsigned optionsBackground = 20;

CSprite* LoadTargetSprite455(unsigned id, const char* path)
{
    if (_access(path, 0) != 0) return nullptr;
    auto* sprite = new CSprite;
    sprite->LoadSprite(const_cast<char*>(path));
    if (sprite->GetMaxActions() && (id != systemSprite || sprite->GetMaxFrames(0) > optionsBackground))
        return sprite;
    sprite->ReleaseSprite();
    delete sprite;
    return nullptr;
}
}

// Separate target-ID registry while old callers still use their 0.7 group IDs.
CSprite* CSpriteMgr::GetTargetSprite455(unsigned id)
{
    if (id >= 55) return nullptr;
    auto*& cached = m_targetSprites455[id];
    if (cached) return cached;

    char path[260];
    if (!RF455_SelectSpritePath(id, path, sizeof(path))) return nullptr;
    cached = LoadTargetSprite455(id, path);
    if (cached || id != systemSprite) return cached;

    // Both shipped regional copies of this atlas are identical and contain the
    // options background. The Common copy in mixed installations can predate it.
    const char* fallbacks[] = {"./SpriteImage/Common/system.spr",
                               "./SpriteImage/zh-tw/system.spr", "./SpriteImage/ko-kr/system.spr"};
    for (const char* fallback : fallbacks) {
        if (std::strcmp(path, fallback) == 0) continue;
        cached = LoadTargetSprite455(id, fallback);
        if (cached) {
            OutputDebugStringA("RF455 Sprite:system-compatible-fallback");
            break;
        }
    }
    return cached;
}
void CSpriteMgr::UnloadTargetSprites455(){
    for(auto*& sprite:m_targetSprites455)if(sprite){sprite->ReleaseSprite();delete sprite;sprite=nullptr;}
}
