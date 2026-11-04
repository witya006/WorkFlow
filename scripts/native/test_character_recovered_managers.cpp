#include <winsock2.h>
#include "Character.h"
#include <cstdio>
#include <cstring>

// Test-only tripwires. The unresolved error helpers stay unresolved in the client
// until reconstructed; a call here fails this bounded ordinary-container test.
extern "C" __declspec(noreturn) void rf_unexpected_legacy_exception() {
    std::fputs("Unverified legacy exception path reached\n", stderr);
    ExitProcess(99);
}
#pragma comment(linker, "/alternatename:?_Xlen@std@@YAXXZ=_rf_unexpected_legacy_exception")
#pragma comment(linker, "/alternatename:?_Xran@std@@YAXXZ=_rf_unexpected_legacy_exception")

static int __cdecl suppress_interactive_faults() {
    SetErrorMode(SEM_FAILCRITICALERRORS | SEM_NOGPFAULTERRORBOX);
    return 0;
}
#pragma section(".CRT$XIB", read)
extern "C" __declspec(allocate(".CRT$XIB")) int (__cdecl* rf_test_fault_mode)() = suppress_interactive_faults;

static unsigned checks;
#define CHECK(condition) do { ++checks; if (!(condition)) { std::fprintf(stderr, "check %u at line %d failed\n", checks, __LINE__); return 1; } } while (0)
int main() {
    unsigned animation_checks = checks;
    {
        AnimationManager animations;
        CHECK(animations.legacy_begin == nullptr && animations.legacy_end == nullptr && animations.legacy_capacity == nullptr);
        CHECK(animations.unknown_010 == 0 && animations.legacy_next_id == 1);
        CHECK(animations.GetAnimationData(9999UL) == nullptr);
        char missing_animation[] = "missing";
        CHECK(animations.GetAnimationData(missing_animation) == nullptr);
        for (unsigned i = 0; i < 257; ++i) {
            char name[80], lower_name[80];
            std::sprintf(name, "Motion\\Clip_%u.ANI", i);
            std::sprintf(lower_name, "motion\\clip_%u.ani", i);
            CHECK(animations.AddAnimation(name)); // Registration only; no file load.
            ChAnimation* clip = animations.GetAnimationData(i + 1);
            CHECK(clip != nullptr && clip->m_Ident == i + 1 && clip->m_Load == 0);
            CHECK(std::strcmp(clip->m_Name, lower_name) == 0);
            CHECK(animations.GetAnimationData(name) == clip);
            CHECK(animations.GetAnimationID(name) == i + 1);
            CHECK(!animations.AddAnimation(name)); // Case-normalized duplicate.
        }
        CHECK(animations.legacy_end - animations.legacy_begin == 257);
        CHECK(animations.legacy_next_id == 258);
        // DeleteAnimation(char*) has a suspected lifetime bug in the original
        // decompilation. Do not exercise or silently repair it in this test.
        animations.DeleteAnimation2(101UL);
        CHECK(animations.GetAnimationData(101UL) == nullptr);
        CHECK(animations.legacy_end - animations.legacy_begin == 256);
        for (unsigned i = 1; i <= 257; ++i) {
            if (i != 101) CHECK(animations.GetAnimationData(i) != nullptr);
        }
    } // Actual SDK destructor releases all remaining unloaded animation records.
    animation_checks = checks - animation_checks;
    CObjectManager manager;
    CHECK(manager.legacy_begin == nullptr && manager.legacy_end == nullptr && manager.legacy_capacity == nullptr);
    CHECK(manager.legacy_next_id == 0 && manager.legacy_name[0] == 0);
    CHECK(manager.GetCharacter(99UL) == nullptr);
    // Avoid modern instantiations of the same STL types present in the old SDK:
    // matching COMDAT names could otherwise hide an ABI mismatch in the test.
    CHARACTEROBJECT* objects[257] = {};
    for (unsigned i = 0; i < 257; ++i) {
        auto object = new CHARACTEROBJECT{};
        std::sprintf(object->m_Name, "item_%u", i);
        manager.AddCharacter(object); // Actual supplied old function, not a model.
        objects[i] = object;
        CHECK(object->m_ID == i);
        CHECK(manager.GetCharacter(i) == object);
        CHECK(manager.GetCharacter(object->m_Name) == object);
        CHECK(manager.GetID(object->m_Name) == i);
    }
    CHECK(manager.legacy_end - manager.legacy_begin == 257);
    CHECK(manager.GetCharacter(99999UL) == nullptr);
    char missing[] = "does-not-exist", other_case[] = "ITEM_2";
    CHECK(manager.GetCharacter(missing) == nullptr && manager.GetCharacter(other_case) == nullptr);
    manager.DeleteCharacter(123UL);
    char by_name[] = "item_25";
    manager.DeleteCharacter(by_name);
    CHECK(manager.legacy_end - manager.legacy_begin == 255);
    CHECK(manager.GetCharacter(123UL) == nullptr && manager.GetCharacter(25UL) == nullptr);
    for (unsigned i = 0; i < 257; ++i) {
        if (i != 25 && i != 123) CHECK(manager.GetCharacter(i) == objects[i]);
    }
    manager.DeleteCharacter(99999UL);
    CHECK(manager.legacy_end - manager.legacy_begin == 255);
    auto extra = new CHARACTEROBJECT{};
    std::strcpy(extra->m_Name, "extra");
    manager.AddCharacter(extra);
    CHECK(extra->m_ID == 257);
    manager.Clear(); // Actual old clear/destructor paths with unloaded objects.
    CHECK(manager.legacy_begin == manager.legacy_end);
    CHECK(manager.legacy_next_id == 258);
    auto reused = new CHARACTEROBJECT{};
    std::strcpy(reused->m_Name, "reused");
    manager.AddCharacter(reused);
    CHECK(reused->m_ID == 258 && manager.GetCharacter(258UL) == reused);
    std::printf("{\"checks_passed\":%u,\"object_manager_checks\":%u,\"animation_manager_checks\":%u,\"objects_added\":259,\"animations_added\":257,\"unverified_exception_paths_called\":false}\n", checks, checks-animation_checks, animation_checks);
    // The real old destructor releases the final object and vector storage.
    return 0;
}
