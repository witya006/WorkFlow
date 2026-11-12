#include "gameobject/manager/ccharactermgr.h"
#include "gameobject/board/common/cboardmanager.h"
#include "cland.h"
#include "ccamera.h"
#include "datafile.h"
#include "datatable/cresourcedatamgr.h"
#include "item/citemmgr.h"
#include "input/imeedit.h"
#include "baseheader.h"
#include "gameprogress/cgameprogress.h"
#include "userinterface/gamewindow/guiselectedcharwin.h"
#include "userinterface/spritemgr.h"
#include "mainapp.h"
#include "client455_client_items.h"
#include "client455_protocol_observation.h"
#include "client455_tutorial_targets.h"
#include "client455_world_updates.h"
#include <algorithm>
#include <cstdlib>
#include <cstring>

RF455TutorialTargets::RF455TutorialTargets() = default;
RF455TutorialTargets::~RF455TutorialTargets() = default;

bool RF455TutorialTargets::spawn(std::uint32_t code, const RF455TutorialVector& position)
{
    const auto& table = RF455_GameItems().data.characterTables()[2];
    std::uint32_t index = 0;
    for (; index < table.count; ++index) {
        const auto row = table.get(index);
        std::uint32_t recordCode;
        std::memcpy(&recordCode, row.data + 4, sizeof(recordCode));
        if (recordCode == code) break;
    }
    if (index == table.count || index > 0xffff) return false;

    auto* attributes = _GetCharDataMgr()->GetMonster(index);
    if (!attributes) return false;
    const auto serial = RF455_GetTutorialCreationIds().monster++;
    RF455MonsterSpawn placement{};
    placement.record = static_cast<std::uint16_t>(index);
    placement.zoneIndex = 1;
    placement.serial = serial;
    for (unsigned i = 0; i != position.size(); ++i)
        placement.position[i] = static_cast<std::int16_t>(RF455_TutorialCoordinateWord(position[i]));

    auto monster = std::make_unique<CMonster>();
    monster->SetIndex(serial);
    monster->SetServerIndex(placement.zoneIndex);
    monster->SetDTIndex(index);
    monster->SetAttribute(attributes);
    monster->Disable(ROSF_OUT_OF_VISUAL_FIELD_CLIENT | ROSF_OUT_OF_VISUAL_FIELD_SERVER);
    RF455_PlaceMonster(*monster, placement);
    monster->SetAction(CAI_MOVE_STOP, FALSE);
    monsters.push_back(std::move(monster));
    RF455_ObserveProtocol("tutorial-monster-spawn", code, index, serial);
    return true;
}

bool RF455TutorialTargets::hasSelection() const
{
    return selected && !selected->IsDeath();
}

std::uint32_t RF455TutorialTargets::selectedId() const
{
    return hasSelection() ? selected->GetIndex() : ID_INVALID;
}

