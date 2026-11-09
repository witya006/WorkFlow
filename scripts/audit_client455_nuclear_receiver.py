"""Pin actual receiver/selected item use/MainGame ownership, reusing112/110."""
import hashlib,json,struct
from pathlib import Path
from audit_client455_item_payloads import record
from audit_client455_tutorial_integration import rtti
from build_client455_x87_math import read_va
from checkpoint_client455_rvp_effects import check,load,require,sha
from compare_client_binaries import WS,pe


def main():
    file=WS/'artifacts/client455-progress/nuclear116-reference.json';session_file=file.with_name('nuclear116-session.json');raw=json.loads(file.read_text());session=json.loads(session_file.read_text())
    refs=[load('client455-nuclear-protocol-reference'),load('client455-message-dispatch-reference'),load('client455-nuclear-registry-reference')]
    for ref in refs:check(ref['raw']);check(ref['session'])
    old=json.loads((WS/refs[0]['raw']['file']).read_text());dispatch=json.loads((WS/refs[1]['raw']['file']).read_text());registry=json.loads((WS/refs[2]['raw']['file']).read_text())
    cached_addresses={x['addr'].lower() for x in old['assembly']}|{'0x52b870'}
    code={x['addr'].lower():x for x in old['functions'] if x['addr'].lower() in cached_addresses};code.update({x['addr'].lower():x for x in raw['functions']})
    assembly={x['addr'].lower():x for x in old['assembly']};assembly.update({x['addr'].lower():x for x in raw['assembly']});assembly['0x4fe020']=next(x for x in dispatch['assembly'] if x['addr']=='0x4fe020');assembly['0x52b870']=next(x for x in registry['assembly'] if x['addr'].lower()=='0x52b870')
    bounds={x['query'].lower():x['fn'] for x in old['ranges']['result'] if x['query'].lower() in cached_addresses};bounds.update({x['query'].lower():x['fn'] for x in raw['bounds']['result']})
    require(len(code)==len(bounds)==44 and len(assembly)==42,'Selected body/full assembly coverage')
    require(all(x['cursor']['done'] and not x['truncated'] and x['line_count']==x['total_lines'] for x in code.values()),'Complete selected pcode')
    tails={'0x545d00':(0xa2bae0,0xa2bcac)}
    for address,row in assembly.items():
        require(row['cursor']['done'] and row['instruction_count']==row['total_instructions']==len(row['asm']['lines']),'Complete assembly')
        begin=int(address,16);end=begin+int(bounds[address]['size'],16);tail=tails.get(address,(0,0));require(all(begin<=int(x['addr'],16)<end or tail[0]<=int(x['addr'],16)<tail[1] for x in row['asm']['lines']),'Body/EH range')
    require(session['closed']['success'] and session['closed']['saved'] and session['closed']['owned'] and session['after']['count']==0,'Owned IDA savedclosed/list0')
    pins=json.loads((WS/'config/client-target.json').read_text());references=[]
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        path=WS/f'work/client-reference/{folder}/RF_Online.bin';image=path.read_bytes();require(sha(path)==pins[key]['sha256'] and pe(image)['architecture']=='x86','Pinned455/x86')
        ranges=[dict(rva=hex(int(address,16)-0x400000),bytes=int(fn['size'],16),sha256=hashlib.sha256(read_va(image,int(address,16),int(fn['size'],16))).hexdigest()) for address,fn in sorted(bounds.items())]
        eh=[dict(owner_rva=hex(int(owner,16)-0x400000),rva=hex(begin-0x400000),bytes=end-begin,sha256=hashlib.sha256(read_va(image,begin,end-begin)).hexdigest()) for owner,(begin,end) in tails.items()]
        identity=rtti(image,0xaac50c);require(identity['class_name']=='CInventoryBoard' and struct.unpack('<I',read_va(image,0xaac50c+124,4))[0]==0x475a90,'Actual inventory callback slot124')
        edges=[]
        for body in assembly.values():
            for line in body['asm']['lines']:
                if not line['instruction'].startswith('call ') or not line.get('refs'):continue
                at=int(line['addr'],16);data=read_va(image,at,5)
                if data[0]!=0xe8:continue
                target=int(line['refs'][0]['addr'],16);require(at+5+struct.unpack('<i',data[1:])[0]==target,'Decoded direct edge');edges.append(dict(rva=hex(at-0x400000),target_rva=hex(target-0x400000)))
        vtable=dict(rva='0x6ac50c',bytes=160,sha256=hashlib.sha256(read_va(image,0xaac50c,160)).hexdigest());row=dict(sha256=sha(path),architecture='x86',image_base='0x400000',ranges=ranges,tails=eh,decoded_calls=edges,inventory_identity=identity,inventory_vtable=vtable)
        require(not references or {k:v for k,v in row.items() if k!='sha256'}=={k:v for k,v in references[0].items() if k!='sha256'},'Two-pin selected equivalence');references.append(row)
    require('/ 2' in code['0x41b350']['code'] and '4452' in code['0x41c630']['code'],'Race normalization/level actual getters')
    require('this + 58' in code['0x40b950']['code'] and 'this + 146' in code['0x412000']['code'] and 'this + 1' in code['0x40b200']['code'],'Original board object→payload584→serial4')
    wrapper=[x['instruction'] for x in assembly['0x5c59d0']['asm']['lines']];require('imul edx, 21Ch' in wrapper and 'lea ecx, [eax+edx+2DC4h]' in wrapper,'Actual three marker selection,not separate dialog')
    require('229' in code['0x470690']['code'] and 'sub_4FD860' in code['0x5c5bd0']['code'] and 'sub_4FAD00(1)' in code['0x5c5bd0']['code'],'Result2 original board zero→real use result,not inventory Show')
    use=code['0x475a90']['code'];require('case 0x21u:' in use and 'sub_4757D0(this)' in use and 'sub_475E10(dword_1028AC0)' in use,'Actual nuclear inventory completion')
    require(code['0x4757d0']['line_count']==4 and 'this + 17848' in code['0x475e10']['code'] and '*(this + 1) = -1' in code['0x417140']['code'],'Empty nuclear callback then selected use-field4 reset,not item destruction')
    require('if ( !result )' in code['0x4fad00']['code'] and 'sub_4FE330' in code['0x4fad00']['code'],'Use-result clears operation only without hover/backup')
    require('this + 188' in code['0x545d00']['code'] and 'dword_1028AC8' in code['0x545d00']['code'] and '*(this + 47) = 0' in code['0x5496d0']['code'],'Stage Init binding and Destroy ownership')
    new_asm=[x for x in raw['assembly'] if x['addr'].lower() not in {v['addr'].lower() for v in old['assembly']}]
    report=dict(status='CONFIRMED_SELECTED',scope='Actual group60 handlers,original selection/serial/type33 inventory use and stage-owned registry;full stage/auth/inventory/world acceptance remains open',script_sha256=sha(Path(__file__)),raw=record(file),session=record(session_file),cached_reference=[record(WS/'inventory'/name) for name in ['client455-nuclear-protocol-reference.json','client455-message-dispatch-reference.json','client455-nuclear-registry-reference.json']],selected_functions=len(code),full_assembly_functions=len(assembly),instructions=sum(x['instruction_count'] for x in assembly.values()),new_assembly_functions=len(new_asm),new_instructions=sum(x['instruction_count'] for x in new_asm),references=references,corrections=['5C59D0 selects actual MiniMap marker at+2DC4+index*540;not a separate nuclear dialog','Result2 reads original storage boardBYTE229;zero invokes actual CObjectBoard UI_UseResult(TRUE),not an inventory-visible query/open','Result1 reads original board object232,not hover244/backup252;payload584→serialDWORD4 is sent as little-endian WORD','Type33 inventory branch4757D0 is empty,then475E10→417140 writes only player use recordDWORD4=FFFFFFFF;not a shared-item release/full620byte Clear','Base UI_UseResult clears operation only when actual hover/backup is absent;ClearOperation may C1A-cancel aiming even with empty cursor'],gaps=['Only selected nuclear category33 inventory completion is restored;all other inventory use branches/full target using-item record and producers remain open','Own invalid/post-release pointer and uncreated-stage cleanup differ from unsafe target leak/dangling domains;full normal stage lifecycle/world/bootstrap/auth still unaccepted','Unchecked malformed input/index/FP/OOM/concurrency/privateABI and all prior client-acceptance gaps remain;20registry R3T teardown warnings still require follow-up'],input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-nuclear-receiver-reference.json').write_text(json.dumps(report,indent=2)+'\n');print(f'CONFIRMED_SELECTED:{len(code)}bodies/{len(assembly)}fullasm/{report["instructions"]}instructions,bothpins/real use callback/marker/owner,IDA savedclosed/list0')


if __name__=='__main__':main()
