"""Exercise the owned manager/model route from our fullclient lab entry."""
import hashlib,json,os,shutil,subprocess
from pathlib import Path
from compare_client_binaries import WS,pe
from probe_client_helpers import import_names
from probe_client455_character_manager import fixtures

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    build=json.loads((WS/'inventory/client-helper-lab-build.json').read_text(encoding='utf-8'));gpu=json.loads((WS/'inventory/client455-character-manager-gpu.json').read_text(encoding='utf-8'));link=json.loads((WS/'inventory/client455-character-manager-link.json').read_text(encoding='utf-8'))['lab']
    if build['build_exit'] or build['build_settings'].get('RF_CLIENT_455_CHARACTER_MANAGER')!='ON' or len(link['functions'])!=13:raise ValueError('Character455 source-enabled lab required')
    for group in ['lab_input_sha256','character_manager_input_sha256','model_input_sha256','mesh_runtime_input_sha256','mesh_binding_input_sha256','shared_buffer_input_sha256','texture_input_sha256']:
        for name,digest in build[group].items():
            if sha(WS/name)!=digest:raise ValueError('Stale lab source:'+name)
    for name,field in [('client455-character-manager-build','build_report_sha256'),('client455-character-manager-reference','reference_report_sha256'),('character-mesh08-bone-pairs','pair_report_sha256'),('character-texture-inputs','texture_report_sha256')]:
        if gpu[field]!=sha(WS/f'inventory/{name}.json'):raise ValueError('Stale component proof:'+name)
    pair=json.loads((WS/'inventory/character-mesh08-bone-pairs.json').read_text(encoding='utf-8'));ref=json.loads((WS/'inventory/client455-character-manager-reference.json').read_text(encoding='utf-8'));golden=WS/pair['golden'];ctor=WS/ref['constructor_golden'];texture=json.loads((WS/'inventory/character-texture-inputs.json').read_text(encoding='utf-8'));source=WS/texture['fixture_root']
    if sha(golden)!=pair['golden_sha256'] or sha(ctor)!=ref['constructor_golden_sha256']:raise ValueError('Changed golden')
    for item in pair['samples']:
        if sha(WS/item['mesh'])!=item['mesh_sha256']:raise ValueError('Pinned model changed')
    for record in texture['fixture_files']:
        if record['relative'].startswith('tex/') and sha(source/record['relative'])!=record['sha256']:raise ValueError('Texture fixture changed')
    dll=Path('C:/Windows/SysWOW64/d3dx9_36.dll')
    if sha(dll)!=gpu['provider_sha256']:raise ValueError('Changed D3DX9 provider')
    original=WS/'work/client-build/build-helper-lab/Release/RF_Online.bin';digest=sha(original)
    if digest!=link['exe_sha256'] or set(import_names(original.read_bytes(),13))!={'mss32.dll','abuse.dll','adv.dll','pdll.dll'}:raise ValueError('Link identity mismatch or game DLLs not delayed')
    base=WS/'work/m9'/digest[:8];base.mkdir(parents=True,exist_ok=True);root=base/f'client{len(list(base.glob("client*")))+1:03}';root.mkdir();fixtures(root);shutil.copytree(source/'tex',root/'tex');exe=root/'RF_Online.bin';shutil.copyfile(original,exe)
    if any(root.rglob('*.dll')) or any(original.parent.glob('*.dll')):raise ValueError('Unexpected local DLL')
    output=root/'result.json';env=os.environ.copy();env.update(RF_MODEL_WORKSPACE=str(WS),RF_MODEL_GOLDEN=str(golden),RF_CHARACTER_CTOR_GOLDEN=str(ctor),RF_MODEL_DLL=str(dll),RF_LAB_HELPER_OUTPUT=str(output))
    run=subprocess.run([str(exe),'--rf-character-manager-scenario'],cwd=root,env=env,capture_output=True,timeout=60,creationflags=subprocess.CREATE_NO_WINDOW);(root/'stdout.txt').write_bytes(run.stdout);(root/'stderr.txt').write_bytes(run.stderr)
    if run.returncode:raise RuntimeError(f'Own fullclient manager check:{run.returncode:#x}:{run.stderr!r};{root}')
    native=json.loads(output.read_text(encoding='utf-8'))
    if native!=gpu['native']:raise ValueError('Fullclient/component Character results differ')
    report={'scope':'Owned fullclient entry:source record/manager/cache/raw-MSH/postload pointers/model route with actual matrix/texture/HAL providers;normal dispatcher/BN/animation/shaders remain open','architecture':'x86','exe':exe.relative_to(WS).as_posix(),'exe_sha256':digest,'entry_rva':hex(pe(exe.read_bytes())['entry_rva']),'native':native,'output':output.relative_to(WS).as_posix(),'output_sha256':sha(output),'game_dlls_loaded':False,'dmalloc_balance':0,'owned_heap_balance':0,'device_and_d3d9_release_counts':0,'component_gpu_report_sha256':sha(WS/'inventory/client455-character-manager-gpu.json'),'reference_report_sha256':sha(WS/'inventory/client455-character-manager-reference.json')}
    (WS/'inventory/client455-character-manager-client.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(native));print(root)
if __name__=='__main__':main()
