"""Snapshot the newly built client PE and audit direct providers without loading it."""
import argparse
import hashlib
import json
import re
import shutil
import struct
import subprocess
from pathlib import Path
from compare_client_binaries import WS,pe


def without_timestamps(data):
    image = pe(data)
    header = struct.unpack_from('<I',data,0x3c)[0]
    fields = [{'name':'COFF timestamp','offset':header+8,'size':4}]
    rva,size = struct.unpack_from('<II',data,header+24+96+6*8)
    if size:
        if size%28:
            raise ValueError('Unexpected debug directory size')
        section = next(s for s in image['sections'] if s['rva']<=rva<s['rva']+s['raw_size'])
        at = section['raw_offset']+rva-section['rva']
        if at+size>len(data):
            raise ValueError('Truncated debug directory')
        fields.extend({'name':'Debug directory timestamp','offset':start+4,'size':4} for start in range(at,at+size,28))
    normalized = bytearray(data)
    for field in fields:
        normalized[field['offset']:field['offset']+field['size']] = bytes(field['size'])
    return bytes(normalized),fields


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--label',required=True)
    args = parser.parse_args()
    if not re.fullmatch('[a-z0-9][a-z0-9-]{0,39}',args.label):
        raise ValueError('Snapshot labels must be short lowercase names, not paths')
    build = WS/'work/client-build/build-character-diagnostic'
    result = json.loads((WS/'inventory/client-character-diagnostic.json').read_text(encoding='utf-8'))
    if result['build_exit'] or result['unresolved_symbols'] or result['generated_objects']!=180:
        raise ValueError('The complete client build is not successful')
    if result['build_settings'].get('RF_CLIENT_HELPER_LAB')=='ON':
        raise ValueError('Normal client snapshots cannot contain the helper-lab entry')
    exe = build/'Release/RF_Online.bin'
    data = exe.read_bytes()
    image = pe(data)
    at = struct.unpack_from('<I',data,0x3c)[0]
    characteristics = struct.unpack_from('<H',data,at+22)[0]
    subsystem = struct.unpack_from('<H',data,at+24+68)[0]
    if characteristics&0x2000 or subsystem!=2:
        raise ValueError('Expected a GUI executable, not a DLL')
    if not any(s['rva']<=image['entry_rva']<s['rva']+s['raw_size'] for s in image['sections']):
        raise ValueError('Entrypoint is outside stored sections')
    verified = json.loads((WS/'inventory/msvc-verification.json').read_text(encoding='utf-8'))
    dumpbin = Path(verified['compiler_path'].splitlines()[0]).with_name('dumpbin.exe')
    dependents = subprocess.check_output([str(dumpbin),'/dependents',str(exe)]).decode('ascii',errors='replace')
    dlls = re.findall(r'^\s+([^\s\\/]+\.(?:dll|drv))\s*$',dependents,re.I|re.M)
    paths = json.loads((WS/'config/paths.json').read_text(encoding='utf-8'))
    client = Path(paths['client_455'])
    providers = []
    for dll in dlls:
        if dll.lower().startswith(('api-ms-','ext-ms-')):
            providers.append({'name':dll,'kind':'Windows API contract'})
            continue
        candidates = [exe.parent/dll,client/dll,client/'Snd'/dll,Path('C:/Windows/SysWOW64')/dll]
        provider = next((p for p in candidates if p.is_file()),None)
        entry = {'name':dll,'provider':str(provider) if provider else None}
        if provider:
            raw = provider.read_bytes()
            entry['architecture'] = pe(raw)['architecture']
            entry['sha256'] = hashlib.sha256(raw).hexdigest()
        providers.append(entry)
    output = WS/f'artifacts/client-first-build/{args.label}'
    output.mkdir(parents=True,exist_ok=True)
    for source in [exe,WS/'artifacts/client-character-diagnostic/build.txt',build/'CMakeCache.txt']:
        destination = output/source.name
        if destination.exists() and destination.read_bytes()!=source.read_bytes():
            raise ValueError(f'Preserving different snapshot: {destination}')
        if not destination.exists():
            shutil.copyfile(source,destination)
    sections = [{**s,'sha256':hashlib.sha256(data[s['raw_offset']:s['raw_offset']+s['raw_size']]).hexdigest()} for s in image['sections']]
    record = {'sha256':hashlib.sha256(data).hexdigest(),'size':len(data),'architecture':'x86',
        'image_base':hex(image['image_base']),'entry_rva':hex(image['entry_rva']),'subsystem':'Windows GUI',
        'snapshot':output.relative_to(WS).as_posix(),'build_settings':result['build_settings'],
        'sections':sections,'direct_providers':providers,'executed':False,
        'limits':'Diagnostic /Od source-base build with selected 455 branches and adapted CharacterMR. Direct provider discovery is not recursive loader/runtime validation or 455 parity.'}
    report_path = WS/'inventory/client-first-build.json'
    report = json.loads(report_path.read_text(encoding='utf-8')) if report_path.exists() else {}
    report[args.label] = record
    if 'initial' in report and 'clean' in report:
        a,b = report['initial'],report['clean']
        raw_a = (WS/a['snapshot']/'RF_Online.bin').read_bytes()
        raw_b = (WS/b['snapshot']/'RF_Online.bin').read_bytes()
        for raw,entry in [(raw_a,a),(raw_b,b)]:
            if hashlib.sha256(raw).hexdigest()!=entry['sha256']:
                raise ValueError('Saved build snapshot changed')
        normalized_a,fields_a = without_timestamps(raw_a)
        normalized_b,fields_b = without_timestamps(raw_b)
        report['comparison'] = {'same_raw_sha256':a['sha256']==b['sha256'],
            'same_section_hashes':[(s['name'],s['sha256']) for s in a['sections']]==[(s['name'],s['sha256']) for s in b['sections']],
            'equal_after_excluding_only_timestamp_fields':normalized_a==normalized_b,
            'excluded_timestamp_fields':fields_a,'same_timestamp_field_locations':fields_a==fields_b,
            'claim':'Two successful builds; no bit-identical executable claim unless the compared hashes match.'}
    report_path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(f'PASS: {args.label} RF_Online.bin, {len(data)} bytes, x86 GUI, entry RVA {image["entry_rva"]:#x}; not executed.')
    print(json.dumps({'direct_dlls':dlls,'providers_not_found':[p['name'] for p in providers if p.get('provider') is None and p.get('kind')!='Windows API contract']}))


if __name__=='__main__':
    main()
