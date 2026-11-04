"""Verify source model lifetime andMESH08route selected in client project."""
import argparse,hashlib,json,re,subprocess
from pathlib import Path
from compare_client_binaries import WS,pe
from verify_client_coff import directives
SYMBOLS=['_RF455_'+s for s in ['DestroyMeshStorage','AllocateMeshArray','DeleteMeshStorage','ReleaseModelMeshArray','LoadMesh08Model']]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    cli=argparse.ArgumentParser();cli.add_argument('--lab',action='store_true');args=cli.parse_args();mode='lab' if args.lab else 'normal';build=WS/'work/client-build'/('build-helper-lab' if args.lab else 'build-character-diagnostic')
    summary=json.loads((WS/('inventory/client-helper-lab-build.json' if args.lab else 'inventory/client-character-diagnostic.json')).read_text(encoding='utf-8'));proof=json.loads((WS/'inventory/client455-models-build.json').read_text(encoding='utf-8'));gpu=json.loads((WS/'inventory/client455-models-gpu.json').read_text(encoding='utf-8'))
    if summary['build_exit'] or summary['build_settings'].get('RF_CLIENT_455_MODELS')!='ON':raise ValueError('Source models enabled client required')
    lib=WS/proof['library']
    if sha(lib)!=proof['library_sha256'] or sha(Path(summary['build_settings']['RF_CLIENT_455_MODELS_LIBRARY']))!=sha(lib) or gpu['build_report_sha256']!=sha(WS/'inventory/client455-models-build.json'):raise ValueError('Model source/native proof stale')
    for name,digest in proof['source_sha256'].items():
        if sha(WS/'scripts/native'/name)!=digest:raise ValueError('Model source changed')
    for item in proof['objects']:
        obj=WS/item['file']
        if sha(obj)!=item['sha256'] or '/DEFAULTLIB:"LIBCMT"' not in directives(obj.read_bytes()):raise ValueError('Model object/MT mismatch')
    mapping=(build/'RF_Online-Release.map').read_text(encoding='ascii',errors='replace');symbols={m[1]:(int(m[2],16),line) for line in mapping.splitlines() if (m:=re.match(r'\s+[0-9a-fA-F]{4}:[0-9a-fA-F]{8}\s+(\S+)\s+([0-9a-fA-F]{8})\s',line))};selected=[]
    for name in SYMBOLS:
        if name not in symbols:
            if args.lab:raise ValueError('Source model API missing:'+name)
            continue
        va,line=symbols[name]
        if 'RFClient455Models:' not in line:raise ValueError('Model API not fromsource archive')
        selected.append({'symbol':name,'rva':hex(va-0x400000)})
    providers=[name for name in symbols if name.startswith('?RF455_CrtMeshMemoryOps@@')]
    if args.lab and (len(providers)!=1 or 'RFClient455Models:lifecycle.obj' not in symbols[providers[0]][1]):raise ValueError('Actual CRT allocator provider missing')
    if args.lab:
        info=json.loads((WS/'inventory/msvc-verification.json').read_text(encoding='utf-8'));dump=Path(info['compiler_path'].splitlines()[0]).with_name('dumpbin.exe');table=subprocess.check_output([str(dump),'/symbols',str(build/'RF_Online.dir/Release/test_client455_models.obj')]).decode('utf-8',errors='replace')
        for name in SYMBOLS+providers:
            if not any('UNDEF' in line and re.search(r'\|\s*'+re.escape(name)+r'(?:\s+\(.*\))?\s*$',line) for line in table.splitlines()):raise ValueError('Actual model test caller missing:'+name)
    exe=build/'Release/RF_Online.bin';path=WS/'inventory/client455-models-link.json';report=json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}
    report[mode]={'exe_sha256':sha(exe),'entry_rva':hex(pe(exe.read_bytes())['entry_rva']),'architecture':'x86','image_base':'0x400000','functions':selected,'crt_provider_symbols':providers,'library_sha256':sha(lib),'scope':'Own model source pipeline/lifetime available;lab invokes full route;normal file dispatch/manager/renderer/animation not integrated'};path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(f'PASS:{mode}model lifecycle/MESH08source;{len(selected)}C APIs +{len(providers)}CRT provider linked')
if __name__=='__main__':main()
