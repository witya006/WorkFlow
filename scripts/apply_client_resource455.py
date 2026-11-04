"""Compose resource-I/O patches over compiler/weather copies; preserve all branches."""
import hashlib
import json
from pathlib import Path
from compare_client_binaries import WS
from apply_client_port_patches import PATCHES
from apply_client_weather455 import render_weather
from apply_client_draw455 import merge_behavior_manifest

FLAG='RF_CLIENT_455_RESOURCE_IO'
WEATHER={'1stclass/r3bsp.h','1stclass/bsp.cpp','1stclass/r3particle.cpp','1stclass/r3material.cpp','2ndclass/level.cpp'}


def render_resource(rel,d):
    nl=b'\r\n' if b'\r\n' in d else b'\n'
    def text(s):return s.encode('ascii').replace(b'\n',nl)
    def one(old,new):
        nonlocal d
        if d.count(old)!=1:raise ValueError(f'Nonunique resource anchor:{rel} {old!r}')
        d=d.replace(old,new,1)
    def add_entry(signature,statements):
        nonlocal d
        at=d.index(b'{',d.index(signature))+1
        d=d[:at]+text('\n#if defined('+FLAG+')\n'+statements+'\n#endif')+d[at:]
    def reader(signature,old):
        nonlocal d
        start=d.index(signature);at=d.index(old,start)
        d=d[:at]+text('#if defined('+FLAG+')\n')+old.replace(b'fopen(',b'RF455_OpenResource(')+text('\n#else\n')+old+text('\n#endif')+d[at+len(old):]
    # Includes precede legacy headers but are guarded by the explicit feature.
    d=text('#if defined('+FLAG+')\n#include "client455_resource_io.h"\n#endif\n')+d
    if rel=='1stclass/r3bsp.h':
        anchor=b'\t_BSP_FILE_HEADER\t\tmBSPHeader;'
        one(anchor,text('#if defined('+FLAG+')\n    RF455_RpkGroup mResourceGroup;\n#endif\n')+anchor)
    elif rel=='1stclass/bsp.cpp':
        add_entry(b'void CBsp::LoadBsp(char *name)','    RF455_SetResourceGroup(NULL);')
        one(b'    LoadEnvironment455();',text('#if defined('+FLAG+')\n    mResourceGroup.LoadDirectory(GetR3State()->EntityPath);\n    RF455_SetResourceGroup(&mResourceGroup);\n#endif\n')+b'    LoadEnvironment455();')
        # WEATHER/OFF still needs the group before the legacy single layer path.
        anchor=b'\tmEnvID = r3_state->mEnvID;'
        one(anchor,text('#if defined('+FLAG+')\n    mResourceGroup.LoadDirectory(GetR3State()->EntityPath);\n    RF455_SetResourceGroup(&mResourceGroup);\n#endif\n')+anchor)
        anchor=b'\tmTotalAllocSize += mEntityListNum*sizeof(CParticle);'
        one(anchor,anchor+text('\n#if defined('+FLAG+')\n    RF455_SetResourceGroup(&mResourceGroup);\n#endif'))
        add_entry(b'void CBsp::ReleaseBsp()', '    mResourceGroup.Release();')
    elif rel=='2ndclass/level.cpp':
        add_entry(b'void CLevel::LoadLevel(char *name)','    RF455_SetResourceGroup(NULL);')
        for anchor in (b'\t\tLoadLightMap(tempname);',b'\t\tmDummy.LoadExtDummy(tempname);'):
            one(anchor,text('#if defined('+FLAG+')\n        RF455_SetResourceGroup(NULL);\n#endif\n')+anchor)
    elif rel=='1stclass/entity.cpp':
        reader(b'BOOL CEntity::LoadEntity(',b'FILE *fp = fopen(filename,"rb");')
        anchor=b'\tif( IsExistFile(r3m_path) )'
        one(anchor,text('#if defined('+FLAG+')\n    if (RF455_ResourceExists(r3m_path))\n#else\n')+anchor+text('\n#endif'))
        anchor=b'\tmMapColor = 0xff808080;'
        one(anchor,text('#if defined('+FLAG+')\n    strlwr(filename);\n#endif\n')+anchor)
    elif rel=='1stclass/r3material.cpp':
        reader(b'void LoadR3X(',b'if( (fp = fopen(name,"rb")) == NULL)')
        reader(b'_R3MATERIAL* LoadIndependenceR3M(',b'if( (fp = fopen(name,"rb")) == NULL)')
    elif rel=='1stclass/r3d3dtex.cpp':
        reader(b'R3Texture *R3GetTexInfoR3T(',b'FILE *fp = fopen(name,"rb");')
        reader(b'void LoadR3T(R3Texture *tex)',b'FILE *fp = fopen(tex->mName,"rb");')
    elif rel=='1stclass/r3particle.cpp':
        reader(b'BOOL CParticle::LoadParticleSPT(',b'if(( fp =fopen(name,"rt"))==NULL)')
        # Both loops retain case-sensitive end check before the later strlwr.
        at=d.index(b'        if (!strcmp(hole,"[Particle]"))',d.index(b'BOOL CParticle::LoadParticleSPT'))
        d=d[:at]+text('#if defined('+FLAG+')\n        if (RF455_ParticleScriptEnd(hole)) break;\n#endif\n')+d[at:]
        start=d.index(b'\t\tstrlwr(hole);',d.index(b'BOOL CParticle::LoadParticleSPT'))
        d=d[:start]+text('#if defined('+FLAG+')\n        if (RF455_ParticleScriptEnd(hole)) break;\n#endif\n')+d[start:]
    else:raise ValueError('Unknown resource patch target')
    return d


