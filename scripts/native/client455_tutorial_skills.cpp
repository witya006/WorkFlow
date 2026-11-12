#include "gameobject/manager/ccharactermgr.h"
#include "gameobject/board/common/cboardmanager.h"
#include "baseheader.h"
#include "client455_client_items.h"
#include "client455_protocol_observation.h"
#include "client455_tutorial_inventory.h"
#include "client455_tutorial_skills.h"
#include <cstring>
#include <stdexcept>

namespace {
constexpr BYTE shortcutWindowId = 3;

DWORD field(RF455ItemDataSpan row, std::size_t offset)
{
    DWORD value = 0;
    if (row.size >= offset + sizeof(value)) std::memcpy(&value, row.data + offset, sizeof(value));
    return value;
}

RF455SkillForceItem* payload(CBoardObject* source)
{
    return source ? dynamic_cast<RF455SkillForceItem*>(source->GetItem455()) : nullptr;
}

CGUISkFcUnit* skillRow(CBoardObject* source)
{
    auto* item = payload(source);
    return item ? static_cast<CGUISkFcUnit*>(item->record().iconBoard) : nullptr;
}

bool center(CGUIItem* icon, POINT& point)
{
    if (!icon || icon->GetSizeX() <= 0 || icon->GetSizeY() <= 0) return false;
    point = {icon->GetPosX() + icon->GetSizeX() / 2, icon->GetPosY() + icon->GetSizeY() / 2};
    return true;
}
}

RF455TutorialSkills::RF455TutorialSkills() = default;
RF455TutorialSkills::~RF455TutorialSkills() = default;

void RF455TutorialSkills::initialize(bool forceLesson)
{
    if (skills) return;
    force = forceLesson;
    const BYTE race = _GetAvatar()->GetRace();
    if (race >= 6 || (force && race >= 4)) throw std::runtime_error("Tutorial ability race is invalid");
    if (force) skills = std::make_unique<CForceBoard>();
    else skills = std::make_unique<CSkillBoard>();
    skills->Create(force ? IBT_FORCE : IBT_SKILL, force ? 5 : 7, force ? 40 : 20);
    skills->InitWindow(force ? UII_FORCE_WINDOW : UII_SKILL_WINDOW, 0, 0);
    for (BYTE bank = 0; bank < skills->GetMaxPackNum(); ++bank) skills->AddPack(bank);

    const BYTE category = force ? CAT_FORCE : CAT_SKILL;
    auto& items = RF455_GameItems();
    unsigned rows = 0;
    for (DWORD index = 0; ; ++index) {
        const auto row = items.skillForce.get(category, index);
        if (!row.data) break;
        if (row.size < (force ? 458u : 1096u)) throw std::runtime_error("Tutorial skill record is invalid");
        const auto code = field(row, 4);
        BYTE tab = row.data[12];
        if ((code & 0x000ff000) == 0x000ff000 || !row.data[452 + race]) continue;
        if (force) {
            if (tab == (race < 2 ? FCT_DARK : FCT_HOLY) || tab > 5) continue;
            if (tab) --tab;
        } else if (tab >= 5 || !field(row, 1092) || (tab == 4 && field(row, 1068) == 0xffffffff)) continue;
        const BYTE slot = skills->FindEmptySocket(tab);
        if (slot == 255) throw std::runtime_error("Tutorial skill tab has no available slot");
        auto* skill = items.manager.createSkillForce(items.skillForce, category, index);
        if (!skill) throw std::runtime_error("Tutorial skill payload could not be created");
        CBoardObject source;
        source.SetItem455(skill);
        if (!skills->AddTypedSF455(tab, slot, source))
            throw std::runtime_error("Tutorial skill row could not be added");
        if (force) skillRow(skills->GetObject(tab, slot))->SetUnitState(CGUISkFcUnit::NoneUnit);
        ++rows;
    }
    if (!rows) throw std::runtime_error("Tutorial skill records are unavailable");

    shortcuts = std::make_unique<CLinkBoard>();
    shortcuts->InitializeMainGame455();
    shortcuts->LinkerWindow455().PostUseRequests455(true);
    skills->CloseWindow();
    RF455_ObserveProtocol(force ? "tutorial-force-rows" : "tutorial-skill-rows", rows, race, 0);
}

void RF455TutorialSkills::shutdown()
{
    cancelPick();
    if (shortcuts && shortcuts->GetWindow()) {
        shortcuts->ClearTypedLinker455();
        _GetUIScreen()->Remove(shortcuts->GetWindow());
    }
    if (skills && skills->GetWindow()) {
        skills->Clear();
        _GetUIScreen()->Remove(skills->GetWindow());
    }
    shortcuts.reset();
    skills.reset();
    beacons.clear();
}

