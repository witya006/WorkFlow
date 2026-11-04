"""Run owned ANI/character dispatcher; never execute input EXEs."""
import argparse,hashlib,json,shutil,struct,subprocess
from pathlib import Path
from compare_client_binaries import WS

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def fixtures(root):
    raw=(WS/'work/client-reference/character-animation455/channels.ani').read_bytes()
    (root/'XANI').write_bytes(raw);(root/'broken.ani').write_bytes(b'\x01\0\0\0');(root/'empty.bn').write_bytes(b'\0\0')
    header=bytearray(693);header[:8]=b'oversize';struct.pack_into('<H',header,394,21334)
    (root/'oversize.msh').write_bytes(b'\x01\0'+header+bytes(88*21334))
    pack=root/'pack';pack.mkdir();offset=4+2*64
    directory=struct.pack('<I',2)+struct.pack('<56sII',b'packed.ani',offset,len(raw))+struct.pack('<56sII',b'short.ani',offset+len(raw),10000)
    (pack/'DATA0.RFS').write_bytes(directory+raw+b'x');(pack/'short.ani').write_bytes(raw)

def inputs():
    build=json.loads((WS/'inventory/client455-animation-build.json').read_text(encoding='utf-8'));reference=json.loads((WS/'inventory/client455-animation-reference.json').read_text(encoding='utf-8'))
    if build['compile_only']:raise ValueError('Native animation test required')
    for name,digest in build['source_sha256'].items():
        if sha(WS/'scripts/native'/name)!=digest:raise ValueError('Stale animation source:'+name)
    for record in build['dependencies']:
        if sha(WS/record['file'])!=record['sha256']:raise ValueError('Changed linked animation dependency')
    if sha(WS/'scripts/audit_client455_animation.py')!=reference['script_sha256'] or sha(WS/'scripts/ani455.py')!=reference['framing_script_sha256']:raise ValueError('Changed ANI oracle')
    for record in reference['samples']:
        if sha(WS/record['copy'])!=record['sha256']:raise ValueError('Changed ANI fixture')
    golden=WS/reference['golden']
    if sha(golden)!=reference['golden_sha256']:raise ValueError('Changed ANI golden')
    pairs=json.loads((WS/'inventory/character-mesh08-bone-pairs.json').read_text(encoding='utf-8'));pair=WS/pairs['golden']
    if sha(pair)!=pairs['golden_sha256']:raise ValueError('Changed pair golden')
    for i,sample in enumerate(pairs['samples']):
        if sha(WS/sample['mesh'])!=sample['mesh_sha256'] or sha(WS/f'work/client-reference/character-legacy-runtime/real_{i:02}.bn')!=sample['skeleton_sha256']:raise ValueError('Changed mesh/BN fixture')
    textures=json.loads((WS/'inventory/character-texture-inputs.json').read_text(encoding='utf-8'));texture_root=WS/textures['fixture_root']
    for record in textures['fixture_files']:
        if record['relative'].startswith('tex/') and sha(texture_root/record['relative'])!=record['sha256']:raise ValueError('Changed texture fixture')
    dll=Path('C:/Windows/SysWOW64/d3dx9_36.dll');provider='c12f0ab0338eb5031d3d04beaf7208ac848f7e037d21ff963d2af90221cbe935'
    if sha(dll)!=provider:raise ValueError('Pinned D3DX9 provider required')
    return build,reference,golden,pairs,pair,textures,texture_root,dll,provider

def main():
    cli=argparse.ArgumentParser();cli.add_argument('--gpu',action='store_true');args=cli.parse_args();mode='gpu' if args.gpu else 'cpu'
    build,reference,golden,pairs,pair,textures,texture_root,dll,provider=inputs()
    original=WS/build['exe'];digest=sha(original)
    if digest!=build['exe_sha256']:raise ValueError('Own animation test changed')
    base=WS/'work/m9'/digest[:8];base.mkdir(parents=True,exist_ok=True);root=base/f'{mode}{len(list(base.glob(mode+"*")))+1:03}';root.mkdir();fixtures(root);shutil.copytree(texture_root/'tex',root/'tex');exe=root/'animation-probe.exe';shutil.copyfile(original,exe);output=root/'result.json'
    run=subprocess.run([str(exe),'--'+mode,str(WS),str(golden),str(pair),str(dll),str(output)],cwd=root,capture_output=True,timeout=60,creationflags=subprocess.CREATE_NO_WINDOW);(root/'stdout.txt').write_bytes(run.stdout);(root/'stderr.txt').write_bytes(run.stderr)
    if run.returncode:raise RuntimeError(f'Owned ANI check:{run.returncode:#x}:{run.stderr!r};{root}')
    native=json.loads(output.read_text(encoding='utf-8'));parts=sum(s['meshes']+s['skeleton_meshes'] for s in pairs['samples'][1:])
    if native['status']!='PASS' or native['ani_files']!=27 or native['tracks']!=reference['total_tracks'] or native['real_ani_matches']!=22 or native['model_parts']!=parts or bool(native['physical_parts'])!=args.gpu or native['stranded_raw_blocks_observed_and_harness_freed']!=1:raise ValueError('Incomplete ANI/dispatcher test')
    report={'scope':'Selected raw ANI/record/attachment/character dispatch;normal consumers/pose/shaders/async manager still open','architecture':'x86','exe':exe.relative_to(WS).as_posix(),'exe_sha256':digest,'entry_rva':build['entry_rva'],'native':native,'output':output.relative_to(WS).as_posix(),'output_sha256':sha(output),'owned_heap_balance_after_explicit_reference_leak_observation':0,'device_and_d3d9_release_counts':0 if args.gpu else None,'build_report_sha256':sha(WS/'inventory/client455-animation-build.json'),'reference_report_sha256':sha(WS/'inventory/client455-animation-reference.json'),'pair_report_sha256':sha(WS/'inventory/character-mesh08-bone-pairs.json'),'texture_report_sha256':sha(WS/'inventory/character-texture-inputs.json'),'provider_sha256':provider,'reference_exe_executed':False}
    (WS/f'inventory/client455-animation-{mode}.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(native));print(root)
if __name__=='__main__':main()
