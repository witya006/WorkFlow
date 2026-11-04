"""Check own source/MT shared buffer APIs in fullclient lab/normal link maps."""
import argparse,hashlib,json,re,subprocess
from pathlib import Path
from compare_client_binaries import WS,pe
from verify_client_coff import directives
SYMBOLS=['_RF455_'+name for name in ['ConstructVertexPool','ConstructIndexPool','DestroyVertexPool','DestroyIndexPool','UploadVertices36','UploadVertices64','UploadIndices','BindVertices36','BindVertices64','BindIndices','RebaseMesh08Indices','UploadMesh08Gpu']]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    cli=argparse.ArgumentParser();cli.add_argument('--lab',action='store_true');args=cli.parse_args();mode='lab' if args.lab else 'normal';build=WS/'work/client-build'/('build-helper-lab' if args.lab else 'build-character-diagnostic')
    summary=json.loads((WS/('inventory/client-helper-lab-build.json' if args.lab else 'inventory/client-character-diagnostic.json')).read_text(encoding='utf-8'));proof=json.loads((WS/'inventory/client455-shared-buffers-build.json').read_text(encoding='utf-8'));gpu=json.loads((WS/'inventory/client455-shared-buffers-gpu.json').read_text(encoding='utf-8'))
    if summary['build_exit'] or summary['build_settings'].get('RF_CLIENT_455_SHARED_BUFFERS')!='ON':raise ValueError('Successful shared buffer enabled client required')
    lib=WS/proof['library'];obj=WS/proof['object']
    if sha(lib)!=proof['library_sha256'] or sha(Path(summary['build_settings']['RF_CLIENT_455_SHARED_BUFFERS_LIBRARY']))!=sha(lib) or sha(obj)!=proof['object_sha256'] or '/DEFAULTLIB:"LIBCMT"' not in directives(obj.read_bytes()):raise ValueError('Shared buffer source archive/object stale')
    if gpu['build_report_sha256']!=sha(WS/'inventory/client455-shared-buffers-build.json'):raise ValueError('Shared buffer native proof stale')
    for name,digest in proof['source_sha256'].items():
        if sha(WS/'scripts/native'/name)!=digest:raise ValueError('Shared buffer source changed')
    mapping=(build/'RF_Online-Release.map').read_text(encoding='ascii',errors='replace');symbols={m[1]:(int(m[2],16),line) for line in mapping.splitlines() if (m:=re.match(r'\s+[0-9a-fA-F]{4}:[0-9a-fA-F]{8}\s+(\S+)\s+([0-9a-fA-F]{8})\s',line))};selected=[]
    for name in SYMBOLS:
        if name not in symbols:
            if args.lab:raise ValueError('Actual shared buffer API missing:'+name)
            continue
        va,line=symbols[name]
        if 'RFClient455SharedBuffers:shared-buffers.obj' not in line:raise ValueError('Shared buffer API not source selected')
        selected.append({'symbol':name,'rva':hex(va-0x400000)})
    if args.lab:
        info=json.loads((WS/'inventory/msvc-verification.json').read_text(encoding='utf-8'));dump=Path(info['compiler_path'].splitlines()[0]).with_name('dumpbin.exe');table=subprocess.check_output([str(dump),'/symbols',str(build/'RF_Online.dir/Release/test_client455_shared_buffers.obj')]).decode('utf-8',errors='replace')
        for name in SYMBOLS:
            if not any('UNDEF' in line and re.search(r'\|\s*'+re.escape(name)+r'\s*$',line) for line in table.splitlines()):raise ValueError('Actual test TU does not call source API:'+name)
    exe=build/'Release/RF_Online.bin';path=WS/'inventory/client455-shared-buffers-link.json';report=json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}
    report[mode]={'exe_sha256':sha(exe),'entry_rva':hex(pe(exe.read_bytes())['entry_rva']),'architecture':'x86','image_base':'0x400000','functions':selected,'library_sha256':sha(lib),'scope':'Own source dependency andlab calls;normal full model dispatch/animation/renderer integration remains open'};path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(f'PASS:{mode}source shared buffers/MT;{len(selected)}APIs linked')
if __name__=='__main__':main()
