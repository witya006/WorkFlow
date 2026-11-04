"""Run our clock probe, never the reference input executable."""
import hashlib,json,subprocess
from compare_client_binaries import WS
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    build=json.loads((WS/'inventory/client455-loop-clock-build.json').read_text(encoding='utf-8'));ref=json.loads((WS/'inventory/client455-loop-clock-reference.json').read_text(encoding='utf-8'));exe=WS/build['exe'];golden=WS/ref['golden'];output=WS/'artifacts/client455-loop-clock/result.json'
    if sha(exe)!=build['exe_sha256'] or sha(golden)!=ref['golden_sha256']:raise ValueError('Changed loop clock inputs')
    run=subprocess.run([str(exe),str(golden),str(output)],cwd=exe.parent,capture_output=True,timeout=20,creationflags=subprocess.CREATE_NO_WINDOW)
    (output.parent/'stdout.txt').write_bytes(run.stdout);(output.parent/'stderr.txt').write_bytes(run.stderr)
    if run.returncode:raise ValueError(f'Loop probe:{run.returncode}:{run.stderr!r}')
    native=json.loads(output.read_text(encoding='utf-8'))
    if native['status']!='PASS' or native['state_cases']!=ref['cases'] or native['failures'] or native['actual_engine_bridge']:raise ValueError('Loop checks incomplete')
    report={'scope':'Finite clock state/OS callback lifecycle/selected duration;not process scheduling equivalence','exe':build['exe'],'exe_sha256':sha(exe),'native':native,'output':output.relative_to(WS).as_posix(),'output_sha256':sha(output),'build_report_sha256':sha(WS/'inventory/client455-loop-clock-build.json'),'reference_report_sha256':sha(WS/'inventory/client455-loop-clock-reference.json')};(WS/'inventory/client455-loop-clock-cpu.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(native))
if __name__=='__main__':main()
