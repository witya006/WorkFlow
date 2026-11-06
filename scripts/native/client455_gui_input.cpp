#include "client455_gui_input.h"
#include <mmsystem.h>
namespace {RF455GuiInputClock inputClock=nullptr;RF455GuiKeyState keyState=nullptr;}
RF455GuiInputClock RF455_SetGuiInputClock(RF455GuiInputClock clock){auto previous=inputClock;inputClock=clock;return previous;}
RF455GuiKeyState RF455_SetGuiKeyState(RF455GuiKeyState provider){auto previous=keyState;keyState=provider;return previous;}
DWORD RF455_GuiInputTime(){return inputClock?inputClock():timeGetTime();}
SHORT RF455_GuiKeyState(int key){return keyState?keyState(key):GetKeyState(key);}
BYTE RF455_ProcessKeyScan(LPARAM flags){
    //6271E0 uses the entire arithmetic high half,not a masked scan byte.
    const LONG scan=static_cast<LONG>(flags)>>16;
    if(scan>=16&&scan<=25)return static_cast<BYTE>("QWERTYUIOP"[scan-16]);
    if(scan>=30&&scan<=38)return static_cast<BYTE>("ASDFGHJKL"[scan-30]);
    if(scan>=44&&scan<=50)return static_cast<BYTE>("ZXCVBNM"[scan-44]);
    return 0xff;
}
