#pragma once
#include "client455_tutorial_spatial.h"

using RF455TutorialObject = std::uintptr_t;
struct RF455TutorialSlot {std::uint8_t pack = 0, slot = 0;};
struct RF455TutorialPoint {std::int32_t x = 0, y = 0;};
struct RF455TutorialPointResult {
    bool success = false, initialized = false;
    RF455TutorialPoint point;
};
struct RF455TutorialProjection {int result = 0; float x = 0, y = 0;};
struct RF455TutorialCombatParameters {
    std::uint8_t attackType = 255;
    std::uint32_t skillId = 0xffffffff, targetTypeOrCount = 0, targetIndex = 0xffffffff;
};

class RF455TutorialActionsHost : public RF455TutorialSpatialHost {
public:
    virtual void openBoard(unsigned board, bool) = 0;
    virtual void closeBoard(unsigned board, bool) = 0;
    virtual bool boardOpen(unsigned board) = 0;
    virtual void selectInventoryPage(std::uint8_t, bool) = 0; //4731E0
    virtual RF455TutorialObject boardWindow(unsigned board) = 0;
    virtual void updateSkillTab(RF455TutorialObject window, std::uint8_t, std::uint8_t, bool) = 0;
    virtual void selectSkillTab(RF455TutorialObject window, std::uint8_t) = 0;
    virtual bool findUi25Item(RF455TutorialSlot&) = 0; //Land4289E0+36 ->477D10
    virtual void useInventoryItem(RF455TutorialSlot) = 0;
    virtual void localizedNotice(unsigned index) = 0;
    virtual void showSpecialWindow(unsigned uiId) = 0;
    virtual void closeSpecialWindow(unsigned uiId) = 0;
    virtual bool specialWindowOpen(unsigned uiId) = 0;
    virtual RF455TutorialObject beginBoardObject() = 0; //620-byte target temporary, source-owned host type
    virtual void endBoardObject(RF455TutorialObject) = 0;
    virtual bool findEquipCandidate(RF455TutorialObject temporary, std::uint8_t mappedCategory, RF455TutorialSlot&) = 0;
    virtual void equipFromInventory(RF455TutorialSlot) = 0;
    virtual void unequipSlot(std::uint8_t) = 0;
    virtual bool boardTransactionBusy() = 0;
    virtual bool equipmentSlotPresent(std::uint8_t) = 0;
    virtual void setGameInputEnabled(std::uint32_t) = 0; //Current stage vt60, Tutorial5588A0
    virtual void showMouse(std::int32_t) = 0;           //CGUIMouse vt48 ->6233C0
    virtual std::array<float,2> screenSize() = 0;
    virtual RF455TutorialPointResult cursorPoint(std::uint8_t window, bool defaultPoint, std::uint32_t element) = 0;
    virtual RF455TutorialObject firstProjectionObject() = 0;
    virtual RF455TutorialVector objectPosition(RF455TutorialObject) = 0;
    virtual RF455TutorialProjection projectCursorPoint(const RF455TutorialVector&) = 0;
    virtual bool cursorUsesWindowOrigin() = 0;
    virtual RF455TutorialPoint windowOrigin() = 0;
    virtual void setSystemCursor(RF455TutorialPoint) = 0;
    virtual void setLogicalCursor(RF455TutorialPoint) = 0;
    virtual RF455TutorialPoint logicalCursor() = 0;
    virtual void startCursorMotion(RF455TutorialPoint, std::uint8_t button) = 0; //5578F0
    virtual void setCombatMode(bool) = 0;               //411320
    virtual void setCombatFlag24308(bool) = 0;          //420B70; actual UI side effects belong to host
    virtual void traceLockOnWait() = 0;
    virtual RF455TutorialObject currentLockTarget() = 0;
    virtual std::uint32_t targetType(RF455TutorialObject) = 0;
    virtual std::uint8_t targetPlayerRace(RF455TutorialObject) = 0;
    virtual std::uint32_t targetLocalIndex(RF455TutorialObject) = 0;
    virtual bool attackSkillCode(std::uint8_t type, std::uint32_t storedIndex, std::uint32_t& code) = 0;
    virtual RF455TutorialObject createItem(std::uint32_t zero, std::uint8_t category, std::uint32_t localIndex) = 0;
    virtual bool itemStackable(RF455TutorialObject) = 0;
    virtual void setItemCount(RF455TutorialObject, std::uint32_t) = 0;
    virtual std::uint32_t itemDefaultValue(RF455TutorialObject) = 0; //45FE90
    virtual void setItemValue(RF455TutorialObject, std::uint32_t) = 0; //429C40, item+96
    virtual void setItemSerial(RF455TutorialObject, std::uint16_t) = 0;
    virtual std::uint32_t itemSerial(RF455TutorialObject) = 0;
    virtual void attachBoardItem(RF455TutorialObject boardObject, RF455TutorialObject item) = 0;
    virtual void setBoardSerial(RF455TutorialObject boardObject, std::uint32_t) = 0;
    virtual bool findEmptyInventorySlot(RF455TutorialSlot&) = 0;
    virtual void insertInventory(RF455TutorialSlot, RF455TutorialObject temporary) = 0;
    virtual RF455TutorialObject boardFindIndex(unsigned board, std::uint32_t index) = 0;
    virtual RF455TutorialObject boardItem(RF455TutorialObject boardObject) = 0;
    virtual bool linkBoardContains(RF455TutorialObject boardObject) = 0;
    virtual bool findBoardItemSlot(unsigned board, RF455TutorialObject item, RF455TutorialSlot&) = 0;
    virtual void addHotbarLink(unsigned sourceBoard, RF455TutorialSlot, std::uint8_t targetPack,
                               std::uint8_t targetSlot, bool selectPage) = 0;
    virtual std::uint32_t itemField112(RF455TutorialObject) = 0;
    virtual RF455TutorialObject hotbarObject(std::uint8_t pack, std::uint8_t slot) = 0;
    virtual std::uint32_t boardIdentity(RF455TutorialObject) = 0;
    virtual bool boardIdentityEquals(RF455TutorialObject, std::uint32_t) = 0;
    virtual void traceItemStart() = 0;
};

bool RF455_GetTutorialCombatParameters(const RF455TutorialProcessor&, RF455TutorialCombatParameters&);

class RF455TutorialActionsFactory final : public RF455TutorialFactory {
public:
    explicit RF455TutorialActionsFactory(RF455TutorialActionsHost& host,
        RF455TutorialCreationIds& ids = RF455_GetTutorialCreationIds()) : host(host), ids(ids), spatial(host,ids) {}
    std::unique_ptr<RF455TutorialProcessor> create(const RF455TutorialInstruction&) override;
private:
    RF455TutorialActionsHost& host;
    RF455TutorialCreationIds& ids;
    RF455TutorialSpatialFactory spatial;
};
