"""Verify selected chat input source and actual compiled clock-parser consumers."""
import argparse,hashlib,json,re,subprocess
from pathlib import Path
from compare_client_binaries import WS
from build_client455_clock import sha
from verify_client_coff import directives

def main():
    cli=argparse.ArgumentParser();cli.add_argument('--lab',action='store_true');args=cli.parse_args()
    mode='lab' if args.lab else 'normal';folder='build-helper-lab' if args.lab else 'build-character-diagnostic';build=WS/'work/client-build'/folder
    summary=json.loads((WS/('inventory/client-helper-lab-build.json' if args.lab else 'inventory/client-character-diagnostic.json')).read_text(encoding='utf-8'))
    if summary['build_exit'] or summary['build_settings'].get('RF_CLIENT_455_TIME_COMMANDS')!='ON':raise ValueError('Successful time-command-enabled client required')
    proof=json.loads((WS/'inventory/client455-time-commands.json').read_text(encoding='utf-8'))
    for name,digest in proof['source_sha256'].items():
        if sha(WS/'scripts/native'/name)!=digest:raise ValueError('Command source proof stale')
    patch=[p for p in json.loads((WS/'inventory/client-behavior-patches.json').read_text(encoding='utf-8')) if p['build_option']=='RF_CLIENT_455_TIME_COMMANDS']
    if len(patch)!=1 or sha(WS/patch[0]['file'])!=patch[0]['patched_sha256']:raise ValueError('Chat source selection stale')
    info=json.loads((WS/'inventory/msvc-verification.json').read_text(encoding='utf-8'));dumpbin=Path(info['compiler_path'].splitlines()[0]).with_name('dumpbin.exe');objects=[]
    module=list((build/'R3EngineClientMT.dir/Release').glob('client455_time_commands*.obj'))
    if len(module)!=1:raise ValueError('Missing/ambiguous command module object')
    for obj,required in [(build/'RF_Online.dir/Release/cavatar_relationinfo2.obj',['_RF455_TryClockCommand']),(module[0],['_RF455_SetDayTime','_RF455_SetRealDayTime'])]:
        raw=obj.read_bytes()
        if '/DEFAULTLIB:"LIBCMT"' not in directives(raw):raise ValueError('Command consumer is not x86 /MT')
        table=subprocess.check_output([str(dumpbin),'/symbols',str(obj)]).decode('utf-8',errors='replace')
        for name in required:
            if not any('UNDEF' in line and re.search(r'\|\s*'+re.escape(name)+r'\s*$',line) for line in table.splitlines()):raise ValueError('Actual command consumer missing:'+name)
        objects.append({'object':obj.relative_to(WS).as_posix(),'sha256':sha(obj),'undefined_references':required})
    mapping=(build/'RF_Online-Release.map').read_text(encoding='ascii',errors='replace');symbol='_RF455_TryClockCommand'
    rows=[m for line in mapping.splitlines() if (m:=re.match(r'\s+[0-9a-fA-F]{4}:[0-9a-fA-F]{8}\s+(\S+)\s+([0-9a-fA-F]{8})\s',line)) and m[1]==symbol]
    if len(rows)!=1:raise ValueError('Linked command symbol missing/ambiguous')
    va=int(rows[0][2],16);clock=json.loads((WS/'inventory/client455-clock-link.json').read_text(encoding='utf-8'))[mode]
    if clock['exe_sha256']!=sha(build/'Release/RF_Online.bin'):raise ValueError('Current clock link proof missing')
    path=WS/'inventory/client455-time-commands-link.json';report=json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}
    report[mode]={'exe':(build/'Release/RF_Online.bin').relative_to(WS).as_posix(),'exe_sha256':sha(build/'Release/RF_Online.bin'),'architecture':'x86','image_base':'0x400000','parser_va':hex(va),'parser_rva':hex(va-0x400000),'objects':objects,'component_report_sha256':sha(WS/'inventory/client455-time-commands.json'),'source_patch_sha256':patch[0]['patched_sha256'],'reference_report_sha256':sha(WS/'inventory/client455-time-command-reference.json'),'scope':'Actual source/compiled input and clock consumers,not instruction identity of the C++text parser. Native component/input scenarios recorded separately;full chat/other directives remain open.'}
    path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(f'PASS:{mode} real chat input and command module select verified game/real HMS APIs;source ledger and linked parser recorded.')

if __name__=='__main__':main()
