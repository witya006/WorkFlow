#include "character_legacy_stdio.h"
#include <windows.h>
#include <cstring>
#include <cstdlib>

static_assert(sizeof(void*) == 4, "This adapter is for the supplied x86 VC6 objects");

namespace {
HMODULE classic_crt() {
    // Streams can survive until old atexit handlers. Keep the provider for process lifetime.
    static HMODULE module = []() {
        HMODULE loaded = LoadLibraryExW(L"msvcrt.dll", nullptr, LOAD_LIBRARY_SEARCH_SYSTEM32);
        if (!loaded) std::abort();
        return loaded;
    }();
    return module;
}

template<class Function> Function resolve(const char* name) {
    FARPROC address = GetProcAddress(classic_crt(), name);
    if (!address) std::abort();
    Function result;
    static_assert(sizeof(result) == sizeof(address), "Win32 function pointer representation");
    std::memcpy(&result, &address, sizeof(result));
    return result;
}
}

extern "C" RF_LegacyFile* __cdecl rf_vc6_fopen(const char* path, const char* mode) {
    static auto function = resolve<RF_LegacyFile*(__cdecl*)(const char*, const char*)>("fopen");
    return function(path, mode);
}
extern "C" int __cdecl rf_vc6_fclose(RF_LegacyFile* stream) {
    static auto function = resolve<int(__cdecl*)(RF_LegacyFile*)>("fclose");
    return function(stream);
}
extern "C" char* __cdecl rf_vc6_fgets(char* out, int capacity, RF_LegacyFile* stream) {
    static auto function = resolve<char*(__cdecl*)(char*, int, RF_LegacyFile*)>("fgets");
    return function(out, capacity, stream);
}
extern "C" std::size_t __cdecl rf_vc6_fread(void* out, std::size_t size, std::size_t count, RF_LegacyFile* stream) {
    static auto function = resolve<std::size_t(__cdecl*)(void*, std::size_t, std::size_t, RF_LegacyFile*)>("fread");
    return function(out, size, count, stream);
}
extern "C" std::size_t __cdecl rf_vc6_fwrite(const void* data, std::size_t size, std::size_t count, RF_LegacyFile* stream) {
    static auto function = resolve<std::size_t(__cdecl*)(const void*, std::size_t, std::size_t, RF_LegacyFile*)>("fwrite");
    return function(data, size, count, stream);
}
extern "C" int __cdecl rf_vc6_fseek(RF_LegacyFile* stream, long offset, int origin) {
    static auto function = resolve<int(__cdecl*)(RF_LegacyFile*, long, int)>("fseek");
    return function(stream, offset, origin);
}
extern "C" long __cdecl rf_vc6_ftell(RF_LegacyFile* stream) {
    static auto function = resolve<long(__cdecl*)(RF_LegacyFile*)>("ftell");
    return function(stream);
}

extern "C" FARPROC __cdecl rf_vc6_fscanf_target() {
    static auto function = resolve<FARPROC>("fscanf");
    return function;
}
// The classic DLL has fscanf but no vfscanf. Preserve the caller's full cdecl
// argument stack and tail-jump to the genuine implementation. No format emulation.
extern "C" __declspec(naked) int __cdecl rf_vc6_fscanf(RF_LegacyFile*, const char*, ...) {
    __asm {
        push ebp
        mov ebp, esp
        call rf_vc6_fscanf_target
        mov esp, ebp
        pop ebp
        jmp eax
    }
}
