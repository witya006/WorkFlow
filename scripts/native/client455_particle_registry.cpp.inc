#include "client455_effect_ini.h"
#include <io.h>
#include <cstdio>
#include <cstring>
#include <new>

namespace {
constexpr DWORD maxOrdinaryEffectDefinitions455 = 65535;

// The 455 lazy loaders select the ordinary CHEF group for the complete load.
// Restore the caller's routing, including an independently disabled archive flag.
class OrdinaryChefScope455 {
    RF455_RpkGroup* previousGroup;
    BOOL previousEnabled;

public:
    explicit OrdinaryChefScope455(RF455_RpkGroup& chef)
        : previousGroup(RF455_GetResourceGroup()), previousEnabled(RF455_GetResourceArchiveEnabled())
    {
        RF455_SetResourceGroup(&chef);
    }

    ~OrdinaryChefScope455()
    {
        RF455_SetResourceGroup(previousGroup);
        RF455_SetResourceArchiveEnabled(previousEnabled);
    }

    OrdinaryChefScope455(const OrdinaryChefScope455&) = delete;
    OrdinaryChefScope455& operator=(const OrdinaryChefScope455&) = delete;
};

void releaseParticleInstances455(CParticle* instances)
{
    if (!instances) return;
    for (unsigned i = 1; i < MAX_DUMMY_PARTICLE; ++i) {
        instances[i].mEntity = nullptr; // Clones borrow only the source entity.
        instances[i].ReleaseParticle();
    }
    instances[0].ReleaseParticle();
    instances[0].ReleaseEntity();
}

int profileIndex455(const RF455EffectIni& profile, const char* section)
{
    char text[256];
    profile.readString(section, "INDEX", "0", text, sizeof(text));
    int index = 0;
    std::sscanf(text, "%d", &index);
    return index;
}

void profileFloat455(const RF455EffectIni& profile, const char* section, const char* key,
                     const char* defaultValue, float& value)
{
    char text[256];
    profile.readString(section, key, defaultValue, text, sizeof(text));
    std::sscanf(text, "%f", &value);
}

template<class Slot>
void readEffectTransform455(const RF455EffectIni& profile, const char* section, Slot& slot)
{
    profileFloat455(profile, section, "SCALEX", "1.0", slot.m_fScale[0]);
    profileFloat455(profile, section, "SCALEY", "1.0", slot.m_fScale[1]);
    profileFloat455(profile, section, "SCALEZ", "1.0", slot.m_fScale[2]);
    float axis = 0.0f;
    char text[256];
    profile.readString(section, "ABSAXIS", "1", text, sizeof(text));
    static_assert(sizeof(axis) == sizeof(slot.m_bAbsAxis), "455 ABSAXIS field");
    if (std::sscanf(text, "%f", &axis) == 1)
        std::memcpy(&slot.m_bAbsAxis, &axis, sizeof(axis));
}
}

CHPARTICLE::~CHPARTICLE()
{
    Release();
}

void CHPARTICLE::Release()
{
    releaseParticleInstances455(m_Particle.get());
    m_Particle.reset();
    m_bLoad = m_bRealLoad = FALSE;
    m_Count = 0;
}

BOOL CHPARTICLE::RealLoad()
{
    if (m_bRealLoad) return TRUE;
    if (!m_bLoad || m_sFileName.empty()) return FALSE;
    std::unique_ptr<CParticle[]> pending(new (std::nothrow) CParticle[MAX_DUMMY_PARTICLE]);
    if (!pending) return FALSE;
    if (!pending[0].LoadParticleSPT(&m_sFileName[0], _DO_NOT_MANAGE_TEXTURE)) {
        releaseParticleInstances455(pending.get());
        return FALSE;
    }
    for (unsigned i = 1; i < MAX_DUMMY_PARTICLE; ++i) {
        if (!pending[i].CopyTemplate455(pending[0])) {
            releaseParticleInstances455(pending.get());
            return FALSE;
        }
    }
    float origin[3]{};
    for (unsigned i = 0; i < MAX_DUMMY_PARTICLE; ++i) {
        auto& particle = pending[i];
        particle.InitParticle();
        if (!particle.mElement) {
            releaseParticleInstances455(pending.get());
            return FALSE;
        }
        particle.SetParticleState(_PARTICLE_STATE_START);
        particle.SetCreatePos(origin);
    }
    m_Particle.swap(pending);
    m_bRealLoad = TRUE;
    return TRUE;
}

CHENTITY::~CHENTITY()
{
    Release();
}

void CHENTITY::Release()
{
    m_Entity.ReleaseEntity();
    m_bLoad = m_bRealLoad = FALSE;
}

BOOL CHENTITY::RealLoad()
{
    if (m_bRealLoad) return TRUE;
    if (!m_bLoad || m_sFileName.empty() ||
        !m_Entity.LoadEntity(&m_sFileName[0], _DO_NOT_MANAGE_TEXTURE) || !m_Entity.IsLoadedEntity())
        return FALSE;
    m_Entity.RestoreTexMem();
    m_bRealLoad = TRUE;
    return TRUE;
}

CHPARTICLE* CParticleManager::GetCHParticle(DWORD id)
{
    const auto* slot = id < m_Particle.size() ? &m_Particle[id] : nullptr;
    return slot && *slot && (*slot)->m_bLoad ? slot->get() : nullptr;
}

CHENTITY* CParticleManager::GetCHEntity(DWORD id)
{
    const auto* slot = id < m_Entity.size() ? &m_Entity[id] : nullptr;
    return slot && *slot && (*slot)->m_bLoad ? slot->get() : nullptr;
}

