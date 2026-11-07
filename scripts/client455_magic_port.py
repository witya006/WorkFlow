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
        raw=b'#include "client455_resource_io.h"\r\n#include <stdexcept>\r\n#include <memory>\r\n'+raw
        start,end=section(raw,b'void CProcessMagic::CreateMagicTrack(',b'void CProcessMagic::CreateMagicTrack(')
        body=raw[start:end]
        def edit(old,new):
            nonlocal body
            if body.count(old)!=1:raise ValueError('Magic parser '+repr(old))
            body=body.replace(old,new)
        edit(b'fopen(r_name,"rt")',b'RF455_OpenResource(r_name,"rt")')
        edit(b'char hole[256];',b'std::unique_ptr<FILE,int(*)(FILE*)> sourceFile455(fp,fclose);\r\n\tchar hole[256];')
        body=body.replace(b'fclose(fp);',b'sourceFile455.reset();')
        edit(b'mCreateType=0;',b'mCreateType=0;mAxisType455=0;mAxisInfo455=0;')
        edit(b'strlwr(hole);',b'strlwr(hole);\r\n\t\tif(!strcmp(hole,"end"))break;')
        edit(b'memset(&mMagicTrack[mTrackNum],0,sizeof(_MAGIC_TRACK));',b'if(mTrackNum>=64)throw std::out_of_range("455 magic track overflow");\r\n\t\t\tmemset(&mMagicTrack[mTrackNum],0,sizeof(_MAGIC_TRACK));')
        edit(b'mMagicTrack[now_track_id].Flag|=_MT_FLAG_BILLBOARD;',b'mMagicTrack[now_track_id].Flag|=(_MT_FLAG_BILLBOARD|0x800);')
        anchor=b'\t\tif( !strcmp(hole,"create_pos"))'
        edit(anchor,b'\t\tif(!strcmp(hole,"axis_type")){fscanf(fp,"%255s",hole);mAxisType455=BYTE(atol(hole));fscanf(fp,"%255s",hole);mAxisInfo455=BYTE(atol(hole));}\r\n'+anchor)
        anchor=b'\t\tif( !strcmp(hole,"sky_fade_color"))'
        edit(anchor,b'''\t\tif(!strcmp(hole,"screen_blur_time")){fscanf(fp,"%255s",hole);auto& t=mMagicTrack[now_track_id];t.Flag|=0x1000;if(t.QuakeDensity==0)t.QuakeDensity=.15f;t.QuakeTime=float(atof(hole));}\r\n\t\tif(!strcmp(hole,"screen_blur_density")){fscanf(fp,"%255s",hole);auto& t=mMagicTrack[now_track_id];t.Flag|=0x1000;if(t.QuakeTime==0)t.QuakeTime=1;t.QuakeDensity=float(atof(hole));}\r\n'''+anchor)
        import re
        body,count=re.subn(rb'(if\s*\(\s*!strcmp\(hole,"entity_id"\)\)\s*\{)',rb'\1\r\n\t\t\tif(mMagicTrack[now_track_id].EntityID){Warning(name,"455 duplicate entity ID");mMagicTrack[now_track_id].Flag=0;}',body)
        if count!=1:raise ValueError('Magic duplicate entity boundary')
        close=body.rfind(b'sourceFile455.reset();')
        if close<0:raise ValueError('Magic stream-close boundary')
        at=body.rfind(b'}',0,close)
        if at<0:raise ValueError('Magic final parser loop')
        body=body[:at]+b'\r\n'+(native/'client455_magic_parser_extra.inc').read_bytes()+body[at:]
        raw=raw[:start]+body+raw[end:]
        start,end=section(raw,b'LONG CProcessMagic::GetEntityIDs(float old_frame,float now_frame,LONG *start_loop)',b'LONG CProcessMagic::GetEntityIDs(float old_frame,float now_frame,LONG *start_loop)')
        body=raw[start:end];body=body.replace(b'mState = 0;',b'mState &= 0xffffff00u;')
        body,count=re.subn(rb'if\( now_frame > mMagicTrack\[mTrackNum-1\].Time \)\s+return -2;\s+return -1;',b'if(mMagicTrack[mTrackNum-1].Time>=now_frame)return -1;return -2;',body)
        if count!=1:raise ValueError('Magic final selector comparison')
        raw=raw[:start]+body+raw[end:]
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
        return raw,True
    if relative=='addcodebyjang/effectentitylist.cpp':
        raw=b'#include "client455_resource_io.h"\r\n'+raw
        anchor=b'static DWORD stEntityNum;'
        at=raw.index(anchor)
        end=raw.index(b'\n',at)+1
        raw=raw[:end]+b'''\r\nnamespace {\r\nstruct EffectResourceGroup455 : RF455_RpkGroup {\r\n    ~EffectResourceGroup455(){Release();}\r\n};\r\nEffectResourceGroup455 effectResources455;\r\n}\r\nRF455_RpkGroup* GetEffectResourceGroup455(){return &effectResources455;}\r\n'''+raw[end:]
        once(b'stMaxEntityNum=768;',b'stMaxEntityNum=768;\r\n\tif(stEffectEntityList)Dfree(stEffectEntityList);')
        once(b'memset(stEffectEntityList,0,sizeof(_EFFECT_ENTITY_LIST)*stMaxEntityNum );',
             b'memset(stEffectEntityList,0,sizeof(_EFFECT_ENTITY_LIST)*stMaxEntityNum );\r\n\teffectResources455.Release();\r\n\teffectResources455.LoadDirectory(".\\\\effect\\\\");')
        import re
        raw,count=re.subn(rb'(void ReleaseEffectEntityList\(\)\r?\n\{)',
                          rb'\1\r\n\teffectResources455.Release();',raw)
        if count!=1:raise ValueError('Effect group release entry')
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
