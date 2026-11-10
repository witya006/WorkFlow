"""Restore actual455 MobControl and its required shared movement dependency."""
def port_mob_control(raw,relative,native):
    root='userinterface/gamewindow/recall/guimobcontrol'
    if relative==root+'.h':return b'#pragma once\n#include "client455_mob_control.h"\n',True
    if relative==root+'.cpp':return b'''#include "GUIMobControl.h"
#include "../../SpriteMgr.h"
#include "../../GUIController/GUITooltip.h"
#include "client455_language.h"
#include "client455_nation_paths.h"
#include <algorithm>
#include <cmath>
#include <cstdio>
#include <cstring>
#include <stdexcept>
'''+(native/'client455_mob_control.inc').read_bytes(),True
    if relative=='userinterface/uiglobal.h':
        a=raw.index(b'struct MoveObjectInfo');b=raw.index(b'typedef list< MoveObjectInfo * >',a)
        raw=raw[:a]+b'''struct MoveObjectInfo {
    CGUIObject* pObject;int nInitPos,nLastPos,nMidPos;MoveAxis eAxis;
    DWORD dwMoveStartTime,dwVelocity;float fInitialVelocity,fAcceleration;
    BYTE byWaveCnt,byCurWaveCnt;WORD wMaxWaveLength;BOOL bIsFinished;
};

'''+raw[b:]
        needle=b'\tvoid\tFrameMove( void );';assert raw.count(needle)==1
        extra=b'''\n    void AddMoveObject455(CGUIObject*,MoveAxis,int,int,float,float,BYTE=0,WORD=10);
    void StartMoveAt455(CGUIObject*,DWORD);
    void FrameMoveAt455(DWORD);
'''
        return raw.replace(needle,needle+extra),True
    if relative=='userinterface/uiglobal.cpp':
        start=raw.index(b'CGUIMoveObjectMgr::CGUIMoveObjectMgr()');end=raw.index(b'g_cMoveObjectMgr;',start)+len(b'g_cMoveObjectMgr;')
        # Remove the preceding return-type-free constructor start through the
        # single ordinary manager instance. Earlier avatar/filter code survives.
        return b'#include <cmath>\n#include <stdexcept>\n'+raw[:start]+(native/'client455_gui_move.inc').read_bytes()+raw[end:],True
    return raw,False