bool RF455TutorialTargets::attack(RF455SkillForceItem* skill, RF455TutorialContext& context)
{
    if (!hasSelection()) return false;
    auto* avatar = _GetAvatar();
    const DWORD index = skill ? skill->tableIndex() : ID_INVALID;
    CSFItem activeSkill;
    if (skill) {
        const BYTE level = skill->EffectiveLevel455();
        if (!activeSkill.CreateSkill455(index, level ? level : 1) || !activeSkill.IsAttackable()) return false;
    }

    auto* target = selected;
    auto* hit = target->AddAttackerInfo(avatar, TRUE);
    if (!hit) return false;
    avatar->CCharacter::SetCombatMode(CSI_COMBAT);
    avatar->SetRotY(avatar->GetPosition(), target->GetPosition(), TRUE);
    avatar->SetSFItem(skill ? &activeSkill : nullptr);
    avatar->CPlayer::SetAction(skill ? CAI_SKILL_INVOKE : CAI_COMBAT_ATTACK, FALSE);

    // Local Tutorial results have their own scripted damage intervals (RVA 0x1647d0).
    const DWORD damage = skill ? 300 + std::rand() % 50 : 200 + std::rand() % 10;
    hit->SetDamage455(damage);
    hit->SetDamageType_AT(skill ? CAT_SKILL : CAT_NORMAL);
    hit->SetDamageType_Dist(ADT_NEAR);
    hit->SetEffectFrameNum(1);
    target->ReceiveHealth455(0);
    hit->AdvanceDamage455();
    target->ApplyHealthImpact455(hit->GetCurDamagePoint(), damage, 1);
    hit->SetProcessedDamage(TRUE);
    target->SetDeath(mon_destroy_code_die);
    target->SetReceiveNetMsg("Death");

    context.attackType = skill ? 0 : 4;
    context.skillIndex = index;
    context.target[0] = CTI_MONSTER;
    context.target[1] = target->GetIndex();
    ++context.state52;
    clearSelection();
    if (skill) RF455_ObserveProtocol("tutorial-skill-used", index, activeSkill.GetDTCode(), activeSkill.GetLevel());
    RF455_ObserveProtocol("tutorial-attack-animation", avatar->GetAction(), avatar->GetAnimationID(), context.attackType);
    RF455_ObserveProtocol("tutorial-attack-result", context.attackType, damage, context.target[1]);
    return true;
}

bool RF455TutorialTargets::select(long x, long y, const RF455TutorialVector& camera)
{
    CMonster* target = nullptr;
    float nearest = 0;
    for (const auto& monster : monsters) {
        Vector3f hit{};
        if (monster->IsDeath() || !monster->CollisionCheckWithBoundBox(x, y, hit)) continue;
        const float dx = hit[0] - camera[0], dy = hit[1] - camera[1], dz = hit[2] - camera[2];
        const float distance = dx * dx + dy * dy + dz * dz;
        if (!target || distance < nearest) {
            target = monster.get();
            nearest = distance;
        }
    }
    if (!target) return false;
    if (!window) {
        auto panel = std::make_unique<CGUISelectedMobInfoWin>();
        panel->Init();
        panel->SetID(UII_TARGET_INFO_WINDOW);
        panel->SetPos((_GetUIScreen()->GetSizeX() - panel->GetSizeX()) / 2, 0);
        _GetUIScreen()->Add(panel.get());
        window = std::move(panel);
    }
    selected = target;
    window->SetMobName(target->GetName());
    window->SetLevel455(target->GetLevel());
    window->SetHP(target->GetHPRate());
    window->Open();
    RF455_ObserveProtocol("tutorial-monster-selected", target->GetIndex(), target->GetDTIndex(), 0);
    return true;
}

void RF455TutorialTargets::clearSelection()
{
    selected = nullptr;
    if (window) window->Close();
}

void RF455TutorialTargets::update()
{
    for (const auto& monster : monsters) {
        monster->FrameMove();
        monster->Animation();
    }
    monsters.erase(std::remove_if(monsters.begin(), monsters.end(), [&](const auto& monster) {
        if (!monster->IsEnable(ROSF_DESTROY)) return false;
        if (selected == monster.get()) clearSelection();
        return true;
    }), monsters.end());
    auto* avatar = _GetAvatar();
    if ((avatar->IsEqualAction(CAI_COMBAT_ATTACK) || avatar->IsEqualAction(CAI_SKILL_INVOKE)) &&
        !avatar->GetAnimation()->IsAnimating()) {
        avatar->SetSFItem(nullptr);
        avatar->SetAction(CAI_MOVE_STOP);
    }
}

void RF455TutorialTargets::render()
{
    for (const auto& monster : monsters) monster->Render();
}

void RF455TutorialTargets::shutdown()
{
    clearSelection();
    if (window) _GetUIScreen()->Remove(window.get());
    window.reset();
    monsters.clear();
}
