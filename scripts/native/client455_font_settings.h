#pragma once
struct RF455FontSettings {
    char name[256],defaultName[256];
    int points,height,charset;
    unsigned codepage;
};
int RF455_SetFontParameters(const char* name,int points,int height,int charset);
void RF455_SetFontCodePage(unsigned);
const RF455FontSettings& RF455_GetFontSettings();
