"""Verify real CLevel sky dispatch,projection inputs and source-owned overlays."""
import hashlib,json,struct
from pathlib import Path
from audit_client455_texture_lifetime import archive_objects
from audit_client455_item_payloads import record
from build_client455_x87_math import read_va
from checkpoint_client455_rvp_effects import load,require,sha,check
from compare_client_binaries import WS,pe


def main():
    file=WS/'artifacts/client455-progress/sky-projection123-reference.json';raw=json.loads(file.read_text());selected=set(raw['selected']);bounds={x['query']:x['fn'] for x in raw['bounds']['result']};assembly={x['addr']:x for x in raw['assembly']};require(len(selected)==6 and set(bounds)==set(assembly)==selected,'Six selected functions')
    for addr in selected:
        x=[x for x in raw['functions'] if x['addr']==addr and 'pages' in x][-1];require(sum(p['line_count'] for p in x['pages'])==x['pages'][0]['total_lines'] and x['pages'][-1]['cursor']['done'],'Complete selected pcode')
    for x in assembly.values():require(len(x['lines'])==x['total_instructions']==sum(p['instruction_count'] for p in x['pages']) and len({r['addr'] for r in x['lines']})==len(x['lines']) and x['pages'][-1]['cursor']['done'] and all(p['instruction_count']==len(p['asm']['lines'])<=100 for p in x['pages']),'Complete bounded unique asm')
    require(sum(x['total_instructions'] for x in assembly.values())==1435,'Instruction total');sf=WS/'artifacts/client455-progress/sky-projection123-session.json';session=json.loads(sf.read_text());require(session['closed']['success'] and session['closed']['saved'] and session['after']['count']==0,'IDA closed/saved')
    pins=json.loads((WS/'config/client-target.json').read_text());refs=[]
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        path=WS/f'work/client-reference/{folder}/RF_Online.bin';data=path.read_bytes();require(sha(path)==pins[key]['sha256'] and pe(data)['architecture']=='x86','Pinned x86 input');ranges=[dict(rva=hex(int(at,16)-0x400000),bytes=int(fn['size'],16),sha256=hashlib.sha256(read_va(data,int(at,16),int(fn['size'],16))).hexdigest()) for at,fn in sorted(bounds.items())];calls=[]
        for x in assembly.values():
            for line in x['lines']:
                if not line['instruction'].startswith('call ') or not line.get('refs'):continue
                at=int(line['addr'],16);b=read_va(data,at,5)
                if b[0]!=0xe8:continue
                target=int(line['refs'][0]['addr'],16);require(at+5+struct.unpack('<i',b[1:])[0]==target,'Actual decoded call');calls.append(dict(rva=hex(at-0x400000),target_rva=hex(target-0x400000)))
        literal_refs={(int(r['addr'],16),8 if r['name'].startswith('dbl_') else 4) for x in assembly.values() for line in x['lines'] for r in line.get('refs',[]) if r['name'].startswith(('flt_','dbl_')) and int(r['addr'],16)<0xc00000}
        literals=[dict(rva=hex(at-0x400000),bytes=n,hex=read_va(data,at,n).hex()) for at,n in sorted(literal_refs)];require(struct.unpack('<f',read_va(data,0xaaa450,4))[0]==5,'Actual referenced initial scale constant')
        vtable=read_va(data,0xb38494,204);require(struct.unpack_from('<I',vtable,17*4)[0]==0x8e7a10 and read_va(data,0x8e9f77,6)==b'\xc7\x06'+struct.pack('<I',0xb38494),'Ordinary CLevel constructor/sky slot17')
        row=dict(sha256=sha(path),architecture='x86',image_base='0x400000',ranges=ranges,decoded_calls=calls,read_only_numeric_literals=literals,ordinary_vtable=dict(rva='0x738494',bytes=204,sha256=hashlib.sha256(vtable).hexdigest(),sky_slot=17,sky_rva='0x4e7a10'));require(not refs or {k:v for k,v in row.items() if k!='sha256'}=={k:v for k,v in refs[0].items() if k!='sha256'},'Both selected455 proofs equal');refs.append(row)
    engine=load('client455-startup-engine-build');require(engine['script_sha256']==sha(WS/'scripts/build_client455_engine_startup.py') and engine['objects']==67 and len(engine['derived_sources'])==15,'Current engine build')
    for row in engine['base_sources']+engine['derived_sources']+[engine['baseline_library'],engine['core_header_overlay'],engine['sky_header_overlay'],engine['camera_header_overlay'],engine['particle_header_overlay']]:check(row)
    source=WS/'scripts/native/client455_sky_projection.inc';require(engine['sky_projection']['client455_sky_projection.inc']==sha(source),'Exact sky projection source');old=WS/'artifacts/client455-progress/engine-before123.lib';require(sha(old)=='2fa70824eb20d19588c5043b438f12176f49e61065b31e68175da588e80bc1e4','Exact122 engine');a,b=archive_objects(old,True),archive_objects(WS/engine['library'],True);require(set(a)==set(b) and len(a)==67,'Same67 members');changed=[];stamp=[];same=[]
    for name in a:
        x,y=a[name]['payload'],b[name]['payload']
        if x==y:same.append(name)
        elif len(x)==len(y) and x[:4]+x[8:]==y[:4]+y[8:]:stamp.append(name)
        else:changed.append(name)
    gaps=['Selected ordinary CLevel sky wrapper/state init restored;full CSkyBox/entity/fade numeric/render behavior is not accepted by this wrapper alone','Direct orthographic stores were searched in8B0000..940000;InitCore false/scale5 verified,indirect/alias/UI/console writers and other ray/Character/alpha consumers remain open','Source-owned state extension changes layout;all own consumers must rebuild,not a target privateABI overlay','AllFP/NaN/zero scale/invalid near-far/OOM/lost-device/reset/reentry and full world/Character/stages/auth/gameplay/client-acceptance gaps remain;M9 OPEN']
    out=dict(status='CONFIRMED_SELECTED',scope='Ordinary CLevel near2 sky projection,conditional loaded sky/fade and perspective/orthographic restoration;fullrenderer open',script_sha256=sha(Path(__file__)),raw=record(file),session=record(sf),full_assembly=6,instructions=1435,references=refs,source=record(source),engine=record(WS/engine['library']),old_engine=record(old),core_header=engine['core_header_overlay'],sky_header=engine['sky_header_overlay'],payload_changed_members=changed,timestamp_only_members=stamp,unchanged_members=same,confirmed_initial_flag=0,confirmed_initial_scale=5,private_layout_equivalence=False,gaps=gaps,input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN');(WS/'inventory/client455-sky-projection-reference.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(asm=6,instructions=1435,payload_changed=len(changed),stamp=len(stamp),same=len(same))))


if __name__=='__main__':main()
