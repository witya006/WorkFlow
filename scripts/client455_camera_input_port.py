"""Recover the ordinary right-drag camera limit without changing free-target mode."""
import re

from client455_trade_ore_port import patch_method, replace


def port_camera_input(raw, relative, section, native):
    if relative != 'gameprogress/cgp_maingame_processinput.cpp':
        return raw, False

    def right_drag_pitch(body):
        boundary = body.index(b'if( !m_bIsFreeTargetCombatMode && (gMouse.button & _MIDDLE_BUTTON_UP) )')
        branch, tail = body[:boundary], body[boundary:]
        clamp = rb'if\( _GetCamera\(\)->GetCameraMode\(\) != 2 \)\s*\{\s*if\( l_fViewAngleX < CAM_MIN_TH \)\s*l_fViewAngleX = CAM_MIN_TH;\s*\}\s*else\s*\{\s*if\( l_fViewAngleX < -89 \)\s*l_fViewAngleX = -89;\s*\}'
        branch, count = re.subn(clamp, b'if( l_fViewAngleX < -89 )\n\t\t\t\tl_fViewAngleX = -89;', branch)
        if count != 1:
            raise ValueError('Unexpected right-drag camera pitch branch')
        return branch + tail

    owner = b'CGP_MainGame'
    raw = patch_method(raw, section, owner, b'InputProcess_Mouse', right_drag_pitch)
    raw = patch_method(raw, section, owner, b'InputProcess', lambda body: replace(
        body, b'\t_GetUIMouseDev()->Update();',
        b'\tconst RF455CameraMouseObservation cameraInput;\n\t_GetUIMouseDev()->Update();'))
    raw = patch_method(raw, section, owner, b'ProcessMousePicking_Character', lambda body: replace(
        body, b'\tg_pPickedObjectID[0] = pi_pChar->GetCharTypeID();',
        b'''    if (RF455_WorldObservation().combat)
        RF455_ObserveProtocol("combat-pick", pi_pChar->GetCharTypeID(), pi_pChar->GetIndex(), pi_bIsByKeyboard);
\tg_pPickedObjectID[0] = pi_pChar->GetCharTypeID();'''))
    raw = patch_method(raw, section, owner, b'ProcessMousePicking_Character_Monster', lambda body: replace(
        body, b'\tif( m_bIsFreeTargetCombatMode )',
        b'''    if (RF455_WorldObservation().combat)
        RF455_ObserveProtocol("combat-monster-choice", _GetAvatar()->GetCombatMode(),
                             m_bIsFreeTargetCombatMode, _GetAvatar()->IsRequestChangeToCombatMode());
\tif( m_bIsFreeTargetCombatMode )'''))
    anchor = b'#include "CInputProcessMgr.h"'
    helper = (native / 'client455_camera_mouse_observation.inc').read_bytes()
    return replace(raw, anchor, anchor + b'\n#include "client455_protocol_observation.h"\n' + helper), True
