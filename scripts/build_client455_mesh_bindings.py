"""Build source packed455 parent/bone kernels;run on real pinned paired inputs."""
import hashlib,json,shutil,subprocess
from pathlib import Path
from compare_client_binaries import WS
from verify_client_coff import directives

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    pairs=json.loads((WS/'inventory/character-mesh08-bone-pairs.json').read_text(encoding='utf-8'))
    if pairs['script_sha256']!=sha(WS/'scripts/audit_mesh08_bone_pairs.py') or sha(WS/pairs['golden'])!=pairs['golden_sha256']:raise ValueError('Bone pair expectations changed')
    for sample in pairs['samples']:
        for path,key in [('mesh','mesh_sha256'),('skeleton_copy','skeleton_sha256')]:
            if sha(WS/sample[path])!=sample[key]:raise ValueError('Pinned mesh/bone input changed')
    framing=json.loads((WS/'inventory/client455-mesh08.json').read_text(encoding='utf-8'));mesh08=WS/framing['library']
    if sha(mesh08)!=framing['library_sha256']:raise ValueError('MESH08source library changed')
    root=WS/'work/recovered/client455/mesh-bindings';root.mkdir(parents=True,exist_ok=True);hashes={}
    for name in ['client455_mesh_bindings.cpp','client455_mesh_bindings.h','test_client455_mesh_bindings.cpp','client455_mesh08.h']:
        source=WS/'scripts/native'/name;shutil.copyfile(source,root/name);hashes[name]=sha(source)
    info=json.loads((WS/'inventory/msvc-verification.json').read_text(encoding='utf-8'));dev=Path(info['installation_path'])/'Common7/Tools/VsDevCmd.bat'
    artifact=WS/'artifacts/character-mesh08-bones';artifact.mkdir(parents=True,exist_ok=True);log=artifact/'build.txt'
    batch=root/'build.cmd';batch.write_text(f'''@echo off
call "{dev}" -no_logo -arch=x86 -host_arch=x64 > env.txt 2>&1
if errorlevel 1 exit /b 1
cl /nologo /MT /O2 /Gy /EHsc /std:c++14 /W4 /WX /c client455_mesh_bindings.cpp /Fomesh-bindings.obj > "{log}" 2>&1
if errorlevel 1 exit /b 1
lib /nologo /machine:x86 /out:RFClient455MeshBindings.lib mesh-bindings.obj >> "{log}" 2>&1
if errorlevel 1 exit /b 1
cl /nologo /MT /O2 /EHsc /std:c++14 /W4 /WX /D_CRT_SECURE_NO_WARNINGS test_client455_mesh_bindings.cpp RFClient455MeshBindings.lib "{mesh08}" /Femesh-bindings-probe.exe >> "{log}" 2>&1
exit /b %errorlevel%
''',encoding='ascii')
    if subprocess.run(['cmd.exe','/d','/c',str(batch)],cwd=root).returncode:raise RuntimeError(f'455mesh-binding build failed:{log}')
    obj=root/'mesh-bindings.obj'
    if '/DEFAULTLIB:"LIBCMT"' not in directives(obj.read_bytes()) or obj.read_bytes()[:2]!=b'\x4c\x01':raise ValueError('Source object must be x86/MT')
    run=subprocess.run([str(root/'mesh-bindings-probe.exe'),str(WS/pairs['golden']),str(WS)],cwd=root,capture_output=True,timeout=40,creationflags=subprocess.CREATE_NO_WINDOW)
    (artifact/'native-result.txt').write_bytes(run.stdout+run.stderr)
    if run.returncode:raise RuntimeError(f'Source455mesh-binding tests failed:{run.returncode:#x};{run.stderr!r}')
    native=json.loads(run.stdout)
    if native['failures'] or native['real_pairs']!=12 or native['parts']!=pairs['mesh_count'] or native['overlap_cases']!=20:raise ValueError('Source binding fixture coverage incomplete')
    report={'architecture':'x86','runtime':'/MT','library':(root/'RFClient455MeshBindings.lib').relative_to(WS).as_posix(),'library_sha256':sha(root/'RFClient455MeshBindings.lib'),'source_sha256':hashes,'object_sha256':sha(obj),'executable_sha256':sha(root/'mesh-bindings-probe.exe'),'native_test':native,'pair_report_sha256':sha(WS/'inventory/character-mesh08-bone-pairs.json'),'reference_report_sha256':sha(WS/'inventory/client455-mesh-bindings-reference.json'),'framing_library_sha256':sha(mesh08),'scope':'Standalone source455packed CPU binding kernels on12real mesh/skeleton pairs;not full Character/source constructor/material/animation/GPU/full client normal loader integration','limits':['Borrowed input views;vector ownership and reference debug logging not wired','Bounded >50resolved andmalformed records return owned errors;not unchecked reference failure parity','Fixture skeleton selection is not full game asset-selection proof']}
    (WS/'inventory/client455-mesh-bindings.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(f'PASS:455source mesh/bone kernels,{native["checks"]}checks/12real pairs/{native["parts"]}meshes/20overlap cases;x86/MT.')
if __name__=='__main__':main()
