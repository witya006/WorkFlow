#include "client455_client_items.h"
#include "client455_monster_force_result.h"
#include "gameobject/manager/ccharactermgr.h"
#include "gameobject/board/common/cboardmanager.h"
#include "network/netmsgprocessor/combat/cnetmsgprocessor_combat.h"
#include "network/netmsgprocessor/item/cnetmsgprocessor_itemarrangement.h"

#include <array>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <memory>

namespace {
void require(bool condition, const char* message) {
    if (condition) return;
    std::fprintf(stderr, "%s\n", message);
    std::exit(1);
}

bool sendHealth(CNetMsgProcessor_ItemArrangement& processor, DWORD serial, BYTE opcode, WORD fraction,
                bool truncated = false) {
    std::array<char, 16> payload{};
    const bool targetInfo = opcode == 27;
    const std::size_t type = targetInfo ? 2 : 1;
    payload[type] = CTI_MONSTER;
    std::memcpy(payload.data() + type + 1, &serial, sizeof serial);
    std::memcpy(payload.data() + type + 5, &fraction, sizeof fraction);
    _MSG_HEADER header{WORD(4 + (targetInfo ? 16 : 8) - (truncated ? 1 : 0)), {13, opcode}};
    return processor.AnalysisServerPacket(&header, payload.data());
}

void checkDamage(CCharacterMgr& manager, CMonster& wing, CMonster& primary, bool checkHealth) {
    constexpr std::array<std::int32_t, 6> amounts{70000, 4500, 321, 1, -1, -2};
    std::array<CMonster*, amounts.size()> targets{};
    targets[0] = &primary;
    CNetMsgProcessor_Combat processor;
    CNetMsgProcessor_ItemArrangement itemProcessor;
    CCharacter& healthOwner = primary;
    const auto expectRate = [&healthOwner](float expected) {
        require(std::fabs(healthOwner.GetHPRate() - expected) < 0.000001f, "Health from the ordinary actor getter");
    };
    if (checkHealth) {
        expectRate(1.0f);
        require(sendHealth(itemProcessor, primary.GetIndex(), 29, 8000), "Immediate health without attackers");
        expectRate(0.8f);
    }
    std::array<char, 15 + 14 * amounts.size()> payload{};
    const DWORD serial = wing.GetIndex();
    payload[0] = CTI_MONSTER;
    std::memcpy(payload.data() + 1, &serial, sizeof serial);
    payload[5] = 24;
    payload[6] = 1;
    payload[12] = 1;
    payload[14] = static_cast<char>(amounts.size());
    for (std::size_t i = 0; i < amounts.size(); ++i) {
        const DWORD targetSerial = primary.GetIndex() + static_cast<DWORD>(i);
        if (i != 0 && i != 2) {
            targets[i] = manager.AddMonster(targetSerial);
            require(targets[i], "Create an ordinary victim");
            targets[i]->SetIndex(targetSerial);
        }
        const std::size_t offset = 15 + 14 * i;
        payload[offset] = CTI_MONSTER;
        std::memcpy(payload.data() + offset + 1, &targetSerial, sizeof targetSerial);
        std::memcpy(payload.data() + offset + 5, &amounts[i], sizeof amounts[i]);
    }
    _MSG_HEADER header{WORD(4 + payload.size()), {5, 9}};
    require(processor.AnalysisServerPacket(&header, payload.data()), "Normal dispatcher receives multi-target Force");
    require(wing.GetCombatState()->GetTotalEnemyNum(ET_VICTIM) == 5 && wing.GetAnimationID() == 0x10c0,
            "All known targets enter the attack");
    for (std::size_t i = 0; i < amounts.size(); ++i) {
        auto* target = targets[i];
        if (!target) continue;
        auto* outgoing = wing.GetVictimInfo(target);
        auto* incoming = target->GetAttackerInfo(&wing);
        const DWORD attackPoint = i == 5 ? static_cast<DWORD>(-2) : i < 2 ? amounts[i] : 0;
        const DWORD damage = i < 2 ? amounts[i] : 0;
        require(outgoing && incoming && outgoing->GetAttacked() && outgoing->GetAttackPoint() == attackPoint &&
                incoming->GetTotalDamagePoint() == damage && incoming->GetCurDamagePoint() == 0 &&
                incoming->GetDamageType_CT() == 1 && incoming->GetDamageType_AT() == CAT_FORCE &&
                incoming->GetDamageType_Dist() == ADT_NEAR && incoming->GetSFItem()->HasForceRow455() &&
                incoming->GetSFItem()->GetDTIndex() == 24,
                "Per-victim Force record retains damage, type, and critical state");
    }

    auto* incoming = primary.GetAttackerInfo(&wing);
    const auto hp = primary.GetHP();
    if (checkHealth) {
        require(sendHealth(itemProcessor, primary.GetIndex(), 29, 5000), "Queue received health before impact");
        expectRate(0.8f);
    }
    constexpr DWORD original = 70000;
    std::srand(613);
    const bool add = (std::rand() % 2) != 0;
    const DWORD jitter = std::rand() % 7001;
    const DWORD first = add ? 35000 + jitter : 35000 - jitter;
    std::srand(613);
    incoming->SetEffectFrameNum(2);
    incoming->SetDamaged(TRUE);
    primary.GetCombatState()->ProcessDamage();
    require(incoming->GetCurDamagePoint() == first && incoming->GetTotalDamagePoint() == original - first &&
            incoming->GetEffectFrameNum() == 1, "First impact uses the 455 jitter and pending damage");
    if (checkHealth) expectRate(0.8f - (0.8f - 0.5f) * float(double(first) / original));
    incoming->SetDamaged(TRUE);
    primary.GetCombatState()->ProcessDamage();
    require(incoming->GetCurDamagePoint() == original - first && !incoming->GetTotalDamagePoint() &&
            !incoming->GetEffectFrameNum() && primary.GetHP() == hp, "Final impact uses the remaining damage");
    if (checkHealth) {
        expectRate(0.5f);
        require(sendHealth(itemProcessor, primary.GetIndex(), 29, 9000), "Recovery applies with a queued attacker");
        expectRate(0.9f);
        require(sendHealth(itemProcessor, primary.GetIndex(), 27, 9500), "Successful target info updates health");
        expectRate(0.95f);
        require(!sendHealth(itemProcessor, primary.GetIndex(), 29, 1000, true), "Short update is rejected");
        expectRate(0.95f);
        require(targets[1]->GetHPRate() == 1.0f, "Health belongs to the addressed monster");
    }
}
}

