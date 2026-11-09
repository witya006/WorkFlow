"""Pin-comparison and source provenance for selected sky2/day/material changes."""
import hashlib,json,struct
from pathlib import Path
from audit_client455_item_payloads import record
from audit_client455_texture_lifetime import archive_objects
from build_client455_x87_math import read_va
from checkpoint_client455_rvp_effects import load,require,sha,check
from compare_client_binaries import WS,pe


def main():
    file=WS/'artifacts/client455-progress/sky-material125-reference.json';raw=json.loads(file.read_text());selected=set(raw['selected']);assembly={x['addr']:x for x in raw['assembly']};bounds={x['query']:x['fn'] for x in raw['bounds']['result']};require(selected==set(assembly)==set(bounds) and len(selected)==8,'Eight complete selected functions')
    for at in selected:
        x=next(x for x in raw['functions'] if x['addr'].lower()==at and 'pages' in x);require(sum(p['line_count'] for p in x['pages'])==x['pages'][0]['total_lines'] and x['pages'][-1]['cursor']['done'],'Complete selected pcode')
    for x in assembly.values():require(len(x['lines'])==x['total_instructions']==sum(p['instruction_count'] for p in x['pages']) and len({r['addr'] for r in x['lines']})==len(x['lines']) and x['pages'][-1]['cursor']['done'] and all(len(p['asm']['lines'])==p['instruction_count']<=100 for p in x['pages']),'Complete bounded unique assembly')
    total=sum(x['total_instructions'] for x in assembly.values());require(total==1696,'Instruction total');sf=WS/'artifacts/client455-progress/sky-material125-session.json';session=json.loads(sf.read_text());require(session['closed']['success'] and session['closed']['saved'] and session['after']['count']==0,'Owned IDA saved/closed/list0');pins=json.loads((WS/'config/client-target.json').read_text());refs=[]
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        path=WS/f'work/client-reference/{folder}/RF_Online.bin';data=path.read_bytes();require(sha(path)==pins[key]['sha256'] and pe(data)['architecture']=='x86','Pinned x86 input');ranges=[dict(rva=hex(int(at,16)-0x400000),bytes=int(fn['size'],16),sha256=hashlib.sha256(read_va(data,int(at,16),int(fn['size'],16))).hexdigest()) for at,fn in sorted(bounds.items())];calls=[]
        for x in assembly.values():
            for row in x['lines']:
                if not row['instruction'].startswith('call ') or not row.get('refs'):continue
                at=int(row['addr'],16);b=read_va(data,at,5)
                if b[0]!=0xe8:continue
                target=int(row['refs'][0]['addr'],16);require(at+5+struct.unpack('<i',b[1:])[0]==target,'Decoded direct call');calls.append(dict(rva=hex(at-0x400000),target_rva=hex(target-0x400000)))
        literal_refs={(int(r['addr'],16),8 if r['name'].startswith('dbl_') else 4) for x in assembly.values() for row in x['lines'] for r in row.get('refs',[]) if r['name'].startswith(('flt_','dbl_')) and int(r['addr'],16)<0xc00000};literals=[dict(rva=hex(at-0x400000),bytes=n,hex=read_va(data,at,n).hex()) for at,n in sorted(literal_refs)]
        for at,fmt,v in [(0xb36a88,'d',.791666686534881591796875),(0xb36a00,'d',.854166686534881591796875),(0xb369f8,'d',.20833332836627960205078125),(0xb369f0,'f',.3333333432674407958984375),(0xb369e8,'d',.12500001490116119384765625),(0xada090,'d',16),(0xaaa3e8,'d',255)]:require(read_va(data,at,struct.calcsize(fmt))==struct.pack('<'+fmt,v),'Referenced night/alpha literal')
        require(read_va(data,0xbf7344,4)==struct.pack('<I',1),'File-backed enable default1');stub=read_va(data,0xa95770,10);require(stub[:6]==b'\xb9'+struct.pack('<I',0x1154df4)+b'\xe8' and 0xa9577a+struct.unpack('<i',stub[6:])[0]==0x900ab0,'Actual profile initializer calls zero-night constructor');require(read_va(data,0xaa8700,4)==struct.pack('<I',0xa95770),'Actual readonly initializer table registration');aux=[dict(rva=hex(at-0x400000),bytes=n,hex=read_va(data,at,n).hex()) for at,n in [(0xbf7344,4),(0xa95770,10),(0xaa86f4,28)]]
        row=dict(sha256=sha(path),architecture='x86',image_base='0x400000',ranges=ranges,decoded_calls=calls,numeric_literals=literals,initialization=aux);require(not refs or {k:v for k,v in row.items() if k!='sha256'}=={k:v for k,v in refs[0].items() if k!='sha256'},'Both455 selected evidence equal');refs.append(row)
    engine=load('client455-startup-engine-build');require(engine['objects']==67 and len(engine['derived_sources'])==16 and engine['script_sha256']==sha(WS/'scripts/build_client455_engine_startup.py'),'Current67engine/16derived');sources=[record(WS/'scripts/native'/n) for n in ['client455_sky_day.h','client455_sky_day.inc','client455_map_sky.inc','client455_sky_material.inc']];require(engine['sky_material']=={Path(x['file']).name:x['sha256'] for x in sources},'Exact new sources')
    for row in engine['base_sources']+engine['derived_sources']:check(row)
    old=WS/'artifacts/client455-progress/engine-before125.lib';require(sha(old)=='9e1b9c677ee4d9fe62f01e3186a3a481489950d3afccd02e1c83561febf7fb9f','Exact124backup');a,b=archive_objects(old,True),archive_objects(WS/engine['library'],True);require(set(a)==set(b) and len(a)==67,'Same67members');changed=[];stamp=[];same=[]
    for name in a:
        x,y=a[name]['payload'],b[name]['payload']
        if x==y:same.append(name)
        elif len(x)==len(y) and x[:4]+x[8:]==y[:4]+y[8:]:stamp.append(name)
        else:changed.append(name)
    require(len(changed)==2 and {Path(x.replace('\\','/')).name for x in changed}=={'level.obj','skybox.obj'},'Only intended level/sky payload changes');previous=json.loads((WS/'artifacts/client455-progress/client455-startup-engine-build-before125.json').read_text());headers=['core_header_overlay','sky_header_overlay','bsp_header_overlay','camera_header_overlay','particle_header_overlay'];require(all(engine[x]==previous[x] for x in headers),'Shared declarations/layouts unchanged')
    gaps=['Only night-weight slice of8B1F20 lighting tail restored;sun matrices,exposure/scattering/light colors/day-night fog and other lighting updates remain open','Enabled special atmosphere prepass8B1840 is absent,not replaced by a success/no-op implementation;full sky2 images are not455visual equivalence','Ordinary CLevel map selection restored;INS/Planet selection/update owners remain separate gaps','Finite nearest/even night cases and selected material/layer submissions verified;allRC/NaN/Inf/OOM/lost-reset/recreate/reentry and full renderer/gameplay/client-acceptance remain open','NeutralB references missing original e_neutrala/trade_bel/trade_bel.r3e;warning retained,not silently substituted']
    out=dict(status='CONFIRMED_SELECTED',scope='Ordinary sky2/legacy selection,enable state,night-weight slice and sky material flags;fullatmosphere remains open',script_sha256=sha(Path(__file__)),raw=record(file),session=record(sf),full_assembly=8,instructions=total,references=refs,sources=sources,engine=record(WS/engine['library']),old_engine=record(old),payload_changed_members=changed,timestamp_only_members=stamp,unchanged_members=same,headers_unchanged=True,gaps=gaps,input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN');(WS/'inventory/client455-sky-material-reference.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(asm=8,instructions=total,changed=changed,stamp=len(stamp),same=len(same))))


if __name__=='__main__':main()
