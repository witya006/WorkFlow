"""Port two-layer weather plumbing on copied sources; retain legacy branches."""
import hashlib
import json
from pathlib import Path
from compare_client_binaries import WS
from apply_client_draw455 import merge_behavior_manifest
from apply_client_port_patches import PATCHES

FLAG=b'RF_CLIENT_455_WEATHER'


def replace(data,before,after):
    if data.count(before)!=1: raise ValueError(f'Nonunique weather anchor {before[:80]!r}')
    return data.replace(before,after,1)


def guarded(old,new,nl):
    return b'#if defined('+FLAG+b')'+nl+new+nl+b'#else'+nl+old+nl+b'#endif'


def brace_end(data,at):
    start=data.index(b'{',at);depth=1;cursor=start+1
    while depth:
        byte=data[cursor];cursor+=1
        if byte==123: depth+=1
        elif byte==125: depth-=1
    return cursor


def main():
    paths=json.loads((WS/'config/paths.json').read_text(encoding='utf-8'))
    root=Path(paths['legacy_source'])/'R3Engine/R3Engine'
    evidence=json.loads((WS/'inventory/client455-weather-helper.json').read_text(encoding='utf-8'))['binary_evidence']
    target=json.loads((WS/'config/client-target.json').read_text(encoding='utf-8'))
    if [item.get('input') for item in evidence]!=['current','reference-backup']:
        raise ValueError('Both ordered pinned weather references are required')
    for item,key in zip(evidence,['behavior_reference','secondary_reference']):
        binary=WS/f'work/client-reference/{item["input"]}/RF_Online.bin'
        if hashlib.sha256(binary.read_bytes()).hexdigest()!=item['sha256'] or item['sha256']!=target[key]['sha256']:
            raise ValueError('Weather instruction evidence is stale')
    records=[]
    prior={item['file']:item for item in json.loads((WS/'inventory/client-behavior-patches.json').read_text(encoding='utf-8'))}
    for rel in ['1stclass/core.h','1stclass/core.cpp','1stclass/r3material.h','1stclass/r3material.cpp',
                '1stclass/r3bsp.h','1stclass/bsp.cpp','1stclass/r3render.cpp','1stclass/r3particle.cpp','2ndclass/level.cpp']:
        original=(root/rel).read_bytes();base=original
        for before,after in PATCHES.get('R3Engine/'+rel,[]):
            base=replace(base,before,after)
        d=base;nl=b'\r\n' if b'\r\n' in d else b'\n'
        def text(s): return s.encode('ascii').replace(b'\n',nl)
        if rel=='1stclass/core.h':
            start=d.index(b'\tchar mEnvEntityName[128];');end=d.index(nl,d.index(b'\tDWORD mEnvID;',start))
            old=d[start:end]
            new=text('union { char mEnvEntityName[128]; char mEnvEntityNames[2][128]; };\nunion { DWORD mEnvID; DWORD mEnvIDs[2]; };\nBOOL mEnvironmentEnabled;\nDWORD mEnvironmentSceneFlags;')
            d=d[:start]+guarded(old,new,nl)+d[end:]
        elif rel=='1stclass/core.cpp':
            anchor=b'\tstState.mIsDrawLogo=FALSE;'
            d=replace(d,anchor,anchor+nl+text('#if defined(RF_CLIENT_455_WEATHER)\n\tstState.mEnvironmentEnabled=TRUE;\n#endif'))
        elif rel=='1stclass/r3material.h':
            start=d.index(b'typedef struct{',d.index(b'#define EXT_MAT_EXIST_ENV'))
            end=d.index(b'}_EXT_MAT;',start)+len(b'}_EXT_MAT;')
            d=d[:start]+guarded(d[start:end],b'typedef RF455_ExtMaterial _EXT_MAT;',nl)+d[end:]
            d=text('#if defined(RF_CLIENT_455_WEATHER)\n#include "client455_weather_format.h"\n#endif\n')+d
        elif rel=='1stclass/r3material.cpp':
            anchor=b'\t\t\tr3_state->mEnvID = (DWORD)atoi(hole);'+nl+b'\t\t}'
            new=anchor+nl+text('#if defined(RF_CLIENT_455_WEATHER)\n        if (!strcmp(hole,"*ENVIRONMENT2")) {\n            fscanf(fp,"%s",hole);\n            strcpy(r3_state->mEnvEntityNames[1],hole);\n        }\n        if (!strcmp(hole,"*ENVIRONMENT_ID2")) {\n            fscanf(fp,"%s",hole);\n            r3_state->mEnvIDs[1]=(DWORD)atoi(hole);\n        }\n#endif')
            d=replace(d,anchor,new)
            start=d.index(b'        if (!strcmp(hole,"*ENVIRONMENT"))')
            end=d.index(b'#endif',start)+len(b'#endif')
            d=d[:start]+guarded(base[base.index(b'        if (!strcmp(hole,"*ENVIRONMENT"))'):base.index(nl+b'\t}',base.index(b'        if (!strcmp(hole,"*ENVIRONMENT_ID"))'))],
                b'        RF455_ReadWeatherTokens(fp,hole);',nl)+d[end:]
            start=d.index(b'\tfread(&version,sizeof(DWORD),1,fp);')
            end=d.index(b'\tfread(&ext_mat,sizeof(_EXT_MAT),1,fp);',start)+len(b'\tfread(&ext_mat,sizeof(_EXT_MAT),1,fp);')
            old=d[start:end]
            warning_start=old.index(b'\t\tWarning(');warning_end=old.index(nl,warning_start)
            new=text('    if (!RF455_ReadExtMaterial(fp,&ext_mat)) {\n')+old[warning_start:warning_end]+text('\n        fclose(fp);\n        return;\n    }\n    state->mEnvironmentSceneFlags=ext_mat.mSceneFlags;')
            d=d[:start]+guarded(old,new,nl)+d[end:]
            anchor=b'\t\tstrcpy(state->mEnvEntityName,ext_mat.mEnvEntityName);'
            d=replace(d,anchor,anchor+nl+text('#if defined(RF_CLIENT_455_WEATHER)\n        state->mEnvIDs[1]=ext_mat.mEnvID2;\n        strcpy(state->mEnvEntityNames[1],ext_mat.mEnvEntityName2);\n#endif'))
            anchor=b'\tstate->mEnvID=0;'
            if d.count(anchor)!=2: raise ValueError('Expected two material reset paths')
            d=d.replace(anchor,anchor+nl+text('#if defined(RF_CLIENT_455_WEATHER)\n    state->mEnvIDs[1]=0;\n    state->mEnvironmentEnabled=TRUE;\n#endif'))
        elif rel=='1stclass/r3bsp.h':
            start=d.index(b'\tDWORD mEnvID;');end=d.index(b'\npublic:',start)
            old=d[start:end]
            new=text('    union { DWORD mEnvID; DWORD mEnvIDs[2]; };\n    union {\n        CEntity* mEnvEntity; CParticle* mEnvParticle;\n        CEntity* mEnvEntities[2]; CParticle* mEnvParticles[2];\n    };\n    CExtDummy* mEnvironmentDummies;')
            d=d[:start]+guarded(old,new,nl)+d[end:]
            anchor=b'class  CBsp{'
            d=replace(d,anchor,text('#if defined(RF_CLIENT_455_WEATHER)\nclass CExtDummy;\n#endif\n')+anchor)
            anchor=b'\tvoid SaveExtBsp(char *name,_ADD_BSP_SAVE *add_bsp);'
            methods=text('#if defined(RF_CLIENT_455_WEATHER)\n    void LoadEnvironment455();\n    void ReleaseEnvironment455();\n    void UpdateEnvironment455();\n    void DrawEnvironment455();\n    void SetEnvironmentDummies455(CExtDummy* owner) { mEnvironmentDummies=owner; }\n    CParticle* GetEnvironmentParticle455(unsigned i) { return i<2?mEnvParticles[i]:NULL; }\n    DWORD GetEnvironmentKind455(unsigned i) { return i<2?mEnvIDs[i]:0; }\n#endif\n')
            d=replace(d,anchor,methods+anchor)
        elif rel=='1stclass/bsp.cpp':
            anchor=b'\tmEnvID=0;';at=d.index(anchor)
            d=d[:at]+d[at:].replace(anchor,anchor+nl+text('#if defined(RF_CLIENT_455_WEATHER)\n    mEnvIDs[1]=0;\n    memset(mEnvParticles,0,sizeof(mEnvParticles));\n    mEnvironmentDummies=NULL;\n#endif'),1)
            start=d.index(b'\tmEnvID = r3_state->mEnvID;');end=brace_end(d,d.index(b'\tif( mEnvID )',start))
            d=d[:start]+guarded(d[start:end],b'    LoadEnvironment455();',nl)+d[end:]
            start=d.index(b'\tif( mEnvID )',d.index(b'void CBsp::ReleaseBsp'))
            end=brace_end(d,start)
            d=d[:start]+guarded(d[start:end],b'    ReleaseEnvironment455();',nl)+d[end:]
        elif rel=='1stclass/r3render.cpp':
            start=d.index(b'{',d.index(b'void CBsp::RenderEnvironment(DWORD id)'))+1
            end=brace_end(d,d.index(b'void CBsp::RenderEnvironment(DWORD id)'))-1
            d=d[:start]+nl+guarded(d[start:end],b'    DrawEnvironment455();',nl)+nl+d[end:]
        elif rel=='1stclass/r3particle.cpp':
            at=d.index(b'\t\tstrlwr(hole);',d.index(b'BOOL CParticle::LoadParticleSPT'))
            anchor=b'\t\tstrlwr(hole);'
            d=d[:at]+d[at:].replace(anchor,anchor+nl+text('#if defined(RF_CLIENT_455_WEATHER)\n        if (!strcmp(hole,"night")) mFlag|=0x10000;\n#endif'),1)
        elif rel=='2ndclass/level.cpp':
            d=text('#if defined(RF_CLIENT_455_WEATHER)\n#include "client455_weather_format.h"\n#endif\n')+d
            anchor=b'\t\tmDummy.LoadExtDummy(tempname);'
            d=replace(d,anchor,anchor+nl+text('#if defined(RF_CLIENT_455_WEATHER)\n        mBsp->SetEnvironmentDummies455(&mDummy);\n#endif'))
            anchor=b'\tSetMultiLayerTime(R3GetTime());'
            d=replace(d,anchor,anchor+nl+text('#if defined(RF_CLIENT_455_WEATHER)\n    RF455_AdvanceDayClock();\n#endif'))
            anchor=b'\tmBsp->CalcObjectLoop();'
            d=replace(d,anchor,text('#if defined(RF_CLIENT_455_WEATHER)\n    mBsp->UpdateEnvironment455();\n#endif\n')+anchor)
        output=WS/'work/client-build/source/R3Engine'/rel
        current=output.read_bytes()
        known=prior.get(output.relative_to(WS).as_posix())
        recognized=known is not None and known['build_option']==FLAG.decode() and known['original_sha256']==hashlib.sha256(original).hexdigest() and known['input_sha256']==hashlib.sha256(base).hexdigest() and known['patched_sha256']==hashlib.sha256(current).hexdigest()
        if current not in (original,base,d) and not recognized: raise ValueError(f'Preserving unexpected source edits: {rel}')
        if output.read_bytes()!=d: output.write_bytes(d)
        records.append({'file':output.relative_to(WS).as_posix(),'original_sha256':hashlib.sha256(original).hexdigest(),
            'input_sha256':hashlib.sha256(base).hexdigest(),'patched_sha256':hashlib.sha256(d).hexdigest(),
            'build_option':FLAG.decode(),'legacy_branch_preserved':True,
            'reason':'455 two-layer R3X/text config, weather lifecycle, helper interior stop, frame update/draw split and night particle flag. GPU and full clock/network parity remain open.',
            'binary_evidence_report':'inventory/client455-weather-helper.json'})
    merge_behavior_manifest(records)
    print('PASS: two-layer weather selections staged in nine copied files; originals and legacy branches retained.')


if __name__=='__main__': main()
