#include "client455_client_items.h"
#include "client455_monster_force_result.h"
#include "gameobject/manager/ccharactermgr.h"
#include "gameobject/board/common/cboardmanager.h"
#include "network/netmsgprocessor/combat/cnetmsgprocessor_combat.h"
#include "network/netmsgprocessor/item/cnetmsgprocessor_itemarrangement.h"
#include "addcodebyjang/foreffect.h"
#include "addcodebyjang/effectutil.h"
#include "addcodebyjang/effectutilfont.h"
#include "addcodebyjang/cmagicscript.h"
#include "addcodebyjang/effectcore.h"
#include "cland.h"
#include "ccamera.h"
#include "datafile.h"
#include "datatable/cresourcedatamgr.h"
#include "input/imeedit.h"
#include "gameprogress/cgameprogress.h"
#include "userinterface/spritemgr.h"
#include "network/cnetworkmgr.h"
#include "mainapp.h"
#include "r3sound.h"
#include "mss.h"

#include <array>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <memory>

extern CMainApp g_MainApp;

namespace {
void require(bool condition, const char* message) {
    if (condition) return;
    std::fprintf(stderr, "%s\n", message);
    std::exit(1);
}

#include "client455_combat_result_effect_probe.inc"

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

void checkHitReaction(CMonster& target, CMonster& wing, DWORD effectType, bool retain = false) {
    target.SetMesh(1);
    auto* incoming = target.GetAttackerInfo(&wing);
    auto* effects = _GetEffectInfoList();
    effects->Clear();
    const DWORD expected = (target.GetMeshID() << 8) | (effectType << 4) | (target.GetAnimationID() & 0xf);
    const float health = target.GetHPRate();
    target.GetCombatState()->ProcessDamage();
    require(effects->empty(), "Reaction waits for the impact flag");
    incoming->SetDamaged(TRUE);
    target.GetCombatState()->ProcessDamage();
    require(effects->size() == 1, "One reaction entered the normal effect queue");
    const auto& effect = **effects->begin();
    require(effect.dwID == expected && effect.dwType == ETI_MONSTER && effect.dwValue == 0 &&
            effect.dwMyself[0] == CTI_MONSTER && effect.dwMyself[1] == target.GetIndex() &&
            effect.dwTarget[0] == CTI_MONSTER && effect.dwTarget[1] == wing.GetIndex() &&
            target.GetHPRate() == health && !incoming->GetTotalDamagePoint(),
            "Queued effect key, actors and zero damage match the impact");
    target.GetCombatState()->ProcessDamage();
    require(effects->size() == 1, "A consumed impact does not repeat");
    if (!retain) effects->Clear();
}

void checkForceImpactEffect(CMonster& target, CMonster& wing, DWORD damage, bool retain = false,
                            bool expectCritical = true) {
    auto* effects = _GetEffectInfoList();
    require(effects->size() == (expectCritical ? 2 : 1), "One Force effect and the expected critical effect");
    auto current = effects->begin();
    if (expectCritical) {
        const auto& critical = **current++;
        require(critical.dwType == ETI_MONSTER && ((critical.dwID >> 4) & 0xf) == MET_DAMAGE_CRITICAL &&
                critical.dwValue == damage && critical.dwMyself[0] == CTI_MONSTER &&
                critical.dwMyself[1] == target.GetIndex() && critical.dwTarget[0] == CTI_MONSTER &&
                critical.dwTarget[1] == wing.GetIndex(), "Critical precedes Force and keeps the impact actors");
    }
    const auto& effect = **current;
    require(effect.dwType == ETI_FORCE && effect.dwID == 0x92000e &&
            effect.dwValue == damage && effect.byRangeType_For_Effect == 0 &&
            effect.unknown48_455 == 0 && effect.dwMyself[0] == CTI_MONSTER &&
            effect.dwMyself[1] == target.GetIndex() && effect.dwTarget[0] == CTI_MONSTER &&
            effect.dwTarget[1] == wing.GetIndex(), "455 Force key, range, amount and actor identities");
    if (!retain) effects->Clear();
}

template<class Tag, typename Tag::Type Member>
struct MemberAccess {
    friend typename Tag::Type access(Tag) { return Member; }
};
struct CombatBoundsMember {
    using Type = BBOX* CResObject::*;
    friend Type access(CombatBoundsMember);
};
template struct MemberAccess<CombatBoundsMember, &CResObject::m_pBBox>;

void checkCriticalReaction(CMonster& target, CMonster& wing, DWORD damage, CAniData& peace, CAniData& combat) {
    require(target.GetAction() == CAI_DAMAGED_CRITICAL && target.GetAnimationID() == 0x10e0 &&
            target.GetAnimation()->GetAniData() == &peace && peace.m_Load && peace.imported,
            "A critical impact selects the real Wing peace animation");
    checkForceImpactEffect(target, wing, damage, true);
    target.SetPosition(2, 10, 8);
    target.SetScale(1.0f);
    target.SetDamageTimeForShake(0.0f);
    BBOX bounds{};
    bounds.pMax[1] = 40.0f;
    auto& boundSlot = target.*access(CombatBoundsMember{});
    auto* previousBounds = boundSlot;
    boundSlot = &bounds;
    auto* effects = _GetEffectInfoList();
    auto force = effects->begin();
    ++force;
    effects->erase(force);
    DispatchQueuedEffects();
    boundSlot = previousBounds;
    Vector3f position{};
    target.Get2ndLightPos(position);
    require(effects->empty() && target.GetDamageTimeForShake() == 0.27f &&
            std::fabs(target.Get2ndLightRadius() - 12.0f) < 0.00001f && target.Get2ndDensity() == 1.0f &&
            position[0] == 2 && std::fabs(position[1] - 38.8f) < 0.00001f && position[2] == 8,
            "Normal queue applies the 455 critical shock using the target bounds");
    target.SetCombatMode(CSI_COMBAT);
    require(target.GetAction() == CAI_DAMAGED_CRITICAL && target.GetAnimationID() == 0x10f0 &&
            target.GetAnimation()->GetAniData() == &combat && combat.m_Load && combat.imported,
            "Combat mode reselects the real Wing combat animation for the same action");
}

void checkDamage(CCharacterMgr& manager, CMonster& wing, CMonster& primary, bool checkHealth, bool checkReaction,
                 bool checkImpactEffect, CombatResultDisplay* display,
                 CAniData* criticalPeace, CAniData* criticalCombat) {
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
    if (checkImpactEffect || criticalPeace) {
        CSFItem secondRow;
        require(secondRow.CreateForce455(25, 1) && secondRow.GetDTCode() == 0x9201 &&
                secondRow.GetRangeTypeForEffect() == 1, "Second real Force row preserves code and nonzero range");
        auto* effects = _GetEffectInfoList();
        effects->Clear();
        primary.GetCombatState()->ProcessDamage();
        require(effects->empty(), "Force effect waits for the impact");
    }
    incoming->SetDamaged(TRUE);
    primary.GetCombatState()->ProcessDamage();
    require(incoming->GetCurDamagePoint() == first && incoming->GetTotalDamagePoint() == original - first &&
            incoming->GetEffectFrameNum() == 1, "First impact uses the 455 jitter and pending damage");
    if (checkHealth) expectRate(0.8f - (0.8f - 0.5f) * float(double(first) / original));
    if (checkImpactEffect) {
        checkForceImpactEffect(primary, wing, first, display != nullptr);
        if (display) display->verifyDamage(primary, first, 0);
    }
    if (criticalPeace) {
        checkCriticalReaction(primary, wing, first, *criticalPeace, *criticalCombat);
        primary.EnableCharacterFlags455(2);
    }
    incoming->SetDamaged(TRUE);
    primary.GetCombatState()->ProcessDamage();
    require(incoming->GetCurDamagePoint() == original - first && !incoming->GetTotalDamagePoint() &&
            !incoming->GetEffectFrameNum() && primary.GetHP() == hp, "Final impact uses the remaining damage");
    if (checkImpactEffect) {
        checkForceImpactEffect(primary, wing, original - first, display != nullptr);
        if (display) display->verifyDamage(primary, original - first, 1);
    }
    if (criticalPeace) {
        checkForceImpactEffect(primary, wing, original - first, false, false);
        require(primary.GetAnimationID() == 0x10f0, "The control flag suppresses the critical reaction");
        primary.DisableCharacterFlags455(2);
    }
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
    if (checkReaction) {
        checkHitReaction(*targets[5], wing, 13, display != nullptr);
        if (display) display->verifyVisible(*targets[5], true);
        checkHitReaction(*targets[4], wing, 4, display != nullptr);
        if (display) {
            display->verifyVisible(*targets[4], false);
            checkHitReaction(*targets[5], wing, 13, true);
            display->verifyClipped(*targets[5]);
        }
    }
}
}

