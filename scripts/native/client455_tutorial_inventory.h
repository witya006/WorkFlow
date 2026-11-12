#pragma once
#include "client455_tutorial_runtime.h"
#include <windows.h>

class CInventoryBoard;
class CEquipBoard;
class CBoardObject;

// Tutorial equipment has its own lifetime and never sends a zone request.
class RF455TutorialInventory {
public:
    RF455TutorialInventory();
    ~RF455TutorialInventory();
    void initialize();
    void shutdown();
    void show(bool visible);
    bool isOpen() const;
    bool handleMessage(UINT, WPARAM, LPARAM);
    bool inventoryPoint(DWORD code, POINT&);
    bool equipmentPoint(BYTE slot, POINT&);
    void grant(BYTE table, DWORD code);
    void equipCandidate(BYTE slot);
    void unequip(BYTE slot);
    bool equipped(BYTE slot);
    void combat(bool enabled);
private:
    enum class Location { None, Bag, Equipment };
    std::unique_ptr<CEquipBoard> equipment;
    std::unique_ptr<CInventoryBoard> inventory;
    std::unique_ptr<CBoardObject> originalWeapon;
    BYTE originalCombat = 0;
    bool weaponChanged = false;
    Location held = Location::None;
    BYTE heldSlot = 0;

    void pick(Location, BYTE);
    void cancelPick();
    bool transfer(Location source, BYTE from, BYTE to);
    void quickTransfer(Location source, BYTE slot);
};

std::unique_ptr<RF455TutorialProcessor> RF455_CreateTutorialInventoryCommand(
    const RF455TutorialInstruction&, RF455TutorialHost&, RF455TutorialInventory&);
