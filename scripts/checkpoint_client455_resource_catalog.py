"""Verify the real ordinary resource catalog while keeping full client M9 open."""
import json,re
from pathlib import Path
from checkpoint_client455_login import main as check_login,record
from checkpoint_client455_rvp_effects import require,check,load,sha
from compare_client_binaries import WS

def main():
    check_login();ref=load('client455-resource-catalog-reference');native=load('client455-resource-catalog-native');link=load('client455-normal-link');prep=load('client455-normal-preparation')
    for key in ['raw','expected','snapshot','script']:check(ref[key])
    for item in ref['sources']+ref['references']:check(item)
    require(ref['full_functions']==7 and ref['full_instructions']==934 and ref['positive_cfg_blocks']==108,'Full selected catalog reference including EH tails')
    require(ref['references'][0]['functions']==ref['references'][1]['functions'],'All CFG regions equal in both455pins')
    require(native['reference_sha256']==sha(WS/'inventory/client455-resource-catalog-reference.json'),'Current catalog reference')
    require(native['normal_link_sha256']==sha(WS/'inventory/client455-normal-link.json') and native['natural_exit']==0,'Fresh own native run')
    for key in ['source','script','builder','exe','map','console','output']:check(native[key])
    for item in native['inputs']:check(item)
    result=native['native'];require(result['status']=='PASS' and result['groups']==9 and result['rows']==[1267,10484,18872] and result['registered']==[1267,10483,18872],'Real nine catalog groups and registered owners')
    require(result['all_catalog_row_bytes'] and result['player_bones_loaded']==5 and result['real_player_animation'] and not result['full_bootstrap_or_selection'],'Five real skeletons/real animation,not full selection')
    require(len(ref['expected_skipped_meshes'])==1 and ref['expected_skipped_meshes'][0]['group']==4 and ref['expected_skipped_meshes'][0]['index']==20483,'Declared missing NPC parent explains skip')
    require(prep['resource_catalog_port_sha256']==sha(WS/'scripts/client455_resource_catalog_port.py') and prep['record_inputs']['client455_resource_catalog.h']==sha(WS/'scripts/native/client455_resource_catalog.h'),'Current ordinary source port')
    mapping=(WS/link['map']['file']).read_text();methods={}
    for owner,name in [('CCharResDataMgr','LoadData'),('CCharResData','LoadBoneDataList'),('CCharResData','LoadMeshDataList'),('CCharResData','LoadAniDataList')]:
        found=re.findall(r'^\s+\S+\s+\?'+name+'@'+owner+r'@@\S+\s+([0-9a-fA-F]{8})\b',mapping,re.M)
        require(len(found)==1,'Ordinary linked resource method '+name);methods[owner+'::'+name]=hex(int(found[0],16)-0x400000)
    base=WS/'artifacts/client455-progress/before141/inventory/client455-registered-characters-checkpoint.json'
    require(base.is_file() and json.loads(base.read_text())['normal_executable']['sha256']=='a3002fc48427f09cb1cb7c2f57c95696162d1099ce7714e890f1053d1c321607','Preserved exact140base;not fresh141account proof')
    names=['resource-catalog-reference','resource-catalog-native','login-checkpoint','login-frame-native','login-visual','normal-preparation','normal-build','normal-consumers','normal-link','startup-engine-build','startup-native','startup-audit','own-entry']
    report=dict(status='PARTIAL',scope=ref['scope'],script=record(Path(__file__)),normal_link_sha256=sha(WS/'inventory/client455-normal-link.json'),normal_executable=link['executable'],
        component=result,ordinary_methods_rva=methods,fresh_evidence={name:record(WS/f'inventory/client455-{name}.json') for name in names},snapshot=ref['snapshot'],
        historical_base=record(base),account_protocol_rerun_on_this_PE=False,full_bootstrap=False,full_character_appearance=False,ordinary_selection_UI_accepted=False,full_client=False,
        checked_missing_resource_references=len(ref['missing_declared_inputs']),missing_resource_inventory_is_complete=False,resolved_archive_members=len(ref['resolved_archive_members']),
        gaps=ref['gaps']+['Remaining legacy resource getters/consumers and all client-acceptance gaps'],input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-resource-catalog-checkpoint.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PARTIAL:real Resource.edf nine groups/1267bones/10483meshes/18872ANI registrations,five player skeletons+realANI;ordinary Login preserved;full bootstrap/selection/M9 OPEN')
if __name__=='__main__':main()
