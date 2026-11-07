#pragma once
#include "userinterface/guicontroller/guiobject.h"
#include <cstdint>

#pragma pack(push,4)
struct RF455GuiTimerState {
    DWORD duration,startedAt,elapsedOffset,started;
    double remaining;
    float angle;
};
#pragma pack(pop)
static_assert(sizeof(RF455GuiTimerState)==28,"455 selected timer fields96..123");
struct RF455TimerLabel {DWORD color;POINT offset;BYTE unit;float scale;};
DWORD RF455_TimerLabel455(DWORD milliseconds,BYTE context,RF455TimerLabel&);
using RF455TimerTriangleSink=void(*)(void*,const _D3DR3TLVERTEX_TEX1*);

// Source-owned CGUIObject child;no overlay/cast of the private target208-byte ABI.
class RF455GuiTimer:public CGUIObject {
    RF455GuiTimerState state;
    _D3DR3TLVERTEX_TEX1 vertices[3];
public:
    RF455GuiTimer();
    RF455GuiTimerState& State455(){return state;}
    const RF455GuiTimerState& State455()const{return state;}
    const _D3DR3TLVERTEX_TEX1* Vertices455()const{return vertices;}
    void Reset455();
    void Start455(LONG elapsed=-1);
    BOOL IsStarted455()const{return static_cast<BOOL>(state.started);}
    void Update()override;
    BOOL Draw()override;
    BOOL Draw(RECT&)override;
    BOOL DrawWithSink455(RF455TimerTriangleSink,void*,const RECT* =nullptr);
};
