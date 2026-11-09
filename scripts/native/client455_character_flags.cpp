#include "gameobject/manager/ccharactermgr.h"
#include "gameobject/board/common/cboardmanager.h"
#include "cland.h"
#include "ccamera.h"
#include "datafile.h"
#include "datatable/cresourcedatamgr.h"
#include "input/imeedit.h"
#include "gameprogress/cgameprogress.h"
#include "userinterface/spritemgr.h"
#include "mainapp.h"
#include "client455_character_flags.h"
#include <mmsystem.h>

namespace {std::uint32_t clock455(){return timeGetTime();}}
void CCharacter::EnableCharacterFlags455(DWORD mask){m_characterFlags455.enable(mask,clock455);}
void CCharacter::DisableCharacterFlags455(DWORD mask){m_characterFlags455.disable(mask);}
void CCharacter::ToggleCharacterFlags455(DWORD mask,BOOL on){m_characterFlags455.toggle(mask,on!=FALSE,clock455);}
BOOL CPlayer::ApplyCharacterControlFlags455(ULONGLONG flags){
    return m_characterFlags455.applyServer(flags,[this](){return m_dwActionID;},
        [this](std::uint32_t action,bool duplicate){SetAction(action,duplicate);},clock455)?TRUE:FALSE;
}
