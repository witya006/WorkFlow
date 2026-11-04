"""Validate normal caller integration,focused native checks andscoped graphics."""
import hashlib,json
from compare_client_binaries import WS

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(name):return json.loads((WS/f'inventory/{name}.json').read_text(encoding='utf-8'))
def main():
    build=load('client455-animation-timing-build');ref=load('client455-animation-timing-reference');cpu=load('client455-animation-timing-cpu');client=load('client455-animation-timing-client');link=load('client455-animation-timing-link');graphics=load('client455-animation-timing-graphics');coff=load('client-mt-variant')
    for name,digest in build['source_sha256'].items():
        if sha(WS/'scripts/native'/name)!=digest:raise ValueError('Changed timing source')
    if sha(WS/build['object'])!=build['object_sha256'] or sha(WS/ref['golden'])!=ref['golden_sha256'] or sha(WS/'scripts/audit_client455_animation_timing.py')!=ref['script_sha256']:raise ValueError('Changed timing object/oracle')
    for report in [cpu,client]:
        if sha(WS/report['exe'])!=report['exe_sha256'] or sha(WS/report['output'])!=report['output_sha256']:raise ValueError('Changed runtime evidence')
    if cpu['build_report_sha256']!=sha(WS/'inventory/client455-animation-timing-build.json') or cpu['reference_report_sha256']!=sha(WS/'inventory/client455-animation-timing-reference.json') or cpu['native']['failures'] or client['component']!=cpu['native'] or client['component_report_sha256']!=sha(WS/'inventory/client455-animation-timing-cpu.json'):raise ValueError('Stale native proof')
    if client['native']['actual_cases']!=16 or client['native']['failures'] or client['native']['dmalloc_balance'] or client['exe_sha256']!=link['lab']['exe_sha256'] or len(link['normal']['functions'])!=2 or len(link['lab']['functions'])!=3:raise ValueError('Actual caller selection/runtime mismatch')
    previous={case['case']:case for case in load('client455-animation-graphics')['cases']}
    for case in graphics['cases']:
        if case['failures'] or case['errors'] or case['warnings'] or case['allocation_before']!=case['allocation_after'] or case['device_refs_after_release'] or case['d3d_refs_after_release'] or case.get('frame_sha256')!=previous[case['case']].get('frame_sha256'):raise ValueError('Scoped graphics regression')
    if graphics['exe_sha256']!=link['lab']['exe_sha256'] or sum(r['objects_verified'] for r in coff['targets'])!=290 or load('client-helper-lab-build')['generated_objects']!=190:raise ValueError('Current PE/build manifest mismatch')
    normal=WS/load('client-first-build')['character455-animation-timing']['snapshot']/'RF_Online.bin'
    if sha(normal)!=link['normal']['exe_sha256']:raise ValueError('Changed normal snapshot')
    evidence=['client455-animation-timing-reference','client455-animation-timing-build','client455-animation-timing-cpu','client455-animation-timing-client','client455-animation-timing-link','client455-animation-timing-graphics','client-mt-variant','client-behavior-patches']
    report={'scope':'Normal sourceCAnimation ctor/CResObject frame numeric integration,not fullCharacter455 orM9','normal':link['normal'],'lab':{k:link['lab'][k] for k in ['architecture','exe_sha256','exe_bytes','entry_rva']},'native':cpu['native'],'actual_caller':client['native'],'scoped_graphics_checks':sum(c['checks'] for c in graphics['cases']),'previous_frame_hashes_equal':True,'normal_runtime_intentionally_changed':'CAnimationctor andtwo CResObject frame advance paths nowcall source455kernels','normal_modern_coff_objects':290,'lab_client_objects':190,'unchanged_bulk_suites_repeated':False,'evidence_sha256':{name:sha(WS/f'inventory/{name}.json') for name in evidence}}
    (WS/'inventory/client455-animation-timing-checkpoint.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('PASS:normal2APIs/3actualcallsites;612rational cases/16actual actor cases;Platform01-device69;290MTobjects')
if __name__=='__main__':main()
