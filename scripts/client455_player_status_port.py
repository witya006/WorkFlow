"""Restore the confirmed player status producer/getter without changing originals."""
import re


def port_player_status(raw,relative,section):
    if relative=='character/player/cplayer.h':
        raw=b'#include "client455_player_status.h"\r\n'+raw
        raw,count=re.subn(rb'(CPlayer \*\s*m_pLinkPlayer;)',rb'\1\r\n\tRF455PlayerStatus m_status455;',raw)
        if count!=1:raise ValueError('Player status member boundary')
        anchor=b'\tCPlayer();'
        if raw.count(anchor)!=1:raise ValueError('Player status API boundary')
        raw=raw.replace(anchor,anchor+b'\r\n\tvoid ApplyStatusFlags455(ULONGLONG flags){m_status455.apply(flags);}\r\n\tvoid SetStatusCode455(DWORD code){m_status455.set(code);}\r\n\tDWORD GetStatusCode455()const{return m_status455.get();}')
        raw,count=re.subn(rb'SetServerStatusFlag\( DWORD pi_dwFlag \)',b'SetServerStatusFlag( ULONGLONG pi_dwFlag )',raw)
        if count!=1:raise ValueError('Player full-width status declaration')
        return raw,True
    if relative=='character/player/cplayer.cpp':
        old=b'CPlayer::SetServerStatusFlag( DWORD pi_dwFlag )'
        if raw.count(old)!=1:raise ValueError('Player full-width status definition')
        raw=raw.replace(old,b'CPlayer::SetServerStatusFlag( ULONGLONG pi_dwFlag )')
        start,end=section(raw,b'CPlayer::SetServerStatusFlag(',b'CPlayer::SetServerStatusFlag(')
        at=raw.index(b'{',start)+1
        raw=raw[:at]+b'\r\n\tApplyStatusFlags455(pi_dwFlag);'+raw[at:]
        return raw,True
    return raw,False
