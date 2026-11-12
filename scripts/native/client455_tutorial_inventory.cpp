#include "gameobject/manager/ccharactermgr.h"
#include "gameobject/board/common/cboardmanager.h"
#include "baseheader.h"
#include "userinterface/gamewindow/guiinventorywindow.h"
#include "client455_client_items.h"
#include "client455_equipment_conditions.h"
#include "client455_protocol_observation.h"
#include "client455_tutorial_inventory.h"
#include "client455_tutorial_spatial.h"
#include <cstring>
#include <stdexcept>

namespace {
constexpr BYTE bagIndex = 0;
constexpr BYTE ammunitionKind = 11;

CGUIInventoryWindow& inventoryWindow(CInventoryBoard& board)
{
    return *static_cast<CGUIInventoryWindow*>(board.GetWindow());
}

CGUIEquipWindow& equipmentWindow(CEquipBoard& board)
{
    return *static_cast<CGUIEquipWindow*>(board.GetWindow());
}

BYTE itemKind(CBoardObject* item)
{
    return item ? RF455ConditionItem(item->GetItem455()).kind() : 255;
}

bool admitsEquipment(BYTE kind, BYTE slot)
{
    return (kind == IEPT_WEAPON && slot == UIPT_WEAPON) ||
        (kind == ammunitionKind && (slot == UIPT_BULLET_LEFT || slot == UIPT_BULLET_RIGHT));
}
}

RF455TutorialInventory::RF455TutorialInventory() = default;
RF455TutorialInventory::~RF455TutorialInventory() = default;

void RF455TutorialInventory::initialize()
{
    if (inventory) return;
    auto* avatar = _GetAvatar();
    originalCombat = avatar->GetCombatMode();
    if (auto* weapon = avatar->GetNormalItem455(IEPT_WEAPON)) {
        originalWeapon = std::make_unique<CBoardObject>();
        originalWeapon->SetItem455(weapon);
    }
    _SetUIAvatarRace(avatar->GetRace());
    equipment = std::make_unique<CEquipBoard>();
    equipment->Create(IBT_EQUIP, 1, MAX_EQUIP_WINDOW_SLOT);
    equipment->InitWindow(UII_EQUIP_WINDOW, 0, 0);
    equipment->AddPack(0);
    inventory = std::make_unique<CInventoryBoard>();
    inventory->Create(IBT_INVENTORY, 1, MAX_INVENTORY_SOCKET);
    inventory->InitWindow(UII_INVENTORY, 0, 0);
    auto& window = inventoryWindow(*inventory);
    inventory->SetEquipWindow(&equipmentWindow(*equipment));
    if (!inventory->AddPack(bagIndex)) throw std::runtime_error("Tutorial bag could not be created");
    auto* bag = window.GetPackWindow(bagIndex);
    bag->SetID(UII_INVENTORY_PACK);
    if (window.GetSizeY() + bag->GetSizeY() > _GetUIScreen()->GetSizeY()) {
        bag->SetDockingBorder(CGUIWindow::NONE_BORDER);
        bag->SetPos(window.GetPosX() - bag->GetSizeX(), window.GetPosY());
    }
    show(false);
}

void RF455TutorialInventory::shutdown()
{
    cancelPick();
    if (inventory && inventory->GetWindow()) {
        show(false);
        auto& window = inventoryWindow(*inventory);
        if (auto* bag = window.GetPackWindow(bagIndex)) _GetUIScreen()->Remove(bag);
        _GetUIScreen()->Remove(&window);
    }
    if (equipment && equipment->GetWindow()) {
        for (const BYTE slot : {UIPT_WEAPON, UIPT_BULLET_LEFT, UIPT_BULLET_RIGHT})
            if (equipped(slot)) equipment->Remove(0, slot);
        if (weaponChanged && originalWeapon) _GetAvatar()->PutOnEquipment455(originalWeapon.get());
        _GetAvatar()->CCharacter::SetCombatMode(originalCombat);
    }
    inventory.reset();
    equipment.reset();
    originalWeapon.reset();
    weaponChanged = false;
}

void RF455TutorialInventory::show(bool visible)
{
    if (!inventory || !inventory->GetWindow()) return;
    auto& window = inventoryWindow(*inventory);
    if (visible) {
        inventory->OpenWindow();
        inventory->UI_OpenPack(bagIndex, TRUE);
    } else {
        cancelPick();
        if (window.GetPackWindow(bagIndex)) inventory->UI_OpenPack(bagIndex, FALSE);
        inventory->CloseWindow();
    }
    RF455_ObserveProtocol(visible ? "tutorial-inventory-open" : "tutorial-inventory-close", 0, 0, 0);
}

