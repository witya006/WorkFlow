"""Exercise actual engine resource/SPT/R3X consumers in own full-client CPU entry."""
import hashlib
import json
import os
import struct
import subprocess
from compare_client_binaries import WS
from probe_client_helpers import import_names


def fixture(files):
    count=len(files)+1;payload=b'';offsets=[-1]
    nodes=[struct.pack('<52sIHHI',b'.\\',0,2,count-1,1)]
    for name,data in files:
        offsets.append(len(payload));payload+=data
        nodes.append(struct.pack('<52sIHHI',name,len(data),len(name),0,0))
    return (struct.pack('<II',0x3f800000,count)+struct.pack(f'<{count}I',*range(count))
            +struct.pack(f'<{count}i',*offsets)+b''.join(nodes)+payload)


def main():
    report=json.loads((WS/'inventory/client-helper-lab-build.json').read_text(encoding='utf-8'))
    if report['build_exit'] or report['build_settings'].get('RF_CLIENT_455_RESOURCE_IO')!='ON':raise ValueError('Successful resource-enabled lab build required')
    for group in ['resource_input_sha256','lab_input_sha256']:
        for name,digest in report[group].items():
            if hashlib.sha256((WS/name).read_bytes()).hexdigest()!=digest:raise ValueError(f'Stale resource lab:{name}')
    exe=WS/'work/client-build/build-helper-lab/Release/RF_Online.bin';data=exe.read_bytes();digest=hashlib.sha256(data).hexdigest()
    if set(import_names(data,13))!={'mss32.dll','abuse.dll','adv.dll','pdll.dll'}:raise ValueError('Game DLLs must be delayed')
    if json.loads((WS/'inventory/client455-x87-link.json').read_text(encoding='utf-8'))['lab']['sha256']!=digest:raise ValueError('Lab linked math proof stale')
    folder=WS/'work/client-resource-lab'/digest[:16];folder.mkdir(parents=True,exist_ok=True)
    if any(folder.rglob('*.dll')) or any(exe.parent.glob('*.dll')):raise ValueError('Unexpected game DLL beside CPU probe')
    resources=folder/'resources';resources.mkdir(exist_ok=True)
    body=bytearray(1032);struct.pack_into('<I',body,0,0x20)
    body[256:256+13]=b'FirstCase.SPT';body[392:392+14]=b'SecondCase.SPT'
    struct.pack_into('<I',body,384,1);struct.pack_into('<I',body,520,2);struct.pack_into('<I',body,524,123)
    files=[(b'first.spt',b'[Particle] num 3 live_time 60 end num 900\r\n'),
           (b'upper.spt',b'[Particle] num 3 END num 4 end num 901\r\n'),
           (b'invalid.spt',b'end [Particle] num 888\r\n'),
           (b'weather.r3x',struct.pack('<f',1.1)+body),
           (b'tail.spt',b'[Particle] num 999 live_time 3 end\r\n')]
    archive=fixture(files);(resources/'fixtures.rpk').write_bytes(archive)
    output=folder/'result.json';env=os.environ.copy();env['RF_LAB_HELPER_OUTPUT']=str(output)
    result=subprocess.run([str(exe),'--rf-resource-scenario'],cwd=folder,env=env,capture_output=True,timeout=20,creationflags=subprocess.CREATE_NO_WINDOW)
    if result.returncode:raise ValueError(f'Resource scenario exit{result.returncode:#x}: {output.read_text() if output.exists() else result.stderr!r}')
    result=json.loads(output.read_text(encoding='utf-8'))
    if result['failures'] or result['checks']<30:raise ValueError('Incomplete resource checks')
    result.update({'exe_sha256':digest,'fixture_sha256':hashlib.sha256(archive).hexdigest(),
                   'lab_source_sha256':report['resource_input_sha256'],
                   'scope':'Actual CParticle::LoadParticleSPT and LoadR3X consume an RPK via production source; adjacent entries/end/case/header boundaries. No entity/GPU/network or game DLL executed.'})
    (WS/'inventory/client455-resource-runtime.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(f'PASS: {result["checks"]}full-project native resource/SPT/R3X checks; game DLLs absent.')


if __name__=='__main__':main()
