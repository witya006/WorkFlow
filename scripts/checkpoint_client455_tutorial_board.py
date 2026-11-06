"""Accept board control and actual modal consumers without claiming a full455 UI."""
import hashlib
import json
from pathlib import Path
from compare_client_binaries import WS,pe
from build_client455_x87_math import read_va
from client455_normal_link_evidence import validate_normal_link
from prepare_client455_normal import kernel_sources


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    def load(name):return json.loads((WS/f'inventory/{name}.json').read_text())
    def check(row):
        if sha(WS/row['file'])!=row['sha256']:raise ValueError('Changed board evidence:'+row['file'])
    reference=load('client455-tutorial-board-reference');native=load('client455-tutorial-board-native')
    if reference['script_sha256']!=sha(WS/'scripts/audit_client455_tutorial_board.py') or \
       native['script_sha256']!=sha(WS/'scripts/probe_client455_tutorial_board.py') or \
       native['reference_sha256']!=sha(WS/'inventory/client455-tutorial-board-reference.json'):
        raise ValueError('Stale board verification')
    if reference['script_reference_sha256']!=sha(WS/'inventory/client455-tutorial-scripts-reference.json'):
        raise ValueError('Changed script pin')
    for row in reference['raw_evidence']+reference['assemblies']:check(row)
    for row in reference['assemblies']:
        body=json.loads((WS/row['file']).read_text())
        if not body['cursor']['done'] or len(body['asm']['lines'])!=row['instructions']:
            raise ValueError('Incomplete board assembly')
    for folder,pin in zip(['current','reference-backup'],reference['references']):
        binary=WS/f'work/client-reference/{folder}/RF_Online.bin'
        if sha(binary)!=pin['sha256']:raise ValueError('Changed455pin')
        raw=binary.read_bytes()
        for row in pin['ranges']+pin['data']:
            if hashlib.sha256(read_va(raw,0x400000+int(row['rva'],16),row['bytes'])).hexdigest()!=row['sha256']:
                raise ValueError('Changed board contract')
    for row in reference['inputs']:
        if sha(Path(row['file']))!=row['sha256']:raise ValueError('Changed race/class script')
    for name,digest in native['sources'].items():
        if sha(WS/'scripts/native'/name)!=digest:raise ValueError('Changed board source:'+name)
    if native['normal_link_sha256']!=sha(WS/'inventory/client455-normal-link.json'):
        raise ValueError('Changed normal client inputs')
    validate_normal_link(load('client455-normal-link'))
    if native['processor_report_sha256']!=sha(WS/'inventory/client455-tutorial-actions-native.json'):
        raise ValueError('Changed QBI library evidence')
    action=load('client455-tutorial-actions-native')
    for name,digest in action['sources'].items():
        if sha(WS/'scripts/native'/name)!=digest:raise ValueError('Changed QBI dependency:'+name)
    for name in ['processor_library','exe','map','build_log','link_response','output','frame','preview']:check(native[name])
    for row in native['objects']+native['inputs']:check(row)
    if pe((WS/native['exe']['file']).read_bytes())['entry_rva']!=int(native['entry_rva'],16):
        raise ValueError('Wrong own board entry')
    actual=json.loads((WS/native['output']['file']).read_text())
    if actual!=native['native'] or actual['status']!='PASS' or native['natural_exit']:
        raise ValueError('Board native failed')
    for name in ['board_rules','real_modal2_and3','real_language441_and444','mbsnbcpy_and_bounds',
                 'key_guide_rows','quit_and_finish_order','report_clock_wrap']:
        if not actual[name]:raise ValueError('Missing board observation:'+name)
    if actual['race_class_programs_prepared']!=3 or actual['modal_colored_pixels']<=100:
        raise ValueError('Missing race/class or actual viewport rendering')
    frame=native['frame']
    if frame['width']!=640 or frame['height']!=480 or (WS/frame['file']).stat().st_size!=640*480*4:
        raise ValueError('Frame must contain just the actual640x480viewport')
    if not actual['rich_view_is_test_fixture'] or actual['production_host'] or \
       actual['full_briefing_window'] or actual['full_Tutorial'] or native['normal_client_relinked']:
        raise ValueError('Do not promote a partial board/legacy GUI bridge into455acceptance')
    kernels,_=kernel_sources(WS/'scripts/native')
    if len(kernels)!=20:raise ValueError('Canonical source discovery changed')
    report={'status':'PARTIAL','board_control_rules':'PASS','real_modal_GUI_bridge_and_D3D':'PASS',
            'modal_sprite_mapping_455':'OPEN','full_CGUIBriefingWindow':'OPEN','production_host':'OPEN',
            'full_Tutorial':'OPEN','evidence_sha256':{name:sha(WS/f'inventory/{name}.json') for name in
                ['client455-tutorial-board-reference','client455-tutorial-board-native']},
            'gaps':reference['gaps'],'input_exe_executed':False,'server_modified':False,
            'M6':'OPEN','M6F':'OPEN','M7':'OPEN','M9':'OPEN'}
    (WS/'inventory/client455-tutorial-board-checkpoint.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PARTIAL:board control/modal GUI bridge/D3D PASS;455sprites/rich UI/host/Tutorial/M9 OPEN')


if __name__=='__main__':main()
