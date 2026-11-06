"""Measure the current source layout before adapting the455particle runtime."""
import hashlib,json,subprocess
from pathlib import Path
from client455_own_probe import build_full_object_probe
from compare_client_binaries import WS

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    source=WS/'scripts/native/client455_particle_layout_probe.cpp';exe=build_full_object_probe('particle-layout',source)
    run=subprocess.run([str(exe)],cwd=exe.parent,capture_output=True,timeout=15,creationflags=subprocess.CREATE_NO_WINDOW)
    if run.returncode:raise ValueError('Layout probe failed')
    result=json.loads(run.stdout);report=dict(scope='Measured owned455particle/entity source fields and exact1296byte particle constructor;fullparticle acceptance remains open',
        script_sha256=sha(Path(__file__)),source=dict(file=source.relative_to(WS).as_posix(),sha256=sha(source)),
        normal_link_sha256=sha(WS/'inventory/client455-normal-link.json'),engine_report_sha256=sha(WS/'inventory/client455-startup-engine-build.json'),
        exe=dict(file=exe.relative_to(WS).as_posix(),sha256=sha(exe)),native=result,input_exe_executed=False,server_modified=False,M6='OPEN',M9='OPEN')
    (WS/'inventory/client455-particle-layout.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
