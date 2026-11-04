"""Run deterministic clock checks through the own full-client laboratory entry."""
import argparse,hashlib,json,os,shutil,subprocess
from compare_client_binaries import WS
from probe_client_helpers import import_names

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    cli=argparse.ArgumentParser();cli.add_argument('--map-time',action='store_true');args=cli.parse_args()
    label='map-time' if args.map_time else 'clock';checks=314 if args.map_time else 1443
    build=json.loads((WS/'inventory/client-helper-lab-build.json').read_text(encoding='utf-8'))
    if build['build_exit'] or build['build_settings'].get('RF_CLIENT_455_CLOCK')!='ON':raise ValueError('Successful clock-enabled lab required')
    if args.map_time and build['build_settings'].get('RF_CLIENT_455_MAP_TIME')!='ON':raise ValueError('Map time branch must be enabled')
    for group in ['lab_input_sha256','weather_input_sha256']:
        for name,digest in build[group].items():
            if sha(WS/name)!=digest:raise ValueError('Stale clock lab source:'+name)
    original=WS/'work/client-build/build-helper-lab/Release/RF_Online.bin';digest=sha(original)
    linked=json.loads((WS/f'inventory/client455-{label}-link.json').read_text(encoding='utf-8'))['lab']
    if linked['exe_sha256']!=digest or (not args.map_time and len(linked['functions'])!=11):raise ValueError('Full lab linked clock proof required')
    if set(import_names(original.read_bytes(),13))!={'mss32.dll','abuse.dll','adv.dll','pdll.dll'}:raise ValueError('Game DLLs must remain delayed')
    root=WS/f'work/client-{label}-lab'/digest[:16];root.mkdir(parents=True,exist_ok=True)
    exe=root/'RF_Online.bin'
    if exe.exists() and sha(exe)!=digest:raise ValueError('Preserving unexpected clock snapshot')
    if not exe.exists():shutil.copyfile(original,exe)
    if any(root.rglob('*.dll')) or any(original.parent.glob('*.dll')):raise ValueError('Unexpected local game DLL')
    output=root/f'result-{len(list(root.glob("result-*.json")))+1:03}.json'
    env=os.environ.copy();env['RF_LAB_HELPER_OUTPUT']=str(output)
    run=subprocess.run([str(exe),f'--rf-{label}-scenario'],cwd=root,env=env,capture_output=True,timeout=20,creationflags=subprocess.CREATE_NO_WINDOW)
    native=json.loads(output.read_text(encoding='utf-8')) if output.exists() else {}
    if run.returncode or native.get('failures') or native.get('checks')!=checks or native.get('precision_rounding_modes')!=12:raise ValueError(f'Full-client clock check failed:{run.returncode}:{native}')
    report={'exe':exe.relative_to(WS).as_posix(),'exe_sha256':digest,'native_test':native,'output':output.relative_to(WS).as_posix(),'output_sha256':sha(output),'link_report_sha256':sha(WS/f'inventory/client455-{label}-link.json'),'game_dlls_loaded':False,'scope':'Actual compiled clock/map-time inside full client; deterministic provider installed by the test only and restored. No normal WinMain, network, GPU or reference input execution.'}
    (WS/f'inventory/client455-{label}-runtime.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(f'PASS:{checks}actual full-client {label} checks/12FP modes;game DLLs absent.')

if __name__=='__main__':main()
