"""Verify source455mesh CPU kernels in the full project;normal loader still open."""
import argparse,hashlib,json,re,subprocess
from pathlib import Path
from compare_client_binaries import WS
from verify_client_coff import directives

SYMBOLS=['_RF455_ConstructMeshStorage','_RF455_ApplyMesh08Header','_RF455_LoadMesh08Materials']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    cli=argparse.ArgumentParser();cli.add_argument('--lab',action='store_true');args=cli.parse_args();mode='lab' if args.lab else 'normal'
    build=WS/'work/client-build'/('build-helper-lab' if args.lab else 'build-character-diagnostic')
    summary=json.loads((WS/('inventory/client-helper-lab-build.json' if args.lab else 'inventory/client-character-diagnostic.json')).read_text(encoding='utf-8'))
    proof=json.loads((WS/'inventory/client455-mesh-runtime.json').read_text(encoding='utf-8'))
    if summary['build_exit'] or summary['build_settings'].get('RF_CLIENT_455_MESH_RUNTIME')!='ON':raise ValueError('Successful455mesh runtime-enabled client required')
    library=WS/proof['library'];configured=Path(summary['build_settings']['RF_CLIENT_455_MESH_RUNTIME_LIBRARY'])
    if sha(library)!=proof['library_sha256'] or sha(configured)!=proof['library_sha256']:raise ValueError('Different455mesh runtime library selected')
    for name,digest in proof['source_sha256'].items():
        if sha(WS/'scripts/native'/name)!=digest:raise ValueError('Mesh runtime source proof stale')
    if sha(WS/'inventory/character-mesh08-headers.json')!=proof['header_report_sha256'] or sha(WS/'inventory/client455-mesh-runtime-reference.json')!=proof['reference_report_sha256'] or sha(Path(proof['matrix_provider']['path']))!=proof['matrix_provider']['sha256']:raise ValueError('Mesh runtime inputs/provider changed')
    obj=library.parent/'mesh-runtime.obj'
    if sha(obj)!=proof['object_sha256'] or '/DEFAULTLIB:"LIBCMT"' not in directives(obj.read_bytes()):raise ValueError('Mesh runtime object/CRT changed')
    mapping=(build/'RF_Online-Release.map').read_text(encoding='ascii',errors='replace')
    symbols={m[1]:(int(m[2],16),line) for line in mapping.splitlines() if (m:=re.match(r'\s+[0-9a-fA-F]{4}:[0-9a-fA-F]{8}\s+(\S+)\s+([0-9a-fA-F]{8})\s',line))}
    functions=[]
    for name in SYMBOLS:
        if name not in symbols:
            if args.lab:raise ValueError('Actual mesh runtime lab API missing')
            continue
        va,line=symbols[name]
        if 'RFClient455MeshRuntime:mesh-runtime.obj' not in line:raise ValueError('Mesh runtime API not selected fromsource')
        functions.append({'symbol':name,'va':hex(va),'rva':hex(va-0x400000)})
    if args.lab:
        info=json.loads((WS/'inventory/msvc-verification.json').read_text(encoding='utf-8'));dumpbin=Path(info['compiler_path'].splitlines()[0]).with_name('dumpbin.exe')
        table=subprocess.check_output([str(dumpbin),'/symbols',str(build/'RF_Online.dir/Release/client_helper_lab.obj')]).decode('utf-8',errors='replace')
        for name in SYMBOLS:
            if not any('UNDEF' in line and re.search(r'\|\s*'+re.escape(name)+r'\s*$',line) for line in table.splitlines()):raise ValueError('Actual mesh runtime lab caller missing')
    path=WS/'inventory/client455-mesh-runtime-link.json';report=json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}
    report[mode]={'exe':(build/'Release/RF_Online.bin').relative_to(WS).as_posix(),'exe_sha256':sha(build/'Release/RF_Online.bin'),'architecture':'x86','image_base':'0x400000','functions':functions,'library_sha256':sha(library),'component_report_sha256':sha(WS/'inventory/client455-mesh-runtime.json'),'scope':'Source455mesh construction/header/material request dependency available;own lab invokes3APIs. Normal full model-loader/texture backend/GPU not integrated;unused normal APIs may be stripped.'}
    path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(f'PASS:{mode}455mesh runtime source/MT,{len(functions)}linked APIs;normal full model-loader remains open.')
if __name__=='__main__':main()
