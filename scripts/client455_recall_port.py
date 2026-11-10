"""Replace the legacy Recall window/rows with typed455 source owners."""
def port_recall(raw,relative,native):
    root='userinterface/gamewindow/recall/guirecallwindow'
    if relative==root+'.h':return b'#pragma once\n#include "client455_recall_window.h"\n',True
    if relative!=root+'.cpp':return raw,False
    return b'''#include "GUIRecallWindow.h"
#include "../../SpriteMgr.h"
#include "../../GUIController/GUIScreen.h"
#include "client455_language.h"
#include "client455_modal.h"
#include <algorithm>
#include <cmath>
#include <cstdio>
#include <cstring>
#include <stdexcept>
'''+(native/'client455_recall_window.inc').read_bytes(),True
