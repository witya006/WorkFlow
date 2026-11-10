"""Verify selected actual Avatar index/name integration;full skill/UI/selection open."""
import json,re,struct,subprocess
from pathlib import Path
from checkpoint_client455_login import main as check_login,record
from checkpoint_client455_rvp_effects import require,check,load,sha
from compare_client_binaries import WS
from build_client455_x87_math import read_va

def main():
    check_login();ref=load('client455-avatar-classes-reference');run=load('client455-avatar-classes-native');link=load('client455-normal-link');prep=load('client455-normal-preparation');account=load('client455-account-native')
    for key in ['raw','script','snapshot','reused_class_table_reference']:check(ref[key])
    for row in ref['sources']+ref['references']:check(row)
    require(ref['full_functions']==14 and ref['full_instructions']==460 and ref['positive_cfg_blocks']==76,'Complete selected class writer/getter/copy/UI reference')
    require(ref['references'][0]['functions']==ref['references'][1]['functions'],'Selected CFG regions equal both455pins')
    require(run['reference_sha256']==sha(WS/'inventory/client455-avatar-classes-reference.json') and run['normal_link_sha256']==sha(WS/'inventory/client455-normal-link.json'),'Fresh Avatar native evidence')
    for key in ['source','script','builder','map']:check(run[key])
    require(len(run['runs'])==len(ref['cases'])==3,'Three real localized class cases')
    for case,result in zip(ref['cases'],run['runs']):
        check(case['expected']);require(case['name']==result['name'] and result['natural_exit']==0,'Matching successful locale')
        for key in ['exe','console','output']:check(result[key])
        for item in result['inputs']:check(item)
        n=result['native'];require(n['status']=='PASS' and n['actual_Avatar'] and n['class_rows']==165 and n['all_class_bytes'],'Real class corpus applied to actual Avatar')
        require(n['numeric_string_setter_difference'] and n['ui_absent_retains_names'] and n['class23_text_owner'] and n['legacy_fields_preserved'],'Actual writer semantics/text owners')
        require(not n['class_skill_callback_tested'] and not n['full_layout_equipment_selection'],'Do not overclaim full UI/skill/appearance')
    require(account['normal_link_sha256']==sha(WS/'inventory/client455-normal-link.json') and account['natural_exit']==0 and account['native']['status']=='PASS','Fresh affected account/registered receiver run')
    require(account['source_sha256']==sha(WS/account['source']) and account['script_sha256']==sha(WS/'scripts/probe_client455_account.py'),'Current receiver test sources')
    for item in account['inputs']:check(item)
    for key in ['exe','map','output','registered_character_output']:check(account[key])
    for name,value in account['registered_character_sources'].items():require(sha(WS/'scripts/native'/name)==value,'Current registered receiver source '+name)
    classes=account['real_registered_classes'];require(classes['rows']==3 and classes['table_classes']==165 and classes['actual_encrypted_receiver'] and classes['source_reference_sha256']==sha(WS/'inventory/client455-avatar-classes-reference.json'),'Actual1/9receiver applies3real class indices')
    require(prep['avatar_classes_port_sha256']==sha(WS/'scripts/client455_avatar_classes_port.py') and prep['record_inputs']['client455_avatar_classes.inc']==sha(WS/'scripts/native/client455_avatar_classes.inc'),'Current ordinary port')
    source=WS/'work/client455-port/normal/source/character/avatar/cavatar_etc.cpp';body=source.read_bytes()
    require(b'GetClassData455(pi_strDTCode)' in body and b'RefreshClassNames455(pi_byOrderNo,false)' in body and b'RefreshClassNames455(pi_byOrderNo,true)' in body,'Separate ordinary writer routes')
    window=(WS/'work/client455-port/normal/source/userinterface/gamewindow/guicharinfowindow.h').read_bytes();require(b'm_uiInfoValues455[23]' in window and b'if(slot<23)' in window,'Own23field text owner,not legacy Level/Guild indices')
    mapping=(WS/link['map']['file']).read_text();methods={}
    for owner,name in [('CAvatar','SetClassDTIndex'),('CAvatar','SetClassDTIndexByStrDTCode'),('CAvatar','RefreshClassNames455'),('CAvatar','SetPrimaryClassName455'),('RF455ItemDataStore','classByCode'),('RF455ItemDataStore','classByIndex'),('CNetworkMgr','SystemMsg_RegedCharResult_zone')]:
        found=re.findall(r'^\s+\S+\s+\?'+name+'@'+owner+r'@@\S+\s+([0-9a-fA-F]{8})\b',mapping,re.M)
        require(len(found)==1,'Actual ordinary method '+owner+'::'+name);methods[owner+'::'+name]=hex(int(found[0],16)-0x400000)
    # Decode the receiver's exact symbol interval,then prove the transfer to
    # the production class writer rather than just its presence in the MAP.
    begin=0x400000+int(methods['CNetworkMgr::SystemMsg_RegedCharResult_zone'],16)
    function_addresses=[int(m[1],16) for m in re.finditer(r'^\s+[0-9A-Fa-f]{4}:[0-9A-Fa-f]{8}\s+\S+\s+([0-9A-Fa-f]{8})\s+f\s',mapping,re.M)]
    end=min(a for a in function_addresses if a>begin);require(end-begin<0x2000,'Bounded ordinary receiver function')
    info=load('msvc-verification');dumpbin=Path(info['compiler_path'].splitlines()[0]).with_name('dumpbin.exe')
    decoded=subprocess.run([str(dumpbin),'/DISASM:BYTES',f'/RANGE:0x{begin:x},0x{end:x}',str(WS/link['executable']['file'])],capture_output=True,creationflags=subprocess.CREATE_NO_WINDOW)
    require(not decoded.returncode,'Decode own registered receiver');binary=(WS/link['executable']['file']).read_bytes();calls=[];target=0x400000+int(methods['CAvatar::SetClassDTIndexByStrDTCode'],16)
    for line in decoded.stdout.decode(errors='replace').splitlines():
        match=re.match(r'^\s+([0-9A-F]{8}): ((?:[0-9A-F]{2} )+)\s+(\w+)\s*(.*?)\s*$',line)
        if not match:continue
        address=int(match[1],16);data=bytes.fromhex(match[2]);require(read_va(binary,address,len(data))==data,'Own decoded receiver bytes')
        if len(data)==5 and data[0]==0xe8 and address+5+struct.unpack('<i',data[1:])[0]==target:calls.append(dict(rva=hex(address-0x400000),target_rva=hex(target-0x400000),bytes=data.hex()))
    require(len(calls)==1,'Production registered receiver calls actual typed455class writer')
    base=WS/'artifacts/client455-progress/before144/inventory/client455-character-tables-checkpoint.json';require(json.loads(base.read_text())['normal_executable']['sha256']=='b41d50ffb5001c04a54dd0f16bd471c2bc0168e4b8757a52eca7a41067e0b4ec','Exact143base preserved')
    names=['avatar-classes-reference','avatar-classes-native','account-native','login-checkpoint','login-frame-native','login-visual','normal-preparation','normal-build','normal-consumers','normal-link','startup-engine-build','startup-native','startup-audit','own-entry']
    out=dict(status='PARTIAL',scope=ref['scope'],script=record(Path(__file__)),normal_link_sha256=sha(WS/'inventory/client455-normal-link.json'),normal_executable=link['executable'],ordinary_methods_rva=methods,ordinary_registered_class_calls=calls,
        fresh_evidence={name:record(WS/f'inventory/client455-{name}.json') for name in names},snapshot=ref['snapshot'],historical_base=record(base),real_locales=3,class_rows=165,actual_registered_Avatar_classes=3,
        actual_index_and_name_writers=True,text_widget_owners=23,full_class_skill_callback=False,full455CharInfo_layout=False,full_equipment_appearance=False,full_bootstrap=False,ordinary_selection_UI_accepted=False,full_client=False,
        gaps=ref['gaps'],input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-avatar-classes-checkpoint.json').write_text(json.dumps(out,indent=2)+'\n')
    print('PARTIAL:actual Avatar class writers/3locales/165classes and encrypted receiver3real Avatar indices verified;skill callback/full UI/equipment/selection/M9 OPEN')
if __name__=='__main__':main()
