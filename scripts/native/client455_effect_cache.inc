static void ReleaseMagicControl455(CProcessMagic& script) noexcept
{
    auto* node = script.m_control455.first;
    while (node) {
        auto* next = node->next;
        delete node;
        node = next;
    }
    script.m_control455 = {};
}

struct MagicCandidate455 {
    CProcessMagic script = {};

    ~MagicCandidate455()
    {
        ReleaseMagicControl455(script);
    }
};

struct MagicCacheEntry455 {
    DWORD id;
    std::shared_ptr<MagicCandidate455> owner;
};

static std::list<MagicCacheEntry455> stMagicCache;
static bool stMagicCacheReady455 = false;
// Keep ownership parallel to the packed CMagicList records and their borrowed pointers.
static std::shared_ptr<MagicCandidate455> stMagicOwners455[_MAX_MAGIC_EFFECT_CNT];

static auto FindMagicCacheEntry455(DWORD magicId)
{
    auto entry = stMagicCache.begin();
    while (entry != stMagicCache.end() && entry->id != magicId) ++entry;
    return entry;
}

static std::shared_ptr<MagicCandidate455> FindOrLoadMagicTrack455(DWORD magicId)
{
    if (!stMagicCacheReady455 || GetRealIDFromMagicSpt(magicId) == static_cast<DWORD>(-1))
        return nullptr;
    char* name = GetFilenameFromMagicSpt(magicId);
    const auto* config = GetR3State();
    if (!name || !std::memchr(config->EffectPath, 0, sizeof(config->EffectPath)))
        return nullptr;
    char path[256];
    const int length = std::snprintf(path, sizeof(path), "%s%s", config->EffectPath, name);
    if (length < 0 || length >= static_cast<int>(sizeof(path)))
        return nullptr;

    try {
        RF455_SetResourceGroup(GetEffectResourceGroup455());
        if (!RF455_ResourceExists(path)) {
            @@MISSING_MAGIC_WARNING@@
            return nullptr;
        }
        auto entry = FindMagicCacheEntry455(magicId);
        if (entry != stMagicCache.end()) {
            stMagicCache.splice(stMagicCache.begin(), stMagicCache, entry);
            return entry->owner;
        }

        auto owner = std::make_shared<MagicCandidate455>();
        owner->script.CreateMagicTrack(name);
        if (!owner->script.mTrackNum) return nullptr;
        stMagicCache.push_front({magicId, owner});
        if (stMagicCache.size() > _MAX_MAGIC_CACHE_SIZE) stMagicCache.pop_back();
        return owner;
    } catch (const std::bad_alloc&) {
        return nullptr;
    } catch (const std::out_of_range&) {
        return nullptr;
    } catch (const std::runtime_error&) {
        return nullptr;
    }
}

static void ReleaseActiveEffects455()
{
    for (DWORD i = 0; i < stELcnt; ++i) {
        auto& effect = stEffectList[i];
        if ((effect.mFlag & _MT_FLAG_PARTICLE) && effect.mParticle) {
            auto* particle = effect.mParticle;
            effect.mParticle = nullptr;
            particle->ReleaseParticle();
            delete particle;
        }
    }
    stELcnt = 0;
    for (DWORD i = 0; i < stMLcnt; ++i) {
        stMagicList[i].mMagicPtr = nullptr;
        stMagicOwners455[i].reset();
    }
    stMLcnt = 0;
    NowMagicListPtr = nullptr;
}
