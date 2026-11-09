"""Verify class dispatch before accepting camera/world/light method behavior."""
import hashlib,json,struct
from pathlib import Path
from audit_client455_texture_lifetime import archive_objects
from audit_client455_item_payloads import record
from build_client455_x87_math import read_va
from checkpoint_client455_rvp_effects import load,require,sha,check
from compare_client_binaries import WS,pe

def main():
    raw_file=WS/'artifacts/client455-progress/world-frame120-reference.json';raw=json.loads(raw_file.read_text());selected=set(raw['selected']+raw['extra_selected']);bounds={x['query']:x['fn'] for x in raw['bounds']['result']+raw['extra_bounds']['result']};functions={x['addr']:x for x in raw['functions'] if x['addr'] in selected};assembly={x['addr']:x for x in raw['assembly']};require(len(selected)==26 and set(bounds)==set(functions)==set(assembly)==selected,'Selected dispatch/light coverage')
    for addr,x in functions.items():
        if addr in ['0x8fe980','0x8fec90']:
            tail=next(t for t in raw['extra_tails'] if t['addr']==addr);require(x['line_count']+tail['line_count']==x['total_lines'] and tail['cursor']['done'],'Complete geometry pages')
        elif addr=='0x8c4ec0':require(x['line_count']+raw['declaration_page']['line_count']+raw['declaration_tail']['line_count']==x['total_lines']==429 and raw['declaration_tail']['cursor']['done'],'Complete declaration pages')
        else:require(x['cursor']['done'] and not x.get('truncated') and x['line_count']==x['total_lines'],'Full selected pcode')
    for x in assembly.values():
        require(len(x['lines'])==x['total_instructions']==sum(p['instruction_count'] for p in x['pages']) and len({r['addr'] for r in x['lines']})==len(x['lines']) and x['pages'][-1]['cursor']['done'],'Full unique assembly')
        require(all(len(p['asm']['lines'])==p['instruction_count']<=120 for p in x['pages']),'No silent MCP truncation')
    pins=json.loads((WS/'config/client-target.json').read_text());references=[]
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        path=WS/f'work/client-reference/{folder}/RF_Online.bin';image=path.read_bytes();require(sha(path)==pins[key]['sha256'] and pe(image)['architecture']=='x86','Pinned x86 client');ranges=[dict(rva=hex(int(at,16)-0x400000),bytes=int(fn['size'],16),sha256=hashlib.sha256(read_va(image,int(at,16),int(fn['size'],16))).hexdigest()) for at,fn in sorted(bounds.items())]
        tables=[]
        for at in [0xb38494,0xb3872c]:
            data=read_va(image,at,204);table=struct.unpack('<51I',data);tables.append(dict(rva=hex(at-0x400000),bytes=204,sha256=hashlib.sha256(data).hexdigest(),methods=[hex(x-0x400000) for x in table]))
        require(tables[0]['methods'][9]=='0x4ea220' and tables[0]['methods'][14]=='0x4e7910' and tables[0]['methods'][18]=='0x4e7c40' and tables[0]['methods'][27]=='0x4e7850','Actual CLevel vtable dispatch')
        require(tables[1]['methods'][9]=='0x4ed220' and tables[1]['methods'][14]=='0x4ec190' and tables[1]['methods'][27]=='0x4eb7f0','Separate INS vtable dispatch')
        require(read_va(image,0x8e9f77,6)[:2]==b'\xc7\x06' and struct.unpack('<I',read_va(image,0x8e9f79,4))[0]==0xb38494,'CLevel constructor writes its vtable')
        # Decode ordinary map allocation/new call/virtual slot9 directly from bytes.
        calls=[]
        for fn in assembly.values():
            for line in fn['lines']:
                if not line['instruction'].startswith('call ') or not line.get('refs'):continue
                at=int(line['addr'],16);b=read_va(image,at,5)
                if b[0]!=0xe8:continue
                dest=int(line['refs'][0]['addr'],16);require(at+5+struct.unpack('<i',b[1:])[0]==dest,'Actual decoded call');calls.append(dict(rva=hex(at-0x400000),target_rva=hex(dest-0x400000)))
        require(any(x==dict(rva='0x3c8703',target_rva='0x4e9f40') for x in calls),'Ordinary map constructs actual CLevel')
        row=dict(sha256=sha(path),architecture='x86',image_base='0x400000',ranges=ranges,vtables=tables,decoded_calls=calls);require(not references or {k:v for k,v in row.items() if k!='sha256'}=={k:v for k,v in references[0].items() if k!='sha256'},'Both455 selected bodies/tables equal');references.append(row)
    session_file=WS/'artifacts/client455-progress/world-frame120-session.json';session=json.loads(session_file.read_text());require(session['closed']['success'] and session['closed']['saved'] and session['after']['count']==0,'Owned IDA saved/closed')
    extra_session_file=WS/'artifacts/client455-progress/world-frame120-extra-session.json';extra_session=json.loads(extra_session_file.read_text());require(extra_session['closed']['success'] and extra_session['closed']['saved'] and extra_session['after']['count']==0,'Second owned IDA saved/closed')
    old=WS/'artifacts/client455-progress/engine-before120.lib';require(sha(old)=='9ae6ace8b0f34718c7708c4d62847b54b6310d3e0c254216028f0bb317279b74','Exact119 engine');engine=load('client455-startup-engine-build');require(engine['objects']==67 and len(engine['derived_sources'])==13 and engine['script_sha256']==sha(WS/'scripts/build_client455_engine_startup.py'),'Current engine build')
    for row in engine['base_sources']+engine['derived_sources']+[engine['baseline_library']]:check(row)
    a,b=archive_objects(old,True),archive_objects(WS/engine['library'],True);code=[];stamp=[];same=[]
    for name in a:
        x,y=a[name]['payload'],b[name]['payload']
        if x==y:same.append(name)
        elif len(x)==len(y) and x[:4]+x[8:]==y[:4]+y[8:]:stamp.append(name)
        else:code.append(name)
    require(len(a)==len(b)==67 and len(code)==1 and Path(code[0]).name.lower()=='level.obj','Only map view behavior changed')
    result=dict(status='CONFIRMED_SELECTED',scope='Actual CLevel/INS dispatch distinction,map view correction and selected dynamic-light queue/render contracts;full world/gameplay open',script_sha256=sha(Path(__file__)),raw=record(raw_file),session=record(session_file),extra_session=record(extra_session_file),references=references,full_assembly=26,instructions=sum(x['total_instructions'] for x in assembly.values()),engine=record(WS/engine['library']),old_engine=record(old),code_changed_members=code,timestamp_only_members=stamp,unchanged_members=same,correction119='119 misidentified8EB7F0 as ordinary map and8E7850 as Empty;actual ordinary CLevel ctor/vtable/owner prove8E7850,INS prove8EB7F0.119previous-view acceptance is retracted;current source uses input/current view',source=record(WS/'scripts/native/client455_level_view.inc'),gaps=['FullILevel/Empty/INS source and all virtual methods remain unported;selected dispatch proof is not privateABI parity','Confirmed unported geometry differences:regular light skipsAttr0x10,leafcap128,facecap5000;magic skipsAttr0x30,requires bboxwidth<=1000/both endpoints inside root bounds,saturates faceindex2999,batch2000;target uses owned CBsp worldmatrix and explicit declaration;legacy path still differs','Full map frame/calculations/environment/projection/sky/alpha/shadow/device/reset/lighting/Character/gameplay not proven by selected queue and GPU examples','AllFP/oldCRT/invalid counts/OOM/NaN/concurrency/RNG interleaving and previous client-acceptance gaps remain open'],input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-world-frame-reference.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(asm=26,instructions=result['instructions'],code=code,stamp=len(stamp),same=len(same))))

if __name__=='__main__':main()
