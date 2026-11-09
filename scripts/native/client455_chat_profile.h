#pragma once
#include <windows.h>
#include <array>
#include <cstddef>

struct RF455ChatFont {BYTE size=0,padding[3]={};DWORD style=0,color=0xffffffff;float scale=1;};
struct RF455ChatPrefix {WORD length=0;char text[16]={};};
static_assert(sizeof(RF455ChatFont)==16&&offsetof(RF455ChatFont,color)==8&&sizeof(RF455ChatPrefix)==18,"455 chat records");

// Source owner for the confirmed font/prefix part of the MainGame chat manager.
// The target's process font singleton16 and map/tree private ABI are not overlaid.
class RF455ChatProfile {
public:
    RF455ChatProfile();~RF455ChatProfile();
    RF455ChatProfile(const RF455ChatProfile&)=delete;
    RF455ChatProfile&operator=(const RF455ChatProfile&)=delete;
    bool Load(unsigned nation,const char* explicitPath=nullptr);
    void Release();
    bool Ready()const{return ready;}
    const RF455ChatFont& Header(unsigned style)const{return header.at(style);}
    const RF455ChatFont& Body(unsigned style)const{return body.at(style);}
    const RF455ChatPrefix& Prefix(unsigned style)const{return prefixes.at(style);}
    unsigned ScriptRecords()const{return scriptRecords;}
    unsigned FallbackRecords()const{return fallbackRecords;}
private:
    void fallback(unsigned,unsigned nation);
    void prefix(unsigned,const char*);
    std::array<RF455ChatFont,36> header,body;
    std::array<RF455ChatPrefix,36> prefixes;
    bool ready=false;unsigned scriptRecords=0,fallbackRecords=0;
};
RF455ChatProfile* RF455_GetChatProfile();
