"""Exercise the recovered collection/ANI owner in the complete client lab."""
import json,os,shutil,subprocess
from compare_client_binaries import WS,pe
from probe_client455_animation_manager import inputs,sha,stage
from probe_client_helpers import import_names
def main():
    ref,proof=inputs();build=json.loads((WS/'inventory/client-helper-lab-build.json').read_text(encoding='utf-8'));cpu=json.loads((WS/'inventory/client455-animation-manager-cpu.json').read_text(encoding='utf-8'))
    if build['build_exit'] or build['build_settings'].get('RF_CLIENT_455_ANIMATION_MANAGER')!='ON':raise ValueError('Manager-enabled client required')
    for group in ['lab_input_sha256','animation_manager_input_sha256']:
        for name,digest in build[group].items():
            if sha(WS/name)!=digest:raise ValueError('Changed fullclient manager source')
    original=WS/'work/client-build/build-helper-lab/Release/RF_Online.bin';digest=sha(original)
    if set(import_names(original.read_bytes(),13))!={'mss32.dll','abuse.dll','adv.dll','pdll.dll'}:raise ValueError('GameDLLs mustremain delayed')
    base=WS/'work/m9'/digest[:8];base.mkdir(parents=True,exist_ok=True);root=base/f'client{len(list(base.glob("client*")))+1:03}';root.mkdir();exe=root/'RF_Online.bin';shutil.copyfile(original,exe);stage(root,ref);output=root/'result.json'
    if any(root.rglob('*.dll')) or any(original.parent.glob('*.dll')):raise ValueError('Unexpected local DLL')
    env=os.environ.copy();env.update(RF_LAB_HELPER_OUTPUT=str(output),RF_AM_BYTES=str(ref['sample']['bytes']),RF_AM_MAXIMUM=str(ref['sample']['max_frame']));run=subprocess.run([str(exe),'--rf-animation-manager-scenario'],cwd=root,env=env,capture_output=True,timeout=20,creationflags=subprocess.CREATE_NO_WINDOW);(root/'stdout.txt').write_bytes(run.stdout);(root/'stderr.txt').write_bytes(run.stderr)
    if run.returncode:raise ValueError(f'Fullclient manager:{run.returncode:#x}:{run.stderr!r};{root}')
    native=json.loads(output.read_text(encoding='utf-8'))
    if native!=cpu['native']:raise ValueError('Fullclient manager differsfromcomponent')
    report={'scope':'Source manager/record ownership/one ANI in complete client lab;normal consumers notswitched','architecture':'x86','exe':exe.relative_to(WS).as_posix(),'exe_sha256':digest,'entry_rva':hex(pe(exe.read_bytes())['entry_rva']),'native':native,'output':output.relative_to(WS).as_posix(),'output_sha256':sha(output),'component_report_sha256':sha(WS/'inventory/client455-animation-manager-cpu.json'),'dmalloc_balance':0,'game_dlls_loaded':False,'normal_game_entry_executed':False,'rendered':False};(WS/'inventory/client455-animation-manager-client.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(native));print(root)
if __name__=='__main__':main()
