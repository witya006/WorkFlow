"""Verify selected typed equipment/default resource owners;not full appearance/M9."""
import json,re,struct,subprocess
from pathlib import Path
from checkpoint_client455_login import main as check_login,record
from checkpoint_client455_rvp_effects import require,check,load,sha
from compare_client_binaries import WS
from build_client455_x87_math import read_va

def main():
    check_login();ref=load('client455-equipment-reference');run=load('client455-equipment-native');link=load('client455-normal-link');prep=load('client455-normal-preparation');account=load('client455-account-native')
    for key in ['raw','script','snapshot','expected']:check(ref[key])
    for row in ref['sources']+ref['references']:check(row)
    require(ref['full_functions']==18 and ref['full_instructions']==630 and ref['positive_cfg_blocks']==60,'Full selected creation/resource/getter regions')
    require(ref['references'][0]['functions']==ref['references'][1]['functions'] and ref['references'][0]['equipment_rtti']==ref['references'][1]['equipment_rtti'],'Selected bodies/RTTI equal both455pins')
    require(run['reference_sha256']==sha(WS/'inventory/client455-equipment-reference.json') and run['normal_link_sha256']==sha(WS/'inventory/client455-normal-link.json'),'Fresh exact equipment run')
    for key in ['source','script','builder','exe','map','console','output']:check(run[key])
    for row in run['inputs']:check(row)
    n=run['native'];require(run['natural_exit']==0 and n['status']=='PASS' and n['plan_cases']==ref['plan_cases']==51,'Branch plans/native result')
    require(n['real_models_loaded']==len(ref['selected'])==32 and n['actual_default_creations']==30 and n['gpu_texture_entries']==len(ref['texture_names'])==33,'Real models/defaults/GPU textures')
    require(n['default_payload_owners']==6 and n['payloads_after_teardown']==0 and n['actual_resource_bindings'] and n['ordinary_Avatar_default_setter'] and not n['full_player_appearance_or_draw'],'Resource/payload lifetime and bounded scope')
    require(not ref['missing'] and len(ref['texture_fallbacks'])==33,'Required textures resolved using actual RFT fallback')
    require(account['normal_link_sha256']==sha(WS/'inventory/client455-normal-link.json') and account['natural_exit']==0 and account['native']['status']=='PASS','Affected registered/account path remains working')
    require(account['registered_character_sources']['client455_registered_characters.inc']==sha(WS/'scripts/native/client455_registered_characters.inc'),'Fresh typed default getter in affected receiver')
    for key in ['exe','map','output','registered_character_output']:check(account[key])
    for row in account['inputs']:check(row)
    require(prep['equipment_port_sha256']==sha(WS/'scripts/client455_equipment_port.py'),'Current ordinary equipment port')
    for name in ['client455_equipment_object.h','client455_equipment_object.cpp']:
        require(prep['record_inputs'][name]==sha(WS/'scripts/native'/name),'Current equipment source '+name)
    header=(WS/'work/client455-port/normal/source/character/avatar/cavatar.h').read_bytes();body=(WS/'work/client455-port/normal/source/character/avatar/cavatar_etc.cpp').read_bytes()
    require(b'RF455EquipmentObject m_defaultItems455[6]' in header and b'GetDefaultItem455(BYTE part)' in header and b'object.Create455(pi_byPartType,pi_dwDTIndex)' in body,'Actual Avatar owns typed defaults')
    receiver=(WS/'scripts/native/client455_registered_characters.inc').read_bytes();require(receiver.count(b'GetDefaultItem455(')==2 and b'GetDefaultItem(' not in receiver,'Ordinary registered receiver uses typed default getters')
    mapping=(WS/link['map']['file']).read_text();methods={}
    symbols={'default_setter':'?SetDefaultItem@CAvatar@@QAEHEK@Z','equipment_create':'?Create455@RF455EquipmentObject@@QAE_NEK@Z','equipment_bind':'?SetItem455@RF455EquipmentObject@@UAEXPAVRF455ManagedItem@@@Z','receiver':'?SystemMsg_RegedCharResult_zone@CNetworkMgr@@IAEXPAD@Z'}
    for name,sym in symbols.items():
        found=re.findall(r'^\s+\S+\s+'+re.escape(sym)+r'\s+([0-9a-fA-F]{8})\b',mapping,re.M);require(len(found)==1,'Actual production method '+name);methods[name]=hex(int(found[0],16)-0x400000)
    begin=0x400000+int(methods['receiver'],16);target=0x400000+int(methods['default_setter'],16)
    addresses=[int(m[1],16) for m in re.finditer(r'^\s+[0-9A-Fa-f]{4}:[0-9A-Fa-f]{8}\s+\S+\s+([0-9A-Fa-f]{8})\s+f\s',mapping,re.M)];end=min(a for a in addresses if a>begin)
    require(end-begin<0x2000,'Bounded ordinary receiver interval');info=load('msvc-verification');dumpbin=Path(info['compiler_path'].splitlines()[0]).with_name('dumpbin.exe')
    decoded=subprocess.run([str(dumpbin),'/DISASM:BYTES',f'/RANGE:0x{begin:x},0x{end:x}',str(WS/link['executable']['file'])],capture_output=True,creationflags=subprocess.CREATE_NO_WINDOW)
    require(not decoded.returncode,'Decode own registered/default call');binary=(WS/link['executable']['file']).read_bytes();calls=[]
    for line in decoded.stdout.decode(errors='replace').splitlines():
        m=re.match(r'^\s+([0-9A-F]{8}): ((?:[0-9A-F]{2} )+)\s+(\w+)\s*(.*?)\s*$',line)
        if not m:continue
        address=int(m[1],16);data=bytes.fromhex(m[2]);require(read_va(binary,address,len(data))==data,'Own decoded bytes match PE')
        if len(data)==5 and data[0]==0xe8 and address+5+struct.unpack('<i',data[1:])[0]==target:calls.append(dict(rva=hex(address-0x400000),target_rva=hex(target-0x400000),bytes=data.hex()))
    require(len(calls)==1,'Production receiver calls new default Avatar setter')
    base=WS/'artifacts/client455-progress/before145/inventory/client455-avatar-classes-checkpoint.json';require(json.loads(base.read_text())['normal_executable']['sha256']=='ea25eea5222039073ddf7e7823219336080ae298fd78afa0e99b38a65584f812','Exact144base preserved')
    names=['equipment-reference','equipment-native','account-native','login-checkpoint','login-frame-native','login-visual','normal-preparation','normal-build','normal-consumers','normal-link','startup-engine-build','startup-native','startup-audit','own-entry']
    out=dict(status='PARTIAL',scope=ref['scope'],script=record(Path(__file__)),normal_link_sha256=sha(WS/'inventory/client455-normal-link.json'),normal_executable=link['executable'],ordinary_methods_rva=methods,ordinary_default_calls=calls,
        fresh_evidence={name:record(WS/f'inventory/client455-{name}.json') for name in names},snapshot=ref['snapshot'],historical_base=record(base),real_models=32,gpu_textures=33,actual_default_creations=30,default_slots=6,
        actual_default_owner_connected=True,full_player_equipment_consumers=False,full_appearance_or_draw=False,full_bootstrap=False,ordinary_selection_UI_accepted=False,full_client=False,
        gaps=ref['gaps'],input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-equipment-checkpoint.json').write_text(json.dumps(out,indent=2)+'\n')
    print('PARTIAL:typed equipment/default resource owners/32realmodels/33GPUtextures/30Avatar defaults/normal Login verified;full Player equipment/draw/selection/M9 OPEN')
if __name__=='__main__':main()