bool RF455TutorialInventory::isOpen() const
{
    return inventory && inventory->IsOpen();
}

bool RF455TutorialInventory::inventoryPoint(DWORD code, POINT& point)
{
    if (!inventory) return false;
    BYTE slot = 0;
    if (code == 0xffffffff) {
        slot = inventory->FindEmptySocket(bagIndex);
    } else {
        BYTE ammunition = 255;
        unsigned ammunitionCount = 0;
        for (; slot < inventory->GetMaxSocketNum455(bagIndex); ++slot) {
            auto* item = inventory->GetObject(bagIndex, slot);
            auto* basic = item ? dynamic_cast<RF455BasicItem*>(item->GetItem455()) : nullptr;
            const auto row = basic ? basic->rawData() : RF455ItemDataSpan{};
            DWORD candidate = 0;
            if (row.size < 8) continue;
            std::memcpy(&candidate, row.data + 4, sizeof(candidate));
            if (candidate == code) break;
            if (itemKind(item) == ammunitionKind) {
                ammunition = slot;
                ++ammunitionCount;
            }
        }
        // Three shipped Specialist scripts refer to another magazine code.
        // Their demonstration can use the only magazine granted in this bag.
        if (slot == inventory->GetMaxSocketNum455(bagIndex) && ammunitionCount == 1 &&
            (code == 0x31050800 || code == 0xc5081104)) {
            slot = ammunition;
            RF455_ObserveProtocol("tutorial-ammunition-cursor-fallback", code, slot, 0);
        }
    }
    auto* bag = inventoryWindow(*inventory).GetPackWindow(bagIndex);
    return bag && bag->SlotCenter455(slot, point);
}

bool RF455TutorialInventory::equipmentPoint(BYTE slot, POINT& point)
{
    return equipment && equipmentWindow(*equipment).SlotCenter455(slot, point);
}

BYTE RF455TutorialInventory::grant(BYTE table, DWORD code)
{
    std::uint32_t index;
    if (!RF455_GameItems().data.findItemByCode(table, code, index))
        throw std::runtime_error("Tutorial item could not be resolved");
    const BYTE slot = addItem(table, index, 200);
    if (slot == 255) throw std::runtime_error("Tutorial item could not be placed");
    RF455_ObserveProtocol("tutorial-item-granted", table, index, slot);
    return slot;
}

DWORD RF455TutorialInventory::beaconForceCode(BYTE slot) const
{
    if (!inventory || slot >= inventory->GetMaxSocketNum455(bagIndex)) return ID_INVALID;
    auto* object = inventory->GetObject(bagIndex, slot);
    if (itemKind(object) != IEPT_FORCE) return ID_INVALID;
    auto* beacon = dynamic_cast<RF455BasicItem*>(object->GetItem455());
    if (!beacon) return ID_INVALID;
    const auto row = beacon->rawData();
    constexpr std::size_t forceCodeOffset = 152;
    DWORD code = ID_INVALID;
    if (row.size >= forceCodeOffset + sizeof(code)) std::memcpy(&code, row.data + forceCodeOffset, sizeof(code));
    return code;
}

BYTE RF455TutorialInventory::heldBeaconSlot() const
{
    return held == Location::Bag && beaconForceCode(heldSlot) != ID_INVALID ? heldSlot : 255;
}

std::unique_ptr<CBoardObject> RF455TutorialInventory::takeBeacon(BYTE slot)
{
    if (beaconForceCode(slot) == ID_INVALID) return {};
    std::unique_ptr<CBoardObject> beacon(inventory->GetObject(bagIndex, slot)->Clone());
    if (!beacon || !inventory->Remove(bagIndex, slot)) return {};
    if (held == Location::Bag && heldSlot == slot) cancelPick();
    return beacon;
}

bool RF455TutorialInventory::returnBeacon(CBoardObject& beacon, BYTE slot)
{
    if (!inventory || itemKind(&beacon) != IEPT_FORCE) return false;
    if (slot == 255) slot = inventory->FindEmptySocket(bagIndex);
    if (slot >= inventory->GetMaxSocketNum455(bagIndex) || inventory->GetObject(bagIndex, slot)) return false;
    return inventory->Add(bagIndex, slot, &beacon) != FALSE;
}

