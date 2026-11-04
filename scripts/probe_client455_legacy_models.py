"""Run only our owned parser EXE against pinned BN and synthetic goldens."""
import hashlib,json,shutil,subprocess
from compare_client_binaries import WS

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    build=json.loads((WS/'inventory/client455-legacy-models-build.json').read_text(encoding='utf-8'));ref=json.loads((WS/'inventory/client455-legacy-models-reference.json').read_text(encoding='utf-8'))
    for name,digest in build['source_sha256'].items():
        if sha(WS/'scripts/native'/name)!=digest:raise ValueError('Stale source:'+name)
    for record in ref['samples']:
        if sha(WS/record['copy'])!=record['sha256']:raise ValueError('Changed fixture')
    golden=WS/ref['golden']
    if sha(golden)!=ref['golden_sha256']:raise ValueError('Changed golden')
    original=WS/build['exe'];digest=sha(original)
    if digest!=build['exe_sha256']:raise ValueError('Own native test changed')
    base=WS/'work/m9'/digest[:8];base.mkdir(parents=True,exist_ok=True);root=base/f'cpu{len(list(base.glob("cpu*")))+1:03}';root.mkdir();exe=root/'legacy-probe.exe';shutil.copyfile(original,exe);output=root/'result.json'
    run=subprocess.run([str(exe),str(WS),str(golden),str(output)],cwd=root,capture_output=True,timeout=60,creationflags=subprocess.CREATE_NO_WINDOW);(root/'stdout.txt').write_bytes(run.stdout);(root/'stderr.txt').write_bytes(run.stderr)
    if run.returncode:raise RuntimeError(f'Owned legacy parser check:{run.returncode:#x}:{run.stderr!r};{root}')
    native=json.loads(output.read_text(encoding='utf-8'))
    if native['status']!='PASS' or native['files']!=17 or native['parts']!=459 or native['guarded_prefixes']<1000 or native['allocation_failures']!=7:raise ValueError('Incomplete legacy parser tests')
    report={'scope':'Standalone source intermediateMSH/BN reader/compact physique/lifetime;fullclient import/converter/BNruntime/animation stillpending','architecture':'x86','exe':exe.relative_to(WS).as_posix(),'exe_sha256':digest,'entry_rva':build['entry_rva'],'native':native,'output':output.relative_to(WS).as_posix(),'output_sha256':sha(output),'owned_heap_balance':0,'build_report_sha256':sha(WS/'inventory/client455-legacy-models-build.json'),'reference_report_sha256':sha(WS/'inventory/client455-legacy-models-reference.json'),'reference_exe_executed':False}
    (WS/'inventory/client455-legacy-models-cpu.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(native));print(root)
if __name__=='__main__':main()
