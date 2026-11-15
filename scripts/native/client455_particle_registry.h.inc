#include "client455_resource_io.h"
#include <memory>
#include <string>
#include <vector>

constexpr unsigned MAX_DUMMY_PARTICLE = 6;

struct CHPARTICLE {
    BOOL m_bLoad = FALSE;
    BOOL m_bRealLoad = FALSE;
    std::unique_ptr<CParticle[]> m_Particle;
    BOOL m_bAbsAxis = TRUE;
    float m_fScale[3] = {1.0f, 1.0f, 1.0f};
    std::string m_sFileName;
    DWORD m_Count = 0;

    ~CHPARTICLE();
    void Release();
    BOOL RealLoad();
};

struct CHENTITY {
    BOOL m_bLoad = FALSE;
    BOOL m_bRealLoad = FALSE;
    CEntity m_Entity;
    BOOL m_bAbsAxis = TRUE;
    float m_fScale[3]{};
    float m_fRot[3]{};
    std::string m_sFileName;

    ~CHENTITY();
    void Release();
    BOOL RealLoad();
};

class CParticleManager {
public:
    void ReleaseParticle();
    void ReleaseEntity();
    void ResetParticleCount();
    CParticle* GetParticle(DWORD id);
    CEntity* GetEntity(DWORD id);
    CHPARTICLE* GetCHParticle(DWORD id);
    CHENTITY* GetCHEntity(DWORD id);
    float* GetEntityScale(DWORD id);
    BOOL LoadParticleIni(char* filename);
    BOOL LoadEntityIni(char* filename);
    void ReloadParticle(char* filename);
    void ReloadEntity(char* filename);

private:
    void EnsureChefIndexed();
    RF455_RpkGroup m_Chef;
    bool m_ChefIndexed = false;

    // Sparse grow-only pointer arrays. Slots and loaded instances are never
    // relocated when the declared capacity increases.
    std::vector<std::unique_ptr<CHPARTICLE>> m_Particle{3072};
    std::vector<std::unique_ptr<CHENTITY>> m_Entity{3072};
};