bool RF455TutorialInventory::collect(BYTE table, DWORD index, WORD groundSerial, BYTE quantity)
{
    const BYTE slot = addItem(table, index, quantity);
    if (slot == 255) return false;
    RF455_ObserveProtocol("tutorial-loot-collected", groundSerial, index, slot);
    return true;
}

BYTE RF455TutorialInventory::addItem(BYTE table, DWORD index, BYTE quantity)
{
    if (!inventory) return 255;
    const BYTE slot = inventory->FindEmptySocket(bagIndex);
    if (slot == 255) return slot;
    auto* item = static_cast<RF455BasicItem*>(RF455_GameItems().create(0, table, index));
    if (!item) return 255;
    if (item->IsStackable455()) item->SetDownloadValue455(quantity, 0);
    auto& serial = RF455_GetTutorialCreationIds().item;
    item->header().serial = serial;
    item->header().field8 = serial;
    CBoardObject object;
    object.SetItem455(item);
    if (!inventory->Add(bagIndex, slot, &object)) return 255;
    ++serial;
    return slot;
}

bool RF455TutorialInventory::equipped(BYTE slot)
{
    return equipment && equipment->GetObject(0, slot);
}

bool RF455TutorialInventory::transfer(Location source, BYTE from, BYTE to)
{
    if (source == Location::None || !inventory || !equipment) return false;
    const bool equipping = source == Location::Bag;
    CItemBoard& origin = equipping ? static_cast<CItemBoard&>(*inventory) : *equipment;
    CItemBoard& destination = equipping ? static_cast<CItemBoard&>(*equipment) : *inventory;
    if (from >= origin.GetMaxSocketNum455(0) || to >= destination.GetMaxSocketNum455(0) ||
        destination.GetObject(0, to)) return false;
    auto* object = origin.GetObject(0, from);
    const BYTE equipmentSlot = equipping ? to : from;
    if (!admitsEquipment(itemKind(object), equipmentSlot)) return false;
    if (!destination.Add(0, to, object)) {
        RF455_ObserveProtocol("tutorial-inventory-transfer-rejected", equipping, from, to);
        return false;
    }
    if (!origin.Remove(0, from)) {
        destination.Remove(0, to);
        return false;
    }
    if (equipmentSlot == UIPT_WEAPON) weaponChanged = true;
    RF455_ObserveProtocol(equipping ? "tutorial-item-equipped" : "tutorial-item-unequipped",
                          equipmentSlot, equipping ? from : to, 0);
    return true;
}

void RF455TutorialInventory::equipCandidate(BYTE slot)
{
    if (!inventory) return;
    for (BYTE candidate = 0; candidate < inventory->GetMaxSocketNum455(bagIndex); ++candidate)
        if (transfer(Location::Bag, candidate, slot)) return;
}

void RF455TutorialInventory::unequip(BYTE slot)
{
    if (!inventory) return;
    const BYTE free = inventory->FindEmptySocket(bagIndex);
    if (free != 255) transfer(Location::Equipment, slot, free);
}

void RF455TutorialInventory::combat(bool enabled)
{
    _GetAvatar()->CCharacter::SetCombatMode(enabled ? CSI_COMBAT : CSI_PEACE);
}

void RF455TutorialInventory::pick(Location source, BYTE slot)
{
    if (held != Location::None) return;
    auto* object = source == Location::Bag ? inventory->GetObject(bagIndex, slot) : equipment->GetObject(0, slot);
    if (!object || !object->GetIcon() || !object->GetIcon()->UsesTypedIcon455()) return;
    held = source;
    heldSlot = slot;
    _GetUIScreen()->AddTypedHoverIcon455(object->GetIcon());
    if (source == Location::Bag) {
        const auto kind = itemKind(object);
        if (kind == IEPT_WEAPON) equipmentWindow(*equipment).HighlightEquipSlot455(UIPT_WEAPON);
        if (kind == ammunitionKind) equipmentWindow(*equipment).HighlightEquipSlot455(UIPT_BULLET_LEFT);
    }
}

void RF455TutorialInventory::cancelPick()
{
    if (held == Location::None) return;
    held = Location::None;
    _GetUIScreen()->RemoveTypedHoverIcon455();
}

void RF455TutorialInventory::quickTransfer(Location source, BYTE slot)
{
    if (source == Location::Equipment) { unequip(slot); return; }
    const BYTE kind = itemKind(inventory->GetObject(bagIndex, slot));
    if (kind == IEPT_WEAPON) transfer(source, slot, UIPT_WEAPON);
    if (kind == ammunitionKind && !transfer(source, slot, UIPT_BULLET_LEFT))
        transfer(source, slot, UIPT_BULLET_RIGHT);
}

