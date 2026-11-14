"""Compile real normal455consumer objects, recording actual compiler blockers."""
import argparse,hashlib,json,re,subprocess,time
from pathlib import Path
from compare_client_binaries import WS

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--clean-first',action='store_true',help='Recompile client objects from retained source and pinned dependencies')
    args=parser.parse_args()
    from workspace_guard import require_budget
    require_budget()
    root=WS/'work/client455-port/normal';art=WS/'artifacts/client455-normal';info=json.loads((WS/'inventory/msvc-verification.json').read_text());cmake=Path(info['installation_path'])/'Common7/IDE/CommonExtensions/Microsoft/CMake/CMake/bin/cmake.exe'
    config=subprocess.run([str(cmake),'-S',str(root),'-B',str(root/'build'),'-G','Visual Studio 18 2026','-A','Win32','-T','v145','-DCMAKE_SYSTEM_VERSION=10.0.26100.0'],capture_output=True,creationflags=subprocess.CREATE_NO_WINDOW)
    (art/'configure.txt').write_bytes(config.stdout+config.stderr)
    if config.returncode:raise ValueError('Normal455configure failed')
    started=time.monotonic()
    command=[str(cmake),'--build',str(root/'build'),'--config','Release','--target','RFClient455Consumers','RFClient455Facade','RFClient455Kernels','--parallel','4']
    if args.clean_first:command.append('--clean-first')
    run=subprocess.run(command,capture_output=True,timeout=300,creationflags=subprocess.CREATE_NO_WINDOW)
    raw=run.stdout+run.stderr;(art/'build.txt').write_bytes(raw);errors=[]
    for line in raw.decode('utf-8-sig',errors='replace').splitlines():
        match=re.match(r'(.*?)\((\d+),(\d+)\): (?:fatal )?error ([A-Z]+\d+): (.*?) \[',line)
        if match:
            p=Path(match[1]);errors.append({'file':p.relative_to(WS).as_posix() if p.is_relative_to(WS) else str(p),'line':int(match[2]),'code':match[4],'message':match[5]})
    errors=list({tuple(r.values()):r for r in errors}.values());objects=list((root/'build/RFClient455Consumers.dir/Release').glob('*.obj'))
    report={'scope':'Real normal455consumer compilation,not successful executable link/runtime acceptance','build_exit':run.returncode,'original_sources':180,'expected_sources':182,'objects':len(objects),'errors':errors,'log':'artifacts/client455-normal/build.txt','log_sha256':hashlib.sha256(raw).hexdigest(),'source_manifest_sha256':hashlib.sha256((art/'sources.json').read_bytes()).hexdigest(),'legacy_character_linked':False,'M6':'OPEN','M9':'OPEN'}
    report.update(clean_first=args.clean_first,build_seconds=round(time.monotonic()-started,2))
    kernels=list((root/'build/RFClient455Kernels.dir/Release').glob('*.obj'));preparation=json.loads((WS/'inventory/client455-normal-preparation.json').read_text());report['canonical_kernel_objects']=len(kernels);report['expected_kernel_sources']=len(preparation['canonical_kernel_sources'])
    if not run.returncode and len(kernels)!=report['expected_kernel_sources']:raise ValueError('Incomplete canonical kernel set')
    (WS/'inventory/client455-normal-build.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'exit':run.returncode,'objects':len(objects),'canonical_kernels':len(kernels),'errors':len(errors)}));print(json.dumps(errors[:12],ensure_ascii=False))
    if run.returncode:raise SystemExit(run.returncode)
if __name__=='__main__':main()
