"""Pin the actual group60 receiver,guard,owner and packet read boundaries."""
import hashlib,json,struct
from pathlib import Path
from audit_client455_tutorial_integration import record,require,rtti,vptr_store
from build_client455_x87_math import read_va
from compare_client_binaries import WS,pe
from checkpoint_client455_rvp_effects import sha


def main():
    path=WS/'artifacts/client455-progress/nuclear112-reference.json';session_path=WS/'artifacts/client455-progress/nuclear112-session.json'
    raw=json.loads(path.read_text());session=json.loads(session_path.read_text());code={x['addr']:x for x in raw['functions']};asm={x['addr']:x for x in raw['assembly']};bounds={x['query']:x['fn'] for x in raw['ranges']['result']}
    require(len(code)==len(bounds)==45 and len(asm)==22 and sum(x['instruction_count'] for x in asm.values())==903,'Selected coverage')
    require(all(x['cursor']['done'] and not x['truncated'] and x['line_count']==x['total_lines'] for x in code.values()),'Complete selected pseudocode')
    for addr,x in asm.items():
        require(x['cursor']['done'] and x['instruction_count']==x['total_instructions']==len(x['asm']['lines']),'Complete selected assembly')
        start=int(addr,16);end=start+int(bounds[addr]['size'],16);require(all(start<=int(line['addr'],16)<end for line in x['asm']['lines']),'Contiguous selected instruction coverage')
    require(session['closed']['success'] and session['closed']['saved'] and session['after']['count']==0,'Owned IDA cleanup')
    pins=json.loads((WS/'config/client-target.json').read_text());refs=[]
    edges=[(0x5c5844,0x5c5910),(0x5c597f,0x5c5ab0),(0x561bd8,0x5c5730),(0x5c573f,0x57ea30),(0x5c57ed,0x57eac0)]
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        image_path=WS/f'work/client-reference/{folder}/RF_Online.bin';image=image_path.read_bytes();require(sha(image_path)==pins[key]['sha256'] and pe(image)['architecture']=='x86','Pinned x86 reference')
        ranges=[dict(rva=hex(int(addr,16)-0x400000),bytes=int(fn['size'],16),sha256=hashlib.sha256(read_va(image,int(addr,16),int(fn['size'],16))).hexdigest()) for addr,fn in bounds.items()]
        for at,target in edges:
            data=read_va(image,at,5);require(data[0]==0xe8 and at+5+struct.unpack('<i',data[1:])[0]==target,'Decoded actual receiver edge '+hex(at))
        vtable,store=vptr_store(image,0x5c5747);identity=rtti(image,vtable);require(identity['class_name']=='CNetMsgProcessor_Nuclear' and struct.unpack('<I',read_va(image,vtable+4,4))[0]==0x5c5800,'Actual registered processor identity')
        init=read_va(image,0x43a1ca,10);require(init[0]==0xc7 and init[1]>>6==2 and (init[1]>>3)&7==0 and init[1]&7!=4 and struct.unpack_from('<II',init,2)==(640,0),'Actual Character internal flag initialization')
        row=dict(sha256=sha(image_path),architecture='x86',image_base='0x400000',ranges=ranges,processor_identity=identity,constructor_vptr_store=store,decoded_calls=[dict(rva=hex(at-0x400000),target_rva=hex(target-0x400000)) for at,target in edges],internal_flags_zero_store=dict(rva='0x3a1ca',bytes=10,sha256=hashlib.sha256(init).hexdigest()))
        require(not refs or {k:v for k,v in row.items() if k!='sha256'}=={k:v for k,v in refs[0].items() if k!='sha256'},'Two-pin selected equivalence');refs.append(row)
    require('!= 60' in code['0x5c5800']['code'] and 'sub_5C5910' in code['0x5c5800']['code'],'Actual group60/opcode0')
    require('sub_406290(5) || sub_43DA10(3)' in code['0x43db60']['code'] and '*(this + 160)' in code['0x43da10']['code'],'Action/internal flag guard,not hover status')
    report=dict(status='CONFIRMED_SELECTED',scope='Actual client Nuclear receiver group60 and all9 opcode read contracts,guard,registry32 prerequisites; not full protocol/runtime acceptance',script_sha256=sha(Path(__file__)),raw=record(path),session=record(session_path),selected_functions=45,full_assembly_functions=22,instructions=903,references=refs,
        ordinary_start_chain=['CNetworkMgr factory561000 allocates8 and stores real Nuclear processor at this+413996','vtable slot+4 calls AnalysisServerPacket5C5800,group60/opcode0 calls5C5910','result0 and unblocked Avatar calls5C5AB0→existing CE7/requestclear/SetPending core;this is not an input/UI callback'],
        packets=[dict(opcode=0,min_bytes=1,fields='resultBYTE'),dict(opcode=3,min_bytes=17,fields='positionfloat3@4,indexBYTE@16,firstDWORD not used by handler'),dict(opcode=4,min_bytes=2,fields='raceBYTE,indexBYTE'),dict(opcode=5,min_bytes=5,fields='raceBYTE@0,indexBYTE@4,bytes1..3 ignored'),dict(opcode=6,min_bytes=2,fields='raceBYTE,indexBYTE;SetPending0 retains existing effect'),dict(opcode=7,min_bytes=14,fields='raceBYTE,indexBYTE,positionfloat3@2'),dict(opcode=8,min_bytes=2,fields='raceBYTE,indexBYTE remove'),dict(opcode=9,min_bytes=2,fields='same selected reads/handler as8'),dict(opcode=10,min_bytes=1,fields='countBYTE,if<=9 packed14byte rows:race,index,float3;count>9 ignores without reading rows')],
        error_messages={'3':0xce8,'4':0xce9,'5':0xcea,'6':0xceb,'7':0xcec,'8':0x16c,'9':0xced,'10':0xcee,'11':0xcef,'12':0xce6,'default':0xcf0},
        guard='Avatar actionDWORD@592 >>28 equals5 OR internalDWORD@640 &3; internalDWORD constructor initializes0. It is not the server64 flags or player status DWORD.',
        result_branches={'0':'CE7→arm only when pending0;repeat still outputs CE7','1':'get selected board payload serialWORD,request flag1,send group60/opcode1/2bytes if payload exists','2':'open inventory when needed and nuclear dialog based on converted Avatar status','blocked':'Clear aiming→close dialog→CE6 regardless of result byte'},
        record32='DWORD effects@0,4,8;DWORD@12 uninitialized by ctor;float3position@16;DWORD@28 zero. Map key=(race<<8)|index;full lifecycle/frame/draw not yet accepted',
        gaps=['Only bytes read by handlers establish minimum accepted-input boundaries;target unsafe short/null behavior not accepted','All internal flag producers,selection/dialog/network send/otheropcode owner/record FX/frame integration remain mandatory','Full client and all previous client-acceptance gaps remain open'],input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-nuclear-protocol-reference.json').write_text(json.dumps(report,indent=2)+'\n');print('CONFIRMED_SELECTED:45bodies/22fullasm/903instructions equalbothpins;realgroup60/opcode0 receiver,all9payload reads;Character640 init0')


if __name__=='__main__':main()
