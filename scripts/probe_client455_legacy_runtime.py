"""Run owned source converter with byte capture oractual HAL;never inputEXEs."""
import argparse,hashlib,json,shutil,struct,subprocess
from pathlib import Path
from compare_client_binaries import WS

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def fixtures(root):
    source=WS/'work/client-reference/character-legacy-runtime/scene_plain.msh';raw=source.read_bytes();(root/'broken.msh').write_bytes(raw);(root/'broken.mtg').write_bytes(b'x');pack=root/'pack';pack.mkdir()
    (pack/'DATA0.RFS').write_bytes(struct.pack('<I56sII',1,b'scene.any',68,len(raw))+raw)

def main():
    cli=argparse.ArgumentParser();cli.add_argument('--gpu',action='store_true');args=cli.parse_args();mode='gpu' if args.gpu else 'cpu'
    build=json.loads((WS/'inventory/client455-legacy-runtime-build.json').read_text(encoding='utf-8'));inputs=json.loads((WS/'inventory/client455-legacy-runtime-inputs.json').read_text(encoding='utf-8'))
    if build['compile_only']:raise ValueError('Native converter test required')
    for name,digest in build['source_sha256'].items():
        if sha(WS/'scripts/native'/name)!=digest:raise ValueError('Stale source:'+name)
    for record in build['dependencies']:
        if sha(WS/record['file'])!=record['sha256']:raise ValueError('Changed linked dependency')
    for record in inputs['samples']:
        if sha(WS/record['copy'])!=record['sha256'] or (record['mtg'] and sha(WS/record['mtg'])!=record['mtg_sha256']):raise ValueError('Changed converter fixture')
    golden=WS/inputs['golden']
    if sha(golden)!=inputs['golden_sha256'] or inputs['reference_report_sha256']!=sha(WS/'inventory/client455-legacy-runtime-reference.json'):raise ValueError('Changed converter golden/reference')
    pairs=json.loads((WS/'inventory/character-mesh08-bone-pairs.json').read_text(encoding='utf-8'));pair=WS/pairs['golden']
    if sha(pair)!=pairs['golden_sha256']:raise ValueError('Changed pairing golden')
    for sample in pairs['samples']:
        if sha(WS/sample['mesh'])!=sample['mesh_sha256']:raise ValueError('Changed MESH08 fixture')
    textures=json.loads((WS/'inventory/character-texture-inputs.json').read_text(encoding='utf-8'));textureRoot=WS/textures['fixture_root']
    for record in textures['fixture_files']:
        if record['relative'].startswith('tex/') and sha(textureRoot/record['relative'])!=record['sha256']:raise ValueError('Changed texture fixture')
    dll=Path('C:/Windows/SysWOW64/d3dx9_36.dll');provider='c12f0ab0338eb5031d3d04beaf7208ac848f7e037d21ff963d2af90221cbe935'
    if sha(dll)!=provider:raise ValueError('Pinned D3DX9 provider required')
    original=WS/build['exe'];digest=sha(original)
    if digest!=build['exe_sha256']:raise ValueError('Own test changed')
    base=WS/'work/m9'/digest[:8];base.mkdir(parents=True,exist_ok=True);root=base/f'{mode}{len(list(base.glob(mode+"*")))+1:03}';root.mkdir();fixtures(root);shutil.copytree(textureRoot/'tex',root/'tex');exe=root/'runtime-probe.exe';shutil.copyfile(original,exe);output=root/'result.json'
    run=subprocess.run([str(exe),'--'+mode,str(WS),str(golden),str(pair),str(dll),str(output)],cwd=root,capture_output=True,timeout=60,creationflags=subprocess.CREATE_NO_WINDOW);(root/'stdout.txt').write_bytes(run.stdout);(root/'stderr.txt').write_bytes(run.stderr)
    if run.returncode:raise RuntimeError(f'Owned converter check:{run.returncode:#x}:{run.stderr!r};{root}')
    native=json.loads(output.read_text(encoding='utf-8'))
    if native['status']!='PASS' or native['model_runs']!=34 or native['model_parts']!=2*inputs['parts'] or native['paired_files']!=12 or native['paired_parts']!=393 or native['cpu_retained_parts']<2 or native['physical_indexed_parts']!=(832 if args.gpu else 0) or native['paired_physical_parts']!=(276 if args.gpu else 0):raise ValueError('Incomplete legacy converter test')
    report={'scope':'Full selected legacyconverter/fileIO/weights/indexing/MTG/CPUretention withactual BN→MESH08pairs;standalone,normal game animation/shaders/dispatcher stillopen','architecture':'x86','exe':exe.relative_to(WS).as_posix(),'exe_sha256':digest,'entry_rva':build['entry_rva'],'native':native,'output':output.relative_to(WS).as_posix(),'output_sha256':sha(output),'owned_heap_balance':0,'device_and_d3d9_release_counts':0 if args.gpu else None,'build_report_sha256':sha(WS/'inventory/client455-legacy-runtime-build.json'),'reference_report_sha256':sha(WS/'inventory/client455-legacy-runtime-reference.json'),'input_report_sha256':sha(WS/'inventory/client455-legacy-runtime-inputs.json'),'pair_report_sha256':sha(WS/'inventory/character-mesh08-bone-pairs.json'),'texture_report_sha256':sha(WS/'inventory/character-texture-inputs.json'),'provider_sha256':provider,'reference_exe_executed':False}
    (WS/f'inventory/client455-legacy-runtime-{mode}.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(native));print(root)
if __name__=='__main__':main()
