"""Own the confirmed aiming core in MainApp and update it in ordinary game frames."""


def port_nuclear_aiming(raw,relative,native,section):
    def once(old,new):
        nonlocal raw
        if raw.count(old)!=1:raise ValueError('Nuclear anchor '+relative+':'+repr(old))
        raw=raw.replace(old,new)
    if relative=='mainapp.h':
        raw=b'#include "client455_nuclear_aiming.h"\r\n'+raw
        once(b'RF455TaggedAudio m_taggedAudio455;',b'RF455TaggedAudio m_taggedAudio455;\r\n\tRF455NuclearAiming m_nuclearAiming455;')
        once(b'RF455TaggedAudio& TaggedAudio455(){return m_taggedAudio455;}',b'RF455TaggedAudio& TaggedAudio455(){return m_taggedAudio455;}\r\n\tRF455NuclearAiming& NuclearAiming455(){return m_nuclearAiming455;}')
        return raw,True
    if relative=='mainapp.cpp':
        once(b'm_taggedAudio455.Close();',b'm_nuclearAiming455.Clear();\r\n\tm_taggedAudio455.Close();')
        return raw,True
    if relative=='addcodebyjang/foreffect.cpp':
        raw=b'#include "client455_nuclear_aiming.h"\r\n'+raw
        once(b'FrameMoveAllEffectsList();',b'RF455_NuclearAiming().FrameMove();\r\n\tFrameMoveAllEffectsList();')
        return raw,True
    if relative=='addcodebyjang/effectcore.cpp':
        start,end=section(raw,b'BOOL MovePosMagicEffect(',b'BOOL MovePosMagicEffect(')
        raw=raw[:start]+(native/'client455_magic_move.inc').read_bytes()+raw[end:]
        return raw,True
    return raw,False
