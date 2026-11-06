#pragma once
#include <windows.h>
typedef DWORD (*RF455GuiInputClock)();
typedef SHORT (*RF455GuiKeyState)(int key);
RF455GuiInputClock RF455_SetGuiInputClock(RF455GuiInputClock clock);
RF455GuiKeyState RF455_SetGuiKeyState(RF455GuiKeyState provider);
DWORD RF455_GuiInputTime();
SHORT RF455_GuiKeyState(int key);
BYTE RF455_ProcessKeyScan(LPARAM flags);
