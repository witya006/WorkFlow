"""Run new secondary flow in the owned full-client diagnostic entry."""
import hashlib,json,os,shutil,subprocess
from compare_client_binaries import WS
from probe_client_helpers import import_names
from probe_client455_pose import inputs

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    *_,dll,_=inputs();build=json.loads((WS/'inventory/client-helper-lab-build.json').read_text(encoding='utf-8'));cpu=json.loads((WS/'inventory/client455-secondary-cpu.json').read_text(encoding='utf-8'));ref=json.loads((WS/'inventory/client455-secondary-reference.json').read_text(encoding='utf-8'));link=json.loads((WS/'inventory/client455-pose-link.json').read_text(encoding='utf-8'))['lab'];golden=WS/ref['golden']
    if build['build_exit'] or len(link['functions'])!=6:raise ValueError('Connected pose/secondary lab required')
    for group in ['lab_input_sha256','pose_input_sha256','animation_input_sha256','legacy_runtime_input_sha256','character_manager_input_sha256','model_input_sha256']:
        for name,digest in build[group].items():
            if sha(WS/name)!=digest:raise ValueError('Stale fullclient source:'+name)
    if cpu['build_report_sha256']!=sha(WS/'inventory/client455-secondary-build.json') or cpu['reference_report_sha256']!=sha(WS/'inventory/client455-secondary-reference.json') or sha(golden)!=ref['golden_sha256']:raise ValueError('Stale secondary proof')
    for record in ref['human_models']:
        if sha(WS/record['copy'])!=record['sha256']:raise ValueError('Changed human skeleton')
    original=WS/'work/client-build/build-helper-lab/Release/RF_Online.bin';digest=sha(original)
    if digest!=link['exe_sha256'] or set(import_names(original.read_bytes(),13))!={'mss32.dll','abuse.dll','adv.dll','pdll.dll'}:raise ValueError('Changed image/game imports')
    base=WS/'work/m9'/digest[:8];base.mkdir(parents=True,exist_ok=True);root=base/f'client{len(list(base.glob("client*")))+1:03}';root.mkdir();exe=root/'RF_Online.bin';shutil.copyfile(original,exe);output=root/'result.json'
    if any(root.rglob('*.dll')) or any(original.parent.glob('*.dll')):raise ValueError('Unexpected local DLL')
    env=os.environ.copy();env.update(RF_POSE_WORKSPACE=str(WS),RF_SECONDARY_GOLDEN=str(golden),RF_POSE_DLL=str(dll),RF_LAB_HELPER_OUTPUT=str(output));run=subprocess.run([str(exe),'--rf-secondary-scenario'],cwd=root,env=env,capture_output=True,timeout=60,creationflags=subprocess.CREATE_NO_WINDOW);(root/'stdout.txt').write_bytes(run.stdout);(root/'stderr.txt').write_bytes(run.stderr)
    if run.returncode:raise RuntimeError(f'Fullclient secondary:{run.returncode:#x}:{run.stderr!r};{root}')
    native=json.loads(output.read_text(encoding='utf-8'))
    if native!=cpu['native']:raise ValueError('Secondary component/fullclient mismatch')
    report={'scope':'Own fullclient connected secondary flow andhuman skeletons;staticCRTsin parity/normal consumers/draw stillopen','exe':exe.relative_to(WS).as_posix(),'exe_sha256':digest,'architecture':'x86','entry_rva':link['entry_rva'],'native':native,'output':output.relative_to(WS).as_posix(),'output_sha256':sha(output),'component_report_sha256':sha(WS/'inventory/client455-secondary-cpu.json'),'game_dlls_loaded':False,'dmalloc_balance':0,'owned_heap_balance':0,'reference_exe_executed':False};(WS/'inventory/client455-secondary-client.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(native));print(root)
if __name__=='__main__':main()
