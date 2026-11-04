#pragma once
#include <cstddef>
// Opaque classic CRT stream. It must never be passed to modern CRT FILE APIs.
struct RF_LegacyFile;
extern "C" {
RF_LegacyFile* __cdecl rf_vc6_fopen(const char*, const char*);
int __cdecl rf_vc6_fclose(RF_LegacyFile*);
char* __cdecl rf_vc6_fgets(char*, int, RF_LegacyFile*);
std::size_t __cdecl rf_vc6_fread(void*, std::size_t, std::size_t, RF_LegacyFile*);
std::size_t __cdecl rf_vc6_fwrite(const void*, std::size_t, std::size_t, RF_LegacyFile*);
int __cdecl rf_vc6_fseek(RF_LegacyFile*, long, int);
long __cdecl rf_vc6_ftell(RF_LegacyFile*);
int __cdecl rf_vc6_fscanf(RF_LegacyFile*, const char*, ...);
}
