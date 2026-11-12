#pragma once
#include "client455_tutorial_spatial.h"
#include <memory>

class CMonster;
class CGUISelectedMobInfoWin;

class RF455TutorialTargets {
public:
    RF455TutorialTargets();
    ~RF455TutorialTargets();
    bool spawn(std::uint32_t code, const RF455TutorialVector& position);
    bool select(long x, long y, const RF455TutorialVector& camera);
    bool hasSelection() const;
    void clearSelection();
    void update();
    void render();
    void shutdown();

private:
    std::vector<std::unique_ptr<CMonster>> monsters;
    std::unique_ptr<CGUISelectedMobInfoWin> window;
    CMonster* selected = nullptr;
};
