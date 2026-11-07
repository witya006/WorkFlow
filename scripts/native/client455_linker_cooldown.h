#pragma once
#include <windows.h>
#include <array>
#include <list>
class CBoardObject;
class RF455GuiAnimation;
#pragma pack(push,4)
struct RF455LinkerCooldownRecord {
    BYTE bank;
    CBoardObject* object;
    DWORD startedAt,elapsedOffset,duration;
    RF455LinkerCooldownRecord():object(nullptr),startedAt(0),elapsedOffset(0),duration(0){}
};
#pragma pack(pop)
static_assert(sizeof(RF455LinkerCooldownRecord)==20,"455 selected cooldown record");
struct RF455LinkerCooldownState {
    std::array<RF455LinkerCooldownRecord,50> records;
    std::list<RF455GuiAnimation*> pending;
};
DWORD& RF455_SFDelayGate455();
