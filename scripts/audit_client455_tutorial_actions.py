"""Pin QBI UI/equipment/cursor/combat/item rules and enumerate real SCP programs."""
import hashlib
import json
from pathlib import Path
from compare_client_binaries import WS
from build_client455_x87_math import read_va


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    directory=WS/'artifacts/client455-tutorial'
    source=directory/'actions-reference.json'
    evidence=json.loads(source.read_text())
    scripts=json.loads((WS/'inventory/client455-tutorial-scripts-reference.json').read_text())
    assemblies=[]
    for row in evidence['asm']:
        path=WS/row['file'];asm=json.loads(path.read_text())
        if len(asm['asm']['lines'])!=asm['instruction_count'] or not asm['cursor']['done']:
            raise ValueError('Incomplete QBI action instructions')
        assemblies.append({'file':row['file'],'sha256':sha(path),'instructions':asm['instruction_count']})
    pins=[]
    for folder,pin in zip(['current','reference-backup'],scripts['references']):
        binary=WS/f'work/client-reference/{folder}/RF_Online.bin'
        if sha(binary)!=pin['sha256']:raise ValueError('Changed455pin')
        raw=binary.read_bytes();ranges=[]
        for row in evidence['ranges']['result']:
            if row['error']:raise ValueError('Missing QBI action function')
            fn=row['fn'];addr,size=int(fn['addr'],16),int(fn['size'],16)
            ranges.append({'rva':hex(addr-0x400000),'bytes':size,
                           'sha256':hashlib.sha256(read_va(raw,addr,size)).hexdigest()})
        for addr in [0x42C3D0,0x42C490,0x42C550,0x42C6B0]:
            body=read_va(raw,addr,0x13)
            if body!=read_va(raw,0x42C050,0x13):raise ValueError('Expected confirmed empty Finish')
            ranges.append({'rva':hex(addr-0x400000),'bytes':0x13,'sha256':hashlib.sha256(body).hexdigest()})
        data=[]
        for addr,size,role in [(0xAA9C74,16,'equip_slot_map'),(0xAB0F9C+60,4,'Tutorial_input_virtual'),
                               (0xADA37C+48,4,'Mouse_Show_virtual')]:
            value=read_va(raw,addr,size)
            data.append({'rva':hex(addr-0x400000),'bytes':size,'role':role,'hex':value.hex(),
                         'sha256':hashlib.sha256(value).hexdigest()})
        if pins and (ranges!=pins[0]['ranges'] or data!=pins[0]['data']):
            raise ValueError('QBI action contracts differ between pins')
        pins.append({'sha256':pin['sha256'],'architecture':'x86','image_base':'0x400000','ranges':ranges,'data':data})
    inputs=[{'name':row['relative'],'file':row['file'],'sha256':row['sha256']} for row in scripts['inputs']]
    files=['actions-reference.json','actions-decompile.json','actions-helpers.json','actions-bindings.json','actions-visibility.json']
    report={'scope':'QBI19to46 rules with abstract host; all47 processor families available, real Tutorial still OPEN',
            'references':pins,'raw_evidence':[{'file':(directory/name).relative_to(WS).as_posix(),
                                             'sha256':sha(directory/name)} for name in files],
            'assemblies':assemblies,'script_sha256':sha(Path(__file__)),'inputs':inputs,
            'script_reference_sha256':sha(WS/'inventory/client455-tutorial-scripts-reference.json'),
            'supported_selectors':list(range(47)),
            'facts':['UI open/close commands finish via bit4; wait commands observe state without timeout',
                     'Equipment slot12 removal and wait include slot13; map16 includes category46 at slot15',
                     'Cursor coordinates use signed lowWORD; default/element UI helpers output DWORD X/Y, not a rectangle',
                     'Cursor29 controls current stage input DWORD; Cursor30 invokes actual mouse Show BOOL',
                     'Lock type/race/template filters and attack-feedback reset preserved; missing templates may accept waits',
                     'Items use temporary clone/board-object lifetimes, shared WORDserial and exact insert/use/link ordering'],
            'gaps':['Concrete UI/Avatar/world host, full board/briefing/frame/data-view bindings, ordinary client integration',
                    'Failed UI point lookup may leave original local coordinates uninitialized; unknown points are not fabricated',
                    'Equipment23 invalid table indices16..254 refused; unsafe foreign-pointer/message/error domains remain OPEN',
                    'Cursor33/34 external completion, combat feedback/counter writers and actual helper provider side effects',
                    'Item creation25byte tail from059, camera276 name and remaining numeric/error domains',
                    'Full Tutorial/fourstage/online authentication/M6F/M9'],
            'global_window_proc_decompile_is_excerpt':True,'input_exe_executed':False,'server_modified':False,
            'M6':'OPEN','M6F':'OPEN','M9':'OPEN'}
    (WS/'inventory/client455-tutorial-actions-reference.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'pinned_ranges':len(pins[0]['ranges']),'complete_action_asm':len(assemblies),
                      'real_programs':len(inputs),'selectors':47,'fullTutorial':'OPEN'}))


if __name__=='__main__':main()
