"""Pin the typed icon/grade-border contract and actual455sprite inputs."""
import hashlib,json,shutil,struct
from pathlib import Path
from audit_client455_item_payloads import record
from audit_client455_sprites import sprite
from build_client455_x87_math import read_va
from checkpoint_client455_rvp_effects import require,sha
from compare_client_binaries import WS,pe

def main():
    evidence=WS/'artifacts/client455-progress/item-icon092-reference.json';raw=json.loads(evidence.read_text())
    metadata=raw['ranges']['result'];require(len(metadata)==18,'Reference function count')
    require(all(r['code'] and not r['truncated'] and r['line_count']==r['total_lines'] for r in raw['functions']),'Incomplete pseudocode')
    heads={r['fn']['addr'].lower():r['fn'] for r in metadata};assembly=[];tails=[]
    for body in raw['assembly']:
        lines=[r for page in body['pages'] for r in page['asm']['lines']];start=int(body['addr'],16);end=start+int(heads[body['addr']]['size'],16)
        require(len(lines)==len({r['addr'] for r in lines})==body['pages'][0]['total_instructions'],'Incomplete assembly')
        assembly.append(dict(rva=hex(start-0x400000),instructions=len(lines)))
        tails.extend(dict(rva=hex(int(r['addr'],16)-0x400000),bytes=15) for r in lines if not start<=int(r['addr'],16)<end)
    pins=json.loads((WS/'config/client-target.json').read_text());refs=[]
    extra=[(0x61cd20,48),(0xbd59d4,32),(0xb8007c,20),(0xad9f18,64)]
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        path=WS/f'work/client-reference/{folder}/RF_Online.bin';binary=path.read_bytes();require(sha(path)==pins[key]['sha256'] and pe(binary)['architecture']=='x86','Changed pin')
        ranges=[]
        for fn in [r['fn'] for r in metadata]+[dict(addr=hex(a),size=hex(n)) for a,n in extra]:
            a,n=int(fn['addr'],16),int(fn['size'],16);ranges.append(dict(rva=hex(a-0x400000),bytes=n,sha256=hashlib.sha256(read_va(binary,a,n)).hexdigest()))
        windows=[dict(**r,sha256=hashlib.sha256(read_va(binary,0x400000+int(r['rva'],16),r['bytes'])).hexdigest()) for r in tails]
        if refs:require(ranges==refs[0]['ranges'] and windows==refs[0]['external_assembly_windows'],'Pins differ in selected contract')
        refs.append(dict(sha256=sha(path),architecture='x86',image_base='0x400000',ranges=ranges,external_assembly_windows=windows))
    require(read_va(binary,0xbd59dc,16).startswith(b'.?AVCGUIItem@@\0'),'RTTI name')
    require(struct.unpack('<I',read_va(binary,0xad9f18,4))[0]==0xb8007c,'RTTI COL/vtable link')
    require(struct.unpack('<I',read_va(binary,0xb80088,4))[0]==0xbd59d4,'RTTI type descriptor')
    table=struct.unpack('<12I',read_va(binary,0x61cd20,48));colors=[]
    for va in table+(0x61cd14,):
        instruction=read_va(binary,va,5);require(instruction[0]==0xb8,'Grade result MOV EAX immediate');colors.append(struct.unpack_from('<I',instruction,1)[0])
    root=WS/'work/client-reference/item-icon455';root.mkdir(parents=True,exist_ok=True)
    golden=root/'grade-colors.bin';golden.write_bytes(b''.join(struct.pack('<I',colors[i] if i<12 else colors[12]) for i in range(256)))
    client=Path(json.loads((WS/'config/paths.json').read_text())['client_455']);inputs=[]
    for target_id,name in [(6,'inventory.spr'),(8,'item.spr')]:
        original=client/'SpriteImage/Common'/name;copy=root/name;shutil.copyfile(original,copy)
        data=copy.read_bytes();inputs.append(dict(**record(copy),bytes=len(data),original=str(original),target_id=target_id,**sprite(data)))
    require(inputs[0]['frames'][3]>3,'Actual inventory grade border frames')
    report=dict(status='CONFIRMED_SELECTED',scope='Typed icon index, BYTE grade color map, grade-border geometry and core draw/quantity;not completeCGUIItem/automatic item-atlas factory',
        script_sha256=sha(Path(__file__)),raw_evidence=[record(evidence)],references=refs,assembly=assembly,actual_instructions=sum(r['instructions'] for r in assembly),
        decoded_grade_colors=[hex(c) for c in colors],fixtures=[record(golden)],inputs=inputs,
        RTTI=dict(type_descriptor_rva='0x7d59d4',complete_object_locator_rva='0x78007c',vtable_rva='0x6d9f1c'),
        facts=['Wrapper596 points toGUIItem;refresh writesGUIItem96/index and GUIItem1240 ARGB64 using gradeBYTE1236',
            '1240 is inlineCGUIObject96 grade border,NOT caption/text; inventory targetID6/action3/frame2(width<64)or3(width>=64)',
            'All typed icon types use64pixel cells; ordinary default displayedsize32; position and size propagate to grade border',
            'Quantity enabled:zero onlytype0;above1 type0/7 in bothpaths,addtype2 onlyunclipped;WORD values are unsigned',
            'Full original GUIItem has further timers/overlays/text/animations;selected source-owned metadata is not its complete privateABI'],
        gaps=['Automatic itemID/classification toatlas-frame callback7B0570/7B0400 and fullspriteUnit lifecycle remain unported',
            'BaseCGUIObject SetSize remains legacy nonvirtual;typedCGUIItem/derived pointer path only;completebase dispatch/size96ABI not claimed',
            'GUIItem constructor/copy/update/shake/cooldowns/optionalchildren and full hover/Linker5x10/input/use/download remain open',
            'Normal data bootstrap/mixed legacy consumers/Quest sentence expansion/fullTutorial/Login/auth/game and prior M6F/M7/M9 gaps remain mandatory'],
        input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-item-icon-reference.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(ranges=len(refs[0]['ranges']),instructions=report['actual_instructions'],colors=256,sprites=[dict(id=r['target_id'],actions=r['actions'],frames=r['frames'],bytes=r['bytes']) for r in inputs])))
if __name__=='__main__':main()
