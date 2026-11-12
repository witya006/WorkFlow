#pragma once
#include "client455_tutorial_runtime.h"
#include <map>
#include <windows.h>

class CLinkBoard;
class CSFBoard;
class CBoardObject;
class RF455SkillForceItem;
class RF455TutorialInventory;

class RF455TutorialSkills {
public:
    RF455TutorialSkills();
    ~RF455TutorialSkills();
    void initialize(bool forceLesson);
    void shutdown();
    void show(bool visible);
    bool isOpen() const;
    bool skillPoint(DWORD code, POINT&);
    bool shortcutPoint(DWORD number, POINT&);
    bool matchesShortcut(BYTE number, DWORD code);
    bool hasBeacon(DWORD code) const;
    bool installBeacon(RF455TutorialInventory&, BYTE slot);
    RF455SkillForceItem* readyForce(DWORD index);
    void activateShortcut(BYTE slot);
    RF455SkillForceItem* shortcutSkill(BYTE bank, BYTE slot);
    bool handleMessage(UINT message, WPARAM owner, LPARAM data, RF455TutorialInventory&);

private:
    std::unique_ptr<CSFBoard> skills;
    std::unique_ptr<CLinkBoard> shortcuts;
    std::map<DWORD, std::unique_ptr<CBoardObject>> beacons;
    CBoardObject* held = nullptr;
    bool force = false;

    CBoardObject* findSkill(DWORD code);
    void pick(CBoardObject*);
    void cancelPick();
    bool bind(BYTE bank, BYTE slot, CBoardObject*);
    bool returnBeacon(RF455TutorialInventory&, CBoardObject*, BYTE slot = 255);
};
