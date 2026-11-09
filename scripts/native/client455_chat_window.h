#pragma once
#include <windows.h>
#include <string>

struct RF455ChatWindowState {
    DWORD filters[4][14]={};
    BYTE currentPane=0xff;
    bool initialized=false;
};
