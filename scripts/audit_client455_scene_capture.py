"""Pin scene-resource/capture contracts and retain the larger refraction backlog."""
import hashlib,json
from pathlib import Path
from compare_client_binaries import WS,pe
from build_client455_x87_math import read_va
from audit_client455_item_payloads import record
from audit_client455_texture_lifetime import archive_objects
from checkpoint_client455_rvp_effects import require,check,load,sha
from client455_normal_link_evidence import validate_normal_link

def main():
    file=WS/'artifacts/client455-progress/refraction137-reference.json';raw=json.loads(file.read_text())
    bounds={x['query']:x['fn'] for x in raw['ranges']['result']};cfg={x['addr']:x for x in raw['cfg']['result']}
    spans=[];total=0;tail_count=0
    for f in raw['assembly']:
        addr=f['addr'];pages=f['pages'];lines=[x for p in pages for x in p['asm']['lines']]
        addresses={int(x['addr'],16) for x in lines};linear=len(lines)
        require(linear==len(addresses)==pages[0]['total_instructions']==sum(p['instruction_count'] for p in pages) and all(p['instruction_count']==len(p['asm']['lines'])<=100 for p in pages) and pages[-1]['cursor']['done'],'Full paginated assembly '+addr)
        for tail in raw['tails']:
            if tail['owner']!=addr:continue
            for query in tail['result']['result']:
                require(query['cursor']['done'] and query['count']==len(query['matches']) and not query['truncated'],'Complete lower instruction chunk')
                tail_addresses={int(x['addr'],16) for x in query['matches']};require(not addresses&tail_addresses,'Distinct lower chunk');addresses|=tail_addresses;tail_count+=len(tail_addresses)
        blocks=cfg[addr];require(blocks['count']==blocks['total_blocks']==len(blocks['blocks']) and blocks['cursor']['done'] and all(int(b['start'],16) in addresses for b in blocks['blocks'] if b['size']>0),'All positive CFG starts including lower chunks '+addr)
        p=next(x['pages'] for x in raw['functions'] if x['addr']==addr)
        require(sum(x['line_count'] for x in p)==p[0]['total_lines'] and p[-1]['cursor']['done'],'Full selected pseudocode '+addr)
        ranges=[(int(addr,16),int(addr,16)+int(bounds[addr]['size'],16))]+[(int(b['start'],16),int(b['end'],16)) for b in blocks['blocks'] if b['size']>0];merged=[]
        for lo,hi in sorted(ranges):
            if merged and lo<=merged[-1][1]:merged[-1][1]=max(hi,merged[-1][1])
            else:merged.append([lo,hi])
        spans += [(addr,lo,hi-lo) for lo,hi in merged];total+=len(addresses)
    require(set(raw['selected'])==set(bounds)==set(cfg)=={x['addr'] for x in raw['assembly']} and len(bounds)==12 and total==1855 and tail_count==8,'Twelve complete selected functions including8lower-tail instructions')
    sessionfile=WS/'artifacts/client455-progress/refraction137-session.json';s=json.loads(sessionfile.read_text());require(s['saved']['ok'] and s['closed']['success'] and s['closed']['saved'] and s['after']['count']==0,'Owned IDA saved/closed')
    pins=json.loads((WS/'config/client-target.json').read_text());refs=[]
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        path=WS/f'work/client-reference/{folder}/RF_Online.bin';data=path.read_bytes();require(sha(path)==pins[key]['sha256'] and pe(data)['architecture']=='x86','Pinned x86 client455')
        rows=[dict(owner_rva=hex(int(owner,16)-0x400000),rva=hex(at-0x400000),bytes=n,sha256=hashlib.sha256(read_va(data,at,n)).hexdigest()) for owner,at,n in spans]
        if refs:require(rows==refs[0]['ranges'],'Both455resource/refraction ranges agree')
        refs.append(dict(sha256=sha(path),architecture='x86',image_base='0x400000',ranges=rows))
    before=WS/'artifacts/client455-progress/before137';snapshot=before/'manifest.json'
    for row in json.loads(snapshot.read_text()):check(row)
    engine=load('client455-startup-engine-build');previous=json.loads((before/'inventory/client455-startup-engine-build.json').read_text())
    for key in ['camera_header_overlay','particle_header_overlay','vertex_header_overlay','material_header_overlay']:
        check(engine[key]);require(engine[key]['sha256']==previous[key]['sha256'],'Shared declarations unchanged137')
    for row in engine['base_sources']+engine['derived_sources']:check(row)
    for name,value in engine['scene_capture'].items():require(value==sha(WS/'scripts/native'/name),'Current scene resource source')
    old,new=archive_objects(before/previous['library'],True),archive_objects(WS/engine['library'],True);require(set(old)==set(new) and len(new)==67,'Same67engine objects');changed=[]
    for name in old:
        a,b=old[name]['payload'],new[name]['payload']
        if a!=b and not(len(a)==len(b) and a[:4]+a[8:]==b[:4]+b[8:]):changed.append(name)
    require({Path(x).name.lower() for x in changed}=={'r3d3d8.obj'},'Only scene/device owner payload changes')
    link=load('client455-normal-link');require(validate_normal_link(link)=='PASS' and any(x['sha256']==engine['library_sha256'] for x in link['libraries']),'Actual normal own client uses current engine')
    original=Path(json.loads((WS/'config/paths.json').read_text())['client_455'])/'System/PerbMap.dds'
    out=dict(status='CONFIRMED_SELECTED',scope='Ordinary InitFullScreenEffect/ReleaseFullScreenEffect five resource owners and captured-scene helper;larger refraction functions are reference contracts,not implemented render acceptance',
        script=record(Path(__file__)),raw=record(file),session=record(sessionfile),references=refs,selected_full_functions=12,instructions=total,lower_tail_instructions=tail_count,verified_ranges=len(spans),CFG_complete=True,
        resource_owner_rvas=['0xd64038','0xd63fe8','0xd63fc0','0xd64010','0xd64060'],resource_configuration=['screen-width/height depth','512x512 depth','512x512 no-depth','512x512 depth','256x256 no-depth'],
        perturbation_input=dict(original=str(original),exists=original.is_file(),**(dict(sha256=sha(original)) if original.is_file() else {})),
        engine=record(WS/engine['library']),normal_executable=link['executable'],normal_link_sha256=sha(WS/'inventory/client455-normal-link.json'),snapshot=record(snapshot),changed_members=changed,shared_headers_changed=False,
        ordinary_resource_owner=True,capture_helper_normal_game_caller_connected=False,
        gaps=load('client455-shader-text-checkpoint')['gaps']+[
            'Full Fraction/particle azirang producers/draw owners and BBoShasi capture-enabled Begin/Clear/End/postprocess routing remain unported;ordinary stage integration takes priority after137',
            '8CE2A0 binds Fraction,not Plazma.8CE0A0 uploads unowned stack data toVS13 and viewport data toPS15;no fabricated defaults or full equivalence claim',
            '8CE020 retains GetSurfaceLevel reference and ignores HRESULTs;lab alone compensates its retained reference after observation.Production balanced capture lifetime is not claimed',
            'PerbMap is missing as a loose file in pinned installation;positive load uses an explicitly synthetic DDS fixture,not a455asset substitute',
            'Existing wrapper allocates640x500 before publishing640x480 viewport in this lab;full wrapper/reset/lost-device/partial allocation failures remain open',
            'All client-acceptance M6/M6F/M7/M9 requirements remain open;no complete Title/Login/ordinary game loop claimed'],
        input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-scene-capture-reference.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(functions=12,instructions=total,ranges=len(spans),changed=changed,PerbMap=original.is_file())))

if __name__=='__main__':main()
