"""Run actual camera-plane publisher and CResObject clipping inside our client."""
import hashlib,json,os,shutil,subprocess
from pathlib import Path
from compare_client_binaries import WS,pe
from probe_client_helpers import import_names

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    build=json.loads((WS/'inventory/client-helper-lab-build.json').read_text(encoding='utf-8'));proof=json.loads((WS/'inventory/client455-frustum-build.json').read_text(encoding='utf-8'));ref=json.loads((WS/'inventory/client455-frustum-reference.json').read_text(encoding='utf-8'));link=json.loads((WS/'inventory/client455-frustum-link.json').read_text(encoding='utf-8'))['lab']
    if build['build_exit'] or build['build_settings'].get('RF_CLIENT_455_FRUSTUM')!='ON':raise ValueError('Selected fullclient build required')
    for group in ['lab_input_sha256','frustum_input_sha256']:
        for name,digest in build[group].items():
            if sha(WS/name)!=digest:raise ValueError('Changed fullclient input:'+name)
    original=WS/'work/client-build/build-helper-lab/Release/RF_Online.bin';digest=sha(original);golden=WS/ref['golden'];dll=Path('C:/Windows/SysWOW64/d3dx9_36.dll')
    if digest!=link['exe_sha256'] or sha(golden)!=ref['golden_sha256'] or sha(dll)!=ref['provider_sha256'] or set(import_names(original.read_bytes(),13))!={'mss32.dll','abuse.dll','adv.dll','pdll.dll'}:raise ValueError('Changed binary/runtime/fixture')
    base=WS/'work/m9'/digest[:8];base.mkdir(parents=True,exist_ok=True);root=base/f'client{len(list(base.glob("client*")))+1:03}';root.mkdir();exe=root/'RF_Online.bin';shutil.copyfile(original,exe);output=root/'result.json'
    if any(original.parent.glob('*.dll')) or any(root.rglob('*.dll')):raise ValueError('Unexpected local DLL')
    env=os.environ.copy();env.update(RF_FRUSTUM_GOLDEN=str(golden),RF_LAB_HELPER_OUTPUT=str(output));run=subprocess.run([str(exe),'--rf-frustum-scenario'],cwd=root,env=env,capture_output=True,timeout=30,creationflags=subprocess.CREATE_NO_WINDOW);(root/'stdout.txt').write_bytes(run.stdout);(root/'stderr.txt').write_bytes(run.stderr)
    if run.returncode:raise ValueError(f'Actual frustum:{run.returncode:#x}:{run.stderr!r};{root}')
    native=json.loads(output.read_text(encoding='utf-8'));numeric=json.loads((root/'result.json.component.json').read_text(encoding='utf-8'));expected=dict(proof['native']);expected['actual_publisher']=True;expected['checks']-=ref['matrix_cases']
    if native['status']!='PASS' or native['failures'] or native['dmalloc_balance'] or native['actor_cases']!=9 or numeric!=expected:raise ValueError('Actual clipping mismatch')
    report={'scope':'Actual SetCharacterClipping and9CResObject cases;no normalWinMain/fullcamera/full455Character acceptance','architecture':'x86','exe':exe.relative_to(WS).as_posix(),'exe_sha256':digest,'entry_rva':hex(pe(exe.read_bytes())['entry_rva']),'native':native,'numeric':numeric,'output':output.relative_to(WS).as_posix(),'output_sha256':sha(output),'numeric_output':(root/'result.json.component.json').relative_to(WS).as_posix(),'numeric_output_sha256':sha(root/'result.json.component.json'),'link_report_sha256':sha(WS/'inventory/client455-frustum-link.json'),'game_dlls_loaded':False,'normal_game_entry_executed':False};(WS/'inventory/client455-frustum-client.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(native));print(json.dumps(numeric));print(root)
if __name__=='__main__':main()
