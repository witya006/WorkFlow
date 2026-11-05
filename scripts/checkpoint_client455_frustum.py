"""Record source frustum integrated into real callers without closing M6/M9."""
import hashlib,json
from pathlib import Path
from compare_client_binaries import WS

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(name):return json.loads((WS/f'inventory/{name}.json').read_text(encoding='utf-8'))
def main():
    ref=load('client455-frustum-reference');build=load('client455-frustum-build');client=load('client455-frustum-client');link=load('client455-frustum-link');api=load('client455-normal-character-api');mt=load('client-mt-variant');graphics=load('client455-frustum-graphics')
    if sha(WS/ref['golden'])!=ref['golden_sha256'] or sha(WS/'scripts/audit_client455_frustum.py')!=ref['script_sha256'] or build['reference_report_sha256']!=sha(WS/'inventory/client455-frustum-reference.json'):raise ValueError('Stale frustum oracle')
    for name,digest in build['source_sha256'].items():
        if sha(WS/'scripts/native'/name)!=digest:raise ValueError('Changed frustum source')
    for report in [build,client]:
        if sha(WS/report['exe'])!=report['exe_sha256'] or sha(WS/report['output'])!=report['output_sha256'] or report['native']['status']!='PASS' or report['native']['failures']:raise ValueError('Changed/incomplete runtime proof')
    if sha(WS/client['numeric_output'])!=client['numeric_output_sha256'] or client['link_report_sha256']!=sha(WS/'inventory/client455-frustum-link.json') or client['exe_sha256']!=link['lab']['exe_sha256'] or client['native']['actor_cases']!=9 or client['native']['dmalloc_balance']:raise ValueError('Actual actor evidence mismatch')
    numeric=dict(build['native']);numeric['checks']-=ref['matrix_cases'];numeric['actual_publisher']=True
    if client['numeric']!=numeric:raise ValueError('Actual publisher does not match independent numeric cases')
    normal=WS/'work/client-build/build-character-diagnostic/Release/RF_Online.bin'
    if sha(normal)!=link['normal']['exe_sha256'] or sha(normal)!=api['exe_sha256'] or api['reference_status'].get('linked_location_target_unproven',0):raise ValueError('Current normal source/call audit stale')
    if api['client_objects']!=180 or api['engine_objects']!=67 or sum(r['objects_verified'] for r in mt['targets'])!=293:raise ValueError('Incomplete normal compiler artifact audit')
    dll=Path('C:/Windows/SysWOW64/d3dx9_36.dll')
    if sha(dll)!=ref['provider_sha256']:raise ValueError('Changed math runtime')
    previous={r['case']:r for r in load('client455-loop-clock-graphics')['cases']}
    if graphics['exe_sha256']!=client['exe_sha256']:raise ValueError('Graphics regression used another build')
    for case in graphics['cases']:
        if case['failures'] or case['errors'] or case['warnings'] or case['allocation_before']!=case['allocation_after'] or case['device_refs_after_release'] or case['d3d_refs_after_release'] or case.get('frame_sha256')!=previous[case['case']].get('frame_sha256'):raise ValueError('Scoped device/Platform01 regression failed')
    names=['client455-frustum-reference','client455-frustum-build','client455-frustum-link','client455-frustum-client','client455-frustum-graphics','client455-normal-character-api','client-mt-variant']
    report={'status':'PASS','scope':'Scene-frustum producer/AABB source math integrated into actual normal SetCharacterClipping/CResObject callers;M6/M6F/M7/M9 remain OPEN','normal':link['normal'],'lab':link['lab'],'numeric_cases':{'matrix':ref['matrix_cases'],'bbox':ref['bbox_cases'],'fp_modes':12},'actor_cases':9,'normal_api':{'named_calls':api['linked_direct_calls'],'distinct_symbols':api['linked_distinct_symbols'],'legacy_sdk_functions':39,'candidate_fields':api['field_candidate_count']},'evidence_sha256':{n:sha(WS/f'inventory/{n}.json') for n in names},'not_accepted':['Normal typed model/animation/Character455 layout and full D3D9 renderer','High-level camera/visibility/actor lifecycle and full455runtime equivalence','CRT matherr/errno/unmasked exceptions and nonfinite normalization payloads','Deployment failure policy:missing math runtime abort differs fromoriginal mandatory import failure'],'input_exe_executed':False,'server_modified':False}
    (WS/'inventory/client455-frustum-checkpoint.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('PASS:sourcefrustum inactualnormal callers/9actorcases;M6/M9 OPEN')
if __name__=='__main__':main()