int main(int argc, char** argv) {
    const bool checkCritical = argc == 8 && std::strcmp(argv[5], "--critical") == 0;
    const bool checkHealth = argc == 6 && std::strcmp(argv[5], "--health") == 0;
    const bool checkBlockRender = argc == 6 && std::strcmp(argv[5], "--block-render") == 0;
    const bool checkDamageRender = argc == 6 && std::strcmp(argv[5], "--damage-render") == 0;
    const bool checkReaction = checkBlockRender || (argc == 6 && std::strcmp(argv[5], "--reaction") == 0);
    const bool checkImpactEffect = checkDamageRender || (argc == 6 && std::strcmp(argv[5], "--impact-effect") == 0);
    require(argc == 5 || checkHealth || checkReaction || checkImpactEffect || checkCritical ||
            (argc == 6 && std::strcmp(argv[5], "--damage") == 0),
            "Expected actual 455 Force and Wing inputs");
    require(RF455_GameItems().skillForce.loadFiles(argv[1], argv[2]), "Load Force tables");
    auto display = checkBlockRender || checkDamageRender
        ? std::make_unique<CombatResultDisplay>(checkDamageRender) : nullptr;
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
    CAniData* criticalPeace = nullptr;
    CAniData* criticalCombat = nullptr;
    std::array<ANI_EXT_INFO, 2> criticalExtras{};
    if (checkCritical) {
        criticalPeace = _GetAniMgr()->AddAni(RLI_MONSTER, argv[6]);
        criticalCombat = _GetAniMgr()->AddAni(RLI_MONSTER, argv[7]);
        require(criticalPeace && criticalCombat, "Register actual Wing critical clips");
        criticalPeace->m_Ident = 0x10e0;
        criticalCombat->m_Ident = 0x10f0;
        criticalPeace->m_pExtra = &criticalExtras[0];
        criticalCombat->m_pExtra = &criticalExtras[1];
    }

    auto manager = std::make_unique<CCharacterMgr>();
    constexpr DWORD serial = 1032066, targetSerial = 1032067;
    auto* wing = manager->AddMonster(serial);
    auto* target = manager->AddMonster(targetSerial);
    require(wing && target, "Create both normal actors");
    wing->SetIndex(serial);
    wing->SetMesh(1);
    target->SetIndex(targetSerial);
    require(wing->GetMeshID() == 1, "Actor owns the registered mesh identity");

    if (argc >= 6) {
        target->SetMesh(1);
        checkDamage(*manager, *wing, *target, checkHealth, checkReaction, checkImpactEffect, display.get(),
                    criticalPeace, criticalCombat);
        manager->Clear();
        manager.reset();
        if (checkCritical) {
            criticalPeace->m_pExtra = nullptr;
            criticalCombat->m_pExtra = nullptr;
        }
        require(_DestroyAnimationMgr() && _DestroyMeshMgr(), "Release normal asset managers");
        g_ifCharIF = nullptr;
        if (display)
            display->report();
        else if (checkCritical)
            std::puts("{\"status\":\"PASS\",\"clips\":[4320,4336],\"critical_before_force\":true,"
                      "\"control_flag_suppresses_critical\":true,\"shake_seconds\":0.27,"
                      "\"light_radius\":12,\"light_density\":1,\"light_position\":[2,38.8,8]}");
        else if (checkImpactEffect)
            std::puts("{\"status\":\"PASS\",\"effect_id\":\"0x92000e\",\"range\":0,"
                      "\"checked_impacts\":2,\"total_damage\":70000,\"second_range\":1}");
        else if (checkReaction)
            std::puts("{\"status\":\"PASS\",\"reaction_types\":[13,4],\"checked_impacts\":2,"
                      "\"numeric_damage\":0,\"duplicated_reaction\":false}");
        else if (checkHealth)
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
