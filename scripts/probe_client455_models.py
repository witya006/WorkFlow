"""Run only our own compiled model test,in a fresh owned cwd with texture copies."""
import argparse,hashlib,json,shutil,subprocess
from pathlib import Path
from compare_client_binaries import WS,pe
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    cli=argparse.ArgumentParser();cli.add_argument('--gpu',action='store_true');args=cli.parse_args();mode='gpu' if args.gpu else 'cpu'
    build=json.loads((WS/'inventory/client455-models-build.json').read_text(encoding='utf-8'))
    if build['compile_only']:raise ValueError('Native model test required')
    for name,digest in build['source_sha256'].items():
        if sha(WS/'scripts/native'/name)!=digest:raise ValueError('Stale source model test:'+name)
    pairs=json.loads((WS/'inventory/character-mesh08-bone-pairs.json').read_text(encoding='utf-8'));golden=WS/pairs['golden']
    if sha(golden)!=pairs['golden_sha256']:raise ValueError('Paired model golden changed')
    for sample in pairs['samples']:
        if sha(WS/sample['mesh'])!=sample['mesh_sha256']:raise ValueError('Pinned model changed')
    textures=json.loads((WS/'inventory/character-texture-inputs.json').read_text(encoding='utf-8'));fixtures=WS/textures['fixture_root']
    for record in textures['fixture_files']:
        if record['relative'].startswith('tex/') and sha(fixtures/record['relative'])!=record['sha256']:raise ValueError('Pinned texture fixture changed')
    dll=Path('C:/Windows/SysWOW64/d3dx9_36.dll');dllsha='c12f0ab0338eb5031d3d04beaf7208ac848f7e037d21ff963d2af90221cbe935'
    if sha(dll)!=dllsha:raise ValueError('Pinned real D3DX9provider required')
    original=WS/build['exe'];digest=sha(original)
    if digest!=build['exe_sha256']:raise ValueError('Model test changed')
    base=WS/'work/m9'/digest[:8];base.mkdir(parents=True,exist_ok=True);root=base/f'{mode}{len(list(base.glob(mode+"*")))+1:03}';root.mkdir();shutil.copytree(fixtures/'tex',root/'tex');exe=root/'model-probe.exe';shutil.copyfile(original,exe);output=root/'result.json'
    run=subprocess.run([str(exe),'--'+mode,str(WS),str(golden),str(dll),str(output)],cwd=root,capture_output=True,timeout=60,creationflags=subprocess.CREATE_NO_WINDOW);(root/'stdout.txt').write_bytes(run.stdout);(root/'stderr.txt').write_bytes(run.stderr)
    if run.returncode:raise RuntimeError(f'Model native check:{run.returncode:#x}:{run.stderr!r};{root}')
    native=json.loads(output.read_text(encoding='utf-8'))
    if native['status']!='PASS' or native['real_files']!=12 or native['model_parts']!=393 or native['lifetime_cases']!=12 or native['physical_uploaded_parts']!=(276 if args.gpu else 0):raise ValueError('Incomplete model lifetime/pipeline checks')
    report={'scope':'Own source model lifetime+MESH08pipeline,actual D3DX9matrix'+('/HALtextures/buffers' if args.gpu else ';no physicalGPU')+';normal game dispatch/full animation/shaders not integrated','architecture':'x86','exe':exe.relative_to(WS).as_posix(),'exe_sha256':digest,'entry_rva':hex(pe(exe.read_bytes())['entry_rva']),'native':native,'output':output.relative_to(WS).as_posix(),'output_sha256':sha(output),'build_report_sha256':sha(WS/'inventory/client455-models-build.json'),'reference_report_sha256':sha(WS/'inventory/client455-models-reference.json'),'paired_report_sha256':sha(WS/'inventory/character-mesh08-bone-pairs.json'),'texture_report_sha256':sha(WS/'inventory/character-texture-inputs.json'),'matrix_texture_provider_sha256':dllsha}
    (WS/f'inventory/client455-models-{mode}.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(native));print(root)
if __name__=='__main__':main()
