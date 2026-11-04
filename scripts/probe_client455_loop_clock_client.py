"""Run actual engine timer/animation callers in our complete client build."""
import hashlib,json,os,shutil,subprocess
from compare_client_binaries import WS,pe
from probe_client_helpers import import_names
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    build=json.loads((WS/'inventory/client-helper-lab-build.json').read_text(encoding='utf-8'));ref=json.loads((WS/'inventory/client455-loop-clock-reference.json').read_text(encoding='utf-8'));cpu=json.loads((WS/'inventory/client455-loop-clock-cpu.json').read_text(encoding='utf-8'))
    if build['build_exit'] or build['build_settings'].get('RF_CLIENT_455_LOOP_CLOCK')!='ON':raise ValueError('Loop-enabled fullclient required')
    for group in ['lab_input_sha256','loop_clock_input_sha256','animation_timing_input_sha256']:
        for name,digest in build[group].items():
            if sha(WS/name)!=digest:raise ValueError('Changed loop/actor source')
    original=WS/'work/client-build/build-helper-lab/Release/RF_Online.bin';digest=sha(original);golden=WS/ref['golden']
    if sha(golden)!=ref['golden_sha256'] or set(import_names(original.read_bytes(),13))!={'mss32.dll','abuse.dll','adv.dll','pdll.dll'}:raise ValueError('Changed inputs/delayed imports')
    base=WS/'work/m9'/digest[:8];base.mkdir(parents=True,exist_ok=True);root=base/f'client{len(list(base.glob("client*")))+1:03}';root.mkdir();exe=root/'RF_Online.bin';shutil.copyfile(original,exe);output=root/'result.json'
    if any(root.rglob('*.dll')) or any(original.parent.glob('*.dll')):raise ValueError('Unexpected local DLL')
    env=os.environ.copy();env.update(RF_LOOP_CLOCK_GOLDEN=str(golden),RF_LAB_HELPER_OUTPUT=str(output));run=subprocess.run([str(exe),'--rf-loop-clock-scenario'],cwd=root,env=env,capture_output=True,timeout=30,creationflags=subprocess.CREATE_NO_WINDOW);(root/'stdout.txt').write_bytes(run.stdout);(root/'stderr.txt').write_bytes(run.stderr)
    if run.returncode:raise ValueError(f'Actual clock:{run.returncode:#x}:{run.stderr!r};{root}')
    native=json.loads(output.read_text(encoding='utf-8'));states=json.loads((root/'result.json.clock.json').read_text(encoding='utf-8'));expected=dict(cpu['native']);expected['actual_engine_bridge']=True
    if native['status']!='PASS' or native['failures'] or native['dmalloc_balance'] or native['frame']!=309 or states!=expected:raise ValueError('Actual clock mismatch')
    report={'scope':'Actual R3CalculateTime/get-set/toggles and CResObject numeric caller;not normalWinMain/fullCharacter455 acceptance','architecture':'x86','exe':exe.relative_to(WS).as_posix(),'exe_sha256':digest,'entry_rva':hex(pe(exe.read_bytes())['entry_rva']),'native':native,'states':states,'output':output.relative_to(WS).as_posix(),'output_sha256':sha(output),'states_output':(root/'result.json.clock.json').relative_to(WS).as_posix(),'states_output_sha256':sha(root/'result.json.clock.json'),'component_report_sha256':sha(WS/'inventory/client455-loop-clock-cpu.json'),'game_dlls_loaded':False,'normal_game_entry_executed':False};(WS/'inventory/client455-loop-clock-client.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(native));print(json.dumps(states));print(root)
if __name__=='__main__':main()
