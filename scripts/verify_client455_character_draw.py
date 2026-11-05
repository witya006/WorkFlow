"""Verify actual source draw route callers/providers in the full client."""
import argparse,json,re
from pathlib import Path
from compare_client_binaries import WS,pe
from probe_client455_character_draw import inputs,sha
from verify_client455_animation_timing import calls
APIS={'_RF455_'+name:owner for name,owner in [('ResetCharacterTransparency','core'),('QueueCharacterTransparency','core'),('SetCharacterEffectStage','core'),('DrawDynamicCharacterMesh','core'),('DrawCharacter455','route'),('FlushCharacterTransparency','route'),('FlushCharacterMeshBatch','route'),('DrawCharacterShadow','route')]}
def main():
    cli=argparse.ArgumentParser();cli.add_argument('--lab',action='store_true');args=cli.parse_args();mode='lab' if args.lab else 'normal';build,ref,dll=inputs();root=WS/'work/client-build'/('build-helper-lab' if args.lab else 'build-character-diagnostic');summary=json.loads((WS/('inventory/client-helper-lab-build.json' if args.lab else 'inventory/client-character-diagnostic.json')).read_text(encoding='utf-8'))
    if summary['build_exit'] or summary['build_settings'].get('RF_CLIENT_455_CHARACTER_DRAW')!='ON' or sha(Path(summary['build_settings']['RF_CLIENT_455_CHARACTER_DRAW_LIBRARY']))!=build['library_sha256']:raise ValueError('Main draw archive mismatch')
    mapping=(root/'RF_Online-Release.map').read_text(encoding='ascii',errors='replace');selected=[]
    for symbol,owner in APIS.items():
        lines=[line for line in mapping.splitlines() if re.search(r'\s'+re.escape(symbol)+r'\s',line)]
        if not lines:
            if args.lab:raise ValueError('Missing main draw API:'+symbol)
            continue
        provider='RFClient455CharacterDraw:'+owner+'.obj'
        if len(lines)!=1 or provider not in lines[0]:raise ValueError('Wrong main draw provider')
        address=re.search(re.escape(symbol)+r'\s+([0-9a-fA-F]{8})',lines[0]);selected.append({'symbol':symbol,'rva':hex(int(address[1],16)-0x400000),'provider':provider})
    actual=[]
    if args.lab:
        actual=calls((root/'RF_Online.dir/Release/test_client455_character_draw.obj').read_bytes(),list(APIS),include_static=True)
        if set(c['target'] for c in actual)!=set(APIS):raise ValueError('Actual main draw callers missing')
    exe=root/'Release/RF_Online.bin';path=WS/'inventory/client455-character-draw-link.json';report=json.loads(path.read_text(encoding='utf-8')) if path.exists() else {};report[mode]={'architecture':'x86','image_base':'0x400000','exe_sha256':sha(exe),'exe_bytes':exe.stat().st_size,'entry_rva':hex(pe(exe.read_bytes())['entry_rva']),'functions':selected,'actual_callsites':actual,'library_sha256':build['library_sha256'],'scope':'Source Character draw routing;normal typedrenderer andfull455 runtime stillopen'};path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(f'PASS:{mode} main Character draw/{len(selected)}sourceAPIs linked')
if __name__=='__main__':main()