def main():
    root=Path(json.loads((WS/'config/paths.json').read_text(encoding='utf-8'))['legacy_source'])/'R3Engine/R3Engine'
    prior={x['file']:x for x in json.loads((WS/'inventory/client-behavior-patches.json').read_text(encoding='utf-8'))}
    proof=json.loads((WS/'inventory/client455-resource-io.json').read_text(encoding='utf-8'))
    for name,digest in proof['source_sha256'].items():
        if hashlib.sha256((WS/'scripts/native'/name).read_bytes()).hexdigest()!=digest:raise ValueError('Native resource proof stale')
    updates=[]
    for rel in ['1stclass/r3bsp.h','1stclass/bsp.cpp','2ndclass/level.cpp','1stclass/entity.cpp','1stclass/r3material.cpp','1stclass/r3d3dtex.cpp','1stclass/r3particle.cpp']:
        original=(root/rel).read_bytes();base=original
        for before,after in PATCHES.get('R3Engine/'+rel,[]):
            if base.count(before)!=1:raise ValueError('Compiler anchor changed')
            base=base.replace(before,after,1)
        upstream=render_weather(rel,base) if rel in WEATHER else base
        desired=render_resource(rel,upstream)
        path=WS/'work/client-build/source/R3Engine'/rel;key=path.relative_to(WS).as_posix()
        current=path.read_bytes();known=prior.get(key)
        if current not in (base,upstream,desired):raise ValueError(f'Preserving unexpected resource edits:{rel}')
        if known and (known['original_sha256']!=hashlib.sha256(original).hexdigest() or known['input_sha256']!=hashlib.sha256(base).hexdigest()):raise ValueError('Behavior ledger input changed')
        if current!=desired:path.write_bytes(desired)
        updates.append({'file':key,'original_sha256':hashlib.sha256(original).hexdigest(),
                        'input_sha256':hashlib.sha256(base).hexdigest(),'patched_sha256':hashlib.sha256(desired).hexdigest(),
                        'build_option':FLAG,'upstream_build_option':'RF_CLIENT_455_WEATHER' if rel in WEATHER else None,
                        'upstream_sha256':hashlib.sha256(upstream).hexdigest(),'legacy_branch_preserved':True,
                        'reason':'Archive-aware resource opens/exists, BSP group ownership/selection and exact case-sensitive particle end boundaries; prior weather branches retained.',
                        'binary_evidence_report':'inventory/client455-resource-reference.json'})
    merge_behavior_manifest(updates)
    print('PASS: resource I/O/end patches composed over compiler/weather branches in7copied files.')


if __name__=='__main__':main()
