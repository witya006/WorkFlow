"""Pin real455 weather producers/map virtual owner and the connected source port."""
import hashlib
import json
import struct
from pathlib import Path
from audit_client455_item_payloads import record
from audit_client455_texture_lifetime import archive_objects
from build_client455_x87_math import read_va
from checkpoint_client455_rvp_effects import check,load,require,sha
from client455_normal_link_evidence import validate_normal_link
from compare_client_binaries import WS,pe


def main():
    rawfile=WS/'artifacts/client455-progress/weather-owner129-reference.json'
    sessionfile=rawfile.with_name('weather-owner129-session.json')
    raw=json.loads(rawfile.read_text());session=json.loads(sessionfile.read_text())
    require(session['saved']['ok'] and session['closed']['success'] and session['after']['count']==0,'Owned IDA saved and closed')
    selected=set(raw['selected']);assembly={x['addr']:x for x in raw['assembly']};cfg={x['addr']:x for x in raw['cfg']}
    require(len(selected)==6 and selected==set(assembly)==set(cfg),'Six selected full functions')
    for at in selected:
        a,g=assembly[at],cfg[at];addresses={int(x['addr'],16) for x in a['lines']}
        require(len(addresses)==len(a['lines'])==a['total_instructions']==sum(p['instruction_count'] for p in a['pages'])
                and a['pages'][-1]['cursor']['done'] and all(len(p['asm']['lines'])==p['instruction_count']<=100 for p in a['pages'])
                and g['cursor']['done'] and g['count']==g['total_blocks']==len(g['blocks'])
                and all(int(b['start'],16) in addresses for b in g['blocks'] if b['size']>0),'Full bounded assembly and all CFG block starts '+at)
        p=next(x for x in raw['functions'] if x['addr'].lower()==at)['pages']
        require(sum(x['line_count'] for x in p)==p[0]['total_lines'] and p[-1]['cursor']['done'],'Complete selected decompilation '+at)
    require(sum(x['total_instructions'] for x in assembly.values())==1546,'1546 selected instructions')
    bounds={x['query']:x['fn'] for x in raw['bounds']['result']}
    pins=json.loads((WS/'config/client-target.json').read_text());refs=[]
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        path=WS/f'work/client-reference/{folder}/RF_Online.bin';data=path.read_bytes();image=pe(data)
        require(sha(path)==pins[key]['sha256'] and image['architecture']=='x86' and image['image_base']==0x400000,'Pinned455 x86 reference')
        bodies=[]
        for at in sorted(selected):
            spans=[(int(at,16),int(at,16)+int(bounds[at]['size'],16))]+[(int(x['start'],16),int(x['end'],16)) for x in cfg[at]['blocks'] if x['size']>0]
            merged=[]
            for lo,hi in sorted(spans):
                if merged and lo<=merged[-1][1]:merged[-1][1]=max(hi,merged[-1][1])
                else:merged.append([lo,hi])
            for lo,hi in merged:
                bodies.append(dict(owner_rva=hex(int(at,16)-0x400000),rva=hex(lo-0x400000),bytes=hi-lo,sha256=hashlib.sha256(read_va(data,lo,hi-lo)).hexdigest()))
        require(len(bodies)==7 and any(x['rva']=='0x65e0d0' and x['bytes']==99 for x in bodies),'Complete CLevel constructor EH tail included')
        context=[dict(rva=hex(at-0x400000),bytes=size,hex=read_va(data,at,size).hex()) for at,size in [(0xb384c8,32),(0x8ea683,41),(0xaaa3e8,8)]]
        require(read_va(data,0xb384d0,4)==struct.pack('<I',0x8e77b0),'Actual CLevel virtual slot15 points to weather owner')
        require(read_va(data,0x8ea68a,3)==bytes.fromhex('8b523c') and read_va(data,0x8ea690,2)==bytes.fromhex('ffd2'),'Map load uses virtual slot15')
        calls=[]
        for at,target in [(0x8ea692,0x8f1700),(0x8ea6a7,0x8fdea0),(0x8e77d7,0x8b1210)]:
            b=read_va(data,at,5);require(b[0]==0xe8 and at+5+struct.unpack('<i',b[1:])[0]==target,'Decoded actual call/order')
            calls.append(dict(rva=hex(at-0x400000),target_rva=hex(target-0x400000)))
        require(struct.unpack('<d',read_va(data,0xaaa3e8,8))[0]==255,'Pinned double multiplier/divisor255')
        if refs:require(bodies==refs[0]['bodies'] and context==refs[0]['context'],'Both455 reference bodies and contexts equal')
        refs.append(dict(sha256=sha(path),architecture='x86',image_base='0x400000',bodies=bodies,context=context,decoded_calls=calls))
    script='\n'.join(x['instruction'] for x in assembly['0x90a4d0']['lines'])
    require('call __strupr' in script and 'call __strlwr' in script and script.index('call __strupr')<script.index('call __strlwr'),'Actual upper then lower tag dispatch')
    caps=Path('C:/Program Files (x86)/Windows Kits/10/Include/10.0.26100.0/shared/d3d9caps.h')
    require('#define D3DTEXOPCAPS_BUMPENVMAP' in caps.read_text() and '0x00200000' in next(x for x in caps.read_text().splitlines() if x.startswith('#define D3DTEXOPCAPS_BUMPENVMAP ')),'Official SDK bit21 is BUMPENVMAP')
    engine=load('client455-startup-engine-build');check(dict(file=engine['library'],sha256=engine['library_sha256']))
    require(engine['objects']==67 and len(engine['derived_sources'])==18 and engine['script_sha256']==sha(WS/'scripts/build_client455_engine_startup.py'),'Current engine67/18derived')
    for row in engine['base_sources']+engine['derived_sources']:check(row)
    sources=[record(WS/'scripts/native'/name) for name in ['client455_weather_parameters.h','client455_weather_parameters.inc','client455_level_weather.inc','client455_weather.cpp']]
    require(engine['weather_parameters']=={Path(x['file']).name:x['sha256'] for x in sources},'Current source-owned weather implementation')
    for name in ['level_header_overlay','camera_header_overlay']:check(engine[name])
    level=(WS/'work/client455-port/startup-engine/source/level.cpp').read_bytes()
    require(b'SetWeatherColor455(RF455_GetMaterialWeather());\n\tResetTexMemSize();' in level and level.index(b'SetWeatherColor455(RF455_GetMaterialWeather());')<level.index(b'mBsp->LoadBsp(real_bsp_name'),'Actual map load calls owner before reset/BSP')
    material=(WS/'work/client455-port/startup-engine/source/r3material.cpp').read_bytes()
    start=material.index(b'static _R3MATERIAL* LoadIndependenceMaterial(');end=material.index(b'void LoadR3X(',start);body=material[start:end]
    require(body.index(b'strupr(hole);')<body.index(b'RF455_ReadSkyFogToken(fp,hole);')<body.index(b'RF455_ReadWeatherTokens(fp,hole);'),'Ordinary script restores original tag-fold order')
    header=(WS/engine['level_header_overlay']['file']).read_bytes()
    require(b'virtual void SetWeatherColor455(DWORD color);' in header and b'DWORD mWeatherColor455;' in header,'Shared source ABI declares per-owner virtual setter and storage')
    before=load_backup('client455-startup-engine-build');old=WS/'artifacts/client455-progress/engine-before129.lib'
    require(sha(old)==before['library_sha256'],'Exact128 engine backup')
    a,b=archive_objects(old,True),archive_objects(WS/engine['library'],True);require(set(a)==set(b) and len(a)==67,'Same67 engine members')
    changed=[];same=[];stamp=[]
    for name in a:
        x,y=a[name]['payload'],b[name]['payload']
        (same if x==y else stamp if len(x)==len(y) and x[:4]+x[8:]==y[:4]+y[8:] else changed).append(name)
    require(before['camera_header_overlay']['sha256']!=engine['camera_header_overlay']['sha256'],'Shared class declaration changed,full client rebuild required')
    build=load('client455-normal-build');require(not build['build_exit'] and build['objects']==182 and build['canonical_kernel_objects']==20,'Successful full182/20 client build')
    link=load('client455-normal-link');require(validate_normal_link(link)=='PASS','Exact current normal link')
    mapping=(WS/link['map']['file']).read_text(errors='replace')
    require('SetWeatherColor455@CLevel' in mapping and 'RF455_ReadWeatherParameters' in mapping and 'RF455_GetMaterialWeather' in mapping,'Actual ordinary PE retains connected weather owner/producer path')
    gaps=['INS/Planet weather owners and other gameplay virtual callers remain open',
          'Material8000/CPU tint consumers and lensflare/local fog volumes remain open;1157CB8 is hardware BUMPENVMAP capability,not ordinary lighting enable',
          'Finite selected packed conversion and software fog are covered;all CRT/x87/RC/NaN/Inf/overflow/status-flag parity remains open',
          'Class overlay is source-owned ABI,not a claim of target binary CLevel layout or identical virtual slot numbers',
          'Selected neutralB camera looks upward with thin geometry strips visible;world/camera/material fidelity is not accepted',
          'Full lighting/world/device reset/stages/auth/protocol/Character/gameplay/client455 acceptance remain open']
    out=dict(status='CONFIRMED_SELECTED',scope='Packed script weather and ordinary map CLevel virtual owner,including tag-fold correction',script_sha256=sha(Path(__file__)),raw=record(rawfile),session=record(sessionfile),
             reused_sources=[record(WS/'artifacts/client455-progress'/x) for x in raw['reused_sources']],full_assembly=6,instructions=1546,verified_ranges=7,CFG_complete=True,references=refs,
             SDK_caps=dict(file=str(caps),sha256=sha(caps),field_offset=144,mask='0x00200000',meaning='D3DTEXOPCAPS_BUMPENVMAP'),
             sources=sources,engine=record(WS/engine['library']),old_engine=record(old),payload_changed_members=changed,unchanged_members=same,timestamp_only_members=stamp,
             shared_headers_changed=True,client_objects=182,kernel_objects=20,level_header_overlay=engine['level_header_overlay'],normal_executable=link['executable'],
             casefold_correction='126/128 case-sensitive script claims were wrong:90A5ED uppercase before FOG/ENV,90ACEC lowercase before weather/scene flags',
             gaps=gaps,input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-weather-owner-reference.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(dict(status=out['status'],full_assembly=6,instructions=1546,changed=changed,unchanged=len(same),shared_header_changed=True)))


def load_backup(name):return json.loads((WS/f'artifacts/client455-progress/{name}-before129.json').read_text())


if __name__=='__main__':main()
