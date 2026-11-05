"""Check pinned shader bootstrap/HAL draw in the full project own entry."""
import json,os,shutil,subprocess,struct
from compare_client_binaries import WS,pe
from probe_client455_shaders import inputs,sha,stage,source_proof
from probe_client_helpers import import_names
def main():
    ref,proof,dll=inputs();build=json.loads((WS/'inventory/client-helper-lab-build.json').read_text(encoding='utf-8'));gpu=json.loads((WS/'inventory/client455-shaders-gpu.json').read_text(encoding='utf-8'))
    if build['build_exit'] or build['build_settings'].get('RF_CLIENT_455_SHADERS')!='ON':raise ValueError('Shader-enabled client required')
    for group in ['lab_input_sha256','shader_input_sha256']:
        for name,digest in build[group].items():
            if sha(WS/name)!=digest:raise ValueError('Changed shader caller source')
    original=WS/'work/client-build/build-helper-lab/Release/RF_Online.bin';digest=sha(original)
    if set(import_names(original.read_bytes(),13))!={'mss32.dll','abuse.dll','adv.dll','pdll.dll'}:raise ValueError('Game DLLs mustremain delayed')
    base=WS/'work/m9'/digest[:8];base.mkdir(parents=True,exist_ok=True);root=base/f'client{len(list(base.glob("client*")))+1:03}';root.mkdir();stage(root,ref);exe=root/'RF_Online.bin';shutil.copyfile(original,exe);output=root/'result.json'
    if any(root.rglob('*.dll')) or any(original.parent.glob('*.dll')):raise ValueError('Unexpected local DLL')
    env=os.environ.copy();env.update(RF_SHADER_DLL=str(dll),RF_LAB_HELPER_OUTPUT=str(output));run=subprocess.run([str(exe),'--rf-shaders-scenario'],cwd=root,env=env,capture_output=True,timeout=60,creationflags=subprocess.CREATE_NO_WINDOW);(root/'stdout.txt').write_bytes(run.stdout);(root/'stderr.txt').write_bytes(run.stderr)
    if run.returncode:raise ValueError(f'Fullclient shader:{run.returncode:#x}:{run.stderr!r};{root}')
    native=json.loads(output.read_text(encoding='utf-8'))
    if native!=gpu['native'] or sha(root/'shader-frame.bgra')!=gpu['frame_sha256']:raise ValueError('Fullclient shader/frame differsfromcomponent')
    sources=source_proof(root,ref);pixels=(root/'shader-frame.bgra').read_bytes();bitmap=root/'shader-frame.bmp';bitmap.write_bytes(struct.pack('<2sIHHI',b'BM',54+len(pixels),0,0,54)+struct.pack('<IiiHHIIiiII',40,64,-64,1,32,0,len(pixels),0,0,0,0)+pixels)
    report={'scope':'Source Character shader bootstrap/HAL resources in fullclient ownentry;triangle is harness,not fullCharacter draw','architecture':'x86','exe':exe.relative_to(WS).as_posix(),'exe_sha256':digest,'entry_rva':hex(pe(exe.read_bytes())['entry_rva']),'native':native,'output':output.relative_to(WS).as_posix(),'output_sha256':sha(output),'frame':(root/'shader-frame.bgra').relative_to(WS).as_posix(),'frame_sha256':sha(root/'shader-frame.bgra'),'preview':bitmap.relative_to(WS).as_posix(),'actual_compiler_sources':sources,'component_report_sha256':sha(WS/'inventory/client455-shaders-gpu.json'),'dmalloc_balance':0,'game_dlls_loaded':False,'normal_game_entry_executed':False};(WS/'inventory/client455-shaders-client.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(native));print(root)
if __name__=='__main__':main()
