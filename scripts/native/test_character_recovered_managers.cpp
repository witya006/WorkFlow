#include <winsock2.h>
#include "Character.h"
#include <cstdio>
#include <cstring>

static int __cdecl suppress_interactive_faults() {
    SetErrorMode(SEM_FAILCRITICALERRORS | SEM_NOGPFAULTERRORBOX);
    return 0;
}
#pragma section(".CRT$XIB", read)
extern "C" __declspec(allocate(".CRT$XIB")) int (__cdecl* rf_test_fault_mode)() = suppress_interactive_faults;

static unsigned checks;
#define CHECK(condition) do { ++checks; if (!(condition)) { std::fprintf(stderr, "check %u at line %d failed\n", checks, __LINE__); return 1; } } while (0)
int main() {
    for (unsigned repetition=0; repetition<8; ++repetition) {
        ChInterface render;
        CHECK(&CRender::GetRender() == static_cast<CRender*>(&render));
        CHECK(render.legacy_device == nullptr && render.m_TM.legacy_device == nullptr);
        CHECK(render.m_TM.legacy_next_id == 1 && render.m_TM.unknown_014 == 0);
        CHECK(render.m_TM.legacy_begin == nullptr && render.m_TM.legacy_end == nullptr && render.m_TM.legacy_capacity == nullptr);
        CHECK(render.m_TM.legacy_mip_skip == 0 && render.m_TM.legacy_path[0] == 0);
        CHECK(render.legacy_shadow_surface == nullptr);
        for (auto shadow : render.legacy_shadow) CHECK(shadow == nullptr);
        D3DLIGHT8 light;
        std::memcpy(&light, reinterpret_cast<const char*>(&render)+8, sizeof(light));
        CHECK(light.Type == D3DLIGHT_DIRECTIONAL && light.Diffuse.r == 0.8f);
        CHECK(light.Ambient.r == 1.0f && light.Specular.r == 0.0f && light.Direction.z == -1.0f);
        CHECK(render.m_TM.GetTextureID("missing.dds") == 0);
        render.SetMipMap(repetition%4);
        CHECK(render.m_TM.legacy_mip_skip == repetition%4);
        CHARACTEROBJECT object{};
        char texture_path[] = ".\\character\\texture";
        render.SetTexPath(&object, texture_path);
        CHECK(std::strcmp(object.legacy_texture_path,texture_path)==0);
        render.InitCharacter(nullptr); // No D3D device or file loading.
        for (unsigned i=0; i<17; ++i) {
            char name[40];
            // The original lookup uppercases its query, while AddPartToMM stores
            // the supplied name verbatim. Use the SDK's uppercase naming domain.
            std::sprintf(name,"PART_%u",i);
            render.AddPartToMM(name); // Real SDK allocation/vector growth.
            CObjectManager* part = render.legacy_parts.GetObjectManager(name);
            CHECK(part != nullptr && std::strcmp(part->legacy_name,name)==0);
            CHECK(part->legacy_begin == part->legacy_end && part->legacy_next_id == 0);
        }
        CHECK(render.legacy_parts.legacy_end-render.legacy_parts.legacy_begin == 17);
        // Real old CRender destructor releases shadows/managers/part allocations.
    }
    const unsigned render_checks = checks;
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
    std::printf("{\"checks_passed\":%u,\"object_manager_checks\":%u,\"animation_manager_checks\":%u,\"render_construction_checks\":%u,\"objects_added\":259,\"animations_added\":257,\"render_instances\":8,\"part_managers_added\":136,\"unverified_exception_paths_called\":false}\n", checks, checks-animation_checks-render_checks, animation_checks, render_checks);
    // The real old destructor releases the final object and vector storage.
    return 0;
}
