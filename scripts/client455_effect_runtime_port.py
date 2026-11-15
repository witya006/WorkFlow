"""Port ordinary effect scheduling, cache lifecycle, and render-pass selection."""

import re


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
    once(b'#define _MAX_MAGIC_CACHE_SIZE\t256', b'#define _MAX_MAGIC_CACHE_SIZE\t512')
    once(b'#include "Cjcache.h"', b'')
    raw, replaced = re.subn(rb'static CJcache stMagicCache;[^\r\n]*\r?\n', b'', raw)
    if replaced != 1:
        raise ValueError('Magic cache owner boundary')
    once(b'return stMagicCache.GetCacheCnt();', b'return static_cast<DWORD>(stMagicCache.size());')
    raw = (b'#include <cstdio>\r\n#include <cstring>\r\n#include <list>\r\n#include <memory>\r\n'
           b'#include <new>\r\n#include <stdexcept>\r\n#include <utility>\r\n'+raw)
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
    raw = raw[:start]+b'''void DeleteMagicList(DWORD id, BOOL force)
{
    if (id >= stMLcnt) return;
    for (DWORD j = 0; j < stMagicList[id].mEntityUniqueIDCnt; ++j)
        SetDisapearTimeEffect(stMagicList[id].mEntityUniqueID[j], force ? -1.0f : 0.0f);

    std::memmove(stMagicList + id, stMagicList + id + 1, sizeof(CMagicList) * (stMLcnt - id - 1));
    for (DWORD i = id; i + 1 < stMLcnt; ++i)
        stMagicOwners455[i] = std::move(stMagicOwners455[i + 1]);
    --stMLcnt;
    stMagicList[stMLcnt].mMagicPtr = nullptr;
    stMagicOwners455[stMLcnt].reset();
}
'''+raw[end:]
    start, end = section(raw, b'DWORD StartMagicEffect(float mat[4][4]', b'DWORD StartMagicEffect(float mat[4][4]')
    body = raw[start:end]
    cache_start = body.index(b'\tCProcessMagic *get_magic;')
    cache_publish = b'\tif(!get_magic->mTrackNum)return 0;'
    cache_end = body.index(cache_publish, cache_start) + len(cache_publish)
    warnings = re.findall(rb'Warning\(path,[^\r\n]+?\);', body[cache_start:cache_end])
    if len(warnings) != 1:
        raise ValueError('Magic cache resource warning boundary')
    body = body[:cache_start]+b'''    stMagicOwners455[stMLcnt] = std::move(owner);
    stMagicList[stMLcnt].mMagicPtr = get_magic;'''+body[cache_end:]
    at = body.index(b'\tPushMagicIDList(magic_id);')
    publish = body.index(b'\tstMagicList[stMLcnt].mState = state;', at)
    body = body[:at]+b'''    auto owner = FindOrLoadMagicTrack455(magic_id);
    if (!owner) return 0;
    auto* get_magic = &owner->script;
    PushMagicIDList(magic_id);
    auto* e_Info = static_cast<EffectInfo*>(v_einfo);
    if (stMLcnt >= _MAX_MAGIC_EFFECT_CNT) DeleteMagicList(0, TRUE);
'''+body[publish:]
    raw = raw[:start]+body+raw[end:]

    reset = b'void ResetEffectManager()'
    start, end = section(raw, reset, reset)
    helpers = (native/'client455_effect_cache.inc').read_bytes()
    warning_placeholder = b'@@MISSING_MAGIC_WARNING@@'
    if helpers.count(warning_placeholder) != 1:
        raise ValueError('Magic cache helper warning boundary')
    helpers = helpers.replace(warning_placeholder, warnings[0])
    raw = raw[:start]+helpers+b'''\r\nvoid ResetEffectManager()
{
    ReleaseActiveEffects455();
}
'''+raw[end:]

    angular_start = b'DWORD StartMagicEffect(Vector3f pos,float y_angle'
    start, end = section(raw, angular_start, angular_start)
    body = raw[start:end]
    first = body.index(b'\tstMagicList[stMLcnt].mYAngle = y_angle;')
    last = body.index(b'\treturn StartMagicEffect(mat,magic_id,e_Info,state);', first)
    body = body[:first]+b'''    const DWORD id = StartMagicEffect(mat, magic_id, e_Info, state);
    if (id) {
        auto& effect = stMagicList[stMLcnt - 1];
        effect.mYAngle = y_angle;
        effect.mYOldAngle = y_angle;
        effect.mYAngleCnt = 0;
    }
    return id;'''+body[last+len(b'\treturn StartMagicEffect(mat,magic_id,e_Info,state);'):]
    raw = raw[:start]+body+raw[end:]

    remove = b'BOOL DelMagicEffect(DWORD magic_id)'
    start, end = section(raw, remove, remove)
    raw = raw[:start]+b'''BOOL DelMagicEffect(DWORD magic_id)
{
    auto entry = FindMagicCacheEntry455(magic_id);
    if (entry == stMagicCache.end()) return FALSE;
    stMagicCache.erase(entry);
    return TRUE;
}
'''+raw[end:]

    create = b'void CreateEffectsList(char *filename)'
    start, end = section(raw, create, create)
    raw = raw[:start]+b'''void CreateEffectsList(char* filename)
{
    if (stMLcnt || stELcnt) return;
    if (!RF455_TryLoadEffectEntityList455(filename)) return;
    stMagicCache.clear();
    stMagicCacheReady455 = true;
}
'''+raw[end:]
    destroy = b'void DestroyEffectsList()'
    start, end = section(raw, destroy, destroy)
    raw = raw[:start]+b'''void DestroyEffectsList()
{
    ReleaseActiveEffects455();
    stMagicCache.clear();
    stMagicCacheReady455 = false;
    ReleaseEffectEntityList();
}
'''+raw[end:]
    drop_active = b'void DestroyEffectsCache()'
    start, end = section(raw, drop_active, drop_active)
    raw = raw[:start]+b'''void DestroyEffectsCache()
{
    ReleaseActiveEffects455();
}
'''+raw[end:]
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
