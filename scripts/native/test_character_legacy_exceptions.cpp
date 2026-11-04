#include <windows.h>
#include <stdexcept>
#include <cstdio>
#include <cstring>

namespace std {
__declspec(noreturn) void __cdecl _Xlen();
__declspec(noreturn) void __cdecl _Xran();
}
using Helper = void (__cdecl*)();
static unsigned checks, destroyed;
struct Guard { ~Guard() { ++destroyed; } };
#define CHECK(c) do { ++checks; if (!(c)) { std::fprintf(stderr, "check %u line %d failed\n", checks, __LINE__); return 1; } } while (0)

int main() {
    SetErrorMode(SEM_FAILCRITICALERRORS | SEM_NOGPFAULTERRORBOX);
    HMODULE baseline = LoadLibraryExW(L"msvcp60.dll", nullptr, LOAD_LIBRARY_SEARCH_SYSTEM32);
    CHECK(baseline != nullptr);
    FARPROC addresses[] = {GetProcAddress(baseline, "?_Xlen@std@@YAXXZ"),
                          GetProcAddress(baseline, "?_Xran@std@@YAXXZ")};
    Helper classic[2];
    CHECK(addresses[0] != nullptr && addresses[1] != nullptr);
    std::memcpy(classic, addresses, sizeof(classic));
    Helper recovered[] = {std::_Xlen, std::_Xran};
    const char* messages[] = {"string too long", "invalid string position"};
    for (unsigned round = 0; round < 64; ++round) {
        for (unsigned which = 0; which < 2; ++which) {
            Helper functions[] = {classic[which], recovered[which]};
            for (Helper fn : functions) {
                bool caught = false;
                unsigned before = destroyed;
                try {
                    Guard outer;
                    try { Guard inner; fn(); }
                    catch (const std::logic_error& error) {
                        CHECK(std::strcmp(error.what(), messages[which]) == 0);
                        throw; // Verify cross-frame rethrow and destructor execution.
                    }
                } catch (const std::length_error& error) {
                    CHECK(which == 0 && std::strcmp(error.what(), messages[which]) == 0);
                    caught = true;
                } catch (const std::out_of_range& error) {
                    CHECK(which == 1 && std::strcmp(error.what(), messages[which]) == 0);
                    caught = true;
                } catch (...) { CHECK(false); }
                CHECK(caught && destroyed == before + 2);
            }
        }
    }
    const auto dos = reinterpret_cast<const IMAGE_DOS_HEADER*>(baseline);
    const auto nt = reinterpret_cast<const IMAGE_NT_HEADERS32*>(reinterpret_cast<const char*>(baseline)+dos->e_lfanew);
    std::printf("{\"checks_passed\":%u,\"guard_destructors\":%u,\"provider_timestamp\":%lu,\"provider_image_size\":%lu}\n",
        checks, destroyed, nt->FileHeader.TimeDateStamp, nt->OptionalHeader.SizeOfImage);
    // Keep the provider mapped until process shutdown; no remaining exception objects.
    return 0;
}
