"""Exercise source Character texture backend through our full-client lab entry."""
import hashlib,json,os,shutil,subprocess
from pathlib import Path
from compare_client_binaries import WS,pe
from probe_client_helpers import import_names

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    build=json.loads((WS/'inventory/client-helper-lab-build.json').read_text(encoding='utf-8'));component=json.loads((WS/'inventory/client455-texture-gpu.json').read_text(encoding='utf-8'));reference=json.loads((WS/'inventory/client455-texture-reference.json').read_text(encoding='utf-8'))
    if build['build_exit'] or build['build_settings'].get('RF_CLIENT_455_TEXTURE')!='ON':raise ValueError('Source texture-enabled fullclient lab required')
    for group in ['lab_input_sha256','texture_input_sha256','mesh_runtime_input_sha256','mesh08_input_sha256']:
        for name,digest in build[group].items():
            if sha(WS/name)!=digest:raise ValueError('Stale full-client texture source:'+name)
    original=WS/'work/client-build/build-helper-lab/Release/RF_Online.bin';digest=sha(original)
    if set(import_names(original.read_bytes(),13))!={'mss32.dll','abuse.dll','adv.dll','pdll.dll'}:raise ValueError('Game DLLs must remain delayed')
    dll=Path(reference['provider']['path'])
    if sha(dll)!=reference['provider']['sha256'] or sha(dll)!=component['dll_sha256']:raise ValueError('Actual texture DLL changed')
    if component['build_report_sha256']!=sha(WS/'inventory/client455-texture-build.json'):raise ValueError('Component texture check stale')
    corpus=json.loads((WS/'inventory/character-texture-inputs.json').read_text(encoding='utf-8'));fixtures=WS/corpus['fixture_root']
    for name,value in corpus['python_source_sha256'].items():
        if sha(WS/'scripts'/name)!=value:raise ValueError('Independent texture fixture source changed')
    if sha(WS/'inventory/character-texture-inputs.json')!=component['fixture_manifest_sha256']:raise ValueError('Texture fixture proof changed')
    for item in corpus['fixture_files']:
        if sha(fixtures/item['relative'])!=item['sha256']:raise ValueError('Pinned texture fixture changed')
    base=WS/'work/t9'/digest[:8];base.mkdir(parents=True,exist_ok=True);root=base/f'client{len(list(base.glob("client*")))+1:03}';shutil.copytree(fixtures,root);exe=root/'RF_Online.bin';shutil.copyfile(original,exe)
    if any(root.rglob('*.dll')) or any(original.parent.glob('*.dll')):raise ValueError('Unexpected local game DLL')
    output=root/'result.json';frame=root/'checker.bmp';env=os.environ.copy();env['RF_LAB_HELPER_OUTPUT']=str(output);env['RF_TEXTURE_DLL']=str(dll);env['RF_TEXTURE_FRAME']=str(frame)
    run=subprocess.run([str(exe),'--rf-texture-scenario'],cwd=root,env=env,capture_output=True,timeout=60,creationflags=subprocess.CREATE_NO_WINDOW);(root/'stdout.txt').write_bytes(run.stdout);(root/'stderr.txt').write_bytes(run.stderr)
    if run.returncode:raise RuntimeError(f'Fullclient source texture probe failed:{run.returncode:#x}:{run.stderr!r};{root}')
    native=json.loads(output.read_text(encoding='utf-8'))
    if native!=component['native'] or sha(frame)!=component['frame_sha256']:raise ValueError('Component/fullclient source texture results differ')
    report={'scope':'Actual fullclient project own entry;source RFS/DDS/cache/material methods create real D3D9textures;normal WinMain/full model-loader integration remains open','exe':exe.relative_to(WS).as_posix(),'exe_sha256':digest,'entry_rva':hex(pe(exe.read_bytes())['entry_rva']),'architecture':'x86','native':native,'output':output.relative_to(WS).as_posix(),'output_sha256':sha(output),'frame':frame.relative_to(WS).as_posix(),'frame_sha256':sha(frame),'component_gpu_report_sha256':sha(WS/'inventory/client455-texture-gpu.json'),'reference_report_sha256':sha(WS/'inventory/client455-texture-reference.json'),'game_dlls_loaded':False,'dmalloc_balance':0,'device_and_d3d9_release_counts':0}
    (WS/'inventory/client455-texture-client.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(native));print(root)
if __name__=='__main__':main()
