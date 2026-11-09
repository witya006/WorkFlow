"""Pin selected quake contracts to both455 binaries and current own engine."""
import hashlib,json,struct
from pathlib import Path
from audit_client455_texture_lifetime import archive_objects
from audit_client455_item_payloads import record
from build_client455_x87_math import read_va
from checkpoint_client455_rvp_effects import check,load,require,sha
from compare_client_binaries import WS,pe

def main():
    raw_file=WS/'artifacts/client455-progress/quake119-reference.json';raw=json.loads(raw_file.read_text());session_file=WS/'artifacts/client455-progress/quake119-session.json';session=json.loads(session_file.read_text());require(session['closed']['success'] and session['closed']['saved'] and session['after']['count']==0,'Owned IDA saved/closed')
    functions={x['addr']:x for x in raw['functions']};bounds={x['query']:x['fn'] for x in raw['bounds']['result']};assembly={x['addr']:x for x in raw['assembly']};require(len(functions)==len(bounds)==len(assembly)==17 and set(functions)==set(bounds)==set(assembly),'Selected function coverage')
    for addr,x in functions.items():
        if addr=='0x8ea220':require(x['line_count']+raw['level_load_tail']['line_count']==x['total_lines']==396 and raw['level_load_tail']['cursor']['done'],'Complete load pcode pages')
        else:require(x['cursor']['done'] and not x['truncated'] and x['line_count']==x['total_lines'],'Full pcode')
    for addr,x in assembly.items():
        require(len(x['lines'])==x['total_instructions']==sum(p['instruction_count'] for p in x['pages']) and len({a['addr'] for a in x['lines']})==len(x['lines']) and x['pages'][-1]['cursor']['done'],'Full assembly pages')
        for p in x['pages']:require(len(p['asm']['lines'])==p['instruction_count'] and p['instruction_count']<=120,'No MCP response truncation')
    cached=raw['cached_scheduler'];check(cached['reference']);a=cached['assembly'];require(a['cursor']['done'] and len(a['asm']['lines'])==a['instruction_count']==a['total_instructions']==629,'Full cached scheduler assembly');bounds[cached['bound']['query']]=cached['bound']['fn'];assembly[a['addr']]=dict(lines=a['asm']['lines'],total_instructions=a['instruction_count'])
    constants=[(0xb36b08,8,'period bias double(float0.999)'),(0xb36b50,8,'42ms interpolation divisor'),(0xbf736c,4,'initial interpolation period5'),(0xbf7374,4,'vertical amplitude scale1')]
    pins=json.loads((WS/'config/client-target.json').read_text());references=[]
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        file=WS/f'work/client-reference/{folder}/RF_Online.bin';image=file.read_bytes();require(sha(file)==pins[key]['sha256'] and pe(image)['architecture']=='x86' and pe(image)['image_base']==0x400000,'Pinned455 x86/base')
        ranges=[dict(rva=hex(int(addr,16)-0x400000),bytes=int(fn['size'],16),sha256=hashlib.sha256(read_va(image,int(addr,16),int(fn['size'],16))).hexdigest()) for addr,fn in sorted(bounds.items())]
        data=[dict(rva=hex(at-0x400000),bytes=n,role=role,sha256=hashlib.sha256(read_va(image,at,n)).hexdigest()) for at,n,role in constants]
        require(struct.unpack('<d',read_va(image,0xb36b08,8))[0]==struct.unpack('<f',struct.pack('<f',.999))[0] and struct.unpack('<d',read_va(image,0xb36b50,8))[0]==42 and struct.unpack('<I',read_va(image,0xbf736c,4))[0]==5 and struct.unpack('<f',read_va(image,0xbf7374,4))[0]==1,'Exact constants')
        calls=[]
        for x in assembly.values():
            for line in x['lines']:
                if not line['instruction'].startswith('call ') or not line.get('refs'):continue
                at=int(line['addr'],16);b=read_va(image,at,5)
                if b[0]!=0xe8:continue
                target=int(line['refs'][0]['addr'],16);require(at+5+struct.unpack('<i',b[1:])[0]==target,'Actual decoded target call');calls.append(dict(rva=hex(at-0x400000),target_rva=hex(target-0x400000)))
        row=dict(sha256=sha(file),architecture='x86',image_base='0x400000',ranges=ranges,constants=data,decoded_calls=calls);require(not references or {k:v for k,v in row.items() if k!='sha256'}=={k:v for k,v in references[0].items() if k!='sha256'},'Both455 selected ranges/calls equal');references.append(row)
    old=WS/'artifacts/client455-progress/engine-before119.lib';require(sha(old)=='dce960bd12d8f82257edd760ebdbc73127b1f372b01a178141028cd397b4e656','Exact118 engine baseline');engine=load('client455-startup-engine-build');new=WS/engine['library'];require(engine['objects']==67 and len(engine['derived_sources'])==13 and engine['script_sha256']==sha(WS/'scripts/build_client455_engine_startup.py'),'Current67 derived engine')
    for row in engine['derived_sources']+engine['base_sources']+[engine['baseline_library']]:check(row)
    for name,digest in engine['quake'].items():require(sha(WS/'scripts/native'/name)==digest,'Prepared quake source')
    before,after=archive_objects(old,True),archive_objects(new,True);require(set(before)==set(after) and len(before)==67,'Same archive67 members');code=[];stamp=[];same=[]
    for name in before:
        x,y=before[name]['payload'],after[name]['payload']
        if x==y:same.append(name)
        elif len(x)==len(y) and x[:4]+x[8:]==y[:4]+y[8:]:stamp.append(name)
        else:code.append(name)
    require(len(code)==2 and {Path(x).name.lower() for x in code}=={'r3util.obj','level.obj'},'Only quake utility/map code changed')
    gaps=['Sway activation/control writer7E2AD0 observed statically but not restored to ordinary game input/action flow','Empty-level8E7850 and INS variants have separate behavior;map CLevel proof does not accept them','Provider timer/toggle negative branch/live game timing/full world frame/light/compositing and allFP/oldCRT/privateABI/NaN/zero-heading/modulo0/overflow/RNG-interleaving remain open','All previous client acceptance gaps;M6/M6F/M7/M9 open']
    result=dict(status='CONFIRMED_SELECTED',scope='Selected quake/sway/attenuation,map previous-view publication and successful map-load sway stop;full camera/gameplay/world acceptance open',script_sha256=sha(Path(__file__)),raw=record(raw_file),session=record(session_file),cached_scheduler=record(WS/'inventory/client455-effect-runtime-reference.json'),references=references,new_full_assembly=17,new_instructions=sum(x['total_instructions'] for x in raw['assembly']),full_assembly=18,instructions=sum(x['total_instructions'] for x in assembly.values()),old_engine=record(old),engine=record(new),code_changed_members=code,timestamp_only_members=stamp,unchanged_members=same,source=[record(WS/'scripts/native'/n) for n in engine['quake']],gaps=gaps,input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-quake-reference.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(fullasm=18,instructions=result['instructions'],code_changed=code,timestamp_only=len(stamp),unchanged=len(same))))

if __name__=='__main__':main()
