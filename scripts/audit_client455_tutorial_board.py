"""Pin board lifecycle/message routes; rich-window and production bindings stay open."""
import hashlib
import json
from pathlib import Path
from compare_client_binaries import WS
from build_client455_x87_math import read_va


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    directory=WS/'artifacts/client455-tutorial'
    evidence=json.loads((directory/'board-reference.json').read_text())
    scripts=json.loads((WS/'inventory/client455-tutorial-scripts-reference.json').read_text())
    pins=[]
    for folder,pin in zip(['current','reference-backup'],scripts['references']):
        binary=WS/f'work/client-reference/{folder}/RF_Online.bin'
        if sha(binary)!=pin['sha256']:raise ValueError('Changed455pin')
        raw=binary.read_bytes();ranges=[]
        for row in evidence['ranges']['result']:
            if row['error']:raise ValueError('Missing board function')
            fn=row['fn'];address,size=int(fn['addr'],16),int(fn['size'],16)
            ranges.append({'rva':hex(address-0x400000),'bytes':size,
                           'sha256':hashlib.sha256(read_va(raw,address,size)).hexdigest()})
        data=[]
        for address,size,role in [(0xAAD81C,32,'CTutorialBoard_vtable'),
                                  (0xAAD848,26,'script_suffixes_and_prefixes')]:
            value=read_va(raw,address,size)
            data.append({'rva':hex(address-0x400000),'bytes':size,'role':role,
                         'hex':value.hex(),'sha256':hashlib.sha256(value).hexdigest()})
        if pins and (ranges!=pins[0]['ranges'] or data!=pins[0]['data']):
            raise ValueError('Board contracts differ between pins')
        pins.append({'sha256':pin['sha256'],'architecture':'x86','image_base':'0x400000',
                     'ranges':ranges,'data':data})
    assemblies=[]
    for row in evidence['asm']:
        path=WS/row['file'];body=json.loads(path.read_text())
        if not body['cursor']['done'] or len(body['asm']['lines'])!=row['instructions']:
            raise ValueError('Incomplete board instructions')
        assemblies.append({**row,'sha256':sha(path)})
    inputs=[]
    for name in ['DataTable/en-gb/bw.scp','DataTable/en-gb/cr.scp','DataTable/en-gb/as.scp']:
        row=next(row for row in scripts['inputs'] if row['relative']==name)
        inputs.append({'name':name,'file':row['file'],'sha256':row['sha256']})
    files=['board-reference.json','board-decompile.json','board-bindings.json','board-terminal.json','board-base-window.json']
    report={'scope':'CTutorialBoard control rules and concrete legacy-GUI modal2/3 bridge; full455 rich UI/host OPEN',
            'references':pins,'assemblies':assemblies,
            'raw_evidence':[{'file':(directory/name).relative_to(WS).as_posix(),'sha256':sha(directory/name)} for name in files],
            'script_sha256':sha(Path(__file__)),'inputs':inputs,
            'script_reference_sha256':sha(WS/'inventory/client455-tutorial-scripts-reference.json'),
            'facts':['Modal2/3 concatenate serialized lengths with _mbsnbcpy; target buffer1024',
                     'Window38 only; first handled event initializes shared clock, then reads it again',
                     'Progress report only when unsigned elapsed strictly exceeds60000; payload byte uninitialized',
                     'Hidden briefing writes input3; quit prompt441 gated by five-frame shared cooldown and busy',
                     'Incomplete first finish asks444 and clears ready; second finish or forced/completed transitions',
                     'Transition order capture-null/Avatar skip1/stage virtual52/input1/unload/Avatar stage3',
                     'Key17 creates two rows, preserving high byte and255 markers'],
            'gaps':['Full CGUIBriefingWindow: rich/paged/animated text, portraits, key images, exact layout and input',
                    'Concrete Avatar/current-stage/capture providers, board registration, ordinary Tutorial/frame and event routing',
                    'Modal rendering/fonts/layout/input remain legacy GUI consumers; captured buttons use old sprite mappings, not full455 GUI equivalence',
                    'Progress report group1/op17 uninitialized payload byte; no invented value/network packet',
                    'Target modal text overflow/foreign pointers and invalid race/class/path domains not reproduced',
                    'Remaining itemtail25/camera276/cursor/helper/numeric/error domains; fullTutorial/M6F/M9'],
            'input_exe_executed':False,'server_modified':False,'M6':'OPEN','M6F':'OPEN','M9':'OPEN'}
    (WS/'inventory/client455-tutorial-board-reference.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'pinned_ranges':len(pins[0]['ranges']),'assemblies':len(assemblies),'full_briefing':'OPEN'}))


if __name__=='__main__':main()
