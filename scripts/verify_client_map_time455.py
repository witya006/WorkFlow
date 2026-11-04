"""Check linked map-time arithmetic and the selected real client source objects."""
import argparse,hashlib,json,re,struct,subprocess
from pathlib import Path
from compare_client_binaries import WS
from build_client455_clock import sha
from build_client455_x87_math import read_va

def main():
    cli=argparse.ArgumentParser();cli.add_argument('--lab',action='store_true');args=cli.parse_args()
    mode='lab' if args.lab else 'normal';folder='build-helper-lab' if args.lab else 'build-character-diagnostic';build=WS/'work/client-build'/folder
    summary=json.loads((WS/('inventory/client-helper-lab-build.json' if args.lab else 'inventory/client-character-diagnostic.json')).read_text(encoding='utf-8'))
    if summary['build_exit'] or summary['build_settings'].get('RF_CLIENT_455_MAP_TIME')!='ON':raise ValueError('Successful map-time-enabled build required')
    proof=json.loads((WS/'inventory/client455-map-time.json').read_text(encoding='utf-8'))
    for name,digest in proof['source_sha256'].items():
        if sha(WS/'scripts/native'/name)!=digest:raise ValueError('Map time component source proof stale')
    patches=[p for p in json.loads((WS/'inventory/client-behavior-patches.json').read_text(encoding='utf-8')) if p['build_option']=='RF_CLIENT_455_MAP_TIME']
    if len(patches)!=3 or any(sha(WS/p['file'])!=p['patched_sha256'] for p in patches):raise ValueError('Map time3source ledgers changed')
    data=(build/'Release/RF_Online.bin').read_bytes();mapping=(build/'RF_Online-Release.map').read_text(encoding='ascii',errors='replace')
    symbols={m[1]:int(m[2],16) for line in mapping.splitlines() if (m:=re.match(r'\s+[0-9a-fA-F]{4}:[0-9a-fA-F]{8}\s+(\S+)\s+([0-9a-fA-F]{8})\s',line))}
    address=symbols['_RF455_MapGameFraction'];reference=(WS/'work/client-reference/current/RF_Online.bin').read_bytes()
    target=json.loads((WS/'config/client-target.json').read_text(encoding='utf-8'))
    if hashlib.sha256(reference).hexdigest()!=target['behavior_reference']['sha256']:raise ValueError('Map time reference changed')
    expected=bytearray(read_va(reference,0x7c8dc4,130));actual=read_va(data,address+15,130);thunks=[]
    for reloc in proof['binary_evidence'][0]['relocations']:
        at=reloc['fragment_offset'];dest=symbols[reloc['symbol']]
        value=dest
        if reloc['type']==20:
            called=address+15+at+4+struct.unpack_from('<i',actual,at)[0];cursor=called
            for _ in range(4):
                if cursor==dest:break
                jump=read_va(data,cursor,5)
                if jump[0]!=0xe9:raise ValueError('Map rate call has unexpected forwarding code')
                thunks.append({'va':hex(cursor),'rva':hex(cursor-0x400000),'bytes':jump.hex()})
                cursor+=5+struct.unpack_from('<i',jump,1)[0]
            if cursor!=dest:raise ValueError('Map rate call does not reach the verified getter')
            value=(called-(address+15+at+4))&0xFFFFFFFF
        struct.pack_into('<I',expected,at,value)
    if actual!=expected:raise ValueError('Linked map-time130byte calculation changed')
    if read_va(data,address,15)!=bytes.fromhex('558bec81ecc40000008b45088945a8') or read_va(data,address+145,7)!=bytes.fromhex('d945a48be55dc3'):raise ValueError('Map time helper frame/return changed')
    verified=json.loads((WS/'inventory/msvc-verification.json').read_text(encoding='utf-8'));dumpbin=Path(verified['compiler_path'].splitlines()[0]).with_name('dumpbin.exe');objects=[]
    for name,required in [('cland.obj',['_RF455_InitMapTime','_RF455_ApplyMapTime']),('cnetmsgprocessor_map.obj',['_RF455_ReceiveMapTime'])]:
        obj=build/'RF_Online.dir/Release'/name;table=subprocess.check_output([str(dumpbin),'/symbols',str(obj)]).decode('utf-8',errors='replace')
        for symbol in required:
            if not any('UNDEF' in line and re.search(r'\|\s*'+re.escape(symbol)+r'\s*$',line) for line in table.splitlines()):raise ValueError('Actual client object misses selected API:'+symbol)
        objects.append({'object':obj.relative_to(WS).as_posix(),'sha256':sha(obj),'undefined_references':required})
    path=WS/'inventory/client455-map-time-link.json';out=json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}
    out[mode]={'exe':(build/'Release/RF_Online.bin').relative_to(WS).as_posix(),'exe_sha256':hashlib.sha256(data).hexdigest(),'architecture':'x86','image_base':'0x400000','numeric_helper_va':hex(address),'numeric_helper_rva':hex(address-0x400000),'reference_fragment_va':'0x7c8dc4','reference_fragment_rva':'0x3c8dc4','fragment_size':130,'fragment_sha256':hashlib.sha256(actual).hexdigest(),'instruction_identity_except_verified_operands':True,'verified_rate_call_thunks':thunks,'selected_objects':objects,'component_report_sha256':sha(WS/'inventory/client455-map-time.json'),'scope':'Selected linked arithmetic and actual client undefined references/source ledgers. Full CLand UI/load-error behavior and calendar domain not certified.'}
    path.write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
    print(f'PASS:{mode} linked map-time130bytes and actual CLand/packet object source selection verified.')

if __name__=='__main__':main()
