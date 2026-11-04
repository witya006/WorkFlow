"""Run the new 600case exact-rational numeric/constructor test only."""
import hashlib,json,shutil,subprocess
from compare_client_binaries import WS

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    build=json.loads((WS/'inventory/client455-animation-timing-build.json').read_text(encoding='utf-8'));ref=json.loads((WS/'inventory/client455-animation-timing-reference.json').read_text(encoding='utf-8'));original=WS/build['exe'];digest=sha(original);golden=WS/ref['golden']
    for name,value in build['source_sha256'].items():
        if sha(WS/'scripts/native'/name)!=value:raise ValueError('Changed timing source')
    if digest!=build['exe_sha256'] or sha(golden)!=ref['golden_sha256'] or sha(WS/'scripts/audit_client455_animation_timing.py')!=ref['script_sha256']:raise ValueError('Changed timing input')
    base=WS/'work/m9'/digest[:8];base.mkdir(parents=True,exist_ok=True);root=base/f'timing{len(list(base.glob("timing*")))+1:03}';root.mkdir();exe=root/'timing-probe.exe';shutil.copyfile(original,exe);output=root/'result.json';run=subprocess.run([str(exe),str(golden),str(output)],cwd=root,capture_output=True,timeout=30,creationflags=subprocess.CREATE_NO_WINDOW);(root/'stdout.txt').write_bytes(run.stdout);(root/'stderr.txt').write_bytes(run.stderr)
    if run.returncode:raise ValueError(f'Timing check:{run.returncode}:{run.stderr!r}')
    native=json.loads(output.read_text(encoding='utf-8'))
    if native['status']!='PASS' or native['cases']!=ref['cases'] or native['failures']:raise ValueError('Incomplete timing check')
    report={'scope':'Exact rational frame kernel andtwo constructors,notwhole Character/actor/runtime','architecture':'x86','exe':exe.relative_to(WS).as_posix(),'exe_sha256':digest,'entry_rva':build['entry_rva'],'native':native,'output':output.relative_to(WS).as_posix(),'output_sha256':sha(output),'build_report_sha256':sha(WS/'inventory/client455-animation-timing-build.json'),'reference_report_sha256':sha(WS/'inventory/client455-animation-timing-reference.json'),'reference_exe_executed':False};(WS/'inventory/client455-animation-timing-cpu.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(native))
if __name__=='__main__':main()
