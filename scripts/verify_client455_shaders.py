"""Verify source shader archive and actual full-client direct callsites."""
import argparse,json,re
from pathlib import Path
from compare_client_binaries import WS,pe
from probe_client455_shaders import inputs,sha
from verify_client455_animation_timing import calls
from verify_client_coff import directives
APIS=['_RF455_'+name for name in ['ConstructShaderManager','ReleaseShaderManager','ReadShaderSources','CreateShaderProgram','LoadShaderProgram','InitializeCharacterShaders','ReleaseCharacterDeclarations']]
def main():
    cli=argparse.ArgumentParser();cli.add_argument('--lab',action='store_true');args=cli.parse_args();mode='lab' if args.lab else 'normal';ref,proof,dll=inputs();root=WS/'work/client-build'/('build-helper-lab' if args.lab else 'build-character-diagnostic');summary=json.loads((WS/('inventory/client-helper-lab-build.json' if args.lab else 'inventory/client-character-diagnostic.json')).read_text(encoding='utf-8'));gpu=json.loads((WS/'inventory/client455-shaders-gpu.json').read_text(encoding='utf-8'))
    if summary['build_exit'] or summary['build_settings'].get('RF_CLIENT_455_SHADERS')!='ON' or gpu['build_report_sha256']!=sha(WS/'inventory/client455-shaders-build.json'):raise ValueError('Shader build/proof stale')
    if sha(Path(summary['build_settings']['RF_CLIENT_455_SHADERS_LIBRARY']))!=proof['library_sha256'] or sha(WS/proof['object'])!=proof['object_sha256'] or '/DEFAULTLIB:"LIBCMT"' not in directives((WS/proof['object']).read_bytes()):raise ValueError('Shader source archive/object/MT mismatch')
    mapping=(root/'RF_Online-Release.map').read_text(encoding='ascii',errors='replace');selected=[]
    for symbol in APIS:
        lines=[line for line in mapping.splitlines() if re.search(r'\s'+re.escape(symbol)+r'\s',line)]
        if not lines:
            if args.lab:raise ValueError('Missing shader API:'+symbol)
            continue
        if len(lines)!=1 or 'RFClient455Shaders:shaders.obj' not in lines[0]:raise ValueError('Wrong shader provider')
        address=re.search(re.escape(symbol)+r'\s+([0-9a-fA-F]{8})',lines[0]);selected.append({'symbol':symbol,'rva':hex(int(address[1],16)-0x400000),'provider':'RFClient455Shaders:shaders.obj'})
    actual=[]
    if args.lab:
        actual=calls((root/'RF_Online.dir/Release/test_client455_shaders.obj').read_bytes(),APIS,include_static=True)
        if set(c['target'] for c in actual)!=set(APIS):raise ValueError('Actual shader caller missing')
    exe=root/'Release/RF_Online.bin';path=WS/'inventory/client455-shaders-link.json';report=json.loads(path.read_text(encoding='utf-8')) if path.exists() else {};report[mode]={'architecture':'x86','image_base':'0x400000','exe_sha256':sha(exe),'exe_bytes':exe.stat().st_size,'entry_rva':hex(pe(exe.read_bytes())['entry_rva']),'functions':selected,'actual_callsites':actual,'library_sha256':proof['library_sha256'],'scope':'Source shader bootstrap;normal D3D8 renderer stillseparate,notfull455Character integration'};path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(f'PASS:{mode} source shader bootstrap/{len(selected)}APIs linked')
if __name__=='__main__':main()