void RF455TutorialSkills::show(bool visible)
{
    if (!skills) return;
    if (visible) skills->OpenWindow();
    else {
        cancelPick();
        skills->CloseWindow();
    }
    const char* event = force ? (visible ? "tutorial-force-open" : "tutorial-force-close")
                              : (visible ? "tutorial-skills-open" : "tutorial-skills-close");
    RF455_ObserveProtocol(event, 0, 0, 0);
}

bool RF455TutorialSkills::isOpen() const
{
    return skills && skills->IsOpen();
}

CBoardObject* RF455TutorialSkills::findSkill(DWORD code)
{
    if (!skills) return nullptr;
    for (BYTE tab = 0; tab < skills->GetMaxPackNum(); ++tab) {
        for (BYTE slot = 0; slot < skills->GetMaxSocketNum455(tab); ++slot) {
            auto* source = skills->GetObject(tab, slot);
            auto* item = payload(source);
            if (item && field(item->rawData(), 4) == code) return source;
        }
    }
    return nullptr;
}

bool RF455TutorialSkills::skillPoint(DWORD code, POINT& point)
{
    auto* source = findSkill(code);
    if (!source || !skills->IsOpen()) return false;
    BYTE tab = 0, slot = 0;
    if (!skills->GetObjectPosition(tab, slot, source->GetIndex())) return false;
    auto* window = static_cast<CGUISFWindow*>(skills->GetWindow());
    return center(window->RevealSkill455(tab, source->GetIndex()), point);
}

bool RF455TutorialSkills::shortcutPoint(DWORD number, POINT& point)
{
    if (!shortcuts || number < 1 || number > 10) return false;
    auto& window = shortcuts->LinkerWindow455();
    const auto bank = window.HotbarState455().active;
    return center(shortcuts->LinkerIcon455(bank, static_cast<BYTE>(number - 1)), point);
}

bool RF455TutorialSkills::matchesShortcut(BYTE number, DWORD code)
{
    if (!shortcuts) return false;
    auto* source = findSkill(code);
    if (!source) return false;
    if (number >= 1 && number <= 10)
        return source->IsEqual(shortcuts->GetObject(0, number - 1));
    if (number != 255) return false;
    for (BYTE bank = 0; bank < shortcuts->GetMaxPackNum(); ++bank)
        for (BYTE slot = 0; slot < shortcuts->GetMaxSocketNum455(bank); ++slot)
            if (source->IsEqual(shortcuts->GetObject(bank, slot))) return true;
    return false;
}

bool RF455TutorialSkills::hasBeacon(DWORD code) const
{
    return beacons.find(code) != beacons.end();
}

bool RF455TutorialSkills::installBeacon(RF455TutorialInventory& inventory, BYTE slot)
{
    if (!force) return false;
    const DWORD code = inventory.beaconForceCode(slot);
    auto* source = findSkill(code);
    auto* row = skillRow(source);
    if (!row) return false;
    const auto entry = beacons.emplace(code, nullptr);
    if (!entry.second) return false;
    auto beacon = inventory.takeBeacon(slot);
    if (!beacon) {
        beacons.erase(entry.first);
        return false;
    }
    entry.first->second = std::move(beacon);
    payload(source)->SetEquipmentLevel455(1);
    row->SetUnitState(CGUISkFcUnit::Enabled);
    RF455_ObserveProtocol("tutorial-beacon-installed", code, slot, 0);
    return true;
}

bool RF455TutorialSkills::returnBeacon(RF455TutorialInventory& inventory, CBoardObject* source, BYTE slot)
{
    auto* item = payload(source);
    if (!force || !item) return false;
    const auto code = field(item->rawData(), 4);
    const auto beacon = beacons.find(code);
    if (beacon == beacons.end() || matchesShortcut(255, code) || !inventory.returnBeacon(*beacon->second, slot))
        return false;
    cancelPick();
    beacons.erase(beacon);
    item->SetEquipmentLevel455(0);
    skillRow(source)->SetUnitState(CGUISkFcUnit::NoneUnit);
    RF455_ObserveProtocol("tutorial-beacon-returned", code, slot, 0);
    return true;
}

RF455SkillForceItem* RF455TutorialSkills::readyForce(DWORD index)
{
    if (!force || !skills || held) return nullptr;
    auto* item = payload(skills->GetObjectByIndex(index));
    return item && hasBeacon(field(item->rawData(), 4)) ? item : nullptr;
}

void RF455TutorialSkills::activateShortcut(BYTE slot)
{
    if (!shortcuts || slot >= 10 || held) return;
    auto& window = shortcuts->LinkerWindow455();
    window.UseItem455(window.HotbarState455().active, slot);
}

