"""Verify ordinary initial item data integration without claiming full455/M9."""
import json,re,struct,subprocess
from pathlib import Path
from checkpoint_client455_login import main as check_login,record
from checkpoint_client455_rvp_effects import require,check,load,sha
from compare_client_binaries import WS
from build_client455_x87_math import read_va

def main():
    check_login();ref=load('client455-item-bootstrap-reference');run=load('client455-item-bootstrap-native');link=load('client455-normal-link');prep=load('client455-normal-preparation')
    for key in ['raw','script','snapshot','reused_item_decoder_reference','reused_item_decoder_raw','country_source']:check(ref[key])
    for row in ref['sources']+ref['references']:check(row)
    require(ref['full_functions']==4 and ref['full_instructions']==257 and ref['positive_cfg_blocks']==27,'Complete new selected reference')
    require(ref['references'][0]['functions']==ref['references'][1]['functions'] and ref['references'][0]['country_item_policy']==ref['references'][1]['country_item_policy'],'Equal bodies and11profile policies')
    require(len(ref['references'][0]['country_item_policy'])==11 and all(row['segmented'] for row in ref['references'][0]['country_item_policy']),'All11 true,not Taiwan inference')
    require(ref['reused_item_loader_instructions']==588,'Existing full Item loader reference retained')
    require(run['reference_sha256']==sha(WS/'inventory/client455-item-bootstrap-reference.json') and run['normal_link_sha256']==sha(WS/'inventory/client455-normal-link.json'),'Fresh native data integration')
    for key in ['source','script','builder','map']:check(run[key])
    require(len(run['runs'])==len(ref['cases'])==6,'Six real locale/selector/error cases')
    for case,result in zip(ref['cases'],run['runs']):
        check(case['expected']);require(case['name']==result['name'] and not result['natural_exit'],'Matching successful case')
        for key in ['exe','console','output']:check(result[key])
        for item in result['inputs']:check(item)
        native=result['native'];require(native['status']=='PASS' and native['selector']==case['selector'] and native['cash_loaded']==case['cash_localization_expected'],'Actual selector/cash result')
        require(native['cash_rows']==1000 and native['set_effect_rows']==1373 and native['item_tables']==47 and native['item_rows']==76049 and native['actual_typed_wrappers']==12,'Real table owners and actual item wrappers')
        require(native['all_table_description_bytes'] and native['actual_reply_selector'] and not native['full_bootstrap_or_legacy_consumers'],'Bounded accepted scope')
    require(prep['item_bootstrap_port_sha256']==sha(WS/'scripts/client455_item_bootstrap_port.py'),'Current ordinary source port')
    for name in ['client455_item_bootstrap.h','client455_item_bootstrap.inc','client455_client_items.h','client455_item_object.cpp']:
        require(prep['record_inputs'][name]==sha(WS/'scripts/native'/name),'Current ordinary native source '+name)
    source=WS/'work/client455-port/normal/source/gameprogress/cgp_login.cpp';body=source.read_bytes()
    require(body.count(b'_GetItemDataMgr()->LoadBootstrap455();')==1 and b'_GetItemDataMgr()->LoadData();' not in body,'Actual Login invokes the new initial path')
    mapping=(WS/link['map']['file']).read_text();methods={}
    for owner,name in [('CItemDataMgr','LoadBootstrap455'),('RF455ClientItems','loadCashFiles'),('RF455ClientItems','loadSetEffectFile'),('RF455ClientItems','loadItemFiles')]:
        found=re.findall(r'^\s+\S+\s+\?'+name+'@'+owner+r'@@\S+\s+([0-9a-fA-F]{8})\b',mapping,re.M)
        require(len(found)==1,'Ordinary linked item method '+name);methods[name]=hex(int(found[0],16)-0x400000)
    # LoadData is inlined into this production bridge. The new typed accessor
    # is currently retained only by the full-object probe,not ordinary gameplay.
    probe_map=(WS/run['map']['file']).read_text();accessor=re.findall(r'^\s+\S+\s+\?GetData455@CItemDataMgr@@\S+\s+([0-9a-fA-F]{8})\b',probe_map,re.M)
    require(len(accessor)==1,'Real typed accessor retained by full-object probe')
    info=load('msvc-verification');dumpbin=Path(info['compiler_path'].splitlines()[0]).with_name('dumpbin.exe');begin=0x400000+int(methods['LoadBootstrap455'],16)
    decoded=subprocess.run([str(dumpbin),'/DISASM:BYTES',f'/RANGE:0x{begin:x},0x{begin+0x90:x}',str(WS/link['executable']['file'])],capture_output=True,creationflags=subprocess.CREATE_NO_WINDOW)
    require(not decoded.returncode,'Decode own item bootstrap');binary=(WS/link['executable']['file']).read_bytes();transfers=[]
    targets={0x400000+int(methods[name],16):name for name in ['loadCashFiles','loadSetEffectFile','loadItemFiles']}
    for line in decoded.stdout.decode(errors='replace').splitlines():
        match=re.match(r'^\s+([0-9A-F]{8}): ((?:[0-9A-F]{2} )+)\s+(\w+)\s*(.*?)\s*$',line)
        if not match:continue
        address=int(match[1],16);data=bytes.fromhex(match[2]);require(read_va(binary,address,len(data))==data,'Own disassembly bytes')
        if len(data)==5 and data[0] in [0xe8,0xe9]:
            target=address+5+struct.unpack('<i',data[1:])[0]
            if target in targets:transfers.append(dict(rva=hex(address-0x400000),target=targets[target],instruction=match[3],bytes=data.hex()))
    require([row['target'] for row in transfers]==['loadCashFiles','loadSetEffectFile','loadItemFiles'],'Actual production cash/set/Item transfer order')
    base=WS/'artifacts/client455-progress/before142/inventory/client455-resource-catalog-checkpoint.json';check(ref['snapshot']);require(json.loads(base.read_text())['normal_executable']['sha256']=='b3f769a9b551a81099ca0ef01b92ac96b47bc5048d6ea9594e21a56a97d8d00c','Exact preserved141base')
    names=['item-bootstrap-reference','item-bootstrap-native','login-checkpoint','login-frame-native','login-visual','normal-preparation','normal-build','normal-consumers','normal-link','startup-engine-build','startup-native','startup-audit','own-entry']
    output=dict(status='PARTIAL',scope=ref['scope'],script=record(Path(__file__)),normal_link_sha256=sha(WS/'inventory/client455-normal-link.json'),normal_executable=link['executable'],
        ordinary_methods_rva=methods,ordinary_bootstrap_transfers=transfers,typed_accessor_only_probe_rva=hex(int(accessor[0],16)-0x400000),fresh_evidence={name:record(WS/f'inventory/client455-{name}.json') for name in names},snapshot=ref['snapshot'],historical_base=record(base),
        real_locales=['ko-kr','zh-tw','ru-ru'],real_cases=6,country_segmented_profiles=11,item_tables=47,item_rows=76049,typed_wrappers_per_case=12,
        initial_item_path_source_linked=True,ordinary_Login_success_response_bootstrap_executed=False,full_bootstrap=False,legacy_item_consumers_migrated=False,full_character_appearance=False,ordinary_selection_UI_accepted=False,full_client=False,
        gaps=ref['gaps'],input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-item-bootstrap-checkpoint.json').write_text(json.dumps(output,indent=2)+'\n')
    print('PARTIAL:ordinary initial cash/set/Item47+ND path,6real locale-selector cases/76049rows/12typed wrappers each;legacy consumers/full bootstrap/selection/M9 OPEN')
if __name__=='__main__':main()
