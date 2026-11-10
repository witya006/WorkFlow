"""Accept selected ordinary character-table integration,not class/selection/full455."""
import json,re,struct,subprocess
from pathlib import Path
from checkpoint_client455_login import main as check_login,record
from checkpoint_client455_rvp_effects import require,check,load,sha
from compare_client_binaries import WS
from build_client455_x87_math import read_va

def main():
    check_login();ref=load('client455-character-tables-reference');run=load('client455-character-tables-native');link=load('client455-normal-link');prep=load('client455-normal-preparation')
    for key in ['raw','script','snapshot']:check(ref[key])
    for row in ref['sources']+ref['references']:check(row)
    require(ref['full_functions']==15 and ref['full_instructions']==1737 and ref['positive_cfg_blocks']==193,'Complete selected character loader/lookup/Read reference')
    require(ref['references'][0]['functions']==ref['references'][1]['functions'],'All selected positive CFG regions equal both pins')
    require(run['reference_sha256']==sha(WS/'inventory/client455-character-tables-reference.json') and run['normal_link_sha256']==sha(WS/'inventory/client455-normal-link.json'),'Fresh native integration evidence')
    for key in ['source','script','builder','map']:check(run[key])
    require(len(run['runs'])==len(ref['cases'])==5,'Four real cases and one changed-name DBCS fixture')
    for case,result in zip(ref['cases'],run['runs']):
        check(case['expected']);require(case['name']==result['name'] and result['natural_exit']==0,'Matching successful case')
        for key in ['exe','console','output']:check(result[key])
        for item in result['inputs']:check(item)
        n=result['native'];require(n['status']=='PASS' and n['selector']==case['selector'] and n['loader_results']==[int(case['results'][k]) for k in ['player','skill','store','character']],'Actual selector and target localization results')
        require(n['tables']==14 and n['class_rows']==165 and n['typed_sf_wrappers']==5,'Complete real corpus and typed wrappers')
        require(n['all_table_bytes'] and n['store_owned_descriptions'] and n['actual_reply_selector'] and n['actual_skill_force_board_dimensions'] and not n['full_class_equipment_selection'],'Exact bounded accepted scope')
    require(prep['character_tables_port_sha256']==sha(WS/'scripts/client455_character_tables_port.py'),'Current ordinary character port')
    for name in ['client455_character_tables.h','client455_character_tables.cpp','client455_item_payloads.h','client455_item_payloads.cpp']:
        require(prep['record_inputs'][name]==sha(WS/'scripts/native'/name),'Current native source '+name)
    source=WS/'work/client455-port/normal/source/datatable/ccharacterdatamgr.cpp';body=source.read_bytes()
    require(body.index(b'm_tables455.loadPlayerFile()')<body.index(b'm_tables455.skillResult=LoadSkillForceData()')<body.index(b'm_tables455.storeResult=LoadNpcData()')<body.index(b'm_tables455.characterResult=LoadCharacterData()'),'Ordinary four loader order')
    require(b'IBT_SKILL, 7, 20' in body and b'7, 12, 100' in body and b'IBT_FORCE, 6, 20' in body and b'6, 24, 100' in body,'Actual source board dimensions')
    mapping=(WS/link['map']['file']).read_text();methods={}
    for owner,name in [('CCharacterDataMgr','LoadData'),('RF455CharacterTables','loadPlayerFile'),('RF455SkillForceData','loadFiles'),('RF455CharacterTables','loadStoreFiles'),('RF455CharacterTables','loadCharacterFiles'),('RF455ItemDataStore','localizeCharacterEdf')]:
        found=re.findall(r'^\s+\S+\s+\?'+name+'@'+owner+r'@@\S+\s+([0-9a-fA-F]{8})\b',mapping,re.M)
        require(len(found)==1,'Ordinary linked loader '+owner+'::'+name);methods[owner+'::'+name]=hex(int(found[0],16)-0x400000)
    info=load('msvc-verification');dumpbin=Path(info['compiler_path'].splitlines()[0]).with_name('dumpbin.exe');begin=0x400000+int(methods['CCharacterDataMgr::LoadData'],16)
    decoded=subprocess.run([str(dumpbin),'/DISASM:BYTES',f'/RANGE:0x{begin:x},0x{begin+0x400:x}',str(WS/link['executable']['file'])],capture_output=True,creationflags=subprocess.CREATE_NO_WINDOW)
    require(not decoded.returncode,'Decode actual ordinary manager');binary=(WS/link['executable']['file']).read_bytes();transfers=[]
    expected=['RF455CharacterTables::loadPlayerFile','RF455SkillForceData::loadFiles','RF455CharacterTables::loadStoreFiles','RF455CharacterTables::loadCharacterFiles']
    targets={0x400000+int(methods[name],16):name for name in expected}
    for line in decoded.stdout.decode(errors='replace').splitlines():
        match=re.match(r'^\s+([0-9A-F]{8}): ((?:[0-9A-F]{2} )+)\s+(\w+)\s*(.*?)\s*$',line)
        if not match:continue
        address=int(match[1],16);data=bytes.fromhex(match[2]);require(read_va(binary,address,len(data))==data,'Own decoded bytes match PE')
        if match[3].lower().startswith('ret'):break
        if len(data)==5 and data[0] in [0xe8,0xe9]:
            target=address+5+struct.unpack('<i',data[1:])[0]
            if target in targets:transfers.append(dict(rva=hex(address-0x400000),target=targets[target],instruction=match[3],bytes=data.hex()))
    require([r['target'] for r in transfers]==expected,'Production manager actually calls455loaders in order')
    base=WS/'artifacts/client455-progress/before143/inventory/client455-item-bootstrap-checkpoint.json'
    require(json.loads(base.read_text())['normal_executable']['sha256']=='f0114c80b2a08bdb313113368c729b4a7cb4b4c0c05cdc193ee368edf627f2d1','Preserved exact142base')
    names=['character-tables-reference','character-tables-native','login-checkpoint','login-frame-native','login-visual','normal-preparation','normal-build','normal-consumers','normal-link','startup-engine-build','startup-native','startup-audit','own-entry']
    out=dict(status='PARTIAL',scope=ref['scope'],script=record(Path(__file__)),normal_link_sha256=sha(WS/'inventory/client455-normal-link.json'),normal_executable=link['executable'],
        ordinary_methods_rva=methods,ordinary_loader_transfers=transfers,fresh_evidence={name:record(WS/f'inventory/client455-{name}.json') for name in names},snapshot=ref['snapshot'],historical_base=record(base),
        real_cases=4,synthetic_dbcs_cases=1,locales=['ko-kr','zh-tw','ru-ru'],tables=14,class_rows=165,typed_sf_wrappers_per_case=5,
        actual_manager_loader_connected=True,ordinary_success_response_bootstrap_executed=False,full_bootstrap=False,legacy_character_skill_consumers_migrated=False,full_class_equipment_selection=False,full_client=False,
        gaps=ref['gaps'],input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-character-tables-checkpoint.json').write_text(json.dumps(out,indent=2)+'\n')
    print('PARTIAL: ordinary CharacterDataMgr/14tables/165classlookups/actual SF boards/4real cases+DBCS verified;Avatar classes/equipment/selection/full455 OPEN')
if __name__=='__main__':main()
