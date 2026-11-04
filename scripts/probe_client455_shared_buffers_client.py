"""Run shared-buffer capture/physical HAL scenario from our fullclient entry."""
import hashlib,json,os,shutil,subprocess
from compare_client_binaries import WS,pe
from probe_client_helpers import import_names
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    build=json.loads((WS/'inventory/client-helper-lab-build.json').read_text(encoding='utf-8'));gpu=json.loads((WS/'inventory/client455-shared-buffers-gpu.json').read_text(encoding='utf-8'));link=json.loads((WS/'inventory/client455-shared-buffers-link.json').read_text(encoding='utf-8'))['lab']
    if build['build_exit'] or build['build_settings'].get('RF_CLIENT_455_SHARED_BUFFERS')!='ON' or len(link['functions'])!=12:raise ValueError('Source shared buffers fullclient required')
    for group in ['lab_input_sha256','shared_buffer_input_sha256','mesh08_input_sha256','mesh_runtime_input_sha256']:
        for name,digest in build[group].items():
            if sha(WS/name)!=digest:raise ValueError('Shared buffer fullclient source stale:'+name)
    for item in gpu['mesh_inputs']:
        if sha(WS/item['file'])!=item['sha256']:raise ValueError('Pinned mesh changed')
    if gpu['build_report_sha256']!=sha(WS/'inventory/client455-shared-buffers-build.json'):raise ValueError('Stale shared buffer component')
    original=WS/'work/client-build/build-helper-lab/Release/RF_Online.bin';digest=sha(original)
    if digest!=link['exe_sha256'] or set(import_names(original.read_bytes(),13))!={'mss32.dll','abuse.dll','adv.dll','pdll.dll'}:raise ValueError('Linked fullclient mismatch or game DLLs not delayed')
    base=WS/'work/b9'/digest[:8];base.mkdir(parents=True,exist_ok=True);root=base/f'client{len(list(base.glob("client*")))+1:03}';root.mkdir();exe=root/'RF_Online.bin';shutil.copyfile(original,exe)
    if any(root.rglob('*.dll')) or any(original.parent.glob('*.dll')):raise ValueError('Unexpected local game DLLs')
    output=root/'result.json';frame=root/'frame';env=os.environ.copy();env['RF_LAB_HELPER_OUTPUT']=str(output);env['RF_BUFFER_WORKSPACE']=str(WS);env['RF_BUFFER_FRAMES']=str(frame)
    run=subprocess.run([str(exe),'--rf-shared-buffers-scenario'],cwd=root,env=env,capture_output=True,timeout=60,creationflags=subprocess.CREATE_NO_WINDOW);(root/'stdout.txt').write_bytes(run.stdout);(root/'stderr.txt').write_bytes(run.stderr)
    if run.returncode:raise RuntimeError(f'Actual fullclient buffer scenario:{run.returncode:#x}:{run.stderr!r};{root}')
    native=json.loads(output.read_text(encoding='utf-8'));frames=[{'file':(root/f'frame-{stride}.bmp').relative_to(WS).as_posix(),'sha256':sha(root/f'frame-{stride}.bmp')} for stride in [36,64]]
    if native!=gpu['native'] or [f['sha256'] for f in frames]!=[f['sha256'] for f in gpu['frames']]:raise ValueError('Fullclient/component buffer results differ')
    report={'scope':'Own fullclient entry,source shared buffers/rebase/MESH08 GPU upload;test-only COM capture+actual HALD3D9,not full Character shaders/animation/normal model-loader acceptance','exe':exe.relative_to(WS).as_posix(),'exe_sha256':digest,'entry_rva':hex(pe(exe.read_bytes())['entry_rva']),'architecture':'x86','native':native,'output':output.relative_to(WS).as_posix(),'output_sha256':sha(output),'frames':frames,'dmalloc_balance':0,'device_and_d3d9_release_counts':0,'game_dlls_loaded':False,'component_gpu_report_sha256':sha(WS/'inventory/client455-shared-buffers-gpu.json'),'reference_report_sha256':sha(WS/'inventory/client455-shared-buffers-reference.json')}
    (WS/'inventory/client455-shared-buffers-client.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(native));print(root)
if __name__=='__main__':main()
