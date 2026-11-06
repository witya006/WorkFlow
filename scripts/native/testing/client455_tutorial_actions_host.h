#pragma once
#include "../client455_tutorial_actions.h"
#include "client455_tutorial_recording_host.h"
#include <map>
using BaseHost=RF455TutorialRecordingSpatialHost<RF455TutorialActionsHost>;
struct RF455TutorialRecordingActionsHost final : BaseHost {
    std::map<unsigned,bool> boards,special;
    bool ui25Found=true,equipFound=true,busy=false,offsetCursor=true,freeSlot=true,stackable=true,memberSlot=true,linked=false;
    std::array<bool,256> equipment{};
    RF455TutorialSlot candidate{2,3};
    RF455TutorialPoint cursorPointNow{},systemPoint{},motionPoint{},origin{100,200};
    RF455TutorialPointResult uiPoint{true,true,{500,600}};
    RF455TutorialProjection projection{1,12.9f,20.9f};
    RF455TutorialObject projectionObject=600,lockTarget=900,foundObject=701,innerItem=501,hotbar=801;
    std::uint32_t lockType=1,lockIndex=0x12345,inputEnabled=0,defaultValue=17,countValue=0,itemValue=0;
    std::uint32_t skillCode=88,ready112=0,identity=1234,hotbarIdentity=1234;
    std::uint16_t serial=0;
    std::uint8_t race=3,lastMapped=0,lastHotbarSlot=0,lastCategory=0;
    std::int32_t mouseValue=0;
    unsigned notices=0,equipQueries=0,busyQueries=0,motions=0,systems=0,skillQueries=0,traceItems=0,traceLocks=0;
    bool skillFound=true;
    bool pointDefault=false;
    std::uint8_t pointWindow=0;
    std::uint32_t pointElement=0;
    void event(const std::string& value){calls.push_back(value);}
    void openBoard(unsigned b,bool value) override {RF455_TutorialTestCheck(value,"open arg");boards[b]=true;event("open"+std::to_string(b));}
    void closeBoard(unsigned b,bool value) override {RF455_TutorialTestCheck(value,"close arg");boards[b]=false;event("close"+std::to_string(b));}
    bool boardOpen(unsigned b) override {event("is-open"+std::to_string(b));return boards[b];}
    void selectInventoryPage(std::uint8_t page,bool value) override {RF455_TutorialTestCheck(page==0&&value,"inventory page");event("inventory-page");}
    RF455TutorialObject boardWindow(unsigned b) override {event("window"+std::to_string(b));return 1000+b;}
    void updateSkillTab(RF455TutorialObject w,std::uint8_t page,std::uint8_t item,bool value) override {
        RF455_TutorialTestCheck((w==1007||w==1003)&&!page&&!item&&value,"skill tab args");event("tab-update");
    }
    void selectSkillTab(RF455TutorialObject w,std::uint8_t page) override {RF455_TutorialTestCheck((w==1007||w==1003)&&!page,"select tab");event("tab-select");}
    bool findUi25Item(RF455TutorialSlot& out) override {out=candidate;event("find-ui25");return ui25Found;}
    void useInventoryItem(RF455TutorialSlot p) override {RF455_TutorialTestCheck(p.pack==2&&p.slot==3,"use slot");boards[3]=true;event("use");}
    void localizedNotice(unsigned index) override {RF455_TutorialTestCheck(index==284,"notice index");++notices;event("notice284");}
    void showSpecialWindow(unsigned id) override {special[id]=true;event("special-open");}
    void closeSpecialWindow(unsigned id) override {special[id]=false;event("special-close");}
    bool specialWindowOpen(unsigned id) override {return special[id];}
    RF455TutorialObject beginBoardObject() override {event("board-construct");return 800;}
    void endBoardObject(RF455TutorialObject value) override {RF455_TutorialTestCheck(value==800,"board temporary");event("board-destruct");}
    bool findEquipCandidate(RF455TutorialObject value,std::uint8_t category,RF455TutorialSlot& out) override {
        RF455_TutorialTestCheck(value==800,"equip temporary");lastMapped=category;out=candidate;event("equip-find");return equipFound;
    }
    void equipFromInventory(RF455TutorialSlot p) override {RF455_TutorialTestCheck(p.pack==2&&p.slot==3,"equip slot");event("equip");}
    void unequipSlot(std::uint8_t slot) override {equipment[slot]=false;event("unequip"+std::to_string(slot));}
    bool boardTransactionBusy() override {++busyQueries;return busy;}
    bool equipmentSlotPresent(std::uint8_t slot) override {++equipQueries;return equipment[slot];}
    void setGameInputEnabled(std::uint32_t value) override {inputEnabled=value;}
    void showMouse(std::int32_t value) override {mouseValue=value;}
    std::array<float,2> screenSize() override {return {{1025,769}};}
    RF455TutorialPointResult cursorPoint(std::uint8_t window,bool defaultPoint,std::uint32_t element) override {
        pointWindow=window;pointDefault=defaultPoint;pointElement=element;return uiPoint;
    }
    RF455TutorialObject firstProjectionObject() override {return projectionObject;}
    RF455TutorialVector objectPosition(RF455TutorialObject object) override {RF455_TutorialTestCheck(object==600,"project object");return {{1,2,3}};}
    RF455TutorialProjection projectCursorPoint(const RF455TutorialVector&) override {return projection;}
    bool cursorUsesWindowOrigin() override {return offsetCursor;}
    RF455TutorialPoint windowOrigin() override {return origin;}
    void setSystemCursor(RF455TutorialPoint point) override {systemPoint=point;++systems;}
    void setLogicalCursor(RF455TutorialPoint point) override {cursorPointNow=point;}
    RF455TutorialPoint logicalCursor() override {return cursorPointNow;}
    void startCursorMotion(RF455TutorialPoint point,std::uint8_t) override {motionPoint=point;++motions;}
    void setCombatMode(bool value) override {toggle=value;}
    void setCombatFlag24308(bool value) override {toggle=value;}
    void traceLockOnWait() override {++traceLocks;}
    RF455TutorialObject currentLockTarget() override {return lockTarget;}
    std::uint32_t targetType(RF455TutorialObject value) override {RF455_TutorialTestCheck(value==900,"lock target");return lockType;}
    std::uint8_t targetPlayerRace(RF455TutorialObject) override {return race;}
    std::uint32_t targetLocalIndex(RF455TutorialObject) override {return lockIndex;}
    bool attackSkillCode(std::uint8_t,std::uint32_t,std::uint32_t& out) override {++skillQueries;out=skillCode;return skillFound;}
    bool resolveItem(std::uint8_t category,std::uint32_t index,bool clone,std::uint32_t& out) override {
        lastCategory=category;return BaseHost::resolveItem(category,index,clone,out);
    }
    RF455TutorialObject createItem(std::uint32_t zero,std::uint8_t category,std::uint32_t local) override {
        RF455_TutorialTestCheck(!zero&&category==lastCategory&&local==0x12345&&cloneActive,"create item args");event("create-item");return 501;
    }
    bool itemStackable(RF455TutorialObject) override {event("stackable");return stackable;}
    void setItemCount(RF455TutorialObject,std::uint32_t value) override {countValue=value;event("set-count");}
    std::uint32_t itemDefaultValue(RF455TutorialObject) override {event("default-value");return defaultValue;}
    void setItemValue(RF455TutorialObject,std::uint32_t value) override {itemValue=value;event("set-value");}
    void setItemSerial(RF455TutorialObject,std::uint16_t value) override {serial=value;event("set-serial");}
    std::uint32_t itemSerial(RF455TutorialObject) override {event("get-serial");return serial;}
    void attachBoardItem(RF455TutorialObject temporary,RF455TutorialObject item) override {RF455_TutorialTestCheck(temporary==800&&item==501,"attach item");event("attach-item");}
    void setBoardSerial(RF455TutorialObject temporary,std::uint32_t value) override {RF455_TutorialTestCheck(temporary==800&&value==serial,"board serial");event("board-serial");}
    bool findEmptyInventorySlot(RF455TutorialSlot& out) override {out=candidate;event("empty-slot");return freeSlot;}
    void insertInventory(RF455TutorialSlot p,RF455TutorialObject temporary) override {
        RF455_TutorialTestCheck(p.pack==2&&p.slot==3&&temporary==800&&cloneActive,"insert args/lifetime");event("insert");
    }
    RF455TutorialObject boardFindIndex(unsigned b,std::uint32_t index) override {RF455_TutorialTestCheck((b==3||b==7)&&index==77,"find board index");return foundObject;}
    RF455TutorialObject boardItem(RF455TutorialObject object) override {RF455_TutorialTestCheck(object!=0,"nonnull board object");return innerItem;}
    bool linkBoardContains(RF455TutorialObject object) override {return object!=0&&linked;}
    bool findBoardItemSlot(unsigned b,RF455TutorialObject item,RF455TutorialSlot& out) override {
        RF455_TutorialTestCheck((b==3||b==7)&&item==501,"find item position");out=candidate;return memberSlot;
    }
    void addHotbarLink(unsigned b,RF455TutorialSlot p,std::uint8_t pack,std::uint8_t slot,bool select) override {
        RF455_TutorialTestCheck((b==3||b==7)&&p.pack==2&&p.slot==3&&pack==255&&slot==255&&!select,"hotbar request args");event("link"+std::to_string(b));
    }
    std::uint32_t itemField112(RF455TutorialObject item) override {RF455_TutorialTestCheck(item==501,"item ready");return ready112;}
    RF455TutorialObject hotbarObject(std::uint8_t pack,std::uint8_t slot) override {RF455_TutorialTestCheck(!pack,"hotbar pack");lastHotbarSlot=slot;return hotbar;}
    std::uint32_t boardIdentity(RF455TutorialObject object) override {RF455_TutorialTestCheck(object!=0,"identity target");return identity;}
    bool boardIdentityEquals(RF455TutorialObject object,std::uint32_t value) override {RF455_TutorialTestCheck(object==801,"hotbar identity");return hotbarIdentity==value;}
    void traceItemStart() override {++traceItems;event("item-start");}
};