int main(int argc, char** argv) {
    const bool checkHealth = argc == 6 && std::strcmp(argv[5], "--health") == 0;
    require(argc == 5 || checkHealth || (argc == 6 && std::strcmp(argv[5], "--damage") == 0),
            "Expected actual 455 Force and Wing inputs");
    require(RF455_GameItems().skillForce.loadFiles(argv[1], argv[2]), "Load Force tables");
    ChInterface renderer;
    g_ifCharIF = &renderer;
    require(_CreateMeshMgr() && _CreateAnimationMgr(), "Initialize normal asset managers");
    char fixtureMesh[] = "wing-identity.msh";
    auto* mesh = _GetMeshMgr()->AddMesh(RLI_MONSTER, fixtureMesh, nullptr);
    require(mesh, "Register a mesh identity in the normal manager");
    mesh->m_ID = 1;
    mesh->m_Load = true;

    auto* attack = _GetAniMgr()->AddAni(RLI_MONSTER, argv[3]);
    auto* support = _GetAniMgr()->AddAni(RLI_MONSTER, argv[4]);
    require(attack && support, "Register both actual Wing clips");
    attack->m_Ident = 0x10c0;
    support->m_Ident = 0x10d0;

    auto manager = std::make_unique<CCharacterMgr>();
    constexpr DWORD serial = 1032066, targetSerial = 1032067;
    auto* wing = manager->AddMonster(serial);
    auto* target = manager->AddMonster(targetSerial);
    require(wing && target, "Create both normal actors");
    wing->SetIndex(serial);
    wing->SetMesh(1);
    target->SetIndex(targetSerial);
    require(wing->GetMeshID() == 1, "Actor owns the registered mesh identity");

    if (argc == 6) {
        checkDamage(*manager, *wing, *target, checkHealth);
        manager->Clear();
        manager.reset();
        require(_DestroyAnimationMgr() && _DestroyMeshMgr(), "Release normal asset managers");
        g_ifCharIF = nullptr;
        if (checkHealth)
            std::puts("{\"status\":\"PASS\",\"health_routes\":[27,29],\"initial_fraction\":1,"
                      "\"before_impact\":0.8,\"after_final_impact\":0.5,\"after_recovery\":0.95,"
                      "\"verified_impact_frames\":2,\"short_update_rejected\":true}");
        else
            std::puts("{\"status\":\"PASS\",\"target_rows\":6,\"resolved_targets\":5,"
                      "\"largest_damage\":70000,\"verified_impact_frames\":2}");
        return 0;
    }

    CNetMsgProcessor_Combat processor;
    std::array<char, 29> payload{};
    payload[0] = CTI_MONSTER;
    std::memcpy(payload.data() + 1, &serial, sizeof serial);
    payload[14] = 1;
    payload[15] = CTI_MONSTER;
    std::memcpy(payload.data() + 16, &targetSerial, sizeof targetSerial);
    _MSG_HEADER header{WORD(4 + payload.size()), {5, 9}};

    payload[5] = 24;
    payload[6] = 1;
    _GetGGI()->SetRequestProcessState(TRUE);
    require(processor.AnalysisServerPacket(&header, payload.data()) &&
            wing->GetCombatMode() == CSI_COMBAT && wing->GetAction() == CAI_FORCE_INVOKE &&
            wing->GetCombatState()->IsReceiveAttackResultMsg() &&
            wing->GetSFItem() && wing->GetSFItem()->GetDTIndex() == 24 &&
            wing->GetAnimationID() == 0x10c0 && attack->m_Load && attack->imported,
            "Ordinary 5/9 installs the active Force and loads the attack animation");

    payload[5] = 25;
    require(processor.AnalysisServerPacket(&header, payload.data()) &&
            wing->GetSFItem()->GetDTIndex() == 25 && wing->GetSFItem()->GetLevel() == 1 &&
            wing->GetAnimationID() == 0x10d0 && support->m_Load && support->imported,
            "Another Force result selects the real support animation");

    payload[5] = static_cast<char>(255);
    require(processor.AnalysisServerPacket(&header, payload.data()) &&
            wing->GetSFItem()->GetDTIndex() == 25 && wing->GetAnimationID() == 0x10d0,
            "Missing Force data leaves the current item and animation in place");
    payload[5] = 24;
    --header.m_wSize;
    require(!processor.AnalysisServerPacket(&header, payload.data()) &&
            wing->GetAnimationID() == 0x10d0, "Short result leaves the actor untouched");
    ++header.m_wSize;
    payload[14] = 33;
    require(!processor.AnalysisServerPacket(&header, payload.data()) &&
            wing->GetAnimationID() == 0x10d0, "Invalid victim count leaves the actor untouched");
    payload[14] = 1;
    payload[0] = CTI_PLAYER;
    require(!processor.AnalysisServerPacket(&header, payload.data()) &&
            wing->GetAnimationID() == 0x10d0, "Selected route applies to monsters");

    manager->Clear();
    manager.reset();
    require(_DestroyAnimationMgr() && _DestroyMeshMgr(), "Release normal asset managers");
    g_ifCharIF = nullptr;
    std::puts("{\"status\":\"PASS\",\"selected_routes\":2,\"rejected_cases\":3,"
              "\"missing_row_retained\":true,\"real_animations\":2}");
    return 0;
}
