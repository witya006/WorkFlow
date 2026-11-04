"""Run parser fixtures plus real grade-gated CHAT_INFO input without connections."""
import hashlib,json,os,shutil,subprocess
from compare_client_binaries import WS
from probe_client_helpers import import_names

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    build=json.loads((WS/'inventory/client-helper-lab-build.json').read_text(encoding='utf-8'))
    if build['build_exit'] or build['build_settings'].get('RF_CLIENT_455_TIME_COMMANDS')!='ON':raise ValueError('Successful command-enabled lab required')
    for group in ['lab_input_sha256','weather_input_sha256']:
        for name,digest in build[group].items():
            if sha(WS/name)!=digest:raise ValueError('Stale command lab source:'+name)
    original=WS/'work/client-build/build-helper-lab/Release/RF_Online.bin';digest=sha(original)
    linked=json.loads((WS/'inventory/client455-time-commands-link.json').read_text(encoding='utf-8'))['lab']
    if linked['exe_sha256']!=digest:raise ValueError('Current actual command consumer proof required')
    if set(import_names(original.read_bytes(),13))!={'mss32.dll','abuse.dll','adv.dll','pdll.dll'}:raise ValueError('Game DLLs must remain delayed')
    root=WS/'work/client-time-commands-lab'/digest[:16];root.mkdir(parents=True,exist_ok=True);exe=root/'RF_Online.bin'
    if exe.exists() and sha(exe)!=digest:raise ValueError('Preserving unexpected command lab snapshot')
    if not exe.exists():shutil.copyfile(original,exe)
    if any(root.rglob('*.dll')) or any(original.parent.glob('*.dll')):raise ValueError('Unexpected local game DLL')
    output=root/f'result-{len(list(root.glob("result-*.json")))+1:03}.json';env=os.environ.copy();env['RF_LAB_HELPER_OUTPUT']=str(output)
    run=subprocess.run([str(exe),'--rf-time-commands-scenario'],cwd=root,env=env,capture_output=True,timeout=25,creationflags=subprocess.CREATE_NO_WINDOW)
    if run.returncode:raise ValueError(f'Command lab failed:{run.returncode:#x}:{run.stderr!r}')
    component=json.loads(output.read_text(encoding='utf-8'));input_file=output.with_name(output.name+'.input.json');native=json.loads(input_file.read_text(encoding='utf-8'))
    if component['failures'] or component['checks']!=2628 or component['cases']!=432 or component['precision_rounding_modes']!=12:raise ValueError('Incomplete full-client parser fixtures')
    if native['failures'] or native['checks']!=20 or not native['actual_chat_send_called'] or native['grades']!=[1,0] or native['network_processes_created'] or native['game_dlls_loaded']:raise ValueError('Actual input/access/lifecycle scenario incomplete')
    report={'exe':exe.relative_to(WS).as_posix(),'exe_sha256':digest,'component':component,'input':native,'output_sha256':sha(output),'input_output_sha256':sha(input_file),'output':output.relative_to(WS).as_posix(),'input_output':input_file.relative_to(WS).as_posix(),'link_report_sha256':sha(WS/'inventory/client455-time-commands-link.json'),'scope':'Own full-client entry,real CHAT_INFO/CNetworkMgr construction and SendMessage,grade1 accepts/grade0 rejects,history/prefix and independent clocks. Winsock initialization only,no Create/SetNetSystem/Connect or connections. No reference EXE/game DLL/normal WinMain executed.'}
    (WS/'inventory/client455-time-commands-runtime.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('PASS:432full-client parser cases/2628checks plus20actual CHAT_INFO input/access/lifecycle checks;no connections/game DLLs.')

if __name__=='__main__':main()
