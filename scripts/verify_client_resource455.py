"""Check actual compiled resource references, flags and branch ledgers in both builds."""
import hashlib
import json
import re
import subprocess
from pathlib import Path
from compare_client_binaries import WS
from build_client455_x87_math import read_va


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    ledger=json.loads((WS/'inventory/client-behavior-patches.json').read_text(encoding='utf-8'))
    selected=[row for row in ledger if row['build_option']=='RF_CLIENT_455_RESOURCE_IO']
    if len(selected)!=7:raise ValueError('Seven selected resource files required')
    for row in selected:
        if sha(WS/row['file'])!=row['patched_sha256']:raise ValueError('Resource source ledger changed')
    verified=json.loads((WS/'inventory/msvc-verification.json').read_text(encoding='utf-8'))
    dumpbin=Path(verified['compiler_path'].splitlines()[0]).with_name('dumpbin.exe')
    expected={'r3particle':['?RF455_OpenResource@@','?RF455_ParticleScriptEnd@@'],
              'entity':['?RF455_OpenResource@@','?RF455_ResourceExists@@'],
              'r3material':['?RF455_OpenResource@@'], 'r3d3dtex':['?RF455_OpenResource@@'],
              'bsp':['?LoadDirectory@RF455_RpkGroup@@','?Release@RF455_RpkGroup@@','?RF455_SetResourceGroup@@'],
              'level':['?RF455_SetResourceGroup@@']}
    builds=[]
    reference=WS/'work/client-reference/current/RF_Online.bin'
    pinned=json.loads((WS/'config/client-target.json').read_text(encoding='utf-8'))
    if sha(reference)!=pinned['behavior_reference']['sha256']:raise ValueError('DDS mask reference changed')
    mask=read_va(reference.read_bytes(),0xbf7f00,128)
    for label,folder in [('normal','build-character-diagnostic'),('lab','build-helper-lab')]:
        root=WS/'work/client-build'/folder
        cache=(root/'CMakeCache.txt').read_text(encoding='utf-8')
        if 'RF_CLIENT_455_RESOURCE_IO:BOOL=ON' not in cache:raise ValueError('Resource flag disabled')
        engine=root/'R3EngineClientMT.dir/Release'
        rows=[]
        for name,prefixes in expected.items():
            path=engine/f'{name}.obj'
            symbols=subprocess.check_output([str(dumpbin),'/symbols',str(path)])
            undefined=b'\n'.join(line for line in symbols.splitlines() if b'UNDEF' in line)
            for prefix in prefixes:
                if prefix.encode('ascii') not in undefined:raise ValueError(f'{label}/{name}: resource branch not compiled')
            if name in ('entity','r3particle') and b'UNDEF' in undefined and b'_fopen' in undefined:
                raise ValueError(f'{name}: legacy fopen still compiled')
            rows.append({'object':path.relative_to(WS).as_posix(),'sha256':sha(path),'undefined_references':prefixes})
        implementation=engine/'client455_resource_io.obj'
        if not implementation.exists():raise ValueError('Resource implementation not compiled')
        mapping=(root/'RF_Online-Release.map').read_text(encoding='ascii',errors='replace')
        addresses=re.findall(r'^\s+[\da-fA-F]{4}:[\da-fA-F]{8}\s+\?pass_word@@3PAEA\s+([\da-fA-F]{8})\s',mapping,re.M)
        if len(addresses)!=1:raise ValueError('Cannot identify linked legacy DDS mask')
        address=int(addresses[0],16)
        if read_va((root/'Release/RF_Online.bin').read_bytes(),address,128)!=mask:raise ValueError('Compiled DDS mask differs from455')
        builds.append({'variant':label,'exe_sha256':sha(root/'Release/RF_Online.bin'),
                       'module_object_sha256':sha(implementation),'selected_objects':rows,
                       'dds_header_mask':{'va':hex(address),'rva':hex(address-0x400000),'sha256':hashlib.sha256(mask).hexdigest(),'matches455':True}})
    report={'source_files_verified':7,'builds':builds,
            'implementation_source_sha256':{name:sha(WS/'scripts/native'/name) for name in ['client455_resource_io.h','client455_resource_io.cpp']},
            'scope':'Actual compiled undefined references and module object/EXE hashes, plus source ledger. Native module/full-client runtime reports are separate. No normal game/GPU execution.'}
    (WS/'inventory/client455-resource-link.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('PASS: both full-client builds select resource/SPT branches in6engine objects;7source ledgers verified.')


if __name__=='__main__':main()
