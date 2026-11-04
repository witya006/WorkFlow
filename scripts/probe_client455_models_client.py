"""Run connected source model route from our fullclient own entry,not WinMain."""
import hashlib,json,os,shutil,subprocess
from pathlib import Path
from compare_client_binaries import WS,pe
from probe_client_helpers import import_names
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    build=json.loads((WS/'inventory/client-helper-lab-build.json').read_text(encoding='utf-8'));gpu=json.loads((WS/'inventory/client455-models-gpu.json').read_text(encoding='utf-8'));link=json.loads((WS/'inventory/client455-models-link.json').read_text(encoding='utf-8'))['lab']
    if build['build_exit'] or build['build_settings'].get('RF_CLIENT_455_MODELS')!='ON' or len(link['functions'])!=5:raise ValueError('Source model enabled lab required')
    for group in ['lab_input_sha256','model_input_sha256','mesh_runtime_input_sha256','mesh_binding_input_sha256','shared_buffer_input_sha256','texture_input_sha256']:
        for name,digest in build[group].items():
            if sha(WS/name)!=digest:raise ValueError('Stale model lab source:'+name)
    if gpu['build_report_sha256']!=sha(WS/'inventory/client455-models-build.json') or gpu['paired_report_sha256']!=sha(WS/'inventory/character-mesh08-bone-pairs.json') or gpu['texture_report_sha256']!=sha(WS/'inventory/character-texture-inputs.json'):raise ValueError('Stale source model inputs')
    pairs=json.loads((WS/'inventory/character-mesh08-bone-pairs.json').read_text(encoding='utf-8'));golden=WS/pairs['golden'];textures=json.loads((WS/'inventory/character-texture-inputs.json').read_text(encoding='utf-8'));fixtures=WS/textures['fixture_root']
    if sha(golden)!=pairs['golden_sha256']:raise ValueError('Paired golden changed')
    for item in pairs['samples']:
        if sha(WS/item['mesh'])!=item['mesh_sha256']:raise ValueError('Pinned model changed')
    for record in textures['fixture_files']:
        if record['relative'].startswith('tex/') and sha(fixtures/record['relative'])!=record['sha256']:raise ValueError('Pinned texture changed')
    dll=Path('C:/Windows/SysWOW64/d3dx9_36.dll')
    if sha(dll)!=gpu['matrix_texture_provider_sha256']:raise ValueError('D3DX9provider changed')
    original=WS/'work/client-build/build-helper-lab/Release/RF_Online.bin';digest=sha(original)
    if digest!=link['exe_sha256'] or set(import_names(original.read_bytes(),13))!={'mss32.dll','abuse.dll','adv.dll','pdll.dll'}:raise ValueError('Model link mismatch or game DLLs not delayed')
    base=WS/'work/m9'/digest[:8];base.mkdir(parents=True,exist_ok=True);root=base/f'client{len(list(base.glob("client*")))+1:03}';root.mkdir();shutil.copytree(fixtures/'tex',root/'tex');exe=root/'RF_Online.bin';shutil.copyfile(original,exe)
    if any(root.rglob('*.dll')) or any(original.parent.glob('*.dll')):raise ValueError('Unexpected local DLL')
    output=root/'result.json';env=os.environ.copy();env['RF_LAB_HELPER_OUTPUT']=str(output);env['RF_MODEL_WORKSPACE']=str(WS);env['RF_MODEL_GOLDEN']=str(golden);env['RF_MODEL_DLL']=str(dll)
    run=subprocess.run([str(exe),'--rf-models-scenario'],cwd=root,env=env,capture_output=True,timeout=60,creationflags=subprocess.CREATE_NO_WINDOW);(root/'stdout.txt').write_bytes(run.stdout);(root/'stderr.txt').write_bytes(run.stderr)
    if run.returncode:raise RuntimeError(f'Model fullclient check:{run.returncode:#x}:{run.stderr!r};{root}')
    native=json.loads(output.read_text(encoding='utf-8'))
    if native!=gpu['native']:raise ValueError('Fullclient/component model results differ')
    report={'scope':'Own fullclient entry connected model lifetime/MESH08route withreal matrix/texture/GPU providers;normal file dispatch/manager/skeleton loader/animation/shaders not integrated','architecture':'x86','exe':exe.relative_to(WS).as_posix(),'exe_sha256':digest,'entry_rva':hex(pe(exe.read_bytes())['entry_rva']),'native':native,'output':output.relative_to(WS).as_posix(),'output_sha256':sha(output),'game_dlls_loaded':False,'dmalloc_balance':0,'owned_heap_balance':0,'device_and_d3d9_release_counts':0,'component_gpu_report_sha256':sha(WS/'inventory/client455-models-gpu.json'),'reference_report_sha256':sha(WS/'inventory/client455-models-reference.json')}
    (WS/'inventory/client455-models-client.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(native));print(root)
if __name__=='__main__':main()
