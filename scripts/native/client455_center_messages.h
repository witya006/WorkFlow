#pragma once
#include <windows.h>
#include <cstddef>
#include <list>

struct RF455CenterChunk {char text[60];DWORD color;};
struct RF455CenterLine {
    float x=0,y=0;
    char text[60];
    DWORD color=0xffffffff,time=0;
    float scale=1,alpha=0;
};
static_assert(sizeof(RF455CenterChunk)==64&&sizeof(RF455CenterLine)==84
    &&offsetof(RF455CenterLine,color)==68&&offsetof(RF455CenterLine,time)==72
    &&offsetof(RF455CenterLine,scale)==76&&offsetof(RF455CenterLine,alpha)==80,"455 center records");

// Equivalent source owner; modern STL storage does not claim the old list24 ABI.
// Its lifetime is the ordinary MainGame member lifetime, including before Create.
class RF455CenterMessages {
public:
    RF455CenterMessages();~RF455CenterMessages();
    RF455CenterMessages(const RF455CenterMessages&)=delete;
    RF455CenterMessages&operator=(const RF455CenterMessages&)=delete;
    void Add(const char*,DWORD);
    void FrameMove();
    // Same update kernel with the captured time/delta supplied explicitly.
    // Promoted records still obtain their own real timeGetTime, as in455.
    void FrameMoveAt(DWORD capturedTime,float loopTime);
    void Draw()const;
    void Clear();
    const std::list<RF455CenterChunk>& Pending()const{return pending;}
    const std::list<RF455CenterLine>& Active()const{return active;}
private:
    void appendActive(const char*,DWORD);
    std::list<RF455CenterChunk> pending;
    std::list<RF455CenterLine> active;
};
RF455CenterMessages* RF455_GetCenterMessages();
