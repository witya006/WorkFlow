"""Validate pinned fade evidence and exact own-engine source provenance."""
import hashlib,json,struct
from pathlib import Path
from audit_client455_item_payloads import record
from audit_client455_texture_lifetime import archive_objects
from build_client455_x87_math import read_va
from checkpoint_client455_rvp_effects import load,require,sha,check
from compare_client_binaries import WS,pe


def main():
    file=WS/'artifacts/client455-progress/sky-fade124-reference.json';raw=json.loads(file.read_text());selected=set(raw['selected']);assembly={x['addr']:x for x in raw['assembly']};bounds={x['query']:x['fn'] for x in raw['bounds']['result']};require(selected==set(assembly)==set(bounds) and len(selected)==4,'Four selected fade functions')
    for at in selected:
        x=next(x for x in raw['functions'] if x['addr']==at and 'pages' in x);require(sum(p['line_count'] for p in x['pages'])==x['pages'][0]['total_lines'] and x['pages'][-1]['cursor']['done'],'Full selected pcode')
    for x in assembly.values():require(len(x['lines'])==x['total_instructions']==sum(p['instruction_count'] for p in x['pages']) and len({r['addr'] for r in x['lines']})==len(x['lines']) and x['pages'][-1]['cursor']['done'] and all(len(p['asm']['lines'])==p['instruction_count']<=100 for p in x['pages']),'Full unique bounded asm')
    instructions=sum(x['total_instructions'] for x in assembly.values());require(instructions==282,'Instruction total');sf=WS/'artifacts/client455-progress/sky-fade124-session.json';session=json.loads(sf.read_text());require(session['closed']['success'] and session['closed']['saved'] and session['after']['count']==0,'Owned IDA saved/closed/list0');pins=load_target();refs=[]
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        path=WS/f'work/client-reference/{folder}/RF_Online.bin';data=path.read_bytes();require(sha(path)==pins[key]['sha256'] and pe(data)['architecture']=='x86','Pinned x86 input');ranges=[dict(rva=hex(int(at,16)-0x400000),bytes=int(fn['size'],16),sha256=hashlib.sha256(read_va(data,int(at,16),int(fn['size'],16))).hexdigest()) for at,fn in sorted(bounds.items())];calls=[]
        for x in assembly.values():
            for row in x['lines']:
                if not row['instruction'].startswith('call ') or not row.get('refs'):continue
                at=int(row['addr'],16);b=read_va(data,at,5)
                if b[0]!=0xe8:continue
                target=int(row['refs'][0]['addr'],16);require(at+5+struct.unpack('<i',b[1:])[0]==target,'Decoded actual call');calls.append(dict(rva=hex(at-0x400000),target_rva=hex(target-0x400000)))
        literal_refs={(int(r['addr'],16),8 if r['name'].startswith('dbl_') else 4) for x in assembly.values() for row in x['lines'] for r in row.get('refs',[]) if r['name'].startswith(('flt_','dbl_')) and int(r['addr'],16)<0xc00000};literals=[dict(rva=hex(at-0x400000),bytes=n,hex=read_va(data,at,n).hex()) for at,n in sorted(literal_refs)]
        for at,fmt,value in [(0xb36b7c,'f',-.600100040435791015625),(0xb36b78,'f',.0000001),(0xb36b58,'d',struct.unpack('<f',struct.pack('<f',.0001))[0]),(0xada944,'f',.6),(0xb36b88,'f',.600100040435791015625),(0xab0060,'d',6),(0xb36b80,'d',600),(0xaaa3e8,'d',255)]:require(read_va(data,at,struct.calcsize(fmt))==struct.pack('<'+fmt,value),'Actual target literal '+hex(at))
        row=dict(sha256=sha(path),architecture='x86',image_base='0x400000',ranges=ranges,decoded_calls=calls,numeric_literals=literals);require(not refs or {k:v for k,v in row.items() if k!='sha256'}=={k:v for k,v in refs[0].items() if k!='sha256'},'Selected455 evidence equal on both pins');refs.append(row)
    engine=load('client455-startup-engine-build');require(engine['objects']==67 and len(engine['derived_sources'])==15 and engine['script_sha256']==sha(WS/'scripts/build_client455_engine_startup.py'),'Current derived67engine/15sources')
    for row in engine['base_sources']+engine['derived_sources']:check(row)
    sources=[record(WS/'scripts/native'/name) for name in ['client455_sky_fade_math.h','client455_sky_fade.inc']];require(engine['sky_fade']=={Path(x['file']).name:x['sha256'] for x in sources},'Exact fade sources');old=WS/'artifacts/client455-progress/engine-before124.lib';require(sha(old)=='e826ee1aaf9bb6b6f1f10a3470c411357f85eacf846b2436e9fa1aac1fe279cd','Exact123backup');a,b=archive_objects(old,True),archive_objects(WS/engine['library'],True);require(set(a)==set(b) and len(a)==67,'Same67objects');changed=[];stamps=[];same=[]
    for name in a:
        x,y=a[name]['payload'],b[name]['payload']
        if x==y:same.append(name)
        elif len(x)==len(y) and x[:4]+x[8:]==y[:4]+y[8:]:stamps.append(name)
        else:changed.append(name)
    require(len(changed)==1 and 'r3util' in changed[0].lower(),'Only intended r3util payload changed')
    gaps=['Full sky material flags4/8/10h/20h and actual day/night profile remain OPEN;target night coefficient comes from1154E08 in8B1F20,not directly from a guessed fraction','Special sky/atmosphere prepass8B1840 is gated byBF7344 set by map owners;sun/lensflare/scattering update/render/cleanup not restored;do not substitute a no-op','Full Draw2DSprite/render-state/lost-device/reset/reentry behavior is not proved by quad color and fog checks','Finite nearest/even selected inputs under24/53/64bits verified;NaN/Inf/overflow/otherRC modes and all caller states remain unaccepted','All remaining client-acceptance requirements,M6/M6F/M7/M9 OPEN']
    out=dict(status='CONFIRMED_SELECTED',scope='Sky fade state transitions and x87 numeric/color/alpha contract;full sky/atmosphere remains open',script_sha256=sha(Path(__file__)),raw=record(file),session=record(sf),full_assembly=4,instructions=instructions,references=refs,sources=sources,engine=record(WS/engine['library']),old_engine=record(old),payload_changed_members=changed,timestamp_only_members=stamps,unchanged_members=same,gaps=gaps,input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN');(WS/'inventory/client455-sky-fade-reference.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(asm=4,instructions=instructions,payload_changed=changed,stamps=len(stamps),same=len(same))))


def load_target():return json.loads((WS/'config/client-target.json').read_text())
if __name__=='__main__':main()
