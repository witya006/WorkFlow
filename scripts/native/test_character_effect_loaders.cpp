#include <winsock2.h>
#include "Character.h"
#include <cstdio>

static int __cdecl suppress_interactive_faults() {
    SetErrorMode(SEM_FAILCRITICALERRORS | SEM_NOGPFAULTERRORBOX);
    return 0;
}
#pragma section(".CRT$XIB", read)
extern "C" __declspec(allocate(".CRT$XIB")) int (__cdecl* rf_effect_fault_mode)() = suppress_interactive_faults;

static unsigned checks;
#define CHECK(c) do { ++checks; if (!(c)) { std::fprintf(stderr, "check %u line %d failed\n", checks, __LINE__); return 1; } } while (0)
int main() {
    // Own bounded fixtures, consumed by the actual old SDK loaders. Globals and
    // their storage/constructors belong to the old library, not modern STL.
    char patterns[] = "patterns.txt", items[] = "items.txt";
    g_PatternList.LoadEffectPatternList(patterns);
    g_EffectItemList.LoadItemListFile(items);
    CHARACTEROBJECT object{};
    for (DWORD grade = 0; grade < 9; ++grade) {
        const bool expected = (grade % 2) == 0;
        CHECK(IsHaveMeshEffect(&object, 0x10203040UL, grade) == expected);
        CHECK(IsHaveMeshEffect(&object, 0x10203040UL, grade, 0) == expected);
        CHECK(!IsHaveMeshEffect(&object, 0x10203040UL, grade, 5));
        CHECK(!IsHaveMeshEffect(&object, 0x55667788UL, grade));
        CHECK(IsHaveMeshEffect(&object, 0xabcdef01UL, grade) == expected);
        // Effect-file flags remain empty: no device, texture or mesh is loaded.
        SetMeshEffect(&object, 0x10203040UL, grade);
    }
    CHECK(!IsHaveMeshEffect(&object, 0x10203040UL, 9));
    CHECK(!IsHaveMeshEffect(&object, 0x10203040UL, 0xffffffffUL));
    CHECK(!IsHaveMeshEffect(&object, 0xffffffffUL, 0));
    CHECK(object.m_Load == 0 && object.m_MaxObj == 0 && object.m_pMesh == nullptr);
    std::printf("{\"checks_passed\":%u,\"actual_old_file_loaders\":2,\"render_device_used\":false}\n", checks);
    return 0;
}
