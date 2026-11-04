"""Verify MESH08 dependency selection;normal runtime model-loader integration open."""
import argparse,hashlib,json,re,subprocess
from pathlib import Path
from compare_client_binaries import WS
from verify_client_coff import directives

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    cli=argparse.ArgumentParser();cli.add_argument('--lab',action='store_true');args=cli.parse_args();mode='lab' if args.lab else 'normal'
    build=WS/'work/client-build'/('build-helper-lab' if args.lab else 'build-character-diagnostic')
    summary=json.loads((WS/('inventory/client-helper-lab-build.json' if args.lab else 'inventory/client-character-diagnostic.json')).read_text(encoding='utf-8'))
    proof=json.loads((WS/'inventory/client455-mesh08.json').read_text(encoding='utf-8'))
    if summary['build_exit'] or summary['build_settings'].get('RF_CLIENT_455_MESH08')!='ON':raise ValueError('Successful MESH08format-enabled client required')
    library=WS/proof['library']
    if sha(library)!=proof['library_sha256']:raise ValueError('MESH08source library changed')
    configured=Path(summary['build_settings']['RF_CLIENT_455_MESH08_LIBRARY'])
    if sha(configured)!=proof['library_sha256']:raise ValueError('Build selects a different MESH08library')
    for name,digest in proof['source_sha256'].items():
        if sha(WS/'scripts/native'/name)!=digest:raise ValueError('MESH08source proof stale')
    obj=library.parent/'mesh08.obj'
    if sha(obj)!=proof['object_sha256'] or '/DEFAULTLIB:"LIBCMT"' not in directives(obj.read_bytes()):raise ValueError('MESH08object/CRT changed')
    mapping=(build/'RF_Online-Release.map').read_text(encoding='ascii',errors='replace')
    symbols={m[1]:(int(m[2],16),line) for line in mapping.splitlines() if (m:=re.match(r'\s+[0-9a-fA-F]{4}:[0-9a-fA-F]{8}\s+(\S+)\s+([0-9a-fA-F]{8})\s',line))}
    selected=[]
    for name in ['_RF455_DecodeMesh08','_RF455_EncodeMesh08']:
        if name not in symbols:
            if args.lab:raise ValueError('MESH08lab API missing')
            continue # No normal runtime model-loader consumer has been restored yet.
        va,line=symbols[name]
        if 'RFClient455Mesh08:mesh08.obj' not in line:raise ValueError('MESH08API not selected fromsource')
        selected.append({'symbol':name,'va':hex(va),'rva':hex(va-0x400000)})
    if args.lab:
        info=json.loads((WS/'inventory/msvc-verification.json').read_text(encoding='utf-8'));dumpbin=Path(info['compiler_path'].splitlines()[0]).with_name('dumpbin.exe')
        table=subprocess.check_output([str(dumpbin),'/symbols',str(build/'RF_Online.dir/Release/client_helper_lab.obj')]).decode('utf-8',errors='replace')
        for name in ['_RF455_DecodeMesh08','_RF455_EncodeMesh08']:
            if not any('UNDEF' in row and re.search(r'\|\s*'+re.escape(name)+r'\s*$',row) for row in table.splitlines()):raise ValueError('Actual lab MESH08consumer missing')
    path=WS/'inventory/client455-mesh08-link.json';out=json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}
    out[mode]={'exe':(build/'Release/RF_Online.bin').relative_to(WS).as_posix(),'exe_sha256':sha(build/'Release/RF_Online.bin'),'architecture':'x86','image_base':'0x400000','functions':selected,'library_sha256':proof['library_sha256'],'component_report_sha256':sha(WS/'inventory/client455-mesh08.json'),'reference_report_sha256':sha(WS/'inventory/client455-mesh08-reference.json'),'normal_runtime_model_loader_integrated':False,'scope':'Source format dependency available;own lab consumer linked andchecked. Normal fullMESH08loader/material/bone/GPU path remains open;unused normal APIs may be stripped.'}
    path.write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
    print(f'PASS:{mode}MESH08 source dependency/MT;{len(selected)}linked format APIs. Normal runtime model-loader integration remains open.')

if __name__=='__main__':main()
