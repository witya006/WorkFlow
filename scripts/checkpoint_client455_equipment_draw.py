"""Verify this partial runtime without treating a model fixture as a player."""
import collections,json,re,struct,subprocess
from pathlib import Path
from compare_client_binaries import WS
from build_client455_x87_math import read_va
from audit_client455_equipment import record
from checkpoint_client455_rvp_effects import load,check,require,sha
from client455_normal_link_evidence import validate_normal_link

def production_calls(link):
    mapping=(WS/link['map']['file']).read_text();exe=WS/link['executable']['file'];binary=exe.read_bytes()
    symbols={name:int(address,16) for name,address in re.findall(r'^\s+\S+\s+(\S+)\s+([0-9A-Fa-f]{8})\s+f\b',mapping,re.M)}
    names={'queue_clear':'?Clear@CItemEffectRenderer@@QAEXXZ','queue_render':'?Render@CItemEffectRenderer@@QAEHXZ',
        'clear':'?RF455_ClearEquipmentEffects455@@YAXXZ','render':'?RF455_RenderEquipmentEffects455@@YAXXZ',
        'equipment':'?Render@RF455EquipmentObject@@UAEHXZ','draw':'?DrawWithEffect455@RF455EquipmentObject@@AAEXEPBUD3DXMATRIX@@@Z',
        'overlay':'?DrawCharacterOverlay455@CRender@@QAEXPAURF455CharacterStorage@@PAMMMM_N@Z'}
    addresses={k:symbols[v] for k,v in names.items()};all_addresses=sorted(set(symbols.values()))
    dumpbin=Path(load('msvc-verification')['compiler_path'].splitlines()[0]).with_name('dumpbin.exe');result=[]
    for owner,target in [('queue_clear','clear'),('queue_render','render'),('equipment','draw'),('draw','overlay')]:
        start=addresses[owner];end=min(a for a in all_addresses if a>start)
        require(end-start<0x3000,'Bounded source owner '+owner)
        decoded=subprocess.run([str(dumpbin),'/DISASM:BYTES',f'/RANGE:0x{start:x},0x{end:x}',str(exe)],capture_output=True,creationflags=subprocess.CREATE_NO_WINDOW)
        require(decoded.returncode==0,'Own disassembly');matched=[]
        for line in decoded.stdout.decode(errors='replace').splitlines():
            m=re.match(r'^\s+([0-9A-Fa-f]{8}): ((?:[0-9A-Fa-f]{2} )+)\s+\w+',line)
            if not m:continue
            address=int(m[1],16);data=bytes.fromhex(m[2]);require(read_va(binary,address,len(data))==data,'Own decoded bytes')
            if len(data)==5 and data[0] in [0xe8,0xe9] and address+5+struct.unpack('<i',data[1:])[0]==addresses[target]:matched.append(dict(rva=hex(address-0x400000),kind='CALL' if data[0]==0xe8 else 'tail-JMP'))
        require(len(matched)==1,'Actual ordinary transfer '+owner+'->'+target)
        result.append(dict(owner=owner,target=target,source_rva=hex(start-0x400000),target_rva=hex(addresses[target]-0x400000),**matched[0]))
    require('_RF455_DrawCharacterOverlay455' in symbols,'Secondary geometry retained inordinary PE')
    return result

