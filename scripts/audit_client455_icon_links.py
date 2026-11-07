"""Pin semantic icon groups and quantity/usable fanout;stage small key oracle."""
import hashlib,json,shutil,struct
from pathlib import Path
from audit_client455_item_payloads import record
from build_client455_x87_math import read_va
from checkpoint_client455_rvp_effects import check,load,require,sha
from compare_client_binaries import WS,pe

def main():
    evidence=WS/'artifacts/client455-progress/icon-links095-reference.json';raw=json.loads(evidence.read_text());metadata=raw['ranges']['result'];require(len(metadata)==22 and all(r['code'] and not r['truncated'] and r['line_count']==r['total_lines'] for r in raw['functions']),'Incomplete static reference');heads={r['fn']['addr']:r['fn'] for r in metadata};assembly=[];tails=[]
    for body in raw['assembly']:
        lines=[r for p in body['pages'] for r in p['asm']['lines']];a=int(body['addr'],16);end=a+int(heads[body['addr']]['size'],16);require(len(lines)==len({r['addr'] for r in lines})==body['pages'][0]['total_instructions'],'Incomplete assembly');assembly.append(dict(rva=hex(a-0x400000),instructions=len(lines)))
        tails.extend(dict(rva=hex(int(r['addr'],16)-0x400000),bytes=15) for r in lines if not a<=int(r['addr'],16)<end)
    pins=json.loads((WS/'config/client-target.json').read_text());refs=[]
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        path=WS/f'work/client-reference/{folder}/RF_Online.bin';binary=path.read_bytes();require(sha(path)==pins[key]['sha256'] and pe(binary)['architecture']=='x86','Changed pin');ranges=[]
        for r in metadata:
            fn=r['fn'];a,n=int(fn['addr'],16),int(fn['size'],16);ranges.append(dict(rva=hex(a-0x400000),bytes=n,sha256=hashlib.sha256(read_va(binary,a,n)).hexdigest()))
        windows=[dict(**r,sha256=hashlib.sha256(read_va(binary,0x400000+int(r['rva'],16),r['bytes'])).hexdigest()) for r in tails]
        if refs:require(ranges==refs[0]['ranges'] and windows==refs[0]['external_assembly_windows'],'Pins differ')
        refs.append(dict(sha256=sha(path),architecture='x86',image_base='0x400000',ranges=ranges,external_assembly_windows=windows))
    operands=[]
    for va,prefix,n in [(0x7ae556,b'\x25',4),(0x7ae570,b'\x25',4),(0x7ae55d,b'\xb1',1),(0x7ae587,b'\xb1',1)]:
        code=read_va(binary,va,len(prefix)+n);require(code.startswith(prefix),'Expected mask/shift instruction');operands.append(dict(rva=hex(va-0x400000),value=int.from_bytes(code[len(prefix):],'little')))
    mask_item,mask_index,shift_item,shift_type=[r['value'] for r in operands];require([mask_item,mask_index,shift_item,shift_type]==[0xfffffff,0xfffffff,28,60],'Unexpected key geometry')
    root=WS/'work/client-reference/icon-links455';root.mkdir(parents=True,exist_ok=True);cases=[]
    for index in [0,1,0xfffffff,0xf0000000,0xfabcdef0]:
        for item in [0,0xffffffff,0xfffffff,0x12345678]:
            for kind in [0,1,15,16,127,128,255,256]:
                value=(((item&mask_item)<<shift_item)|(index&mask_index)|((kind&255)<<shift_type))&0xffffffffffffffff;cases.append((index,item,kind,value&0xffffffff,value>>32))
    fixture=root/'icon-key-cases.bin';fixture.write_bytes(b'IK95'+struct.pack('<I',len(cases))+b''.join(struct.pack('<5I',*r) for r in cases));inputs=[]
    old=load('client455-item-icon-metadata-reference')
    for row in old['inputs']+old['fixtures']:
        if Path(row['file']).name not in ['item.edf','nd-zh-tw.edf','quest.edf','character.edf','base.edf','zh-tw.edf','inventory.spr','item.spr','metadata-samples.bin']:continue
        check(row);dest=root/Path(row['file']).name;shutil.copyfile(WS/row['file'],dest);inputs.append(record(dest))
    require(len(inputs)==9,'Real inventory inputs')
    report=dict(status='CONFIRMED_SELECTED',scope='Semantic icon buckets and typed quantity/usable fanout with actualMainApp owner;fullLinker/Macro registration callers not ported',script_sha256=sha(Path(__file__)),references=refs,assembly=assembly,actual_instructions=sum(r['instructions'] for r in assembly),decoded_operands=operands,raw_evidence=[record(evidence)],inputs=inputs,fixtures=[record(fixture)],key_cases=len(cases),
        facts=['Key=(itemID&0fffffff)<<28 | (objectIndex&0fffffff) | BYTE(iconType)<<60;bits56..59 zero,toptypebits truncate',
            'Register appends duplicate pointers;remove recomputes currentkey,erases firstmatching pointer,retains emptybucket',
            'Setter updates self then registeredmembers matching CURRENTsemantic key,without recursive propagation;unregistered samekey originals are not members',
            'Quantity is rawWORD;usable stores rawBYTE;quantity has nullmemberguard,usable doesnot;normal registration accepts nonnull icons only',
            'Actual target registration callers are Linker6 and Macro35;not a source-pointer/parent graph or automaticHover registry'],
        gaps=['Existingbucket removal of absentmember/emptyvector is undefined in target;source explicitlythrows instead of erasing end()',
            'Identity must be stable during registration;target doesnotreindex or auto-unregister on keychange/destruction;owners must coordinate removal',
            'CMainApp sourceowns registry before UI/data members,not the completeprivateUIManager ABI;fullshutdown/reset/OOM/concurrency notaccepted',
            'Typed setter paths connected in ordinary client;actual Linker/Macro Add-Remove registration and fullCItemBoard.Add remainopen',
            'Untypedlegacy setters/mixedpayload consumers/fullGUIItemchildren/Linker5x10/Macro/Vending/normalbootstrap/Tutorial/Login/auth/game and priorM6F/M7/M9 gaps mandatory'],
        input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-icon-links-reference.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(ranges=22,instructions=report['actual_instructions'],keys=len(cases),real_inputs=len(inputs))))
if __name__=='__main__':main()
