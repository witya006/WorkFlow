"""Migrate actual455 options owners and messages;keep legacy backend gaps explicit."""
import re

def port_option(raw,relative,native):
    root='userinterface/gamewindow/etcwin/guioptionwindow'
    if relative==root+'.h':return b'#pragma once\n#include "client455_option_window.h"\n',True
    if relative==root+'.cpp':return b'''#include "GUIOptionWindow.h"
#include "../../SpriteMgr.h"
#include "../../GUIController/GUIScreen.h"
#include "../../../DefineMessage.h"
#include "client455_language.h"
#include "client455_nation_paths.h"
#include "client455_font.h"
#include <algorithm>
#include <cmath>
#include <cstdio>
#include <stdexcept>
'''+(native/'client455_option_window.inc').read_bytes(),True
    if relative=='definemessage.h':
        values={'WM_OPTION_TOGGLE_HINT':0x200,'WM_OPTION_TOGGLE_AUTO_VF_ADJUST':0x201,'WM_OPTION_CHANGE_VF_DIST':0x206,'WM_OPTION_CHANGE_CAMERA_MODE':0x208,'WM_OPTION_ADJUST_EFFECT_SOUND':0x209,'WM_OPTION_ADJUST_BGM_SOUND':0x210,'WM_OPTION_ADJUST_GAMMA':0x211,'WM_OPTION_ADJUST_DYNAMIC_LIGHTING':0x212,'WM_OPTION_ADJUST_SHADOW':0x213}
        for name,value in values.items():
            pattern=rb'(#define[ \t]+'+name.encode()+rb'[ \t]+)\([^\r\n]+\)';raw,count=re.subn(pattern,lambda m:m[1]+f'( WM_USER + 0x{value:04X} )'.encode(),raw);assert count==1,name
        # Both producers andconsumers of these0.7-only internal messages use the
        # same macro. Preserve their action,avoid interpreting455Party asdetail
        # texture or455BGM as a keyboard-failure request to quit. These private
        # adapter IDs are NOT asserted to be the original455message contracts.
        for name,value in [('WM_OPTION_DETAIL_TEXTURE',0x203),('WM_EXIT_KEYBOARD_MACRO',0x210)]:
            pattern=rb'(#define[ \t]+'+name.encode()+rb'[ \t]+)\([^\r\n]+\)';raw,count=re.subn(pattern,lambda m:m[1]+f'( WM_APP + 0x{value:04X} )'.encode(),raw);assert count==1,name
        return raw,True
    return raw,False
