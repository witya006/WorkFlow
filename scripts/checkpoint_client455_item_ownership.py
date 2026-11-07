"""Accept selected ownership source foundation without claiming runtime binding."""
import hashlib
import json
import re
from pathlib import Path

from build_client455_x87_math import read_va
from checkpoint_client455_rvp_effects import check, load, require, sha
from client455_normal_link_evidence import validate_normal_link
from compare_client_binaries import WS, pe


def main():
    reference=load('client455-item-ownership-reference')
    require(reference['status']=='CONFIRMED_SELECTED' and reference['script_sha256']==sha(WS/'scripts/audit_client455_item_ownership.py'),
            'Stale reference')
    require(len(reference['references'])==2 and len(reference['assembly'])==14 and reference['actual_instructions']==579,'Reference coverage')
    for row in reference['raw_evidence']+reference['fixtures']:check(row)
    pins=json.loads((WS/'config/client-target.json').read_text())
    for folder,key,pin in zip(['current','reference-backup'],['behavior_reference','secondary_reference'],reference['references']):
        path=WS/f'work/client-reference/{folder}/RF_Online.bin';raw=path.read_bytes()
        require(sha(path)==pins[key]['sha256']==pin['sha256'] and pe(raw)['architecture']=='x86','Changed pin')
        require(len(pin['ranges'])==24,'Selected function coverage')
        for row in pin['ranges']:
            require(hashlib.sha256(read_va(raw,0x400000+int(row['rva'],16),row['bytes'])).hexdigest()==row['sha256'],'Changed selected body')
    session_path=WS/'artifacts/client455-progress/item-ownership087-session.json';session=json.loads(session_path.read_text())
    require(session['closed']['success'] and session['closed']['saved'] and session['after']['count']==0,'Owned IDA not saved/closed')
    native=load('client455-item-ownership-native')
    require(native['script_sha256']==sha(WS/'scripts/probe_client455_item_ownership.py') and
            native['reference_sha256']==sha(WS/'inventory/client455-item-ownership-reference.json') and
            native['builder_sha256']==sha(WS/'scripts/client455_own_probe.py'),'Stale ownership native evidence')
    for row in native['sources']+native['objects']+[native['build_log']]:check(row)
    require(sha(WS/native['library'])==native['library_sha256'],'Changed standalone library')
    require([r['mode'] for r in native['runs']]==['standalone','full_object'],'Missing execution mode')
    first=native['runs'][0]['native']
    fixture_hashes={Path(r['file']).name:r['sha256'] for r in reference['fixtures']}
    for run in native['runs']:
        for name in ['exe','map','console','output']:check(run[name])
        for row in run['inputs']:check(row)
        require({Path(r['file']).name:r['sha256'] for r in run['inputs']}==fixture_hashes,'Oracle copy drift')
        require(run['natural_exit']==0 and run['architecture']=='x86' and
                pe((WS/run['exe']['file']).read_bytes())['architecture']=='x86' and
                run['native']==first==json.loads((WS/run['output']['file']).read_text()),'Native execution drift')
        mapping=(WS/run['map']['file']).read_text()
        for symbol in ['RF455_InitializeItemHeader','RF455_CopyItemHeader','RF455_CopyBoardItemRecord',
                       'RF455_CloneBoardItemRecord','RF455_ReleaseBoardItemReference']:
            require(re.search(re.escape(symbol)+r'[^\r\n]*RF455ItemOwnership:item-ownership.obj',mapping),
                    'Separate-library source provider missing '+symbol)
    require(first['status']=='PASS' and first['item_record_bytes']==92 and first['wrapper_record_bytes']==620 and
            first['whole_record_oracles']==3 and first['lifetime_scenarios']==12 and first['ref_boundary_cases']==7,'Scenario coverage')
    for name in ['primary_empty_guard','signed_byte_release','shared_payload','independent_wrapper_state','allocation_failure','recording_host']:
        require(first[name],'Missing selected branch '+name)
    require(not first['ordinary_Linker_bound'] and not first['actual_item_factory'] and not first['real_item_destructors'] and
            not native['normal_client_relinked'] and not native['ordinary_Linker_changed'],'Unjustified runtime acceptance')
    # The production branch remains exactly086. Its bounded acceptance stays
    # current;do not refresh unrelated GPU/startup suites to inflate this unit.
    link=load('client455-normal-link');require(validate_normal_link(link)=='PASS','Current normal client drift')
    link_hash=sha(WS/'inventory/client455-normal-link.json');hotbar=load('client455-hotbar-checkpoint')
    require(native['normal_link_sha256']==hotbar['normal_link_sha256']==link_hash and
            link['executable']['sha256']=='82625b3ef5c237900146f65531a701a3451d3dbec292a65eef2ed5ece83df6f8','Production086 changed')
    for name,digest in hotbar['fresh_evidence'].items():
        require(sha(WS/'inventory'/(name+'.json'))==digest,'Changed086 acceptance evidence')
    report=dict(status='PARTIAL_SOURCE_FOUNDATION',scope='Selected record copy/clone/refcount/release kernels with recording ownership host;ordinary client086 unchanged',
        reference_sha256=sha(WS/'inventory/client455-item-ownership-reference.json'),
        native_sha256=sha(WS/'inventory/client455-item-ownership-native.json'),
        session=dict(file=session_path.relative_to(WS).as_posix(),sha256=sha(session_path)),
        source_sha256={Path(row['file']).name:row['sha256'] for row in native['sources'] if row['file'].startswith('scripts/native/')},
        script_sha256=sha(Path(__file__)),selected_functions=24,assembly_instructions=579,
        whole_record_oracles=3,lifetime_scenarios=12,reference_boundary_cases=7,
        independent_constructor_stores=8,standalone_and_full_object='PASS_BOUNDED_RECORDING_HOST',
        normal_link_sha256=link_hash,ordinary_runtime_gate='inventory/client455-hotbar-checkpoint.json',
        ordinary_runtime_gate_sha256=sha(WS/'inventory/client455-hotbar-checkpoint.json'),
        ordinary_Linker_changed=False,normal_client_relinked=False,unchanged_GPU_startup_suites_rerun=False,
        gaps=reference['gaps']+[
            'Core field tokens/data records are not a complete callable C++ ABI or source of target dispatch addresses',
            'The concrete manager host,derived payload factories,base resource lifecycle,board/hover ownership and5x10view must be ported before ordinaryLinker binds these kernels',
            'All086 item/storage/GUI/Tutorial/fourstage/Login/auth/gameplay and earlier M6F/M7/M9 gaps remain mandatory'],
        input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-item-ownership-checkpoint.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PARTIAL_SOURCE_FOUNDATION:92/620byte records/shareditem/refcount/cacheguard;12scenarios standalone/fullobject;ordinary086unchanged/M9OPEN')


if __name__=='__main__':main()
