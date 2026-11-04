"""Run only own compiled shared-buffer probe;copied assets read-only,hidden HAL."""
import argparse,hashlib,json,shutil,subprocess
from compare_client_binaries import WS,pe
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    cli=argparse.ArgumentParser();cli.add_argument('--gpu',action='store_true');args=cli.parse_args();mode='gpu' if args.gpu else 'cpu'
    build=json.loads((WS/'inventory/client455-shared-buffers-build.json').read_text(encoding='utf-8'))
    for name,value in build['source_sha256'].items():
        if sha(WS/'scripts/native'/name)!=value:raise ValueError('Stale shared buffer source:'+name)
    samples=json.loads((WS/'inventory/character-mesh08-bone-pairs.json').read_text(encoding='utf-8'))['samples']
    if len(samples)!=12:raise ValueError('Twelve pinned mesh inputs required')
    for sample in samples:
        if sha(WS/sample['mesh'])!=sample['mesh_sha256']:raise ValueError('Pinned mesh changed')
    original=WS/build['exe'];digest=sha(original)
    if digest!=build['exe_sha256']:raise ValueError('Shared buffer probe changed')
    base=WS/'work/b9'/digest[:8];base.mkdir(parents=True,exist_ok=True);root=base/f'{mode}{len(list(base.glob(mode+"*")))+1:03}';root.mkdir();exe=root/'buffer-probe.exe';shutil.copyfile(original,exe);output=root/'result.json';frame=root/'frame'
    run=subprocess.run([str(exe),'--'+mode,str(WS),str(output),str(frame)],cwd=root,capture_output=True,timeout=60,creationflags=subprocess.CREATE_NO_WINDOW);(root/'stdout.txt').write_bytes(run.stdout);(root/'stderr.txt').write_bytes(run.stderr)
    if run.returncode:raise RuntimeError(f'Shared buffer test:{run.returncode:#x}:{run.stderr!r};{root}')
    native=json.loads(output.read_text(encoding='utf-8'))
    if native['status']!='PASS' or native['capture_pool_types']!=3 or native['real_files']!=12 or native['model_parts']!=393 or native['gpu_draws']!=(4 if args.gpu else 0):raise ValueError('Incomplete shared buffer test')
    if args.gpu and (native['gpu_model_parts']!=393 or native['gpu_model_uploads']!=276):raise ValueError('Real mesh GPU coverage incomplete')
    report={'scope':'Own shared-buffer source+test-only COM capture;'+('actual HALD3D9 managed buffers and4synthetic indexed draws' if args.gpu else 'no physicalGPU')+';not full Character renderer/normal model loader','architecture':'x86','exe':exe.relative_to(WS).as_posix(),'exe_sha256':digest,'entry_rva':hex(pe(exe.read_bytes())['entry_rva']),'native':native,'output':output.relative_to(WS).as_posix(),'output_sha256':sha(output),'source_sha256':build['source_sha256'],'build_report_sha256':sha(WS/'inventory/client455-shared-buffers-build.json'),'reference_report_sha256':sha(WS/'inventory/client455-shared-buffers-reference.json'),'mesh_inputs':[{'file':s['mesh'],'sha256':s['mesh_sha256']} for s in samples]}
    if args.gpu:report['frames']=[{'file':(root/f'frame-{stride}.bmp').relative_to(WS).as_posix(),'sha256':sha(root/f'frame-{stride}.bmp')} for stride in [36,64]]
    (WS/f'inventory/client455-shared-buffers-{mode}.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(native));print(root)
if __name__=='__main__':main()