void CParticleManager::EnsureChefIndexed()
{
    if (m_ChefIndexed) return;
    m_Chef.LoadDirectory(".\\chef\\");
    m_ChefIndexed = true;
}

CParticle* CParticleManager::GetParticle(DWORD id)
{
    auto* slot = GetCHParticle(id);
    if (!slot) return nullptr;
    if (!slot->m_bRealLoad) {
        if (slot->m_sFileName.empty()) return nullptr;
        EnsureChefIndexed();
        const OrdinaryChefScope455 scope(m_Chef);
        if (!slot->RealLoad()) return nullptr;
    }
    return &slot->m_Particle[slot->m_Count++ % MAX_DUMMY_PARTICLE];
}

CEntity* CParticleManager::GetEntity(DWORD id)
{
    auto* slot = GetCHEntity(id);
    if (!slot) return nullptr;
    if (!slot->m_bRealLoad) {
        if (slot->m_sFileName.empty()) return nullptr;
        EnsureChefIndexed();
        const OrdinaryChefScope455 scope(m_Chef);
        if (!slot->RealLoad()) return nullptr;
    }
    return &slot->m_Entity;
}

float* CParticleManager::GetEntityScale(DWORD id)
{
    auto* slot = GetCHEntity(id);
    return slot ? slot->m_fScale : nullptr;
}

void CParticleManager::ResetParticleCount()
{
    for (auto& slot : m_Particle)
        if (slot) slot->m_Count = 0;
}

void CParticleManager::ReleaseParticle()
{
    // RVA 0x3BF420 unloads the index and releases only previously loaded slots.
    m_Chef.Release();
    m_ChefIndexed = false;
    for (auto& slot : m_Particle)
        if (slot && slot->m_bRealLoad) slot->Release();
}

void CParticleManager::ReleaseEntity()
{
    for (auto& slot : m_Entity)
        if (slot && slot->m_bRealLoad) slot->Release();
}

// Client 455 x86 RVA 0x3BE640 (load), 0x3BE2A0 (register).
BOOL CParticleManager::LoadParticleIni(char* filename)
{
    if (!filename || !*filename) return FALSE;
    const RF455EffectIni profile(filename);
    const DWORD count = profile.readInt("PARTICLE_INFO", "MAXPARTICLE", 0);
    if (count > maxOrdinaryEffectDefinitions455) return FALSE;
    ReleaseParticle();
    EnsureChefIndexed();
    BOOL available = TRUE;
    try {
        if (m_Particle.size() <= count) m_Particle.resize(static_cast<std::size_t>(count) + 1);
        for (DWORD i = 1; i <= count; ++i) {
            char section[32], name[256];
            std::sprintf(section, "PARTICLE%lu", i);
            const auto id = static_cast<DWORD>(profileIndex455(profile, section));
            profile.readString(section, "PARTICLE", "NULL", name, sizeof(name));
            if (!id) {
                available = FALSE;
            } else {
                char probe[sizeof(name)];
                std::strcpy(probe, name);
                if (!m_Chef.Exists(probe) && _access(probe, 0) != 0) available = FALSE;
            }
            if (id >= m_Particle.size() || GetCHParticle(id)) continue;
            auto& slot = m_Particle[id];
            if (!slot) slot.reset(new CHPARTICLE);
            slot->m_sFileName = name;
            slot->m_bAbsAxis = TRUE;
            for (auto& value : slot->m_fScale) value = 1.0f;
            readEffectTransform455(profile, section, *slot);
            slot->m_bLoad = TRUE;
        }
    } catch (const std::bad_alloc&) {
        return FALSE;
    }
    return available;
}

// Client 455 x86 RVA 0x3BF060 (load), 0x3BE3E0 (register).
BOOL CParticleManager::LoadEntityIni(char* filename)
{
    if (!filename || !*filename) return FALSE;
    const RF455EffectIni profile(filename);
    const DWORD count = profile.readInt("ENTITY_INFO", "MAXENTITY", 0);
    if (count > maxOrdinaryEffectDefinitions455) return FALSE;
    try {
        if (m_Entity.size() <= count) m_Entity.resize(static_cast<std::size_t>(count) + 1);
        for (DWORD i = 1; i <= count; ++i) {
            char section[32], name[256];
            std::sprintf(section, "ENTITY%lu", i);
            const auto id = static_cast<DWORD>(profileIndex455(profile, section));
            if (id >= m_Entity.size() || GetCHEntity(id)) continue;
            profile.readString(section, "ENTITY", "NULL", name, sizeof(name));
            auto& slot = m_Entity[id];
            if (!slot) slot.reset(new CHENTITY);
            slot->m_sFileName = name;
            slot->m_bAbsAxis = TRUE;
            for (auto& value : slot->m_fScale) value = 0.0f;
            for (auto& value : slot->m_fRot) value = 0.0f;
            readEffectTransform455(profile, section, *slot);
            profileFloat455(profile, section, "ROTX", "0.0", slot->m_fRot[0]);
            profileFloat455(profile, section, "ROTY", "0.0", slot->m_fRot[1]);
            profileFloat455(profile, section, "ROTZ", "0.0", slot->m_fRot[2]);
            slot->m_bLoad = TRUE;
        }
    } catch (const std::bad_alloc&) {
        return FALSE;
    }
    return TRUE;
}

void CParticleManager::ReloadParticle(char* filename)
{
    LoadParticleIni(filename);
}

void CParticleManager::ReloadEntity(char* filename)
{
    ReleaseEntity();
    LoadEntityIni(filename);
}
