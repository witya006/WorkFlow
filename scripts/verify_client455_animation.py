"""Verify ANI source archive provenance and actual full-client lab callers."""
import argparse,hashlib,json,re,subprocess
from pathlib import Path
from compare_client_binaries import WS,pe
from verify_client_coff import directives

APIS=['_RF455_'+s for s in ['ConstructAnimation','DestroyAnimation','DecodeAni','ReadAnimationFile','ImportCharacterResource','ReleaseImportedResource','FindAnimationMax','LoadAnimation','ApplyAniTrack','AttachAnimation','ValidateLegacyModel','LoadCharacter','MatchAnimation']]
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    cli=argparse.ArgumentParser();cli.add_argument('--lab',action='store_true');args=cli.parse_args();mode='lab' if args.lab else 'normal';build=WS/'work/client-build'/('build-helper-lab' if args.lab else 'build-character-diagnostic')
    summary=json.loads((WS/('inventory/client-helper-lab-build.json' if args.lab else 'inventory/client-character-diagnostic.json')).read_text(encoding='utf-8'));proof=json.loads((WS/'inventory/client455-animation-build.json').read_text(encoding='utf-8'));gpu=json.loads((WS/'inventory/client455-animation-gpu.json').read_text(encoding='utf-8'))
    if summary['build_exit'] or summary['build_settings'].get('RF_CLIENT_455_ANIMATION')!='ON':raise ValueError('Animation-enabled build required')
    lib=WS/proof['library'];obj=WS/proof['object']
    if sha(lib)!=proof['library_sha256'] or sha(Path(summary['build_settings']['RF_CLIENT_455_ANIMATION_LIBRARY']))!=sha(lib) or gpu['build_report_sha256']!=sha(WS/'inventory/client455-animation-build.json'):raise ValueError('Stale animation library/runtime proof')
    for name,digest in proof['source_sha256'].items():
        if sha(WS/'scripts/native'/name)!=digest:raise ValueError('Changed ANI source:'+name)
    for record in proof['dependencies']:
        if sha(WS/record['file'])!=record['sha256']:raise ValueError('Changed ANI dependency')
    if sha(obj)!=proof['object_sha256'] or '/DEFAULTLIB:"LIBCMT"' not in directives(obj.read_bytes()):raise ValueError('Wrong ANI source object/MT')
    mapping=(build/'RF_Online-Release.map').read_text(encoding='ascii',errors='replace');symbols={m[1]:(int(m[2],16),line) for line in mapping.splitlines() if (m:=re.match(r'\s+[0-9a-fA-F]{4}:[0-9a-fA-F]{8}\s+(\S+)\s+([0-9a-fA-F]{8})\s',line))};selected=[]
    for symbol in APIS:
        if symbol not in symbols:
            if args.lab:raise ValueError('Missing ANI API:'+symbol)
            continue
        va,line=symbols[symbol];provider='RFClient455Animation:animation.obj'
        if provider not in line:raise ValueError('ANI provider differs:'+symbol)
        selected.append({'symbol':symbol,'rva':hex(va-0x400000),'provider':provider})
    if args.lab:
        info=json.loads((WS/'inventory/msvc-verification.json').read_text(encoding='utf-8'));dump=Path(info['compiler_path'].splitlines()[0]).with_name('dumpbin.exe');table=subprocess.check_output([str(dump),'/symbols',str(build/'RF_Online.dir/Release/test_client455_animation.obj')]).decode('utf-8',errors='replace')
        for symbol in APIS:
            if not any('UNDEF' in line and re.search(r'\|\s*'+re.escape(symbol)+r'(?:\s+\(.*\))?\s*$',line) for line in table.splitlines()):raise ValueError('Actual ANI lab caller missing:'+symbol)
    exe=build/'Release/RF_Online.bin';path=WS/'inventory/client455-animation-link.json';report=json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}
    report[mode]={'architecture':'x86','image_base':'0x400000','exe_sha256':sha(exe),'exe_bytes':exe.stat().st_size,'entry_rva':hex(pe(exe.read_bytes())['entry_rva']),'functions':selected,'library_sha256':sha(lib),'scope':'Selected source ANI/character dispatch;normal consumers,pose math,async manager remain open'}
    path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(f'PASS:{mode} source ANI/dispatch;{len(selected)} C APIs linked')
if __name__=='__main__':main()
