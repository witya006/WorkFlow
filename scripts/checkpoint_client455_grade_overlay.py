"""Accept the recovered backend andcurrent partial runtime,not full equipment."""
import collections,json,re,struct,subprocess
from pathlib import Path
from compare_client_binaries import WS
from build_client455_x87_math import read_va
from audit_client455_equipment import record
from checkpoint_client455_rvp_effects import load,check,require,sha
from client455_normal_link_evidence import validate_normal_link

def main():
    ref=load('client455-grade-overlay-reference');native=load('client455-grade-overlay-native')
    link=load('client455-normal-link');link_hash=sha(WS/'inventory/client455-normal-link.json')
    require(validate_normal_link(link)=='PASS','Current normal link')
    require(ref['full_functions']==21 and ref['full_instructions']==2863 and ref['positive_cfg_blocks']==239,'Full pinned selected functions')
    for key in ['raw','reused_raw','script','decoder','region_verifier','port_script','preparer','staging_script','runtime_base']:check(ref[key])
    for row in ref['sources']:check(row)
    for key in ['source','source_include','script','exe','map','console','output','frame','baseline_frame']:check(native[key])
    for row in native['inputs']:check(row)
    result=native['native'];require(result==json.loads((WS/native['output']['file']).read_text()) and result['status']=='PASS' and native['natural_exit']==0,'Actual source/native result')
    require(result['real_materials']==4 and result['real_GPU_textures']==4 and result['all_material_bytes']==2104,'Real material data andtextures')
    require(result['actual_overlay_geometry_draws']>0 and result['visible_model_pixels']>0 and result['changed_overlay_pixels']>0,'Additional actual geometry andRGB contribution')
    require(result['archive_flag_fallback_cases']==3 and result['private_layer6_oracle'] and result['actual_shader_constants92'] and result['actual_release'],'Selected actual contracts')
    require(result['controlled_pose'] and not result['full_equipment_draw'],'Keep ordinary character/appearance open')
    uv=load('client455-material-uv-native');require(uv['natural_exit']==0 and uv['native']['status']=='PASS' and len(uv['native']['layers'])==7,'Actual all7UV layers')
    for key in ['source','script','exe','map','console','output']:check(uv[key])
    for name in ['grade-overlay-native','material-uv-native','account-native','startup-native','ui-startup-native','login-frame-native']:
        require(load('client455-'+name)['normal_link_sha256']==link_hash,'Fresh affected evidence '+name)
    require(load('client455-normal-build')['objects']==182 and load('client455-normal-build')['canonical_kernel_objects']==20 and load('client455-startup-engine-build')['objects']==67,'Complete selected build')
    require(load('client455-startup-contracts-native')['build_sha256']==sha(WS/'inventory/client455-startup-engine-build.json'),'Fresh startup contracts')
    create=load('client455-ui-startup-native');login=load('client455-login-frame-native')
    require(create['completed_existing_client_create'] and login['first_login_frame_completed'] and login['first_login_frame_captured'] and login['capture_result']['result']==0,'Own ordinary Create/Login')
    for key in ['captured_frame','capture_metadata']:check(login[key])
    previous_file=WS/'artifacts/client455-progress/before148/inventory/client455-login-frame-native.json';previous=json.loads(previous_file.read_text())
    profile=lambda value:collections.Counter((e['code'],e['first_chance']) for e in value['exceptions'])
    require(profile(login)==profile(previous) and all(e['first_chance']==1 for e in login['exceptions']),'No new exception profile or unhandled exception')
    account=load('client455-account-native');require(account['natural_exit']==0 and account['registered_character_native']['actual_Avatar_records']==3 and not account['authentication_performed'],'Affected actual account/Avatar path;not auth')
    for key in ['exe','map','output','registered_character_output']:check(account[key])
    mapping=(WS/link['map']['file']).read_text();binary=(WS/link['executable']['file']).read_bytes()
    symbols={'create':'?CreateEffect@@YAXXZ','destroy':'?DestroyEffect@@YAXXZ','load':'?RF455_LoadGradeOverlays455@@YAXXZ','release':'?RF455_ReleaseGradeOverlays455@@YAXXZ'}
    addresses={}
    for key,symbol in symbols.items():
        matches=re.findall(re.escape(symbol)+r'\s+([0-9A-Fa-f]{8})\s+f\b',mapping);require(len(matches)==1,'Production lifecycle symbol '+key);addresses[key]=int(matches[0],16)
    all_addresses=sorted(set(int(m[1],16) for m in re.finditer(r'^\s+\S+\s+\S+\s+([0-9a-fA-F]{8})\s+f\b',mapping,re.M)))
    info=load('msvc-verification');dumpbin=Path(info['compiler_path'].splitlines()[0]).with_name('dumpbin.exe');calls=[]
    for owner,target in [('create','load'),('destroy','release')]:
        start=addresses[owner];end=min(a for a in all_addresses if a>start);require(end-start<0x1000,'Bounded ordinary lifecycle body')
        disasm=subprocess.run([str(dumpbin),'/DISASM:BYTES',f'/RANGE:0x{start:x},0x{end:x}',str(WS/link['executable']['file'])],capture_output=True,creationflags=subprocess.CREATE_NO_WINDOW);require(disasm.returncode==0,'Decode actual lifecycle calls')
        matched=[]
        for line in disasm.stdout.decode(errors='replace').splitlines():
            m=re.match(r'^\s+([0-9A-Fa-f]{8}): ((?:[0-9A-Fa-f]{2} )+)\s+\w+',line)
            if not m:continue
            address=int(m[1],16);data=bytes.fromhex(m[2]);require(read_va(binary,address,len(data))==data,'Own decoded bytes')
            if len(data)==5 and data[0]==0xe8 and address+5+struct.unpack('<i',data[1:])[0]==addresses[target]:matched.append(hex(address-0x400000))
        require(len(matched)==1,'Ordinary '+owner+' calls '+target);calls.append(dict(owner=owner,target=target,call_rva=matched[0],target_rva=hex(addresses[target]-0x400000)))
    names=['grade-overlay-reference','grade-overlay-native','material-uv-native','account-native','normal-preparation','normal-build','normal-consumers','normal-link','startup-engine-build','startup-contracts-native','startup-native','startup-audit','own-entry','ui-startup-native','login-frame-native','character-draw-build','renderer-owner-build']
    report=dict(status='PARTIAL',scope=ref['scope'],script=record(Path(__file__)),normal_link_sha256=link_hash,normal_executable=link['executable'],
        fresh_evidence={name:record(WS/f'inventory/client455-{name}.json') for name in names},prior_runtime=ref['runtime_base'],
        ordinary_lifecycle_calls=calls,ordinary_source_lifecycle_connected=True,lifecycle_execution_in_Login_observed=False,
        actual_materials=4,actual_GPU_textures=4,actual_model_overlay_draws=result['actual_overlay_geometry_draws'],controlled_pose=True,
        visible_model_pixels=result['visible_model_pixels'],changed_overlay_pixels=result['changed_overlay_pixels'],frame=native['frame'],baseline_frame=native['baseline_frame'],
        ordinary_Create=True,ordinary_Login_frame=login['captured_frame'],ordinary_Login_capture=login['capture_result'],known_first_chance_exceptions=len(login['exceptions']),unhandled_exceptions=0,prior_exception_profile=record(previous_file),
        secondary_geometry_retained_in_normal_PE='RF455_DrawCharacterOverlay455' in mapping,
        ordinary_player_connected=False,full_mesh_object_renderer=False,full_appearance_or_selection=False,full_client=False,
        gaps=ref['gaps'],input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-grade-overlay-checkpoint.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PARTIAL:real grade resources/secondary geometry/RGB contribution,source lifecycle/ordinary Create/Login verified;full mesh renderer/player/selection/M9 OPEN')
if __name__=='__main__':main()
