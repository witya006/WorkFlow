"""Verify source Character texture APIs linked into own lab;unused normal is allowed."""
import argparse,hashlib,json,re
from pathlib import Path
from compare_client_binaries import WS,pe
from verify_client_coff import directives

SYMBOLS=['_RF455_'+n for n in ['ConstructTextureManager','InitTextureManager','ClearTextureManager','DestroyTextureManager','LastTextureManager','GetTextureId','GetTextureByName','GetTextureById','AddTexture','DeleteTextureByName','DeleteTextureById','GetTextureAccounting']]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    cli=argparse.ArgumentParser();cli.add_argument('--lab',action='store_true');args=cli.parse_args();mode='lab' if args.lab else 'normal'
    build=WS/'work/client-build'/('build-helper-lab' if args.lab else 'build-character-diagnostic');summary=json.loads((WS/('inventory/client-helper-lab-build.json' if args.lab else 'inventory/client-character-diagnostic.json')).read_text(encoding='utf-8'));proof=json.loads((WS/'inventory/client455-texture-build.json').read_text(encoding='utf-8'));gpu=json.loads((WS/'inventory/client455-texture-gpu.json').read_text(encoding='utf-8'))
    if summary['build_exit'] or summary['build_settings'].get('RF_CLIENT_455_TEXTURE')!='ON':raise ValueError('Successful texture-enabled fullclient required')
    library=WS/proof['library']
    if sha(library)!=proof['library_sha256'] or sha(Path(summary['build_settings']['RF_CLIENT_455_TEXTURE_LIBRARY']))!=proof['library_sha256'] or gpu['build_report_sha256']!=sha(WS/'inventory/client455-texture-build.json'):raise ValueError('Texture archive/GPU proof stale')
    for name,digest in proof['source_sha256'].items():
        if sha(WS/'scripts/native'/name)!=digest:raise ValueError('Texture source proof stale')
    for record in proof['objects']:
        obj=WS/record['file']
        if sha(obj)!=record['sha256'] or obj.read_bytes()[:2]!=b'\x4c\x01' or '/DEFAULTLIB:"LIBCMT"' not in directives(obj.read_bytes()):raise ValueError('Texture object/MT changed')
    mapping=(build/'RF_Online-Release.map').read_text(encoding='ascii',errors='replace');symbols={m[1]:(int(m[2],16),line) for line in mapping.splitlines() if (m:=re.match(r'\s+[0-9a-fA-F]{4}:[0-9a-fA-F]{8}\s+(\S+)\s+([0-9a-fA-F]{8})\s',line))};functions=[]
    for name in SYMBOLS:
        if name not in symbols:
            if args.lab:raise ValueError('Source texture lab API missing:'+name)
            continue
        va,line=symbols[name]
        if 'RFClient455Texture:texture.obj' not in line:raise ValueError('Texture API not from verifiedsource')
        functions.append({'symbol':name,'rva':hex(va-0x400000)})
    if args.lab and '_RF455_RunCharacterTextureChecks' not in symbols:raise ValueError('Separate actual D3D9test TU not linked')
    exe=build/'Release/RF_Online.bin';path=WS/'inventory/client455-texture-link.json';report=json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}
    report[mode]={'exe_sha256':sha(exe),'entry_rva':hex(pe(exe.read_bytes())['entry_rva']),'architecture':'x86','image_base':'0x400000','functions':functions,'library_sha256':sha(library),'scope':'Source dependency available;own lab calls real backend;normal full model-loader not integrated,unused normal texture APIs stripped'};path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(f'PASS:{mode}source texture backend/MT;{len(functions)}C APIs linked;normal full model-loader still open')
if __name__=='__main__':main()
