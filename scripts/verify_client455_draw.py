"""Prove actual draw callers and source archive ownership,not full draw parity."""
import argparse,json,re
from pathlib import Path
from compare_client_binaries import WS,pe
from probe_client455_draw import sha
from verify_client455_animation_timing import calls
from verify_client_coff import directives
APIS=['_RF455_'+name for name in ['SetCharacterDrawState','SelectCharacterShader','SetCharacterMaterial','UploadCharacterPalette','SubmitSharedCharacterMesh']]
def main():
    cli=argparse.ArgumentParser();cli.add_argument('--lab',action='store_true');args=cli.parse_args();mode='lab' if args.lab else 'normal'
    build=json.loads((WS/'inventory/client455-draw-build.json').read_text(encoding='utf-8'));summary=json.loads((WS/('inventory/client-helper-lab-build.json' if args.lab else 'inventory/client-character-diagnostic.json')).read_text(encoding='utf-8'));root=WS/'work/client-build'/('build-helper-lab' if args.lab else 'build-character-diagnostic')
    if summary['build_exit'] or summary['build_settings'].get('RF_CLIENT_455_DRAW')!='ON' or sha(Path(summary['build_settings']['RF_CLIENT_455_DRAW_LIBRARY']))!=build['library_sha256']:raise ValueError('Draw source archive mismatch')
    for name,digest in build['source_sha256'].items():
        if sha(WS/'scripts/native'/name)!=digest:raise ValueError('Changed source draw:'+name)
    obj=WS/build['object']
    if sha(obj)!=build['object_sha256'] or '/DEFAULTLIB:"LIBCMT"' not in directives(obj.read_bytes()):raise ValueError('Draw object/MT mismatch')
    mapping=(root/'RF_Online-Release.map').read_text(encoding='ascii',errors='replace');functions=[]
    for symbol in APIS:
        lines=[line for line in mapping.splitlines() if re.search(r'\s'+re.escape(symbol)+r'\s',line)]
        if not lines:
            if args.lab:raise ValueError('Missing draw API:'+symbol)
            continue
        if len(lines)!=1 or 'RFClient455Draw:draw.obj' not in lines[0]:raise ValueError('Wrong draw provider')
        address=re.search(re.escape(symbol)+r'\s+([0-9a-fA-F]{8})',lines[0]);functions.append({'symbol':symbol,'rva':hex(int(address[1],16)-0x400000),'provider':'RFClient455Draw:draw.obj'})
    actual=[]
    if args.lab:
        actual=calls((root/'RF_Online.dir/Release/test_client455_draw.obj').read_bytes(),APIS,include_static=True)
        if set(c['target'] for c in actual)!=set(APIS):raise ValueError('Actual source draw callers missing')
    exe=root/'Release/RF_Online.bin';path=WS/'inventory/client455-draw-link.json';report=json.loads(path.read_text(encoding='utf-8')) if path.exists() else {};report[mode]={'architecture':'x86','image_base':'0x400000','exe_sha256':sha(exe),'exe_bytes':exe.stat().st_size,'entry_rva':hex(pe(exe.read_bytes())['entry_rva']),'functions':functions,'actual_callsites':actual,'library_sha256':build['library_sha256'],'scope':'Actual source state/material/palette/shared draw;normal D3D8/full draw routing still open'};path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(f'PASS:{mode} source draw primitives/{len(functions)}APIs linked')
if __name__=='__main__':main()
