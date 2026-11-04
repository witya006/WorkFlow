"""Run source converter andactual BN→MESH08 route inour fullclient own entry."""
import hashlib,json,os,shutil,subprocess
from pathlib import Path
from compare_client_binaries import WS
from probe_client_helpers import import_names
from probe_client455_legacy_runtime import fixtures

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    build=json.loads((WS/'inventory/client-helper-lab-build.json').read_text(encoding='utf-8'));gpu=json.loads((WS/'inventory/client455-legacy-runtime-gpu.json').read_text(encoding='utf-8'));link=json.loads((WS/'inventory/client455-legacy-runtime-link.json').read_text(encoding='utf-8'))['lab']
    if build['build_exit'] or build['build_settings'].get('RF_CLIENT_455_LEGACY_RUNTIME')!='ON' or len(link['functions'])!=10:raise ValueError('Full legacy runtime-enabled lab required')
    for group in ['lab_input_sha256','legacy_runtime_input_sha256','character_manager_input_sha256','model_input_sha256','shared_buffer_input_sha256','texture_input_sha256','mesh_runtime_input_sha256','mesh_binding_input_sha256']:
        for name,digest in build[group].items():
            if sha(WS/name)!=digest:raise ValueError('Stale fullclient source:'+name)
    for name,key in [('client455-legacy-runtime-build','build_report_sha256'),('client455-legacy-runtime-reference','reference_report_sha256'),('client455-legacy-runtime-inputs','input_report_sha256'),('character-mesh08-bone-pairs','pair_report_sha256'),('character-texture-inputs','texture_report_sha256')]:
        if gpu[key]!=sha(WS/f'inventory/{name}.json'):raise ValueError('Stale native proof:'+name)
    inputs=json.loads((WS/'inventory/client455-legacy-runtime-inputs.json').read_text(encoding='utf-8'));pairs=json.loads((WS/'inventory/character-mesh08-bone-pairs.json').read_text(encoding='utf-8'));textures=json.loads((WS/'inventory/character-texture-inputs.json').read_text(encoding='utf-8'));golden=WS/inputs['golden'];pair=WS/pairs['golden'];textureRoot=WS/textures['fixture_root']
    if sha(golden)!=inputs['golden_sha256'] or sha(pair)!=pairs['golden_sha256']:raise ValueError('Changed goldens')
    for record in inputs['samples']:
        if sha(WS/record['copy'])!=record['sha256'] or (record['mtg'] and sha(WS/record['mtg'])!=record['mtg_sha256']):raise ValueError('Changed legacyfixture')
    for sample in pairs['samples']:
        if sha(WS/sample['mesh'])!=sample['mesh_sha256']:raise ValueError('Changed MESH08fixture')
    for record in textures['fixture_files']:
        if record['relative'].startswith('tex/') and sha(textureRoot/record['relative'])!=record['sha256']:raise ValueError('Changed texturefixture')
    dll=Path('C:/Windows/SysWOW64/d3dx9_36.dll')
    if sha(dll)!=gpu['provider_sha256']:raise ValueError('Changed D3DX9 provider')
    original=WS/'work/client-build/build-helper-lab/Release/RF_Online.bin';digest=sha(original)
    if digest!=link['exe_sha256'] or set(import_names(original.read_bytes(),13))!={'mss32.dll','abuse.dll','adv.dll','pdll.dll'}:raise ValueError('Stale linked image ornon-delayed game DLLs')
    base=WS/'work/m9'/digest[:8];base.mkdir(parents=True,exist_ok=True);root=base/f'client{len(list(base.glob("client*")))+1:03}';root.mkdir();fixtures(root);shutil.copytree(textureRoot/'tex',root/'tex');exe=root/'RF_Online.bin';shutil.copyfile(original,exe)
    if any(root.rglob('*.dll')) or any(original.parent.glob('*.dll')):raise ValueError('Unexpected local DLL')
    output=root/'result.json';env=os.environ.copy();env.update(RF_LEGACY_WORKSPACE=str(WS),RF_LEGACY_GOLDEN=str(golden),RF_LEGACY_PAIRS=str(pair),RF_LEGACY_DLL=str(dll),RF_LAB_HELPER_OUTPUT=str(output))
    run=subprocess.run([str(exe),'--rf-legacy-runtime-scenario'],cwd=root,env=env,capture_output=True,timeout=60,creationflags=subprocess.CREATE_NO_WINDOW);(root/'stdout.txt').write_bytes(run.stdout);(root/'stderr.txt').write_bytes(run.stderr)
    if run.returncode:raise RuntimeError(f'Own fullclient legacyruntime:{run.returncode:#x}:{run.stderr!r};{root}')
    native=json.loads(output.read_text(encoding='utf-8'))
    if native!=gpu['native']:raise ValueError('Fullclient/component converter results differ')
    report={'scope':'Fullclient ownentry source legacyMSH/BN import+converter+actual BN→MESH08 routes;normal game dispatcher/animation/shaders stillopen','architecture':'x86','exe':exe.relative_to(WS).as_posix(),'exe_sha256':digest,'entry_rva':link['entry_rva'],'native':native,'output':output.relative_to(WS).as_posix(),'output_sha256':sha(output),'game_dlls_loaded':False,'dmalloc_balance':0,'owned_heap_balance':0,'device_and_d3d9_release_counts':0,'component_gpu_report_sha256':sha(WS/'inventory/client455-legacy-runtime-gpu.json'),'reference_report_sha256':sha(WS/'inventory/client455-legacy-runtime-reference.json')}
    (WS/'inventory/client455-legacy-runtime-client.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(native));print(root)
if __name__=='__main__':main()
