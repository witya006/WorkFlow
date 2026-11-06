#include "client455_font_settings.h"
#include <cstring>
namespace { RF455FontSettings settings={"\xb1\xbc\xb8\xb2\xc3\xbc","\xb1\xbc\xb8\xb2\xc3\xbc",9,12,129,949}; }
int RF455_SetFontParameters(const char* name,int points,int height,int charset){
    // 8C5A80 copies250bytes into each256byte global,leaving the final6 intact.
    std::strncpy(settings.name,name,250);
    std::strncpy(settings.defaultName,name,250);
    settings.points=points;settings.height=height;settings.charset=charset;
    return points;
}
void RF455_SetFontCodePage(unsigned value){settings.codepage=value;}
const RF455FontSettings& RF455_GetFontSettings(){return settings;}
