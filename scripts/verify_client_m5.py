"""Evidence gate for M5's first helper-data slice, never M6F/M9 acceptance."""
import hashlib
import json
import argparse
from compare_client_binaries import WS


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def read(name):return json.loads((WS/name).read_text(encoding='utf-8'))


def main():
    cli=argparse.ArgumentParser();cli.add_argument('--saved',action='store_true',help='Validate preserved M5 checkpoint after later source/build changes');args=cli.parse_args()
    if args.saved:
        checkpoint=read('inventory/client-m5-checkpoint.json')
        root=WS/'artifacts/m5-checkpoint'/checkpoint['graphics_exe_sha256'][:16]
        if json.loads((root/'client-m5-checkpoint.json').read_text(encoding='utf-8'))!=checkpoint:raise ValueError('Preserved M5 checkpoint differs')
        for name,digest in checkpoint['evidence_sha256'].items():
            if sha(root/name.split('/')[-1])!=digest:raise ValueError('Preserved M5 report lost/changed:'+name)
        gpu=json.loads((root/'client455-graphics-runtime.json').read_text(encoding='utf-8'))
        if sha(WS/gpu['exe'])!=gpu['exe_sha256']:raise ValueError('Preserved graphics EXE lost/changed')
        for case in gpu['cases']:
            if sha(WS/case['frame'])!=case['frame_sha256']:raise ValueError('Preserved GPU frame changed')
        helper=json.loads((root/'client-helper-runtime.json').read_text(encoding='utf-8'))
        if sha(WS/helper['exe'])!=helper['exe_sha256']:raise ValueError('Preserved helper EXE changed')
        print('PASS:preserved M5 checkpoint/evidence/EXEs/GPU frames intact; this is historical evidence, not a new build regression.')
        return
    gpu=read('inventory/client455-graphics-runtime.json');build=read('inventory/client-helper-lab-build.json')
    if build['build_exit'] or gpu['exe_sha256']!=sha(WS/gpu['exe']):raise ValueError('Graphics executable missing/stale')
    if gpu['exe_sha256']!=sha(WS/'work/client-build/build-helper-lab/Release/RF_Online.bin'):raise ValueError('Graphics report is not current lab')
    for path,digest in gpu['graphics_source_sha256'].items():
        if sha(WS/path)!=digest:raise ValueError('Graphics source evidence stale')
    if len(gpu['cases'])!=13:raise ValueError('13graphics cases required')
    for case in gpu['cases']:
        if case['stage']!='complete' or case['exit_code'] or case['failures'] or case['warnings'] or case['errors']:raise ValueError(f'Graphics case incomplete:{case["case"]}')
        if case['allocation_after']!=case['allocation_before'] or case['device_refs_after_release'] or case['d3d_refs_after_release']:raise ValueError('Graphics ownership gap')
        if sha(WS/case['frame'])!=case['frame_sha256']:raise ValueError('GPU frame changed')
    lobby=next(c for c in gpu['cases'] if c['case']=='level-lobby')
    platform=next(c for c in gpu['cases'] if c['case']=='level-Platform01')
    if (lobby['level']['leaves'],lobby['level']['nodes'])!=(403,402):raise ValueError('Lobby map counts differ')
    p=platform['level']
    if (p['leaves'],p['nodes'],p['helpers'],p['interiors'],p['weather_counts'],p['weather_states'],p['weather_checks'])!=(14141,14140,23,8,[15,500],[[0,0],[1,1],[0,0]],6):raise ValueError('Normal helper/weather consumer scenario differs')
    helper=read('inventory/client-helper-runtime.json')
    if not helper['complete_real_sample_audit'] or helper['real_files']!=140 or helper['checks']!=2546931:raise ValueError('Full helper dataset evidence absent')
    if sha(WS/helper['exe'])!=helper['exe_sha256']:raise ValueError('Historical helper lab lost/changed')
    math=read('inventory/client455-x87-link.json')
    if math['lab']['sha256']!=gpu['exe_sha256']:raise ValueError('Current linked math check absent')
    if read('inventory/client455-weather-runtime.json')['exe_sha256']!=gpu['exe_sha256']:raise ValueError('Current weather regression absent')
    features=read('inventory/client-features.json')
    helper_features=[f for f in features['features'] if f['id'] in ['DATA-SPT-001','WORLD-HELPER-002']]
    if len(helper_features)!=2 or any(f['status']!='implemented' for f in helper_features):raise ValueError('Selected helper source missing')
    reports=['inventory/client-helper-runtime.json','inventory/client455-x87-link.json','inventory/client455-weather-helper.json',
             'inventory/client455-weather-runtime.json','inventory/client455-resource-reference.json','inventory/client455-resource-link.json',
             'inventory/client455-graphics-runtime.json','inventory/client455-graphics-reference.json']
    result={'milestone':'M5','status':'complete','scope':'First selected helper455data slice: loader, exact math and real interior/weather consumer through actual CLevel LoadLevel/FrameMove/GPU in own full-client entry.',
            'graphics_exe_sha256':gpu['exe_sha256'],'graphics_cases':13,'graphics_checks':sum(c['checks'] for c in gpu['cases']),
            'helper_dataset_checks':helper['checks'],'normal_maps':['lobby','Platform01'],
            'evidence_sha256':{name:sha(WS/name) for name in reports},
            'comparison':'Reference helper/consumer contracts statically inspected and byte-pinned in both PE; own source/natives verified. Two math kernels have instruction identity. Reference EXE not executed.',
            'not_closed':['M6/M6F/M7/M9','All particle/renderer/lighting/clock behavior and all other client acceptance areas',
                          'D3D8 legacy vs455D3D9, full Character sources/ABI, UI/network/sound/gameplay, canonical Release',
                          'Reference runtime FPU state, malformed/lifecycle/OOM domains beyond scoped checks']}
    (WS/'inventory/client-m5-checkpoint.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(f'PASS: M5 first helper slice complete:13GPU scenarios/{result["graphics_checks"]}checks, real interior/night states and preserved full helper dataset. M9 remains open.')


if __name__=='__main__':main()
