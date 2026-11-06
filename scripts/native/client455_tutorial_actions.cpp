#include "client455_tutorial_actions.h"
#include <cstring>
#include <stdexcept>

extern "C" void __cdecl _ftol2_sse(void);
namespace {
std::uint16_t word(const std::vector<std::uint8_t>& b, std::size_t at) {
    return std::uint16_t(b[at]) | (std::uint16_t(b[at+1]) << 8);
}
std::uint32_t dword(const std::vector<std::uint8_t>& b, std::size_t at) {
    return std::uint32_t(word(b,at)) | (std::uint32_t(word(b,at+2)) << 16);
}
std::int16_t signedWord(std::uint16_t bits) {std::int16_t value; std::memcpy(&value,&bits,2); return value;}
std::int32_t signedDword(std::uint32_t bits) {std::int32_t value; std::memcpy(&value,&bits,4); return value;}
std::int32_t add(std::int32_t a, std::int32_t b) {return signedDword(std::uint32_t(a)+std::uint32_t(b));}
std::int16_t coordinate(float value, bool half = false) {
    if (!half) return signedWord(RF455_TutorialCoordinateWord(value));
    const double two = 2.0; std::uint16_t result;
    __asm {fld value
           fdiv two
           call _ftol2_sse
           mov result,ax}
    return signedWord(result);
}
int board(unsigned ui) {
    switch (ui) {case 0:case 63:case 64:return 0;case 5:return 7;case 6:return 3;case 11:return 17;default:return -1;}
}
struct BoardTemporary {
    RF455TutorialActionsHost& host; RF455TutorialObject object;
    explicit BoardTemporary(RF455TutorialActionsHost& host) : host(host),object(host.beginBoardObject()) {}
    ~BoardTemporary() {host.endBoardObject(object);}
};
struct ItemClone {
    RF455TutorialActionsHost& host;
    explicit ItemClone(RF455TutorialActionsHost& host) : host(host) {host.beginItemClone();}
    ~ItemClone() {host.endItemClone();}
};
class Action : public RF455TutorialProcessor {
public:
    Action(const RF455TutorialInstruction& op, RF455TutorialActionsHost& host)
        : RF455TutorialProcessor(op.dataType,op.id,op.fixed[4]), host(host) {}
protected:
    RF455TutorialActionsHost& host;
    bool bound(RF455TutorialHost& other) const {return &other == &host;}
};

class Ui final : public Action {
public:
    Ui(const RF455TutorialInstruction& op, RF455TutorialActionsHost& host) : Action(op,host),window(op.fixed[6]) {}
private:
    std::uint8_t window;
    bool start(RF455TutorialHost& other, RF455TutorialContext&) override {
        if (!bound(other)) return false;
        const int b = board(window);
        if (type == 19) {
            if (b >= 0) {
                host.openBoard(b,true);
                if (b == 0) host.selectInventoryPage(0,true);
                else if (b == 7 || b == 3) {
                    const auto w = host.boardWindow(b);
                    host.updateSkillTab(w,0,0,true); host.selectSkillTab(w,0);
                }
            } else if (window == 25) {
                RF455TutorialSlot slot;
                if (host.findUi25Item(slot)) host.useInventoryItem(slot); else host.localizedNotice(284);
            } else if (window == 27) host.showSpecialWindow(27);
            flags |= 4;
        } else if (type == 21) {
            if (b >= 0) host.closeBoard(b,true);
            else if (window == 25 || window == 27) host.closeSpecialWindow(window);
            flags |= 4;
        }
        return true;
    }
    bool update(RF455TutorialHost& other, RF455TutorialContext&) override {
        if (!bound(other) || (type != 20 && type != 22)) return false;
        const int b = board(window);
        bool open;
        if (b >= 0) open = host.boardOpen(b);
        else if (window == 25 || window == 27) open = host.specialWindowOpen(window);
        else return false;
        return type == 20 ? open : !open;
    }
    void finish(RF455TutorialHost&, RF455TutorialContext&) override {}
};

class Equip final : public Action {
public:
    Equip(const RF455TutorialInstruction& op, RF455TutorialActionsHost& host) : Action(op,host),slot(op.fixed[6]) {}
private:
    std::uint8_t slot;
    bool start(RF455TutorialHost& other, RF455TutorialContext&) override {
        if (!bound(other)) return false;
        if (type == 23) {
            if (slot != 255) {
                static const std::uint8_t map[16] = {5,1,2,6,4,8,7,3,9,9,10,10,11,11,11,46};
                if (slot >= 16) return false; // Invalid original table-index domain, not a completed command.
                BoardTemporary temporary(host); RF455TutorialSlot candidate;
                if (host.findEquipCandidate(temporary.object,map[slot],candidate)) host.equipFromInventory(candidate);
            }
            flags |= 4;
        } else if (type == 25) {
            host.unequipSlot(slot); if (slot == 12) host.unequipSlot(13); flags |= 4;
        }
        return true;
    }
    bool update(RF455TutorialHost& other, RF455TutorialContext&) override {
        if (!bound(other) || (type != 24 && type != 26) || slot == 255 || host.boardTransactionBusy()) return false;
        if (type == 24) return host.equipmentSlotPresent(slot);
        if (slot == 12) return !host.equipmentSlotPresent(12) && !host.equipmentSlotPresent(13);
        return !host.equipmentSlotPresent(slot);
    }
    void finish(RF455TutorialHost&, RF455TutorialContext&) override {}
};

class Cursor final : public Action {
public:
    Cursor(const RF455TutorialInstruction& op, RF455TutorialActionsHost& host)
        : Action(op,host),originX(signedWord(word(op.fixed,6))),originY(signedWord(word(op.fixed,8))),
          x(signedWord(word(op.fixed,10))),y(signedWord(word(op.fixed,12))),
          button(op.fixed[14]),window(op.fixed[15]),value(dword(op.fixed,16)) {}
private:
    std::int16_t originX,originY,x,y;
    std::uint8_t button,window;
    std::uint32_t value;
    bool start(RF455TutorialHost& other, RF455TutorialContext&) override {
        if (!bound(other)) return false;
        if (type == 29) {host.setGameInputEnabled(value); flags |= 4; return true;}
        if (type == 30) {host.showMouse(signedDword(value)); flags |= 4; return true;}
        if (type == 27 || type == 31) {
            if (value == 0xffffffff) {x=originX; y=originY;}
            else {
                x=y=0; const auto screen=host.screenSize();
                switch (value) {
                case 0:y=coordinate(screen[1],true);break;
                case 1:x=coordinate(screen[0]);y=coordinate(screen[1],true);break;
                case 2:x=coordinate(screen[0],true);y=coordinate(screen[1],true);break;
                case 3:x=coordinate(screen[0],true);break;
                case 4:x=coordinate(screen[0],true);y=coordinate(screen[1]);break;
                }
            }
        } else if (type == 28 || type == 32) {
            const auto point=host.cursorPoint(window,value==0xffffffff,value);
            if (!point.success) flags |= 4;
            // Target can read uninitialized local DWORD coordinates here.
            // A host must explicitly provide known values; no fabricated point.
            if (!point.initialized) return false;
            x=signedWord(std::uint16_t(point.point.x)); y=signedWord(std::uint16_t(point.point.y));
        } else if (type == 33) {
            const auto object=host.firstProjectionObject();
            if (!object) {flags |= 4;return true;}
            const auto projection=host.projectCursorPoint(host.objectPosition(object));
            if (projection.result<=0) {flags |= 4;return true;}
            x=coordinate(projection.x); y=coordinate(projection.y);
        }
        const RF455TutorialPoint point{x,y};
        if (type == 27 || type == 28) {
            if (x>=0 && y>=0) {
                auto absolute=point;
                if (host.cursorUsesWindowOrigin()) {
                    const auto origin=host.windowOrigin();
                    absolute={add(origin.x,x),add(origin.y,add(y,21))};
                }
                host.setSystemCursor(absolute); host.setLogicalCursor(point);
            } else host.startCursorMotion(point,button);
            flags |= 4;
        } else host.startCursorMotion(point,button);
        return true;
    }
    bool update(RF455TutorialHost& other, RF455TutorialContext&) override {
        if (!bound(other) || (type!=31 && type!=32)) return false;
        const auto point=host.logicalCursor(); return point.x==x && point.y==y;
    }
    void finish(RF455TutorialHost&, RF455TutorialContext&) override {}
};

class Combat final : public Action {
public:
    Combat(const RF455TutorialInstruction& op, RF455TutorialActionsHost& host) : Action(op,host) {
        params={op.fixed[6],dword(op.fixed,8),dword(op.fixed,12),dword(op.fixed,16)};
    }
    RF455TutorialCombatParameters parameters() const {return params;}
private:
    RF455TutorialCombatParameters params;
    bool start(RF455TutorialHost& other, RF455TutorialContext& context) override {
        if (!bound(other)) return false;
        if (type==35) {host.setCombatMode(params.attackType==1);flags|=4;}
        else if (type==37) {host.setCombatFlag24308(params.attackType!=0);flags|=4;}
        else if (type==39) params.attackType=255;
        context.operationActive=1; return true;
    }
    bool update(RF455TutorialHost& other, RF455TutorialContext& context) override {
        if (!bound(other)) return false;
        if (type==36) {
            host.traceLockOnWait(); const auto target=host.currentLockTarget();
            if (!target || host.targetType(target)!=params.targetTypeOrCount) return false;
            if (params.targetIndex==0xffffffff) return true;
            if (params.targetTypeOrCount==0)
                return (host.targetPlayerRace(target)>>1)==(std::uint8_t(params.targetIndex)/2);
            if (params.targetTypeOrCount==1) {
                std::uint32_t local;
                if (!host.resolveMonster(params.targetIndex,local)) return true;
                return local==host.targetLocalIndex(target);
            }
            return true;
        }
        if (type==38) {
            if (params.attackType!=context.attackType) return false;
            if (params.skillId==0xffffffff || params.attackType==4) return true;
            std::uint32_t code;
            return !host.attackSkillCode(params.attackType,context.skillIndex,code) || code==params.skillId;
        }
        return type==39 && context.state52>=params.targetTypeOrCount;
    }
    void finish(RF455TutorialHost&, RF455TutorialContext& context) override {
        if (type==38) {
            context.attackType=255;context.skillIndex=0xffffffff;context.target[0]=context.target[1]=0xffffffff;
        }
        context.operationActive=0;
    }
};

class Item final : public Action {
public:
    Item(const RF455TutorialInstruction& op, RF455TutorialActionsHost& host, RF455TutorialCreationIds& ids)
        : Action(op,host),ids(ids),qualifier(op.fixed[6]),index(dword(op.fixed,8)) {}
private:
    RF455TutorialCreationIds& ids;
    std::uint8_t qualifier;
    std::uint32_t index;
    bool start(RF455TutorialHost& other, RF455TutorialContext&) override {
        if (!bound(other)) return false;
        host.traceItemStart();
        if (type==40 || type==41) {
            ItemClone clone(host);
            std::uint32_t local;
            const auto category=type==41?std::uint8_t(18):qualifier;
            if (host.resolveItem(category,index,true,local)) {
                const auto item=host.createItem(0,category,local);
                if (!item) throw std::runtime_error("Tutorial item provider returned null");
                if (host.itemStackable(item)) host.setItemCount(item,200);
                else host.setItemValue(item,host.itemDefaultValue(item));
                host.setItemSerial(item,ids.item++);
                BoardTemporary temporary(host);
                host.attachBoardItem(temporary.object,item);
                host.setBoardSerial(temporary.object,host.itemSerial(item));
                const bool wasOpen=type==41?host.boardOpen(3):false;
                RF455TutorialSlot slot;
                if (host.findEmptyInventorySlot(slot)) {
                    host.insertInventory(slot,temporary.object);
                    if (type==41) {
                        host.useInventoryItem(slot); if (!wasOpen) host.closeBoard(3,true);
                    }
                }
            }
            flags|=4;
        } else if (type==43 || type==45) {
            const unsigned board=type==43?7:3;
            const auto object=host.boardFindIndex(board,index);
            if (object && !host.linkBoardContains(object)) {
                RF455TutorialSlot slot;
                if (host.findBoardItemSlot(board,host.boardItem(object),slot))
                    host.addHotbarLink(board,slot,255,255,false);
            }
            flags|=4;
        }
        return true;
    }
    bool update(RF455TutorialHost& other, RF455TutorialContext&) override {
        if (!bound(other)) return false;
        if (type==42) {
            const auto object=host.boardFindIndex(3,index);
            const auto item=object?host.boardItem(object):0;
            return item && host.itemField112(item)!=0;
        }
        if (type==44 || type==46) {
            const auto object=host.boardFindIndex(type==44?7:3,index);
            if (!host.linkBoardContains(object)) return false;
            if (qualifier==255) return true;
            const auto slot=host.hotbarObject(0,std::uint8_t(qualifier-1));
            return slot && host.boardIdentityEquals(slot,host.boardIdentity(object));
        }
        return false;
    }
    void finish(RF455TutorialHost&, RF455TutorialContext&) override {}
};
}

