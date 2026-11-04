"""Exercise source mesh bindings and actual CPU InitVertex in a full-client lab."""
import argparse,hashlib,json,os,shutil,subprocess
from compare_client_binaries import WS
from probe_client_helpers import import_names

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    cli=argparse.ArgumentParser();cli.add_argument('--init',action='store_true');args=cli.parse_args()
    build=json.loads((WS/'inventory/client-helper-lab-build.json').read_text(encoding='utf-8'))
    for group in ['lab_input_sha256','character_mesh_input_sha256']:
        for name,digest in build[group].items():
            if sha(WS/name)!=digest:raise ValueError('Stale Character mesh lab source:'+name)
    original=WS/'work/client-build/build-helper-lab/Release/RF_Online.bin';digest=sha(original)
    proof=json.loads((WS/'inventory/character-mesh-source-link.json').read_text(encoding='utf-8'))['lab']
    if build['build_exit'] or build['build_settings'].get('RF_CHARACTER_MESH_SOURCE')!='ON' or proof['exe_sha256']!=digest:raise ValueError('Current verified source mesh lab required')
    if set(import_names(original.read_bytes(),13))!={'mss32.dll','abuse.dll','adv.dll','pdll.dll'}:raise ValueError('Game DLLs must remain delayed')
    root=WS/'work/client-character-mesh-lab'/digest[:16];root.mkdir(parents=True,exist_ok=True);exe=root/'RF_Online.bin'
    if exe.exists() and sha(exe)!=digest:raise ValueError('Preserving unexpected Character mesh snapshot')
    if not exe.exists():shutil.copyfile(original,exe)
    if any(root.rglob('*.dll')) or any(original.parent.glob('*.dll')):raise ValueError('Unexpected local game DLL')
    label='init-result' if args.init else 'result';scenario='init' if args.init else 'mesh'
    output=root/f'{label}-{len(list(root.glob(label+"-*.json")))+1:03}.json';env=os.environ.copy();env['RF_LAB_HELPER_OUTPUT']=str(output)
    run=subprocess.run([str(exe),f'--rf-character-{scenario}-scenario'],cwd=root,env=env,capture_output=True,timeout=30,creationflags=subprocess.CREATE_NO_WINDOW)
    if run.returncode:raise ValueError(f'Character mesh full-client scenario failed:{run.returncode:#x}:{run.stderr!r}')
    native=json.loads(output.read_text(encoding='utf-8'))
    if args.init:
        if native['checks_passed']!=6732 or native['cases']!=144 or native['precision_rounding_modes']!=12 or not native['source_init_vertex'] or native['remaining_capture_buffers'] or native['gpu_used']:raise ValueError('Incomplete Character InitVertex scenario')
    elif native['checks_passed']!=245 or native['source_functions']!=4 or not native['actual_init_vertex'] or native['gpu_used']:raise ValueError('Incomplete Character mesh scenario')
    report={'exe':exe.relative_to(WS).as_posix(),'exe_sha256':digest,'native_test':native,'game_dlls_loaded':False,'output':output.relative_to(WS).as_posix(),'output_sha256':sha(output),'link_report_sha256':sha(WS/'inventory/character-mesh-source-link.json'),'scope':'Own full-client CPU entry,4source bindings vs retained SDK,actual InitVertex skinned/unskinned with3vertices/0faces;Dmalloc balanced. No GPU/sockets/game DLLs/normal WinMain/input EXE execution. Remaining Character SDK and455render parity open.'}
    if args.init:report['scope']='Own full-client entry,source InitVertex/vertex/physique vs original SDK;144cases/12FP modes,real SDK MakeVB with test-only COM input capture. Empty textures,0-2faces,create/lock failure,matrices/parents/weights/destruction;Dmalloc balanced. No physical GPU/sockets/game DLLs/normal WinMain/input EXE execution. Full455layout/render parity remains open.'
    name='character-init-source-runtime.json' if args.init else 'character-mesh-source-runtime.json'
    (WS/'inventory'/name).write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(f'PASS:{native["checks_passed"]}full-client Character {scenario} checks;no physical GPU/network/game DLLs.')

if __name__=='__main__':main()
