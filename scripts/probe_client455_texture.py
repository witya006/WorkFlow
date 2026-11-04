"""Run only our newly built x86 texture probe in a fresh short owned directory."""
import argparse,hashlib,json,shutil,subprocess
from pathlib import Path
from compare_client_binaries import WS,pe

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    cli=argparse.ArgumentParser();cli.add_argument('--gpu',action='store_true');args=cli.parse_args()
    build=json.loads((WS/'inventory/client455-texture-build.json').read_text(encoding='utf-8'))
    if build['compile_only']:raise ValueError('Native texture probe required')
    for name,digest in build['source_sha256'].items():
        if sha(WS/'scripts/native'/name)!=digest:raise ValueError('Stale texture source:'+name)
    original=WS/build['exe'];digest=sha(original)
    if digest!=build['exe_sha256']:raise ValueError('Native texture probe changed')
    pe(original.read_bytes());corpus=json.loads((WS/'inventory/character-texture-inputs.json').read_text(encoding='utf-8'));fixtures=WS/corpus['fixture_root']
    for name,digest in corpus['python_source_sha256'].items():
        if sha(WS/'scripts'/name)!=digest:raise ValueError('Independent texture golden source changed')
    for item in corpus['fixture_files']:
        if sha(fixtures/item['relative'])!=item['sha256']:raise ValueError('Texture fixture changed:'+item['relative'])
    dll=Path('C:/Windows/SysWOW64/d3dx9_36.dll');dllsha='c12f0ab0338eb5031d3d04beaf7208ac848f7e037d21ff963d2af90221cbe935'
    if sha(dll)!=dllsha:raise ValueError('Actual pinned D3DX9provider required')
    base=WS/'work/t9'/digest[:8];base.mkdir(parents=True,exist_ok=True);tag='gpu' if args.gpu else 'cpu';runroot=base/f'{tag}{len(list(base.glob(tag+"*")))+1:03}'
    if runroot.exists():raise ValueError('Fresh owned texture workspace required')
    shutil.copytree(fixtures,runroot);exe=runroot/'texture-probe.exe';shutil.copyfile(original,exe);output=runroot/'result.json';frame=runroot/'checker.bmp'
    run=subprocess.run([str(exe),'--'+tag,str(dll),str(output),str(frame)],cwd=runroot,capture_output=True,timeout=60,creationflags=subprocess.CREATE_NO_WINDOW)
    (runroot/'stdout.txt').write_bytes(run.stdout);(runroot/'stderr.txt').write_bytes(run.stderr)
    if run.returncode:raise RuntimeError(f'Texture probe {run.returncode:#x}: {run.stderr!r};{runroot}')
    native=json.loads(output.read_text(encoding='utf-8'))
    if native['status']!='PASS' or native['dds_profiles']!=80:raise ValueError('Incomplete native texture check')
    if args.gpu and (not native['gpu_texture_pairs'] or native['material_parts']!=97 or not native['material_texture_bindings'] or native['cube_orphans_observed_and_released']!=1):raise ValueError('Incomplete realGPU evidence')
    report={'scope':'Own source x86/MT Character texture probe;actual D3DX9_36'+(' and HALD3D9' if args.gpu else ';CPU checks only')+';no reference EXE execution/normal model-loader integration/full client acceptance','exe_sha256':digest,'entry_rva':build['entry_rva'],'architecture':'x86','source_sha256':build['source_sha256'],'native':native,'output':output.relative_to(WS).as_posix(),'output_sha256':sha(output),'fixture_manifest_sha256':sha(WS/'inventory/character-texture-inputs.json'),'dll_sha256':dllsha,'build_report_sha256':sha(WS/'inventory/client455-texture-build.json')}
    if args.gpu:report['frame']=frame.relative_to(WS).as_posix();report['frame_sha256']=sha(frame)
    (WS/f'inventory/client455-texture-{tag}.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(native));print(runroot)
if __name__=='__main__':main()
