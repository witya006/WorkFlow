"""Port ordinary effect scheduling/lifecycle and render-pass selection."""


def port_effect_runtime(raw, relative, native, section):
    def once(old, new):
        nonlocal raw
        if raw.count(old) != 1:
            raise ValueError('Effect runtime anchor '+relative+':'+repr(old))
        raw = raw.replace(old, new)

    if relative == 'addcodebyjang/effectcore.h':
        once(b'void DeleteMagicList(DWORD id);', b'void DeleteMagicList(DWORD id,BOOL force=FALSE);')
        raw += b'\r\nWORD GetEffectQuality455();\r\nvoid ApplyEffectOption455(BOOL enable,WORD option);\r\nvoid RenderOpaqueEffects455();\r\nvoid RenderAlphaEffects455();\r\n'
        return raw, True
    if relative != 'addcodebyjang/effectcore.cpp':
        return raw, False
    once(b'#define _MAX_EFFECT_CNT\t256', b'#define _MAX_EFFECT_CNT\t512')
    raw = b'#include <stdexcept>\r\n'+raw
    start, end = section(raw, b'void StartEffect(float mat[4][4]', b'void StartEffect(float mat[4][4]')
    body = raw[start:end]
    marker = b'DeleteEffectList(0);'
    if body.count(marker) != 1:
        raise ValueError('Effect eviction boundary')
    body = body.replace(marker, b'if((stEffectList[0].mFlag&_MT_FLAG_PARTICLE)&&stEffectList[0].mParticle){stEffectList[0].mParticle->ReleaseParticle();delete stEffectList[0].mParticle;stEffectList[0].mParticle=NULL;}\r\n\t\t'+marker)
    raw = raw[:start]+body+raw[end:]
    start, end = section(raw, b'BOOL SetDisapearTimeEffect(', b'BOOL SetDisapearTimeEffect(')
    raw = raw[:start]+(native/'client455_effect_disappear.inc').read_bytes()+raw[end:]
    start, end = section(raw, b'void DeleteMagicList(', b'void DeleteMagicList(')
    raw = raw[:start]+b'''void DeleteMagicList(DWORD id,BOOL force){
    if(!stMLcnt)return;
    for(DWORD j=0;j<stMagicList[id].mEntityUniqueIDCnt;++j)
        SetDisapearTimeEffect(stMagicList[id].mEntityUniqueID[j],force?-1.0f:0.0f);
    memcpy(&stMagicList[id],&stMagicList[id+1],sizeof(CMagicList)*(stMLcnt-id-1));--stMLcnt;
}
'''+raw[end:]
    start, end = section(raw, b'DWORD StartMagicEffect(float mat[4][4]', b'DWORD StartMagicEffect(float mat[4][4]')
    body = raw[start:end]
    first = b'if( stMLcnt > _MAX_MAGIC_EFFECT_CNT-1 )'
    at, stop = section(body, first, first)
    body = body[:at]+b'if(stMLcnt>=256){DeleteMagicList(0,TRUE);stMLcnt=255;}'+body[stop:]
    raw = raw[:start]+body+raw[end:]
    start, end = section(raw, b'static void FrameMoveEffectsList()', b'static void FrameMoveEffectsList()')
    body = raw[start:end]
    marker = b'delete particle;'
    if body.count(marker) != 1:
        raise ValueError('Particle completion boundary')
    body = body.replace(marker, b'particle->ReleaseParticle();\r\n\t\t\t\t'+marker)
    raw = raw[:start]+body+raw[end:]
    start, end = section(raw, b'static void FrameMoveMagicEffects()', b'static void FrameMoveMagicEffects()')
    raw = raw[:start]+(native/'client455_effect_schedule.inc').read_bytes()+raw[end:]
    start, end = section(raw, b'void RenderAllEffectsList()', b'void RenderAllEffectsList()')
    raw = raw[:start]+(native/'client455_effect_passes.inc').read_bytes()+raw[end:]
    return raw, True
