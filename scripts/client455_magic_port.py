"""Port the client-owned magic layout and parser; keep engine originals intact."""


def port_magic(raw,relative,native,section):
    def once(old,new):
        nonlocal raw
        if raw.count(old)!=1:raise ValueError('Magic anchor '+relative+':'+repr(old))
        raw=raw.replace(old,new)
    if relative=='global.h':
        import re
        raw,count=re.subn(rb'(DWORD\s+dwValue;)',rb'\1\r\n\tDWORD unknown48_455,unknown52_455; // confirmed tail; consumer meanings remain open',raw)
        if count!=1:raise ValueError('EffectInfo56 tail')
        return raw,True
    if relative=='global.cpp':
        start,end=section(raw,b'EffectInfo::EffectInfo()',b'EffectInfo::EffectInfo()')
        raw=raw[:end-1]+b'\r\n\tunknown52_455=ID_INVALID;\r\n'+raw[end-1:]
        return raw,True
    if relative=='addcodebyjang/cmagicscript.h':
        raw=b'#include "client455_magic_control.h"\r\n'+raw
        once(b'#define _MAX_MAGIC_TRACK 16',b'#define _MAX_MAGIC_TRACK 64')
        import re
        raw,count=re.subn(rb'BYTE(\s+mState;)',rb'DWORD\1',raw)
        if count!=1:raise ValueError('Magic state DWORD')
        raw,count=re.subn(rb'(BYTE\s+mCreateType;)',rb'\1\r\n\tBYTE mAxisType455,mAxisInfo455;',raw)
        if count!=1:raise ValueError('Magic axis fields')
        raw,count=re.subn(rb'(_MAGIC_TRACK\s+mMagicTrack\[_MAX_MAGIC_TRACK\];)',rb'RF455MagicControl m_control455;\r\n\t\1',raw)
        if count!=1:raise ValueError('Magic control member')
        return raw,True
    if relative=='addcodebyjang/cmagicscript.cpp':
        import re
        raw=(b'#include "client455_resource_io.h"\r\n#include "client455_resource_text.h"\r\n'
             b'#include "client455_effect_manifest.h"\r\n#include <cstdio>\r\n#include <cstdlib>\r\n'
             b'#include <cstring>\r\n#include <limits>\r\n#include <stdexcept>\r\n'+raw)
        helper=b'static BOOL GetRandOrNum('
        begin,end=section(raw,helper,helper)
        raw=raw[:begin]+(native/'client455_magic_reader.inc').read_bytes()+raw[end:]
        start,end=section(raw,b'void CProcessMagic::CreateMagicTrack(',b'void CProcessMagic::CreateMagicTrack(')
        body=raw[start:end]
        def edit(old,new):
            nonlocal body
            if body.count(old)!=1:raise ValueError('Magic parser '+repr(old))
            body=body.replace(old,new)
        first=body.index(b'\tFILE *fp;')
        last=body.index(b'\tchar hole[256];',first)
        warnings=re.findall(rb'Warning\(r_name,[^\r\n]+?\);',body[first:last])
        if len(warnings)!=1:raise ValueError('Magic input-open boundary')
        body=body[:first]+b'''    mIsLoaded = FALSE;
    const auto* state = GetR3State();
    if (!name || !std::memchr(state->EffectPath, 0, sizeof(state->EffectPath))) return;
    char r_name[256];
    const int length = std::snprintf(r_name, sizeof(r_name), "%s%s", state->EffectPath, name);
    if (length < 0 || length >= static_cast<int>(sizeof(r_name))) return;
    RF455ResourceText input;
    std::uint64_t archiveBytes = 0;
    auto* stream = RF455_OpenResourceTextStream455(r_name, archiveBytes);
    if (!input.openStream(stream, archiveBytes)) {
        r_name[220] = 0;
        '''+warnings[0]+b'''
        return;
    }
'''+body[last:]
        loop_read=b'fscanf(fp,"%s",hole)==EOF'
        if body.count(loop_read)!=2 or body.count(b'fclose(fp);')!=2:
            raise ValueError('Magic input iteration boundary')
        body=body.replace(loop_read,b'!ReadMagicToken455(input, hole)')
        body=body.replace(b'\t\t\tfclose(fp);',b'')
        edit(b'\tmIsLoaded=TRUE;',b'')
        edit(b'\tfclose(fp);',b'\tmIsLoaded=TRUE;')
        if body.count(b'GetRandOrNum(fp,&from,&at)')!=2:
            raise ValueError('Magic numeric reader boundary')
        body=body.replace(b'GetRandOrNum(fp,&from,&at)',b'GetRandOrNum(input,&from,&at)')
        body=re.sub(rb'(\r?\n\t+)fscanf\(fp,"%s",hole\);',rb'\1RequireMagicToken455(input, hole);',body)
        edit(b'mCreateType=0;',b'mCreateType=0;mAxisType455=0;mAxisInfo455=0;')
        edit(b'strlwr(hole);',b'strlwr(hole);\r\n\t\tif(!strcmp(hole,"end"))break;')
        edit(b'memset(&mMagicTrack[mTrackNum],0,sizeof(_MAGIC_TRACK));',b'if(mTrackNum>=64)throw std::out_of_range("455 magic track overflow");\r\n\t\t\tmemset(&mMagicTrack[mTrackNum],0,sizeof(_MAGIC_TRACK));')
        edit(b'DWORD range=(DWORD)atof(hole);',b'''const double value = std::atof(hole);
                const double maxRange = static_cast<double>((std::numeric_limits<DWORD>::max)()) + 1.0;
                if (!(value >= 1.0 && value < maxRange)) throw std::out_of_range("455 MagicTrack rand_xz range");
                const DWORD range = static_cast<DWORD>(value);''')
        edit(b'DWORD tr_id=(DWORD)atoi(hole);',b'''char* tail = nullptr;
                const long tr_id = std::strtol(hole, &tail, 10);
                if (tail == hole || tr_id < 0 || tr_id >= _MAX_MAGIC_TRACK)
                    throw std::out_of_range("455 MagicTrack pos track index");''')
        edit(b'mMagicTrack[now_track_id].Flag|=_MT_FLAG_BILLBOARD;',b'mMagicTrack[now_track_id].Flag|=(_MT_FLAG_BILLBOARD|0x800);')
        anchor=b'\t\tif( !strcmp(hole,"create_pos"))'
        edit(anchor,b'\t\tif(!strcmp(hole,"axis_type")){RequireMagicToken455(input,hole);mAxisType455=BYTE(atol(hole));RequireMagicToken455(input,hole);mAxisInfo455=BYTE(atol(hole));}\r\n'+anchor)
        anchor=b'\t\tif( !strcmp(hole,"sky_fade_color"))'
        edit(anchor,b'''\t\tif(!strcmp(hole,"screen_blur_time")){RequireMagicToken455(input,hole);auto& t=mMagicTrack[now_track_id];t.Flag|=0x1000;if(t.QuakeDensity==0)t.QuakeDensity=.15f;t.QuakeTime=float(atof(hole));}\r\n\t\tif(!strcmp(hole,"screen_blur_density")){RequireMagicToken455(input,hole);auto& t=mMagicTrack[now_track_id];t.Flag|=0x1000;if(t.QuakeTime==0)t.QuakeTime=1;t.QuakeDensity=float(atof(hole));}\r\n'''+anchor)
        body,count=re.subn(rb'(if\s*\(\s*!strcmp\(hole,"entity_id"\)\)\s*\{)',rb'\1\r\n\t\t\tif(mMagicTrack[now_track_id].EntityID){Warning(name,"455 duplicate entity ID");mMagicTrack[now_track_id].Flag=0;}',body)
        if count!=1:raise ValueError('Magic duplicate entity boundary')
        close=body.index(b'\tmIsLoaded=TRUE;')
        at=body.rfind(b'}',0,close)
        if at<0:raise ValueError('Magic final parser loop')
        body=body[:at]+b'\r\n'+(native/'client455_magic_parser_extra.inc').read_bytes()+body[at:]
        raw=raw[:start]+body+raw[end:]
        start,end=section(raw,b'LONG CProcessMagic::GetEntityIDs(float old_frame,float now_frame,LONG *start_loop)',b'LONG CProcessMagic::GetEntityIDs(float old_frame,float now_frame,LONG *start_loop)')
        body=raw[start:end];body=body.replace(b'mState = 0;',b'mState &= 0xffffff00u;')
        body,count=re.subn(rb'if\( now_frame > mMagicTrack\[mTrackNum-1\].Time \)\s+return -2;\s+return -1;',b'if(mMagicTrack[mTrackNum-1].Time>=now_frame)return -1;return -2;',body)
        if count!=1:raise ValueError('Magic final selector comparison')
        raw=raw[:start]+body+raw[end:]
        helper=b'static DWORD ConvertHexa(char *hole)'
        begin,end=section(raw,helper,helper)
        raw=raw[:begin]+raw[end:]
        loader=b'void CreateMagicSptList(char *name)'
        begin,end=section(raw,loader,loader)
        raw=raw[:begin]+b'''void CreateMagicSptList(char* name)
{
    std::vector<RF455EffectManifestEntry> entries;
    std::size_t skipped = 0;
    if (!RF455_ReadEffectManifest455(name, RF455EffectManifestKind::Magic, entries, &skipped)) {
        Warning("MagicSptList", " could not read a valid manifest");
        return;
    }
    if (skipped) Warning("MagicSptList", " skipped paths longer than 89 bytes");

    static_assert(sizeof(_MAGIC_SPT_LIST) == 96, "455 magic manifest record");
    _MAGIC_SPT_LIST* next = nullptr;
    if (!entries.empty()) {
        next = static_cast<_MAGIC_SPT_LIST*>(Dmalloc(static_cast<int>(entries.size() * sizeof(*next))));
        if (!next) return;
        for (std::size_t i = 0; i < entries.size(); ++i) {
            next[i] = {};
            next[i].id = entries[i].id;
            std::memcpy(next[i].name, entries[i].path, sizeof(next[i].name));
        }
    }
    if (stMagicSptList) Dfree(stMagicSptList);
    stMagicSptList = next;
    stMagicSptNum = stMaxMagicSptNum = static_cast<int>(entries.size());
}'''+raw[end:]
        once(b'stMagicSptNum=0;',b'stMagicSptNum=0;\r\n\tstMaxMagicSptNum=0;')
        return raw,True
    if relative=='addcodebyjang/effectcore.cpp':
        raw=b'#include "client455_resource_io.h"\r\n'+raw
        old=b'IsExistFile(path)'
        if raw.count(old)!=1:raise ValueError('Magic cache resource existence')
        raw=raw.replace(old,b'RF455_ResourceExists(path)')
        once(b'\t\tif( !RF455_ResourceExists(path))',
             b'\t\tRF455_SetResourceGroup(GetEffectResourceGroup455());\r\n\t\tif( !RF455_ResourceExists(path))')
        old=b'stMagicList[stMLcnt].mMagicPtr=get_magic;'
        if raw.count(old)!=1:raise ValueError('Magic cache zero-track boundary')
        raw=raw.replace(old,old+b'\r\n\tif(!get_magic->mTrackNum)return 0;')
        return raw,True
    if relative=='addcodebyjang/effectentitylist.h':
        raw=b'struct RF455_RpkGroup;\r\nRF455_RpkGroup* GetEffectResourceGroup455();\r\n'+raw
        once(b'void LoadEffectEntityList(char *name);',
             b'BOOL RF455_TryLoadEffectEntityList455(char* name);\r\nvoid LoadEffectEntityList(char *name);')
        return raw,True
    if relative=='addcodebyjang/effectentitylist.cpp':
        raw=(b'#include "client455_resource_io.h"\r\n#include "client455_effect_manifest.h"\r\n'
             b'#include <memory>\r\n#include <stdexcept>\r\n'
             b'void CreateEffectsList(char* filename);\r\n'+raw)
        anchor=b'static DWORD stEntityNum;'
        at=raw.index(anchor)
        end=raw.index(b'\n',at)+1
        raw=raw[:end]+b'''\r\nnamespace {\r\nRF455_RpkGroup effectResources455;\r\n}\r\nRF455_RpkGroup* GetEffectResourceGroup455(){return &effectResources455;}\r\n'''+raw[end:]
        helper=b'static DWORD ConvertHexa(char *hole)'
        begin,end=section(raw,helper,helper)
        raw=raw[:begin]+raw[end:]
        loader=b'void LoadEffectEntityList(char *name)'
        begin,end=section(raw,loader,loader)
        raw=raw[:begin]+b'''BOOL RF455_TryLoadEffectEntityList455(char* name)
{
    // Live effects borrow objects from the table until DestroyEffectsList.
    for (DWORD i = 0; i < stEntityNum; ++i)
        if (stEffectEntityList[i].Entity) return FALSE;
    if (!name || !*name) return FALSE;

    try {
        RF455_GetCharacterRfsCache()->RemoveLooseBytes(name);
        std::vector<RF455EffectManifestEntry> entries;
        std::size_t skipped = 0;
        if (!RF455_ReadEffectManifest455(name, RF455EffectManifestKind::Entity, entries, &skipped)) {
            Warning("EffectEntityList", " could not read a valid manifest");
            return FALSE;
        }
        if (skipped) Warning("EffectEntityList", " skipped paths longer than 89 bytes");

        static_assert(sizeof(_EFFECT_ENTITY_LIST) == 100, "455 effect manifest record");
        std::unique_ptr<_EFFECT_ENTITY_LIST, decltype(&Dfree)> staged(nullptr, &Dfree);
        if (!entries.empty()) {
            const auto bytes = static_cast<int>(entries.size() * sizeof(_EFFECT_ENTITY_LIST));
            staged.reset(static_cast<_EFFECT_ENTITY_LIST*>(Dmalloc(bytes)));
            if (!staged) return FALSE;
            auto* rows = staged.get();
            for (std::size_t i = 0; i < entries.size(); ++i) {
                rows[i] = {};
                rows[i].id = entries[i].id;
                std::memcpy(rows[i].name, entries[i].path, sizeof(rows[i].name));
            }
        }

        if (!effectResources455.TryReplaceDirectory455(".\\\\effect\\\\")) return FALSE;
        if (stEffectEntityList) Dfree(stEffectEntityList);
        stEffectEntityList = staged.release();
        stEntityNum = stMaxEntityNum = static_cast<DWORD>(entries.size());
        return TRUE;
    } catch (const std::bad_alloc&) {
        return FALSE;
    } catch (const std::length_error&) {
        return FALSE;
    }
}

void LoadEffectEntityList(char* name)
{
    CreateEffectsList(name);
}'''+raw[end:]
        classifier=b'BOOL IsParticle(DWORD real_id)'
        begin,end=section(raw,classifier,classifier)
        raw=raw[:begin]+b'''BOOL IsParticle(DWORD real_id)
{
    if (!stEffectEntityList || real_id >= stEntityNum) return FALSE;
    const auto* name = stEffectEntityList[real_id].name;
    const auto length = std::strlen(name);
    return length >= 3 && std::strcmp(name + length - 3, "spt") == 0;
}'''+raw[end:]
        import re
        raw,count=re.subn(rb'(void ReleaseEffectEntityList\(\)\r?\n\{)',
                          rb'\1\r\n\teffectResources455.Release();',raw)
        if count!=1:raise ValueError('Effect group release entry')
        raw,count=re.subn(rb'\tif\( stEntityNum == 0\)\r?\n\t\treturn;\r?\n',b'',raw)
        if count!=1:raise ValueError('Effect empty release boundary')
        once(b'stEntityNum=0;',b'stEntityNum=0;\r\n\tstMaxEntityNum=0;')
        raw,count=re.subn(rb'((?:CEntity \*GetEntityFromEffectEntityList|CParticle \*GetParticleFromEffectEntityList)\([^\r\n]+\)[^\r\n]*\r?\n\{)',
                          rb'\1\r\n\tif (!stEffectEntityList || real_id >= stEntityNum) return nullptr;',raw)
        if count!=2:raise ValueError('Effect table lookup boundaries')
        once(b'\t\tif( stEffectEntityList[real_id].Entity->LoadEntity(',
             b'\t\tRF455_SetResourceGroup(&effectResources455);\r\n\t\tif( stEffectEntityList[real_id].Entity->LoadEntity(')
        once(b'\t\tif(!particle->LoadParticleSPT(',
             b'\t\tRF455_SetResourceGroup(&effectResources455);\r\n\t\tif(!particle->LoadParticleSPT(')
        # Target clears NO_LOOP/END only in the finite-emission branch. An
        # always-live template retains its flags, including a pre-existing END.
        once(b'flag = (flag&~_PARTICLE_ATTR_END);',b'// 455: preserve flags outside the finite-emission branch.')
        once(b'particle->SetParticleAttr(_PARTICLE_ATTR_NO_LOOP|flag);',
             b'particle->SetParticleAttr((flag&~(_PARTICLE_ATTR_END|_PARTICLE_ATTR_NO_LOOP))|_PARTICLE_ATTR_NO_LOOP);')
        return raw,True
    return raw,False
