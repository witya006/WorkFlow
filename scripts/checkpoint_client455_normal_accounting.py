"""Prove real cumulative process counters and source link without claiming M9."""
import hashlib,json,re
from compare_client_binaries import WS
from build_client455_x87_math import read_va
from audit_client455_effect_tables import loaded
from client455_normal_link_evidence import validate_normal_link

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def load(name):return json.loads((WS/f'inventory/{name}.json').read_text())
def main():
    ref=load('client455-normal-accounting-reference');cpu=load('client455-normal-accounting-native');gpu=load('client455-normal-renderer-gpu');link=load('client455-normal-link');prep=load('client455-normal-preparation');build=load('client455-normal-build')
    for folder,item in zip(['current','reference-backup'],ref['references']):
        path=WS/f'work/client-reference/{folder}/RF_Online.bin';raw=path.read_bytes()
        if sha(path)!=item['sha256']:raise ValueError('Changed455reference')
        for row in item['functions']:
            if hashlib.sha256(read_va(raw,0x400000+int(row['rva'],16),row['bytes'])).hexdigest()!=row['sha256']:raise ValueError('Changed accounting code')
        row=item['confirmed_initial_counters'];initial=loaded(raw,0x400000+int(row['rva'],16),row['bytes'])
        if any(initial) or hashlib.sha256(initial).hexdigest()!=row['sha256']:raise ValueError('Changed initial counters')
    if sha(WS/'scripts/audit_client455_normal_accounting.py')!=ref['script_sha256'] or sha(WS/ref['ani_fixture'])!=ref['ani_fixture_sha256']:raise ValueError('Stale reference audit')
    for name in ['Character455.h','client455_normal_facade.cpp','client455_normal_accounting.cpp','client455_normal_accounting.h']:
        if sha(WS/'scripts/native'/name)!=prep['record_inputs'][name]:raise ValueError('Changed process-counter source')
    if build['build_exit'] or build['objects']!=182 or build['canonical_kernel_objects']!=20:raise ValueError('Incomplete source build')
    for run in [cpu,gpu]:
        if run['normal_build_sha256']!=sha(WS/'inventory/client455-normal-build.json'):raise ValueError('Stale native build')
        for key,hashkey in [('exe','exe_sha256'),('source','source_sha256'),('output','output_sha256'),('map','map_sha256')]:
            if sha(WS/run[key])!=run[hashkey]:raise ValueError('Changed native evidence')
        for row in run['libraries']:
            if sha(WS/row['file'])!=row['sha256']:raise ValueError('Changed dependency')
        if run['native']['status']!='PASS':raise ValueError('Failed native scenario')
    if cpu['reference_sha256']!=sha(WS/'inventory/client455-normal-accounting-reference.json') or gpu['accounting_reference_sha256']!=cpu['reference_sha256'] or sha(WS/cpu['fixture']['file'])!=cpu['fixture']['sha256']:raise ValueError('Changed fixture/reference')
    n=cpu['native'];accounting=gpu['accounting'];g=accounting['native']
    if n['real_ani_bytes']!=ref['ani_bytes'] or n['renderer_owners']!=2 or n['snapshot_fields']!=7 or not all(n[key] for key in ['cumulative_after_release','cached_load_unchanged','dword_wrap','real_mesh_lifetime']):raise ValueError('Incomplete process ownership/wrap/lifetime checks')
    if sha(WS/accounting['file'])!=accounting['sha256'] or json.loads((WS/accounting['file']).read_text())!=g or g['status']!='PASS' or not all(g[key] for key in ['real_model_counters','cumulative_after_release','next_renderer_keeps_counters']):raise ValueError('Incomplete actual GPU counter check')
    if not all(g[key]>0 for key in ['mesh_count','mesh_bytes','buffer_count','buffer_bytes','texture_count','texture_bytes','ani_bytes']) or gpu['native']['device_refs'] or gpu['native']['dmalloc_balance'] or not gpu['precanonical_frames_equal']:raise ValueError('GPU counter/regression/cleanup failed')
    prior=load('client455-normal-accounting-prior-frames')
    if [row['sha256'] for row in gpu['frames']]!=prior['color'] or [row['sha256'] for row in gpu['effect_frames']]!=prior['effect'] or gpu['shadow_frame']['sha256']!=prior['shadow']:raise ValueError('Previous color/effect/shadow frames changed')
    for row in gpu['frames']+gpu['effect_frames']+[gpu['shadow_frame']]:
        if sha(WS/row['file'])!=row['sha256']:raise ValueError('Changed actual frame file')
    consumer=WS/'work/client455-port/normal/source/addcodebyjang/foreffect.cpp';raw=consumer.read_bytes()
    if b'g_ChMemoryInfo' in raw or raw.count(b'characterMemoryInfo.')!=8 or raw.count(b'RF455_GetCharacterMemoryInfo()')!=1:raise ValueError('Unported memory display consumer')
    caller=WS/'work/client455-port/normal/build/RFClient455Consumers.dir/Release/foreffect.obj'
    if b'?RF455_GetCharacterMemoryInfo@@' not in caller.read_bytes():raise ValueError('Missing actual display call')
    if validate_normal_link(link)!='PASS':raise ValueError('Full normal source link still open')
    mapping=(WS/link['map']['file']).read_text(errors='replace')
    for symbol in ['?RF455_GetCharacterMemoryInfo@@','_RF455_GetNormalCharacterAccounting']:
        if not re.search(re.escape(symbol)+r'[^\r\n]+RFClient455Facade:client455_normal_accounting\.obj',mapping):raise ValueError('Wrong actual accounting provider')
    names=['client455-normal-accounting-reference','client455-normal-accounting-native','client455-normal-accounting-prior-frames','client455-normal-renderer-gpu','client455-normal-preparation','client455-normal-build','client455-normal-link']
    report={'status':'PARTIAL','confirmed_counter_fields':7,'source_process_accounting':'PASS','real_ani_multiple_owners':'PASS','real_model_gpu_counters':'PASS','cumulative_after_release':'PASS','normal_display_source_call':'PASS','full_normal_executable_link':'PASS','remaining_unresolved':0,'gpu_counters':g,'executable':link['executable'],'consumer':{'file':consumer.relative_to(WS).as_posix(),'sha256':sha(consumer),'object':caller.relative_to(WS).as_posix(),'object_sha256':sha(caller)},'evidence_sha256':{name:sha(WS/f'inventory/{name}.json') for name in names},'gaps':ref['gaps']+['Successful source link is not normal WinMain/device-lifecycle or complete455behavior acceptance'],'input_exe_executed':False,'server_modified':False,'M6':'OPEN','M6F':'OPEN','M7':'OPEN','M9':'OPEN'}
    (WS/'inventory/client455-normal-accounting-checkpoint.json').write_text(json.dumps(report,indent=2)+'\n');print('PARTIAL:real process counters/ANI/GPU/normal source link PASS;M6/M9 OPEN')
if __name__=='__main__':main()
