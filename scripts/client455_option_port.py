"""Migrate actual455 options owners and messages;keep legacy backend gaps explicit."""
import re

def port_option(raw,relative,native):
    root='userinterface/gamewindow/etcwin/guioptionwindow'
    if relative == 'gameobject/manager/ccharactermgr.cpp':
        raw, count = re.subn(
            rb'(CCharacterMgr::SetVisualFieldAdjustmentLevel\( BYTE pi_byLevel \)\s*\{)',
            rb'\1\n\tif (pi_byLevel < 1) pi_byLevel = 1;\n\telse if (pi_byLevel > MAX_VISUALFIELD_ADJUSTMENT_LEVEL) pi_byLevel = MAX_VISUALFIELD_ADJUSTMENT_LEVEL;',
            raw)
        if count != 1:
            raise ValueError('Manual visual field level anchor changed')
        start = raw.index(b'CCharacterMgr::EnableAutoVisualFieldAdjustment(')
        end = raw.index(b'CCharacterMgr::SetVisualFieldAdjustmentLevel(', start)
        body = raw[start:end]
        anchor = b'm_bIsEnableAutoVisualFieldAdjustment = pi_bFlag;'
        if body.count(anchor) != 1:
            raise ValueError('Automatic visual field state anchor changed')
        body = body.replace(anchor, anchor + b'''
    if (pi_bFlag) {
        // The constructor starts at MAX; recover invalid state explicitly before clamping.
        if (!std::isfinite(m_fVisualField)) m_fVisualField = MAX_VISUAL_FIELD;
        else if (m_fVisualField < MIN_VISUAL_FIELD) m_fVisualField = MIN_VISUAL_FIELD;
        else if (m_fVisualField > MAX_VISUAL_FIELD) m_fVisualField = MAX_VISUAL_FIELD;
    }''')
        return b'#include <cmath>\n' + raw[:start] + body + raw[end:], True
    if relative == 'gameprogress/cgp_maingame.cpp':
        # The old stage initialized backend owners but left these widgets at defaults.
        # Keep the settings transaction's initial snapshot aligned with those owners.
        start = raw.index(b'CGP_MainGame::LoadGameSetting(')
        end = raw.index(b'CGP_MainGame::SaveGameSetting(', start)
        body = raw[start:end]
        old_default = b'"VisualFieldAdjustmentLevel", 5, l_pFileName'
        if body.count(old_default) != 1:
            raise ValueError('Manual visual field default anchor changed')
        body = body.replace(old_default, b'"VisualFieldAdjustmentLevel", 4, l_pFileName')
        changes = [
            (b'_GetCharMgr()->EnableAutoVisualFieldAdjustment( l_nIntValue );',
             b'\n\t_GetOptionWindow()->SwitchOn(CGUIOptionWindow::AutoSeeDist, l_nIntValue);'),
            (b'_GetCharMgr()->SetVisualFieldAdjustmentLevel( l_nIntValue );',
             b'\n\t_GetOptionWindow()->SetGraphicOption(CGUIOptionWindow::SeeDist, float(_GetCharMgr()->GetVisualFieldAdjustmentLevel()));'),
            (b'_GetCamera()->SetCameraMode( l_nIntValue );',
             b'\n\t_GetOptionWindow()->SelectCamera(BYTE(_GetCamera()->GetCameraMode()));'),
            (b'm_pHintMgr->EnableRenderHint( l_nIntValue );',
             b'\n\t_GetOptionWindow()->SwitchOn(CGUIOptionWindow::Hint, m_pHintMgr->IsRenderHint());'),
        ]
        for old, addition in changes:
            if body.count(old) != 1:
                raise ValueError('Settings initial state anchor changed: ' + old.decode())
            body = body.replace(old, old + addition)
        raw = raw[:start] + body + raw[end:]
        for getter in (b'GetGlobalMusicVolume()', b'GetGlobalWavVolume()'):
            old = b'sprintf( l_pBuf, "%.1f", ' + getter + b' );'
            if raw.count(old) != 1:
                raise ValueError('Saved sound volume precision anchor changed')
            raw = raw.replace(old, b'sprintf( l_pBuf, "%.4f", ' + getter + b' );')
        return raw, True
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
