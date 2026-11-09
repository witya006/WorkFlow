#pragma once
#include <windows.h>
class CBoardObject;
struct RF455BoardHoverState;
BOOL RF455_IsOwnBoardObject455(CBoardObject*);
void RF455_RequireHoverCancellation();

inline bool RF455_ForwardsBoardAdd455(BYTE id){
    return id<16||id==35||id==36||id==38||id==39;
}
