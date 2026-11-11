#include "client455_client_items.h"
#include "character/npc/cmonster.h"
#include "global.h"

#include <cstdio>
#include <cstdlib>

namespace {
void require(bool condition, const char* message) {
    if (condition) return;
    std::fprintf(stderr, "%s\n", message);
    std::exit(1);
}

class WingProbe : public CMonster {
public:
    using CBaseNpc::GetAnimationData;
    using CMonster::GetAnimationData_Force;
    DWORD GetMeshID() override { return 1; }
    DWORD clipKey() { return m_Animation.GetAnimationID(); }

    void setForce(SF_DATA& identity, DWORD index, BYTE level) {
        identity.dwDTIndex = index;
        CSFItem force;
        force.SetSFType(CAT_FORCE);
        force.SetIndex(index);
        force.SetData(&identity);
        force.SetLevel(level);
        SetSFItem(&force);
    }
};
}

int main(int argc, char** argv) {
    require(argc == 5, "Expected two EDF and two Wing ANI inputs");
    require(RF455_GameItems().skillForce.loadFiles(argv[1], argv[2]), "Load actual 455 Force tables");
    ChInterface renderer;
    g_ifCharIF = &renderer;
    require(_CreateAnimationMgr(), "Create ordinary animation manager");
    auto* attack = _GetAniMgr()->AddAni(RLI_MONSTER, argv[3]);
    auto* support = _GetAniMgr()->AddAni(RLI_MONSTER, argv[4]);
    require(attack && support && attack != support, "Register both Wing clips");
    attack->m_Ident = 0x10c0;
    support->m_Ident = 0x10d0;
    {
        SF_DATA identity{};
        WingProbe wing;
        const auto select = [&wing](CAniData* expected) {
            require(wing.GetAnimationData(CAI_FORCE_INVOKE, MAI_FORCE_ATTACK) == expected &&
                    wing.clipKey() == expected->m_Ident && expected->m_Load && expected->imported,
                    "Actor selected and loaded the expected real clip");
        };
        select(support);
        wing.setForce(identity, 24, 1);
        select(attack);
        wing.setForce(identity, 25, 1);
        select(support);
        wing.setForce(identity, 25, 0);
        select(attack);
        wing.setForce(identity, 0, 7);
        select(support);
        require(!wing.GetAnimationData_Force(ID_INVALID) && wing.clipKey() == 0x10d0,
                "Invalid animation type returns before updating the key");
    }
    require(_DestroyAnimationMgr(), "Release normal animation manager");
    g_ifCharIF = nullptr;
    std::puts("{\"status\":\"PASS\",\"selected_cases\":5,\"invalid_type_cases\":1,"
              "\"actual_ani_imported\":2,\"attack_key\":4288,\"support_key\":4304}");
    return 0;
}
