#pragma once
#include "client455_tutorial_runtime.h"
#include <windows.h>

class CLinkBoard;
class CSkillBoard;
class CBoardObject;

class RF455TutorialSkills {
public:
    RF455TutorialSkills();
    ~RF455TutorialSkills();
    void initialize();
    void shutdown();
    void show(bool visible);
    bool isOpen() const;
    bool skillPoint(DWORD code, POINT&);
    bool shortcutPoint(DWORD number, POINT&);
    bool matchesShortcut(BYTE number, DWORD code);
    bool handleMessage(UINT message, WPARAM owner, LPARAM data);

private:
    std::unique_ptr<CSkillBoard> skills;
    std::unique_ptr<CLinkBoard> shortcuts;
    CBoardObject* held = nullptr;

    CBoardObject* findSkill(DWORD code);
    void pick(CBoardObject*);
    void cancelPick();
    bool bind(BYTE bank, BYTE slot, CBoardObject*);
};
