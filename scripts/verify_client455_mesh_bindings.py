"""Verify selected455source CPU kernels without claiming normal loader integration."""
import argparse,hashlib,json,re,subprocess
from pathlib import Path
from compare_client_binaries import WS
from verify_client_coff import directives

SYMBOLS=['_RF455_FindParentMesh','_RF455_BindMeshParents','_RF455_RematchMeshParents','_RF455_ResolveMesh08Bones']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    cli=argparse.ArgumentParser();cli.add_argument('--lab',action='store_true');args=cli.parse_args();mode='lab' if args.lab else 'normal'
    build=WS/'work/client-build'/('build-helper-lab' if args.lab else 'build-character-diagnostic')
    summary=json.loads((WS/('inventory/client-helper-lab-build.json' if args.lab else 'inventory/client-character-diagnostic.json')).read_text(encoding='utf-8'))
    proof=json.loads((WS/'inventory/client455-mesh-bindings.json').read_text(encoding='utf-8'))
    if summary['build_exit'] or summary['build_settings'].get('RF_CLIENT_455_MESH_BINDINGS')!='ON':raise ValueError('Successful455binding-enabled client required')
    library=WS/proof['library'];configured=Path(summary['build_settings']['RF_CLIENT_455_MESH_BINDINGS_LIBRARY'])
    if sha(library)!=proof['library_sha256'] or sha(configured)!=proof['library_sha256']:raise ValueError('Different455binding library selected')
    for name,digest in proof['source_sha256'].items():
        if sha(WS/'scripts/native'/name)!=digest:raise ValueError('Source binding proof stale')
    if sha(WS/'inventory/character-mesh08-bone-pairs.json')!=proof['pair_report_sha256'] or sha(WS/'inventory/client455-mesh-bindings-reference.json')!=proof['reference_report_sha256']:raise ValueError('455binding inputs changed')
    obj=library.parent/'mesh-bindings.obj'
    if sha(obj)!=proof['object_sha256'] or '/DEFAULTLIB:"LIBCMT"' not in directives(obj.read_bytes()):raise ValueError('Source binding object/CRT changed')
    mapping=(build/'RF_Online-Release.map').read_text(encoding='ascii',errors='replace')
    symbols={m[1]:(int(m[2],16),line) for line in mapping.splitlines() if (m:=re.match(r'\s+[0-9a-fA-F]{4}:[0-9a-fA-F]{8}\s+(\S+)\s+([0-9a-fA-F]{8})\s',line))}
    functions=[]
    for name in SYMBOLS:
        if name not in symbols:
            if args.lab:raise ValueError('Actual455binding lab API missing')
            continue
        va,line=symbols[name]
        if 'RFClient455MeshBindings:mesh-bindings.obj' not in line:raise ValueError('455binding API not selected fromsource')
        functions.append({'symbol':name,'va':hex(va),'rva':hex(va-0x400000)})
    if args.lab:
        info=json.loads((WS/'inventory/msvc-verification.json').read_text(encoding='utf-8'));dumpbin=Path(info['compiler_path'].splitlines()[0]).with_name('dumpbin.exe')
        table=subprocess.check_output([str(dumpbin),'/symbols',str(build/'RF_Online.dir/Release/client_helper_lab.obj')]).decode('utf-8',errors='replace')
        for name in SYMBOLS:
            if not any('UNDEF' in line and re.search(r'\|\s*'+re.escape(name)+r'\s*$',line) for line in table.splitlines()):raise ValueError('455binding actual lab caller missing')
    path=WS/'inventory/client455-mesh-bindings-link.json';report=json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}
    report[mode]={'exe':(build/'Release/RF_Online.bin').relative_to(WS).as_posix(),'exe_sha256':sha(build/'Release/RF_Online.bin'),'architecture':'x86','image_base':'0x400000','functions':functions,'library_sha256':sha(library),'component_report_sha256':sha(WS/'inventory/client455-mesh-bindings.json'),'scope':'Source455packed CPU binding kernels available;normal full model-loader not restored;unused normal APIs may be stripped. Own lab invokes all4APIs.'}
    path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(f'PASS:{mode}455mesh binding source/MT,{len(functions)}linked APIs;normal full model-loader remains open.')
if __name__=='__main__':main()