def main():
    ref=load('client455-equipment-draw-reference');native=load('client455-equipment-draw-native');link=load('client455-normal-link');link_hash=sha(WS/'inventory/client455-normal-link.json')
    require(validate_normal_link(link)=='PASS','Current normal link')
    require((ref['full_functions'],ref['full_instructions'],ref['positive_cfg_blocks'])==(62,6959,650),'Full selected reference regions')
    for key in ['raw','effects_raw','diagnostics','script','region_verifier','decoder','port','preparer','runtime_base','prior_source_snapshot']:check(ref[key])
    for row in ref['reused_raw']+ref['sources']:check(row)
    for key in ['source','script','exe','map','console','output']:check(native[key])
    for row in native['source_includes']+native['inputs']+native['frames']:check(row)
    result=native['native'];require(result==json.loads((WS/native['output']['file']).read_text()) and result['status']=='PASS' and native['natural_exit']==0,'Actual source result')
    require(result['primary_draws']>0 and result['overlay_draws']==2*result['primary_draws'] and result['matrix_draws']==result['primary_draws'],'Distinct target render overloads')
    require(result['visible_model_pixels']>0 and result['changed_overlay_pixels']>0 and result['actual_alpha_restore'] and result['fade_render_gate'],'Actual source geometry/alpha/fade')
    require(result['metadata_cases']==8 and result['unit_key_not_BYTE'] and result['virtualgrade_not_boolean'],'Raw metadata andnumeric grade')
    require(result['queue_cap']==256 and result['queue_palette_oracles']>0 and result['queue_four_matrix_aliasing'] and result['queue_shared_payload_teardown'],'Retained queue pose/owner behavior')
    require(not result['actual_nonzero_particle_effects'] and not result['full_player_appearance'],'Keep untested effect/player scope open')
    previous=WS/'artifacts/client455-progress/before149/inventory';old_grade=json.loads((previous/'client455-grade-overlay-native.json').read_text())
    frames={Path(f['file']).name:f for f in native['frames']}
    require(frames['equipment-base.png']['sha256']==old_grade['baseline_frame']['sha256'] and frames['equipment-overlay.png']['sha256']==old_grade['frame']['sha256'],'Wrapper frames equal preserved148controlled backend frames')
    for name in ['equipment-draw-native','account-native','startup-native','ui-startup-native','login-frame-native']:
        require(load('client455-'+name)['normal_link_sha256']==link_hash,'Fresh affected evidence '+name)
    require(load('client455-normal-build')['objects']==182 and load('client455-normal-build')['canonical_kernel_objects']==20 and load('client455-startup-engine-build')['objects']==67,'Complete selected build')
    require(load('client455-startup-contracts-native')['build_sha256']==sha(WS/'inventory/client455-startup-engine-build.json'),'Unchanged startup engine contracts')
    create=load('client455-ui-startup-native');login=load('client455-login-frame-native');account=load('client455-account-native')
    require(create['completed_existing_client_create'] and login['first_login_frame_completed'] and login['first_login_frame_captured'] and login['capture_result']['result']==0,'Ordinary Create/Login')
    for key in ['captured_frame','capture_metadata']:check(login[key])
    old_login=json.loads((previous/'client455-login-frame-native.json').read_text());profile=lambda r:collections.Counter((e['code'],e['first_chance']) for e in r['exceptions'])
    require(profile(login)==profile(old_login) and all(e['first_chance']==1 for e in login['exceptions']),'No new or unhandled exception profile')
    require(account['natural_exit']==0 and account['registered_character_native']['actual_Avatar_records']==3 and not account['authentication_performed'],'Affected Avatar records;not authentication')
    for key in ['exe','map','output','registered_character_output']:check(account[key])
    calls=production_calls(link)
    names=['equipment-draw-reference','equipment-draw-native','account-native','normal-preparation','normal-build','normal-consumers','normal-link','startup-engine-build','startup-contracts-native','startup-native','startup-audit','own-entry','ui-startup-native','login-frame-native','character-draw-build','renderer-owner-build']
    report=dict(status='PARTIAL',scope=ref['scope'],script=record(Path(__file__)),normal_link_sha256=link_hash,normal_executable=link['executable'],
        fresh_evidence={name:record(WS/f'inventory/client455-{name}.json') for name in names},prior_runtime=ref['runtime_base'],
        ordinary_calls=calls,secondary_geometry_retained_in_normal_PE=True,ordinary_queue_entrypoints_connected=True,
        ordinary_player_connected=False,complete_particle_registry=False,actual_nonzero_particle_effects=False,
        source_Render_wrappers=True,native=result,frames=native['frames'],same_controlled_frames_as148=True,
        ordinary_Create=True,ordinary_Login_frame=login['captured_frame'],ordinary_Login_capture=login['capture_result'],
        known_first_chance_exceptions=len(login['exceptions']),unhandled_exceptions=0,
        full_mesh_object_renderer=False,full_appearance_or_selection=False,full_client=False,gaps=ref['gaps'],input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-equipment-draw-checkpoint.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PARTIAL:actual equipment Render/fade/alpha/grade/queue verified;ordinary Create/Login preserved;full player/particle registry/M9 OPEN')

if __name__=='__main__':main()