bool RF455_GetTutorialCombatParameters(const RF455TutorialProcessor& processor, RF455TutorialCombatParameters& out) {
    const auto* combat=dynamic_cast<const Combat*>(&processor);
    if (!combat) return false; out=combat->parameters(); return true;
}

std::unique_ptr<RF455TutorialProcessor> RF455TutorialActionsFactory::create(const RF455TutorialInstruction& op) {
    if (op.selector<19) return spatial.create(op);
    const auto size=op.fixed.size();
    if (op.selector<=22 && size==8) return std::unique_ptr<RF455TutorialProcessor>(new Ui(op,host));
    if (op.selector>=23 && op.selector<=26 && size==12) {
        if (op.dataType==23 && op.fixed[6]>=16 && op.fixed[6]!=255) return nullptr;
        return std::unique_ptr<RF455TutorialProcessor>(new Equip(op,host));
    }
    if (op.selector>=27 && op.selector<=34 && size==20) return std::unique_ptr<RF455TutorialProcessor>(new Cursor(op,host));
    if (op.selector>=35 && op.selector<=39 && size==20) return std::unique_ptr<RF455TutorialProcessor>(new Combat(op,host));
    if (op.selector>=40 && op.selector<=46 && size==12) return std::unique_ptr<RF455TutorialProcessor>(new Item(op,host,ids));
    return nullptr;
}
