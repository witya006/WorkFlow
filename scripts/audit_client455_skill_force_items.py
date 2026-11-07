"""Pin the SF factory/data/manager contract and supplied table incompatibilities."""
import hashlib
import json
import struct
from pathlib import Path

from audit_client455_language import decode, encode_with_envelope
from checkpoint_client455_rvp_effects import check, require, sha
from build_client455_x87_math import read_va
from compare_client_binaries import WS, pe


def record(path):return dict(file=path.relative_to(WS).as_posix(),sha256=sha(path))


def tables(payload):
    at=0;rows=[]
    for i in range(5):
        require(len(payload)-at>=8,'Missing SF table header')
        count,stride=struct.unpack_from('<II',payload,at);at+=8
        require(stride and count<=(len(payload)-at)//stride,'Invalid SF table extent')
        end=at+count*stride
        rows.append(dict(count=count,stride=stride,offset=at,data=bytearray(payload[at:end])));at=end
    return rows,at


def localized_payload(base,names):
    body,consumed=tables(base);at=0;failed=None
    for index,row in enumerate(body):
        require(len(names)-at>=8,'Missing localization header')
        count,ignored=struct.unpack_from('<II',names,at);at+=8
        if count!=row['count']:failed=index;break
        require(count<=(len(names)-at)//544,'Short localization records')
        for ordinal in range(count):
            offset=ordinal*row['stride'];row['data'][offset+112:offset+144]=names[at:at+32]
            row['data'][offset+524:offset+1036]=names[at+32:at+544];at+=544
    return b''.join(struct.pack('<II',r['count'],r['stride'])+r['data'] for r in body),failed


def main():
    raw_path=WS/'artifacts/client455-progress/skill-force088-reference.json';raw=json.loads(raw_path.read_text())
    require(len(raw['functions'])==35 and all(r['code'] and not r['truncated'] and r['line_count']==r['total_lines']
            for r in raw['functions']),'Incomplete selected pseudocode')
    metadata=raw['ranges']['result'];require(len(metadata)==35 and all(r['fn'] and not r['error'] for r in metadata),'Missing ranges')
    functions={r['fn']['addr'].lower():r['fn'] for r in metadata};assembly=[];external=[]
    for body in raw['assembly']:
        lines=[line for page in body['pages'] for line in page['asm']['lines']]
        start=int(body['addr'],16);end=start+int(functions[body['addr'].lower()]['size'],16)
        require(len(lines)==len({r['addr'] for r in lines})==body['pages'][0]['total_instructions'],
                'Incomplete assembly '+body['addr'])
        # IDA also returns noncontiguous compiler EH tails. Pin a full15-byte
        # window at each external instruction (x86 maximum instruction length),
        # instead of silently discarding tails or assuming a contiguous body.
        for line in lines:
            va=int(line['addr'],16)
            if not start<=va<end:external.append(dict(owner_rva=hex(start-0x400000),rva=hex(va-0x400000),bytes=15))
        assembly.append(dict(rva=hex(start-0x400000),instructions=len(lines)))
    require(len(assembly)==16 and sum(r['instructions'] for r in assembly)==1224,'Assembly coverage')
    pins=json.loads((WS/'config/client-target.json').read_text());references=[]
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        path=WS/f'work/client-reference/{folder}/RF_Online.bin';data=path.read_bytes()
        require(sha(path)==pins[key]['sha256'] and pe(data)['architecture']=='x86','Changed pin')
        ranges=[]
        for row in metadata:
            fn=row['fn'];va,size=int(fn['addr'],16),int(fn['size'],16)
            ranges.append(dict(rva=hex(va-0x400000),bytes=size,sha256=hashlib.sha256(read_va(data,va,size)).hexdigest()))
        tails=[dict(**row,sha256=hashlib.sha256(read_va(data,0x400000+int(row['rva'],16),row['bytes'])).hexdigest()) for row in external]
        require(not references or references[0]['ranges']==ranges and references[0]['external_assembly_windows']==tails,
                'Selected functions/tails differ between pins')
        references.append(dict(sha256=sha(path),architecture='x86',image_base='0x400000',ranges=ranges,external_assembly_windows=tails))
    client=Path(json.loads((WS/'config/paths.json').read_text())['client_455']);root=WS/'work/client-reference/skill-force455';root.mkdir(parents=True,exist_ok=True)
    inputs=[];payloads={}
    paths=[('base.edf',client/'DataTable/SkillForce.edf')]+[(folder+'.edf',client/f'DataTable/{folder}/NDSkillForce.edf') for folder in ['zh-tw','ko-kr','ru-ru']]
    for name,path in paths:
        encoded=path.read_bytes();plain=decode(encoded);require(encode_with_envelope(encoded,plain)==encoded,'EDF round trip')
        copy=root/name;copy.write_bytes(encoded);payloads[name]=plain
        input_tables,end=tables(plain)
        require(end==len(plain),'Supplied SF input has unaccounted tail')
        inputs.append(dict(original=str(path),original_sha256=sha(path),**record(copy),
            tables=[{k:r[k] for k in ['count','stride','offset']} for r in input_tables],decoded_sha256=hashlib.sha256(plain).hexdigest()))
    base_tables,end=tables(payloads['base.edf']);base_counts=[r['count'] for r in base_tables]
    require(base_counts==[88,84,504,60,711] and [r['stride'] for r in base_tables]==[1100,1124,1124,1124,1124],'Supplied root data changed')
    golden=[]
    for folder,expected_failure in [('zh-tw',None),('ko-kr',4),('ru-ru',1)]:
        localized,failed=localized_payload(payloads['base.edf'],payloads[folder+'.edf'])
        require(failed==expected_failure,'Supplied mismatch position changed')
        path=root/(folder+'.golden');path.write_bytes(localized);golden.append(dict(locale=folder,failed_table=failed,**record(path)))
    candidates=[]
    for path in sorted((client/'DataTable').rglob('*SkillForce*.edf')):
        plain=decode(path.read_bytes());parsed,end=tables(plain)
        counts=[r['count'] for r in parsed];strides=[r['stride'] for r in parsed]
        candidates.append(dict(original=str(path),sha256=sha(path),counts=counts,strides=strides,
            payload_bytes=len(plain),consumed=end,counts_match_root=counts==base_counts))
    report=dict(status='CONFIRMED_SELECTED',scope='Root five-table SF data/localization,selector1 fresh payload factory and concrete primary manager;other factories/ordinary owners open',
        references=references,assembly=assembly,actual_instructions=1224,raw_evidence=[record(raw_path)],
        inputs=inputs,golden=golden,candidates=candidates,real_records=sum(base_counts),
        source_subtypes=[1,0,2,3,5],count_compatible_test_locale='zh-tw',
        localization_counts_are_not_version_or_full_compatibility_proof=True,
        script_sha256=sha(Path(__file__)),edf_helper_sha256=sha(WS/'scripts/audit_client455_language.py'),
        previous_ownership_reference_sha256=sha(WS/'inventory/client455-item-ownership-reference.json'),
        gaps=['Physical/Animus/Unit/UnitParts/Quest factories and Gesture/Macro owners remain required',
            'Other four SF manager tables/XP/mastery and live icon-board callbacks/recreate are not ported',
            'Reload leaks/old borrowed pointer lifetime and unsafe malformed/OOM/unwind domains are not accepted',
            'Korean/Russian supplied localized counts mismatch the root;do not fabricate labels or change originals/configuration to hide it',
            'Ordinary game-global managers/CItemObject/CResObject/board/hover/Linker/5x10view/Tutorial/game remain open'],
        input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-skill-force-items-reference.json').write_text(json.dumps(report,indent=2)+'\n')
    print('CONFIRMED_SELECTED:35equalranges/1224asm/1447realrows;zh-twcounts match,ko/ru mismatch at4/1;ordinaryownersOPEN')


if __name__=='__main__':main()
