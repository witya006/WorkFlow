"""Verify the actual commonutil callers and source provider in the final PE."""
import argparse,hashlib,json,re
from compare_client_binaries import WS,pe
from verify_client455_animation_timing import calls
from verify_client_coff import directives
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    cli=argparse.ArgumentParser();cli.add_argument('--lab',action='store_true');args=cli.parse_args();mode='lab' if args.lab else 'normal';root=WS/'work/client-build'/('build-helper-lab' if args.lab else 'build-character-diagnostic');build=json.loads((WS/('inventory/client-helper-lab-build.json' if args.lab else 'inventory/client-character-diagnostic.json')).read_text(encoding='utf-8'));proof=json.loads((WS/'inventory/client455-loop-clock-build.json').read_text(encoding='utf-8'));cpu=json.loads((WS/'inventory/client455-loop-clock-cpu.json').read_text(encoding='utf-8'))
    if build['build_exit'] or build['build_settings'].get('RF_CLIENT_455_LOOP_CLOCK')!='ON' or cpu['build_report_sha256']!=sha(WS/'inventory/client455-loop-clock-build.json'):raise ValueError('Loop source proof/build stale')
    for name,digest in proof['source_sha256'].items():
        if sha(WS/'scripts/native'/name)!=digest:raise ValueError('Changed loop source')
    ledger=json.loads((WS/'inventory/client-behavior-patches.json').read_text(encoding='utf-8'));patch=next(p for p in ledger if p['build_option']=='RF_CLIENT_455_LOOP_CLOCK')
    if sha(WS/patch['file'])!=patch['patched_sha256'] or patch['reference_report_sha256']!=sha(WS/'inventory/client455-loop-clock-reference.json'):raise ValueError('Changed loop overlay')
    obj=root/'R3EngineClientMT.dir/Release/commonutil.obj';module=root/'R3EngineClientMT.dir/Release/client455_loop_clock.obj'
    for p in [obj,module]:
        if '/DEFAULTLIB:"LIBCMT"' not in directives(p.read_bytes()):raise ValueError('Loop x86/MT required')
    selected=calls(obj.read_bytes(),['_RF455_UpdateLoopClock','_RF455_GetLoopDuration'])
    if len(selected)!=2 or not any(c['caller']=='?R3CalculateTime@@YAXXZ' and c['target']=='_RF455_UpdateLoopClock' for c in selected) or not any(c['caller']=='?GetDuration@@YAMXZ' and c['target']=='_RF455_GetLoopDuration' for c in selected):raise ValueError('Actual loop callers missing:'+str(selected))
    mapping=(root/'RF_Online-Release.map').read_text(encoding='ascii',errors='replace');functions=[]
    for symbol in ['_RF455_UpdateLoopClock','_RF455_GetLoopDuration','_RF455_GetLoopTicks']:
        lines=[line for line in mapping.splitlines() if re.search(r'\s'+re.escape(symbol)+r'\s',line)]
        if not lines:
            if symbol=='_RF455_UpdateLoopClock':raise ValueError('Update not linked')
            continue
        if len(lines)!=1 or 'R3EngineMT:client455_loop_clock.obj' not in lines[0]:raise ValueError('Wrong loop provider')
        address=re.search(re.escape(symbol)+r'\s+([0-9a-fA-F]{8})',lines[0]);functions.append({'symbol':symbol,'rva':hex(int(address[1],16)-0x400000),'provider':'R3EngineMT:client455_loop_clock.obj'})
    exe=root/'Release/RF_Online.bin';path=WS/'inventory/client455-loop-clock-link.json';report=json.loads(path.read_text(encoding='utf-8')) if path.exists() else {};report[mode]={'architecture':'x86','image_base':'0x400000','exe_sha256':sha(exe),'exe_bytes':exe.stat().st_size,'entry_rva':hex(pe(exe.read_bytes())['entry_rva']),'functions':functions,'actual_callsites':selected,'commonutil_object_sha256':sha(obj),'module_sha256':sha(module),'scope':'Normal elapsed-clock source selected;normalWinMain/fullCharacter/renderer acceptance remainsopen'};path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(f'PASS:{mode} actual R3CalculateTime/GetDuration calls selectsource loopclock')
if __name__=='__main__':main()
