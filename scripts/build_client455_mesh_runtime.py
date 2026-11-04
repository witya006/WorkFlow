"""Build/test source455mesh construction,metadata andmaterial request kernels."""
import hashlib,json,shutil,subprocess
from pathlib import Path
from compare_client_binaries import WS,pe
from verify_client_coff import directives

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    headers=json.loads((WS/'inventory/character-mesh08-headers.json').read_text(encoding='utf-8'))
    if headers['script_sha256']!=sha(WS/'scripts/audit_mesh08_headers.py') or headers['corpus_report_sha256']!=sha(WS/'inventory/character-mesh08-corpus.json') or sha(WS/headers['golden'])!=headers['golden_sha256']:raise ValueError('Header fixtures changed')
    for sample in headers['samples']:
        if sha(WS/sample['copy'])!=sample['sha256']:raise ValueError('Pinned model changed')
    reference=json.loads((WS/'inventory/client455-mesh-runtime-reference.json').read_text(encoding='utf-8'));dll=Path(reference['matrix_provider']['path'])
    if sha(dll)!=reference['matrix_provider']['sha256']:raise ValueError('Matrix provider changed')
    framing=json.loads((WS/'inventory/client455-mesh08.json').read_text(encoding='utf-8'));library=WS/framing['library']
    if sha(library)!=framing['library_sha256']:raise ValueError('MESH08reader library changed')
    root=WS/'work/recovered/client455/mesh-runtime';root.mkdir(parents=True,exist_ok=True);hashes={}
    for name in ['client455_mesh_runtime.cpp','client455_mesh_runtime.h','test_client455_mesh_runtime.cpp','client455_mesh_bindings.h','client455_mesh08.h']:
        source=WS/'scripts/native'/name;shutil.copyfile(source,root/name);hashes[name]=sha(source)
    artifact=WS/'artifacts/character-mesh08-runtime';artifact.mkdir(parents=True,exist_ok=True);log=artifact/'build.txt'
    info=json.loads((WS/'inventory/msvc-verification.json').read_text(encoding='utf-8'));dev=Path(info['installation_path'])/'Common7/Tools/VsDevCmd.bat'
    batch=root/'build.cmd';batch.write_text(f'''@echo off
call "{dev}" -no_logo -arch=x86 -host_arch=x64 > env.txt 2>&1
if errorlevel 1 exit /b 1
cl /nologo /MT /O2 /Gy /EHsc /std:c++14 /W4 /WX /D_CRT_SECURE_NO_WARNINGS /c client455_mesh_runtime.cpp /Fomesh-runtime.obj > "{log}" 2>&1
if errorlevel 1 exit /b 1
lib /nologo /machine:x86 /out:RFClient455MeshRuntime.lib mesh-runtime.obj >> "{log}" 2>&1
if errorlevel 1 exit /b 1
cl /nologo /MT /O2 /EHsc /std:c++14 /W4 /WX /D_CRT_SECURE_NO_WARNINGS test_client455_mesh_runtime.cpp RFClient455MeshRuntime.lib "{library}" kernel32.lib /Femesh-runtime-probe.exe >> "{log}" 2>&1
exit /b %errorlevel%
''',encoding='ascii')
    if subprocess.run(['cmd.exe','/d','/c',str(batch)],cwd=root).returncode:raise RuntimeError(f'Mesh runtime build failed:{log}')
    obj=root/'mesh-runtime.obj'
    if '/DEFAULTLIB:"LIBCMT"' not in directives(obj.read_bytes()) or obj.read_bytes()[:2]!=b'\x4c\x01':raise ValueError('Mesh runtime object must be x86/MT')
    run=subprocess.run([str(root/'mesh-runtime-probe.exe'),str(WS/headers['golden']),str(WS),str(dll)],cwd=root,capture_output=True,timeout=60,creationflags=subprocess.CREATE_NO_WINDOW)
    (artifact/'native-result.txt').write_bytes(run.stdout+run.stderr)
    if run.returncode:raise RuntimeError(f'Mesh runtime native tests failed:{run.returncode:#x}:{run.stderr!r}')
    native=json.loads(run.stdout)
    if native['failures'] or native['real_files']!=12 or native['parts']!=393 or native['material_cases']!=8 or native['precision_rounding_modes']!=12:raise ValueError('Mesh runtime native coverage incomplete')
    report={'architecture':'x86','runtime':'/MT','library':(root/'RFClient455MeshRuntime.lib').relative_to(WS).as_posix(),'library_sha256':sha(root/'RFClient455MeshRuntime.lib'),'source_sha256':hashes,'object_sha256':sha(obj),'executable_sha256':sha(root/'mesh-runtime-probe.exe'),'executable':(root/'mesh-runtime-probe.exe').relative_to(WS).as_posix(),'entry_rva':hex(pe((root/'mesh-runtime-probe.exe').read_bytes())['entry_rva']),'native_test':native,'header_report_sha256':sha(WS/'inventory/character-mesh08-headers.json'),'reference_report_sha256':sha(WS/'inventory/client455-mesh-runtime-reference.json'),'matrix_provider':reference['matrix_provider'],'framing_library_sha256':sha(library),'scope':'Standalone source455CPU constructor/header/matrix andmaterial request kernels;real pinned D3DX9matrix library;scripted texture backend only in tests;fullclient integration/texture cache/loading/GPU/model dispatch/destructor remain open','limits':['Derived matrices checked byalgebraic invariants andsynthetic exact composition;not full arbitrary matrix bit-equivalence proof','No physical texture creation/shared GPU buffer/skeleton animation/normal game startup','Malformed/singular/OOM/unmasked FP/locale failures not complete reference parity']}
    (WS/'inventory/client455-mesh-runtime.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(f'PASS:source455mesh runtime,{native["checks"]}checks/12real files/393parts,8material traces/12FP modes;real D3DX9_36,x86/MT.')
if __name__=='__main__':main()
