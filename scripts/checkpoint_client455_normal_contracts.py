"""Verify five recovered normal contracts without claiming a finished client."""
import hashlib,json,re
from compare_client_binaries import WS,pe
from build_client455_x87_math import read_va

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def load(name):return json.loads((WS/f'inventory/{name}.json').read_text())
def main():
    ref=load('client455-normal-contracts-reference');prep=load('client455-normal-preparation')
    run=load('client455-normal-consumers');gpu=load('client455-normal-renderer-gpu');link=load('client455-normal-link');build=load('client455-normal-build')
    for folder,record in zip(['current','reference-backup'],ref['references']):
        raw=(WS/f'work/client-reference/{folder}/RF_Online.bin').read_bytes()
        if hashlib.sha256(raw).hexdigest()!=record['sha256']:raise ValueError('Changed reference')
        for row in record['functions']:
            if hashlib.sha256(read_va(raw,int(row['rva'],16)+0x400000,row['bytes'])).hexdigest()!=row['sha256']:raise ValueError('Changed contract body/caller')
    if sha(WS/'scripts/audit_client455_normal_contracts.py')!=ref['script_sha256'] or run['contracts_reference_sha256']!=sha(WS/'inventory/client455-normal-contracts-reference.json'):raise ValueError('Stale contract references')
    if prep['record_inputs']['client455_normal_contracts.cpp']!=sha(WS/'scripts/native/client455_normal_contracts.cpp'):raise ValueError('Changed contract source')
    for report in [run,gpu,link]:
        if report['normal_build_sha256']!=sha(WS/'inventory/client455-normal-build.json'):raise ValueError('Stale build evidence')
        for item in report['libraries']:
            if sha(WS/item['file'])!=item['sha256']:raise ValueError('Changed library')
    for report in [run,gpu]:
        raw=(WS/report['exe']).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=report['exe_sha256'] or pe(raw)['entry_rva']!=int(report['entry_rva'],16) or sha(WS/report['output'])!=report['output_sha256'] or sha(WS/report['map'])!=report['map_sha256']:raise ValueError('Changed own executable/results')
        if report['native']['status']!='PASS' or report['native']['game_dlls_loaded']:raise ValueError('Failed own contracts probe')
    if sha(WS/'scripts/native/client455_normal_consumers_probe.cpp')!=run['source_sha256'] or sha(WS/'scripts/native/client455_normal_renderer_probe.cpp')!=gpu['source_sha256']:raise ValueError('Changed native probe')
    if build['build_exit'] or build['objects']!=182 or build['canonical_kernel_objects']!=20:raise ValueError('Incomplete normal source build')
    if run['native']['model_contract_groups']!=5 or not run['native']['real_bbx_loaded'] or sha(WS/run['bbx_fixture']['copy'])!=run['bbx_fixture']['sha256']:raise ValueError('Missing model/BBX scenarios')
    mapping=(WS/run['map']).read_text(errors='replace')
    methods=['AnimationReset','RematchParent','SetEyeVec','SetTexPath','ImportBoundBox']
    for method in methods:
        if not re.search(r'\?'+method+r'@ChInterface[^\r\n]+RFClient455Facade:client455_normal_contracts\.obj',mapping):raise ValueError('Wrong method provider:'+method)
        if any(method in row['symbol'] for row in link['unresolved']):raise ValueError('Still unresolved:'+method)
    g=gpu['native']
    if not all(g.get(k) for k in ['real_animation_reset_reattach','real_mesh_rematch','texture_path_method']) or not gpu['precanonical_frames_equal'] or g['device_refs'] or g['dmalloc_balance']:raise ValueError('Actual model path/cleanup not verified')
    if not link['link_exit'] or link['other_errors'] or not link['unresolved'] or link['legacy_character_linked'] or link['unresolved_forced']:raise ValueError('Unexpected full link state:inspect before acceptance')
    names=['client455-normal-preparation','client455-normal-build','client455-normal-consumers','client455-normal-renderer-gpu','client455-normal-link','client455-normal-contracts-reference']
    report={'status':'PARTIAL','restored_methods':methods,'contract_scenarios':'PASS','real_model_reset_reattach_rematch':'PASS','previous_two_frames_equal':True,
        'normal_client_objects':182,'canonical_kernel_objects':20,'full_normal_link':'OPEN','remaining_unresolved':link['unique_unresolved'],
        'evidence_sha256':{n:sha(WS/f'inventory/{n}.json') for n in names},'gaps':ref['bounds']+['Effects/particle slots/accounting/Character clock still unresolved;see current normal-link.json','Full normal WinMain,gameplay,UI,network and455behavioral acceptance remain open'],
        'input_exe_executed':False,'server_modified':False,'M6':'OPEN','M6F':'OPEN','M7':'OPEN','M9':'OPEN'}
    (WS/'inventory/client455-normal-contracts-checkpoint.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PARTIAL:five normal model contracts/real reset+rematch PASS;full link'+str(link['unique_unresolved'])+'unresolved;M6/M9OPEN')
if __name__=='__main__':main()
