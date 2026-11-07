"""Pin common-object lifecycle and produce whole-record/flag oracles."""
import hashlib,json,struct
from pathlib import Path
from audit_client455_item_payloads import record
from build_client455_x87_math import read_va
from checkpoint_client455_rvp_effects import require,sha
from compare_client_binaries import WS,pe

def immediate(raw,va):
    code=read_va(raw,va,12);require(code[0] in [0xc6,0xc7],'Immediate store opcode')
    mod,reg,rm=code[1]>>6,(code[1]>>3)&7,code[1]&7
    require(mod in [0,1,2] and reg==0 and rm==0,'EAX store addressing')
    at=2;offset=0
    if mod==1:offset=struct.unpack('b',code[at:at+1])[0];at+=1
    if mod==2:offset=struct.unpack('<i',code[at:at+4])[0];at+=4
    width=1 if code[0]==0xc6 else 4
    return dict(rva=hex(va-0x400000),offset=offset,bytes=width,value=int.from_bytes(code[at:at+width],'little'),instruction=code[:at+width].hex())

def main():
    path=WS/'artifacts/client455-progress/res-object090-reference-complete.json';evidence=json.loads(path.read_text())
    require(len(evidence['functions'])==23 and all(r['code'] and not r['truncated'] and r['line_count']==r['total_lines'] for r in evidence['functions']),'Complete pseudocode required')
    metadata=evidence['ranges']['result'];require(len(metadata)==23 and all(r['fn'] and not r['error'] for r in metadata),'Function ranges')
    heads={r['fn']['addr'].lower():r['fn'] for r in metadata};assembly=[];windows=[];stores=[]
    for body in evidence['assembly']:
        lines=[line for page in body['pages'] for line in page['asm']['lines']];begin=int(body['addr'],16);end=begin+int(heads[body['addr'].lower()]['size'],16)
        require(len(lines)==len({r['addr'] for r in lines})==body['pages'][0]['total_instructions'],'Complete assembly')
        for line in lines:
            va=int(line['addr'],16)
            if not begin<=va<end:windows.append(dict(rva=hex(va-0x400000),bytes=15,owner_rva=hex(begin-0x400000)))
            if body['addr'] in ['0x7CCB70','0x7CCFA0'] and line['instruction'].startswith(('mov byte ptr [eax','mov dword ptr [eax')):stores.append(va)
        assembly.append(dict(rva=hex(begin-0x400000),instructions=len(lines)))
    require(len(assembly)==14 and sum(r['instructions'] for r in assembly)==765,'Assembly coverage')
    pins=json.loads((WS/'config/client-target.json').read_text());references=[];writes=None;profile=None
    constants=[0xaaa4d8,0xaedc40,0xb3a514,0xaaa3dc,0xb3a510,0xada940,0xaae504]
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        binary=WS/f'work/client-reference/{folder}/RF_Online.bin';raw=binary.read_bytes();require(sha(binary)==pins[key]['sha256'] and pe(raw)['architecture']=='x86','Changed pin')
        ranges=[]
        for row in metadata:
            fn=row['fn'];va,n=int(fn['addr'],16),int(fn['size'],16);ranges.append(dict(rva=hex(va-0x400000),bytes=n,sha256=hashlib.sha256(read_va(raw,va,n)).hexdigest()))
        tails=[dict(**r,sha256=hashlib.sha256(read_va(raw,0x400000+int(r['rva'],16),r['bytes'])).hexdigest()) for r in windows]
        floats=[dict(rva=hex(va-0x400000),bytes=read_va(raw,va,4).hex()) for va in constants];decoded=[immediate(raw,va) for va in stores]
        if references:require(references[0]['ranges']==ranges and references[0]['external_assembly_windows']==tails and references[0]['profile_constants']==floats and decoded==writes,'Pins differ')
        references.append(dict(sha256=sha(binary),architecture='x86',image_base='0x400000',ranges=ranges,external_assembly_windows=tails,profile_constants=floats));writes=decoded
        bits=[int.from_bytes(bytes.fromhex(r['bytes']),'little') for r in floats]
        profile=[bits[0],0,bits[1],0,0,1,1,1,1,1,0,0,bits[2],0,0,bits[3],bits[4],bits[5],0x3f800000,bits[6],0]
    root=WS/'work/client-reference/resource-object455';root.mkdir(parents=True,exist_ok=True);fixtures=[]
    def save(name,data):p=root/name;p.write_bytes(data);fixtures.append(record(p))
    expected=bytearray([0xa5]*584)
    def put(at,value):struct.pack_into('<I',expected,at,value)
    for row in writes:expected[row['offset']:row['offset']+row['bytes']]=row['value'].to_bytes(row['bytes'],'little')
    put(0,0xc0455000);expected[16:48]=bytes(32);expected[80:116]=bytes(36);put(116,0x20000180)
    expected[140:240]=bytes(100);put(144,0xffffffff);put(148,0x3f800000)
    for i in range(10):put(156+4*i,0xffffffff)
    put(240,0x3f800000);put(244,0x01020304);expected[256:460]=bytes(204);put(468,0x3f800000)
    expected[500:584]=struct.pack('<21I',*profile)
    save('constructed.bin',expected)
    source=bytearray((37*i+11)%256 for i in range(584));source[:4]=bytes(4);copied=bytearray([0xcc]*584)
    copied[:4]=struct.pack('<I',0xc0455000);copied[4]=source[4];copied[8:584]=source[8:584]
    save('copy-source.bin',source);save('copied.bin',copied)
    cases=[]
    for combination in range(16):
        flags=sum(bit for index,bit in enumerate([2,0x10000,0x20000,0x1000]) if combination&(1<<index))|0x80
        for enable in [0,1]:
            for mask in [0,2,0x10000,0x20000,0x1000]:
                result=flags|mask if enable else flags&~mask
                receive=0 if enable and result&0x10000 else 1
                clear=bool(result&0x21000 or not result&2)
                cases.append(struct.pack('<6I',flags,enable,mask,result,receive,int(clear)))
    save('flags.bin',b'RO90'+struct.pack('<I',len(cases))+b''.join(cases))
    report=dict(status='CONFIRMED_SELECTED',scope='Common CObject80/CResObject584 ctor/copy/name/flags/effect-clear lifecycle;not fullresource rendering or itemwrapper integration',
        references=references,assembly=assembly,actual_instructions=765,constructor_stores=writes,raw_evidence=[record(path)],fixtures=fixtures,
        offsets=dict(name=16,position=80,status=116,animation=140,scale=240,created_time=244,interpolation=248,material=288,light=356,
            alpha=468,blink=472,hide=476,text_color=480,receive_fix=484,effects=492,secondary_state=500),
        flag_cases=len(cases),script_sha256=sha(Path(__file__)),
        gaps=['Fullresource methods/render-name metrics/currentlegacyderivedconsumer behavior remain required',
            'ActualCItemObject/CBoardObject620 payload/board/hover/Linker owners still required',
            'Selected source resource lifecycle is not all shader/lighting/FX/reset/OOM/unwind/privateABI equivalence',
            'All previous storage/item/Tutorial/fourstage/Login/auth/gameplay/M6F/M7/M9 gaps remain mandatory'],
        input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-resource-object-reference.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(functions=23,instructions=765,decoded_stores=len(writes),flag_cases=len(cases))))
if __name__=='__main__':main()
