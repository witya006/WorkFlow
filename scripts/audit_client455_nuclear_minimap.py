"""Pin real marker owner/geometry/draw roles; no full receiver acceptance."""
import hashlib,json,struct
from pathlib import Path
from audit_client455_tutorial_integration import record,require,rtti,vptr_store
from build_client455_x87_math import read_va
from checkpoint_client455_rvp_effects import check,load,sha
from compare_client_binaries import WS,pe


def main():
    file=WS/'artifacts/client455-progress/nuclear114-reference.json';session_file=WS/'artifacts/client455-progress/nuclear114-session.json';raw=json.loads(file.read_text());session=json.loads(session_file.read_text())
    prior=load('client455-character-flags-reference');check(prior['raw']);check(prior['session']);cached=json.loads((WS/prior['raw']['file']).read_text());old112=load('client455-nuclear-protocol-reference');check(old112['raw']);old=json.loads((WS/old112['raw']['file']).read_text())
    input_file=WS/'artifacts/client455-progress/nuclear114-input-reference.json';input_session_file=WS/'artifacts/client455-progress/nuclear114-input-session.json';supplement=json.loads(input_file.read_text());input_session=json.loads(input_session_file.read_text())
    all_code={x['addr'].lower():x for x in raw['functions']};old_code={x['addr'].lower():x for x in cached['functions']};old112_code={x['addr'].lower():x for x in old['functions']}
    code={addr:all_code[addr] for addr in raw['selected_new']};code.update({addr:old_code[addr] for addr in raw['cached_selected']});code['0x70bf30']=old112_code['0x70bf30']
    assembly={x['addr'].lower():x for x in raw['assembly']};assembly.update({x['addr'].lower():x for x in cached['assembly'] if x['addr'].lower() in set(code)-set(assembly)})
    bounds={x['query'].lower():x['fn'] for x in raw['bounds']['result']};bounds['0x70bf30']=next(x['fn'] for x in old['ranges']['result'] if x['query'].lower()=='0x70bf30')
    code.update({x['addr']:x for x in supplement['functions'] if x['addr'] in ['0x60cf90','0x60d010']});assembly.update({x['addr']:x for x in supplement['assembly']});bounds.update({x['query']:x['fn'] for x in supplement['bounds']['result']})
    require(len(code)==len(bounds)==26 and len(raw['assembly'])+len(supplement['assembly'])==19 and len(assembly)==24,'Selected new/cached coverage')
    require(all(x['cursor']['done'] and not x['truncated'] and x['line_count']==x['total_lines'] for x in code.values()),'Complete selected pcode')
    tails={'0x705160':(0xa45df0,0xa45fc2),'0x70bbb0':(0xa462a0,0xa462df)}
    for address,row in assembly.items():
        require(row['cursor']['done'] and row['instruction_count']==row['total_instructions']==len(row['asm']['lines']),'Complete selected assembly')
        begin=int(address,16);end=begin+int(bounds[address]['size'],16);tail=tails.get(address,(0,0));require(all(begin<=int(x['addr'],16)<end or tail[0]<=int(x['addr'],16)<tail[1] for x in row['asm']['lines']),'Body/EH ranges')
    require(session['closed']['success'] and session['closed']['saved'] and session['after']['count']==0 and session['observed_before_close']['count']==1,'Owned IDA close/save/list0')
    require(input_session['closed']['success'] and input_session['closed']['saved'] and input_session['after']['count']==0,'Owned input-supplement IDA close/save/list0')
    pins=json.loads((WS/'config/client-target.json').read_text());references=[]
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        image_path=WS/f'work/client-reference/{folder}/RF_Online.bin';image=image_path.read_bytes();require(sha(image_path)==pins[key]['sha256'] and pe(image)['architecture']=='x86','Pinned455/x86')
        ranges=[dict(rva=hex(int(address,16)-0x400000),bytes=int(fn['size'],16),sha256=hashlib.sha256(read_va(image,int(address,16),int(fn['size'],16))).hexdigest()) for address,fn in bounds.items()]
        eh=[dict(owner_rva=hex(int(owner,16)-0x400000),rva=hex(begin-0x400000),bytes=end-begin,sha256=hashlib.sha256(read_va(image,begin,end-begin)).hexdigest()) for owner,(begin,end) in tails.items()]
        identities=[]
        for at,name in [(0x7051ab,'CGUIMiniMapWindow'),(0x70bbed,'CGUINuclearBomb')]:
            vt,store=vptr_store(image,at);identity=rtti(image,vt);require(identity['class_name']==name,'Actual UI owner identity')
            require(struct.unpack('<I',read_va(image,vt+36,4))[0]==0x60cb50,'Inherited clipped Draw role')
            require(struct.unpack('<I',read_va(image,vt+40,4))[0]==(0x7099a0 if name=='CGUIMiniMapWindow' else 0x70bec0),'Ordinary Draw role')
            require(struct.unpack('<I',read_va(image,vt+88,4))[0]==0x60cf90,'Container input flag setter role,not focus')
            identities.append(dict(identity=identity,store_rva=hex(at-0x400000),store=store,vtable=dict(rva=hex(vt-0x400000),bytes=152,sha256=hashlib.sha256(read_va(image,vt,152)).hexdigest())))
        edges=[]
        for body in assembly.values():
            for line in body['asm']['lines']:
                if not line['instruction'].startswith('call ') or not line.get('refs'):continue
                at=int(line['addr'],16);instruction=read_va(image,at,5)
                if instruction[0]!=0xe8:continue
                target=int(line['refs'][0]['addr'],16);require(at+5+struct.unpack('<i',instruction[1:])[0]==target,'Decoded actual direct edge');edges.append(dict(rva=hex(at-0x400000),target_rva=hex(target-0x400000)))
        row=dict(sha256=sha(image_path),architecture='x86',image_base='0x400000',ranges=ranges,tails=eh,identities=identities,decoded_calls=edges)
        require(not references or {k:v for k,v in row.items() if k!='sha256'}=={k:v for k,v in references[0].items() if k!='sha256'},'Both pins selected equivalence');references.append(row)
    alpha=assembly['0x70bec0']['asm']['lines'];require(any(x['instruction']=='add eax, 5' for x in alpha) and any(x['instruction']=='cmp eax, 0FFh' for x in alpha) and any(x['instruction'].startswith('movzx eax, [ebp+var_5]') for x in alpha),'Unsigned byte alpha wrap,not a clamped fade')
    require('sub_70C2D0' in code['0x7067a0']['code'] and 'sub_70C310' in code['0x706810']['code'] and 'sub_70C360' in code['0x70c2d0']['code'],'Actual geometry fanout')
    require(code['0x70bf30']['code'].index('sub_70BFE0')<code['0x70bf30']['code'].index('sub_70BD80'),'Position before resource configuration')
    require('588 * a2 + 552' in code['0x7c9240']['code'] and '588 * a2 + 564' in code['0x7c9240']['code'],'Actual world geometry record fields;not legacy hardcoded8map array')
    require('a3 | (a2 << 8)' in code['0x52b3e0']['code'],'Actual race/index position lookup key')
    require('*(this + 22) = a2' in code['0x60d010']['code'] and '+ 88' in code['0x60cf90']['code'],'Raw mouse inputDWORD88 and propagation to existing children')
    report=dict(status='CONFIRMED_SELECTED',scope='Actual MiniMap3marker owners/init/geometry/post-lookup display/draw;registry/worldproducer/receiver/fullminimap not accepted',script_sha256=sha(Path(__file__)),raw=record(file),session=record(session_file),cached_reference=[record(WS/'inventory/client455-character-flags-reference.json'),record(WS/'inventory/client455-nuclear-protocol-reference.json')],selected_functions=24,full_assembly_functions=22,new_assembly_functions=17,new_instructions=sum(x['instruction_count'] for x in raw['assembly']),instructions=sum(x['instruction_count'] for x in assembly.values()),references=references,ordinary_Draw_slot=40,clipped_Draw_slot=36,alpha='After successful ordinary Draw:BYTE(alpha+5),including255to4;not time-scaled/not clipped Draw;empty shown marker still advances',position='first position before configuration/autosize;font cell0 yields first backgroundwidth0,then7x9;actual race/index registry lookup occurs outside selected source UI methods',geometry='SetBounds7067A0 and SetGeometry706810 fan out to3 children;positive widths/heights recompute float scale,invalid bounds retain previous scale;world source7C9240 reads record588+552/556/560/564',gaps=['Actual registry/race/record32/FX/lifetime and normal group60 receiver remain open','World geometry producer7C9240/real588byte map record loader not ported;typed geometry/position API exercised in full-object lab only','Full map controls/avatar/world/reset/teardown and all prior client-acceptance gaps remain','Owned checked index3/sprite availability and admitted finite coordinates do not accept target unchecked OOB/missing resources/overflow/privateABI/OOM/FP domains'],input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    report.update(selected_functions=26,full_assembly_functions=24,new_assembly_functions=19,new_instructions=sum(x['instruction_count'] for x in raw['assembly']+supplement['assembly']),instructions=sum(x['instruction_count'] for x in assembly.values()),input_raw=record(input_file),input_session=record(input_session_file),root_input_flag='Init virtual88 uses60CF90(0),which writes mouse inputDWORD88 and propagates to existing children;not a focus toggle/fullparent input acceptance')
    (WS/'inventory/client455-nuclear-minimap-reference.json').write_text(json.dumps(report,indent=2)+'\n');print(f'CONFIRMED_SELECTED:26bodies/24fullasm/{report["instructions"]}instructions,bothpins;ordinaryDraw40/clip36/input88/3markers/realgeometry')


if __name__=='__main__':main()
