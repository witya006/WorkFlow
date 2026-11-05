"""Check real normal renderer evidence while leaving complete455acceptance open."""
import hashlib,json,re
from compare_client_binaries import WS,pe
from build_client455_x87_math import read_va
from client455_d3d9_port import ENGINE_DEFINITIONS

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(name):return json.loads((WS/f'inventory/{name}.json').read_text())
def main():
    ref=load('client455-normal-renderer-reference');math=load('client455-normal-renderer-math');gpu=load('client455-normal-renderer-gpu');link=load('client455-normal-link');build=load('client455-normal-build')
    if build['build_exit'] or build['objects']!=182:raise ValueError('Incomplete normal build')
    if sha(WS/'scripts/audit_client455_normal_renderer.py')!=ref['script_sha256'] or sha(WS/'scripts/native/client455_normal_renderer_constants.h')!=ref['constants_header_sha256'] or sha(WS/ref['golden'])!=ref['golden_sha256']:raise ValueError('Changed wrapper oracle')
    for folder,record in zip(['current','reference-backup'],ref['references']):
        binary=WS/f'work/client-reference/{folder}/RF_Online.bin';raw=binary.read_bytes()
        if sha(binary)!=record['sha256']:raise ValueError('Changed455reference')
        for f in record['functions']:
            if hashlib.sha256(read_va(raw,int(f['rva'],16)+0x400000,f['bytes'])).hexdigest()!=f['sha256']:raise ValueError('Changed455body')
    for report in [math,gpu]:
        if report['normal_build_sha256']!=sha(WS/'inventory/client455-normal-build.json') or report['reference_sha256']!=sha(WS/'inventory/client455-normal-renderer-reference.json'):raise ValueError('Stale renderer evidence')
        exe=WS/report['exe'];raw=exe.read_bytes()
        if sha(exe)!=report['exe_sha256'] or pe(raw)['entry_rva']!=int(report['entry_rva'],16) or sha(WS/report['output'])!=report['output_sha256'] or sha(WS/report['source'])!=report['source_sha256'] or sha(WS/report['map'])!=report['map_sha256']:raise ValueError('Changed own renderer run')
        if report['native']['status']!='PASS' or report['legacy_character_linked']:raise ValueError('Incomplete renderer run')
        for item in report['libraries']:
            if sha(WS/item['file'])!=item['sha256']:raise ValueError('Changed renderer dependency')
        for item in report.get('extra_sources',[]):
            if sha(WS/item['file'])!=item['sha256']:raise ValueError('Changed additional native probe source')
    if not set(ENGINE_DEFINITIONS)<=set(gpu['definitions']):raise ValueError('Wrong engine state layout in probe')
    if not gpu['precanonical_frames_equal'] or gpu['precanonical_report_sha256']!=sha(WS/'inventory/client455-normal-renderer-precanonical.json'):raise ValueError('Canonical rebuild equivalence unproven')
    if not any(p['file'].endswith('/RFClient455Kernels.lib') for p in gpu['libraries']) or any('/work/recovered/client455/' in '/'+p['file'] and p['file'].endswith('.lib') and 'x87-math' not in p['file'] for p in gpu['libraries']):raise ValueError('Normal path uses old separately compiled storage definitions')
    n=math['native'];g=gpu['native']
    if [n['angle_cases'],n['box_cases'],n['fp_modes']]!=[96,60,12] or not g['normal_unity_model_pipeline'] or [g['animated_frames'],g['matrix_wrapper_equal_frames'],g['geometry_parts'],g['filter_cases']]!=[2,2,46,3] or g['device_refs'] or g['dmalloc_balance'] or g['game_dlls_loaded'] or not g['alpha_material_checked']:raise ValueError('Incomplete changed contracts')
    if not all(g.get(name) for name in ['real_animation_reset_reattach','real_mesh_rematch','texture_path_method']):raise ValueError('Real model contracts not exercised')
    if not g.get('shadow_capture') or g.get('shadow_target_passes')!=3 or not g.get('real_model_shadow') or g.get('shadow_begin_success_return')!=0:raise ValueError('Shadow target scenarios missing')
    if len(gpu['frames'])!=2 or gpu['frames'][0]['sha256']==gpu['frames'][1]['sha256']:raise ValueError('No animation change')
    for frame in gpu['frames']:
        if sha(WS/frame['file'])!=frame['sha256'] or sha(WS/frame['preview'])!=frame['preview_sha256']:raise ValueError('Changed rendered frame')
    mapping=(WS/gpu['map']).read_text(errors='replace')
    for name in ['DrawCharacter@CRender','FrameMove@CRender','LoadMeshData@ChInterface','IsLoadAnimation@ChInterface']:
        if not re.search(re.escape(name)+r'[^\r\n]+RFClient455Facade:client455_normal_facade\.obj',mapping):raise ValueError('Normal facade provider absent:'+name)
        if any(name in r['symbol'] for r in link['unresolved']):raise ValueError('Normal method still unresolved')
    from client455_normal_link_evidence import validate_normal_link
    link_state=validate_normal_link(link)
    names=['client455-normal-build','client455-normal-consumers','client455-normal-link','client455-normal-renderer-reference','client455-normal-renderer-math','client455-normal-renderer-gpu']
    report={'status':'PARTIAL','normal_model_pose_draw':'PASS','world_and_matrix_wrappers_equal':True,'visibility_alpha_material_state':'PASS','full_normal_executable_link':'OPEN','unresolved_symbols':link['unique_unresolved'],'evidence_sha256':{n:sha(WS/f'inventory/{n}.json') for n in names},'gaps':['Remaining named methods/data:effects/reset/parent/bounds/shadow-target/time/texture-path','Original staticCRT trig/profiling andallFP-special/failure policies notcertified','Renderer blendDuration constructor bytes unwritten;normal initialization remainsunproven;test explicitlysets150','Batch/orthographic/device-reset/fullscreen/fullnormal shutdown/gameplay/UI/network acceptance open','No original455gameframe parity;owncamera/renderedfixture evidence only'],'legacy_character_linked':False,'input_exe_executed':False,'server_modified':False,'M6':'OPEN','M6F':'OPEN','M7':'OPEN','M9':'OPEN'}
    report['canonical_kernel_objects']=build['canonical_kernel_objects'];report['precanonical_frames_equal']=True
    report['full_normal_executable_link']=link_state
    report['gaps'][0]='Ground shadow projection/normal BOOLcaller behavior and full effect/actor lifecycle still open'
    (WS/'inventory/client455-normal-renderer-checkpoint.json').write_text(json.dumps(report,indent=2)+'\n');print('PARTIAL:actual normalCUnity/model/pose/draw/2frames PASS;fullRF_Online link '+link_state+';M6/M9 OPEN')
if __name__=='__main__':main()
