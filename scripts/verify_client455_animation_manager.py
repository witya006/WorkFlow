"""Verify the source collection provider and actual full-client test callers."""
import argparse,json,re
from pathlib import Path
from compare_client_binaries import WS,pe
from probe_client455_animation_manager import inputs,sha
from verify_client455_animation_timing import calls
from verify_client_coff import directives
APIS=['_RF455_'+name for name in ['ConstructAnimationManager','ResetAnimationCounters','RegisterAnimation','GetOrRegisterAnimation','FindAnimationName','FindAnimationSuffix','FindAnimationId','FindAnimationIdByName','DeleteAnimationName','DeleteAnimationId','ReleaseAnimationManager']]
def main():
    cli=argparse.ArgumentParser();cli.add_argument('--lab',action='store_true');args=cli.parse_args();mode='lab' if args.lab else 'normal';ref,proof=inputs();root=WS/'work/client-build'/('build-helper-lab' if args.lab else 'build-character-diagnostic');summary=json.loads((WS/('inventory/client-helper-lab-build.json' if args.lab else 'inventory/client-character-diagnostic.json')).read_text(encoding='utf-8'));cpu=json.loads((WS/'inventory/client455-animation-manager-cpu.json').read_text(encoding='utf-8'))
    if summary['build_exit'] or summary['build_settings'].get('RF_CLIENT_455_ANIMATION_MANAGER')!='ON' or cpu['build_report_sha256']!=sha(WS/'inventory/client455-animation-manager-build.json'):raise ValueError('Manager build/proof stale')
    if sha(Path(summary['build_settings']['RF_CLIENT_455_ANIMATION_MANAGER_LIBRARY']))!=proof['library_sha256'] or sha(WS/proof['object'])!=proof['object_sha256'] or '/DEFAULTLIB:"LIBCMT"' not in directives((WS/proof['object']).read_bytes()):raise ValueError('Manager source archive/object/MT mismatch')
    mapping=(root/'RF_Online-Release.map').read_text(encoding='ascii',errors='replace');selected=[]
    for symbol in APIS:
        lines=[line for line in mapping.splitlines() if re.search(r'\s'+re.escape(symbol)+r'\s',line)]
        if not lines:
            if args.lab:raise ValueError('Missing manager source API:'+symbol)
            continue
        if len(lines)!=1 or 'RFClient455AnimationManager:animation_manager.obj' not in lines[0]:raise ValueError('Wrong manager source provider')
        address=re.search(re.escape(symbol)+r'\s+([0-9a-fA-F]{8})',lines[0]);selected.append({'symbol':symbol,'rva':hex(int(address[1],16)-0x400000),'provider':'RFClient455AnimationManager:animation_manager.obj'})
    actual=[]
    if args.lab:
        obj=root/'RF_Online.dir/Release/test_client455_animation_manager.obj';actual=calls(obj.read_bytes(),APIS,include_static=True)
        if set(c['target'] for c in actual)!=set(APIS):raise ValueError('Manager actual test callers missing')
    exe=root/'Release/RF_Online.bin';path=WS/'inventory/client455-animation-manager-link.json';report=json.loads(path.read_text(encoding='utf-8')) if path.exists() else {};report[mode]={'architecture':'x86','image_base':'0x400000','exe_sha256':sha(exe),'exe_bytes':exe.stat().st_size,'entry_rva':hex(pe(exe.read_bytes())['entry_rva']),'functions':selected,'actual_callsites':actual,'library_sha256':proof['library_sha256'],'scope':'Source collection available;normal CUnity/ChAnimation consumers remainlegacy,no unsafe ABI cast'};path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(f'PASS:{mode} source AnimationManager4028/{len(selected)}APIs linked')
if __name__=='__main__':main()
