#pragma once
#include "userinterface/guicontroller/guiitem.h"
#include <array>

// The banked icon owner of the actual window. The complete target window's
// controls/layout and private ABI are separate, still-required migration work.
class RF455LinkerIconSlots {
    std::array<CGUIItem,50> icons;
    float scale=1;
public:
    void SetScale455(float value){scale=value;}
    LONG Size455()const{return static_cast<LONG>(double(scale)*38);}
    CGUIItem* get(BYTE bank,BYTE slot){return bank<5&&slot<10?&icons[10*bank+slot]:nullptr;}
    BOOL takeIn(BYTE bank,BYTE slot,CGUIItem* source);
    BOOL takeOut(BYTE bank,BYTE slot);
};
