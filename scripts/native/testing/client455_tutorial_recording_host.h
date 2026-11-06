#pragma once
#include "client455_tutorial_spatial.h"
#include <stdexcept>
#include <string>
#include <vector>
inline void RF455_TutorialTestCheck(bool ok,const char* why){if(!ok)throw std::runtime_error(why);}
template<class Interface = RF455TutorialSpatialHost>
struct RF455TutorialRecordingSpatialHost : Interface {
    std::uint32_t now = 0, pending = 0, clocks = 0;
    RF455TutorialVector position{{0,0,0}}, target{}, orbit{}, relative{};
    float yaw = 0, parameter = 0;
    unsigned markers = 0, releases = 0, turns = 0, cursor = 0;
    bool toggle = false, monsterFound = true, itemFound = true, cloneActive = false;
    std::vector<std::string> calls;
    std::vector<std::array<std::uint8_t,17>> monsters;
    std::vector<std::array<std::uint8_t,25>> items;
    bool skipTutorial() override {return false;}
    bool boardBusy() override {return false;}
    std::uint32_t milliseconds() override {++clocks; return now;}
    void resetCursorButton() override {++cursor;}
    void questRefreshed() override {}
    void scriptCompleted() override {}
    void message(std::uint8_t, const RF455TutorialMessage*, std::uint16_t) override {}
    RF455TutorialWaitState waitState(std::uint32_t) override {return {};}
    void setAvatarPosition(const RF455TutorialVector& p, bool first, bool second) override {
        RF455_TutorialTestCheck(first && !second, "position args"); position = p; calls.push_back("set-position");
    }
    void setAvatarYaw(float y, bool first, float speed) override {
        RF455_TutorialTestCheck(first && speed == 12, "yaw args"); yaw = y; calls.push_back("set-yaw");
    }
    void setCameraOrbit(const RF455TutorialVector& p, bool dirty) override {
        RF455_TutorialTestCheck(dirty, "camera dirty"); orbit = p; calls.push_back("orbit");
    }
    void animateCameraOrbit(const RF455TutorialVector& p) override {relative = p; calls.push_back("relative");}
    void setCameraParameter276(float p) override {parameter = p; calls.push_back("parameter276");}
    RF455TutorialVector avatarPosition() override {calls.push_back("position"); return position;}
    float avatarX() override {calls.push_back("x"); return position[0];}
    float avatarY() override {calls.push_back("y"); return position[1];}
    float avatarZ() override {calls.push_back("z"); return position[2];}
    float avatarYaw() override {calls.push_back("yaw"); return yaw;}
    void createAvatarPath(const RF455TutorialVector& p) override {target = p; calls.push_back("path");}
    void turnAvatarToward(RF455TutorialVector& p, bool first, float speed) override {
        RF455_TutorialTestCheck(first && speed == 12, "facing args"); target = p; ++turns; calls.push_back("face");
    }
    void avatarState(std::uint32_t state, bool enable) override {
        RF455_TutorialTestCheck(state == 0x10000001 && enable, "move state"); calls.push_back("state");
    }
    void avatarToggle(bool value, bool second) override {RF455_TutorialTestCheck(!second, "toggle second"); toggle = value;}
    std::uint32_t placeMarker(const RF455TutorialVector&, float a, std::uint32_t color, int b, int c) override {
        RF455_TutorialTestCheck(a == 0 && color == 1358954291U && b == 0 && c == 0, "marker args"); ++markers; return 123;
    }
    void releaseMarker(std::uint32_t marker, float value) override {
        RF455_TutorialTestCheck(marker == 123 && value == 1, "release marker"); ++releases;
    }
    bool resolveMonster(std::uint32_t index, std::uint32_t& result) override {
        RF455_TutorialTestCheck(index == 77, "monster DT index"); result = 0x12345; return monsterFound;
    }
    void beginItemClone() override {RF455_TutorialTestCheck(!cloneActive,"clone nesting"); cloneActive = true; calls.push_back("item-construct");}
    bool resolveItem(std::uint8_t, std::uint32_t index, bool clone, std::uint32_t& result) override {
        RF455_TutorialTestCheck(index == 77 && clone && cloneActive, "item lookup"); calls.push_back("item-resolve"); result = 0x12345; return itemFound;
    }
    void endItemClone() override {RF455_TutorialTestCheck(cloneActive,"clone already ended"); cloneActive = false; calls.push_back("item-destruct");}
    void localMonsterSpawn(const std::array<std::uint8_t,17>& p) override {monsters.push_back(p);}
    void localItemSpawnKnown25(const std::array<std::uint8_t,25>& p) override {
        RF455_TutorialTestCheck(cloneActive,"clone lifetime through local dispatch"); items.push_back(p); calls.push_back("item-dispatch");
    }
    std::uint32_t pendingCreations() override {return pending;}
};