bool RF455TutorialInventory::handleMessage(UINT message, WPARAM owner, LPARAM data)
{
    if (!inventory) return false;
    if (message == WM_BOARD_DROP_OBJECT && held != Location::None) { cancelPick(); return true; }
    if (message == WM_CLOSE_WINDOW && owner == UII_INVENTORY) {
        cancelPick();
        if (inventory->UI_IsOpenedPack(bagIndex)) inventory->UI_OpenPack(bagIndex, FALSE);
        return true;
    }
    if (!isOpen() || (owner != UII_INVENTORY_PACK && owner != UII_EQUIP_WINDOW)) return false;
    const UI_MOUSE_MSG event(static_cast<DWORD>(data));
    if (event.m_byPackNo != 0) return false;
    const auto source = owner == UII_EQUIP_WINDOW ? Location::Equipment : Location::Bag;
    if (message == WM_BOARD_CHECK_REMOVE_OBJECT || message == WM_BOARD_REMOVE_OBJECT ||
        message == WM_BOARD_ADD_OBJECT || message == WM_BOARD_EQUIP_HOT_KEY)
        RF455_ObserveProtocol("tutorial-inventory-input", message, static_cast<DWORD>(owner), event.m_bySocketNo);
    switch (message) {
    case WM_BOARD_CHECK_REMOVE_OBJECT:
    case WM_BOARD_REMOVE_OBJECT: pick(source, event.m_bySocketNo); return true;
    case WM_BOARD_ADD_OBJECT:
        if (held != Location::None && held != source && transfer(held, heldSlot, event.m_bySocketNo)) cancelPick();
        return true;
    case WM_BOARD_EQUIP_HOT_KEY: quickTransfer(source, event.m_bySocketNo); return true;
    default: return false;
    }
}

namespace {
class InventoryCommand final : public RF455TutorialProcessor {
    RF455TutorialHost& owner;
    RF455TutorialInventory& inventory;
    const BYTE argument;
    DWORD code = 0;
    bool start(RF455TutorialHost& host, RF455TutorialContext&) override {
        if (&host != &owner) return false;
        switch (type) {
        case 19: inventory.show(true); break;
        case 21: inventory.show(false); break;
        case 23: inventory.equipCandidate(argument); break;
        case 25:
            inventory.unequip(argument);
            if (argument == UIPT_BULLET_LEFT) inventory.unequip(UIPT_BULLET_RIGHT);
            break;
        case 35: inventory.combat(argument == 1); break;
        case 40: inventory.grant(argument, code); break;
        default: return true;
        }
        flags |= 4;
        return true;
    }
    bool update(RF455TutorialHost& host, RF455TutorialContext&) override {
        if (&host != &owner) return false;
        switch (type) {
        case 20: return inventory.isOpen();
        case 24: return inventory.equipped(argument);
        case 26:
            return !inventory.equipped(argument) &&
                (argument != UIPT_BULLET_LEFT || !inventory.equipped(UIPT_BULLET_RIGHT));
        default: return false;
        }
    }
    void finish(RF455TutorialHost&, RF455TutorialContext&) override {}
public:
    InventoryCommand(const RF455TutorialInstruction& command, RF455TutorialHost& host, RF455TutorialInventory& inventory)
        : RF455TutorialProcessor(command.dataType, command.id, command.fixed[4]),
          owner(host), inventory(inventory), argument(command.fixed[6]) {
        if (type == 40) std::memcpy(&code, command.fixed.data() + 8, sizeof(code));
    }
};
}

std::unique_ptr<RF455TutorialProcessor> RF455_CreateTutorialInventoryCommand(
    const RF455TutorialInstruction& command, RF455TutorialHost& host, RF455TutorialInventory& inventory)
{
    const auto& data = command.fixed;
    if (command.selector != command.dataType || data.size() < 8) return nullptr;
    const auto arg = data[6];
    switch (command.selector) {
    case 19: case 20: case 21:
        if (data.size() != 8 || arg != 0) return nullptr;
        break;
    case 23: case 24: case 25: case 26:
        if (data.size() != 12 || (arg != UIPT_WEAPON && arg != UIPT_BULLET_LEFT)) return nullptr;
        break;
    case 35:
        if (data.size() != 20 || arg != 1) return nullptr;
        break;
    case 40:
        if (data.size() != 12 || (arg != 6 && arg != 11 && arg != 18)) return nullptr;
        break;
    default: return nullptr;
    }
    return std::make_unique<InventoryCommand>(command, host, inventory);
}
