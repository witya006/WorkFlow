"""Own tagged audio service in the ordinary client; legacy engine remains intact."""


def port_tagged_audio(raw,relative,section):
    if relative=='mainapp.h':
        raw=b'#include "client455_tagged_audio.h"\r\n'+raw
        old=b'RF455IconLinks m_iconLinks455;'
        if raw.count(old)!=1:raise ValueError('Tagged audio owner boundary')
        raw=raw.replace(old,old+b'\r\n\tRF455TaggedAudio m_taggedAudio455;')
        old=b'RF455IconLinks& IconLinks455(){return m_iconLinks455;}'
        if raw.count(old)!=1:raise ValueError('Tagged audio API boundary')
        raw=raw.replace(old,old+b'\r\n\tRF455TaggedAudio& TaggedAudio455(){return m_taggedAudio455;}')
        return raw,True
    if relative=='mainapp.cpp':
        old=b'InitR3SoundSystem('
        if raw.count(old)!=1:raise ValueError('Tagged audio search before Miles startup')
        raw=raw.replace(old,b'RF455_PrepareTaggedAudio(GetR3State()->SoundPath);\r\n\t'+old)
        start,end=section(raw,b'CMainApp::Create(',b'CMainApp::Create(')
        body=raw[start:end];old=b'm_cLand.Create();'
        if body.count(old)!=1:raise ValueError('Tagged audio Create boundary')
        body=body.replace(old,b'if(!m_taggedAudio455.Open(".\\\\Snd\\\\WaveList.spt",GetR3State()->SoundPath))return FALSE;\r\n\t'+old)
        raw=raw[:start]+body+raw[end:]
        start,end=section(raw,b'CMainApp::Destroy(',b'CMainApp::Destroy(');at=raw.index(b'{',start)+1
        raw=raw[:at]+b'\r\n\tm_taggedAudio455.Close();'+raw[at:]
        return raw,True
    return raw,False
