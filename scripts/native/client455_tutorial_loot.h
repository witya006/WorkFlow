#pragma once

#include "client455_tutorial_spatial.h"

class RF455TutorialInventory;

class RF455TutorialLoot {
public:
    RF455TutorialLoot();
    ~RF455TutorialLoot();
    bool spawn(std::uint8_t table, std::uint32_t code, const RF455TutorialVector& position);
    bool empty() const { return drops.empty(); }
    void pointAt(long x, long y, const RF455TutorialVector& camera);
    void clearHover() { hovered = nullptr; }
    bool pickHovered(RF455TutorialInventory&);
    bool pickNearest(RF455TutorialInventory&);
    void render();
    void clear();
private:
    struct Drop;
    std::vector<std::unique_ptr<Drop>> drops;
    Drop* hovered = nullptr;
    bool collect(Drop*, RF455TutorialInventory&);
};
