"""Record the integrated elapsed clock with only relevant regression evidence."""
import hashlib,json
from compare_client_binaries import WS
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(name):return json.loads((WS/f'inventory/{name}.json').read_text(encoding='utf-8'))
def main():
    ref=load('client455-loop-clock-reference');build=load('client455-loop-clock-build');cpu=load('client455-loop-clock-cpu');client=load('client455-loop-clock-client');link=load('client455-loop-clock-link');graphics=load('client455-loop-clock-graphics')
    for name,digest in build['source_sha256'].items():
        if sha(WS/'scripts/native'/name)!=digest:raise ValueError('Changed loop source')
    if sha(WS/ref['golden'])!=ref['golden_sha256'] or sha(WS/'scripts/audit_client455_loop_clock.py')!=ref['script_sha256'] or sha(WS/build['object'])!=build['object_sha256']:raise ValueError('Changed loop oracle/object')
    if cpu['build_report_sha256']!=sha(WS/'inventory/client455-loop-clock-build.json') or cpu['reference_report_sha256']!=sha(WS/'inventory/client455-loop-clock-reference.json') or cpu['native']['failures'] or client['component_report_sha256']!=sha(WS/'inventory/client455-loop-clock-cpu.json'):raise ValueError('Stale loop proof')
    for report in [cpu,client]:
        if sha(WS/report['exe'])!=report['exe_sha256'] or sha(WS/report['output'])!=report['output_sha256']:raise ValueError('Changed runtime proof')
    if sha(WS/client['states_output'])!=client['states_output_sha256'] or client['states']!={**cpu['native'],'actual_engine_bridge':True} or client['native']['failures'] or client['native']['frame']!=309 or client['native']['dmalloc_balance'] or client['exe_sha256']!=link['lab']['exe_sha256']:raise ValueError('Actual bridge/frame mismatch')
    previous={c['case']:c for c in load('client455-animation-timing-graphics')['cases']}
    for case in graphics['cases']:
        if case['failures'] or case['errors'] or case['warnings'] or case['allocation_before']!=case['allocation_after'] or case['device_refs_after_release'] or case['d3d_refs_after_release'] or case.get('frame_sha256')!=previous[case['case']].get('frame_sha256'):raise ValueError('Scoped graphics regression')
    if graphics['exe_sha256']!=link['lab']['exe_sha256'] or sum(r['objects_verified'] for r in load('client-mt-variant')['targets'])!=291 or load('client-helper-lab-build')['generated_objects']!=191:raise ValueError('Build identity mismatch')
    snapshot=WS/load('client-first-build')['character455-loop-clock-final']['snapshot']/'RF_Online.bin'
    if sha(snapshot)!=link['normal']['exe_sha256']:raise ValueError('Changed normal snapshot')
    evidence=['client455-loop-clock-reference','client455-loop-clock-build','client455-loop-clock-cpu','client455-loop-clock-client','client455-loop-clock-link','client455-loop-clock-graphics','client-mt-variant','client-behavior-patches']
    report={'scope':'Recovered elapsed loop clock integrated into normal engine and actual frame producer;not full client455/M9 acceptance','normal':link['normal'],'lab':{k:link['lab'][k] for k in ['architecture','exe_sha256','exe_bytes','entry_rva']},'component':cpu['native'],'actual_engine':client['states'],'connected_actor':client['native'],'scoped_graphics_checks':sum(c['checks'] for c in graphics['cases']),'previous_frame_hashes_equal':True,'normal_runtime_intentionally_changed':True,'normal_modern_coff_objects':291,'lab_client_objects':191,'unchanged_bulk_suites_repeated':False,'remaining':['RTMovie0x0B normal event consumer','Full actor/normal455CharacterABI/AnimationManager-worker/skin-draw/shaders/D3D9renderer','No independent original process timer trace/unmasked FP exception equivalence'],'evidence_sha256':{name:sha(WS/f'inventory/{name}.json') for name in evidence}}
    (WS/'inventory/client455-loop-clock-checkpoint.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('PASS:actual elapsed clock/144states/3provider paths/frame309/Platform01-device69;291MTobjects')
if __name__=='__main__':main()
