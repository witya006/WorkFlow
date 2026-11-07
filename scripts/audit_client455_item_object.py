"""Pin typed wrapper lifecycle and stage real-data/current-base oracles."""
import hashlib,json,shutil,struct
from pathlib import Path
from audit_client455_item_payloads import record
from build_client455_x87_math import read_va
from checkpoint_client455_rvp_effects import check,load,require,sha
from compare_client_binaries import WS,pe

def main():
    raw_path=WS/'artifacts/client455-progress/item-object091-reference.json';raw=json.loads(raw_path.read_text())
    functions=raw['functions'];metadata=raw['ranges']['result'];require(len(functions)==len(metadata)==21 and all(r['code'] and not r['truncated'] and r['line_count']==r['total_lines'] for r in functions),'Incomplete reference')
    heads={r['fn']['addr'].lower():r['fn'] for r in metadata};assembly=[];tails=[]
    for body in raw['assembly']:
        lines=[r for page in body['pages'] for r in page['asm']['lines']];begin=int(body['addr'],16);end=begin+int(heads[body['addr'].lower()]['size'],16)
        require(len(lines)==len({r['addr'] for r in lines})==body['pages'][0]['total_instructions'],'Incomplete assembly')
        for line in lines:
            va=int(line['addr'],16)
            if not begin<=va<end:tails.append(dict(rva=hex(va-0x400000),bytes=15,owner_rva=hex(begin-0x400000)))
        assembly.append(dict(rva=hex(begin-0x400000),instructions=len(lines)))
    require(len(assembly)==14 and sum(r['instructions'] for r in assembly)==444,'Assembly coverage')
    pins=json.loads((WS/'config/client-target.json').read_text());references=[]
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        path=WS/f'work/client-reference/{folder}/RF_Online.bin';binary=path.read_bytes();require(sha(path)==pins[key]['sha256'] and pe(binary)['architecture']=='x86','Changed pin')
        ranges=[]
        for row in metadata:
            fn=row['fn'];va,n=int(fn['addr'],16),int(fn['size'],16);ranges.append(dict(rva=hex(va-0x400000),bytes=n,sha256=hashlib.sha256(read_va(binary,va,n)).hexdigest()))
        windows=[dict(**r,sha256=hashlib.sha256(read_va(binary,0x400000+int(r['rva'],16),r['bytes'])).hexdigest()) for r in tails]
        if references:require(references[0]['ranges']==ranges and references[0]['external_assembly_windows']==windows,'Selected reference differs')
        references.append(dict(sha256=sha(path),architecture='x86',image_base='0x400000',ranges=ranges,external_assembly_windows=windows))
    root=WS/'work/client-reference/item-object455';root.mkdir(parents=True,exist_ok=True)
    base=load('client455-resource-object-reference');payload=load('client455-item-payloads-reference');sf=load('client455-skill-force-items-reference');inputs=[]
    for row in payload['inputs']+payload['fixtures']+sf['inputs']+sf['golden']:
        check(row);original=WS/row['file'];copy=root/original.name;shutil.copyfile(original,copy);inputs.append(record(copy))
    source_base=next(r for r in base['fixtures'] if r['file'].endswith('/constructed.bin'));check(source_base)
    constructed=bytearray((WS/source_base['file']).read_bytes())+bytearray([0xa5]*36)
    for at,width in [(584,4),(588,4),(592,1),(596,4),(600,17)]:constructed[at:at+width]=bytes(width)
    source=bytearray((31*i+7)%256 for i in range(620));source[:4]=bytes(4);source[584:588]=bytes(4)
    copied=bytearray([0xcc]*620);copied[:4]=struct.pack('<I',0xc0455000)
    for at,n in [(4,1),(8,585),(596,21)]:copied[at:at+n]=source[at:at+n]
    fixtures=[]
    for name,data in [('board-constructed.bin',constructed),('board-copy-source.bin',source),('board-copied.bin',copied)]:
        path=root/name;path.write_bytes(data);fixtures.append(record(path))
    report=dict(status='CONFIRMED_SELECTED',scope='Typed ordinary item592/board620 lifecycle with global source manager;icon/mixed callers/automatic data load remain open',
        references=references,assembly=assembly,actual_instructions=444,raw_evidence=[record(raw_path)],inputs=inputs,fixtures=fixtures,
        script_sha256=sha(Path(__file__)),base_reference_sha256=sha(WS/'inventory/client455-resource-object-reference.json'),
        payload_reference_sha256=sha(WS/'inventory/client455-item-payloads-reference.json'),SF_reference_sha256=sha(WS/'inventory/client455-skill-force-items-reference.json'),
        gaps=['Actual icon/caption refresh refuses nonnull icons on typed wrappers;legacy mixed derived payload binding explicitly refused',
            'CMainApp owns the new manager/data,loadFiles is real but not wired into normal gameplay bootstrap yet',
            'Full inventory/hover/Linker5x10 ownership/view/input/cooldowns/download and legacy payload consumption remain open',
            'Quest sentence names/full payload gameplay/Gesture/Macro/36boards/Trunk/protocol/Tutorial/Login/auth/game and prior M6F/M7/M9 requirements remain mandatory'],
        input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-item-object-reference.json').write_text(json.dumps(report,indent=2)+'\n');print('CONFIRMED_SELECTED:21equalranges/444asm/currentbase620byteoracles/real EDF fixtures')
if __name__=='__main__':main()