RF455SkillForceItem* RF455TutorialSkills::shortcutSkill(BYTE bank, BYTE slot)
{
    if (!shortcuts || held || bank >= shortcuts->GetMaxPackNum() ||
        slot >= shortcuts->GetMaxSocketNum455(bank)) return nullptr;
    return payload(shortcuts->GetObject(bank, slot));
}

void RF455TutorialSkills::pick(CBoardObject* source)
{
    if (held || !source || !source->GetIcon()) return;
    _GetUIScreen()->AddTypedHoverIcon455(source->GetIcon());
    held = source;
}

void RF455TutorialSkills::cancelPick()
{
    if (!held) return;
    held = nullptr;
    _GetUIScreen()->RemoveTypedHoverIcon455();
}

bool RF455TutorialSkills::bind(BYTE bank, BYTE slot, CBoardObject* source)
{
    auto* row = skillRow(source);
    if (!row || slot >= shortcuts->GetMaxSocketNum455(bank) ||
        (force && !hasBeacon(field(payload(source)->rawData(), 4)))) return false;
    auto* old = shortcuts->GetObject(bank, slot);
    if (source->IsEqual(old)) return true;
    auto* previous = old ? skills->GetObjectByIndex(old->GetIndex()) : nullptr;
    if (old && (!previous || !shortcuts->RemoveTypedObject455(bank, slot))) return false;
    if (!shortcuts->AddTypedObject455(bank, slot, source, row)) {
        if (previous) shortcuts->AddTypedObject455(bank, slot, previous, skillRow(previous));
        return false;
    }
    if (previous && !matchesShortcut(255, field(payload(previous)->rawData(), 4)))
        skillRow(previous)->SetUnitState(force ? CGUISkFcUnit::Enabled : CGUISkFcUnit::Disabled);
    RF455_ObserveProtocol("tutorial-shortcut-linked", bank, slot, field(payload(source)->rawData(), 4));
    return true;
}

bool RF455TutorialSkills::handleMessage(UINT message, WPARAM owner, LPARAM data, RF455TutorialInventory& inventory)
{
    if (!shortcuts) return false;
    if (message == WM_BOARD_DROP_OBJECT && held) {
        cancelPick();
        return true;
    }
    if (force && owner == UII_INVENTORY_PACK && inventory.isOpen()) {
        const UI_MOUSE_MSG event(static_cast<DWORD>(data));
        if (event.m_byPackNo != 0) return false;
        if (message == WM_BOARD_ADD_OBJECT && held) {
            returnBeacon(inventory, held, event.m_bySocketNo);
            return true;
        }
        if ((message == WM_BOARD_EQUIP_HOT_KEY || message == WM_BOARD_USE_OBJECT) &&
            inventory.beaconForceCode(event.m_bySocketNo) != ID_INVALID) {
            if (installBeacon(inventory, event.m_bySocketNo)) show(true);
            return true;
        }
    }
    if (owner == (force ? UII_FORCE_WINDOW : UII_SKILL_WINDOW)) {
        if (message == WM_CLOSE_WINDOW) { cancelPick(); return true; }
        if (message == WM_BOARD_ADD_OBJECT) {
            if (force) installBeacon(inventory, inventory.heldBeaconSlot());
            else cancelPick();
            return true;
        }
        auto* source = skills->GetObjectByIndex(static_cast<DWORD>(data));
        if (message == WM_BOARD_REMOVE_OBJECT) {
            if (!force || (source && hasBeacon(field(payload(source)->rawData(), 4)))) pick(source);
            return true;
        }
        if (message == WM_BOARD_EQUIP_HOT_KEY) {
            if (force) {
                returnBeacon(inventory, source);
                return true;
            }
            const BYTE bank = shortcuts->LinkerWindow455().HotbarState455().active;
            bind(bank, shortcuts->CObjectBoard::FindEmptySocket(bank), source);
            return true;
        }
        if (force && message == WM_BOARD_USE_OBJECT && GetKeyState(VK_CONTROL) < 0) {
            const BYTE bank = shortcuts->LinkerWindow455().HotbarState455().active;
            bind(bank, shortcuts->CObjectBoard::FindEmptySocket(bank), source);
            return true;
        }
        return false;
    }
    if (owner != shortcutWindowId) return false;
    const UI_MOUSE_MSG event(static_cast<DWORD>(data));
    if (message == WM_BOARD_ADD_OBJECT && held) {
        if (bind(event.m_byPackNo, event.m_bySocketNo, held)) cancelPick();
        return true;
    }
    if (message == WM_BOARD_CHECK_REMOVE_OBJECT) {
        auto* old = shortcuts->GetObject(event.m_byPackNo, event.m_bySocketNo);
        if (old) pick(skills->GetObjectByIndex(old->GetIndex()));
        return true;
    }
    return message == WM_BOARD_USE_OBJECT;
}
