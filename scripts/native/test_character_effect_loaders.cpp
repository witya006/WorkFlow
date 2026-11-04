#include <winsock2.h>
#include "Character.h"
#include <cstdio>
#include <cstring>

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
    // Positive effect state through the actual old binary effect loader and map
    // application. Texture strings are empty: CPU effects only, without a GPU.
    char effect_list[] = "effects.txt", effect_file[] = "EFFECT_A.EFF";
    g_EFFMonList.LoadEffectFileList(effect_list);
    CHECK(g_EFFMonList.legacy_present[1] == 1);
    CHECK(std::strcmp(g_EFFMonList.legacy_files[1],effect_file)==0);
    ObjectMesh meshes[2]; // Genuine old constructor, not modern layout substitutes.
    // The supplied constructor leaves +160 untouched, while its destructor frees
    // it. Our synthetic meshes have no blends: establish explicit ownership state.
    // This is fixture setup, not a silent change to the SDK constructor.
    for (auto& mesh : meshes) mesh.m_pMatBlend = nullptr;
    CHARACTEROBJECT character{};
    character.m_MaxObj = 2;
    character.m_pMesh = meshes;
    EffectObjectManager::SetPartEffect(&character,effect_file,9); // Baseline, bypass bridge.
    for (auto& mesh : meshes) CHECK(mesh.m_ParticleID[0].m_ID == 17);
    for (auto& mesh : meshes) mesh.m_ParticleID[0].m_ID = 0;
    g_EFFMonList.SetEffect(&character,1);
    for (auto& mesh : meshes) CHECK(mesh.m_ParticleID[0].m_ID == 17);
    g_EFFMonList.SetEffect(&character,499); // Absent table entry.
    for (auto& mesh : meshes) CHECK(mesh.m_ParticleID[0].m_ID == 17);
    g_EFFMonList.SetEffect(&character,500); // Owned bridge's bounded domain.
    g_EFFMonList.SetEffect(&character,0xffffffffUL);
    for (auto& mesh : meshes) CHECK(mesh.m_ParticleID[0].m_ID == 17);
    g_EFFMonList.SetEffect(nullptr,1); // Actual SDK tolerates null character.
    std::printf("{\"checks_passed\":%u,\"actual_old_file_loaders\":4,\"mesh_effects_applied\":2,\"render_device_used\":false}\n", checks);
    std::fflush(stdout);
    return 0;
}
