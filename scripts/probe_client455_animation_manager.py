"""Run a focused manager probe with one pinned real ANI, not the bulk suites."""
import hashlib,json,shutil,subprocess
from compare_client_binaries import WS,pe
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def inputs():
    ref=json.loads((WS/'inventory/client455-animation-manager-reference.json').read_text(encoding='utf-8'));build=json.loads((WS/'inventory/client455-animation-manager-build.json').read_text(encoding='utf-8'))
    for name,digest in build['source_sha256'].items():
        if sha(WS/'scripts/native'/name)!=digest:raise ValueError('Changed manager source')
    for item in build['dependencies']:
        if sha(WS/item['file'])!=item['sha256']:raise ValueError('Changed manager dependency')
    if sha(WS/'scripts/audit_client455_animation_manager.py')!=ref['script_sha256'] or sha(WS/ref['sample']['copy'])!=ref['sample']['sha256']:raise ValueError('Changed manager reference')
    return ref,build
def stage(root,ref):
    clips=root/'clips';clips.mkdir();shutil.copyfile(WS/ref['sample']['copy'],clips/'real.ani')
def main():
    ref,build=inputs();original=WS/build['exe'];digest=sha(original)
    if digest!=build['exe_sha256']:raise ValueError('Changed own manager executable')
    base=WS/'work/m9'/digest[:8];base.mkdir(parents=True,exist_ok=True);root=base/f'cpu{len(list(base.glob("cpu*")))+1:03}';root.mkdir();exe=root/'animation-manager-probe.exe';shutil.copyfile(original,exe);stage(root,ref);output=root/'result.json'
    run=subprocess.run([str(exe),str(output),str(ref['sample']['bytes']),str(ref['sample']['max_frame'])],cwd=root,capture_output=True,timeout=20,creationflags=subprocess.CREATE_NO_WINDOW);(root/'stdout.txt').write_bytes(run.stdout);(root/'stderr.txt').write_bytes(run.stderr)
    if run.returncode:raise ValueError(f'Manager:{run.returncode}:{run.stderr!r};{root}')
    native=json.loads(output.read_text(encoding='utf-8'))
    if native['status']!='PASS' or native['groups']!=4 or native['real_ani_files']!=1 or native['owned_heap_balance']:raise ValueError('Manager checks incomplete')
    report={'scope':'Source manager collection/cache/owners plusone real ANI load;not normal455 integration','architecture':'x86','exe':exe.relative_to(WS).as_posix(),'exe_sha256':digest,'entry_rva':hex(pe(exe.read_bytes())['entry_rva']),'native':native,'output':output.relative_to(WS).as_posix(),'output_sha256':sha(output),'build_report_sha256':sha(WS/'inventory/client455-animation-manager-build.json'),'reference_report_sha256':sha(WS/'inventory/client455-animation-manager-reference.json')};(WS/'inventory/client455-animation-manager-cpu.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(native));print(root)
if __name__=='__main__':main()
