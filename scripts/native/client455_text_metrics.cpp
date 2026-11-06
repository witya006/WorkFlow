#include "client455_text_metrics.h"
#include "client455_font.h"
#include "client455_language.h"
#include <cstring>
#include <string>

long RF455_TextWidth(const char* text,std::uint16_t bytes){
    if(!text||!bytes)return 0;
    if(bytes==0xffff)return RF455_MeasureTextAnsi(text).cx;
    const auto length=std::strlen(text);
    if(!length)return 0;
    if(bytes>=length)return RF455_MeasureTextAnsi(text).cx;
    // Target uses strncpy into a shared scratch buffer and can cut a DBCS pair.
    // Preserve the exact byte prefix, not a decoded Unicode substring.
    const std::string prefix(text,bytes);
    return RF455_MeasureTextAnsi(prefix.c_str()).cx;
}

int RF455_TextFitBytes(const char* text,int maximumWidth){
    if(!text)return 0; // Target requires a valid pointer; invalid domain OPEN.
    int count=RF455_FitTextAnsi(text,maximumWidth);
    if(count&&RF455_GetNormalLanguagePack()->isLead(text,count-1))--count;
    return count;
}

int RF455_DefaultTextHeight(){
    static bool initialized=false;static int height=0;
    if(!initialized){height=RF455_MeasureTextAnsi("").cy;initialized=true;}
    return height; // Target7B2630 retains the first measured value across reloads.
}
