"""Validate128 ordinary lighting integration against pinned127 contracts."""
import hashlib
import json
import struct
from pathlib import Path
from audit_client455_item_payloads import record
from audit_client455_texture_lifetime import archive_objects
from build_client455_x87_math import read_va
from checkpoint_client455_rvp_effects import check,load,require,sha
from compare_client_binaries import WS,pe


def main():
    previous=load('client455-sky-lighting-reference')
    require(previous['status']=='PARTIAL_COMPONENT' and previous['full_assembly']==17
            and previous['instructions']==1538 and previous['CFG_complete'], 'Confirmed127 contracts')
    check(previous['raw']);check(previous['session']);check(previous['reused_reference'])
    raw=json.loads((WS/previous['raw']['file']).read_text())
    selected=set(raw['selected']);assembly={x['addr']:x for x in raw['assembly']};cfg={x['addr']:x for x in raw['cfg']}
    require(selected==set(assembly)==set(cfg) and len(selected)==17,'Selected17 bodies')
    for at in selected:
        a,g=assembly[at],cfg[at];addresses={int(x['addr'],16) for x in a['lines']}
        require(len(addresses)==len(a['lines'])==a['total_instructions']==sum(p['instruction_count'] for p in a['pages'])
                and a['pages'][-1]['cursor']['done'] and all(len(p['asm']['lines'])==p['instruction_count']<=100 for p in a['pages'])
                and g['cursor']['done'] and all(int(b['start'],16) in addresses for b in g['blocks'] if b['size']>0),'Complete bounded asm/CFG')
        p=next(x for x in raw['functions'] if x['addr'].lower()==at)['pages']
        require(sum(x['line_count'] for x in p)==p[0]['total_lines'] and p[-1]['cursor']['done'],'Complete pcode')
    context={}
    for query in raw['queries']:
        for row in query.get('result',[]):
            for ref in row.get('xrefs',[]) or []:
                fn=ref.get('fn')
                if fn and fn['addr'] in ['0x8c3400','0x90a4d0','0x90aed0']:context[fn['addr']]=fn
    require(len(context)==3,'Actual IDA context bounds')
    pins=json.loads((WS/'config/client-target.json').read_text());contexts=[]
    for i,(folder,key) in enumerate([('current','behavior_reference'),('reference-backup','secondary_reference')]):
        path=WS/f'work/client-reference/{folder}/RF_Online.bin';data=path.read_bytes();ref=previous['references'][i]
        require(sha(path)==pins[key]['sha256']==ref['sha256'] and pe(data)['architecture']=='x86','Pinned x86 reference')
        for row in ref['ranges']:
            b=read_va(data,0x400000+int(row['rva'],16),row['bytes']);require(hashlib.sha256(b).hexdigest()==row['sha256'],'Selected body bytes')
        for row in ref['numeric_literals']+ref['bounded_context_bytes']:
            require(read_va(data,0x400000+int(row['rva'],16),row['bytes']).hex()==row['hex'],'Selected literal/context bytes')
        for row in ref['decoded_calls']:
            at=0x400000+int(row['rva'],16);b=read_va(data,at,5)
            require(b[0]==0xe8 and at+5+struct.unpack('<i',b[1:])[0]==0x400000+int(row['target_rva'],16),'Selected decoded call')
        bodies=[dict(rva=hex(int(at,16)-0x400000),bytes=int(fn['size'],16),sha256=hashlib.sha256(read_va(data,int(at,16),int(fn['size'],16))).hexdigest()) for at,fn in sorted(context.items())]
        require(not contexts or bodies==contexts[0]['bodies'],'Both455 full context body bytes equal')
        contexts.append(dict(sha256=sha(path),architecture='x86',image_base='0x400000',bodies=bodies,full_assembly_claimed=False))
    engine=load('client455-startup-engine-build');sources=[record(WS/'scripts/native'/name) for name in ['client455_sky_lighting.h','client455_sky_lighting.inc','client455_sky_lighting_math.h','client455_sky_atmosphere.inc']]
    require(engine['objects']==67 and len(engine['derived_sources'])==18
            and engine['script_sha256']==sha(WS/'scripts/build_client455_engine_startup.py')
            and engine['sky_lighting']=={Path(x['file']).name:x['sha256'] for x in sources[:3]}
            and engine['sky_atmosphere']['client455_sky_atmosphere.inc']==sources[3]['sha256'],'Current engine sources')
    for row in engine['base_sources']+engine['derived_sources']:check(row)
    before=json.loads((WS/'artifacts/client455-progress/client455-startup-engine-build-before128.json').read_text())
    for field in ['core_header_overlay','sky_header_overlay','bsp_header_overlay','camera_header_overlay','particle_header_overlay']:
        require(engine[field]==before[field],'Shared declarations/layout unchanged')
    old=WS/'artifacts/client455-progress/engine-before128.lib';require(sha(old)==previous['engine']['sha256']==before['library_sha256'],'Exact previous126 engine')
    a,b=archive_objects(old,True),archive_objects(WS/engine['library'],True);require(set(a)==set(b) and len(a)==67,'Same67members')
    changed=[];same=[];stamp=[]
    for name in a:
        x,y=a[name]['payload'],b[name]['payload']
        if x==y:same.append(name)
        elif len(x)==len(y) and x[:4]+x[8:]==y[:4]+y[8:]:stamp.append(name)
        else:changed.append(name)
    require({Path(x.replace('\\','/')).name for x in changed}=={'level.obj','core.obj','r3material.obj'},'Only intended lighting/frame/core/material payload changes')
    level=(WS/'work/client455-port/startup-engine/source/level.cpp').read_bytes();material=(WS/'work/client455-port/startup-engine/source/r3material.cpp').read_bytes()
    require(b'RF455_AdvanceDayClock();\n    RF455_UpdateSkyLighting();' in level
            and b'RF455_LoadSkyFogEndpoints(ext_mat);' in material
            and b'RF455_ReadSkyFogToken(fp,hole);' in material,'Actual ordinary frame and both real loaders connected')
    start=material.index(b'static _R3MATERIAL* LoadIndependenceMaterial(');end=material.index(b'void LoadR3X(',start)
    require(b'strupr(hole)' not in material[start:end],'Main script dispatch retains455 case sensitivity')
    link=load('client455-normal-link');mapping=(WS/link['map']['file']).read_text(errors='replace')
    required=['RF455_UpdateSkyLighting','RF455_SampleSkyColor','RF455_LoadSkyFogEndpoints','RF455_ReadSkyFogToken','RF455_GetSkyTintColor']
    require(all(x in mapping for x in required),'Ordinary PE retains frame/sampling/loading/tint methods')
    gaps=[
        'Ordinary frame/both fog branches/real loaders/map tint bind integrated;full material flag8000 and remaining CPU tint consumers remain open',
        'Exposure helper is used by actual frame and tested in lab,but target CLevel DWORD-owner setter/game producers are not yet connected;do not claim ordinary gameplay exposure handling',
        'Previous-orbit Sun position computed,but full lens-flare consumer and local fog-volume acceptance remain open',
        'Default/selected Mie path restored;indirect day/night parameter writers and full shader/CRT transcendental/FP/RC/NaN/Inf/status-flag parity remain open',
        'Software visible RGB follows selected arithmetic;unused reference transform/extinction FP side effects are not yet reproduced',
        'INS/Planet/full world visibility/materials/device lost-reset/OOM/stages/auth/protocol/Character/gameplay and complete client455 acceptance remain open',
        'Missing original neutralBtrade_bel.r3e warning remains;invalid R3X lab warning is deliberate and counted separately',
    ]
    out=dict(status='CONFIRMED_SELECTED',scope='Ordinary lighting frame,day/night and289point software fog,real endpoint loaders,map texture-factor bind',script_sha256=sha(Path(__file__)),
             reference127=record(WS/'inventory/client455-sky-lighting-reference.json'),raw=previous['raw'],session=previous['session'],full_assembly=17,instructions=1538,context_bodies=contexts,
             sources=sources,engine=record(WS/engine['library']),old_engine=record(old),payload_changed_members=changed,unchanged_members=same,timestamp_only_members=stamp,headers_unchanged=True,
             ordinary_symbols_retained=required,CPU_tint_helper_retained='RF455_ApplySkyTint' in mapping,exposure_color_setter_retained='RF455_SetSkyFogExposureColor' in mapping,
             gaps=gaps,input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-sky-lighting-runtime-reference.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(dict(status=out['status'],changed=changed,unchanged=len(same),headers_unchanged=True,retained=required,CPU_helper=out['CPU_tint_helper_retained'],exposure_setter=out['exposure_color_setter_retained'])))


if __name__=='__main__':main()
