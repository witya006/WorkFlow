"""Prove the fullclient lab calls the owned Character455 module,not legacy APIs."""
import argparse,hashlib,json,re,subprocess
from pathlib import Path
from compare_client_binaries import WS,pe
from verify_client_coff import directives

SYMBOLS=['_RF455_'+name for name in ['ConstructCharacter','ConstructCharacterManager','CreateCharacter','AddCharacter','FindCharacterName','FindCharacterId','CharacterId','DeleteCharacterName','DeleteCharacterId','ClearCharacters','DestroyCharacterManager','RefreshModelTextures','ReadMshFile']]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    cli=argparse.ArgumentParser();cli.add_argument('--lab',action='store_true');args=cli.parse_args();mode='lab' if args.lab else 'normal';build=WS/'work/client-build'/('build-helper-lab' if args.lab else 'build-character-diagnostic')
    summary=json.loads((WS/('inventory/client-helper-lab-build.json' if args.lab else 'inventory/client-character-diagnostic.json')).read_text(encoding='utf-8'));proof=json.loads((WS/'inventory/client455-character-manager-build.json').read_text(encoding='utf-8'));gpu=json.loads((WS/'inventory/client455-character-manager-gpu.json').read_text(encoding='utf-8'))
    if summary['build_exit'] or summary['build_settings'].get('RF_CLIENT_455_CHARACTER_MANAGER')!='ON':raise ValueError('Character455-enabled source build required')
    lib=WS/proof['library']
    if sha(lib)!=proof['library_sha256'] or sha(Path(summary['build_settings']['RF_CLIENT_455_CHARACTER_MANAGER_LIBRARY']))!=sha(lib) or gpu['build_report_sha256']!=sha(WS/'inventory/client455-character-manager-build.json'):raise ValueError('Character module/native proof stale')
    for name,digest in proof['source_sha256'].items():
        if sha(WS/'scripts/native'/name)!=digest:raise ValueError('Source changed:'+name)
    for record in proof['dependencies']:
        if sha(WS/record['file'])!=record['sha256']:raise ValueError('Dependency changed')
    for record in proof['objects']:
        obj=WS/record['file']
        if sha(obj)!=record['sha256'] or '/DEFAULTLIB:"LIBCMT"' not in directives(obj.read_bytes()):raise ValueError('Character object/MT mismatch')
    mapping=(build/'RF_Online-Release.map').read_text(encoding='ascii',errors='replace');symbols={m[1]:(int(m[2],16),line) for line in mapping.splitlines() if (m:=re.match(r'\s+[0-9a-fA-F]{4}:[0-9a-fA-F]{8}\s+(\S+)\s+([0-9a-fA-F]{8})\s',line))};selected=[]
    for name in SYMBOLS:
        if name not in symbols:
            if args.lab:raise ValueError('Character455 API missing:'+name)
            continue
        va,line=symbols[name]
        if 'RFClient455CharacterManager:manager.obj' not in line:raise ValueError('Character455 API not owned source:'+name)
        selected.append({'symbol':name,'rva':hex(va-0x400000)})
    if args.lab:
        info=json.loads((WS/'inventory/msvc-verification.json').read_text(encoding='utf-8'));dump=Path(info['compiler_path'].splitlines()[0]).with_name('dumpbin.exe');table=subprocess.check_output([str(dump),'/symbols',str(build/'RF_Online.dir/Release/test_client455_character_manager.obj')]).decode('utf-8',errors='replace')
        for name in SYMBOLS:
            if not any('UNDEF' in line and re.search(r'\|\s*'+re.escape(name)+r'(?:\s+\(.*\))?\s*$',line) for line in table.splitlines()):raise ValueError('Actual module test caller missing:'+name)
    exe=build/'Release/RF_Online.bin';path=WS/'inventory/client455-character-manager-link.json';report=json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}
    report[mode]={'architecture':'x86','image_base':'0x400000','exe_sha256':sha(exe),'exe_bytes':exe.stat().st_size,'entry_rva':hex(pe(exe.read_bytes())['entry_rva']),'functions':selected,'library_sha256':sha(lib),'scope':'Owned source record/manager/cache/raw-MSH APIs;lab connected to source MESH08 route;normal Character callers/renderer/animation remain legacy'}
    path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(f'PASS:{mode}Character455 source module;{len(selected)} C APIs linked')
if __name__=='__main__':main()
