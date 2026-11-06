#pragma once
#include <cstdint>

struct RF455NationDescriptor {
    const char* setting;const char* folder;const char* crtLocale;
    const char* font;unsigned charset;
};
struct RF455NationPaths {
    std::uint16_t nation=0xffff;bool configured=false;
    char folder[32]={},dataRoot[260]={};
};
// Only nation mapping/path publication. Full ETCAction factories, CRT/font/
// NDLanguage initialization remain distinct, unfinished startup contracts.
std::uint16_t RF455_MapNation(const char*);
const RF455NationDescriptor& RF455_NationDescriptor(unsigned);
bool RF455_ReadNationPaths(const char* ini,RF455NationPaths*);
RF455NationPaths* RF455_GetNormalNationPaths();
const char* RF455_GetClientDataRoot();
int RF455_InitializeNationPaths();
