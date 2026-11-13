"""Restore the455 actor's BSP color/material/light consumer in owned sources."""


def port_actor_lighting(raw,relative,native,section):
    if relative=='cresobject.h':
        old=b'BOOL\t\t\tm_bIsHide;'
        if raw.count(old)!=1:raise ValueError('Actor blink DWORD field anchor')
        raw=raw.replace(old,b'DWORD\t\t\tm_dwBlinkColor455;')
        old=b'void\tSetBlink( BOOL pi_bIsBlink );'
        if raw.count(old)!=1:raise ValueError('Actor blink public API anchor')
        raw=raw.replace(old,old+b'\n\tvoid SetBlink455(BOOL enabled,DWORD color);')
        return raw,True
    if relative=='cresobject.cpp':
        first,last=section(raw,b'CResObject::SetLightColorFromMap(',b'CResObject::SetLightColorFromMap(')
        #section begins after the separately-written return type.
        replacement=(native/'client455_actor_lighting.inc').read_bytes()
        include=b'#include "client455_enhanced_lighting.h"\n'
        replacement=replacement.replace(b'\r\n',b'\n')
        if replacement.startswith(include):replacement=replacement[len(include):]
        if not replacement.startswith(b'void '):raise ValueError('Actor light return type')
        raw=raw[:first]+replacement[5:]+raw[last:]
        raw=raw.replace(b'm_bIsHide',b'm_dwBlinkColor455')
        raw=b'#include <stdexcept>\n'+include+raw
        return raw,True
    return raw,False
