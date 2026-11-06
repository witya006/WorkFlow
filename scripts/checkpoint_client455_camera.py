"""Bind realcamera read/play/projection evidence;full455/Tutorial remainsopen."""
import hashlib,json,re
from pathlib import Path
from compare_client_binaries import WS
from build_client455_x87_math import read_va
from client455_normal_link_evidence import validate_normal_link

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def load(name):return json.loads((WS/f'inventory/{name}.json').read_text())
def check(row):
    if sha(WS/row['file'])!=row['sha256']:raise ValueError('Changed camera artifact:'+row['file'])
def main():
    ref=load('client455-camera-reference');native=load('client455-camera-native');prep=load('client455-normal-preparation');engine=load('client455-startup-engine-build');link=load('client455-normal-link');validate_normal_link(link)
    for report,script in [(ref,'audit_client455_camera.py'),(native,'probe_client455_camera.py')]:
        if report['script_sha256']!=sha(WS/'scripts'/script):raise ValueError('Stale camera producer')
    for folder,row in zip(['current','reference-backup'],ref['references']):
        path=WS/f'work/client-reference/{folder}/RF_Online.bin';raw=path.read_bytes()
        if sha(path)!=row['sha256']:raise ValueError('Changed455pin')
        for body in row['ranges']:
            if hashlib.sha256(read_va(raw,0x400000+int(body['rva'],16),body['bytes'])).hexdigest()!=body['sha256']:raise ValueError('Changed455camera body')
    for name in ['raw_evidence','playback_asm']:check(ref[name])
    for row in ref['inputs']:
        if sha(Path(row['file']))!=row['sha256'] or not row['layout']['roundtrip_equal']:raise ValueError('Changed sourcecamera input')
    if native['source_sha256']!=sha(WS/native['source']) or native['normal_link_sha256']!=sha(WS/'inventory/client455-normal-link.json') or native['reference_sha256']!=sha(WS/'inventory/client455-camera-reference.json') or native['builder_sha256']!=sha(WS/'scripts/client455_own_probe.py') or native['engine_build_sha256']!=sha(WS/'inventory/client455-startup-engine-build.json'):raise ValueError('Stale ordinary camera native evidence')
    for name,digest in native['sources'].items():
        if sha(WS/'scripts/native'/name)!=digest or prep['record_inputs'][name]!=digest:raise ValueError('Changed camera implementation')
    for name,digest in engine['camera'].items():
        if native['sources'][name]!=digest:raise ValueError('Derived engine camera mismatch')
    for key in ['exe','map','output']:check(native[key])
    for row in native['inputs']+native['roundtrip_outputs']:check(row)
    n=native['native']
    if native['natural_exit'] or n['status']!='PASS' or n['files']!=5 or n['cameras']!=51 or n['dummies']!=42 or n['fullTutorial']:raise ValueError('Wrong camera runtime scope')
    if not all(n[key] for key in ['wire_roundtrip','actual_camera_materialization','actual_play_projection','actual_release_balance','synthetic13_fov','playback_clock_and_boundaries','bounded_truncation']):raise ValueError('Missing actual camera behavior')
    mapping=(WS/link['map']['file']).read_text()
    for symbol,provider in [('LoadAniCamera@CAniCamera','R3Engine455Startup:anicamera.obj'),('PlayAniCamera@CAniCamera','R3Engine455Startup:anicamera.obj'),('RF455_AdvanceCamera','RFClient455Facade:client455_camera.obj'),('RF455_LoadCameraFile','RFClient455Facade:client455_camera.obj')]:
        if not re.search(re.escape(symbol)+r'[^\r\n]+'+re.escape(provider),mapping,re.I):raise ValueError('Missing ordinary camera provider:'+symbol)
    ui=load('client455-ui-startup-native')
    if ui['normal_link_sha256']!=native['normal_link_sha256'] or not ui['completed_existing_client_create'] or ui['markers'][-1]['eax']!=1:raise ValueError('Current existingCreate regression required')
    report={'status':'PARTIAL','real_CAM12_load_and_typed_materialization':'PASS','CAM13_synthetic_and_FOV_keys':'PASS','raw_roundtrip_four_real_files':'PASS','ordinary_playback_and_GPU_projection':'PASS','clock_boundaries_and_release_balance':'PASS','actual_existing_Create':'PASS','fullTutorial':'OPEN','evidence_sha256':{name:sha(WS/f'inventory/{name}.json') for name in ['client455-camera-reference','client455-camera-native','client455-normal-link','client455-startup-engine-build','client455-ui-startup-native']},'gaps':ref['gaps'],'input_exe_executed':False,'server_modified':False,'M6':'OPEN','M6F':'OPEN','M7':'OPEN','M9':'OPEN'}
    (WS/'inventory/client455-camera-checkpoint.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('PARTIAL:ordinaryCAM1.2/1.3/load/play/projection/release PASS;fullTutorial/cameraparity/M9 OPEN')
if __name__=='__main__':main()
