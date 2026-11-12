#pragma once
#include <windows.h>

class CGameProgress;
CGameProgress* RF455_CreateTutorialStage();
void RF455_DeliverTutorialDialog(CGameProgress&, WORD id, DWORD result);
void RF455_ReceiveTutorialDialog(WORD id, DWORD result);
void RF455_CaptureTutorialFrame455();
