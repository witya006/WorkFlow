"""Compile the real D3D9 migration tree and retain unresolved source diagnostics."""
import hashlib,json,re,subprocess
from pathlib import Path
from compare_client_binaries import WS

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    root=WS/'work/client455-port';build=root/'build-vs2026';art=WS/'artifacts/client455-d3d9-port';art.mkdir(parents=True,exist_ok=True);info=json.loads((WS/'inventory/msvc-verification.json').read_text(encoding='utf-8'));cmake=Path(info['installation_path'])/'Common7/IDE/CommonExtensions/Microsoft/CMake/CMake/bin/cmake.exe'
    configure=subprocess.run([str(cmake),'-S',str(root),'-B',str(build),'-G','Visual Studio 18 2026','-A','Win32','-T','v145','-DCMAKE_SYSTEM_VERSION=10.0.26100.0'],capture_output=True,timeout=120,creationflags=subprocess.CREATE_NO_WINDOW);(art/'configure.txt').write_bytes(configure.stdout+configure.stderr)
    if configure.returncode:raise ValueError('D3D9 port configure failed:'+str(art/'configure.txt'))
    run=subprocess.run([str(cmake),'--build',str(build),'--config','Release','--target','R3Engine455','--parallel','4'],capture_output=True,timeout=300,creationflags=subprocess.CREATE_NO_WINDOW);log=art/'build.txt';log.write_bytes(run.stdout+run.stderr);text=log.read_text(encoding='utf-8-sig',errors='replace');errors=[]
    for line in text.splitlines():
        match=re.match(r'(.*?)\((\d+),(\d+)\): (?:fatal )?error ([A-Z]+\d+): (.*?) \[',line)
        if match:
            path=Path(match[1]);errors.append({'file':path.relative_to(WS).as_posix() if path.is_relative_to(WS) else str(path),'line':int(match[2]),'code':match[4],'message':match[5]})
    unique=list({(r['file'],r['line'],r['code'],r['message']):r for r in errors}.values());objects=list((build/'R3Engine455.dir/Release').glob('*.obj'));report={'scope':'Real D3D9 engine source migration;compile evidence only,not455runtime parity','target':'R3Engine455','architecture':'x86','build_exit':run.returncode,'objects':len(objects),'expected_sources':67,'unique_errors':len(unique),'errors':unique,'log':log.relative_to(WS).as_posix(),'log_sha256':sha(log),'source_manifest_sha256':sha(WS/'artifacts/client455-d3d9-port/source-migration.json'),'input_exe_executed':False,'server_modified':False};(WS/'inventory/client455-d3d9-port-build.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:report[k] for k in ['build_exit','objects','expected_sources','unique_errors']}));print(json.dumps(unique[:18],ensure_ascii=False))
    if run.returncode and not unique:raise ValueError('Build failure not parsed:'+str(log))
    if run.returncode:raise SystemExit(run.returncode)
if __name__=='__main__':main()
