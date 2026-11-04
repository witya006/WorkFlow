"""Run only new secondary state/math/connected human skeleton checks."""
import hashlib,json,shutil,subprocess
from pathlib import Path
from compare_client_binaries import WS

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    proof=json.loads((WS/'inventory/client455-secondary-build.json').read_text(encoding='utf-8'));ref=json.loads((WS/'inventory/client455-secondary-reference.json').read_text(encoding='utf-8'));original=WS/proof['exe'];digest=sha(original);golden=WS/ref['golden']
    if digest!=proof['exe_sha256'] or sha(WS/proof['source'])!=proof['source_sha256'] or sha(golden)!=ref['golden_sha256'] or sha(WS/'scripts/audit_client455_secondary.py')!=ref['script_sha256'] or sha(WS/'inventory/client455-pose-build.json')!=proof['pose_build_sha256']:raise ValueError('Changed secondary proof')
    for sample in ref['human_models']:
        if sha(WS/sample['copy'])!=sample['sha256']:raise ValueError('Changed human skeleton')
    dll=Path('C:/Windows/SysWOW64/d3dx9_36.dll')
    if sha(dll)!='c12f0ab0338eb5031d3d04beaf7208ac848f7e037d21ff963d2af90221cbe935':raise ValueError('Changed pinned D3DX')
    base=WS/'work/m9'/digest[:8];base.mkdir(parents=True,exist_ok=True);root=base/f'secondary{len(list(base.glob("secondary*")))+1:03}';root.mkdir();exe=root/'secondary-probe.exe';shutil.copyfile(original,exe);output=root/'result.json';run=subprocess.run([str(exe),str(WS),str(golden),str(dll),str(output)],cwd=root,capture_output=True,timeout=60,creationflags=subprocess.CREATE_NO_WINDOW);(root/'stdout.txt').write_bytes(run.stdout);(root/'stderr.txt').write_bytes(run.stderr)
    if run.returncode:raise RuntimeError(f'Secondary check:{run.returncode:#x}:{run.stderr!r};{root}')
    native=json.loads(output.read_text(encoding='utf-8'))
    if native['status']!='PASS' or native['scalar_cases']!=36 or native['human_models']!=2 or native['human_updates']!=6:raise ValueError('Incomplete secondary result')
    report={'scope':'Selected secondary state/matrix flow/connected source human skeletons;CRT sine bit parity/normal consumers/animateddraw remain open','exe':exe.relative_to(WS).as_posix(),'exe_sha256':digest,'architecture':'x86','entry_rva':proof['entry_rva'],'native':native,'output':output.relative_to(WS).as_posix(),'output_sha256':sha(output),'build_report_sha256':sha(WS/'inventory/client455-secondary-build.json'),'reference_report_sha256':sha(WS/'inventory/client455-secondary-reference.json'),'owned_heap_balance':0,'reference_exe_executed':False};(WS/'inventory/client455-secondary-cpu.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(native));print(root)
if __name__=='__main__':main()
