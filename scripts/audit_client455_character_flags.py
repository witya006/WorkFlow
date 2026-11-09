"""Pin Character internal flag semantics and the actual MiniMap marker owner."""
import hashlib,json,struct
from pathlib import Path
from audit_client455_tutorial_integration import record,require,rtti,vptr_store
from build_client455_x87_math import read_va
from checkpoint_client455_rvp_effects import check,sha
from compare_client_binaries import WS,pe


def main():
    path=WS/'artifacts/client455-progress/nuclear113-reference.json';session_path=WS/'artifacts/client455-progress/nuclear113-session.json'
    raw=json.loads(path.read_text());state=json.loads(session_path.read_text());code={x['addr'].lower():x for x in raw['functions']};assembly={x['addr'].lower():x for x in raw['assembly']}
    bounds={x['query'].lower():x['fn'] for x in raw['bounds']['result']}
    prior=json.loads((WS/'artifacts/client455-progress/nuclear112-reference.json').read_text())
    old_bounds={x['query'].lower():x['fn'] for x in prior['ranges']['result']};bounds['0x70bf30']=old_bounds['0x70bf30']
    require(len(code)==29 and len(bounds)==30 and len(assembly)==14,'Selected reference coverage')
    require(all(x['cursor']['done'] and not x['truncated'] and x['line_count']==x['total_lines'] for x in code.values()),'Complete selected pseudocode')
    tail_bounds={'0x705160':(0xa45df0,0xa45fc2),'0x70bbb0':(0xa462a0,0xa462df)}
    for address,row in assembly.items():
        require(row['cursor']['done'] and row['instruction_count']==row['total_instructions']==len(row['asm']['lines']),'Complete selected assembly')
        begin=int(address,16);end=begin+int(bounds[address]['size'],16);tail=tail_bounds.get(address,(0,0))
        require(all(begin<=int(x['addr'],16)<end or tail[0]<=int(x['addr'],16)<tail[1] for x in row['asm']['lines']),'Assembly within confirmed body or separately pinned EH tail')
    require(state['closed']['success'] and state['closed']['saved'] and state['after']['count']==0,'Owned session saved/closed')
    require(state['expired_session']['authoritative_after']['count']==0,'Expired worker termination independently confirmed')
    pins=json.loads((WS/'config/client-target.json').read_text());references=[]
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        file=WS/f'work/client-reference/{folder}/RF_Online.bin';image=file.read_bytes();require(sha(file)==pins[key]['sha256'] and pe(image)['architecture']=='x86','Pinned455/x86')
        ranges=[dict(rva=hex(int(address,16)-0x400000),bytes=int(fn['size'],16),sha256=hashlib.sha256(read_va(image,int(address,16),int(fn['size'],16))).hexdigest()) for address,fn in bounds.items()]
        vt=0xaa8ddc;identity=rtti(image,vt);require(identity['class_name']=='CPlayer','Actual player vtable identity')
        for slot,target in [(172,0x43d960),(176,0x43d9d0),(180,0x43da70),(184,0x44bb90),(208,0x44f320)]:require(struct.unpack('<I',read_va(image,vt+slot,4))[0]==target,'Actual virtual flag/action producer')
        ui=[]
        for at,name in [(0x7051ab,'CGUIMiniMapWindow'),(0x70bbed,'CGUINuclearBomb')]:
            table,store=vptr_store(image,at);item=rtti(image,table);require(item['class_name']==name,'Actual UI owner identity');ui.append(dict(identity=item,constructor_store_rva=hex(at-0x400000),constructor_store=store))
        tails=[dict(owner_rva=hex(int(owner,16)-0x400000),rva=hex(begin-0x400000),bytes=end-begin,sha256=hashlib.sha256(read_va(image,begin,end-begin)).hexdigest()) for owner,(begin,end) in tail_bounds.items()]
        edges=[]
        for body in assembly.values():
            for line in body['asm']['lines']:
                if not line['instruction'].startswith('call ') or not line.get('refs'):continue
                at=int(line['addr'],16);instruction=read_va(image,at,5)
                if instruction[0]!=0xe8:continue
                target=int(line['refs'][0]['addr'],16);require(at+5+struct.unpack('<i',instruction[1:])[0]==target,'Selected direct call bytes')
                edges.append(dict(rva=hex(at-0x400000),target_rva=hex(target-0x400000)))
        row=dict(sha256=sha(file),architecture='x86',image_base='0x400000',ranges=ranges,tails=tails,decoded_calls=edges,player_identity=identity,player_vtable=dict(rva=hex(vt-0x400000),bytes=224,sha256=hashlib.sha256(read_va(image,vt,224)).hexdigest()),ui_identities=ui)
        require(not references or {k:v for k,v in row.items() if k!='sha256'}=={k:v for k,v in references[0].items() if k!='sha256'},'Both pins selected bytes/identities equal');references.append(row)
    require('sub_43D9B0' in code['0x43d960']['code'] and 'sub_5E5BD0' in code['0x43d960']['code'],'Clock before OR producer')
    require('== 0' in code['0x5e5c30']['code'] and 'sub_5E5C30' in code['0x43da40']['code'],'None(mask),not all-mask')
    require('11716' in code['0x705160']['code'] and '0x21Cu, 3, sub_70BBB0' in code['0x705160']['code'],'Three540byte markers owned by actual MiniMap')
    require('v2[0] = 4' in code['0x70bd80']['code'] and 'v3 = 5' in code['0x70bd80']['code'] and 'v4 = 43' in code['0x70bd80']['code'],'Marker actual sprite tuple')
    cached=[]
    for name in ['client455-nuclear-protocol-reference','client455-player-status-reference']:
        cached.append(record(WS/f'inventory/{name}.json'))
    report=dict(status='CONFIRMED_SELECTED',scope='Character flag owner/any-none/selected64bit producer prerequisites; actual MiniMap marker identity,not full action/movement/receiver acceptance',script_sha256=sha(Path(__file__)),raw=record(path),session=record(session_path),cached_reference=cached,selected_functions=30,pseudocode_functions=29,full_assembly_functions=len(assembly),instructions=sum(x['instruction_count'] for x in assembly.values()),references=references,guard='action highnibble5 OR internal CharacterDWORD640&3; any(mask) differs from none(mask)',clock='enable bit1 timestamps real movement-controller+8 before OR,including repeated enable; source clock field restored,full controller/frame open',marker_owner='Three CGUINuclearBomb540-byte children at actual MiniMap+11716;5C59D0 consumes ECX MiniMap,not processor or a separate dialog',marker_tuple='sprite4/main.spr,action5,frame43;imagefont1/common.spr,action7,frame3,7x9',gaps=['Full Character action writers,movement-controller owner/frame and all64bit status sideeffects remain open','Normal Nuclear receiver,selected item serial/send,record registry and MiniMap marker source integration remain open','Marker map transforms/configuration/virtual frame roles require remaining owner evidence before implementation'],input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-character-flags-reference.json').write_text(json.dumps(report,indent=2)+'\n');print(f'CONFIRMED_SELECTED:30ranges/29pcode/{len(assembly)}fullasm/{report["instructions"]}instructions;Characterflags/MiniMap identities,both455pins')


if __name__=='__main__':main()
