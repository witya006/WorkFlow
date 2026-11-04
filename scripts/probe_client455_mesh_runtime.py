"""Run source455CPU mesh initialization withactual D3DX9matrix exports in own entry."""
import hashlib,json,os,shutil,subprocess
from pathlib import Path
from compare_client_binaries import WS
from probe_client_helpers import import_names

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    build=json.loads((WS/'inventory/client-helper-lab-build.json').read_text(encoding='utf-8'))
    if build['build_exit'] or build['build_settings'].get('RF_CLIENT_455_MESH_RUNTIME')!='ON':raise ValueError('455mesh runtime lab required')
    for group in ['lab_input_sha256','mesh08_input_sha256','mesh_binding_input_sha256','mesh_runtime_input_sha256']:
        for name,digest in build[group].items():
            if sha(WS/name)!=digest:raise ValueError('Stale455mesh runtime lab source:'+name)
    original=WS/'work/client-build/build-helper-lab/Release/RF_Online.bin';digest=sha(original)
    linked=json.loads((WS/'inventory/client455-mesh-runtime-link.json').read_text(encoding='utf-8'))['lab']
    if linked['exe_sha256']!=digest or len(linked['functions'])!=3:raise ValueError('Mesh runtime linked proof required')
    proof=json.loads((WS/'inventory/client455-mesh-runtime.json').read_text(encoding='utf-8'));headers=json.loads((WS/'inventory/character-mesh08-headers.json').read_text(encoding='utf-8'));dll=Path(proof['matrix_provider']['path'])
    if proof['header_report_sha256']!=sha(WS/'inventory/character-mesh08-headers.json') or sha(WS/headers['golden'])!=headers['golden_sha256'] or sha(dll)!=proof['matrix_provider']['sha256']:raise ValueError('Mesh runtime input/provider changed')
    for sample in headers['samples']:
        if sha(WS/sample['copy'])!=sample['sha256']:raise ValueError('Pinned model changed')
    if set(import_names(original.read_bytes(),13))!={'mss32.dll','abuse.dll','adv.dll','pdll.dll'}:raise ValueError('Game DLLs must remain delayed')
    root=WS/'work/client455-mesh-runtime-lab'/digest[:16];root.mkdir(parents=True,exist_ok=True);exe=root/'RF_Online.bin'
    if exe.exists() and sha(exe)!=digest:raise ValueError('Preserving unexpected mesh runtime snapshot')
    if not exe.exists():shutil.copyfile(original,exe)
    if any(root.rglob('*.dll')) or any(original.parent.glob('*.dll')):raise ValueError('Unexpected local game DLL')
    output=root/f'result-{len(list(root.glob("result-*.json")))+1:03}.json';env=os.environ.copy();env['RF_LAB_HELPER_OUTPUT']=str(output);env['RF_MESH_RUNTIME_GOLDEN']=str(WS/headers['golden']);env['RF_MESH_RUNTIME_WS']=str(WS);env['RF_MESH_RUNTIME_MATRIX_DLL']=str(dll)
    run=subprocess.run([str(exe),'--rf-mesh-runtime-scenario'],cwd=root,env=env,capture_output=True,timeout=45,creationflags=subprocess.CREATE_NO_WINDOW)
    if run.returncode:raise ValueError(f'Actual mesh runtime lab failed:{run.returncode:#x}:{run.stderr!r}')
    native=json.loads(output.read_text(encoding='utf-8'))
    if native!=proof['native_test']:raise ValueError('Full-client mesh runtime checks differ fromcomponent')
    report={'exe':exe.relative_to(WS).as_posix(),'exe_sha256':digest,'native_test':native,'output':output.relative_to(WS).as_posix(),'output_sha256':sha(output),'game_dlls_loaded':False,'matrix_provider_sha256':sha(dll),'link_report_sha256':sha(WS/'inventory/client455-mesh-runtime-link.json'),'scope':'Own full-client entry;3source CPU construction/header/material request APIs,12real files/393parts/12FP modes;real D3DX9_36matrix exports andscripted texture callbacks only in test,Dmalloc balance0. No normal loader/WinMain/physical texture creation/GPU/network/reference EXE execution.'}
    (WS/'inventory/client455-mesh-runtime-client.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(f'PASS:{native["checks"]}actual full-client CPU mesh runtime checks/12real files/393parts;real D3DX9matrix provider,scripted material requests.')
if __name__=='__main__':main()
