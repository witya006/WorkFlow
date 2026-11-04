#include "Character.h"
#include <cstdio>
#include <cstring>

// Machine-ABI leaf-method probe on guarded storage, without constructing or
// pretending to initialize a renderer. Only our newly compiled methods execute.
// This is a byte-write/thiscall contract check, not a live C++ renderer test.
using PathFunction = void (__thiscall*)(void*, CHARACTEROBJECT*, char*);
using MipFunction = void (__thiscall*)(void*, DWORD);
static unsigned checks;
#define CHECK(c) do { ++checks; if (!(c)) { std::fprintf(stderr,"check %u line %d failed\n",checks,__LINE__); return 1; } } while (0)
int main() {
    auto path_member = &ChInterface::SetTexPath;
    auto mip_member = &CRender::SetMipMap;
    PathFunction set_path;
    MipFunction set_mip;
    static_assert(sizeof(path_member) == sizeof(set_path), "x86 single-inheritance method pointer");
    static_assert(sizeof(mip_member) == sizeof(set_mip), "x86 single-inheritance method pointer");
    std::memcpy(&set_path, &path_member, sizeof(set_path));
    std::memcpy(&set_mip, &mip_member, sizeof(set_mip));
    alignas(4) unsigned char storage[sizeof(CRender)+32];
    unsigned char expected[sizeof(storage)];
    const DWORD values[] = {0,1,2,3,4,0x80000000UL,0xffffffffUL};
    for (DWORD value : values) {
        std::memset(storage, 0xa5, sizeof(storage));
        std::memcpy(expected, storage, sizeof(storage));
        std::memcpy(expected+16+offsetof(CRender,m_TM)+offsetof(TextureManager,legacy_mip_skip), &value, 4);
        set_mip(storage+16, value);
        CHECK(std::memcmp(storage,expected,sizeof(storage))==0);
    }
    const unsigned lengths[] = {0,1,10,127,128,254,255,256,600};
    char source[601];
    for (unsigned length : lengths) {
        std::memset(source, 'Q', length);
        source[length] = 0;
        std::memset(storage, 0xa5, sizeof(storage));
        std::memcpy(expected, storage, sizeof(storage));
        // Independently specify affected bytes, padding and untouched byte 255.
        for (unsigned i=0; i<255; ++i)
            expected[16+offsetof(CHARACTEROBJECT,legacy_texture_path)+i] = i<length ? 'Q' : 0;
        set_path(storage+16, reinterpret_cast<CHARACTEROBJECT*>(storage+16), source);
        CHECK(std::memcmp(storage,expected,sizeof(storage))==0);
    }
    std::memset(storage, 0xa5, sizeof(storage));
    std::memcpy(expected, storage, sizeof(storage));
    set_path(storage+16, reinterpret_cast<CHARACTEROBJECT*>(storage+16), nullptr);
    CHECK(std::memcmp(storage,expected,sizeof(storage))==0);
    set_path(storage+16, nullptr, nullptr); // Source guard precedes destination use.
    CHECK(std::memcmp(storage,expected,sizeof(storage))==0);
    std::printf("{\"checks_passed\":%u,\"renderer_constructed\":false,\"probe\":\"leaf machine ABI on guarded storage\"}\n", checks);
}
