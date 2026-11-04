"""Check only our owned compiled module; reference EXEs are never executed."""
import argparse,hashlib,json,shutil,struct,subprocess
from pathlib import Path
from compare_client_binaries import WS,pe

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def fixtures(root):
    for name,data in [('XMSH',b'nodot'),('.MSH',b'dot'),('empty.msh',b'')]:
        (root/name).write_bytes(data)
    pack=root/'pack';pack.mkdir();(pack/'same.MSH').write_bytes(b'loose');(pack/'short.MSH').write_bytes(b'loose-after-short')
    pairs=json.loads((WS/'inventory/character-mesh08-bone-pairs.json').read_text(encoding='utf-8'))
    real=(WS/pairs['samples'][0]['mesh']).read_bytes()
    # The short member is last, so its declared extent exceeds the whole file.
    members=[('same.MSH',b'archive-first',None),('zero.MSH',b'',0),('model.MSH',real,None),('short.MSH',b'x',10000)]
    data=bytearray(struct.pack('<I',len(members)));offset=4+64*len(members);payload=bytearray()
    for name,raw,declared in members:
        data+=struct.pack('<56sII',name.encode(),offset,len(raw) if declared is None else declared);payload+=raw;offset+=len(raw)
    (pack/'DATA0.RFS').write_bytes(data+payload)

def main():
    cli=argparse.ArgumentParser();cli.add_argument('--gpu',action='store_true');args=cli.parse_args();mode='gpu' if args.gpu else 'cpu'
    proof=json.loads((WS/'inventory/client455-character-manager-build.json').read_text(encoding='utf-8'));reference=json.loads((WS/'inventory/client455-character-manager-reference.json').read_text(encoding='utf-8'))
    for name,digest in proof['source_sha256'].items():
        if sha(WS/'scripts/native'/name)!=digest:raise ValueError('Stale Character source:'+name)
    for record in proof['dependencies']:
        if sha(WS/record['file'])!=record['sha256']:raise ValueError('Stale dependency')
    pair=json.loads((WS/'inventory/character-mesh08-bone-pairs.json').read_text(encoding='utf-8'));golden=WS/pair['golden'];ctor=WS/reference['constructor_golden']
    if sha(golden)!=pair['golden_sha256'] or sha(ctor)!=reference['constructor_golden_sha256']:raise ValueError('Golden changed')
    for record in pair['samples']:
        if sha(WS/record['mesh'])!=record['mesh_sha256']:raise ValueError('Pinned model changed')
    texture=json.loads((WS/'inventory/character-texture-inputs.json').read_text(encoding='utf-8'));source=WS/texture['fixture_root']
    for record in texture['fixture_files']:
        if record['relative'].startswith('tex/') and sha(source/record['relative'])!=record['sha256']:raise ValueError('Texture fixture changed')
    dll=Path('C:/Windows/SysWOW64/d3dx9_36.dll');provider='c12f0ab0338eb5031d3d04beaf7208ac848f7e037d21ff963d2af90221cbe935'
    if sha(dll)!=provider:raise ValueError('Pinned D3DX9 provider required')
    original=WS/proof['exe'];digest=sha(original)
    if digest!=proof['exe_sha256']:raise ValueError('Own test EXE changed')
    base=WS/'work/m9'/digest[:8];base.mkdir(parents=True,exist_ok=True);root=base/f'{mode}{len(list(base.glob(mode+"*")))+1:03}';root.mkdir();fixtures(root);shutil.copytree(source/'tex',root/'tex');exe=root/'manager-probe.exe';shutil.copyfile(original,exe);output=root/'result.json'
    run=subprocess.run([str(exe),'--'+mode,str(WS),str(golden),str(ctor),str(dll),str(output)],cwd=root,capture_output=True,timeout=60,creationflags=subprocess.CREATE_NO_WINDOW);(root/'stdout.txt').write_bytes(run.stdout);(root/'stderr.txt').write_bytes(run.stderr)
    if run.returncode:raise RuntimeError(f'Own manager check:{run.returncode:#x}:{run.stderr!r};{root}')
    native=json.loads(output.read_text(encoding='utf-8'))
    if native['status']!='PASS' or native['ctor_fp_modes']!=12 or native['raw_files']!=18 or native['model_files']!=12 or native['model_parts']!=393 or native['physical_parts']!=(276 if args.gpu else 0):raise ValueError('Incomplete Character manager tests')
    report={'scope':'Selected Character455 record/manager/cache/raw-MSH and post-load textures connected to source model pipeline;not normal game dispatcher/legacyBN/animation','architecture':'x86','exe':exe.relative_to(WS).as_posix(),'exe_sha256':digest,'entry_rva':hex(pe(exe.read_bytes())['entry_rva']),'native':native,'output':output.relative_to(WS).as_posix(),'output_sha256':sha(output),'owned_heap_balance':0,'device_and_d3d9_release_counts':0 if args.gpu else None,'build_report_sha256':sha(WS/'inventory/client455-character-manager-build.json'),'reference_report_sha256':sha(WS/'inventory/client455-character-manager-reference.json'),'pair_report_sha256':sha(WS/'inventory/character-mesh08-bone-pairs.json'),'texture_report_sha256':sha(WS/'inventory/character-texture-inputs.json'),'provider_sha256':provider}
    (WS/f'inventory/client455-character-manager-{mode}.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(native));print(root)
if __name__=='__main__':main()
