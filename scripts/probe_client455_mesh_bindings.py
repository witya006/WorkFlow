"""Check455source parent/bone kernels inside the full-client project's own entry."""
import hashlib,json,os,shutil,subprocess
from compare_client_binaries import WS
from probe_client_helpers import import_names

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    build=json.loads((WS/'inventory/client-helper-lab-build.json').read_text(encoding='utf-8'))
    if build['build_exit'] or build['build_settings'].get('RF_CLIENT_455_MESH_BINDINGS')!='ON':raise ValueError('455mesh binding lab required')
    for group in ['lab_input_sha256','mesh08_input_sha256','mesh_binding_input_sha256']:
        for name,digest in build[group].items():
            if sha(WS/name)!=digest:raise ValueError('Stale455mesh binding lab source:'+name)
    original=WS/'work/client-build/build-helper-lab/Release/RF_Online.bin';digest=sha(original)
    linked=json.loads((WS/'inventory/client455-mesh-bindings-link.json').read_text(encoding='utf-8'))['lab']
    if linked['exe_sha256']!=digest or len(linked['functions'])!=4:raise ValueError('455mesh binding linked proof required')
    proof=json.loads((WS/'inventory/client455-mesh-bindings.json').read_text(encoding='utf-8'));pairs=json.loads((WS/'inventory/character-mesh08-bone-pairs.json').read_text(encoding='utf-8'))
    if proof['pair_report_sha256']!=sha(WS/'inventory/character-mesh08-bone-pairs.json') or sha(WS/pairs['golden'])!=pairs['golden_sha256']:raise ValueError('455mesh binding inputs changed')
    for sample in pairs['samples']:
        for path,key in [('mesh','mesh_sha256'),('skeleton_copy','skeleton_sha256')]:
            if sha(WS/sample[path])!=sample[key]:raise ValueError('Pinned455mesh/bone input changed')
    if set(import_names(original.read_bytes(),13))!={'mss32.dll','abuse.dll','adv.dll','pdll.dll'}:raise ValueError('Game DLLs must remain delayed')
    root=WS/'work/client455-mesh-bindings-lab'/digest[:16];root.mkdir(parents=True,exist_ok=True);exe=root/'RF_Online.bin'
    if exe.exists() and sha(exe)!=digest:raise ValueError('Preserving unexpected455mesh binding snapshot')
    if not exe.exists():shutil.copyfile(original,exe)
    if any(root.rglob('*.dll')) or any(original.parent.glob('*.dll')):raise ValueError('Unexpected local game DLL')
    output=root/f'result-{len(list(root.glob("result-*.json")))+1:03}.json';env=os.environ.copy();env['RF_LAB_HELPER_OUTPUT']=str(output);env['RF_MESH_BINDING_GOLDEN']=str(WS/pairs['golden']);env['RF_MESH_BINDING_WS']=str(WS)
    run=subprocess.run([str(exe),'--rf-mesh-binding-scenario'],cwd=root,env=env,capture_output=True,timeout=40,creationflags=subprocess.CREATE_NO_WINDOW)
    if run.returncode:raise ValueError(f'Actual455mesh binding lab failed:{run.returncode:#x}:{run.stderr!r}')
    native=json.loads(output.read_text(encoding='utf-8'))
    if native!=proof['native_test']:raise ValueError('455binding checks differ fromcomponent')
    report={'exe':exe.relative_to(WS).as_posix(),'exe_sha256':digest,'native_test':native,'output':output.relative_to(WS).as_posix(),'output_sha256':sha(output),'game_dlls_loaded':False,'link_report_sha256':sha(WS/'inventory/client455-mesh-bindings-link.json'),'scope':'Own full-client entry;4source455packed CPU binding kernels,12real paired fixtures/393meshes/455skeleton records/20overlap cases;Dmalloc balance0. No normal model-loader/WinMain/material/animation/GPU/network/reference EXE execution.'}
    (WS/'inventory/client455-mesh-bindings-runtime.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(f'PASS:{native["checks"]}actual full-client455mesh binding checks/12pairs/393meshes;no GPU/network/game DLLs.')
if __name__=='__main__':main()
