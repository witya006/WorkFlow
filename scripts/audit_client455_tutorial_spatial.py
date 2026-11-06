"""Pin Move/Creation/Position QBI contracts and explicitly retain unresolved tails."""
import hashlib
import json
import struct
from pathlib import Path
from compare_client_binaries import WS
from build_client455_x87_math import read_va


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    directory = WS / 'artifacts/client455-tutorial'
    evidence = json.loads((directory / 'spatial-reference.json').read_text())
    facing = json.loads((directory / 'spatial-facing-contract.json').read_text())
    path_facing = json.loads((directory / 'spatial-path-facing.json').read_text())
    refs = json.loads((WS / 'inventory/client455-tutorial-scripts-reference.json').read_text())['references']
    assemblies = []
    for row in evidence['asm']:
        path = WS / row['file']; body = json.loads(path.read_text())
        if len(body['asm']['lines']) != body['instruction_count'] or not body['cursor']['done']:
            raise ValueError('Incomplete spatial assembly')
        assemblies.append({'file': row['file'], 'sha256': sha(path), 'instructions': body['instruction_count']})
    pins = []
    for folder, ref in zip(['current','reference-backup'], refs):
        path = WS / f'work/client-reference/{folder}/RF_Online.bin'
        if sha(path) != ref['sha256']:
            raise ValueError('Changed455pin')
        raw = path.read_bytes(); ranges = []
        for row in evidence['ranges']['result'] + facing['ranges']['result'] + path_facing['ranges']['result']:
            if row['error']: raise ValueError('Missing spatial function')
            fn = row['fn']; addr, size = int(fn['addr'],16),int(fn['size'],16)
            ranges.append({'rva':hex(addr-0x400000),'bytes':size,
                           'sha256':hashlib.sha256(read_va(raw,addr,size)).hexdigest()})
        data = []
        for addr, size, role in [(0xAA9C44,47,'item_category_map'),(0xBCB758,8,'creation_counters'),
                                 (0xAA9748,8,'tau'),(0xAA9708,8,'degrees'),(0xAA9744,4,'speed'),
                                 (0xAA9024+76,16,'CCharacter_position_and_facing_virtuals')]:
            payload = read_va(raw,addr,size)
            data.append({'rva':hex(addr-0x400000),'bytes':size,'hex':payload.hex(),
                         'role':role,'sha256':hashlib.sha256(payload).hexdigest()})
        if struct.unpack('<H2xI',bytes.fromhex(data[1]['hex'])) != (3840,65535):
            raise ValueError('Unexpected creation initial counters')
        if bytes.fromhex(data[2]['hex']) != struct.pack('<d',6.283185307) or \
           bytes.fromhex(data[3]['hex']) != struct.pack('<d',360.0) or \
           bytes.fromhex(data[4]['hex']) != struct.pack('<f',12.0):
            raise ValueError('Source movement constants differ from455')
        if pins and (ranges != pins[0]['ranges'] or data != pins[0]['data']):
            raise ValueError('Spatial rules differ between pins')
        pins.append({'sha256':ref['sha256'],'architecture':'x86','image_base':'0x400000','ranges':ranges,'data':data})
    inputs = json.loads((WS / 'inventory/client455-tutorial-runtime-reference.json').read_text())['inputs']
    raw_files = ['spatial-reference.json','spatial-decompile.json','spatial-helpers.json',
                 'spatial-world-contracts.json','spatial-camera-followup.json',
                 'spatial-facing-contract.json','spatial-path-facing.json']
    report = {'scope':'Move6to8/Creation9to11/Position12to18 rules and known spawn bytes; real world host OPEN',
              'references':pins,'raw_evidence':[{'file':(directory/name).relative_to(WS).as_posix(),
                                               'sha256':sha(directory/name)} for name in raw_files],
              'assemblies':assemblies,'script_sha256':sha(Path(__file__)),'inputs':inputs,
              'supported_selectors':list(range(19)),'open_selectors':list(range(19,47)),
              'gaps':['Real UI/Avatar/world host, actual frame decrement of shared remaining values, other28 selectors',
                      'Item handler565A90 reads DWORD+25 although QBI initializes only25bytes; target stack tail unresolved',
                      'Camera parameter276 final name/provider unconfirmed; do not call it FOV',
                      'Legacy CRT math/error/FP domains beyond tested finite cases and real provider side effects',
                      'Full Tutorial/board/localmessages/fourstage/authentication/M6F/M9'],
              'input_exe_executed':False,'server_modified':False,'M6':'OPEN','M6F':'OPEN','M9':'OPEN'}
    (WS / 'inventory/client455-tutorial-spatial-reference.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'functions':len(pins[0]['ranges']),'assemblies':len(assemblies),'selectors':list(range(19)),
                      'item_tail25':'OPEN'}))


if __name__ == '__main__':
    main()
