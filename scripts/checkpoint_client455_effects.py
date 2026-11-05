"""Validate restored EFF source/data/texture path without claiming client closure."""
import hashlib,json,re
from compare_client_binaries import WS,pe
from build_client455_x87_math import read_va

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def load(name):return json.loads((WS/f'inventory/{name}.json').read_text())
def main():
    ref=load('client455-effects-reference');cpu=load('client455-effects-native');gpu=load('client455-normal-renderer-gpu');link=load('client455-normal-link');prep=load('client455-normal-preparation');build=load('client455-normal-build')
    for folder,record in zip(['current','reference-backup'],ref['references']):
        raw=(WS/f'work/client-reference/{folder}/RF_Online.bin').read_bytes()
        if hashlib.sha256(raw).hexdigest()!=record['sha256']:raise ValueError('Changed455reference')
        for row in record['functions']+record['particle_fragments']:
            if hashlib.sha256(read_va(raw,int(row['rva'],16)+0x400000,row['bytes'])).hexdigest()!=row['sha256']:raise ValueError('Changed EFF/consumer body')
        for row in ref['constants']:
            if hashlib.sha256(read_va(raw,int(row['rva'],16)+0x400000,row['bytes'])).hexdigest()!=row['sha256']:raise ValueError('Changed factor literal')
    if ref['unparsed_files'] or sha(WS/'scripts/audit_client455_effects.py')!=ref['script_sha256'] or sha(WS/'scripts/native/client455_effect_constants.h')!=ref['constants_header_sha256']:raise ValueError('Incomplete format oracle')
    if sha(WS/ref['fixture'])!=ref['fixture_sha256'] or sha(WS/ref['factor_golden'])!=ref['factor_golden_sha256']:raise ValueError('Changed EFF input/oracle')
    for row in ref['files']:
        if sha(WS/row['copy'])!=row['sha256']:raise ValueError('Changed actual EFF sample')
    for name in ['Character455.h','client455_normal_mesh.inc','client455_effects.cpp','client455_effects.h','client455_effect_constants.h','client455_normal_effects.cpp']:
        if sha(WS/'scripts/native'/name)!=prep['record_inputs'][name]:raise ValueError('Changed normal EFF source')
    if build['build_exit'] or build['objects']!=182 or build['canonical_kernel_objects']!=20:raise ValueError('Incomplete normal compilation')
    for report in [cpu,gpu,link]:
        if report['normal_build_sha256']!=sha(WS/'inventory/client455-normal-build.json'):raise ValueError('Stale normal build evidence')
        for item in report['libraries']:
            if sha(WS/item['file'])!=item['sha256']:raise ValueError('Changed linked dependency')
    for report in [cpu,gpu]:
        if sha(WS/report['exe'])!=report['exe_sha256'] or pe((WS/report['exe']).read_bytes())['entry_rva']!=int(report['entry_rva'],16) or sha(WS/report['output'])!=report['output_sha256'] or sha(WS/report['map'])!=report['map_sha256'] or sha(WS/report['source'])!=report['source_sha256']:raise ValueError('Changed native evidence')
        if report['native']['status']!='PASS':raise ValueError('Failed EFF scenario')
    if cpu['reference_sha256']!=sha(WS/'inventory/client455-effects-reference.json') or gpu['effects_reference_sha256']!=cpu['reference_sha256']:raise ValueError('Stale EFF references')
    n=cpu['native'];g=gpu['native']
    if n['real_files']!=len(ref['files']) or n['real_records']!=sum(row['records'] for row in ref['files']) or not n['lossless_roundtrip'] or [n['factor_cases'],n['fp_modes']]!=[132,12] or not all(n[name] for name in ['registry_filter_slots','file_lists','normal_facade']):raise ValueError('Incomplete source EFF cases')
    for row in gpu['extra_sources']:
        if sha(WS/row['file'])!=row['sha256']:raise ValueError('Changed GPU source')
    source='scripts/native/test_client455_effects_gpu.cpp'
    if {'file':source,'sha256':sha(WS/source)} not in gpu['extra_sources']:raise ValueError('Real EFF GPU integration absent')
    if g['device_refs'] or g['dmalloc_balance'] or g['game_dlls_loaded'] or not gpu['precanonical_frames_equal']:raise ValueError('Renderer regression/cleanup failure')
    for row in gpu['effect_inputs']:
        if sha(WS/row['file'])!=row['sha256']:raise ValueError('Changed actual GPU EFF/texture input')
    if len(gpu['effect_inputs'])!=6 or len(gpu['effect_frames'])!=2:raise ValueError('Incomplete effect experiment')
    frames=[]
    for row in gpu['effect_frames']:
        raw=(WS/row['file']).read_bytes()
        if len(raw)!=256*256*4 or sha(WS/row['file'])!=row['sha256'] or sha(WS/row['preview'])!=row['preview_sha256']:raise ValueError('Changed EFF frame')
        frames.append(raw)
    changed=sum(frames[0][i:i+4]!=frames[1][i:i+4] for i in range(0,len(frames[0]),4))
    if changed<=100:raise ValueError('No visible effect change')
    # /OPT:REF omits entitySlot from the GPU entry; its actual consumer is the
    # CPU slot scenario. Validate providers across both already-verified MAPs.
    mapping='\n'.join((WS/report['map']).read_text(errors='replace') for report in [cpu,gpu])
    for symbol in ['InitEffect@CRender','SetEffect@EffectList','SetPartEffect@EffectObjectManager','LoadEffectFileList@EffectList','LoadEffectFileList@EffectFileList','IsHaveEffect@RF455CharacterStorage','SetMeshEffect','particleSlots@RF455MeshStorage','entitySlot@RF455MeshStorage','LoadEffect@EffectObjectManager','g_EFFMonList','g_EFFUnitList','g_EffectFileList']:
        if not re.search(re.escape(symbol)+r'[^\r\n]+RFClient455Facade:client455_normal_effects\.obj',mapping):raise ValueError('Wrong EFF provider:'+symbol)
        if any(symbol in row['symbol'] for row in link['unresolved']):raise ValueError('Still unresolved EFF contract')
    from client455_normal_link_evidence import validate_normal_link
    link_state=validate_normal_link(link)
    names=['client455-effects-reference','client455-effects-native','client455-normal-renderer-gpu','client455-normal-build','client455-normal-preparation','client455-normal-link']
    report={'status':'PARTIAL','source_eff_read_apply_reset_slots':'PASS','real_texture_model_draw':'PASS','actual_effect_changed_pixels':changed,'real_sample_files':n['real_files'],'real_sample_records':n['real_records'],'format_inventory_records':ref['valid_real_files_records'],
        'full_normal_link':'OPEN','remaining_unresolved':link['unique_unresolved'],'evidence_sha256':{name:sha(WS/f'inventory/{name}.json') for name in names},'gaps':ref['gaps']+['Remaining client contracts in normal-link.json;normal gameplay/UI/network acceptance open'],
        'input_exe_executed':False,'server_modified':False,'M6':'OPEN','M6F':'OPEN','M7':'OPEN','M9':'OPEN'}
    report['full_normal_link']=link_state
    (WS/'inventory/client455-effects-checkpoint.json').write_text(json.dumps(report,indent=2)+'\n');print('PARTIAL:source EFF/real texture/model GPU PASS;full link '+link_state+';M9OPEN')
if __name__=='__main__':main()
