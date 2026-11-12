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
