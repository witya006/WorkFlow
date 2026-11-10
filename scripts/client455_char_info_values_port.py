"""Restore full-width ordinary stat writers,keeping whole455UI acceptance open."""
import re

def port_char_info_values(raw,relative,section,native):
    def once(old,new):
        nonlocal raw
        if raw.count(old)!=1:raise ValueError('CharInfo values anchor '+relative+':'+repr(old))
        raw=raw.replace(old,new)
    if relative=='userinterface/gamewindow/guicharinfowindow.h':
        once(b'SetGenAttackFc( WORD pi_wMinGenAttackFc, WORD pi_wMaxGenAttackFc )',b'SetGenAttackFc( DWORD minimum, DWORD maximum )')
        once(b'SetForceAttackFc( WORD pi_wMinForceAttackFc, WORD pi_wMaxForceAttackFc )',b'SetForceAttackFc( DWORD minimum, DWORD maximum )')
        once(b'SetDeffenceFc( WORD pi_wDefFc )',b'SetDeffenceFc( DWORD value )')
        once(b'SetHitRate( WORD pi_wHitRate ){;}',b'SetHitRate( float value );')
        once(b'SetAvoidRate( WORD pi_wAvoidRate ){;}',b'SetAvoidRate( float value );')
        once(b'CGUIText* GetInfoValue455(BYTE slot){return slot<23?&m_uiInfoValues455[slot]:NULL;}',b'''CGUIText* GetInfoValue455(BYTE slot){return slot<23?&m_uiInfoValues455[slot]:NULL;}
    //The ordinary window's existing basic-stat rows now reference the recovered
    //value owners. Their legacy coordinates are temporary,not455layout proof.
    CGUIText& ValueForLegacySlot455(unsigned slot){
        if(slot==GenAttPower)return m_uiInfoValues455[14];
        if(slot==FcAttPower)return m_uiInfoValues455[15];
        if(slot==Deffense)return m_uiInfoValues455[16];
        return m_uiCharInfo[slot];
    }''')
        return raw,True
    if relative!='userinterface/gamewindow/guicharinfowindow.cpp':return raw,False
    for sig in [b'CGUICharInfoWindow::SetGenAttackFc( WORD',b'CGUICharInfoWindow::SetForceAttackFc( WORD',b'CGUICharInfoWindow::SetDeffenceFc( WORD']:
        first,last=section(raw,sig,sig)
        start=raw.rfind(b'void',0,first)
        if raw[start:first].strip()!=b'void':raise ValueError('Stat setter return type boundary')
        raw=raw[:start]+b'//Full-width455 setter is defined below.\n'+raw[last:]
    raw,count=re.subn(rb'm_uiCharInfo\[([^\]\r\n]+)\]',lambda m:b'ValueForLegacySlot455('+m[1]+b')',raw)
    if count!=24:raise ValueError('CharInfo value consumer count changed:'+str(count))
    raw=b'#include <cmath>\n#include <cstdio>\n#include <cstring>\n'+raw
    raw+=b'\n'+(native/'client455_char_info_values.inc').read_bytes()
    return raw,True
