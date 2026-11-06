#include "client455_text_metrics.h"
#include "client455_font.h"
#include "userinterface/guicontroller/guitext.h"
#include <algorithm>
#include <vector>

namespace {
bool registryAlive=false;
struct Pending {
    std::vector<CGUIText*> objects;
    Pending(){registryAlive=true;}
    ~Pending(){registryAlive=false;}
};
Pending& pending(){static Pending owner;return owner;}
void recalculate(CGUIText& text){
    const LONG width=RF455_TextWidth(text.GetString());
    const WORD cells=static_cast<WORD>(width/12);
    const DWORD style=text.GetFont()->dwStyle;
    if(style&0x80000000)text.SetSize(8*cells,16);
    if(style&0x40000000)text.SetSize(16*cells,32);
    else text.SetSize(width,RF455_DefaultTextHeight());
}
void flush(){
    if(!registryAlive||!RF455_TextResourcesReady())return;
    std::vector<CGUIText*> ready;ready.swap(pending().objects);
    for(auto* object:ready)recalculate(*object);
}
}

void RF455_UpdateGuiTextSize(CGUIText* text){
    // Legacy0.7 creates some UI strings in static constructors. The455 font
    // contract requires a live backend; defer those owned geometry requests
    // until font creation instead of reading an unconstructed provider or
    // poisoning the target's first-height cache with a made-up value.
    if(RF455_TextResourcesReady()){recalculate(*text);return;}
    auto& list=pending().objects;
    if(std::find(list.begin(),list.end(),text)==list.end())list.push_back(text);
    RF455_SetTextReadyCallback(flush);
}
void RF455_ForgetGuiText(CGUIText* text){
    if(!registryAlive)return;
    auto& list=pending().objects;list.erase(std::remove(list.begin(),list.end(),text),list.end());
}
