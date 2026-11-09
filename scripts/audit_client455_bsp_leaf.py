"""Pin affine BSP queries and separate instance/planet owners from ordinary maps."""
import hashlib,json,struct
from pathlib import Path
from audit_client455_texture_lifetime import archive_objects
from audit_client455_item_payloads import record
from build_client455_x87_math import read_va
from checkpoint_client455_rvp_effects import load,require,sha,check
from compare_client_binaries import WS,pe


def main():
    file=WS/'artifacts/client455-progress/bsp-leaf122-reference.json';raw=json.loads(file.read_text());selected=set(raw['selected']);bounds={x['query']:x['fn'] for x in raw['bounds']['result']};assembly={x['addr']:x for x in raw['assembly']};require(len(selected)==11 and set(bounds)==set(assembly)==selected,'Selected new support')
    for addr in selected:
        x=[x for x in raw['functions'] if x['addr']==addr][-1];n=x['line_count']
        if addr=='0x8ed220':n+=raw['tails'][0]['line_count']
        require(n==x['total_lines'],'Complete selected pcode')
    cachefile=WS/'artifacts/client455-progress/world-frame120-reference.json';cache=json.loads(cachefile.read_text());cachedref=json.loads((WS/'artifacts/client455-progress/client455-world-frame-reference-before121.json').read_text());require(sha(cachefile)==cachedref['raw']['sha256'],'Pinned cached dispatch evidence')
    for addr in ['0x7c8600','0x8ecfa0']:
        assembly[addr]=next(x for x in cache['assembly'] if x['addr']==addr);bounds[addr]=next(x['fn'] for x in cache['bounds']['result'] if x['query']==addr)
    for x in assembly.values():
        require(len(x['lines'])==x['total_instructions']==sum(p['instruction_count'] for p in x['pages']) and len({r['addr'] for r in x['lines']})==len(x['lines']) and x['pages'][-1]['cursor']['done'],'Complete unique assembly')
        require(all(p['instruction_count']==len(p['asm']['lines'])<=120 for p in x['pages']),'No silent truncation')
    sessionfile=WS/'artifacts/client455-progress/bsp-leaf122-session.json';session=json.loads(sessionfile.read_text());require(session['closed']['success'] and session['closed']['saved'] and session['after']['count']==0,'Owned IDA closed/saved')
    pins=json.loads((WS/'config/client-target.json').read_text());refs=[]
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        path=WS/f'work/client-reference/{folder}/RF_Online.bin';data=path.read_bytes();require(sha(path)==pins[key]['sha256'] and pe(data)['architecture']=='x86','Pinned x86 reference');ranges=[dict(rva=hex(int(addr,16)-0x400000),bytes=int(fn['size'],16),sha256=hashlib.sha256(read_va(data,int(addr,16),int(fn['size'],16))).hexdigest()) for addr,fn in sorted(bounds.items())];calls=[]
        for x in assembly.values():
            for line in x['lines']:
                if not line['instruction'].startswith('call ') or not line.get('refs'):continue
                at=int(line['addr'],16);b=read_va(data,at,5)
                if b[0]!=0xe8:continue
                target=int(line['refs'][0]['addr'],16);require(at+5+struct.unpack('<i',b[1:])[0]==target,'Decoded direct call');calls.append(dict(rva=hex(at-0x400000),target_rva=hex(target-0x400000)))
        tables=[]
        for at in [0xb3872c,0xb3a0bc]:
            body=read_va(data,at,204);methods=struct.unpack('<51I',body);tables.append(dict(rva=hex(at-0x400000),bytes=204,sha256=hashlib.sha256(body).hexdigest(),load_rva=hex(methods[9]-0x400000),draw_rva=hex(methods[18]-0x400000)))
        require(tables[0]['load_rva']=='0x4ed220' and tables[0]['draw_rva']=='0x4ec850' and tables[1]['draw_rva']=='0x513800','Distinct instance/planet dispatch')
        rtti=[]
        for col,typ,name in [(0xb8ed1c,0xbf7ec0,b'.?AVCInstanceNode@@\0'),(0xb8eeb0,0xbf81b0,b'.?AVCPlanetLevel@@\0')]:
            require(struct.unpack('<I',read_va(data,col+12,4))[0]==typ and read_va(data,typ+8,len(name))==name,'Actual RTTI descriptor');rtti.append(dict(col_rva=hex(col-0x400000),type_rva=hex(typ-0x400000),name=name[:-1].decode(),sha256=hashlib.sha256(read_va(data,typ,8+len(name))).hexdigest()))
        require(read_va(data,0x8eb764,2)==b'\x33\xc0' or read_va(data,0x8eb764,2)==b'\x31\xc0','INS reader normal exit sets EAX zero')
        row=dict(sha256=sha(path),architecture='x86',image_base='0x400000',ranges=ranges,vtables=tables,rtti=rtti,decoded_calls=calls);require(not refs or {k:v for k,v in row.items() if k!='sha256'}=={k:v for k,v in refs[0].items() if k!='sha256'},'Both pinned references agree');refs.append(row)
    oldreport=json.loads((WS/'artifacts/client455-progress/client455-startup-engine-build-before122.json').read_text());engine=load('client455-startup-engine-build');require(engine['script_sha256']==sha(WS/'scripts/build_client455_engine_startup.py') and engine['objects']==67 and len(engine['derived_sources'])==14,'Current engine')
    for key in ['bsp_header_overlay','camera_header_overlay','particle_header_overlay','sprite_header_overlay']:require(engine[key]==oldreport[key],'Shared declarations unchanged');check(engine[key])
    for row in engine['base_sources']+engine['derived_sources']+[engine['baseline_library']]:check(row)
    source=WS/'scripts/native/client455_bsp_leaf.inc';require(engine['bsp_leaf']['client455_bsp_leaf.inc']==sha(source),'Exact restored leaf source');old=WS/'artifacts/client455-progress/engine-before122.lib';require(sha(old)==oldreport['library_sha256']=='12534d28dfeccda98c5e2cdffecc6621ffde7b3a95810501f2a513f01911e810','Exact121 engine');a,b=archive_objects(old,True),archive_objects(WS/engine['library'],True);require(set(a)==set(b) and len(a)==67,'Same67 members');changed=[];stamp=[];same=[]
    for name in a:
        x,y=a[name]['payload'],b[name]['payload']
        if x==y:same.append(name)
        elif len(x)==len(y) and x[:4]+x[8:]==y[:4]+y[8:]:stamp.append(name)
        else:changed.append(name)
    require(len(changed)==1 and changed[0].lower().endswith('bsp.obj'),'Only BSP payload changed')
    gaps=['Full ReadyBspRender local camera/visibility/frustum/alpha/entity cache and placed-instance owners are not restored by GetLeafNum alone','INS reader returns0 on all normal exits in the pinned body;its side effects,Error paths,console selection and full ILevel/INS/Planet source remain open;absence of assets is not completeness proof','Finite affine examples do not accept allFP/CRT/NaN/singular/unsafe IDs/recursive cycles/concurrency/OOM/privateABI domains','Full ordinary projection/sky/alpha/shadow/device reset,Character/stages/input/auth/protocol/gameplay and previous client-acceptance gaps remain;M9 OPEN']
    out=dict(status='CONFIRMED_SELECTED',scope='Actual inverse-affine BSP leaf lookup and distinct CInstanceNode/INS/CPlanetLevel owners;full world open',script_sha256=sha(Path(__file__)),raw=record(file),session=record(sessionfile),cached_raw=record(cachefile),new_full_assembly=11,new_instructions=742,full_assembly=len(assembly),instructions=sum(x['total_instructions'] for x in assembly.values()),references=refs,source=record(source),engine=record(WS/engine['library']),old_engine=record(old),changed_members=changed,timestamp_only_members=stamp,unchanged_members=same,shared_headers_unchanged=True,gaps=gaps,input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-bsp-leaf-reference.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(asm=out['full_assembly'],instructions=out['instructions'],changed=changed,stamp=len(stamp),same=len(same))))


if __name__=='__main__':main()
