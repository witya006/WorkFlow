"""Restore actual Character flag owner/death predicate and selected server writers."""
import re


def port_character_flags(raw,relative,section):
    def once(old,new):
        nonlocal raw
        if raw.count(old)!=1:raise ValueError('Character flags anchor '+relative+':'+repr(old))
        raw=raw.replace(old,new)
    if relative=='character/character/ccharacter.h':
        raw=b'#include "client455_character_flags.h"\r\n'+raw
        raw,n=re.subn(rb'(DWORD\s+m_dwActionID;)',rb'\1\r\n\tRF455CharacterFlags m_characterFlags455;',raw)
        if n!=1:raise ValueError('Character flag member')
        once(b'\tCCharacter();',b'\tCCharacter();\r\n\tvoid EnableCharacterFlags455(DWORD);\r\n\tvoid DisableCharacterFlags455(DWORD);\r\n\tvoid ToggleCharacterFlags455(DWORD,BOOL);\r\n\tDWORD CharacterFlags455()const{return m_characterFlags455.value;}\r\n\tDWORD CharacterFlagTime455()const{if(!m_characterFlags455.touchedKnown)throw std::logic_error("455 flag clock not supplied");return m_characterFlags455.touchedAt;}\r\n\tBOOL AnyCharacterFlags455(DWORD value)const{return m_characterFlags455.any(value);}\r\n\tBOOL NoneCharacterFlags455(DWORD value)const{return m_characterFlags455.none(value);}')
        return raw,True
    if relative=='character/character/ccharacter_etc.cpp':
        begin,end=section(raw,b'CCharacter::IsDeath( void )',b'CCharacter::IsDeath( void )')
        raw=raw[:begin]+b'CCharacter::IsDeath( void )\r\n{\r\n\treturn m_characterFlags455.blocked(m_dwActionID)?TRUE:FALSE;\r\n}\r\n'+raw[end:]
        return raw,True
    if relative=='character/player/cplayer.h':
        once(b'void ApplyStatusFlags455(',b'BOOL ApplyCharacterControlFlags455(ULONGLONG flags);\r\n\tvoid ApplyStatusFlags455(')
        return raw,True
    if relative=='character/player/cplayer.cpp':
        once(b'ApplyStatusFlags455(pi_dwFlag);',b'const BOOL wasBlocked455=ApplyCharacterControlFlags455(pi_dwFlag);\r\n\tApplyStatusFlags455(pi_dwFlag);')
        begin,end=section(raw,b'CPlayer::SetServerStatusFlag(',b'CPlayer::SetServerStatusFlag(');body=raw[begin:end]
        # Remove the two legacy action writers, which contradict the recovered
        # corpse/control-bit order and mining's !wasBlocked guard in455.
        body,n=re.subn(rb'\tif\( \( pi_dwFlag >> FLAG_CORPSE_STATE \) & 0x1 \)\s*\{.*?\n\t\}',b'\t// Corpse/control action writers use the recovered455 owner above.',body,flags=re.S)
        if n!=1:raise ValueError('Legacy corpse action writer')
        body,n=re.subn(rb'\tif\( \( pi_dwFlag >> FLAG_MINING_STATE \) & 0x1 \)\s*\{.*?\n\t\}',b'\tif((pi_dwFlag&(ULONGLONG(1)<<11))&&!wasBlocked455)SetAction(0x70000004,TRUE);',body,flags=re.S)
        if n!=1:raise ValueError('Legacy mining action writer')
        raw=raw[:begin]+body+raw[end:];return raw,True
    return raw,False
