"""Exercise production weather parser/lifecycle/update functions in own client lab.

No reference EXE/game DLL runs; graphics/network initialization and GPU drawing
are outside these checks. Real lens-flare R3X files use the shared reader only.
"""
import hashlib
import json
import os
import shutil
import struct
import subprocess
from pathlib import Path
from compare_client_binaries import WS
from probe_client_helpers import import_names


def main():
    build=json.loads((WS/'inventory/client-helper-lab-build.json').read_text(encoding='utf-8'))
    expected_objects=181+sum(build['build_settings'].get(name)=='ON' for name in ['RF_CLIENT_455_TEXTURE','RF_CLIENT_455_SHARED_BUFFERS','RF_CLIENT_455_MODELS','RF_CLIENT_455_CHARACTER_MANAGER','RF_CLIENT_455_LEGACY_RUNTIME','RF_CLIENT_455_ANIMATION','RF_CLIENT_455_POSE'])
    if build['build_settings'].get('RF_CLIENT_455_POSE')=='ON':expected_objects+=1 # Secondary test TU shares the pose flag.
    if build['build_settings'].get('RF_CLIENT_455_ANIMATION_TIMING')=='ON':expected_objects+=1
    if build['build_settings'].get('RF_CLIENT_455_LOOP_CLOCK')=='ON':expected_objects+=1
    if build['build_settings'].get('RF_CLIENT_455_ANIMATION_MANAGER')=='ON':expected_objects+=1
    if build['build_settings'].get('RF_CLIENT_455_SHADERS')=='ON':expected_objects+=1
    if build['build_exit'] or build['generated_objects']!=expected_objects or build['build_settings'].get('RF_CLIENT_455_WEATHER')!='ON':
        raise ValueError('Successful weather-enabled full client lab required')
    for key in ['lab_input_sha256','weather_input_sha256']:
        if key not in build: raise ValueError('Weather build hashes missing')
        for file,digest in build[key].items():
            if hashlib.sha256((WS/file).read_bytes()).hexdigest()!=digest:
                raise ValueError(f'Stale weather build: {file}')
    exe=WS/'work/client-build/build-helper-lab/Release/RF_Online.bin'
    data=exe.read_bytes();digest=hashlib.sha256(data).hexdigest()
    linked=json.loads((WS/'inventory/client455-x87-link.json').read_text(encoding='utf-8'))['lab']
    if digest!=linked['sha256']: raise ValueError('Linked math verification is stale')
    if set(import_names(data,13))!={'mss32.dll','abuse.dll','adv.dll','pdll.dll'}:
        raise ValueError('Input game DLLs must remain delay imports')
    lab=WS/'work/client-weather-lab'/digest[:16]
    lab.mkdir(parents=True,exist_ok=True)
    if any(lab.rglob('*.dll')) or any(exe.parent.glob('*.dll')): raise ValueError('Unexpected local DLL')
    scan=[]
    root=Path(json.loads((WS/'config/paths.json').read_text(encoding='utf-8'))['client_455'])
    for source in sorted((root/'Map').rglob('*')):
        if source.is_file() and source.suffix.lower()=='.r3x':
            raw=source.read_bytes()
            scan.append((source.relative_to(root).as_posix(),raw))
    fixtures=[('wrong-version',struct.pack('<f',2.0)+bytes(1032)),
        ('version-only',struct.pack('<f',1.1)),('short-body',struct.pack('<f',1.1)+struct.pack('<I',0x20)+bytes(524)),
        ('env-bit-off',struct.pack('<f',1.1)+struct.pack('<I',0)+bytes(1032))]
    cases=[];total=0;applied=0
    def run(label,raw,original=None):
        nonlocal total,applied
        folder=lab/label;folder.mkdir(parents=True,exist_ok=True)
        input=folder/'input.r3x';output=folder/'output.bin'
        input.write_bytes(raw)
        env=os.environ.copy();env.update(RF_LAB_HELPER_INPUT=str(input),RF_LAB_HELPER_OUTPUT=str(output))
        process=subprocess.run([str(exe),'--rf-weather-read'],cwd=folder,env=env,capture_output=True,timeout=20,creationflags=subprocess.CREATE_NO_WINDOW)
        if process.returncode: raise ValueError(f'{label}: native weather read exit{process.returncode:#x}')
        result=output.read_bytes()
        if len(result)!=1328 or result[:8]!=b'RFWEA455': raise ValueError('Bad native weather output')
        version,parsed,did_apply,native_checks,failed,id0,id1,scene=struct.unpack_from('<8I',result,8)
        if version!=1 or failed: raise ValueError('Native weather output failed')
        valid=len(raw)>=4 and struct.unpack_from('<f',raw)[0]==struct.unpack('<f',struct.pack('<f',1.1))[0]
        if parsed!=valid: raise ValueError('Weather version check changed')
        body=(raw[4:1036]+bytes(1032))[:1032] if valid else bytes(1032)
        if result[296:]!=body: raise ValueError('Weather shared-reader bytes differ')
        flags=struct.unpack_from('<I',body)[0]
        expected_apply=valid and not flags&0x10
        if did_apply!=expected_apply: raise ValueError('Lens-guarded application selection differs')
        checks=3
        if did_apply:
            applied+=1
            expected_ids=tuple(struct.unpack_from('<I',body,at)[0] for at in (384,520)) if flags&0x20 else (0,0)
            expected_names=[body[at:at+128].split(b'\0')[0] for at in (256,392)] if flags&0x20 else [b'',b'']
            names=[result[40:168].split(b'\0')[0],result[168:296].split(b'\0')[0]]
            if (id0,id1)!=expected_ids or names!=expected_names or scene!=struct.unpack_from('<I',body,524)[0]:
                raise ValueError(f'Actual LoadR3X weather state differs: {label}')
            checks+=3
        total+=checks+native_checks
        return {'path':original,'case':label,'size':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),
            'parsed':bool(parsed),'full_LoadR3X_cpu_application':bool(did_apply),'checks':checks+native_checks,
            'flags':flags,'ids':[id0,id1],'output_sha256':hashlib.sha256(result).hexdigest()}
    for i,(path,raw) in enumerate(scan): cases.append(run(f'real/{i:03}',raw,path))
    for name,raw in fixtures: cases.append(run('fixtures/'+name,raw))
    scenario=lab/'scenario';scenario.mkdir(exist_ok=True)
    helpers=(b'script_begin [HelperObjectBegin] *ROOM -1 -1 -1 1 1 1 -interior '
        b'-node_tm 1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1 [HelperObjectEnd] script_end')
    (scenario/'helper.spt').write_bytes(helpers)
    for index in (0,1):
        (scenario/f'p{index}.spt').write_bytes(b'[Particle] num 1 live_time 60 '+(b'NiGhT ' if index==0 else b''))
    (scenario/'weather.mst').write_bytes(b'junk *environment FirstCase.SPT *environment_id 2 *environment2 SecondCase.SPT *environment_id2 1')
    env=os.environ.copy();output=scenario/'result.json'
    env.update(RF_LAB_HELPER_INPUT=str(scenario/'helper.spt'),RF_LAB_HELPER_OUTPUT=str(output))
    process=subprocess.run([str(exe),'--rf-weather-scenario'],cwd=scenario,env=env,capture_output=True,timeout=20,creationflags=subprocess.CREATE_NO_WINDOW)
    if process.returncode:
        detail=output.read_text(encoding='utf-8') if output.exists() else process.stderr.decode(errors='replace')
        raise ValueError(f'Native weather scenario exit{process.returncode:#x}: {detail}')
    native=json.loads(output.read_text(encoding='utf-8'))
    if native['failures'] or native['checks']<30: raise ValueError('Incomplete weather lifecycle scenario')
    total+=native['checks']
    shutil.copyfile(exe,lab/'RF_Online.bin')
    report={'exe':(lab/'RF_Online.bin').relative_to(WS).as_posix(),'exe_sha256':digest,
        'real_files':len(scan),'fixtures':len(fixtures),'full_LoadR3X_cpu_applications_including_fixtures':applied,
        'checks':total,'cases':cases,'lifecycle':native,
        'limits':'Shared production reader on all real R3X; full LoadR3X CPU apply skips lens-flare files. Two synthetic CPU particles exercise actual load/init/state/update/release and production text token consumer; no GPU draw, full material/particle/clock/normal map acceptance claimed. Unchecked headers shorter than four bytes retain reference indeterminate behavior and are not exercised.'}
    (WS/'inventory/client455-weather-runtime.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(f'PASS: {len(scan)} real R3X, {len(fixtures)} fixtures, actual two-layer CPU lifecycle/update/text parsing; {total} checks.')


if __name__=='__main__': main()
