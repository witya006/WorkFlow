"""Run own ANI/dispatcher entry inside full client project; no input EXEs."""
import hashlib,json,os,shutil,subprocess
from compare_client_binaries import WS
from probe_client_helpers import import_names
from probe_client455_animation import fixtures,inputs

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    _,_,golden,_,pair,_,texture_root,dll,_=inputs()
    build=json.loads((WS/'inventory/client-helper-lab-build.json').read_text(encoding='utf-8'));gpu=json.loads((WS/'inventory/client455-animation-gpu.json').read_text(encoding='utf-8'));link=json.loads((WS/'inventory/client455-animation-link.json').read_text(encoding='utf-8'))['lab']
    if build['build_exit'] or build['build_settings'].get('RF_CLIENT_455_ANIMATION')!='ON' or len(link['functions'])!=13:raise ValueError('Full ANI-enabled lab required')
    for group in ['lab_input_sha256','animation_input_sha256','legacy_runtime_input_sha256','character_manager_input_sha256','model_input_sha256','shared_buffer_input_sha256','texture_input_sha256','mesh_runtime_input_sha256','mesh_binding_input_sha256']:
        for name,digest in build[group].items():
            if sha(WS/name)!=digest:raise ValueError('Stale full-client source:'+name)
    for name,key in [('client455-animation-build','build_report_sha256'),('client455-animation-reference','reference_report_sha256'),('character-mesh08-bone-pairs','pair_report_sha256'),('character-texture-inputs','texture_report_sha256')]:
        if gpu[key]!=sha(WS/f'inventory/{name}.json'):raise ValueError('Stale native ANI proof:'+name)
    original=WS/'work/client-build/build-helper-lab/Release/RF_Online.bin';digest=sha(original)
    if digest!=link['exe_sha256'] or set(import_names(original.read_bytes(),13))!={'mss32.dll','abuse.dll','adv.dll','pdll.dll'}:raise ValueError('Stale linked image or non-delayed game DLLs')
    base=WS/'work/m9'/digest[:8];base.mkdir(parents=True,exist_ok=True);root=base/f'client{len(list(base.glob("client*")))+1:03}';root.mkdir();fixtures(root);shutil.copytree(texture_root/'tex',root/'tex');exe=root/'RF_Online.bin';shutil.copyfile(original,exe)
    if any(root.rglob('*.dll')) or any(original.parent.glob('*.dll')):raise ValueError('Unexpected local DLL')
    output=root/'result.json';env=os.environ.copy();env.update(RF_ANI_WORKSPACE=str(WS),RF_ANI_GOLDEN=str(golden),RF_ANI_PAIRS=str(pair),RF_ANI_DLL=str(dll),RF_LAB_HELPER_OUTPUT=str(output))
    run=subprocess.run([str(exe),'--rf-animation-scenario'],cwd=root,env=env,capture_output=True,timeout=60,creationflags=subprocess.CREATE_NO_WINDOW);(root/'stdout.txt').write_bytes(run.stdout);(root/'stderr.txt').write_bytes(run.stderr)
    if run.returncode:raise RuntimeError(f'Own full-client ANI:{run.returncode:#x}:{run.stderr!r};{root}')
    native=json.loads(output.read_text(encoding='utf-8'))
    if native!=gpu['native']:raise ValueError('Full-client/component ANI results differ')
    report={'scope':'Full-client own entry source ANI/record/attachment/character dispatch;normal game consumers/pose/shaders remain open','architecture':'x86','exe':exe.relative_to(WS).as_posix(),'exe_sha256':digest,'entry_rva':link['entry_rva'],'native':native,'output':output.relative_to(WS).as_posix(),'output_sha256':sha(output),'game_dlls_loaded':False,'dmalloc_balance':0,'owned_heap_balance_after_explicit_reference_leak_observation':0,'device_and_d3d9_release_counts':0,'component_gpu_report_sha256':sha(WS/'inventory/client455-animation-gpu.json'),'reference_report_sha256':sha(WS/'inventory/client455-animation-reference.json')}
    (WS/'inventory/client455-animation-client.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(native));print(root)
if __name__=='__main__':main()
